#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器 - 厂商管理器

负责处理厂商相关的功能，如获取厂商列表、厂商文档等。
"""

import os
import logging
import re
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
    
    def _smart_date_sort_key(self, doc_item: Dict[str, Any]) -> str:
        """
        智能日期排序键生成函数，处理不同的日期格式
        
        Args:
            doc_item: 文档项目字典
            
        Returns:
            标准化的日期字符串，用于排序
        """
        date_str = doc_item.get('date', '')
        if not date_str:
            return '1970-01-01'  # 默认最早日期
        
        try:
            # 处理华为月度格式：YYYY-MM -> YYYY-MM-01
            if re.match(r'^\d{4}-\d{1,2}$', date_str):
                parts = date_str.split('-')
                year = parts[0]
                month = parts[1].zfill(2)  # 确保月份是两位数
                normalized_date = f"{year}-{month}-01"
                self.logger.debug(f"华为月度日期排序标准化: {date_str} -> {normalized_date}")
                return normalized_date
            
            # 处理下划线格式：YYYY_MM_DD -> YYYY-MM-DD
            if re.match(r'^\d{4}_\d{1,2}_\d{1,2}$', date_str):
                return date_str.replace('_', '-')
            
            # 标准格式直接返回
            if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', date_str):
                return date_str
            
            # 其他格式尝试解析
            return date_str
            
        except Exception as e:
            self.logger.debug(f"日期排序键生成出错: {date_str}, {e}")
            return '1970-01-01'
    
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
                docs[doc_type].sort(key=self._smart_date_sort_key, reverse=True)
        
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
                docs[doc_type].sort(key=self._smart_date_sort_key, reverse=True)
        
        return docs
        
    def get_weekly_updates(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取本周所有厂商的更新文章
        
        Returns:
            按厂商分组的本周更新文章列表（仅包含有AI分析的文章）
        """
        from datetime import datetime, timedelta
        import re
        
        # 获取当前周的起止日期（从周一到周日）
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())  # 周一
        start_of_week = datetime(start_of_week.year, start_of_week.month, start_of_week.day)
        end_of_week = start_of_week + timedelta(days=6)  # 周日
        
        self.logger.info(f"获取本周更新 ({start_of_week.strftime('%Y-%m-%d')} 到 {end_of_week.strftime('%Y-%m-%d')})")
        
        weekly_updates = {}
        
        # 遍历所有厂商目录
        if os.path.exists(self.raw_dir):
            for vendor in os.listdir(self.raw_dir):
                vendor_dir = os.path.join(self.raw_dir, vendor)
                
                if os.path.isdir(vendor_dir):
                    vendor_updates = []
                    
                    # 遍历厂商的所有文档类型
                    for doc_type in os.listdir(vendor_dir):
                        type_dir = os.path.join(vendor_dir, doc_type)
                        
                        if os.path.isdir(type_dir):
                            # 遍历此类型下的所有文件
                            for filename in os.listdir(type_dir):
                                file_path = os.path.join(type_dir, filename)
                                
                                if os.path.isfile(file_path) and filename.endswith('.md'):
                                    # 检查是否有AI分析版本
                                    analysis_path = os.path.join(self.analyzed_dir, vendor, doc_type, filename)
                                    if not os.path.isfile(analysis_path):
                                        continue  # 如果没有分析版本，跳过此文件
                                    
                                    # 提取文档信息
                                    meta = self.document_manager._extract_document_meta(file_path)
                                    date_str = meta.get('date', '')
                                    
                                    # 检查日期是否在本周范围内
                                    if date_str:
                                        try:
                                            # 处理不同的日期格式
                                            if re.match(r'\d{4}-\d{1,2}-\d{1,2}', date_str):
                                                doc_date = datetime.strptime(date_str, '%Y-%m-%d')
                                            elif re.match(r'\d{4}_\d{1,2}_\d{1,2}', date_str):
                                                doc_date = datetime.strptime(date_str, '%Y_%m_%d')
                                            else:
                                                continue
                                            
                                            # 检查是否在本周范围内
                                            if start_of_week <= doc_date <= end_of_week:
                                                # 获取分析文档的翻译标题
                                                translated_title = self.document_manager._extract_translated_title(analysis_path)
                                                original_title = meta.get('title', filename.replace('.md', ''))
                                                
                                                vendor_updates.append({
                                                    'filename': filename,
                                                    'path': f"{vendor}/{doc_type}/{filename}",
                                                    'title': translated_title if translated_title else original_title,
                                                    'original_title': original_title,
                                                    'translated_title': translated_title,
                                                    'date': date_str,
                                                    'doc_type': doc_type,
                                                    'vendor': vendor,
                                                    'size': os.path.getsize(file_path)
                                                })
                                        except (ValueError, TypeError) as e:
                                            self.logger.debug(f"解析日期出错: {date_str}, {e}")
                    
                    # 如果有更新，按日期排序并添加到结果中
                    if vendor_updates:
                        vendor_updates.sort(key=self._smart_date_sort_key, reverse=True)
                        weekly_updates[vendor] = vendor_updates
        
        return weekly_updates
        
    def get_daily_updates(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取今日所有厂商的更新文章
        
        Returns:
            按厂商分组的今日更新文章列表（仅包含有AI分析的文章）
        """
        from datetime import datetime
        import re
        
        # 获取今天的日期
        today = datetime.today()
        today_date = datetime(today.year, today.month, today.day)
        
        self.logger.info(f"获取今日更新 ({today_date.strftime('%Y-%m-%d')})")
        
        daily_updates = {}
        
        # 遍历所有厂商目录
        if os.path.exists(self.raw_dir):
            for vendor in os.listdir(self.raw_dir):
                vendor_dir = os.path.join(self.raw_dir, vendor)
                
                if os.path.isdir(vendor_dir):
                    vendor_updates = []
                    
                    # 遍历厂商的所有文档类型
                    for doc_type in os.listdir(vendor_dir):
                        type_dir = os.path.join(vendor_dir, doc_type)
                        
                        if os.path.isdir(type_dir):
                            # 遍历此类型下的所有文件
                            for filename in os.listdir(type_dir):
                                file_path = os.path.join(type_dir, filename)
                                
                                if os.path.isfile(file_path) and filename.endswith('.md'):
                                    # 检查是否有AI分析版本
                                    analysis_path = os.path.join(self.analyzed_dir, vendor, doc_type, filename)
                                    if not os.path.isfile(analysis_path):
                                        continue  # 如果没有分析版本，跳过此文件
                                    
                                    # 提取文档信息
                                    meta = self.document_manager._extract_document_meta(file_path)
                                    date_str = meta.get('date', '')
                                    
                                    # 检查日期是否为今天
                                    if date_str:
                                        try:
                                            # 处理不同的日期格式
                                            if re.match(r'\d{4}-\d{1,2}-\d{1,2}', date_str):
                                                doc_date = datetime.strptime(date_str, '%Y-%m-%d')
                                            elif re.match(r'\d{4}_\d{1,2}_\d{1,2}', date_str):
                                                doc_date = datetime.strptime(date_str, '%Y_%m_%d')
                                            else:
                                                continue
                                            
                                            # 检查是否为今天的日期
                                            if doc_date.date() == today_date.date():
                                                # 获取分析文档的翻译标题
                                                translated_title = self.document_manager._extract_translated_title(analysis_path)
                                                original_title = meta.get('title', filename.replace('.md', ''))
                                                
                                                vendor_updates.append({
                                                    'filename': filename,
                                                    'path': f"{vendor}/{doc_type}/{filename}",
                                                    'title': translated_title if translated_title else original_title,
                                                    'original_title': original_title,
                                                    'translated_title': translated_title,
                                                    'date': date_str,
                                                    'doc_type': doc_type,
                                                    'vendor': vendor,
                                                    'size': os.path.getsize(file_path)
                                                })
                                        except (ValueError, TypeError) as e:
                                            self.logger.debug(f"解析日期出错: {date_str}, {e}")
                    
                    # 如果有更新，按日期排序并添加到结果中
                    if vendor_updates:
                        vendor_updates.sort(key=self._smart_date_sort_key, reverse=True)
                        daily_updates[vendor] = vendor_updates
        
        return daily_updates
    
    def get_recently_updates(self, days: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取最近几天所有厂商的更新文章
        
        Args:
            days: 天数，获取最近几天的更新，默认为3天
            
        Returns:
            按厂商分组的最近更新文章列表（仅包含有AI分析的文章）
        """
        from datetime import datetime, timedelta
        import re
        
        # 获取今天的日期
        today = datetime.today()
        today_date = datetime(today.year, today.month, today.day)
        # 计算起始日期
        start_date = today_date - timedelta(days=days-1)  # days-1是因为包含今天在内的days天
        
        self.logger.info(f"获取最近{days}天更新 ({start_date.strftime('%Y-%m-%d')} 到 {today_date.strftime('%Y-%m-%d')})")
        
        recently_updates = {}
        
        # 遍历所有厂商目录
        if os.path.exists(self.raw_dir):
            for vendor in os.listdir(self.raw_dir):
                vendor_dir = os.path.join(self.raw_dir, vendor)
                
                if os.path.isdir(vendor_dir):
                    vendor_updates = []
                    
                    # 遍历厂商的所有文档类型
                    for doc_type in os.listdir(vendor_dir):
                        type_dir = os.path.join(vendor_dir, doc_type)
                        
                        if os.path.isdir(type_dir):
                            # 遍历此类型下的所有文件
                            for filename in os.listdir(type_dir):
                                file_path = os.path.join(type_dir, filename)
                                
                                if os.path.isfile(file_path) and filename.endswith('.md'):
                                    # 检查是否有AI分析版本
                                    analysis_path = os.path.join(self.analyzed_dir, vendor, doc_type, filename)
                                    if not os.path.isfile(analysis_path):
                                        continue  # 如果没有分析版本，跳过此文件
                                    
                                    # 提取文档信息
                                    meta = self.document_manager._extract_document_meta(file_path)
                                    date_str = meta.get('date', '')
                                    
                                    # 检查日期是否在指定范围内
                                    if date_str:
                                        try:
                                            # 处理不同的日期格式
                                            if re.match(r'\d{4}-\d{1,2}-\d{1,2}', date_str):
                                                doc_date = datetime.strptime(date_str, '%Y-%m-%d')
                                            elif re.match(r'\d{4}_\d{1,2}_\d{1,2}', date_str):
                                                doc_date = datetime.strptime(date_str, '%Y_%m_%d')
                                            else:
                                                continue
                                            
                                            # 检查是否在指定日期范围内(今天及之前days-1天)
                                            if start_date.date() <= doc_date.date() <= today_date.date():
                                                # 获取分析文档的翻译标题
                                                translated_title = self.document_manager._extract_translated_title(analysis_path)
                                                original_title = meta.get('title', filename.replace('.md', ''))
                                                
                                                vendor_updates.append({
                                                    'filename': filename,
                                                    'path': f"{vendor}/{doc_type}/{filename}",
                                                    'title': translated_title if translated_title else original_title,
                                                    'original_title': original_title,
                                                    'translated_title': translated_title,
                                                    'date': date_str,
                                                    'doc_type': doc_type,
                                                    'vendor': vendor,
                                                    'size': os.path.getsize(file_path)
                                                })
                                        except (ValueError, TypeError) as e:
                                            self.logger.debug(f"解析日期出错: {date_str}, {e}")
                    
                    # 如果有更新，按日期排序并添加到结果中
                    if vendor_updates:
                        vendor_updates.sort(key=self._smart_date_sort_key, reverse=True)
                        recently_updates[vendor] = vendor_updates
        
        return recently_updates