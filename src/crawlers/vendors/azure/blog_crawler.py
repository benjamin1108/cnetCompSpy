#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re
import sys
import time
import hashlib
import datetime
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests
import markdown
import html2text

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

from src.crawlers.common.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)

class AzureBlogCrawler(BaseCrawler):
    """Azure博客爬虫实现"""
    
    def __init__(self, config: Dict[str, Any], vendor: str, source_type: str):
        """初始化Azure博客爬虫"""
        super().__init__(config, vendor, source_type)
        self.source_config = config.get('sources', {}).get(vendor, {}).get(source_type, {})
        self.start_url = self.source_config.get('url')
        
        # 初始化HTML到Markdown转换器
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.ignore_tables = False
        self.html_converter.body_width = 0  # 不限制宽度
        self.html_converter.use_automatic_links = True  # 使用自动链接
        self.html_converter.emphasis_mark = '*'  # 强调使用星号
        self.html_converter.strong_mark = '**'  # 加粗使用双星号
        self.html_converter.wrap_links = False  # 不换行链接
        self.html_converter.pad_tables = True  # 表格填充
    
    def _crawl(self) -> List[str]:
        """
        爬取Azure博客
        
        Returns:
            保存的文件路径列表
        """
        if not self.start_url:
            logger.error("未配置起始URL")
            return []
        
        saved_files = []
        
        try:
            # 获取博客列表页
            logger.info(f"获取Azure博客列表页: {self.start_url}")
            html = self._get_selenium(self.start_url)
            if not html:
                logger.error(f"获取博客列表页失败: {self.start_url}")
                return []
            
            # 解析博客列表，获取文章链接和日期
            article_info = self._parse_article_links(html)
            logger.info(f"解析到 {len(article_info)} 篇文章链接")
            
            # 如果是测试模式或有文章数量限制，截取所需数量的文章链接
            test_mode = self.source_config.get('test_mode', False)
            article_limit = self.crawler_config.get('article_limit', 50)
            
            if test_mode:
                logger.info("爬取模式：限制爬取1篇文章")
                article_info = article_info[:1]
            elif article_limit > 0:
                logger.info(f"爬取模式：限制爬取{article_limit}篇文章")
                article_info = article_info[:article_limit]
            
            # 爬取每篇文章
            for idx, (title, url, list_date) in enumerate(article_info, 1):
                logger.info(f"正在爬取第 {idx}/{len(article_info)} 篇文章: {title}")
                
                try:
                    # 获取文章内容
                    article_html = self._get_selenium(url)
                    if not article_html:
                        logger.warning(f"获取文章内容失败: {url}")
                        continue
                    
                    # 解析文章内容和日期
                    article_content, pub_date = self._parse_article_content(url, article_html, list_date)
                    
                    # 保存为Markdown
                    file_path = self.save_to_markdown(url, title, (article_content, pub_date))
                    saved_files.append(file_path)
                    logger.info(f"已保存文章: {title} -> {file_path}")
                    
                    # 间隔一段时间再爬取下一篇
                    if idx < len(article_info):
                        time.sleep(self.interval)
                    
                except Exception as e:
                    logger.error(f"爬取文章失败: {url} - {e}")
            
            return saved_files
        except Exception as e:
            logger.error(f"爬取Azure博客过程中发生错误: {e}")
            return saved_files
    
    def _parse_article_links(self, html: str) -> List[Tuple[str, str, Optional[str]]]:
        """
        从博客列表页解析文章链接和日期
        
        Args:
            html: 博客列表页HTML
            
        Returns:
            文章信息列表，每项为(标题, URL, 日期)元组，日期可能为None
        """
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # 打印页面的标题，便于调试
        page_title = soup.find('title')
        if page_title:
            logger.info(f"页面标题: {page_title.text.strip()}")
        
        # Azure博客搜索结果页面的文章通常在指定的容器内
        try:
            # Azure搜索结果页面的文章卡片选择器 
            # 首先尝试找到结果区域
            results_containers = soup.select('.search-results-content, .results-list, #main-column, main')
            
            # 如果找到结果容器，从中找到文章卡片
            if results_containers:
                results_container = results_containers[0]
                # Azure通常使用卡片布局显示搜索结果
                article_cards = results_container.select('.search-item, .card, article, .link-card, .document-card, .post-card, .text-card, .result-item, .msx-card')
                
                if article_cards:
                    for card in article_cards:
                        # 查找标题元素
                        title_elem = card.select_one('h2, h3, .card-title, .title, .post-title, a[role="heading"], .msx-card__title') or card.select_one('a')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            
                            # 查找链接
                            link_elem = None
                            if title_elem.name == 'a':
                                link_elem = title_elem
                            else:
                                # 在标题或卡片中查找链接
                                link_elem = title_elem.find('a') or card.find('a', href=True)
                            
                            if link_elem and link_elem.get('href'):
                                href = link_elem['href']
                                # 构建完整URL
                                url = href if href.startswith('http') else urljoin(self.start_url, href)
                                
                                # 提取日期 - 查找卡片中的日期信息
                                date = None
                                # 针对Azure博客列表页面中的特定日期格式
                                meta_items = card.select('.msx-card__meta li')
                                for item in meta_items:
                                    # 尝试匹配日期格式（如 Jan 27, Mar 15 等）
                                    if re.match(r'^\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s*$', item.get_text().strip()):
                                        date_text = item.get_text().strip()
                                        try:
                                            # 添加年份（假设为当前年份）
                                            current_year = datetime.datetime.now().year
                                            full_date_text = f"{date_text}, {current_year}"
                                            # 解析为日期对象
                                            parsed_date = datetime.datetime.strptime(full_date_text, '%b %d, %Y')
                                            date = parsed_date.strftime('%Y_%m_%d')
                                            logger.info(f"从列表页面卡片提取到日期: {date}")
                                            break
                                        except (ValueError, TypeError) as e:
                                            logger.debug(f"解析列表页面日期出错: {e}")
                                
                                # 避免重复
                                if url not in [x[1] for x in articles]:
                                    articles.append((title, url, date))
            
            # 如果没有找到文章卡片，使用通用选择器
            if not articles:
                logger.warning("未找到文章卡片，尝试使用通用选择器")
                
                # 使用更通用的选择器查找可能的文章链接
                content_area = soup.select_one('main, #main, .main-content, .content, article, section') or soup.body
                
                # 查找所有链接
                if content_area:
                    links = content_area.find_all('a', href=True)
                    
                    for link in links:
                        href = link.get('href', '')
                        # Azure博客文章URL通常包含特定路径
                        if (
                            ('azure.microsoft.com' in href and '/blog/' in href) or 
                            ('/articles/' in href) or 
                            ('/posts/' in href) or
                            ('/announcements/' in href)
                        ) and not any(x in href for x in ['category', 'tag', 'archive', 'author', 'search']):
                            # 获取标题
                            title = link.get_text(strip=True)
                            if not title or len(title) < 5:  # 忽略太短的标题
                                continue
                            
                            # 构建完整URL
                            url = href if href.startswith('http') else urljoin(self.start_url, href)
                            
                            # 避免重复
                            if url not in [x[1] for x in articles]:
                                articles.append((title, url, None))
            
            logger.info(f"找到 {len(articles)} 篇潜在的博客文章链接")
            
            # 如果没有找到任何文章，并且当前页面可能是博客文章，直接爬取当前页面
            if not articles and self._is_likely_blog_post(self.start_url):
                page_title = soup.find('title')
                title = page_title.text.strip() if page_title else "Azure Blog Post"
                articles.append((title, self.start_url, None))
                logger.info(f"未找到文章列表，将当前页面作为博客文章处理: {title}")
            
            return articles
        
        except Exception as e:
            logger.error(f"解析文章链接时出错: {e}")
            return []
    
    def _parse_article_content(self, url: str, html: str, list_date: Optional[str]) -> Tuple[str, Optional[str]]:
        """
        从文章页面解析文章内容和发布日期
        
        Args:
            url: 文章URL
            html: 文章页面HTML
            list_date: 从列表页获取的日期（可能为None）
            
        Returns:
            (文章内容, 发布日期)元组，如果找不到日期则使用列表页日期或当前日期
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # 提取发布日期
        pub_date = self._extract_publish_date(soup, list_date, url)
        
        # 找到文章主体
        article_content = self._locate_and_extract_content(soup, url)
        
        return article_content, pub_date
    
    def _extract_publish_date(self, soup: BeautifulSoup, list_date: Optional[str], url: str = None) -> str:
        """
        从文章页面提取发布日期
        
        Args:
            soup: BeautifulSoup对象
            list_date: 从列表页获取的日期（可能为None）
            url: 文章URL（可选）
            
        Returns:
            发布日期字符串 (YYYY_MM_DD格式)
        """
        date_format = "%Y_%m_%d"
        
        # 尝试找到文章页面中的日期元素
        # 特别针对Azure博客的日期提取
        date_selectors = [
            'time', 
            '.date', 
            '.post-date', 
            '.published-date', 
            'meta[property="article:published_time"]',
            '.post-meta', 
            '.article-meta', 
            '.entry-meta'
        ]
        
        for selector in date_selectors:
            date_elements = soup.select(selector)
            if date_elements:
                for date_elem in date_elements:
                    if date_elem.name == 'meta':
                        date_str = date_elem.get('content', '')
                    else:
                        date_str = date_elem.get_text(strip=True)
                    
                    if date_str:
                        try:
                            # 尝试解析日期字符串
                            for date_pattern in [
                                '%Y-%m-%d', '%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y', 
                                '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d'
                            ]:
                                try:
                                    # 如果格式包含时间，只保留日期部分
                                    if 'T' in date_str:
                                        date_str = date_str.split('T')[0]
                                    
                                    parsed_date = datetime.datetime.strptime(date_str, date_pattern)
                                    logger.info(f"从页面提取到日期: {parsed_date.strftime(date_format)}")
                                    return parsed_date.strftime(date_format)
                                except ValueError:
                                    continue
                        except Exception as e:
                            logger.debug(f"解析日期出错: {e}")
        
        # 如果在页面中没有找到日期，尝试使用从列表页获取的日期
        if list_date:
            logger.info(f"使用从列表页获取的日期: {list_date}")
            return list_date
        
        # 如果还是找不到日期，从URL中寻找可能的日期模式
        if url:
            url_date_match = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', url)
            if url_date_match:
                try:
                    year, month, day = url_date_match.groups()
                    parsed_date = datetime.datetime(int(year), int(month), int(day))
                    logger.info(f"从URL提取到日期: {parsed_date.strftime(date_format)}")
                    return parsed_date.strftime(date_format)
                except (ValueError, TypeError) as e:
                    logger.debug(f"从URL提取日期出错: {e}")
        
        # 如果所有方法都失败，使用当前日期
        logger.warning("未找到发布日期，使用当前日期")
        return datetime.datetime.now().strftime(date_format)
        
    def _locate_and_extract_content(self, soup: BeautifulSoup, url: str) -> str:
        """
        定位和提取文章内容
        
        Args:
            soup: BeautifulSoup对象
            url: 文章URL
            
        Returns:
            Markdown格式的文章内容
        """
        # 尝试定位文章主体内容
        content_selectors = [
            'article', 
            '.entry-content', 
            '.post-content', 
            '.article-content', 
            '.main-content',
            '.blog-post',
            '.content-container'
        ]
        
        article_elem = None
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                # 选择最长的元素作为文章主体
                article_elem = max(elements, key=lambda x: len(str(x)))
                break
        
        # 如果没有找到文章主体，使用页面主体
        if not article_elem:
            article_elem = soup.find('main') or soup.find('body')
            
        if not article_elem:
            logger.warning(f"未找到文章主体: {url}")
            return ""
        
        # 清理非内容元素
        for elem in article_elem.select('header, footer, sidebar, .sidebar, nav, .navigation, .ad, .ads, .comments, .social-share'):
            elem.decompose()
        
        # 处理图片 - 使用原始URL
        for img in article_elem.find_all('img'):
            if img.get('src'):
                img['src'] = urljoin(url, img['src'])
        
        # 转换为Markdown
        html = str(article_elem)
        markdown_content = self.html_converter.handle(html)
        
        # 清理和美化Markdown
        markdown_content = self._clean_markdown(markdown_content)
        
        return markdown_content
    
    def _is_likely_blog_post(self, url: str) -> bool:
        """
        判断URL是否可能是博客文章
        
        Args:
            url: 要检查的URL
            
        Returns:
            True如果URL可能是博客文章，否则False
        """
        # 移除协议和域名部分
        parsed = urlparse(url)
        path = parsed.path
        
        # Azure博客文章URL的常见模式
        blog_patterns = [
            r'/blog/[^/]+',         # 如 /blog/article-name
            r'/articles/[^/]+',     # 如 /articles/article-name
            r'/posts/[^/]+',        # 如 /posts/article-name
            r'/\d{4}/\d{2}/[^/]+',  # 如 /2022/01/article-name (日期格式)
            r'/announcements/[^/]+', # 如 /announcements/article-name
        ]
        
        # 检查是否匹配任何博客文章模式
        for pattern in blog_patterns:
            if re.search(pattern, path):
                return True
        
        # 排除常见的非文章页面
        exclude_patterns = [
            r'/tag/', r'/tags/', r'/category/', r'/categories/',
            r'/author/', r'/about/', r'/contact/', r'/feed/',
            r'/archive/', r'/archives/', r'/page/\d+', r'/search/'
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, path):
                return False
                
        # 检查是否在URL路径中包含特定关键词
        blog_keywords = ['post', 'article', 'blog', 'news', 'announcement']
        for keyword in blog_keywords:
            if keyword in path.lower():
                return True
                
        # 默认返回False，宁可错过也不要误报
        return False
    
    def _clean_markdown(self, markdown_content: str) -> str:
        """
        清理和美化Markdown内容
        
        Args:
            markdown_content: 原始Markdown内容
            
        Returns:
            清理后的Markdown内容
        """
        # 去除连续多个空行
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        
        # 美化代码块
        markdown_content = re.sub(r'```([^`]+)```', r'\n\n```\1```\n\n', markdown_content)
        
        # 美化图片格式，确保图片前后有空行
        markdown_content = re.sub(r'([^\n])!\[', r'\1\n\n![', markdown_content)
        markdown_content = re.sub(r'\.(?:jpg|jpeg|png|gif|webp|svg)\)([^\n])', r'.jpg)\n\n\1', markdown_content)
        
        # 修复可能的链接问题
        markdown_content = re.sub(r'\]\(\/(?!http)', r'](https://azure.microsoft.com/', markdown_content)
        
        return markdown_content
    
    def _create_filename(self, url: str, pub_date: str, ext: str) -> str:
        """
        根据发布日期和URL哈希值创建文件名
        
        Args:
            url: 文章URL
            pub_date: 发布日期（YYYY_MM_DD格式）
            ext: 文件扩展名（如.md）
            
        Returns:
            格式为: YYYY_MM_DD_URLHASH.md 的文件名
        """
        # 生成URL的哈希值（取前8位作为短哈希）
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # 组合日期和哈希值
        filename = f"{pub_date}_{url_hash}{ext}"
        
        return filename
    
    def save_to_markdown(self, url: str, title: str, content_and_date: Tuple[str, Optional[str]]) -> str:
        """
        保存内容为Markdown文件
        
        Args:
            url: 文章URL
            title: 文章标题
            content_and_date: 文章内容和发布日期的元组
            
        Returns:
            保存的文件路径
        """
        content, pub_date = content_and_date
        
        if not pub_date:
            # 如果没有提取到日期，使用当前日期
            pub_date = datetime.datetime.now().strftime("%Y_%m_%d")
        
        # 创建用于存储的文件名（使用日期和URL哈希）
        filename = self._create_filename(url, pub_date, ".md")
        filepath = os.path.join(self.output_dir, filename)
        
        # 将日期格式转换为更友好的显示格式（比如 2024-03-02）
        display_date = pub_date.replace('_', '-') if pub_date else "未知"
        
        # 构建Markdown内容（美化格式）
        metadata = [
            f"# {title}",
            "",
            f"**原始链接:** [{url}]({url})",
            "",
            f"**发布时间:** {display_date}",
            "",
            f"**厂商:** {self.vendor.upper()}",
            "",
            f"**类型:** {self.source_type.upper()}",
            "",
            "---",
            "",
        ]
        
        # 组合最终内容
        final_content = "\n".join(metadata) + content
        
        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_content)
            
        return filepath 