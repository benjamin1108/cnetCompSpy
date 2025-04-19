#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器 - 统计管理器

负责处理统计相关的功能，如分析元数据文件、获取缺失分析文件等。
"""

import os
import logging
from typing import Dict, List, Any

class StatsManager:
    """统计管理器类"""
    
    def __init__(self, data_dir: str):
        """
        初始化统计管理器
        
        Args:
            data_dir: 数据目录路径
        """
        self.logger = logging.getLogger(__name__)
        self.data_dir = data_dir
        
        self.logger.info("统计管理器初始化完成")
    
    def analyze_metadata_files(self, detailed: bool = False) -> Dict[str, Any]:
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
    
    def get_missing_analysis_files(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        获取缺失AI分析的文件
        
        Returns:
            Dict: 按厂商和类型分组的缺失AI分析的文件列表
        """
        # 获取统计数据
        stats_data = self.analyze_metadata_files(detailed=True)
        
        # 提取缺失AI分析的文件
        missing_analysis = {}
        
        for vendor, vendor_data in stats_data.get('details', {}).items():
            for source_type, files in vendor_data.items():
                for file_info in files:
                    # 如果文件没有AI分析或者AI任务未完成
                    if not file_info.get('has_analysis') or not file_info.get('tasks_completed'):
                        if vendor not in missing_analysis:
                            missing_analysis[vendor] = {}
                        
                        if source_type not in missing_analysis[vendor]:
                            missing_analysis[vendor][source_type] = []
                        
                        missing_analysis[vendor][source_type].append({
                            'filename': file_info['filename'],
                            'title': file_info.get('title', file_info['filename']),
                            'has_analysis': file_info.get('has_analysis', False),
                            'tasks_completed': file_info.get('tasks_completed', False),
                            'path': f"{vendor}/{source_type}/{file_info['filename']}"
                        })
        
        return missing_analysis
