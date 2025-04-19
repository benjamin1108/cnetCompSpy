#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器 - 文档管理器

负责处理文档相关的功能，如获取文档、渲染文档等。
"""

import os
import re
import logging
import markdown
from typing import Dict, Any, Optional
from flask import send_from_directory, abort
from datetime import datetime

class DocumentManager:
    """文档管理器类"""
    
    def __init__(self, raw_dir: str, analyzed_dir: str):
        """
        初始化文档管理器
        
        Args:
            raw_dir: 原始数据目录路径
            analyzed_dir: 分析数据目录路径
        """
        self.logger = logging.getLogger(__name__)
        self.raw_dir = raw_dir
        self.analyzed_dir = analyzed_dir
        
        self.logger.info("文档管理器初始化完成")
    
    def get_document(self, vendor: str, doc_type: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        获取文档信息
        
        Args:
            vendor: 厂商名称
            doc_type: 文档类型
            filename: 文件名
            
        Returns:
            文档信息，包括内容、元数据等，如果文档不存在则返回None
        """
        file_path = os.path.join(self.raw_dir, vendor, doc_type, filename)
        
        if not os.path.isfile(file_path):
            return None
        
        content = self._render_document(file_path)
        meta = self._extract_document_meta(file_path)
        
        # 检查是否有对应的分析文件
        analysis_path = os.path.join(self.analyzed_dir, vendor, doc_type, filename)
        has_analysis = os.path.isfile(analysis_path)
        
        return {
            'content': content,
            'meta': meta,
            'has_analysis': has_analysis
        }
    
    def get_analysis_document(self, vendor: str, doc_type: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        获取分析文档信息
        
        Args:
            vendor: 厂商名称
            doc_type: 文档类型
            filename: 文件名
            
        Returns:
            分析文档信息，包括内容、元数据等，如果文档不存在则返回None
        """
        analysis_path = os.path.join(self.analyzed_dir, vendor, doc_type, filename)
        
        if not os.path.isfile(analysis_path):
            return None
        
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
        
        return {
            'content': content,
            'meta': meta,
            'title': title,
            'has_raw': has_raw
        }
    
    def get_raw_file(self, vendor: str, doc_type: str, filename: str):
        """
        获取原始文件用于下载
        
        Args:
            vendor: 厂商名称
            doc_type: 文档类型
            filename: 文件名
            
        Returns:
            文件下载响应
        """
        file_path = os.path.join(self.raw_dir, vendor, doc_type, filename)
        
        if not os.path.isfile(file_path):
            abort(404)
        
        directory = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        
        return send_from_directory(directory, basename, as_attachment=True)
    
    def get_analysis_raw_file(self, vendor: str, doc_type: str, filename: str):
        """
        获取分析文件用于下载
        
        Args:
            vendor: 厂商名称
            doc_type: 文档类型
            filename: 文件名
            
        Returns:
            文件下载响应
        """
        file_path = os.path.join(self.analyzed_dir, vendor, doc_type, filename)
        
        if not os.path.isfile(file_path):
            abort(404)
        
        directory = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        
        return send_from_directory(directory, basename, as_attachment=True)
    
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
