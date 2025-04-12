#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import yaml
from bs4 import BeautifulSoup

# 添加项目根目录到路径
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_dir)

from src.crawlers.vendors.gcp.blog_crawler import GcpBlogCrawler

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gcp_blog_crawler_test')

def load_config(config_path):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            logger.info(f"成功加载配置文件: {config_path}")
            return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return None

def find_config_file():
    """查找配置文件"""
    # 尝试的路径列表
    paths = [
        os.path.join(root_dir, 'config.yaml'),
        os.path.join(root_dir, 'config.test.yaml')
    ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return None

def test_parse_article_links(crawler, html_path):
    """测试文章链接解析"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        links = crawler._parse_article_links(html)
        logger.info(f"解析到 {len(links)} 个文章链接")
        
        for i, (title, url) in enumerate(links[:5], 1):  # 仅显示前5个
            logger.info(f"文章 #{i}: {title} -> {url}")
        
        if len(links) > 5:
            logger.info(f"... 还有 {len(links) - 5} 个文章链接")
        
        return links
    except Exception as e:
        logger.error(f"测试文章链接解析失败: {e}")
        return []

def test_parse_article_content(crawler, html_path, url):
    """测试文章内容解析"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        content = crawler._parse_article_content(url, html)
        logger.info(f"解析文章内容:")
        logger.info(f"标题: {content['title']}")
        logger.info(f"日期: {content['date']}")
        logger.info(f"作者: {content['author']}")
        logger.info(f"标签: {content['tags']}")
        
        # 显示内容前200个字符
        content_preview = content['content'][:200] + ('...' if len(content['content']) > 200 else '')
        logger.info(f"内容预览: {content_preview}")
        
        return content
    except Exception as e:
        logger.error(f"测试文章内容解析失败: {e}")
        return None

def main():
    """主测试函数"""
    # 查找配置文件
    config_path = find_config_file()
    if not config_path:
        logger.error("未找到配置文件")
        return
    
    # 加载配置
    config = load_config(config_path)
    if not config:
        return
    
    # 创建爬虫
    crawler = GcpBlogCrawler(config, 'gcp', 'blog')
    
    # 测试目录
    test_dir = os.path.dirname(os.path.abspath(__file__))
    downloads_dir = os.path.join(test_dir, 'downloads')
    
    # 查找下载的HTML文件
    html_files = []
    for filename in os.listdir(downloads_dir):
        if filename.endswith('.html') and 'cloud_google_com' in filename:
            html_files.append(os.path.join(downloads_dir, filename))
    
    if not html_files:
        logger.error("未找到GCP博客HTML文件，请先运行gcp_blog_analyzer.py下载页面")
        return
    
    # 测试博客列表页
    logger.info("\n\n" + "="*50)
    logger.info("测试博客列表页解析")
    logger.info("="*50)
    
    list_page_files = [f for f in html_files if 'products_networking' in f or 'blog_products' in f]
    if list_page_files:
        list_page = list_page_files[0]
        logger.info(f"使用博客列表页: {list_page}")
        links = test_parse_article_links(crawler, list_page)
    else:
        logger.warning("未找到博客列表页文件，跳过测试")
    
    # 测试博客详情页
    logger.info("\n\n" + "="*50)
    logger.info("测试博客详情页解析")
    logger.info("="*50)
    
    detail_page_files = [f for f in html_files if not (f in list_page_files)]
    if detail_page_files:
        detail_page = detail_page_files[0]
        logger.info(f"使用博客详情页: {detail_page}")
        test_parse_article_content(crawler, detail_page, "https://cloud.google.com/blog/test-article")
    else:
        # 如果没有单独的详情页，使用列表页测试
        if list_page_files:
            logger.info("未找到博客详情页文件，使用列表页测试内容解析")
            if links:
                url = links[0][1]  # 使用第一个链接的URL
                test_parse_article_content(crawler, list_page, url)
        else:
            logger.warning("未找到任何HTML文件，无法测试内容解析")

if __name__ == "__main__":
    main() 