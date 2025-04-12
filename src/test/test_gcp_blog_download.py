#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GCP博客下载和测试脚本
此脚本用于从config.yaml中配置的URL下载GCP博客页面并进行测试
"""

import os
import sys
import logging
import yaml
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 添加项目根目录到路径
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_dir)

from src.crawlers.vendors.gcp.blog_crawler import GcpBlogCrawler

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gcp_blog_download')

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

def setup_selenium():
    """设置Selenium webdriver"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"设置Selenium失败: {e}")
        return None

def download_page(url, output_dir, driver=None):
    """下载页面内容"""
    logger.info(f"开始下载页面: {url}")
    
    if driver:
        try:
            driver.get(url)
            # 等待页面加载完成
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            # 等待JavaScript渲染完成
            time.sleep(5)
            html = driver.page_source
            
            # 保存HTML到文件
            save_html(url, html, output_dir)
            return html
        except Exception as e:
            logger.error(f"使用Selenium下载页面失败: {e}")
            return None
    else:
        try:
            # 使用requests作为备用方法
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            html = response.text
            
            # 保存HTML到文件
            save_html(url, html, output_dir)
            return html
        except Exception as e:
            logger.error(f"使用requests下载页面失败: {e}")
            return None

def save_html(url, html, output_dir):
    """保存HTML到文件"""
    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        filename = f"{parsed_url.netloc.replace('.', '_')}_{parsed_url.path.strip('/').replace('/', '_')}.html"
        if not filename or filename == ".html":
            filename = "index.html"
        
        # 保存文件
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"已保存HTML到: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"保存HTML失败: {e}")
        return None

def download_article_page(url, output_dir, driver=None):
    """下载文章页面"""
    logger.info(f"下载文章页面: {url}")
    return download_page(url, output_dir, driver)

def test_crawler_with_downloaded_pages(crawler, html_dir):
    """使用下载的页面测试爬虫"""
    # 查找下载的HTML文件
    html_files = []
    for filename in os.listdir(html_dir):
        if filename.endswith('.html') and 'cloud_google_com' in filename:
            html_files.append(os.path.join(html_dir, filename))
    
    if not html_files:
        logger.error("未找到GCP博客HTML文件")
        return
    
    # 测试博客列表页解析
    list_page_files = [f for f in html_files if 'products_networking' in f or 'blog_products' in f]
    
    if list_page_files:
        list_page = list_page_files[0]
        logger.info(f"\n\n{'='*50}")
        logger.info(f"测试博客列表页解析: {list_page}")
        logger.info(f"{'='*50}")
        
        with open(list_page, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # 解析文章链接
        links = crawler._parse_article_links(html)
        logger.info(f"解析到 {len(links)} 篇文章链接")
        
        for i, (title, url) in enumerate(links[:5], 1):
            logger.info(f"文章 #{i}: {title[:50]}... -> {url}")
        
        if len(links) > 5:
            logger.info(f"... 还有 {len(links) - 5} 篇文章链接")
        
        # 如果有文章链接，测试第一篇文章内容解析
        if links:
            first_article = links[0]
            article_title, article_url = first_article
            
            # 查找是否有对应的文章HTML文件
            article_html_files = [f for f in html_files if article_url.split('/')[-1] in f]
            
            if article_html_files:
                # 使用已下载的文章HTML
                article_html_file = article_html_files[0]
                logger.info(f"\n\n{'='*50}")
                logger.info(f"测试文章内容解析: {article_title}")
                logger.info(f"使用文件: {article_html_file}")
                logger.info(f"{'='*50}")
                
                with open(article_html_file, 'r', encoding='utf-8') as f:
                    article_html = f.read()
                
                content = crawler._parse_article_content(article_url, article_html)
                logger.info(f"解析文章内容结果:")
                logger.info(f"标题: {content['title']}")
                logger.info(f"日期: {content['date']}")
                logger.info(f"作者: {content['author']}")
                logger.info(f"标签: {content['tags']}")
                
                # 显示内容前300个字符
                content_preview = content['content'][:300] + ('...' if len(content['content']) > 300 else '')
                logger.info(f"内容预览:\n{content_preview}")
            else:
                logger.warning(f"未找到文章HTML文件: {article_title}, 使用列表页HTML测试内容解析")
                
                # 使用列表页HTML文件测试
                content = crawler._parse_article_content(article_url, html)
                logger.info(f"解析文章内容结果:")
                logger.info(f"标题: {content['title']}")
                logger.info(f"日期: {content['date']}")
                logger.info(f"作者: {content['author']}")
                logger.info(f"标签: {content['tags']}")
                
                # 显示内容前300个字符
                content_preview = content['content'][:300] + ('...' if len(content['content']) > 300 else '')
                logger.info(f"内容预览:\n{content_preview}")
    else:
        logger.warning("未找到博客列表页文件")

def main():
    """主函数"""
    # 查找配置文件
    config_path = find_config_file()
    if not config_path:
        logger.error("未找到配置文件")
        return
    
    # 加载配置
    config = load_config(config_path)
    if not config:
        return
    
    # 获取GCP博客URL
    gcp_blog_url = config.get('sources', {}).get('gcp', {}).get('blog', {}).get('url')
    if not gcp_blog_url:
        logger.error("未找到GCP博客URL配置")
        return
    
    logger.info(f"从配置文件中获取GCP博客URL: {gcp_blog_url}")
    
    # 设置输出目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
    os.makedirs(output_dir, exist_ok=True)
    
    # 设置Selenium
    driver = setup_selenium()
    if not driver:
        logger.warning("Selenium设置失败，将使用requests下载")
    
    try:
        # 下载列表页
        logger.info(f"\n\n{'='*50}")
        logger.info(f"下载博客列表页: {gcp_blog_url}")
        logger.info(f"{'='*50}")
        list_page_html = download_page(gcp_blog_url, output_dir, driver)
        
        if not list_page_html:
            logger.error("下载博客列表页失败")
            if driver:
                driver.quit()
            return
        
        # 解析列表页，获取文章链接
        soup = BeautifulSoup(list_page_html, 'lxml')
        crawler = GcpBlogCrawler(config, 'gcp', 'blog')
        links = crawler._find_blog_article_links(soup)
        
        article_links = []
        for link in links:
            href = link.get('href', '')
            if not href or not crawler._is_likely_blog_post(href):
                continue
            
            # 确保是完整URL
            url = crawler._normalize_url(href)
            title = crawler._extract_title_for_link(link)
            
            if title and url and url not in [x[1] for x in article_links]:
                article_links.append((title, url))
        
        logger.info(f"从列表页解析到 {len(article_links)} 篇文章链接")
        
        # 下载前3篇文章
        article_limit = min(3, len(article_links))
        for i in range(article_limit):
            title, url = article_links[i]
            logger.info(f"\n\n{'='*50}")
            logger.info(f"下载文章 {i+1}/{article_limit}: {title}")
            logger.info(f"URL: {url}")
            logger.info(f"{'='*50}")
            
            download_article_page(url, output_dir, driver)
            time.sleep(3)  # 间隔时间
        
        # 测试爬虫
        logger.info(f"\n\n{'='*50}")
        logger.info(f"使用下载的页面测试爬虫")
        logger.info(f"{'='*50}")
        test_crawler_with_downloaded_pages(crawler, output_dir)
    
    finally:
        # 关闭Selenium
        if driver:
            driver.quit()
            logger.info("已关闭Selenium")

if __name__ == "__main__":
    main() 