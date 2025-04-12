#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GCP博客页面分析器
此脚本用于下载Google Cloud博客页面并分析其DOM结构
用途：分析GCP博客页面的HTML结构，特别关注动态生成的DOM结构和属性
"""

import os
import sys
import requests
import logging
import yaml
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gcp_blog_analyzer')

class GCPBlogAnalyzer:
    """分析Google Cloud博客页面结构的工具类"""
    
    def __init__(self, config_path=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        })
        
        # 创建保存HTML的目录
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 加载配置文件
        self.config = {}
        if config_path:
            self.load_config(config_path)
        else:
            # 尝试加载默认配置文件
            default_config_paths = [
                os.path.join(os.getcwd(), 'config.yaml'),
                os.path.join(os.getcwd(), 'config.test.yaml')
            ]
            for path in default_config_paths:
                if os.path.exists(path):
                    self.load_config(path)
                    break
    
    def load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
                logger.info(f"成功加载配置文件: {config_path}")
                
                # 从配置文件中获取博客URL
                self.gcp_blog_url = self.config.get('sources', {}).get('gcp', {}).get('blog', {}).get('url')
                if self.gcp_blog_url:
                    logger.info(f"从配置文件中获取到GCP博客URL: {self.gcp_blog_url}")
                else:
                    logger.warning("未在配置文件中找到GCP博客URL，将使用默认URL")
                    self.gcp_blog_url = "https://cloud.google.com/blog/products/networking"
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self.gcp_blog_url = "https://cloud.google.com/blog/products/networking"
    
    def download_page(self, url: str) -> str:
        """
        下载指定URL的页面内容
        
        Args:
            url: 要下载的页面URL
            
        Returns:
            页面HTML内容
        """
        logger.info(f"下载页面: {url}")
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            html = response.text
            
            # 保存HTML文件
            parsed_url = urlparse(url)
            filename = f"{parsed_url.netloc.replace('.', '_')}_{parsed_url.path.strip('/').replace('/', '_')}"
            if not filename:
                filename = "index"
            filepath = os.path.join(self.output_dir, f"{filename}.html")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
                
            logger.info(f"已保存HTML到: {filepath}")
            return html
        except Exception as e:
            logger.error(f"下载页面失败: {e}")
            return ""
    
    def analyze_html_structure(self, html: str, url: str) -> None:
        """
        分析HTML结构并打印出关键信息
        
        Args:
            html: 要分析的HTML内容
            url: 页面URL
        """
        if not html:
            logger.error("没有HTML内容可分析")
            return
        
        soup = BeautifulSoup(html, 'lxml')
        
        # 打印页面标题
        title = soup.find('title')
        if title:
            logger.info(f"页面标题: {title.text.strip()}")
        
        # 分析页面的<head>中的meta标签
        self._analyze_meta_tags(soup)
        
        # 分析主要容器和其类名
        logger.info("分析主要容器结构...")
        self._analyze_main_containers(soup)
        
        # 分析可能的博客文章卡片
        logger.info("分析可能的博客文章卡片...")
        self._analyze_blog_cards(soup)
        
        # 分析页面中的所有链接
        logger.info("分析页面中的链接...")
        self._analyze_links(soup, url)
        
        # 分析页面中的特殊属性和结构
        logger.info("分析页面中的特殊属性和DOM结构...")
        self._analyze_special_attributes(soup)
        
        # 分析页面中的脚本和动态内容
        logger.info("分析页面中的脚本和动态内容...")
        self._analyze_scripts(soup)
    
    def _analyze_meta_tags(self, soup: BeautifulSoup) -> None:
        """分析页面中的meta标签"""
        meta_tags = soup.find_all('meta')
        logger.info(f"页面包含 {len(meta_tags)} 个meta标签")
        
        important_meta_types = ['description', 'keywords', 'author', 'viewport', 'og:title', 'og:description', 'twitter:card']
        
        for meta_type in important_meta_types:
            meta = soup.find('meta', attrs={'name': meta_type}) or soup.find('meta', attrs={'property': meta_type})
            if meta and meta.get('content'):
                logger.info(f"Meta标签 {meta_type}: {meta.get('content')}")
    
    def _analyze_main_containers(self, soup: BeautifulSoup) -> None:
        """分析主要容器元素及其class和data属性"""
        # 查找主要容器元素
        main_elements = [
            ('main', soup.find_all('main')),
            ('article', soup.find_all('article')),
            ('[role="main"]', soup.select('[role="main"]')),
            ('section', soup.find_all('section')),
            ('div级别1', [div for div in soup.find_all('div', recursive=False) if len(div.find_all()) > 5])
        ]
        
        for name, elements in main_elements:
            if elements:
                logger.info(f"找到 {len(elements)} 个 {name} 元素")
                
                for i, elem in enumerate(elements[:2], 1):  # 限制只显示前2个元素，避免输出过多
                    # 分析所有属性
                    attrs = elem.attrs
                    logger.info(f"{name} #{i} 属性:")
                    
                    # 特别关注class和data-*属性
                    for attr_name, attr_value in attrs.items():
                        if attr_name == 'class':
                            logger.info(f"  - classes: {attr_value}")
                        elif attr_name.startswith('data-'):
                            logger.info(f"  - {attr_name}: {attr_value}")
                        elif attr_name in ['id', 'role']:
                            logger.info(f"  - {attr_name}: {attr_value}")
                    
                    # 分析子元素结构
                    direct_children = list(elem.children)
                    direct_children = [c for c in direct_children if c.name is not None]
                    
                    logger.info(f"{name} #{i} 直接子元素: {len(direct_children)} 个")
                    for j, child in enumerate(direct_children[:3], 1):  # 只显示前3个子元素
                        child_classes = child.get('class', []) if hasattr(child, 'get') else []
                        logger.info(f"  - 子元素 #{j} 标签: {child.name}, classes: {child_classes}")
                    
                    if len(direct_children) > 3:
                        logger.info(f"  - ... 还有 {len(direct_children) - 3} 个子元素")
    
    def _analyze_blog_cards(self, soup: BeautifulSoup) -> None:
        """分析可能的博客文章卡片结构"""
        # 寻找可能的文章卡片 - 通过多种策略
        
        # 策略1: 查找带有特定角色的元素
        article_roles = soup.select('[role="article"]')
        if article_roles:
            logger.info(f"找到 {len(article_roles)} 个[role='article']元素")
            self._analyze_card_structure(article_roles, "[role='article']")
        
        # 策略2: 查找<article>标签
        articles = soup.find_all('article')
        if articles:
            logger.info(f"找到 {len(articles)} 个<article>标签")
            self._analyze_card_structure(articles, "<article>")
        
        # 策略3: 查找可能的卡片div - 包含标题和链接的div
        potential_cards = []
        
        # 查找包含h2/h3/h4和链接的div
        for div in soup.find_all('div'):
            heading = div.find(['h2', 'h3', 'h4'])
            link = div.find('a', href=True)
            
            if heading and link:
                potential_cards.append(div)
        
        if potential_cards:
            logger.info(f"找到 {len(potential_cards)} 个可能的文章卡片div")
            self._analyze_card_structure(potential_cards[:5], "可能的卡片div")  # 只分析前5个
    
    def _analyze_card_structure(self, cards, card_type: str) -> None:
        """分析卡片结构并提取信息"""
        for i, card in enumerate(cards[:3], 1):  # 只显示前3个卡片
            logger.info(f"{card_type} #{i} 分析:")
            
            # 分析所有属性
            all_attrs = card.attrs
            important_attrs = ['class', 'id', 'role']
            for attr in important_attrs:
                if attr in all_attrs:
                    logger.info(f"  - {attr}: {all_attrs[attr]}")
            
            # 分析data-*属性
            data_attrs = {k: v for k, v in all_attrs.items() if k.startswith('data-')}
            if data_attrs:
                logger.info(f"  - data属性: {data_attrs}")
            
            # 分析标题
            heading = card.find(['h1', 'h2', 'h3', 'h4'])
            if heading:
                heading_text = heading.get_text(strip=True)
                heading_attrs = heading.attrs
                logger.info(f"  - 标题: {heading_text[:50]}...")
                logger.info(f"  - 标题标签: {heading.name}, 属性: {heading_attrs}")
                
                # 分析标题中的链接
                link_in_heading = heading.find('a', href=True)
                if link_in_heading:
                    logger.info(f"  - 标题中的链接: {link_in_heading['href']}")
                    # 分析链接的属性
                    link_attrs = {k: v for k, v in link_in_heading.attrs.items() if k != 'href'}
                    if link_attrs:
                        logger.info(f"  - 标题链接属性: {link_attrs}")
            
            # 分析卡片中的所有链接
            links = card.find_all('a', href=True)
            if links:
                logger.info(f"  - 包含 {len(links)} 个链接:")
                for j, link in enumerate(links[:3], 1):  # 只显示前3个链接
                    link_text = link.get_text(strip=True) or "[无文本]"
                    logger.info(f"    链接 #{j}: {link_text[:30]}... -> {link['href']}")
                    
                    # 分析链接的aria属性
                    aria_attrs = {k: v for k, v in link.attrs.items() if k.startswith('aria-')}
                    if aria_attrs:
                        logger.info(f"    链接aria属性: {aria_attrs}")
            
            # 分析图片
            images = card.find_all('img')
            if images:
                logger.info(f"  - 包含 {len(images)} 张图片")
                for j, img in enumerate(images[:2], 1):  # 只显示前2张图片
                    img_attrs = img.attrs
                    img_src = img.get('src', '[无源]')
                    img_alt = img.get('alt', '[无alt]')
                    logger.info(f"    图片 #{j}: {img_alt[:30]} -> {img_src[:50]}...")
    
    def _analyze_links(self, soup: BeautifulSoup, base_url: str) -> None:
        """分析页面中的链接，特别是可能的博客文章链接"""
        all_links = soup.find_all('a', href=True)
        logger.info(f"页面共有 {len(all_links)} 个链接")
        
        # 筛选可能的博客文章链接
        blog_indicators = ['/blog/', '/products/', '/topics/', '/posts/', '/article/']
        exclusions = ['/tag/', '/category/', '/author/', '/archive/', '/search/', '/feed/', '/about/', '/contact/']
        
        # 统计不同类型链接的数量
        link_types = {
            "博客文章链接": 0,
            "内部链接": 0,
            "外部链接": 0,
            "锚点链接": 0,
            "JavaScript链接": 0
        }
        
        blog_links = []
        for link in all_links:
            href = link.get('href', '')
            
            # 统计链接类型
            if href.startswith('#'):
                link_types["锚点链接"] += 1
            elif href.startswith('javascript:'):
                link_types["JavaScript链接"] += 1
            elif href.startswith('http') and not href.startswith(base_url):
                link_types["外部链接"] += 1
            else:
                link_types["内部链接"] += 1
            
            # 检查是否为博客文章链接
            is_likely_blog = any(indicator in href.lower() for indicator in blog_indicators)
            is_excluded = any(exclusion in href.lower() for exclusion in exclusions)
            
            if is_likely_blog and not is_excluded:
                blog_links.append(link)
                link_types["博客文章链接"] += 1
        
        # 打印链接类型统计
        logger.info("链接类型统计:")
        for link_type, count in link_types.items():
            logger.info(f"  - {link_type}: {count}个")
        
        if blog_links:
            logger.info(f"找到 {len(blog_links)} 个可能的博客文章链接:")
            for i, link in enumerate(blog_links[:10], 1):  # 只显示前10个
                link_text = link.get_text(strip=True) or "[无文本]"
                logger.info(f"  博客链接 #{i}: {link_text[:50]} -> {link['href']}")
                
                # 分析链接的上下文结构
                parent = link.parent
                if parent:
                    parent_name = parent.name
                    parent_classes = parent.get('class', [])
                    logger.info(f"  - 父元素: {parent_name}, classes: {parent_classes}")
                    
                    # 检查是否位于标题中
                    is_in_heading = parent.name in ['h1', 'h2', 'h3', 'h4'] or parent.find_parent(['h1', 'h2', 'h3', 'h4'])
                    if is_in_heading:
                        logger.info("  - 链接位于标题元素中")
    
    def _analyze_special_attributes(self, soup: BeautifulSoup) -> None:
        """分析页面中的特殊属性和结构"""
        # 分析动态加载的数据属性
        data_elements = soup.select('[data-load], [data-src], [data-url], [data-content], [data-items]')
        if data_elements:
            logger.info(f"找到 {len(data_elements)} 个可能包含动态加载数据的元素")
            for i, elem in enumerate(data_elements[:5], 1):
                logger.info(f"  动态数据元素 #{i}: {elem.name}")
                for attr_name in ['data-load', 'data-src', 'data-url', 'data-content', 'data-items']:
                    if attr_name in elem.attrs:
                        logger.info(f"    {attr_name}: {elem[attr_name]}")
        
        # 分析ARIA属性 - 这些通常用于可访问性和动态内容
        aria_elements = soup.select('[aria-live], [aria-hidden], [aria-expanded], [aria-controls]')
        if aria_elements:
            logger.info(f"找到 {len(aria_elements)} 个带有ARIA属性的元素")
            aria_attrs_count = {}
            for elem in aria_elements:
                for attr in elem.attrs:
                    if attr.startswith('aria-'):
                        aria_attrs_count[attr] = aria_attrs_count.get(attr, 0) + 1
            
            logger.info("  ARIA属性统计:")
            for attr, count in aria_attrs_count.items():
                logger.info(f"    {attr}: {count}个元素")
    
    def _analyze_scripts(self, soup: BeautifulSoup) -> None:
        """分析页面中的脚本和动态内容"""
        scripts = soup.find_all('script')
        logger.info(f"页面包含 {len(scripts)} 个脚本标签")
        
        # 统计内联脚本和外部脚本
        inline_scripts = [s for s in scripts if not s.get('src')]
        external_scripts = [s for s in scripts if s.get('src')]
        
        logger.info(f"  - 内联脚本: {len(inline_scripts)}个")
        logger.info(f"  - 外部脚本: {len(external_scripts)}个")
        
        # 分析外部脚本来源
        script_domains = {}
        for script in external_scripts:
            src = script.get('src', '')
            if src:
                domain = urlparse(src).netloc
                if domain:
                    script_domains[domain] = script_domains.get(domain, 0) + 1
                else:
                    script_domains['[相对路径]'] = script_domains.get('[相对路径]', 0) + 1
        
        if script_domains:
            logger.info("  外部脚本来源:")
            for domain, count in script_domains.items():
                logger.info(f"    {domain}: {count}个")
        
        # 检查可能的JSON数据
        json_data_scripts = []
        for script in inline_scripts:
            script_text = script.string or ""
            if script_text and (script_text.strip().startswith('{') or script_text.strip().startswith('[')):
                json_data_scripts.append(script)
        
        if json_data_scripts:
            logger.info(f"  发现 {len(json_data_scripts)} 个可能包含JSON数据的脚本")
            
            # 尝试解析第一个JSON脚本
            if json_data_scripts:
                script_text = json_data_scripts[0].string or ""
                logger.info(f"  JSON脚本示例 (前200字符): {script_text[:200]}...")

def find_config_file():
    """查找配置文件"""
    # 尝试的路径列表
    paths = [
        os.path.join(os.getcwd(), 'config.yaml'),
        os.path.join(os.getcwd(), 'config.test.yaml'),
        os.path.join(os.path.dirname(os.getcwd()), 'config.yaml'),
        os.path.join(os.path.dirname(os.getcwd()), 'config.test.yaml')
    ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return None

if __name__ == "__main__":
    # 查找配置文件
    config_path = find_config_file()
    if config_path:
        logger.info(f"找到配置文件: {config_path}")
        analyzer = GCPBlogAnalyzer(config_path)
    else:
        logger.warning("未找到配置文件，使用默认设置")
        analyzer = GCPBlogAnalyzer()
    
    # 获取要分析的URL
    blog_url = analyzer.gcp_blog_url or "https://cloud.google.com/blog/products/networking"
    
    logger.info(f"\n\n{'=' * 50}")
    logger.info(f"开始分析页面: {blog_url}")
    logger.info(f"{'=' * 50}\n")
    
    html = analyzer.download_page(blog_url)
    analyzer.analyze_html_structure(html, blog_url)
    
    logger.info(f"\n{'=' * 50}")
    logger.info(f"页面分析完成: {blog_url}")
    logger.info(f"{'=' * 50}\n\n") 