#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import importlib
import json
import logging
import os
import re
import shutil
import sys
import time
import yaml
from typing import Dict, Any, List, Optional
from copy import deepcopy

import tqdm

# 添加项目根目录到路径
base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, base_dir)

from src.utils.colored_logger import setup_colored_logging

logger = logging.getLogger(__name__)
logger.info(f"已将项目根目录添加到路径: {base_dir}")

from src.crawlers.common.crawler_manager import CrawlerManager
from src.ai_analyzer.analyzer import AIAnalyzer

# 移除原有的日志配置代码，由main函数中的setup_colored_logging替代
logger = logging.getLogger(__name__)

# 配置第三方库的日志级别
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('filelock').setLevel(logging.WARNING)

# 默认配置
DEFAULT_CONFIG = {
    'crawlers': {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'timeout': 10,
        'retry': 3,
        'auto_driver': True,
        'vendors': {
            'aws': {
                'enabled': True,
                'base_url': 'https://aws.amazon.com',
                'blog_url': 'https://aws.amazon.com/blogs/'
            },
            'azure': {
                'enabled': False,
                'base_url': 'https://azure.microsoft.com',
                'blog_url': 'https://azure.microsoft.com/en-us/blog/'
            },
            'google_cloud': {
                'enabled': False,
                'base_url': 'https://cloud.google.com',
                'blog_url': 'https://cloud.google.com/blog/'
            }
        }
    },
    'ai_service': {
        'model': 'openai/gpt-3.5-turbo',
        'temperature': 0.7,
        'max_tokens': 2048
    }
}

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    深度合并配置字典
    
    Args:
        base_config: 基础配置字典
        override_config: 覆盖配置字典
        
    Returns:
        Dict: 合并后的配置字典
    """
    result = deepcopy(base_config)
    
    for key, value in override_config.items():
        # 如果键存在且两个值都是字典，则递归合并
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            # 否则直接覆盖或添加
            result[key] = value
            
    return result

def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    加载YAML文件
    
    Args:
        file_path: YAML文件路径
        
    Returns:
        Dict: YAML文件内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        logger.warning(f"配置文件不存在: {file_path}")
        return {}
    except Exception as e:
        logger.error(f"加载配置文件时出错: {e}")
        return {}

def get_config(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Load config from yaml file and merge with command line arguments.
    """
    config = DEFAULT_CONFIG.copy()
    
    # 获取项目根目录路径
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # 加载主配置文件
    config_path_yaml = os.path.join(base_dir, 'config.yaml')
    if os.path.exists(config_path_yaml):
        config_data = load_yaml_file(config_path_yaml)
        config = merge_configs(config, config_data)
        logger.info(f"已加载主配置: {config_path_yaml}")
    else:
        logger.warning(f"主配置文件不存在: {config_path_yaml}")
    
    # 加载敏感配置文件
    secret_config_path = os.path.join(base_dir, 'config.secret.yaml')
    if os.path.exists(secret_config_path):
        secret_config_data = load_yaml_file(secret_config_path)
        config = merge_configs(config, secret_config_data)
        logger.info(f"已加载敏感配置: {secret_config_path}")
    else:
        logger.warning(f"敏感配置文件不存在: {secret_config_path}")
    
    return config

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="云计算竞争情报爬虫")
    parser.add_argument("--mode", choices=["crawl", "analyze", "test"], help="运行模式: crawl(爬取数据), analyze(分析数据), test(测试模式)")
    parser.add_argument("--vendor", help="爬取指定厂商的数据, 如aws, azure等")
    parser.add_argument("--clean", action="store_true", help="清理所有中间文件")
    parser.add_argument("--limit", type=int, default=0, help="爬取的文章数量限制，如设置为5则每个来源只爬取5篇")
    parser.add_argument("--config", help="指定配置文件路径")
    parser.add_argument("--force", action="store_true", help="强制执行，忽略本地metadata或文件是否已存在")
    parser.add_argument("--file", help="指定要分析的文件路径，仅在analyze模式下有效")
    
    return parser.parse_args()

def clean_data_dir(data_dir: str, dry_run: bool = False) -> None:
    """
    Clean data directory.
    """
    logger.info("开始清理数据目录...")
    
    # 获取项目根目录
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data")
    
    # 清理raw目录下的各个厂商目录
    raw_dir = os.path.join(data_dir, "raw")
    if os.path.exists(raw_dir):
        for vendor in ["aws", "azure", "gcp"]:
            vendor_dir = os.path.join(raw_dir, vendor)
            if os.path.exists(vendor_dir):
                logger.info(f"删除目录: {vendor_dir}")
                if not dry_run:
                    shutil.rmtree(vendor_dir)
    
    # 清理analyzed目录下的各个厂商目录
    analysis_dir = os.path.join(data_dir, "analysis")
    if os.path.exists(analysis_dir):
        for vendor in ["aws", "azure", "gcp"]:
            vendor_dir = os.path.join(analysis_dir, vendor)
            if os.path.exists(vendor_dir):
                logger.info(f"删除目录: {vendor_dir}")
                if not dry_run:
                    shutil.rmtree(vendor_dir)
    
    logger.info("所有数据目录清理完成")

