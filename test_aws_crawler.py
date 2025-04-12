#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import yaml

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.crawlers.vendors.aws.blog_crawler import AwsBlogCrawler

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path='config.yaml'):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        sys.exit(1)

def ensure_directories():
    """确保必要的目录存在"""
    dirs = [
        'data/raw/aws/blog',
        'data/processed/aws/blog',
        'data/analysis/aws/blog'
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        logger.debug(f"确保目录存在: {d}")

def main():
    """测试AWS博客爬虫的主函数"""
    # 确保目录存在
    ensure_directories()
    
    # 加载配置
    config = load_config()
    
    # 创建爬虫实例并运行
    logger.info("开始测试AWS博客爬虫...")
    
    # 修改配置以确保URL正确
    if 'sources' not in config:
        config['sources'] = {}
    if 'aws' not in config['sources']:
        config['sources']['aws'] = {}
    if 'blog' not in config['sources']['aws']:
        config['sources']['aws']['blog'] = {}
    
    # 确保设置了正确的博客URL
    config['sources']['aws']['blog']['url'] = 'https://aws.amazon.com/blogs/'
    # 设置测试模式
    config['sources']['aws']['blog']['test_mode'] = True
    
    # 如果没有爬虫配置，添加一个基本配置
    if 'crawler' not in config:
        config['crawler'] = {
            'article_limit': 1,  # 测试时只爬取一篇文章
            'selenium': {
                'wait_time': 10,
                'headless': True
            }
        }
    
    # 创建爬虫实例
    crawler = AwsBlogCrawler(config, 'aws', 'blog')
    
    # 运行爬虫
    saved_files = crawler.run()
    
    # 输出结果
    logger.info(f"爬虫测试完成，共保存了 {len(saved_files)} 个文件:")
    for file in saved_files:
        logger.info(f" - {file}")

if __name__ == "__main__":
    main() 