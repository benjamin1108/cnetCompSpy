#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
import threading
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

class MetadataManager:
    """元数据管理器，负责管理所有元数据（爬虫和分析）"""
    
    # 创建类级别的锁，确保不同实例之间的线程安全
    _file_locks = {
        'crawler': threading.RLock(),
        'analysis': threading.RLock()
    }
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        初始化元数据管理器
        
        Args:
            base_dir: 项目根目录，如果为None则使用当前目录
        """
        if base_dir is None:
            # 默认使用项目根目录
            self.base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        else:
            self.base_dir = base_dir
        
        # 元数据文件路径
        self.metadata_dir = os.path.join(self.base_dir, 'data', 'metadata')
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        # 爬虫元数据文件路径
        self.crawler_metadata_file = os.path.join(self.metadata_dir, 'crawler_metadata.json')
        
        # 分析元数据文件路径
        self.analysis_metadata_file = os.path.join(self.metadata_dir, 'analysis_metadata.json')
        
        # 加载元数据
        self.crawler_metadata = self._load_metadata(self.crawler_metadata_file)
        self.analysis_metadata = self._load_metadata(self.analysis_metadata_file)
        
        # 创建实例级别的锁，用于内存中元数据的访问
        self.crawler_lock = threading.RLock()
        self.analysis_lock = threading.RLock()
        
        # 细化锁粒度，为每个vendor和source_type创建单独的锁
        self.crawler_vendor_locks: Dict[str, Dict[str, threading.RLock]] = {}
        for vendor in self.crawler_metadata:
            self.crawler_vendor_locks[vendor] = {}
            for source_type in self.crawler_metadata[vendor]:
                self.crawler_vendor_locks[vendor][source_type] = threading.RLock()
    
    def _load_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        加载元数据文件，使用适当的锁确保线程安全
        
        Args:
            file_path: 元数据文件路径
            
        Returns:
            元数据字典
        """
        from src.utils.metadata_utils import load_metadata
        
        lock_key = 'crawler' if 'crawler' in file_path else 'analysis'
        lock = self._file_locks[lock_key]
        
        # 定义更新锁的函数
        def update_locks(data: Dict[str, Any]) -> None:
            if lock_key == 'crawler' and hasattr(self, 'crawler_vendor_locks'):
                for vendor in data:
                    if vendor not in self.crawler_vendor_locks:
                        self.crawler_vendor_locks[vendor] = {}
                    for source_type in data[vendor]:
                        if source_type not in self.crawler_vendor_locks[vendor]:
                            self.crawler_vendor_locks[vendor][source_type] = threading.RLock()
        
        # 使用通用的元数据加载函数
        return load_metadata(
            file_path=file_path,
            lock=lock,
            update_locks_func=update_locks
        )
    
    def _save_metadata(self, file_path: str, metadata: Dict[str, Any]) -> None:
        """
        保存元数据到文件，使用适当的锁确保线程安全
        
        Args:
            file_path: 元数据文件路径
            metadata: 元数据字典
        """
        from src.utils.metadata_utils import save_metadata
        
        lock_key = 'crawler' if 'crawler' in file_path else 'analysis'
        lock = self._file_locks[lock_key]
        
        # 使用通用的元数据保存函数
        save_metadata(
            file_path=file_path,
            metadata=metadata,
            lock=lock
        )
    
    def save_crawler_metadata(self, vendor: Optional[str] = None, source_type: Optional[str] = None) -> None:
        """保存爬虫元数据到文件，线程安全，支持指定vendor和source_type以减少锁范围"""
        if vendor and source_type:
            if vendor in self.crawler_vendor_locks and source_type in self.crawler_vendor_locks[vendor]:
                with self.crawler_vendor_locks[vendor][source_type]:
                    with self.crawler_lock:
                        self._save_metadata(self.crawler_metadata_file, self.crawler_metadata)
            else:
                with self.crawler_lock:
                    self._save_metadata(self.crawler_metadata_file, self.crawler_metadata)
        else:
            with self.crawler_lock:
                self._save_metadata(self.crawler_metadata_file, self.crawler_metadata)
    
    def save_analysis_metadata(self) -> None:
        """保存分析元数据到文件，线程安全"""
        with self.analysis_lock:
            self._save_metadata(self.analysis_metadata_file, self.analysis_metadata)
    
    def get_crawler_metadata(self, vendor: str, source_type: str) -> Dict[str, Dict[str, Any]]:
        """
        获取指定厂商和源类型的爬虫元数据，线程安全
        
        Args:
            vendor: 厂商名称
            source_type: 源类型
            
        Returns:
            爬虫元数据字典
        """
        with self.crawler_lock:
            # 确保vendor和source_type存在
            if vendor not in self.crawler_metadata:
                self.crawler_metadata[vendor] = {}
            
            if source_type not in self.crawler_metadata[vendor]:
                self.crawler_metadata[vendor][source_type] = {}
            
            # 返回元数据的副本，避免直接修改
            return self.crawler_metadata[vendor][source_type].copy()
    
    def update_crawler_metadata(self, vendor: str, source_type: str, metadata: Dict[str, Dict[str, Any]]) -> None:
        """
        更新指定厂商和源类型的整个爬虫元数据字典，线程安全
        
        Args:
            vendor: 厂商名称
            source_type: 源类型
            metadata: 元数据字典
        """
        if vendor in self.crawler_vendor_locks and source_type in self.crawler_vendor_locks[vendor]:
            with self.crawler_vendor_locks[vendor][source_type]:
                with self.crawler_lock:
                    # 确保vendor存在
                    if vendor not in self.crawler_metadata:
                        self.crawler_metadata[vendor] = {}
                    
                    # 更新元数据
                    self.crawler_metadata[vendor][source_type] = metadata
                    
                    # 保存元数据
                    self.save_crawler_metadata(vendor, source_type)
        else:
            with self.crawler_lock:
                # 确保vendor存在
                if vendor not in self.crawler_metadata:
                    self.crawler_metadata[vendor] = {}
                
                # 更新元数据
                self.crawler_metadata[vendor][source_type] = metadata
                
                # 保存元数据
                self.save_crawler_metadata(vendor, source_type)
    
    def update_crawler_metadata_entry(self, vendor: str, source_type: str, url: str, data: Dict[str, Any], batch: bool = False) -> None:
        """
        更新指定URL的爬虫元数据，线程安全，支持批量更新
        
        Args:
            vendor: 厂商名称
            source_type: 源类型
            url: 文章URL
            data: 元数据
            batch: 是否为批量更新，如果为True则不立即保存文件
        """
        if vendor in self.crawler_vendor_locks and source_type in self.crawler_vendor_locks[vendor]:
            with self.crawler_vendor_locks[vendor][source_type]:
                with self.crawler_lock:
                    # 确保vendor和source_type存在
                    if vendor not in self.crawler_metadata:
                        self.crawler_metadata[vendor] = {}
                    
                    if source_type not in self.crawler_metadata[vendor]:
                        self.crawler_metadata[vendor][source_type] = {}
                    
                    # 更新元数据
                    self.crawler_metadata[vendor][source_type][url] = data
                    
                    # 如果不是批量更新，立即保存元数据
                    if not batch:
                        self.save_crawler_metadata(vendor, source_type)
        else:
            with self.crawler_lock:
                # 确保vendor和source_type存在
                if vendor not in self.crawler_metadata:
                    self.crawler_metadata[vendor] = {}
                
                if source_type not in self.crawler_metadata[vendor]:
                    self.crawler_metadata[vendor][source_type] = {}
                
                # 更新元数据
                self.crawler_metadata[vendor][source_type][url] = data
                
                # 如果不是批量更新，立即保存元数据
                if not batch:
                    self.save_crawler_metadata(vendor, source_type)
    
    def get_analysis_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        获取指定文件的分析元数据，线程安全
        
        Args:
            file_path: 文件路径
            
        Returns:
            分析元数据字典
        """
        with self.analysis_lock:
            # 标准化文件路径
            normalized_path = os.path.relpath(file_path, self.base_dir)
            
            # 确保文件路径存在
            if normalized_path not in self.analysis_metadata:
                self.analysis_metadata[normalized_path] = {}
            
            # 返回元数据的副本，避免直接修改
            return self.analysis_metadata[normalized_path].copy()
    
    def update_analysis_metadata(self, file_path: str, data: Dict[str, Any]) -> None:
        """
        更新分析元数据，线程安全
        
        Args:
            file_path: 文件路径
            data: 元数据
        """
        with self.analysis_lock:
            # 标准化文件路径
            normalized_path = os.path.relpath(file_path, self.base_dir)
            
            # 更新元数据
            if normalized_path not in self.analysis_metadata:
                self.analysis_metadata[normalized_path] = {}
            
            self.analysis_metadata[normalized_path].update(data)
            
            # 保存元数据
            self.save_analysis_metadata()
    
    def get_all_crawler_metadata(self) -> Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]:
        """
        获取所有爬虫元数据，线程安全
        
        Returns:
            所有爬虫元数据的副本
        """
        with self.crawler_lock:
            # 创建深拷贝以避免线程安全问题
            import copy
            return copy.deepcopy(self.crawler_metadata)
    
    def get_all_analysis_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有分析元数据，线程安全
        
        Returns:
            所有分析元数据的副本
        """
        with self.analysis_lock:
            # 创建深拷贝以避免线程安全问题
            import copy
            return copy.deepcopy(self.analysis_metadata)
    
    def get_crawler_metadata_by_filepath(self, file_path: str) -> Dict[str, Any]:
        """
        根据文件路径获取爬虫元数据，线程安全
        
        Args:
            file_path: 文件路径
            
        Returns:
            爬虫元数据
        """
        with self.crawler_lock:
            # 遍历所有爬虫元数据，查找匹配的文件路径
            for vendor, vendor_data in self.crawler_metadata.items():
                for source_type, source_data in vendor_data.items():
                    for url, metadata in source_data.items():
                        if metadata.get('filepath') == file_path:
                            return {
                                'url': url,
                                'title': metadata.get('title', ''),
                                'crawl_time': metadata.get('crawl_time', ''),
                                'vendor': vendor,
                                'source_type': source_type
                            }
            
            return {}
    
    def get_files_by_vendor_and_type(self, vendor: str, source_type: str) -> List[str]:
        """
        获取指定厂商和源类型的所有文件路径，线程安全
        
        Args:
            vendor: 厂商名称
            source_type: 源类型
            
        Returns:
            文件路径列表
        """
        with self.crawler_lock:
            files = []
            
            # 获取指定厂商和源类型的元数据
            if vendor in self.crawler_metadata and source_type in self.crawler_metadata[vendor]:
                vendor_metadata = self.crawler_metadata[vendor][source_type]
                
                # 提取文件路径
                for url, metadata in vendor_metadata.items():
                    if 'filepath' in metadata:
                        files.append(metadata['filepath'])
            
            return files
    
    def check_analysis_tasks(self, file_path: str, tasks: Optional[List[str]] = None) -> bool:
        """
        检查文件的分析任务是否全部完成，线程安全
        
        Args:
            file_path: 文件路径
            tasks: 任务列表，如果为None则检查所有任务
            
        Returns:
            True如果所有任务都已完成，否则False
        """
        with self.analysis_lock:
            # 标准化文件路径
            normalized_path = os.path.relpath(file_path, self.base_dir)
            
            # 如果文件不在分析元数据中，返回False
            if normalized_path not in self.analysis_metadata:
                return False
            
            # 获取文件的分析元数据
            file_metadata = self.analysis_metadata[normalized_path]
            
            # 如果没有指定任务列表，则认为只要有任务记录就算完成
            if not tasks:
                return 'tasks' in file_metadata and bool(file_metadata['tasks'])
            
            # 如果指定了任务列表，则检查每个任务是否都已完成
            if 'tasks' not in file_metadata:
                return False
            
            completed_tasks = file_metadata['tasks']
            for task in tasks:
                if task not in completed_tasks:
                    return False
            
            return True
    
    def migrate_legacy_metadata(self) -> None:
        """
        迁移旧的元数据文件到新的聚合文件
        """
        # 迁移爬虫元数据
        self._migrate_legacy_crawler_metadata()
        
        # 迁移分析元数据（如果需要）
        # 分析元数据已经是聚合的，不需要迁移
    
    def update_crawler_metadata_entries_batch(self, vendor: str, source_type: str, entries: Dict[str, Dict[str, Any]]) -> None:
        """
        批量更新多个URL的爬虫元数据，线程安全，减少文件写入次数，使用事务机制确保一致性
        
        Args:
            vendor: 厂商名称
            source_type: 源类型
            entries: 元数据字典，键为URL，值为元数据
        """
        if not entries:
            return
            
        if vendor in self.crawler_vendor_locks and source_type in self.crawler_vendor_locks[vendor]:
            with self.crawler_vendor_locks[vendor][source_type]:
                with self.crawler_lock:
                    # 创建metadata的副本，实现事务机制
                    import copy
                    metadata_copy = copy.deepcopy(self.crawler_metadata)
                    
                    # 确保vendor和source_type存在
                    if vendor not in metadata_copy:
                        metadata_copy[vendor] = {}
                    
                    if source_type not in metadata_copy[vendor]:
                        metadata_copy[vendor][source_type] = {}
                    
                    # 在副本上批量更新元数据，只更新指定的vendor和source_type，保留其他厂商的数据
                    for url, data in entries.items():
                        metadata_copy[vendor][source_type][url] = data
                    
                    # 一次性更新内存中的metadata和文件
                    self.crawler_metadata = metadata_copy
                    self._save_metadata(self.crawler_metadata_file, self.crawler_metadata)
                    logger.info(f"批量更新了 {len(entries)} 个URL的元数据，保留了其他厂商的数据")
        else:
            with self.crawler_lock:
                # 创建metadata的副本，实现事务机制
                import copy
                metadata_copy = copy.deepcopy(self.crawler_metadata)
                
                # 确保vendor和source_type存在
                if vendor not in metadata_copy:
                    metadata_copy[vendor] = {}
                
                if source_type not in metadata_copy[vendor]:
                    metadata_copy[vendor][source_type] = {}
                
                # 在副本上批量更新元数据，只更新指定的vendor和source_type，保留其他厂商的数据
                for url, data in entries.items():
                    metadata_copy[vendor][source_type][url] = data
                
                # 一次性更新内存中的metadata和文件
                self.crawler_metadata = metadata_copy
                self._save_metadata(self.crawler_metadata_file, self.crawler_metadata)
                logger.info(f"批量更新了 {len(entries)} 个URL的元数据，保留了其他厂商的数据")
    
    def _migrate_legacy_crawler_metadata(self) -> None:
        """
        迁移旧的爬虫元数据文件到新的聚合文件
        """
        legacy_files = [f for f in os.listdir(self.metadata_dir) if f.endswith('_metadata.json') and f != 'crawler_metadata.json' and f != 'analysis_metadata.json']
        
        for legacy_file in legacy_files:
            try:
                # 从文件名中提取vendor和source_type
                parts = legacy_file.split('_metadata.json')[0].split('_')
                if len(parts) >= 2:
                    vendor = parts[0]
                    source_type = '_'.join(parts[1:])
                    
                    # 加载旧的元数据文件
                    legacy_file_path = os.path.join(self.metadata_dir, legacy_file)
                    with open(legacy_file_path, 'r', encoding='utf-8') as f:
                        legacy_metadata = json.load(f)
                    
                    # 更新聚合元数据
                    if vendor not in self.crawler_metadata:
                        self.crawler_metadata[vendor] = {}
                    
                    if source_type not in self.crawler_metadata[vendor]:
                        self.crawler_metadata[vendor][source_type] = {}
                    
                    # 合并元数据
                    self.crawler_metadata[vendor][source_type].update(legacy_metadata)
                    
                    logger.info(f"已迁移元数据文件: {legacy_file}")
            except Exception as e:
                logger.error(f"迁移元数据文件失败: {legacy_file} - {e}")
        
        # 保存聚合元数据
        self.save_crawler_metadata()
        
        # 备份旧的元数据文件
        for legacy_file in legacy_files:
            try:
                legacy_file_path = os.path.join(self.metadata_dir, legacy_file)
                backup_file_path = os.path.join(self.metadata_dir, f"{legacy_file}.bak")
                os.rename(legacy_file_path, backup_file_path)
                logger.info(f"已备份元数据文件: {legacy_file} -> {legacy_file}.bak")
            except Exception as e:
                logger.error(f"备份元数据文件失败: {legacy_file} - {e}")
