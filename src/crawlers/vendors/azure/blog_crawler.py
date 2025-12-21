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
            
            # 先尝试使用requests库获取页面内容(优先使用更稳定的方式)
            html = None
            try:
                logger.debug("使用requests库获取页面内容")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0'
                }
                response = requests.get(self.start_url, headers=headers, timeout=30)
                if response.status_code == 200:
                    html = response.text
                    logger.debug("使用requests库成功获取到页面内容")
                else:
                    logger.error(f"请求返回非成功状态码: {response.status_code}")
            except Exception as e:
                logger.error(f"使用requests库获取页面失败: {e}")
            
            # 只有在requests失败时才尝试使用Playwright
            if not html:
                logger.debug("requests获取失败，尝试使用Playwright")
                html = self._get_with_playwright(self.start_url)
            
            if not html:
                logger.error(f"获取博客列表页失败: {self.start_url}")
                return []
            
            # 解析博客列表，获取文章链接和日期
            article_info = self._parse_article_links(html)
            logger.info(f"解析到 {len(article_info)} 篇文章链接")
            
            # 如果是测试模式或有文章数量限制，截取所需数量的文章链接
            test_mode = self.source_config.get('test_mode', False)
            # 将默认的文章数量限制从50改为20
            article_limit = self.crawler_config.get('article_limit', 20)
            
            if test_mode:
                logger.info("爬取模式：限制爬取1篇文章")
                article_info = article_info[:1]
            elif article_limit > 0:
                logger.info(f"爬取模式：限制爬取{article_limit}篇文章")
                article_info = article_info[:article_limit]
            
            # 检查是否启用了强制模式
            force_mode = self.crawler_config.get('force', False)
            if force_mode:
                logger.info("强制模式已启用，将重新爬取所有文章，忽略本地metadata")
                filtered_article_info = article_info
                logger.info(f"强制模式下爬取所有 {len(filtered_article_info)} 篇文章")
            else:
                # 非强制模式下，过滤已爬取的文章链接，避免不必要的网络请求
                filtered_article_info = []
                already_crawled_count = 0
                
                with BaseCrawler.metadata_lock:  # 使用锁确保线程安全
                    for title, url, list_date in article_info:
                        # 只有当URL在metadata中存在且文件也存在时才跳过
                        if (url in self.metadata and 
                            'filepath' in self.metadata[url] and 
                            os.path.exists(self.metadata[url]['filepath'])):
                            # 文章已爬取过且文件存在，直接添加到结果中
                            already_crawled_count += 1
                            logger.debug(f"跳过已爬取的文章: {title} ({url})")
                            saved_files.append(self.metadata[url]['filepath'])
                        else:
                            # 文章未爬取过或文件不存在，添加到待爬取列表
                            if url in self.metadata:
                                logger.info(f"文章元数据存在但文件缺失，将重新爬取: {title} ({url})")
                            filtered_article_info.append((title, url, list_date))
                
                logger.info(f"过滤后: {len(filtered_article_info)} 篇新文章需要爬取，{already_crawled_count} 篇文章已存在")
            
            # 爬取新文章
            for idx, (title, url, list_date) in enumerate(filtered_article_info, 1):
                logger.info(f"正在爬取第 {idx}/{len(filtered_article_info)} 篇文章: {title}")
                
                try:
                    # 尝试获取文章内容 - 优先使用requests
                    article_html = None
                    try:
                        logger.debug(f"使用requests库获取文章内容: {url}")
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                        response = requests.get(url, headers=headers, timeout=30)
                        if response.status_code == 200:
                            article_html = response.text
                            logger.debug("使用requests库成功获取到文章内容")
                        else:
                            logger.error(f"请求返回非成功状态码: {response.status_code}")
                    except Exception as e:
                        logger.error(f"使用requests库获取文章失败: {e}")
                    
                    # 如果requests失败，才尝试Playwright
                    if not article_html:
                        logger.debug(f"尝试使用Playwright获取文章内容: {url}")
                        article_html = self._get_with_playwright(url)
                    
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
                    if idx < len(filtered_article_info):
                        time.sleep(self.interval)
                    
                except Exception as e:
                    logger.error(f"爬取文章失败: {url} - {e}")
            
            return saved_files
        except Exception as e:
            logger.error(f"爬取Azure博客过程中发生错误: {e}")
            return saved_files
        finally:
            # 关闭WebDriver
            self._close_driver()
    
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
            logger.debug(f"页面标题: {page_title.text.strip()}")
        
        logger.debug("开始解析Azure博客列表页...")
        
        
        # Azure博客搜索结果页面的文章通常在指定的容器内
        try:
            # 扩展结果容器选择器，覆盖更多可能的容器
            results_containers = soup.select('.search-results-content, .results-list, #main-column, main, .grid, .items, .site-main, #content, .content, .container, .row, .col, div[class*="blog"], div[class*="post"], div[class*="article"]')
            logger.debug(f"找到 {len(results_containers)} 个可能的结果容器")
            
            # 如果找到结果容器，从中找到文章卡片
            if results_containers:
                # 尝试所有容器，收集所有可能的文章卡片
                all_article_cards = []
                for container in results_containers:
                    logger.debug(f"检查容器: {container.name}{'#'+container.get('id') if container.get('id') else ''}{'.'+container.get('class')[0] if container.get('class') else ''}")
                    
                    # 扩展Azure卡片选择器，覆盖更多可能性
                    card_selectors = '.search-item, .card, article, .link-card, .document-card, .post-card, .text-card, .result-item, .msx-card, .blog-card, .post, .news-item, .grid-item, .item, div[class*="blog"], div[class*="post"], div[class*="article"], a[href*="/blog/"]'
                    article_cards = container.select(card_selectors)
                    
                    logger.debug(f"在当前容器中找到 {len(article_cards)} 个可能的文章卡片")
                    all_article_cards.extend(article_cards)
                
                logger.debug(f"总共找到 {len(all_article_cards)} 个可能的文章卡片")
                
                if all_article_cards:
                    for idx, card in enumerate(all_article_cards):
                        logger.debug(f"处理卡片 {idx+1}: {card.name}{'#'+card.get('id') if card.get('id') else ''}{'.'+card.get('class')[0] if card.get('class') else ''}")
                        
                        # 扩展标题元素选择器
                        title_selectors = 'h1, h2, h3, h4, .card-title, .title, .post-title, a[role="heading"], .msx-card__title, .headline, .entry-title, .heading, p, span, div'
                        title_elem = None
                        for selector in title_selectors.split(', '):
                            title_elem = card.select_one(selector)
                            if title_elem and title_elem.get_text(strip=True):
                                break
                        
                        # 如果卡片本身是链接，直接使用卡片作为标题元素
                        if not title_elem and card.name == 'a':
                            title_elem = card
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            if len(title) < 5:  # 标题太短则忽略
                                continue
                            logger.info(f"找到标题: {title}")
                            
                            # 查找链接
                            link_elem = None
                            if card.name == 'a':
                                link_elem = card
                            elif title_elem.name == 'a':
                                link_elem = title_elem
                            else:
                                # 在标题或卡片中查找链接，扩展搜索范围
                                link_elem = title_elem.find('a') or card.find('a', href=True) or card.find_parent('a', href=True)
                            
                            if link_elem and link_elem.get('href'):
                                href = link_elem['href']
                                # 构建完整URL
                                url = href if href.startswith('http') else urljoin(self.start_url, href)
                                # 检查是否为可能的博客文章链接
                                if not self._is_likely_blog_post(url):
                                    logger.info(f"链接不符合博客文章模式，忽略: {url}")
                                    continue
                                logger.info(f"找到链接: {url}")
                                
                                # 提取日期 - 查找卡片中的日期信息
                                date = None
                                # 针对Azure博客列表页面中的特定日期格式，扩展选择器
                                meta_items = card.select('.msx-card__meta li, .meta, .date, time, .timestamp, p, span, div[class*="date"], div[class*="time"]')
                                if not meta_items:
                                    # 尝试在卡片附近查找日期元素
                                    meta_items = card.find_all_next(['p', 'span', 'div'], limit=3) + card.find_all_previous(['p', 'span', 'div'], limit=3)
                                
                                for item in meta_items:
                                    date_text = item.get_text(strip=True)
                                    # 尝试匹配多种日期格式
                                    date_patterns = [
                                        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}',
                                        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}',
                                        r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',
                                        r'\d{4}-\d{1,2}-\d{1,2}',
                                        r'\d{1,2}/\d{1,2}/\d{4}'
                                    ]
                                    for pattern in date_patterns:
                                        date_match = re.search(pattern, date_text)
                                        if date_match:
                                            try:
                                                matched_date = date_match.group(0)
                                                # 处理不完整日期（缺少年份）
                                                if re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}$', matched_date):
                                                    current_year = datetime.datetime.now().year
                                                    matched_date = f"{matched_date}, {current_year}"
                                                # 尝试解析日期
                                                for fmt in ['%b %d, %Y', '%d %b %Y', '%Y-%m-%d', '%d/%m/%Y']:
                                                    try:
                                                        parsed_date = datetime.datetime.strptime(matched_date, fmt)
                                                        date = parsed_date.strftime('%Y_%m_%d')
                                                        logger.info(f"从列表页面卡片提取到日期: {date}")
                                                        break
                                                    except ValueError:
                                                        continue
                                                if date:
                                                    break
                                            except (ValueError, TypeError) as e:
                                                logger.debug(f"解析列表页面日期出错: {e}")
                                    if date:
                                        break
                                
                                # 避免重复
                                if url not in [x[1] for x in articles]:
                                    articles.append((title, url, date))
                                    logger.debug(f"添加文章: {title} - {url}")
                        else:
                            logger.debug(f"卡片 {idx+1} 没有找到标题元素")
                else:
                    logger.warning("未找到任何文章卡片")
            
            # 如果没有找到文章卡片，使用通用选择器，扩展搜索范围
            if not articles:
                logger.warning("未找到文章卡片，尝试使用通用选择器")
                
                # 直接查找所有链接
                all_links = soup.find_all('a', href=True)
                logger.info(f"页面上共有 {len(all_links)} 个链接")
                
                # 查找可能的博客文章链接，扩展条件
                blog_links = []
                for link in all_links:
                    href = link.get('href', '')
                    # 构建完整URL
                    url = href if href.startswith('http') else urljoin(self.start_url, href)
                    # 检查是否为可能的博客文章链接
                    if self._is_likely_blog_post(url):
                        blog_links.append(link)
                
                logger.info(f"找到 {len(blog_links)} 个可能的博客文章链接")
                
                for link in blog_links:
                    href = link.get('href', '')
                    # 获取标题
                    title = link.get_text(strip=True)
                    if not title or len(title) < 5:  # 忽略太短的标题
                        # 尝试从链接的属性中获取标题
                        title = link.get('title', '') or link.get('aria-label', '')
                        if not title or len(title) < 5:
                            continue
                    
                    # 构建完整URL
                    url = href if href.startswith('http') else urljoin(self.start_url, href)
                    logger.info(f"找到博客链接: {title} - {url}")
                    
                    # 避免重复
                    if url not in [x[1] for x in articles]:
                        articles.append((title, url, None))
                        logger.debug(f"添加文章: {title} - {url}")
            
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
            import traceback
            logger.error(traceback.format_exc())
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
                
                # 处理srcset属性，优先选择webp格式
                if img.get('srcset'):
                    srcset = img['srcset']
                    # 保存srcset值用于调试
                    logger.debug(f"Found image with srcset: {srcset}")
                    
                    # 尝试从srcset中提取webp格式的URL
                    webp_match = re.search(r'(https?://[^\s]+\.webp)', srcset)
                    if webp_match:
                        webp_url = webp_match.group(1)
                        logger.info(f"选择webp格式图片URL: {webp_url}")
                        img['src'] = webp_url
                        
                    # 删除srcset和sizes属性，以防html2text无法正确处理
                    if img.has_attr('srcset'):
                        del img['srcset']
                    if img.has_attr('sizes'):
                        del img['sizes']
        
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
        
        # 排除明显的非文章页面
        exclude_patterns = [
            r'/tag/', r'/tags/', r'/category/', r'/categories/',
            r'/author/', r'/about/', r'/contact/', r'/feed/',
            r'/archive/', r'/archives/', r'/page/\d+', r'/search/',
            r'/content-type/', r'/blog/$', r'/blog/index', r'/blog/home',
            r'^/en-us/blog/?$',  # 博客首页
            r'^/blog/?$',  # 博客首页
            r'/content-type/[^/]+/?$',  # 内容类型页面，如announcements, thought-leadership, events等
            r'/blog/content-type/[^/]+/?$'  # 带有blog前缀的内容类型页面
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return False
        
        # Azure博客文章URL的常见模式
        blog_patterns = [
            r'/blog/[^/]+/[^/]+',         # 如 /blog/topic/article-name
            r'/blog/[^/]+-\d+/',          # 如 /blog/article-name-123/
            r'/en-us/blog/[^/]+/?$',      # 如 /en-us/blog/article-name/ (Azure博客)
            r'/articles/[^/]+',            # 如 /articles/article-name
            r'/posts/[^/]+',               # 如 /posts/article-name
            r'/\d{4}/\d{2}/[^/]+',         # 如 /2022/01/article-name (日期格式)
            r'/announcements/[^/]+/[^/]+', # 如 /announcements/year/article-name
            r'/updates/[^/]+/[^/]+',       # 如 /updates/year/article-name
            r'/news/[^/]+/[^/]+'           # 如 /news/topic/article-name
        ]
        
        # 检查是否匹配任何博客文章模式
        for pattern in blog_patterns:
            if re.search(pattern, path):
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
        markdown_content = re.sub(r'\.((?:jpg|jpeg|png|gif|webp|svg))\)([^\n])', r'.\1)\n\n\2', markdown_content)
        
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
        保存内容为Markdown文件，调用基类方法
        
        Args:
            url: 文章URL
            title: 文章标题
            content_and_date: 文章内容和发布日期的元组
            
        Returns:
            保存的文件路径
        """
        return super().save_to_markdown(url, title, content_and_date)
    
    def _get_with_playwright(self, url: str) -> Optional[str]:
        """
        使用Playwright获取页面内容
        
        Args:
            url: 目标URL
            
        Returns:
            网页HTML内容或None（如果失败）
        """
        from playwright.sync_api import sync_playwright
        
        for i in range(self.retry):
            try:
                logger.info(f"使用Playwright获取页面: {url}")
                with sync_playwright() as p:
                    browser = p.chromium.launch(
                        headless=True,
                        args=['--no-sandbox', '--disable-dev-shm-usage']
                    )
                    try:
                        page = browser.new_page()
                        page.goto(url, wait_until='domcontentloaded', timeout=30000)
                        
                        # 滚动触发懒加载
                        page.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')
                        page.wait_for_timeout(500)
                        
                        html = page.content()
                        logger.info(f"成功获取页面源码，长度: {len(html)} 字符")
                        return html
                    finally:
                        browser.close()
            except Exception as e:
                logger.warning(f"Playwright获取页面失败 (尝试 {i+1}/{self.retry}): {url} - {e}")
                if i < self.retry - 1:
                    retry_interval = self.interval * (i + 1)
                    logger.info(f"等待 {retry_interval} 秒后重试...")
                    time.sleep(retry_interval)
        
        return None
