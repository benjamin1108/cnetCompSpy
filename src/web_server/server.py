#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器

提供Web界面用于浏览和查看从各云服务商爬取的博客和文档内容，以及AI分析结果。
"""

import os
import re
import json
import logging
import glob
import markdown
from pathlib import Path
from typing import Dict, List, Any, Optional

from flask import Flask, render_template, send_from_directory, abort, request, jsonify
from flask import redirect, url_for
from datetime import datetime
from markdown.extensions.codehilite import CodeHiliteExtension


class WebServer:
    """竞争分析Web服务器类"""
    
    def __init__(self, data_dir: str, host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
        """
        初始化Web服务器
        
        Args:
            data_dir: 数据目录路径
            host: 服务器主机地址
            port: 服务器端口
            debug: 是否启用调试模式
        """
        self.logger = logging.getLogger(__name__)
        self.data_dir = os.path.abspath(data_dir)
        self.raw_dir = os.path.join(self.data_dir, 'raw')
        self.analyzed_dir = os.path.join(self.data_dir, 'analysis')
        self.host = host
        self.port = port
        self.debug = debug
        
        # 检查数据目录
        if not os.path.exists(self.raw_dir):
            self.logger.warning(f"原始数据目录不存在: {self.raw_dir}")
        
        if not os.path.exists(self.analyzed_dir):
            self.logger.warning(f"分析数据目录不存在: {self.analyzed_dir}")
            try:
                os.makedirs(self.analyzed_dir, exist_ok=True)
                self.logger.info(f"已创建分析数据目录: {self.analyzed_dir}")
            except Exception as e:
                self.logger.error(f"创建分析数据目录失败: {e}")
        
        # 创建Flask应用
        self.app = Flask(
            __name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static')
        )
        
        # 配置Flask应用
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传大小为16MB
        
        # 注册上下文处理器
        @self.app.context_processor
        def inject_now():
            return {'now': datetime.now()}
        
        # 注册路由
        self._register_routes()
        
        self.logger.info(f"Web服务器初始化完成，数据目录: {self.data_dir}")
    
    def _register_routes(self):
        """注册Flask路由"""
        # 首页 - 显示所有厂商列表
        @self.app.route('/')
        def index():
            vendors = self._get_vendors()
            return render_template(
                'index.html',
                title='云服务厂商竞争分析',
                vendors=vendors
            )
            
        # 统计页面 - 显示文件统计对比
        @self.app.route('/stats')
        def stats_page():
            return render_template(
                'stats.html',
                title='文件统计对比'
            )
        
        # API: 获取统计数据
        @self.app.route('/api/stats')
        def api_stats():
            detailed = request.args.get('detailed', 'false').lower() == 'true'
            
            try:
                # 直接在服务器中分析metadata和文件差异
                stats_data = self._analyze_metadata_files(detailed)
                return jsonify(stats_data)
            except Exception as e:
                self.logger.error(f"获取统计数据失败: {e}")
                return jsonify({'error': str(e)}), 500
        
        # 厂商页面 - 显示特定厂商的所有文档
        @self.app.route('/vendor/<vendor>')
        def vendor_page(vendor):
            if not self._vendor_exists(vendor):
                abort(404)
            
            docs = self._get_vendor_docs(vendor)
            # 检查是否有AI分析的文件
            has_analysis = self._vendor_has_analysis(vendor)
            
            return render_template(
                'vendor.html',
                title=f'{vendor.upper()} - 竞争分析',
                vendor=vendor,
                docs=docs,
                has_analysis=has_analysis,
                view_type='raw'
            )
        
        # AI分析厂商页面 - 显示特定厂商的所有AI分析文档
        @self.app.route('/analysis/<vendor>')
        def analysis_page(vendor):
            if not self._vendor_exists(vendor):
                abort(404)
            
            analysis_docs = self._get_vendor_analysis(vendor)
            if not analysis_docs:
                self.logger.warning(f"厂商 {vendor} 没有分析文档")
                # 如果没有分析文档，重定向到原始文档页面
                return redirect(url_for('vendor_page', vendor=vendor))
            
            return render_template(
                'vendor.html',
                title=f'{vendor.upper()} - AI分析',
                vendor=vendor,
                docs=analysis_docs,
                has_analysis=True,
                view_type='analysis'
            )
        
        # 文档页面 - 显示特定文档内容
        @self.app.route('/document/<vendor>/<doc_type>/<path:filename>')
        def document_page(vendor, doc_type, filename):
            file_path = os.path.join(self.raw_dir, vendor, doc_type, filename)
            
            if not os.path.isfile(file_path):
                abort(404)
            
            content = self._render_document(file_path)
            meta = self._extract_document_meta(file_path)
            
            # 检查是否有对应的分析文件
            analysis_path = os.path.join(self.analyzed_dir, vendor, doc_type, filename)
            has_analysis = os.path.isfile(analysis_path)
            
            return render_template(
                'document.html',
                title=meta.get('title', filename),
                vendor=vendor,
                doc_type=doc_type,
                filename=filename,
                content=content,
                meta=meta,
                has_analysis=has_analysis,
                view_type='raw'
            )
        
        # AI分析文档页面 - 显示特定文档的AI分析内容
        @self.app.route('/analysis/document/<vendor>/<doc_type>/<path:filename>')
        def analysis_document_page(vendor, doc_type, filename):
            analysis_path = os.path.join(self.analyzed_dir, vendor, doc_type, filename)
            
            if not os.path.isfile(analysis_path):
                self.logger.warning(f"请求的分析文档不存在: {analysis_path}")
                # 如果没有分析文档，重定向到原始文档页面
                return redirect(url_for('document_page', vendor=vendor, doc_type=doc_type, filename=filename))
            
            content = self._render_document(analysis_path)
            meta = self._extract_document_meta(analysis_path)
            
            # 提取翻译后的标题
            translated_title = self._extract_translated_title(analysis_path)
            if translated_title:
                # 使用翻译后的标题
                title = translated_title
            else:
                # 回退到原来的行为
                title = f"AI分析: {meta.get('title', filename)}"
            
            # 原始文档路径
            raw_path = os.path.join(self.raw_dir, vendor, doc_type, filename)
            has_raw = os.path.isfile(raw_path)
            
            return render_template(
                'document.html',
                title=title,
                vendor=vendor,
                doc_type=doc_type,
                filename=filename,
                content=content,
                meta=meta,
                has_raw=has_raw,
                view_type='analysis'
            )
        
        # 原始文件 - 提供原始Markdown文件下载
        @self.app.route('/raw/<vendor>/<doc_type>/<path:filename>')
        def raw_file(vendor, doc_type, filename):
            file_path = os.path.join(self.raw_dir, vendor, doc_type, filename)
            
            if not os.path.isfile(file_path):
                abort(404)
            
            directory = os.path.dirname(file_path)
            basename = os.path.basename(file_path)
            
            return send_from_directory(directory, basename, as_attachment=True)
        
        # 分析文件 - 提供AI分析Markdown文件下载
        @self.app.route('/analysis/raw/<vendor>/<doc_type>/<path:filename>')
        def analysis_raw_file(vendor, doc_type, filename):
            file_path = os.path.join(self.analyzed_dir, vendor, doc_type, filename)
            
            if not os.path.isfile(file_path):
                abort(404)
            
            directory = os.path.dirname(file_path)
            basename = os.path.basename(file_path)
            
            return send_from_directory(directory, basename, as_attachment=True)
        
        # 错误处理
        @self.app.errorhandler(404)
        def page_not_found(e):
            return render_template('404.html', title='页面未找到'), 404
        
        @self.app.errorhandler(500)
        def server_error(e):
            return render_template('error.html', title='服务器错误', error=str(e)), 500
    
    def run(self):
        """启动Web服务器"""
        self.logger.info(f"启动Web服务器: http://{self.host}:{self.port}")
        self.app.run(
            host=self.host,
            port=self.port,
            debug=self.debug
        )
    
    def _get_vendors(self) -> List[Dict[str, Any]]:
        """
        获取所有厂商信息
        
        Returns:
            包含厂商名称和文档数量的字典列表
        """
        vendors = []
        
        if not os.path.exists(self.raw_dir):
            return vendors
        
        for vendor_name in os.listdir(self.raw_dir):
            vendor_dir = os.path.join(self.raw_dir, vendor_name)
            
            if os.path.isdir(vendor_dir):
                # 统计文档数量
                doc_count = self._count_vendor_docs(vendor_name)
                analysis_count = self._count_vendor_analysis(vendor_name)
                
                vendors.append({
                    'name': vendor_name,
                    'doc_count': sum(doc_count.values()),
                    'analysis_count': sum(analysis_count.values()),
                    'types': doc_count,
                    'analysis_types': analysis_count
                })
        
        # 按文档总数排序
        vendors.sort(key=lambda v: v['doc_count'], reverse=True)
        
        return vendors
    
    def _vendor_exists(self, vendor: str) -> bool:
        """
        检查厂商是否存在
        
        Args:
            vendor: 厂商名称
            
        Returns:
            是否存在
        """
        vendor_dir = os.path.join(self.raw_dir, vendor)
        return os.path.isdir(vendor_dir)
    
    def _vendor_has_analysis(self, vendor: str) -> bool:
        """
        检查厂商是否有AI分析文档
        
        Args:
            vendor: 厂商名称
            
        Returns:
            是否有AI分析文档
        """
        vendor_dir = os.path.join(self.analyzed_dir, vendor)
        if not os.path.isdir(vendor_dir):
            return False
        
        # 检查是否有任何分析文档
        for doc_type in os.listdir(vendor_dir):
            type_dir = os.path.join(vendor_dir, doc_type)
            if os.path.isdir(type_dir) and os.listdir(type_dir):
                return True
        
        return False
    
    def _count_vendor_docs(self, vendor: str) -> Dict[str, int]:
        """
        统计厂商文档数量
        
        Args:
            vendor: 厂商名称
            
        Returns:
            各类型文档数量
        """
        counts = {}
        vendor_dir = os.path.join(self.raw_dir, vendor)
        
        if not os.path.isdir(vendor_dir):
            return counts
        
        for doc_type in os.listdir(vendor_dir):
            type_dir = os.path.join(vendor_dir, doc_type)
            
            if os.path.isdir(type_dir):
                # 计算此类型下的文档数量
                counts[doc_type] = len([
                    f for f in os.listdir(type_dir)
                    if os.path.isfile(os.path.join(type_dir, f)) and f.endswith('.md')
                ])
        
        return counts
    
    def _count_vendor_analysis(self, vendor: str) -> Dict[str, int]:
        """
        统计厂商AI分析文档数量
        
        Args:
            vendor: 厂商名称
            
        Returns:
            各类型AI分析文档数量
        """
        counts = {}
        vendor_dir = os.path.join(self.analyzed_dir, vendor)
        
        if not os.path.isdir(vendor_dir):
            return counts
        
        for doc_type in os.listdir(vendor_dir):
            type_dir = os.path.join(vendor_dir, doc_type)
            
            if os.path.isdir(type_dir):
                # 计算此类型下的AI分析文档数量
                counts[doc_type] = len([
                    f for f in os.listdir(type_dir)
                    if os.path.isfile(os.path.join(type_dir, f)) and f.endswith('.md')
                ])
        
        return counts
    
    def _get_vendor_docs(self, vendor: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取厂商所有文档
        
        Args:
            vendor: 厂商名称
            
        Returns:
            按类型分组的文档列表
        """
        docs = {}
        vendor_dir = os.path.join(self.raw_dir, vendor)
        
        if not os.path.isdir(vendor_dir):
            return docs
        
        for doc_type in os.listdir(vendor_dir):
            type_dir = os.path.join(vendor_dir, doc_type)
            
            if os.path.isdir(type_dir):
                docs[doc_type] = []
                
                for filename in os.listdir(type_dir):
                    file_path = os.path.join(type_dir, filename)
                    
                    if os.path.isfile(file_path) and filename.endswith('.md'):
                        # 提取文档信息
                        meta = self._extract_document_meta(file_path)
                        
                        # 检查是否有AI分析版本
                        analysis_path = os.path.join(self.analyzed_dir, vendor, doc_type, filename)
                        has_analysis = os.path.isfile(analysis_path)
                        
                        docs[doc_type].append({
                            'filename': filename,
                            'path': f"{vendor}/{doc_type}/{filename}",
                            'title': meta.get('title', filename.replace('.md', '')),
                            'date': meta.get('date', ''),
                            'size': os.path.getsize(file_path),
                            'has_analysis': has_analysis,
                            'source_type': doc_type.upper()
                        })
                
                # 按日期排序，最新的在前面
                docs[doc_type].sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return docs
    
    def _get_vendor_analysis(self, vendor: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取厂商所有AI分析文档
        
        Args:
            vendor: 厂商名称
            
        Returns:
            按类型分组的AI分析文档列表
        """
        docs = {}
        vendor_dir = os.path.join(self.analyzed_dir, vendor)
        
        if not os.path.isdir(vendor_dir):
            return docs
        
        for doc_type in os.listdir(vendor_dir):
            type_dir = os.path.join(vendor_dir, doc_type)
            
            if os.path.isdir(type_dir):
                docs[doc_type] = []
                
                for filename in os.listdir(type_dir):
                    file_path = os.path.join(type_dir, filename)
                    
                    if os.path.isfile(file_path) and filename.endswith('.md'):
                        # 提取文档信息
                        meta = self._extract_document_meta(file_path)
                        
                        # 提取翻译后的标题
                        translated_title = self._extract_translated_title(file_path)
                        
                        # 使用翻译后的标题，如果没有则使用原标题
                        title = translated_title if translated_title else meta.get('title', filename.replace('.md', ''))
                        
                        # 检查是否有原始版本
                        raw_path = os.path.join(self.raw_dir, vendor, doc_type, filename)
                        has_raw = os.path.isfile(raw_path)
                        
                        docs[doc_type].append({
                            'filename': filename,
                            'path': f"{vendor}/{doc_type}/{filename}",
                            'title': title,
                            'date': meta.get('date', ''),
                            'size': os.path.getsize(file_path),
                            'has_raw': has_raw,
                            'source_type': doc_type.upper()
                        })
                
                # 按日期排序，最新的在前面
                docs[doc_type].sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return docs
    
    def _extract_document_meta(self, file_path: str) -> Dict[str, str]:
        """
        从文档中提取元数据
        
        Args:
            file_path: 文档路径
            
        Returns:
            文档元数据
        """
        meta = {
            'title': os.path.basename(file_path).replace('.md', '').replace('_', ' '),
            'date': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(4096)  # 读取前4KB，增加获取元数据的可能性
            
            # 尝试从内容中提取标题
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                meta['title'] = title_match.group(1).strip()
            
            # 判断是分析文档还是原始文档
            is_analysis = 'analyzed' in file_path
            
            # 对于分析文档，如果标题没有"竞争分析摘要："前缀，则添加
            if is_analysis and not meta['title'].startswith('竞争分析摘要：'):
                meta['title'] = f"竞争分析摘要：{meta['title']}"
            
            # 尝试从内容中提取日期 - 优先使用发布日期，而不是文件修改时间
            # 尝试匹配多种可能的日期格式
            date_patterns = [
                r'发布(?:日期|时间)[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # 发布日期: 2025-04-10
                r'\*\*发布时间:\*\*\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # **发布时间:** 2025-04-10
                r'\*\*发布时间:\*\*\s*(\d{4}年\d{1,2}月\d{1,2}日)',    # **发布时间:** 2025年4月10日
                r'\*\*发布时间\*\*:\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})', # **发布时间**: 2025-04-10
                r'\*\*发布日期:\*\*\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # **发布日期:** 2025-04-10
                r'(\d{4}年\d{1,2}月\d{1,2}日)',                       # 2025年4月10日 (仅在上面几种都没匹配到时使用)
                r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s+\d{1,2}:\d{1,2}'    # 2025-04-10 10:30 (包含时间的情况)
            ]
            
            for pattern in date_patterns:
                date_match = re.search(pattern, content, re.MULTILINE)
                if date_match:
                    date_str = date_match.group(1).strip()
                    # 处理中文日期格式 (2025年4月10日 -> 2025-04-10)
                    if '年' in date_str and '月' in date_str and '日' in date_str:
                        date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
                    # 统一分隔符为横杠
                    date_str = date_str.replace('/', '-')
                    meta['date'] = date_str
                    break
            
            # 尝试从内容中提取作者
            author_match = re.search(r'作者[：:]\s*(.+?)[\r\n]', content, re.MULTILINE)
            if author_match:
                meta['author'] = author_match.group(1).strip()
                
            # 尝试从内容中提取source_type
            source_type_match = re.search(r'\*\*类型:\*\*\s*([A-Za-z-]+)', content, re.MULTILINE)
            if source_type_match:
                meta['source_type'] = source_type_match.group(1).strip().upper()
        
        except Exception as e:
            self.logger.error(f"提取文档元数据时出错: {e}")
        
        return meta
    
    def _render_document(self, file_path: str) -> str:
        """
        渲染文档为HTML
        
        Args:
            file_path: 文档路径
            
        Returns:
            渲染后的HTML
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用Python-Markdown渲染
            html = markdown.markdown(
                content,
                extensions=[
                    'markdown.extensions.tables',
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.codehilite',
                    'markdown.extensions.toc'
                ]
            )
            
            return html
        
        except Exception as e:
            self.logger.error(f"渲染文档时出错: {e}")
            return f"<p>无法渲染文档: {e}</p>"
    
    def _analyze_metadata_files(self, detailed: bool = False) -> Dict[str, Any]:
        """
        分析metadata和文件差异
        
        Args:
            detailed: 是否返回详细信息
            
        Returns:
            分析结果
        """
        from src.utils.stats_analyzer import StatsAnalyzer
        
        # 创建统计分析器
        analyzer = StatsAnalyzer(base_dir=os.path.dirname(self.data_dir))
        
        # 分析数据
        return analyzer.generate_json_data(detailed)
    
    def _extract_translated_title(self, file_path: str) -> Optional[str]:
        """
        从分析文档中提取翻译后的标题
        
        Args:
            file_path: 文档路径
            
        Returns:
            翻译后的标题，如果没有找到则返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找AI标题翻译任务的开始和结束标记
            start_marker = "<!-- AI_TASK_START: AI标题翻译 -->"
            end_marker = "<!-- AI_TASK_END: AI标题翻译 -->"
            
            start_idx = content.find(start_marker)
            if start_idx == -1:
                return None
                
            start_idx += len(start_marker)
            end_idx = content.find(end_marker, start_idx)
            
            if end_idx == -1:
                return None
            
            # 提取翻译后的标题
            translated_title = content[start_idx:end_idx].strip()
            
            # 如果标题为空或只包含空白字符，返回None
            if not translated_title:
                return None
                
            # 清理标题中可能的Markdown格式
            # 通常AI只会返回纯文本标题，但以防万一
            translated_title = translated_title.replace('#', '').strip()
            
            self.logger.info(f"从分析文档中提取到翻译标题: {translated_title}")
            return translated_title
            
        except Exception as e:
            self.logger.error(f"提取翻译标题时出错: {e}")
            return None
