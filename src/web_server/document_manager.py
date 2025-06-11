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
                content = f.read(16384)  # 读取前16KB，增加获取元数据的可能性
            
            # 尝试从内容中提取标题
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                meta['title'] = title_match.group(1).strip()
            
            # 判断是分析文档还是原始文档
            is_analysis = 'analyzed' in file_path
            
            # 对于分析文档，如果标题没有"竞争分析摘要："前缀，则添加
            if is_analysis and not meta['title'].startswith('竞争分析摘要：'):
                meta['title'] = f"竞争分析摘要：{meta['title']}"
            
            # 从文件名中提取日期（如果存在）
            filename = os.path.basename(file_path)
            filename_date_match = re.match(r'^(\d{4}-\d{2}-\d{2})_', filename)
            filename_month_match = re.match(r'^(\d{4}-\d{2})\.md$', filename)  # 华为月度格式
            
            filename_date_fallback = None
            if filename_date_match:
                filename_date_fallback = filename_date_match.group(1)
            elif filename_month_match:
                # 华为月度文档：2025-05.md -> 2025-05-01 (添加默认日期)
                year_month = filename_month_match.group(1)
                filename_date_fallback = f"{year_month}-01"
                self.logger.debug(f"华为月度文档日期标准化: {filename} -> {filename_date_fallback}")
            
            # 尝试从内容中提取日期 - 优先使用发布日期，而不是文件修改时间
            # 尝试匹配多种可能的日期格式，同时支持中英文标点符号
            date_patterns = [
                # 常见的显式标记日期格式 - 支持中英文冒号和其他常见变体
                r'发表于[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)',  # 匹配爬虫注入的"发表于"时间
                r'发布(?:日期|时间)[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # 发布日期: 2025-04-10
                r'\*\*发布时间[：:]\*\*\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # **发布时间:** 2025-04-10
                r'\*\*发布时间[：:]\*\*\s*(\d{4}年\d{1,2}月\d{1,2}日)',    # **发布时间:** 2025年4月10日
                r'\*\*发布时间\*\*[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})', # **发布时间**: 2025-04-10
                r'\*\*发布日期[：:]\*\*\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # **发布日期:** 2025-04-10
                # 华为月度格式 - 新增专门处理
                r'\*\*发布时间[：:]\*\*\s*(\d{4}-\d{1,2})',               # **发布时间:** 2025-05
                r'发布时间为\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',            # 发布时间为 2025-04-01
                r'发布日期为\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',            # 发布日期为 2025-04-01
                # 中文日期格式
                r'(\d{4}年\d{1,2}月\d{1,2}日)',                         # 2025年4月10日
                # 含时间的日期格式
                r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s+\d{1,2}[:：]\d{1,2}'   # 2025-04-10 10:30
            ]
            
            # 日期提取标志，表示是否已成功提取日期
            date_extracted = False
            
            for pattern in date_patterns:
                date_match = re.search(pattern, content, re.MULTILINE)
                if date_match:
                    date_str = date_match.group(1).strip()
                    # 处理中文日期格式 (2025年4月10日 -> 2025-04-10)
                    if '年' in date_str and '月' in date_str and '日' in date_str:
                        date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
                    # 统一分隔符为横杠
                    date_str = date_str.replace('/', '-')
                    
                    # 华为月度格式处理：如果只有年月，添加默认日期
                    if re.match(r'^\d{4}-\d{1,2}$', date_str):
                        date_str = f"{date_str}-01"
                        self.logger.debug(f"华为月度日期标准化: {date_match.group(1)} -> {date_str}")
                    
                    meta['date'] = date_str
                    date_extracted = True
                    self.logger.debug(f"从内容中提取到日期: {date_str} (使用模式: {pattern})")
                    break
            
            # 如果从内容中没有提取到日期，但从文件名中提取到了，使用文件名中的日期
            if not date_extracted and filename_date_fallback:
                meta['date'] = filename_date_fallback
                self.logger.debug(f"从文件名中提取到日期: {filename_date_fallback}")
            
            # 尝试从内容中提取作者
            author_match = re.search(r'作者[：:]\s*(.+?)[\r\n]', content, re.MULTILINE)
            if author_match:
                meta['author'] = author_match.group(1).strip()
                
            # 尝试从内容中提取source_type
            source_type_match = re.search(r'\*\*类型[：:]\*\*\s*([A-Za-z-]+)', content, re.MULTILINE)
            if source_type_match:
                meta['source_type'] = source_type_match.group(1).strip().upper()
        
        except Exception as e:
            self.logger.error(f"提取文档元数据时出错: {e}")
        
        return meta
    
    def _render_document(self, file_path: str) -> str:
        """
        渲染文档为原始markdown内容
        
        Args:
            file_path: 文档路径
            
        Returns:
            原始markdown内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
        
        except Exception as e:
            self.logger.error(f"读取文档时出错: {e}")
            return f"无法读取文档: {e}"
    
    def _preprocess_markdown_lists(self, content: str) -> str:
        """
        预处理markdown内容，修复列表缩进问题和斜体语法问题
        
        Args:
            content: 原始markdown内容
            
        Returns:
            处理后的markdown内容
        """
        import re
        
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            # 跳过包含HTML注释的行，避免影响AI任务标记
            if '<!--' in line and '-->' in line:
                processed_lines.append(line)
                continue
            
            # 修复下划线斜体语法问题
            # 匹配模式：非空格字符 + 下划线 + 内容 + 下划线 + 非空格字符
            # 在下划线前后添加空格，确保markdown能正确识别斜体语法
            line = re.sub(r'([^\s])_([^_\s][^_]*[^_\s])_([^\s])', r'\1 _\2_ \3', line)
            
            # 检查是否是列表项（有序或无序）
            # 匹配模式：开头可能有空格，然后是列表标记
            list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.*)$', line)
            
            if list_match:
                indent, marker, text = list_match.groups()
                indent_len = len(indent)
                
                # 如果缩进是2的倍数但不是4的倍数，转换为4空格缩进
                if indent_len > 0 and indent_len % 2 == 0 and indent_len % 4 != 0:
                    # 将2空格缩进转换为4空格缩进
                    new_indent_len = (indent_len // 2) * 4
                    new_indent = ' ' * new_indent_len
                    processed_line = f"{new_indent}{marker} {text}"
                    processed_lines.append(processed_line)
                else:
                    processed_lines.append(line)
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
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
            
            self.logger.debug(f"从分析文档中提取到翻译标题: {translated_title}")
            return translated_title
            
        except Exception as e:
            self.logger.error(f"提取翻译标题时出错: {e}")
            return None
