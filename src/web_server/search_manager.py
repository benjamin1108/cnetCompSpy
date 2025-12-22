#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器 - 搜索管理器

负责处理全文搜索功能，包括：
1. 文档内容全文搜索
2. 匹配内容摘要片段提取
3. 搜索索引缓存机制
"""

import os
import re
import logging
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class SearchResult:
    """搜索结果数据类"""
    filename: str
    path: str
    title: str
    translated_title: str
    vendor: str
    doc_type: str
    date: str
    has_analysis: bool
    snippet: str = ""  # 匹配内容摘要
    match_type: str = "title"  # title / content / both
    relevance_score: float = 0.0  # 相关性得分


@dataclass
class DocumentIndex:
    """文档索引数据类"""
    file_path: str
    vendor: str
    doc_type: str
    filename: str
    title: str
    translated_title: str
    content: str
    date: str
    has_analysis: bool
    last_modified: float
    content_hash: str


class SearchManager:
    """搜索管理器类"""
    
    # 摘要片段的上下文字符数
    SNIPPET_CONTEXT_CHARS = 80
    # 最大摘要长度
    MAX_SNIPPET_LENGTH = 200
    # 索引缓存过期时间（秒）
    INDEX_CACHE_TTL = 300  # 5分钟
    # 最大缓存文档数
    MAX_CACHED_DOCS = 5000
    
    def __init__(self, raw_dir: str, analyzed_dir: str, document_manager: Any):
        """
        初始化搜索管理器
        
        Args:
            raw_dir: 原始数据目录路径
            analyzed_dir: 分析数据目录路径
            document_manager: 文档管理器实例
        """
        self.logger = logging.getLogger(__name__)
        self.raw_dir = raw_dir
        self.analyzed_dir = analyzed_dir
        self.document_manager = document_manager
        
        # 文档索引缓存
        self._index_cache: Dict[str, DocumentIndex] = {}
        self._index_lock = Lock()
        self._last_index_time: float = 0
        self._index_dirty = True  # 标记索引是否需要刷新
        
        self.logger.info("搜索管理器初始化完成")
    
    def search(self, keyword: str, vendor_filter: str = "", 
               search_content: bool = True, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        全文搜索文档
        
        Args:
            keyword: 搜索关键词
            vendor_filter: 厂商过滤器（可选）
            search_content: 是否搜索文档内容（默认True）
            max_results: 最大返回结果数
            
        Returns:
            搜索结果列表
        """
        if not keyword or not keyword.strip():
            return []
        
        keyword = keyword.strip()
        keyword_lower = keyword.lower()
        
        # 确保索引是最新的
        self._ensure_index_fresh()
        
        results: List[SearchResult] = []
        
        with self._index_lock:
            for doc_key, doc_index in self._index_cache.items():
                # 应用厂商过滤
                if vendor_filter and doc_index.vendor != vendor_filter:
                    continue
                
                # 检查标题匹配
                title_match = keyword_lower in doc_index.title.lower()
                translated_title_match = (doc_index.translated_title and 
                                         keyword_lower in doc_index.translated_title.lower())
                
                # 检查内容匹配
                content_match = False
                snippet = ""
                if search_content and doc_index.content:
                    content_match, snippet = self._search_in_content(
                        doc_index.content, keyword
                    )
                
                # 计算相关性得分和匹配类型
                if title_match or translated_title_match or content_match:
                    match_type = self._determine_match_type(
                        title_match, translated_title_match, content_match
                    )
                    relevance_score = self._calculate_relevance(
                        keyword_lower, doc_index, title_match, 
                        translated_title_match, content_match
                    )
                    
                    # 如果只有标题匹配，尝试从内容生成摘要
                    if not snippet and doc_index.content:
                        snippet = self._generate_default_snippet(doc_index.content)
                    
                    result = SearchResult(
                        filename=doc_index.filename,
                        path=f"{doc_index.vendor}/{doc_index.doc_type}/{doc_index.filename}",
                        title=doc_index.title,
                        translated_title=doc_index.translated_title,
                        vendor=doc_index.vendor,
                        doc_type=doc_index.doc_type,
                        date=doc_index.date,
                        has_analysis=doc_index.has_analysis,
                        snippet=snippet,
                        match_type=match_type,
                        relevance_score=relevance_score
                    )
                    results.append(result)
        
        # 按相关性得分排序
        results.sort(key=lambda x: (-x.relevance_score, x.date or ""), reverse=False)
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # 限制结果数量并转换为字典
        return [self._result_to_dict(r) for r in results[:max_results]]
    
    def _search_in_content(self, content: str, keyword: str) -> Tuple[bool, str]:
        """
        在内容中搜索关键词并提取摘要片段
        
        Args:
            content: 文档内容
            keyword: 搜索关键词
            
        Returns:
            (是否匹配, 摘要片段)
        """
        if not content:
            return False, ""
        
        # 清理内容：移除markdown格式标记以便更好地搜索
        clean_content = self._clean_content_for_search(content)
        
        # 不区分大小写搜索
        keyword_lower = keyword.lower()
        content_lower = clean_content.lower()
        
        # 查找所有匹配位置
        match_positions = []
        start = 0
        while True:
            pos = content_lower.find(keyword_lower, start)
            if pos == -1:
                break
            match_positions.append(pos)
            start = pos + 1
        
        if not match_positions:
            return False, ""
        
        # 使用第一个匹配位置生成摘要
        first_pos = match_positions[0]
        snippet = self._extract_snippet(clean_content, first_pos, keyword)
        
        return True, snippet
    
    def _extract_snippet(self, content: str, match_pos: int, keyword: str) -> str:
        """
        从内容中提取包含关键词的摘要片段
        
        Args:
            content: 文档内容
            match_pos: 匹配位置
            keyword: 搜索关键词
            
        Returns:
            带有高亮标记的摘要片段
        """
        content_len = len(content)
        keyword_len = len(keyword)
        
        # 计算摘要的起始和结束位置
        start = max(0, match_pos - self.SNIPPET_CONTEXT_CHARS)
        end = min(content_len, match_pos + keyword_len + self.SNIPPET_CONTEXT_CHARS)
        
        # 调整到词边界（避免截断单词）
        if start > 0:
            # 向前找到空格或换行
            while start > 0 and content[start] not in ' \n\t':
                start -= 1
            start = max(0, start)
        
        if end < content_len:
            # 向后找到空格或换行
            while end < content_len and content[end] not in ' \n\t':
                end += 1
        
        # 提取片段
        snippet = content[start:end].strip()
        
        # 清理多余的空白字符
        snippet = re.sub(r'\s+', ' ', snippet)
        
        # 添加省略号
        if start > 0:
            snippet = "..." + snippet
        if end < content_len:
            snippet = snippet + "..."
        
        # 限制最大长度
        if len(snippet) > self.MAX_SNIPPET_LENGTH:
            snippet = snippet[:self.MAX_SNIPPET_LENGTH] + "..."
        
        return snippet
    
    def _generate_default_snippet(self, content: str, max_length: int = 150) -> str:
        """
        生成默认摘要（用于没有内容匹配但有标题匹配的情况）
        
        Args:
            content: 文档内容
            max_length: 最大摘要长度
            
        Returns:
            摘要文本
        """
        if not content:
            return ""
        
        # 清理内容
        clean = self._clean_content_for_search(content)
        
        # 跳过开头的标题和元数据
        lines = clean.split('\n')
        content_start = 0
        for i, line in enumerate(lines):
            line = line.strip()
            # 跳过空行、标题行、元数据行
            if line and not line.startswith('#') and not line.startswith('**') and len(line) > 20:
                content_start = i
                break
        
        # 合并后续内容
        snippet_lines = lines[content_start:content_start + 5]
        snippet = ' '.join(line.strip() for line in snippet_lines if line.strip())
        
        # 清理和截断
        snippet = re.sub(r'\s+', ' ', snippet).strip()
        if len(snippet) > max_length:
            snippet = snippet[:max_length] + "..."
        
        return snippet
    
    def _clean_content_for_search(self, content: str) -> str:
        """
        清理内容以便搜索
        
        Args:
            content: 原始内容
            
        Returns:
            清理后的内容
        """
        # 移除HTML注释
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        # 移除代码块
        content = re.sub(r'```[\s\S]*?```', '', content)
        # 移除行内代码
        content = re.sub(r'`[^`]+`', '', content)
        # 移除链接但保留文本
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        # 移除图片
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', content)
        # 移除markdown格式符号
        content = re.sub(r'[*_~]+', '', content)
        # 标准化空白
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def _determine_match_type(self, title_match: bool, translated_title_match: bool, 
                              content_match: bool) -> str:
        """确定匹配类型"""
        if (title_match or translated_title_match) and content_match:
            return "both"
        elif title_match or translated_title_match:
            return "title"
        else:
            return "content"
    
    def _calculate_relevance(self, keyword_lower: str, doc_index: DocumentIndex,
                            title_match: bool, translated_title_match: bool,
                            content_match: bool) -> float:
        """
        计算搜索结果的相关性得分
        
        得分规则：
        - 标题完全匹配: +50
        - 翻译标题完全匹配: +45
        - 标题包含关键词: +30
        - 翻译标题包含关键词: +25
        - 内容包含关键词: +10
        - 有AI分析版本: +5
        """
        score = 0.0
        
        # 标题匹配得分
        if title_match:
            if doc_index.title.lower() == keyword_lower:
                score += 50
            else:
                score += 30
        
        if translated_title_match:
            if doc_index.translated_title.lower() == keyword_lower:
                score += 45
            else:
                score += 25
        
        # 内容匹配得分
        if content_match:
            score += 10
            # 计算关键词在内容中出现的次数，增加得分
            content_lower = doc_index.content.lower() if doc_index.content else ""
            occurrences = content_lower.count(keyword_lower)
            score += min(occurrences * 0.5, 10)  # 最多额外加10分
        
        # 有分析版本加分
        if doc_index.has_analysis:
            score += 5
        
        return score
    
    def _result_to_dict(self, result: SearchResult) -> Dict[str, Any]:
        """将SearchResult转换为字典"""
        return {
            'filename': result.filename,
            'path': result.path,
            'title': result.title,
            'translated_title': result.translated_title,
            'vendor': result.vendor,
            'doc_type': result.doc_type,
            'date': result.date,
            'has_analysis': result.has_analysis,
            'snippet': result.snippet,
            'match_type': result.match_type,
            'relevance_score': result.relevance_score
        }
    
    def _ensure_index_fresh(self):
        """确保索引是最新的"""
        current_time = time.time()
        
        # 检查是否需要刷新索引
        if (self._index_dirty or 
            current_time - self._last_index_time > self.INDEX_CACHE_TTL):
            self._build_index()
    
    def _build_index(self):
        """构建或刷新文档索引"""
        self.logger.info("开始构建搜索索引...")
        start_time = time.time()
        
        new_index: Dict[str, DocumentIndex] = {}
        doc_count = 0
        
        if not os.path.exists(self.raw_dir):
            self.logger.warning(f"原始数据目录不存在: {self.raw_dir}")
            return
        
        for vendor in os.listdir(self.raw_dir):
            vendor_dir = os.path.join(self.raw_dir, vendor)
            if not os.path.isdir(vendor_dir):
                continue
            
            for doc_type in os.listdir(vendor_dir):
                type_dir = os.path.join(vendor_dir, doc_type)
                if not os.path.isdir(type_dir):
                    continue
                
                for filename in os.listdir(type_dir):
                    if not filename.endswith('.md'):
                        continue
                    
                    file_path = os.path.join(type_dir, filename)
                    if not os.path.isfile(file_path):
                        continue
                    
                    doc_key = f"{vendor}/{doc_type}/{filename}"
                    
                    # 检查缓存中是否有该文档且未修改
                    last_modified = os.path.getmtime(file_path)
                    if doc_key in self._index_cache:
                        cached = self._index_cache[doc_key]
                        if cached.last_modified == last_modified:
                            new_index[doc_key] = cached
                            doc_count += 1
                            continue
                    
                    # 需要重新索引该文档
                    try:
                        doc_index = self._index_document(
                            file_path, vendor, doc_type, filename, last_modified
                        )
                        if doc_index:
                            new_index[doc_key] = doc_index
                            doc_count += 1
                    except Exception as e:
                        self.logger.error(f"索引文档失败 {file_path}: {e}")
                    
                    # 限制最大缓存数
                    if doc_count >= self.MAX_CACHED_DOCS:
                        self.logger.warning(f"达到最大缓存文档数限制: {self.MAX_CACHED_DOCS}")
                        break
        
        # 更新缓存
        with self._index_lock:
            self._index_cache = new_index
            self._last_index_time = time.time()
            self._index_dirty = False
        
        elapsed = time.time() - start_time
        self.logger.info(f"搜索索引构建完成，共 {doc_count} 个文档，耗时 {elapsed:.2f}秒")
    
    def _index_document(self, file_path: str, vendor: str, doc_type: str, 
                        filename: str, last_modified: float) -> Optional[DocumentIndex]:
        """
        索引单个文档
        
        Args:
            file_path: 文件路径
            vendor: 厂商
            doc_type: 文档类型
            filename: 文件名
            last_modified: 最后修改时间
            
        Returns:
            文档索引对象
        """
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"读取文件失败 {file_path}: {e}")
            return None
        
        # 计算内容哈希
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # 提取元数据
        meta = self.document_manager._extract_document_meta(file_path)
        title = meta.get('title', filename.replace('.md', ''))
        date_str = meta.get('date', '')
        
        # 检查是否有分析版本
        analysis_path = os.path.join(self.analyzed_dir, vendor, doc_type, filename)
        has_analysis = os.path.isfile(analysis_path)
        
        # 获取翻译标题
        translated_title = ""
        if has_analysis:
            translated_title = self.document_manager._extract_translated_title(analysis_path) or ""
        
        return DocumentIndex(
            file_path=file_path,
            vendor=vendor,
            doc_type=doc_type,
            filename=filename,
            title=title,
            translated_title=translated_title,
            content=content,
            date=date_str,
            has_analysis=has_analysis,
            last_modified=last_modified,
            content_hash=content_hash
        )
    
    def invalidate_cache(self):
        """使缓存失效，强制下次搜索时重建索引"""
        with self._index_lock:
            self._index_dirty = True
        self.logger.info("搜索索引缓存已失效")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._index_lock:
            return {
                'cached_docs': len(self._index_cache),
                'last_index_time': self._last_index_time,
                'cache_age_seconds': time.time() - self._last_index_time if self._last_index_time else 0,
                'is_dirty': self._index_dirty,
                'cache_ttl': self.INDEX_CACHE_TTL
            }