def crawl_main(args: argparse.Namespace) -> None:
    """
    Main function for crawling.
    """
    config = get_config(args)
    
    # 如果指定了厂商，过滤配置
    if args.vendor:
        sources = config.get('sources', {})
        # 只保留指定厂商的配置
        filtered_sources = {args.vendor: sources.get(args.vendor, {})} if args.vendor in sources else {}
        # 如果厂商不存在，给出警告
        if not filtered_sources:
            logger.warning(f"未找到厂商 {args.vendor} 的配置，请检查配置文件和厂商名称")
            return
        config['sources'] = filtered_sources
    
    # 如果设置了文章数量限制，更新配置
    if args.limit > 0:
        logger.info(f"设置每个来源的文章数量限制为: {args.limit}")
        if 'crawler' not in config:
            config['crawler'] = {}
        config['crawler']['article_limit'] = args.limit
    
    # 如果设置了force参数，更新配置
    if args.force:
        logger.info("启用强制模式，忽略本地metadata或文件是否已存在")
        if 'crawler' not in config:
            config['crawler'] = {}
        config['crawler']['force'] = True
    
    # 创建并运行爬虫管理器
    crawler_manager = CrawlerManager(config)
    result = crawler_manager.run()
    
    # 记录爬取结果
    for vendor_name, vendor_results in result.items():
        for source_type, files in vendor_results.items():
            file_count = len(files)
            logger.info(f"爬取完成: {vendor_name} {source_type}, 共 {file_count} 个文件")

def test_main(args: argparse.Namespace) -> None:
    """
    Main function for testing.
    """
    # 清理数据
    clean_data_dir(os.path.dirname(os.path.dirname(__file__)), True)
    
    # 加载配置并设置测试模式
    config = get_config(args)
    
    # 为所有厂商和来源设置测试模式
    for vendor_name, vendor_config in config.get('sources', {}).items():
        for source_name, source_config in vendor_config.items():
            source_config['test_mode'] = True
    
    # 爬取
    crawl_main(args)
    
    # 分析
    analyze_main(args)

def analyze_main(args: argparse.Namespace) -> None:
    """
    Main function for analyzing.
    """
    # 加载配置
    config = get_config(args)
    
    # 如果指定了厂商，过滤配置
    if args.vendor:
        # 创建一个过滤函数，用于筛选指定厂商的文件
        def vendor_filter(file_path):
            return f"/{args.vendor}/" in file_path
        
        logger.info(f"仅分析厂商 {args.vendor} 的数据")
        if 'ai_analyzer' not in config:
            config['ai_analyzer'] = {}
        config['ai_analyzer']['vendor_filter'] = vendor_filter
    
    # 如果设置了force参数，更新配置
    if args.force:
        logger.info("启用强制模式，忽略文件是否已存在")
        if 'ai_analyzer' not in config:
            config['ai_analyzer'] = {}
        config['ai_analyzer']['force'] = True
    
    # 如果设置了文章数量限制，更新配置
    if args.limit > 0:
        logger.info(f"设置分析文件数量限制为: {args.limit}")
        if 'ai_analyzer' not in config:
            config['ai_analyzer'] = {}
        config['ai_analyzer']['file_limit'] = args.limit
    
    # 如果指定了文件路径，只分析该文件
    if args.file:
        file_path = args.file
        # 如果文件路径不是绝对路径，则转换为相对于当前工作目录的路径
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        
        logger.info(f"仅分析指定文件: {file_path}")
        if 'ai_analyzer' not in config:
            config['ai_analyzer'] = {}
        config['ai_analyzer']['specific_file'] = file_path
    
    # 创建并运行AI分析器
    analyzer = AIAnalyzer(config)
    analyzer.analyze_all()

def main() -> None:
    """
    Main entry point.
    """
    # 使用彩色日志替换原有的日志配置
    base_dir = os.path.dirname(os.path.dirname(__file__))
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # 使用时间戳作为日志文件名，避免冲突
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"cnetCompSpy_{timestamp}.log")
    
    setup_colored_logging(
        level=logging.INFO,
        log_file=log_file,
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger.info(f"日志文件路径: {log_file}")
    
    # 设置第三方库的日志级别
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('filelock').setLevel(logging.WARNING)
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 如果指定了clean参数，清理数据目录
    if args.clean:
        clean_data_dir(os.path.dirname(os.path.dirname(__file__)), True)
        if not args.mode:
            return
    
    # 根据运行模式执行相应操作
    if args.mode == "crawl":
        logger.info("运行模式: crawl")
        crawl_main(args)
    elif args.mode == "analyze":
        logger.info("运行模式: analyze")
        analyze_main(args)
    elif args.mode == "test":
        logger.info("运行模式: test")
        logger.info("启动测试模式")
        test_main(args)
    else:
        logger.warning("未指定运行模式，使用 --mode 参数指定运行模式")

if __name__ == "__main__":
    main()
