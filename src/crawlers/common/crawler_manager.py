#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List

# 确保src目录在路径中
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

logger = logging.getLogger(__name__)

class CrawlerManager:
    """爬虫管理器，负责调度各个爬虫"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化爬虫管理器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.sources = config.get('sources', {})
        self.max_workers = config.get('crawler', {}).get('max_workers', 4)
    
    def _get_crawler_class(self, vendor: str, source_type: str):
        """
        动态加载爬虫类
        
        Args:
            vendor: 厂商名称
            source_type: 源类型
            
        Returns:
            爬虫类
        """
        try:
            # 处理source_type中的连字符，转换为下划线格式
            module_source_type = source_type.replace('-', '_')
            
            # 组装模块名和类名
            module_name = f"src.crawlers.vendors.{vendor}.{module_source_type}_crawler"
            
            # 首字母大写，并移除连字符
            class_source_type = ''.join(word.capitalize() for word in source_type.split('-'))
            class_name = f"{vendor.capitalize()}{class_source_type}Crawler"
            
            logger.debug(f"尝试加载模块: {module_name}, 类: {class_name}")
            
            module = importlib.import_module(module_name)
            crawler_class = getattr(module, class_name)
            
            logger.debug(f"已加载爬虫类: {class_name}")
            return crawler_class
        except (ImportError, AttributeError) as e:
            logger.warning(f"加载特定爬虫类失败，将使用通用爬虫类: {e}")
            
            # 加载通用爬虫类
            try:
                module_name = f"src.crawlers.vendors.{vendor}.generic_crawler"
                class_name = f"{vendor.capitalize()}GenericCrawler"
                
                module = importlib.import_module(module_name)
                crawler_class = getattr(module, class_name)
                
                logger.debug(f"已加载通用爬虫类: {class_name}")
                return crawler_class
            except (ImportError, AttributeError) as e:
                logger.error(f"加载通用爬虫类失败: {e}")
                return None
    
    def run_crawler(self, vendor: str, source_type: str, source_config: Dict[str, Any]) -> List[str]:
        """
        运行单个爬虫
        
        Args:
            vendor: 厂商名称
            source_type: 源类型
            source_config: 源配置
            
        Returns:
            爬取结果文件路径列表
        """
        crawler_class = self._get_crawler_class(vendor, source_type)
        if not crawler_class:
            logger.error(f"未找到合适的爬虫类: {vendor} {source_type}")
            return []
        
        # 确保配置中包含正确的测试模式和文章数量限制设置
        config_copy = self.config.copy()
        
        # 将source_config合并到配置中，确保所有参数正确传递
        if 'sources' not in config_copy:
            config_copy['sources'] = {}
        if vendor not in config_copy['sources']:
            config_copy['sources'][vendor] = {}
        config_copy['sources'][vendor][source_type] = source_config
        
        logger.info(f"启动爬虫: {vendor}/{source_type}, " + 
                   f"测试模式: {source_config.get('test_mode', False)}, " + 
                   f"文章限制: {config_copy.get('crawler', {}).get('article_limit', '未设置')}")
        
        crawler = crawler_class(config_copy, vendor, source_type)
        return crawler.run()
    
    def run(self) -> Dict[str, Dict[str, List[str]]]:
        """
        运行所有爬虫
        
        Returns:
            爬取结果，格式为 {vendor: {source_type: [file_paths]}}
        """
        results = {}
        futures = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 遍历所有数据源
            for vendor, vendor_sources in self.sources.items():
                results[vendor] = {}
                
                for source_type, source_config in vendor_sources.items():
                    # 提交爬虫任务
                    future = executor.submit(
                        self.run_crawler,
                        vendor,
                        source_type,
                        source_config
                    )
                    futures.append((future, vendor, source_type))
            
            # 收集结果
            for future, vendor, source_type in futures:
                try:
                    result = future.result()
                    results[vendor][source_type] = result
                except Exception as e:
                    logger.error(f"爬虫任务异常: {vendor} {source_type} - {e}")
                    results[vendor][source_type] = []
        
        return results 