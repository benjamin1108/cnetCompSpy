#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

class MetadataManager:
    """元数据管理器，负责管理所有元数据（爬虫和分析）"""
    
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
    
    def _load_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        加载元数据文件
        
        Args:
            file_path: 元数据文件路径
            
        Returns:
            元数据字典
        """
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载元数据文件失败: {file_path} - {e}")
                return {}
        return {}
    
    def _save_metadata(self, file_path: str, metadata: Dict[str, Any]) -> None:
        """
        保存元数据到文件
        
        Args:
            file_path: 元数据文件路径
            metadata: 元数据字典
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            logger.debug(f"元数据已保存到: {file_path}")
        except Exception as e:
            logger.error(f"保存元数据文件失败: {file_path} - {e}")
    
    def save_crawler_metadata(self) -> None:
        """保存爬虫元数据到文件"""
        self._save_metadata(self.crawler_metadata_file, self.crawler_metadata)
    
    def save_analysis_metadata(self) -> None:
        """保存分析元数据到文件"""
        self._save_metadata(self.analysis_metadata_file, self.analysis_metadata)
    
    def get_crawler_metadata(self, vendor: str, source_type: str) -> Dict[str, Dict[str, Any]]:
        """
        获取指定厂商和源类型的爬虫元数据
        
        Args:
            vendor: 厂商名称
            source_type: 源类型
            
        Returns:
            爬虫元数据字典
        """
        # 确保vendor和source_type存在
        if vendor not in self.crawler_metadata:
            self.crawler_metadata[vendor] = {}
        
        if source_type not in self.crawler_metadata[vendor]:
            self.crawler_metadata[vendor][source_type] = {}
        
        return self.crawler_metadata[vendor][source_type]
    
    def update_crawler_metadata(self, vendor: str, source_type: str, url: str, data: Dict[str, Any]) -> None:
        """
        更新爬虫元数据
        
        Args:
            vendor: 厂商名称
            source_type: 源类型
            url: 文章URL
            data: 元数据
        """
        # 获取指定厂商和源类型的元数据
        vendor_metadata = self.get_crawler_metadata(vendor, source_type)
        
        # 更新元数据
        vendor_metadata[url] = data
        
        # 保存元数据
        self.save_crawler_metadata()
    
    def get_analysis_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        获取指定文件的分析元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            分析元数据字典
        """
        # 标准化文件路径
        normalized_path = os.path.relpath(file_path, self.base_dir)
        
        # 确保文件路径存在
        if normalized_path not in self.analysis_metadata:
            self.analysis_metadata[normalized_path] = {}
        
        return self.analysis_metadata[normalized_path]
    
    def update_analysis_metadata(self, file_path: str, data: Dict[str, Any]) -> None:
        """
        更新分析元数据
        
        Args:
            file_path: 文件路径
            data: 元数据
        """
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
        获取所有爬虫元数据
        
        Returns:
            所有爬虫元数据
        """
        return self.crawler_metadata
    
    def get_all_analysis_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有分析元数据
        
        Returns:
            所有分析元数据
        """
        return self.analysis_metadata
    
    def get_crawler_metadata_by_filepath(self, file_path: str) -> Dict[str, Any]:
        """
        根据文件路径获取爬虫元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            爬虫元数据
        """
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
        获取指定厂商和源类型的所有文件路径
        
        Args:
            vendor: 厂商名称
            source_type: 源类型
            
        Returns:
            文件路径列表
        """
        files = []
        
        # 获取指定厂商和源类型的元数据
        vendor_metadata = self.get_crawler_metadata(vendor, source_type)
        
        # 提取文件路径
        for url, metadata in vendor_metadata.items():
            if 'filepath' in metadata:
                files.append(metadata['filepath'])
        
        return files
    
    def check_analysis_tasks(self, file_path: str, tasks: Optional[List[str]] = None) -> bool:
        """
        检查文件的分析任务是否全部完成
        
        Args:
            file_path: 文件路径
            tasks: 任务列表，如果为None则检查所有任务
            
        Returns:
            True如果所有任务都已完成，否则False
        """
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
        
        # 检查是否所有指定的任务都成功完成
        all_tasks_completed = True
        for task_type in tasks:
            task_status = file_metadata.get('tasks', {}).get(task_type, {})
            if not task_status.get('success', False):
                all_tasks_completed = False
                break
        
        return all_tasks_completed
    
    def migrate_legacy_metadata(self) -> None:
        """
        迁移旧的元数据文件到新的聚合文件
        """
        # 迁移爬虫元数据
        self._migrate_legacy_crawler_metadata()
        
        # 迁移分析元数据（如果需要）
        # 分析元数据已经是聚合的，不需要迁移
    
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
