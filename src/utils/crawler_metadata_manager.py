#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class CrawlerMetadataManager:
    """爬虫元数据管理器，负责管理所有爬虫的元数据"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        初始化爬虫元数据管理器
        
        Args:
            base_dir: 项目根目录，如果为None则使用当前目录
        """
        if base_dir is None:
            # 默认使用项目根目录
            self.base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        else:
            self.base_dir = base_dir
        
        # 聚合元数据文件路径
        self.metadata_file = os.path.join(self.base_dir, 'data', 'metadata', 'crawler_metadata.json')
        os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
        
        # 加载元数据
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        加载元数据文件
        
        Returns:
            元数据字典，包含所有爬虫的元数据
        """
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载元数据文件失败: {e}")
                return {}
        return {}
    
    def save_metadata(self) -> None:
        """保存元数据到文件"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            logger.debug(f"元数据已保存到: {self.metadata_file}")
        except Exception as e:
            logger.error(f"保存元数据文件失败: {e}")
    
    def get_metadata(self, vendor: str, source_type: str) -> Dict[str, Dict[str, Any]]:
        """
        获取指定厂商和源类型的元数据
        
        Args:
            vendor: 厂商名称
            source_type: 源类型
            
        Returns:
            元数据字典
        """
        # 确保vendor和source_type存在
        if vendor not in self.metadata:
            self.metadata[vendor] = {}
        
        if source_type not in self.metadata[vendor]:
            self.metadata[vendor][source_type] = {}
        
        return self.metadata[vendor][source_type]
    
    def update_metadata(self, vendor: str, source_type: str, url: str, data: Dict[str, Any]) -> None:
        """
        更新元数据
        
        Args:
            vendor: 厂商名称
            source_type: 源类型
            url: 文章URL
            data: 元数据
        """
        # 获取指定厂商和源类型的元数据
        vendor_metadata = self.get_metadata(vendor, source_type)
        
        # 更新元数据
        vendor_metadata[url] = data
        
        # 保存元数据
        self.save_metadata()
    
    def get_all_metadata(self) -> Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]:
        """
        获取所有元数据
        
        Returns:
            所有元数据
        """
        return self.metadata
    
    def migrate_legacy_metadata(self) -> None:
        """
        迁移旧的元数据文件到新的聚合文件
        """
        metadata_dir = os.path.join(self.base_dir, 'data', 'metadata')
        legacy_files = [f for f in os.listdir(metadata_dir) if f.endswith('_metadata.json') and f != 'crawler_metadata.json' and f != 'analysis_metadata.json']
        
        for legacy_file in legacy_files:
            try:
                # 从文件名中提取vendor和source_type
                parts = legacy_file.split('_metadata.json')[0].split('_')
                if len(parts) >= 2:
                    vendor = parts[0]
                    source_type = '_'.join(parts[1:])
                    
                    # 加载旧的元数据文件
                    legacy_file_path = os.path.join(metadata_dir, legacy_file)
                    with open(legacy_file_path, 'r', encoding='utf-8') as f:
                        legacy_metadata = json.load(f)
                    
                    # 更新聚合元数据
                    if vendor not in self.metadata:
                        self.metadata[vendor] = {}
                    
                    if source_type not in self.metadata[vendor]:
                        self.metadata[vendor][source_type] = {}
                    
                    # 合并元数据
                    self.metadata[vendor][source_type].update(legacy_metadata)
                    
                    logger.info(f"已迁移元数据文件: {legacy_file}")
            except Exception as e:
                logger.error(f"迁移元数据文件失败: {legacy_file} - {e}")
        
        # 保存聚合元数据
        self.save_metadata()
        
        # 备份旧的元数据文件
        for legacy_file in legacy_files:
            try:
                legacy_file_path = os.path.join(metadata_dir, legacy_file)
                backup_file_path = os.path.join(metadata_dir, f"{legacy_file}.bak")
                os.rename(legacy_file_path, backup_file_path)
                logger.info(f"已备份元数据文件: {legacy_file} -> {legacy_file}.bak")
            except Exception as e:
                logger.error(f"备份元数据文件失败: {legacy_file} - {e}")
