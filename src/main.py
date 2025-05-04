#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import importlib
import json
import logging
import logging.config
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

# 获取logger，但配置将由dictConfig处理
logger = logging.getLogger(__name__)

from src.crawlers.common.crawler_manager import CrawlerManager
from src.ai_analyzer.analyzer import AIAnalyzer

# 配置第三方库的日志级别 - 这部分现在可以移到 config.yaml 的 loggers 部分
# logging.getLogger('urllib3').setLevel(logging.WARNING)
# logging.getLogger('selenium').setLevel(logging.WARNING)
# logging.getLogger('filelock').setLevel(logging.WARNING)

# 默认配置 - logging部分可以移除，因为它将在config.yaml中定义
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
    # 注意：这个 base_dir 计算方式假设 main.py 在 src 目录下
    # 如果 main.py 移动到项目根目录，这个计算需要调整
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir) # 项目根目录是 src 的父目录
    
    # 确定主配置文件路径：优先使用命令行参数，其次是项目根目录下的 config.yaml
    if args.config:
        # 如果命令行指定了路径
        config_path_yaml = args.config
        # 如果是相对路径，则相对于当前工作目录解析
        if not os.path.isabs(config_path_yaml):
            config_path_yaml = os.path.abspath(config_path_yaml)
        print(f"信息: 使用命令行指定的配置文件: {config_path_yaml}") # 在日志系统前打印
    else:
        # 否则使用项目根目录下的 config.yaml
        config_path_yaml = os.path.join(base_dir, 'config.yaml')
        print(f"信息: 未指定配置文件，尝试加载默认路径: {config_path_yaml}") # 在日志系统前打印

    # 加载主配置文件
    if os.path.exists(config_path_yaml):
        config_data = load_yaml_file(config_path_yaml)
        config = merge_configs(config, config_data)
        # 不再在这里记录日志，因为日志系统尚未配置
    else:
        print(f"警告: 配置文件不存在: {config_path_yaml}") # 在日志系统前打印
    
    # 加载敏感配置文件 (路径通常相对于项目根目录)
    secret_config_path = os.path.join(base_dir, 'config.secret.yaml')
    if os.path.exists(secret_config_path):
        secret_config_data = load_yaml_file(secret_config_path)
        config = merge_configs(config, secret_config_data)
        # 不再在这里记录日志
    # else:
        # print(f"警告: 敏感配置文件不存在: {secret_config_path}") # 可选，根据需要取消注释
    
    return config

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="云计算竞争情报爬虫")
    parser.add_argument("--mode", choices=["crawl", "analyze", "test"], help="运行模式: crawl(爬取数据), analyze(分析数据), test(测试模式)")
    parser.add_argument("--vendor", help="爬取指定厂商的数据, 如aws, azure等")
    parser.add_argument("--source", help="爬取指定来源的数据, 如blog, whatsnew等")
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

def setup_unified_logging(config: Dict[str, Any], log_level_override: Optional[str] = None, debug_mode: bool = False):
    """使用字典配置统一设置日志系统"""
    log_config = config.get('logging')
    if not log_config:
        print("警告: 配置文件中未找到 'logging' 配置部分，将使用默认 basicConfig。")
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        return

    try:
        # 确保日志目录存在
        log_filename = log_config.get('handlers', {}).get('file', {}).get('filename')
        if log_filename:
            log_dir = os.path.dirname(log_filename)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
        
        # 处理命令行或debug模式的日志级别覆盖
        if debug_mode:
            # 强制将控制台 handler 级别设为 DEBUG
            if 'console' in log_config.get('handlers', {}):
                log_config['handlers']['console']['level'] = 'DEBUG'
            # 也可以考虑将根 logger 级别也设为 DEBUG，如果需要文件也记录DEBUG
            # if 'root' in log_config:
            #     log_config['root']['level'] = 'DEBUG' 
            print("调试模式启用，控制台日志级别设置为 DEBUG。") # 在日志系统前打印
        elif log_level_override:
             # 覆盖控制台 handler 级别
            if 'console' in log_config.get('handlers', {}):
                 log_config['handlers']['console']['level'] = log_level_override.upper()
             # 也可以选择覆盖根 logger 级别
             # if 'root' in log_config:
             #    log_config['root']['level'] = log_level_override.upper()

        logging.config.dictConfig(log_config)
        logger.info("统一日志系统配置完成。")

    except Exception as e:
        print(f"错误：配置日志系统失败: {e}")
        # 回退到基本配置
        logging.basicConfig(level=logging.INFO)
        logger.error("日志系统配置失败，回退到基本配置。", exc_info=True)

def crawl_main(args: argparse.Namespace) -> int:
    """
    Main function for crawling.
    
    Returns:
        int: 0表示成功，非0表示失败
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
            return 1
        config['sources'] = filtered_sources
        
        # 如果同时指定了来源，进一步过滤配置
        if args.source and args.vendor in config['sources']:
            vendor_sources = config['sources'][args.vendor]
            # 只保留指定来源的配置
            if args.source in vendor_sources:
                config['sources'][args.vendor] = {args.source: vendor_sources[args.source]}
                logger.info(f"仅爬取厂商 {args.vendor} 的 {args.source} 来源")
            else:
                logger.warning(f"未找到厂商 {args.vendor} 的 {args.source} 来源配置，请检查配置文件和来源名称")
                return 1
    # 如果只指定了来源但没有指定厂商，给出警告
    elif args.source:
        logger.warning(f"指定了来源 {args.source} 但未指定厂商，请同时使用 --vendor 参数")
        return 1
    
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
    
    # 检查是否成功获取进程锁
    if not result:
        logger.error("爬虫任务失败，可能是因为无法获取进程锁")
        return 1
    
    # 记录爬取结果
    for vendor_name, vendor_results in result.items():
        for source_type, files in vendor_results.items():
            file_count = len(files)
            logger.info(f"爬取完成: {vendor_name} {source_type}, 共 {file_count} 个文件")
    
    return 0

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

def analyze_main(args: argparse.Namespace) -> int:
    """
    Main function for analyzing.
    
    Returns:
        int: 0表示成功，非0表示失败
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
    success = analyzer.analyze_all()
    
    if not success:
        logger.error("分析任务失败，可能是因为无法获取进程锁")
        return 1
    
    return 0

def main() -> int:
    """
    Main entry point.
    
    Returns:
        int: 0表示成功，非0表示失败
    """
    args = parse_arguments()
    config = get_config(args)
    
    # 在执行任何操作前设置日志
    # 注意：目前 main.py 的参数解析没有 log_level 或 debug，这些是在 web_server/run.py 中的
    # 如果需要 main.py 也支持这些，需要添加到 parse_arguments
    # 这里暂时只使用配置文件中的设置
    setup_unified_logging(config)

    # 如果指定了clean参数，清理数据目录
    if args.clean:
        clean_data_dir(os.path.dirname(os.path.dirname(__file__)), True)
        if not args.mode:
            return 0
    
    # 根据运行模式执行相应操作
    if args.mode == "crawl":
        logger.info("运行模式: crawl")
        return crawl_main(args)
    elif args.mode == "analyze":
        logger.info("运行模式: analyze")
        return analyze_main(args)
    elif args.mode == "test":
        logger.info("运行模式: test")
        logger.info("启动测试模式")
        return test_main(args)
    else:
        logger.warning("未指定运行模式，使用 --mode 参数指定运行模式")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
