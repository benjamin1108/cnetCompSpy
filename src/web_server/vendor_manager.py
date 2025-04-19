#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器 - 厂商管理器

负责处理厂商相关的功能，如获取厂商列表、厂商文档等。
"""

import os
import logging
from typing import Dict, List, Any
from datetime import datetime

class VendorManager:
    """厂商管理器类"""
    
    def __init__(self, raw_dir: str, analyzed_dir: str, document_manager: Any):
        """
        初始化厂商管理器
        
        Args:
            raw_dir: 原始数据目录路径
            analyzed_dir: 分析数据目录路径
            document_manager: 文档管理器实例
        """
        self.logger = logging.getLogger(__name__)
        self.raw_dir = raw_dir
        self.analyzed_dir = analyzed_dir
        self.document_manager = document_manager
        
        self.logger.info("厂商管理器初始化完成")
    
    def get_vendors(self) -> List[Dict[str, Any]]:
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
    
    def vendor_exists(self, vendor: str) -> bool:
        """
        检查厂商是否存在
        
        Args:
            vendor: 厂商名称
            
        Returns:
            是否存在
        """
        vendor_dir = os.path.join(self.raw_dir, vendor)
        return os.path.isdir(vendor_dir)
    
    def vendor_has_analysis(self, vendor: str) -> bool:
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
    
    def get_vendor_docs(self, vendor: str) -> Dict[str, List[Dict[str, Any]]]:
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
                        meta = self.document_manager._extract_document_meta(file_path)
                        
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
    
    def get_vendor_analysis(self, vendor: str) -> Dict[str, List[Dict[str, Any]]]:
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
                        meta = self.document_manager._extract_document_meta(file_path)
                        
                        # 提取翻译后的标题
                        translated_title = self.document_manager._extract_translated_title(file_path)
                        
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
