#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re
import sys
import time
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
            
            # 解析博客列表，获取文章链接
            article_links = self._parse_article_links(html)
            logger.info(f"解析到 {len(article_links)} 篇文章链接")
            
            # 如果是测试模式或有文章数量限制，截取所需数量的文章链接
            test_mode = self.source_config.get('test_mode', False)
            article_limit = self.crawler_config.get('article_limit', 50)
            
            if test_mode:
                logger.info("爬取模式：限制爬取1篇文章")
                article_links = article_links[:1]
            elif article_limit > 0:
                logger.info(f"爬取模式：限制爬取{article_limit}篇文章")
                article_links = article_links[:article_limit]
            
            # 爬取每篇文章
            for idx, (title, url) in enumerate(article_links, 1):
                logger.info(f"正在爬取第 {idx}/{len(article_links)} 篇文章: {title}")
                
                try:
                    # 获取文章内容
                    article_html = self._get_selenium(url)
                    if not article_html:
                        logger.warning(f"获取文章内容失败: {url}")
                        continue
                    
                    # 解析文章内容
                    article_content = self._parse_article_content(url, article_html)
                    
                    # 规范化文件名（仅用于文件保存，不影响内容处理）
                    # 将原标题传递给save_to_markdown函数，文件名则使用格式化后的标题
                    clean_title = self._format_filename(title)
                    
                    # 保存为Markdown
                    file_path = self.save_to_markdown(url, clean_title, article_content['content'], [])
                    saved_files.append(file_path)
                    logger.info(f"已保存文章: {title} -> {file_path}")
                    
                    # 间隔一段时间再爬取下一篇
                    if idx < len(article_links):
                        time.sleep(self.interval)
                    
                except Exception as e:
                    logger.error(f"爬取文章失败: {url} - {e}")
            
            return saved_files
        except Exception as e:
            logger.error(f"爬取Azure博客过程中发生错误: {e}")
            return saved_files
    
    def _parse_article_links(self, html: str) -> List[Tuple[str, str]]:
        """
        从博客列表页解析文章链接
        
        Args:
            html: 博客列表页HTML
            
        Returns:
            文章链接列表，每项为(标题, URL)元组
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
                article_cards = results_container.select('.search-item, .card, article, .link-card, .document-card, .post-card, .text-card, .result-item')
                
                if article_cards:
                    for card in article_cards:
                        # 查找标题元素
                        title_elem = card.select_one('h2, h3, .card-title, .title, .post-title, a[role="heading"]') or card.select_one('a')
                        
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
                                
                                # 避免重复
                                if url not in [x[1] for x in articles]:
                                    articles.append((title, url))
            
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
                                articles.append((title, url))
            
            logger.info(f"找到 {len(articles)} 篇潜在的博客文章链接")
            
            # 如果没有找到任何文章，并且当前页面可能是博客文章，直接爬取当前页面
            if not articles and self._is_likely_blog_post(self.start_url):
                page_title = soup.find('title')
                title = page_title.text.strip() if page_title else "Azure Blog Post"
                articles.append((title, self.start_url))
                logger.info(f"未找到文章列表，将当前页面作为博客文章处理: {title}")
            
            return articles
        
        except Exception as e:
            logger.error(f"解析文章链接时出错: {e}")
            return []
    
    def _parse_article_content(self, url: str, html: str) -> Dict[str, Any]:
        """
        从文章页面解析文章内容
        
        Args:
            url: 文章URL
            html: 文章页面HTML
            
        Returns:
            包含文章内容的字典
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # 提取文章标题
        title_elem = (
            soup.select_one('h1.title, h1.post-title, h1.article-title, h1.entry-title') or
            soup.select_one('h1') or
            soup.select_one('title')
        )
        title = title_elem.get_text(strip=True) if title_elem else "Untitled Azure Blog Post"
        
        # 提取发布日期
        date = None
        date_elem = (
            soup.select_one('time, .date, .post-date, .published-date, meta[property="article:published_time"]') or
            soup.select_one('.post-meta, .article-meta, .entry-meta')
        )
        
        if date_elem:
            if date_elem.name == 'meta':
                date = date_elem.get('content', '')
            else:
                date = date_elem.get_text(strip=True)
                # 尝试清理日期文本
                date = re.sub(r'(Posted on:|Published:|Date:)', '', date).strip()
        
        # 提取作者
        author = None
        author_elem = (
            soup.select_one('.author, .post-author, .article-author, .byline, [rel="author"]') or
            soup.select_one('meta[name="author"], meta[property="article:author"]')
        )
        
        if author_elem:
            if author_elem.name == 'meta':
                author = author_elem.get('content', '')
            else:
                author = author_elem.get_text(strip=True)
                # 清理作者文本
                author = re.sub(r'(By:|Author:|Posted by:)', '', author).strip()
        
        # 提取文章内容
        content_elem = (
            soup.select_one('article, .post-content, .article-content, .entry-content, .blog-post-content') or
            soup.select_one('main, #main, .main-content, .content')
        )
        
        # 如果没有找到主要内容区，尝试更广泛的选择器
        if not content_elem:
            # 尝试查找body后的主要区域
            body = soup.body
            if body:
                possible_content = body.select('section, div.content, div.post, div.article')
                # 选择最可能包含内容的元素(通常是文本最多的元素)
                if possible_content:
                    content_elem = max(possible_content, key=lambda x: len(x.get_text()))
        
        # 清理内容元素中的不必要元素
        if content_elem:
            # 移除导航、侧边栏、评论等
            for el in content_elem.select('nav, sidebar, .sidebar, #sidebar, footer, .footer, #footer, .comments, #comments, .related-posts, .share-buttons, .social-share, .author-bio, .post-navigation'):
                el.decompose()
            
            # 转换内容为Markdown
            content_html = str(content_elem)
            content_markdown = self.html_converter.handle(content_html)
            
            # 清理Markdown内容
            content_markdown = self._clean_markdown(content_markdown)
        else:
            content_markdown = "无法提取文章内容。"
        
        # 提取标签/分类
        tags = []
        tag_elems = soup.select('.tags a, .categories a, .topics a, .post-tags a, .post-categories a')
        for tag_elem in tag_elems:
            tag = tag_elem.get_text(strip=True)
            if tag and tag not in tags:
                tags.append(tag)
        
        # 构建文章内容
        article_content = {
            "title": title,
            "url": url,
            "date": date,
            "author": author,
            "content": content_markdown,
            "tags": tags
        }
        
        return article_content
    
    def _is_likely_blog_post(self, url: str) -> bool:
        """
        判断URL是否可能是博客文章
        
        Args:
            url: 要判断的URL
            
        Returns:
            True如果URL可能是博客文章，否则False
        """
        # 检查URL是否符合Azure博客文章的模式
        url_lower = url.lower()
        
        # Azure博客文章URL通常包含以下路径之一
        blog_indicators = [
            'azure.microsoft.com/blog/',
            'azure.microsoft.com/en-us/blog/',
            '/articles/',
            '/announcements/',
            '/azure-blog/',
            '/techcommunity/'
        ]
        
        # 排除明显不是文章的URL
        exclusions = [
            '/tag/', 
            '/category/', 
            '/author/', 
            '/archive/', 
            '/search/', 
            '/feed/', 
            '/rss/',
            '/about/',
            '/contact/'
        ]
        
        # 检查URL是否符合条件
        is_likely = any(indicator in url_lower for indicator in blog_indicators)
        is_excluded = any(exclusion in url_lower for exclusion in exclusions)
        
        return is_likely and not is_excluded
    
    def _clean_markdown(self, markdown_content: str) -> str:
        """
        清理Markdown内容
        
        Args:
            markdown_content: 原始Markdown内容
            
        Returns:
            清理后的Markdown内容
        """
        # 移除多余的空行
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        
        # 移除HTML注释
        markdown_content = re.sub(r'<!--.*?-->', '', markdown_content, flags=re.DOTALL)
        
        # 清理超链接中的文本，去掉多余的空格
        markdown_content = re.sub(r'\[([^]]+)\]\s*\(([^)]+)\)', r'[\1](\2)', markdown_content)
        
        # 修正错误的列表格式
        markdown_content = re.sub(r'(?<!\n)\n\* ', '\n\n* ', markdown_content)
        markdown_content = re.sub(r'(?<!\n)\n\d+\. ', '\n\n1. ', markdown_content)
        
        # 修正标题格式，确保#后有空格
        markdown_content = re.sub(r'(#{1,6})([^#\s])', r'\1 \2', markdown_content)
        
        return markdown_content.strip()
    
    def _format_filename(self, title: str) -> str:
        """
        规范化文件名，确保生成干净且有效的文件名
        
        Args:
            title: 原始标题
            
        Returns:
            规范化后的文件名
        """
        # 如果标题为空，返回默认值
        if not title:
            return "azure_blog_post"
            
        # 基本清理，移除非法字符
        filename = self._sanitize_filename(title)
        
        # 替换空格为下划线
        filename = filename.replace(' ', '_')
        
        # 移除多余的下划线
        filename = re.sub(r'_{2,}', '_', filename)
        
        # 移除标点符号
        filename = re.sub(r'[.,;:!?\'"`]+', '', filename)
        
        # 确保文件名不为空
        if not filename or len(filename.strip()) == 0:
            return "azure_blog_post"
            
        # 确保文件名不过长，最多保留80个字符
        if len(filename) > 80:
            filename = filename[:77] + '...'
        
        return filename 