#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import logging
import os
import sys
import threading
import queue
import concurrent.futures
from typing import Dict, Any, List, Optional

from src.utils.process_lock_manager import ProcessLockManager, ProcessType

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
        # 获取最大工作线程数，默认为1（单线程）
        self.max_workers = config.get('crawler', {}).get('max_workers', 1)
        # 创建线程锁，用于保护共享资源
        self.lock = threading.RLock()
        # 创建结果队列，用于线程安全地收集结果
        self.result_queue = queue.Queue()
        
        # 创建共享的MetadataManager实例，确保所有爬虫线程使用同一个实例
        # 获取项目根目录路径
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # 导入MetadataManager
        from src.utils.metadata_manager import MetadataManager
        self.metadata_manager = MetadataManager(base_dir)
        
        # 创建metadata锁，用于保护metadata的访问
        self.metadata_lock = threading.RLock()
        
        # 初始化进程锁管理器
        self.process_lock_manager = ProcessLockManager.get_instance(ProcessType.CRAWLER)
        self.lock_acquired = False
    
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
            
            return crawler_class
        except (ImportError, AttributeError) as e:
            logger.warning(f"加载特定爬虫类失败，将使用通用爬虫类: {e}")
            
            # 加载通用爬虫类
            try:
                module_name = f"src.crawlers.vendors.{vendor}.generic_crawler"
                class_name = f"{vendor.capitalize()}GenericCrawler"
                
                module = importlib.import_module(module_name)
                crawler_class = getattr(module, class_name)
                
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
        
        # 创建爬虫实例，并传入共享的MetadataManager实例
        crawler = crawler_class(config_copy, vendor, source_type)
        
        # 替换爬虫实例中的MetadataManager为共享实例
        crawler.metadata_manager = self.metadata_manager
        # 重新加载metadata，确保使用最新的数据
        crawler.metadata = crawler.metadata_manager.get_crawler_metadata(vendor, source_type)
        
        return crawler.run()
    
    def _worker(self, vendor: str, source_type: str, source_config: Dict[str, Any]):
        """
        工作线程函数，用于执行爬虫任务
        
        Args:
            vendor: 厂商名称
            source_type: 源类型
            source_config: 源配置
        """
        try:
            logger.info(f"线程开始执行爬虫任务: {vendor}/{source_type}")
            result = self.run_crawler(vendor, source_type, source_config)
            
            # 线程安全地将结果放入队列
            self.result_queue.put((vendor, source_type, result))
            logger.info(f"爬虫任务完成并添加到结果队列: {vendor}/{source_type}, 获取了 {len(result)} 个文件")
        except Exception as e:
            logger.error(f"爬虫任务异常: {vendor} {source_type} - {e}")
            self.result_queue.put((vendor, source_type, []))
    
    def run_multi_threaded(self) -> Dict[str, Dict[str, List[str]]]:
        """
        使用线程池运行所有爬虫（多线程并行执行）
        
        Returns:
            爬取结果，格式为 {vendor: {source_type: [file_paths]}}
        """
        results = {}
        crawl_tasks = []
        
        # 收集所有爬虫任务
        for vendor, vendor_sources in self.sources.items():
            for source_type, source_config in vendor_sources.items():
                crawl_tasks.append((vendor, source_type, source_config))
        
        logger.info(f"共有 {len(crawl_tasks)} 个爬虫任务，使用 {self.max_workers} 个线程执行")
        
        # --- 开始：添加模块预加载逻辑 ---
        modules_to_preload = set()
        logger.info("开始预加载爬虫模块...")
        for vendor, source_type, _ in crawl_tasks:
            try:
                # 尝试构建特定爬虫模块名
                module_source_type = source_type.replace('-', '_')
                specific_module_name = f"src.crawlers.vendors.{vendor}.{module_source_type}_crawler"
                modules_to_preload.add(specific_module_name)

                # 也可以考虑预加载通用爬虫，但优先确保特定爬虫加载
                # generic_module_name = f"src.crawlers.vendors.{vendor}.generic_crawler"
                # modules_to_preload.add(generic_module_name)

            except Exception as e:
                # 在构建模块名时不太可能出错，但以防万一
                logger.warning(f"构建模块名时出错 ({vendor}/{source_type}): {e}")

        loaded_count = 0
        failed_count = 0
        for module_name in modules_to_preload:
            try:
                importlib.import_module(module_name)
                loaded_count += 1
            except ImportError:
                # _get_crawler_class 稍后会处理加载通用爬虫的情况，这里只记录警告
                logger.warning(f"预加载模块失败 (ImportError): {module_name} - 将在运行时尝试加载通用爬虫")
                failed_count += 1
            except Exception as e:
                logger.error(f"预加载模块时发生意外错误: {module_name} - {e}")
                failed_count += 1

        logger.info(f"模块预加载完成: 成功 {loaded_count} 个, 失败/跳过 {failed_count} 个")
        # --- 结束：添加模块预加载逻辑 ---
        
        # 使用线程池执行爬虫任务
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for vendor, source_type, source_config in crawl_tasks:
                executor.submit(self._worker, vendor, source_type, source_config)
        
        # 处理队列中的所有结果
        while not self.result_queue.empty():
            vendor, source_type, result = self.result_queue.get()
            
            # 线程安全地更新结果字典
            with self.lock:
                if vendor not in results:
                    results[vendor] = {}
                results[vendor][source_type] = result
        
        # 确保所有metadata都已保存
        logger.info("所有爬虫任务完成，确保所有metadata都已保存")
        self.metadata_manager.save_crawler_metadata()
        
        return results
    
    def run(self) -> Dict[str, Dict[str, List[str]]]:
        """
        运行所有爬虫
        
        如果max_workers > 1则使用多线程执行，否则使用单线程顺序执行
        
        Returns:
            爬取结果，格式为 {vendor: {source_type: [file_paths]}}
        """
        # 获取进程锁，确保同一时间只有一个爬虫进程在运行
        if not self.process_lock_manager.acquire_lock():
            logger.error("无法获取爬虫进程锁，可能有其他爬虫进程正在运行或互斥进程正在运行")
            return {}
        
        self.lock_acquired = True
        logger.info("已获取爬虫进程锁，开始执行爬虫任务")
        
        try:
            # 根据配置决定使用多线程还是单线程
            if self.max_workers > 1:
                logger.info(f"使用多线程模式运行爬虫，线程数: {self.max_workers}")
                return self.run_multi_threaded()
            
            # 单线程执行模式
            logger.info("使用单线程模式顺序运行爬虫")
            results = {}
            
            # 遍历所有数据源
            for vendor, vendor_sources in self.sources.items():
                results[vendor] = {}
                
                for source_type, source_config in vendor_sources.items():
                    logger.info(f"开始执行爬虫任务: {vendor}/{source_type}")
                    try:
                        # 直接运行爬虫，不使用线程池
                        result = self.run_crawler(vendor, source_type, source_config)
                        results[vendor][source_type] = result
                        logger.info(f"爬虫任务完成: {vendor}/{source_type}, 获取了 {len(result)} 个文件")
                    except Exception as e:
                        logger.error(f"爬虫任务异常: {vendor} {source_type} - {e}")
                        results[vendor][source_type] = []
            
            return results
        finally:
            # 释放进程锁
            if self.lock_acquired:
                self.process_lock_manager.release_lock()
                logger.info("已释放爬虫进程锁")
