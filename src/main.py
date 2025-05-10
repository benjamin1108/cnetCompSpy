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

def get_config(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Load config from yaml file and merge with command line arguments.
    """
    from src.utils.config_loader import get_config as load_config
    
    # 获取项目根目录路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir) # 项目根目录是 src 的父目录
    
    # 使用通用配置加载器加载配置
    config = load_config(
        base_dir=base_dir,
        config_path=args.config,
        default_config=DEFAULT_CONFIG
    )
    
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
    parser.add_argument("--debug", action="store_true", help="启用调试模式，输出详细的日志信息")
    
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
    config = get_config(args)
    ai_analyzer = AIAnalyzer(config=config)

    specific_file_provided = args.file if args.file else None
    # 默认的 force_analyze_all 取决于 --force 或 --debug，但会被 --file 覆盖
    default_force_analyze_all = args.force

    # 初始化 analysis_params
    analysis_params = {
        "specific_file": specific_file_provided,
        "vendor_to_process": args.vendor if args.vendor else None,
        "limit_per_vendor": args.limit if args.limit > 0 else None,
        "force_analyze_all": default_force_analyze_all 
    }

    # 如果用户明确指定了 --file，则它具有最高优先级
    if specific_file_provided:
        logger.info(f"指定了特定文件 '{specific_file_provided}' 进行分析。将忽略其他筛选条件和由 '--force'/'--debug' 设置的 'force_analyze_all'。")
        analysis_params["specific_file"] = specific_file_provided # 确保它被设置
        analysis_params["force_analyze_all"] = False # 强制禁用 force_analyze_all 以优先处理单文件
        analysis_params["vendor_to_process"] = None
        analysis_params["limit_per_vendor"] = None
    elif default_force_analyze_all: # 如果没有指定 --file，但 --force 或 --debug 为 True
        logger.info(f"'force_analyze_all' 将为 True (因为使用了 --force 或 --debug 参数，且未指定 --file)。将分析所有符合条件的文件。")
        analysis_params["specific_file"] = None # 确保 specific_file 在这种情况下是 None
        # analysis_params["force_analyze_all"] 已经由 default_force_analyze_all 设置为 True
    else:
        # 既没有指定 --file，也没有 --force 或 --debug
        logger.info("将根据元数据和筛选条件（如vendor, limit）分析文件。")
        # analysis_params 中的值已经根据 args 正确设置了

    # 对于非特定文件分析且非强制全部重新分析的情况，记录筛选条件
    if not analysis_params["specific_file"] and not analysis_params["force_analyze_all"]:
        if analysis_params["vendor_to_process"]:
            logger.info(f"筛选厂商进行分析: {analysis_params['vendor_to_process']}")
        if analysis_params["limit_per_vendor"]:
            logger.info(f"每个厂商限制分析文件数: {analysis_params['limit_per_vendor']}")

    success = ai_analyzer.analyze_all(**analysis_params)
    
    return 0 if success else 1

def main() -> int:
    """
    Main entry point.
    
    Returns:
        int: 0表示成功，非0表示失败
    """
    args = parse_arguments()
    config = get_config(args)
    
    # 在执行任何操作前设置日志
    # 如果指定了debug参数，设置日志级别为DEBUG
    debug_mode = args.debug
    if debug_mode:
        logger.info("启用调试模式，将显示详细日志")
    setup_unified_logging(config, log_level_override="DEBUG" if debug_mode else None, debug_mode=debug_mode)

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
