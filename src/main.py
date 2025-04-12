#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys
import time
import json
import yaml
from typing import Dict, Any, List
import shutil

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.crawlers.common.crawler_manager import CrawlerManager
from src.ai_analyzer.analyzer import AIAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), "cnetCompSpy.log")),
        logging.StreamHandler()
    ]
)
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

def load_config() -> Dict[str, Any]:
    """加载配置"""
    config = DEFAULT_CONFIG.copy()
    try:
        # 获取项目根目录路径
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
        # 优先尝试加载yaml配置
        config_path_yaml = os.path.join(base_dir, 'config.yaml')
        config_path_json = os.path.join(base_dir, 'config.json')
        
        if os.path.exists(config_path_yaml):
            with open(config_path_yaml, 'r', encoding='utf-8') as f:
                config.update(yaml.safe_load(f))
                logger.info(f"已加载YAML配置: {config_path_yaml}")
        elif os.path.exists(config_path_json):
            with open(config_path_json, 'r', encoding='utf-8') as f:
                config.update(json.load(f))
                logger.info(f"已加载JSON配置: {config_path_json}")
        else:
            logger.info(f"配置文件不存在，使用默认配置")
    except Exception as e:
        logger.warning(f"加载配置文件失败: {e}，使用默认配置")
    
    return config

def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='云计算网络竞品动态分析工具')
    parser.add_argument('--mode', type=str, required=False, choices=['crawl', 'analyze', 'test'],
                       help='运行模式: crawl(爬取数据), analyze(分析数据), test(测试模式)')
    parser.add_argument('--vendor', type=str, help='爬取指定厂商的数据, 如aws, azure等，仅在crawl模式下有效')
    parser.add_argument('--clean', action='store_true', help='清理所有中间文件')
    parser.add_argument('--limit', type=int, default=0, help='爬取的文章数量限制，如设置为5则每个来源只爬取5篇，0表示使用配置文件中的默认值')
    return parser.parse_args()

def ensure_directories():
    """确保必要的目录存在"""
    # 获取项目根目录
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    for dir_name in ['data', 'data/raw', 'data/analysis']:
        dir_path = os.path.join(base_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.info(f"创建目录: {dir_path}")
        
        # 设置目录权限，确保在Windows中可访问
        try:
            os.chmod(dir_path, 0o777)  # 设置所有用户可读写执行
            logger.debug(f"设置目录权限: {dir_path}")
        except Exception as e:
            logger.warning(f"设置目录权限失败: {e}")

def crawl_main(vendor: str = None, article_limit: int = 0):
    """爬取主函数"""
    config = load_config()
    
    # 如果指定了厂商，过滤配置
    if vendor:
        sources = config.get('sources', {})
        if vendor not in sources:
            logger.error(f"指定的厂商 {vendor} 不存在")
            return
        
        # 过滤其他厂商
        filtered_config = config.copy()
        filtered_config['sources'] = {vendor: sources[vendor]}
        config = filtered_config
        logger.info(f"只爬取指定厂商: {vendor}")
    
    # 如果指定了文章数量限制，更新配置
    if article_limit > 0:
        if 'crawler' not in config:
            config['crawler'] = {}
        config['crawler']['article_limit'] = article_limit
        logger.info(f"设置文章数量限制: {article_limit}篇")
    
    crawler = CrawlerManager(config)
    result = crawler.run()
    
    # 记录爬取结果
    for vendor_name, vendor_results in result.items():
        for source_type, files in vendor_results.items():
            file_count = len(files)
            logger.info(f"爬取完成: {vendor_name} {source_type}, 共 {file_count} 个文件")

def clean_data_directories():
    """清理所有数据目录"""
    logger.info("开始清理数据目录...")
    
    # 获取项目根目录
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # 清理raw目录
    raw_dir = os.path.join(base_dir, 'data/raw')
    if os.path.exists(raw_dir):
        for item in os.listdir(raw_dir):
            item_path = os.path.join(raw_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                logger.info(f"删除目录: {item_path}")
            else:
                os.remove(item_path)
                logger.info(f"删除文件: {item_path}")
    
    # 清理analysis目录
    analysis_dir = os.path.join(base_dir, 'data/analysis')
    if os.path.exists(analysis_dir):
        for item in os.listdir(analysis_dir):
            item_path = os.path.join(analysis_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                logger.info(f"删除目录: {item_path}")
            else:
                os.remove(item_path)
                logger.info(f"删除文件: {item_path}")
    
    logger.info("所有数据目录清理完成")

def test_main(vendor: str = None):
    """测试模式：清理数据并依次执行爬虫和分析"""
    logger.info("启动测试模式")
    
    # 清理所有数据
    clean_data_directories()
    
    # 确保目录存在
    ensure_directories()
    
    # 加载配置并设置测试模式
    config = load_config()
    
    # 为所有厂商和来源设置测试模式
    if 'sources' not in config:
        config['sources'] = {}
    
    for vendor_name, vendor_config in config.get('sources', {}).items():
        for source_type, source_config in vendor_config.items():
            config['sources'][vendor_name][source_type]['test_mode'] = True
    
    # 保存临时配置
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_test_path = os.path.join(base_dir, 'config.test.yaml')
    with open(config_test_path, 'w') as f:
        yaml.dump(config, f)
    
    # 执行爬虫 - 使用测试模式，限制为1篇文章
    logger.info("开始执行爬虫 (测试模式)")
    crawl_main(vendor, article_limit=1)
    
    # 执行分析
    logger.info("开始执行分析")
    analyzer = AIAnalyzer(config)
    analyzer.run()
    
    logger.info("测试模式执行完成")

def main():
    """主函数"""
    # 加载配置
    config = load_config()
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 如果指定了清理参数，先清理数据
    if hasattr(args, 'clean') and args.clean:
        clean_data_directories()
        logger.info("清理完成，程序退出")
        return
    
    # 确保必要目录存在
    ensure_directories()
    
    # 根据模式执行相应的任务
    if not hasattr(args, 'mode') or not args.mode:
        logger.error("必须指定运行模式")
        print("必须指定运行模式，使用 --mode 参数指定 crawl, analyze 或 test")
        sys.exit(1)
        
    mode = args.mode.lower()
    logger.info(f"运行模式: {mode}")
    
    if mode == 'crawl':
        crawl_main(args.vendor, args.limit)
    elif mode == 'analyze':
        logger.info("开始AI分析")
        analyzer = AIAnalyzer(config)
        analyzer.run()
    elif mode == 'test':
        test_main(args.vendor)
    else:
        logger.error(f"不支持的模式: {mode}")
        print(f"不支持的模式: {mode}")
        sys.exit(1)

if __name__ == "__main__":
    main() 