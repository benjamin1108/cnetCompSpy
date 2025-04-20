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
from lxml import etree

from bs4 import BeautifulSoup
import requests
import markdown
import html2text

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

from src.crawlers.common.base_crawler import BaseCrawler, metadata_lock

logger = logging.getLogger(__name__)

class GcpBlogCrawler(BaseCrawler):
    """GCP博客爬虫实现"""
    
    def __init__(self, config: Dict[str, Any], vendor: str, source_type: str):
        """初始化GCP博客爬虫"""
        super().__init__(config, vendor, source_type)
        self.source_config = config.get('sources', {}).get(vendor, {}).get(source_type, {})
        self.start_url = self.source_config.get('url')
    
    def _crawl(self) -> List[str]:
        """
        爬取GCP博客
        
        Returns:
            保存的文件路径列表
        """
        if not self.start_url:
            logger.error("未配置起始URL")
            return []
        
        saved_files = []
        
        try:
            # 获取博客列表页
            logger.info(f"获取GCP博客列表页: {self.start_url}")
            
            # 先尝试使用requests库获取页面内容(优先使用更稳定的方式)
            html = None
            try:
                logger.info("使用requests库获取页面内容")
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
                    logger.info("使用requests库成功获取到页面内容")
                else:
                    logger.error(f"请求返回非成功状态码: {response.status_code}")
            except Exception as e:
                logger.error(f"使用requests库获取页面失败: {e}")
            
            # 只有在requests失败时才尝试使用Selenium
            if not html:
                logger.info("requests获取失败，尝试使用Selenium")
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
            
            # 修改：先过滤已爬取的文章链接，避免不必要的网络请求
            filtered_article_links = []
            already_crawled_count = 0
            
            with metadata_lock:  # 使用锁确保线程安全
                for title, url in article_links:
                    # 只有当URL在metadata中存在且文件也存在时才跳过
                    if (url in self.metadata and 
                        'filepath' in self.metadata[url] and 
                        os.path.exists(self.metadata[url]['filepath'])):
                        # 文章已爬取过且文件存在，直接添加到结果中
                        already_crawled_count += 1
                        logger.info(f"跳过已爬取的文章: {title} ({url})")
                        saved_files.append(self.metadata[url]['filepath'])
                    else:
                        # 文章未爬取过或文件不存在，添加到待爬取列表
                        if url in self.metadata:
                            logger.info(f"文章元数据存在但文件缺失，将重新爬取: {title} ({url})")
                        filtered_article_links.append((title, url))
            
            logger.info(f"过滤后: {len(filtered_article_links)} 篇新文章需要爬取，{already_crawled_count} 篇文章已存在")
            
            # 爬取每篇新文章
            for idx, (title, url) in enumerate(filtered_article_links, 1):
                logger.info(f"正在爬取第 {idx}/{len(filtered_article_links)} 篇文章: {title}")
                
                try:
                    # 尝试获取文章内容 - 优先使用requests
                    article_html = None
                    try:
                        logger.info(f"使用requests库获取文章内容: {url}")
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                        response = requests.get(url, headers=headers, timeout=30)
                        if response.status_code == 200:
                            article_html = response.text
                            logger.info("使用requests库成功获取到文章内容")
                        else:
                            logger.error(f"请求返回非成功状态码: {response.status_code}")
                    except Exception as e:
                        logger.error(f"使用requests库获取文章失败: {e}")
                    
                    # 如果requests失败，才尝试Selenium
                    if not article_html:
                        logger.info(f"尝试使用Selenium获取文章内容: {url}")
                        article_html = self._get_selenium(url)
                    
                    if not article_html:
                        logger.warning(f"获取文章内容失败: {url}")
                        continue
                    
                    # 解析文章内容和日期
                    content, pub_date = self._parse_article_content(url, article_html)
                    
                    # 保存为Markdown
                    file_path = self.save_to_markdown(url, title, (content, pub_date))
                    saved_files.append(file_path)
                    logger.info(f"已保存文章: {title} -> {file_path}")
                    
                    # 间隔一段时间再爬取下一篇
                    if idx < len(filtered_article_links):
                        time.sleep(self.interval)
                    
                except Exception as e:
                    logger.error(f"爬取文章失败: {url} - {e}")
            
            return saved_files
        except Exception as e:
            logger.error(f"爬取GCP博客过程中发生错误: {e}")
            return saved_files
        finally:
            # 关闭WebDriver
            self._close_driver()
    
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
        
        try:
            # 检查是否在博客页面上
            # 如果在博客详情页，直接将当前页面作为文章
            if self._is_blog_detail_page(soup):
                title = self._extract_page_title(soup)
                articles.append((title, self.start_url))
                logger.info(f"检测到博客详情页：{title}")
                return articles
            
            # 查找所有可能包含博客文章链接的元素
            blog_links = self._find_blog_article_links(soup)
            
            # 提取有效的文章链接
            seen_urls = set()  # 用于去重
            for link in blog_links:
                href = link.get('href', '')
                if not href or not self._is_likely_blog_post(href):
                    continue
                
                # 确保是完整URL
                url = self._normalize_url(href)
                
                # 跳过已处理的URL
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                
                # 提取标题
                title = self._extract_title_for_link(link)
                if title and url:
                    articles.append((title, url))
            
            logger.info(f"从页面解析到 {len(articles)} 篇文章链接")
            
            # 增加额外的日志记录，帮助理解爬取的内容
            if articles:
                logger.info("前10篇文章链接:")
                for i, (title, url) in enumerate(articles[:10], 1):
                    logger.info(f"{i}. {title} - {url}")
            
            # 如果没有找到任何文章链接，检查当前页面是否就是一篇博客文章
            if not articles and self._is_likely_blog_post(self.start_url):
                logger.info("当前页面可能是单篇博客文章，直接处理")
                title = self._extract_page_title(soup)
                articles.append((title, self.start_url))
            
            # 后处理：只过滤类别页面，不做内容相关性筛选
            filtered_articles = []
            for title, url in articles:
                # 对每个链接再次确认是否是具体文章而非类别页面
                if not self._is_likely_blog_post(url):
                    logger.info(f"过滤掉可能的类别页面: {title} - {url}")
                    continue
                
                filtered_articles.append((title, url))
            
            return filtered_articles
        except Exception as e:
            logger.error(f"解析文章链接时出错: {e}")
            return []
    
    def _is_blog_detail_page(self, soup: BeautifulSoup) -> bool:
        """
        判断当前页面是否是博客详情页
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            是否是博客详情页
        """
        # 特征1: 博客详情页通常有article标签
        if soup.find('article'):
            return True
        
        # 特征2: 博客详情页通常有时间元素
        if soup.find('time') or soup.select('[role="time"]'):
            return True
        
        # 特征3: 博客详情页通常有作者信息
        if soup.select('[rel="author"]'):
            return True
        
        # 特征4: 博客详情页通常会有特定的meta标签
        if soup.find('meta', attrs={'property': 'article:published_time'}):
            return True
        
        # 特征5: URL特征
        url = self.start_url.lower()
        if '/blog/' in url and any(segment for segment in url.split('/') if len(segment) > 20):
            # 博客详情页URL通常包含长标识符
            return True
        
        return False
    
    def _extract_page_title(self, soup: BeautifulSoup) -> str:
        """提取页面标题
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            页面标题
        """
        # 尝试从h1标题提取
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # 否则从title标签提取
        title = soup.find('title')
        if title:
            title_text = title.get_text(strip=True)
            # 移除网站名称（如果存在）
            return re.sub(r'\s*\|\s*Google Cloud.*$', '', title_text)
        
        return "Google Cloud Blog Post"
    
    def _find_blog_article_links(self, soup: BeautifulSoup) -> List[Any]:
        """
        查找所有可能的博客文章链接
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            链接元素列表
        """
        blog_links = []
        
        # 基于测试脚本发现的最佳选择器
        # 选择器 'a[href*="/blog/"][href*="networking"]' 可以精确匹配网络相关的文章链接
        primary_selectors = [
            'a[href*="/blog/"][href*="networking"]',               # 网络博客文章链接
            'a[href*="/blog/topics/telecommunications/"]',          # 电信博客文章链接
        ]

        # 使用精确的选择器查找链接
        for selector in primary_selectors:
            logger.info(f"使用选择器 '{selector}' 查找文章链接")
            links = soup.select(selector)
            if links:
                logger.info(f"选择器 '{selector}' 找到 {len(links)} 个链接元素")
                blog_links.extend(links)
        
        # 如果使用主要选择器没有找到链接，尝试备用策略
        if not blog_links:
            logger.warning("主要选择器未找到链接，尝试备用选择器")
            
            # 确保 /products/networking/ 路径下的所有链接都会被包含
            backup_selectors = [
                'a[href*="/blog/products/networking/"]'  # 指向网络产品博客的链接
            ]
            
            for selector in backup_selectors:
                logger.info(f"使用备用选择器 '{selector}' 查找文章链接")
                links = soup.select(selector)
                if links:
                    logger.info(f"备用选择器 '{selector}' 找到 {len(links)} 个链接元素")
                    blog_links.extend(links)
                    
        # 最后一次尝试：如果仍然没有找到链接，使用带有分钟阅读时间的链接，这些通常是文章
        if not blog_links:
            logger.warning("尝试查找带有阅读时间的链接")
            read_time_patterns = [
                re.compile(r'\d+-minute read', re.IGNORECASE),
                re.compile(r'\d+ min read', re.IGNORECASE)
            ]
            
            for pattern in read_time_patterns:
                # 查找所有包含阅读时间的文本节点
                for element in soup.find_all(text=pattern):
                    # 寻找这个文本节点的父链接
                    parent_link = element.find_parent('a')
                    if parent_link and 'href' in parent_link.attrs:
                        href = parent_link.get('href', '')
                        if href and '/blog/' in href:
                            blog_links.append(parent_link)
            
            if blog_links:
                logger.info(f"根据阅读时间找到 {len(blog_links)} 个链接元素")
        
        # 去重
        unique_links = []
        seen_hrefs = set()
        for link in blog_links:
            href = link.get('href', '')
            if href and href not in seen_hrefs:
                seen_hrefs.add(href)
                unique_links.append(link)
        
        logger.info(f"去重后共找到 {len(unique_links)} 个链接元素")
        return unique_links
    
    def _normalize_url(self, href: str) -> str:
        """
        将相对URL转换为绝对URL
        
        Args:
            href: 原始URL
            
        Returns:
            标准化后的URL
        """
        # 如果已经是完整URL，直接返回
        if href.startswith('http'):
            return href
        
        # 如果是相对于根目录的URL
        if href.startswith('/'):
            base_url = "{0.scheme}://{0.netloc}".format(urlparse(self.start_url))
            return base_url + href
        
        # 如果是相对于当前目录的URL
        return urljoin(self.start_url, href)
    
    def _extract_title_for_link(self, link) -> str:
        """
        为链接提取合适的标题
        
        Args:
            link: 链接元素
            
        Returns:
            标题文本
        """
        # 1. 首先尝试获取链接的aria-label属性，这通常包含更完整的描述
        aria_label = link.get('aria-label')
        if aria_label and len(aria_label) > 5:
            return self._clean_title(aria_label)
        
        # 2. 尝试获取链接的文本内容
        link_text = link.get_text(strip=True)
        if link_text and len(link_text) > 5:
            return self._clean_title(link_text)
        
        # 3. 查找链接周围的内容
        # 检查父元素是否为标题
        parent = link.parent
        if parent and parent.name in ['h1', 'h2', 'h3', 'h4']:
            return self._clean_title(parent.get_text(strip=True))
        
        # 4. 查找最近的标题元素
        ancestor = link.find_parent(['div', 'section', 'article'])
        if ancestor:
            heading = ancestor.find(['h1', 'h2', 'h3', 'h4'])
            if heading:
                return self._clean_title(heading.get_text(strip=True))
        
        # 5. 从URL中提取标题（最后的选择）
        href = link.get('href', '')
        if href:
            # 尝试从URL路径的最后部分提取标题
            path = urlparse(href).path
            last_segment = path.rstrip('/').split('/')[-1]
            if last_segment:
                # 将连字符和下划线替换为空格，并转换为标题格式
                title_from_url = last_segment.replace('-', ' ').replace('_', ' ').title()
                if len(title_from_url) > 3:  # 确保标题不太短
                    return self._clean_title(title_from_url)
        
        # 默认标题
        return "Google Cloud Blog Article"
    
    def _clean_title(self, title: str) -> str:
        """
        清理标题文本，移除分类前缀和阅读时间后缀
        
        Args:
            title: 原始标题文本
            
        Returns:
            清理后的标题
        """
        # 移除分类前缀，如"Telecommunications"、"Networking"等
        categories = [
            "Telecommunications", 
            "Networking", 
            "Security", 
            "AI & Machine Learning",
            "Cloud", 
            "Big Data"
        ]
        
        # 尝试移除分类前缀
        for category in categories:
            if title.startswith(category):
                title = title[len(category):].strip()
        
        # 移除"By Author • X-minute read"格式的后缀
        author_pattern = r'\s*By\s+[\w\s\.]+\s*[•·]\s*\d+-minute read.*$'
        title = re.sub(author_pattern, '', title, flags=re.IGNORECASE)
        
        # 移除"X-minute read"格式的后缀
        read_time_pattern = r'\s*[•·]\s*\d+-minute read.*$'
        title = re.sub(read_time_pattern, '', title, flags=re.IGNORECASE)
        
        # 移除"• X min read"格式的后缀
        min_read_pattern = r'\s*[•·]\s*\d+\s*min read.*$'
        title = re.sub(min_read_pattern, '', title, flags=re.IGNORECASE)
        
        # 返回清理后的标题
        return title.strip()
    
    def _parse_article_content(self, url: str, html: str) -> Tuple[str, Optional[str]]:
        """
        从文章页面解析文章内容和发布日期
        
        Args:
            url: 文章URL
            html: 文章页面HTML
            
        Returns:
            (文章内容, 发布日期) 元组
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # 提取发布日期
        pub_date = self._extract_article_date_enhanced(soup, html, url)
        
        # 提取文章内容
        article_content = self._extract_article_content(soup)
        
        return article_content, pub_date
    
    def _extract_article_date_enhanced(self, soup: BeautifulSoup, html: str, url: str = None) -> str:
        """
        增强版的文章日期提取，使用多种方式尝试获取日期
        
        Args:
            soup: BeautifulSoup对象
            html: 原始HTML
            url: 文章URL（可选）
            
        Returns:
            日期字符串（YYYY_MM_DD格式）
        """
        date_format = "%Y_%m_%d"
        
        # 1. 使用特定的xpath路径提取日期
        try:
            html_tree = etree.HTML(html)
            if html_tree is not None:
                # 根据提供的xpath定位日期元素
                date_elements = html_tree.xpath('/html/body/c-wiz/div/div/article/section[1]/div/div[3]')
                if date_elements:
                    date_text = date_elements[0].text_content().strip()
                    logger.info(f"通过XPath找到日期文本: {date_text}")
                    
                    # 尝试解析这个日期文本
                    # 常见的GCP日期格式如：May 16, 2023 或 Sep 28, 2022
                    date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})', date_text)
                    if date_match:
                        month, day, year = date_match.groups()
                        month_dict = {
                            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                        }
                        month_num = month_dict.get(month)
                        if month_num:
                            try:
                                parsed_date = datetime.datetime(int(year), month_num, int(day))
                                logger.info(f"成功解析XPath日期: {parsed_date.strftime(date_format)}")
                                return parsed_date.strftime(date_format)
                            except ValueError as e:
                                logger.warning(f"解析XPath日期出错: {e}")
        except Exception as e:
            logger.warning(f"使用XPath提取日期时出错: {e}")
        
        # 2. 使用标准方法提取日期
        standard_date = self._extract_article_date(soup)
        if standard_date:
            try:
                # 尝试解析标准日期
                for date_pattern in [
                    '%Y-%m-%d', '%Y/%m/%d', '%B %d, %Y', '%b %d, %Y',
                    '%d %B %Y', '%d %b %Y', '%m/%d/%Y', '%d/%m/%Y'
                ]:
                    try:
                        # 处理可能包含时间的日期
                        date_part = standard_date.split('T')[0] if 'T' in standard_date else standard_date
                        parsed_date = datetime.datetime.strptime(date_part, date_pattern)
                        logger.info(f"通过标准方法解析日期: {parsed_date.strftime(date_format)}")
                        return parsed_date.strftime(date_format)
                    except ValueError:
                        continue
            except Exception as e:
                logger.debug(f"解析标准日期出错: {e}")
        
        # 3. 从URL中尝试提取日期
        if url:
            url_date_match = re.search(r'/(\d{4})/(\d{1,2})/', url)
            if url_date_match:
                try:
                    year, month = url_date_match.groups()
                    # 如果URL中只有年月，日设为1
                    parsed_date = datetime.datetime(int(year), int(month), 1)
                    logger.info(f"从URL中提取到年月: {parsed_date.strftime(date_format)}")
                    return parsed_date.strftime(date_format)
                except ValueError as e:
                    logger.debug(f"解析URL日期出错: {e}")
        
        # 4. 如果所有方法都失败，使用当前日期
        logger.warning(f"未找到日期，使用当前日期")
        return datetime.datetime.now().strftime(date_format)
    
    def _extract_article_date(self, soup: BeautifulSoup) -> Optional[str]:
        """
        提取文章发布日期
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            发布日期字符串，如果找不到则返回None
        """
        # 日期的优先级：
        # 1. time标签
        time_tag = soup.find('time')
        if time_tag:
            datetime_attr = time_tag.get('datetime')
            if datetime_attr:
                return datetime_attr
            return time_tag.get_text(strip=True)
        
        # 2. 带有time角色的元素
        time_role = soup.select_one('[role="time"]')
        if time_role:
            return time_role.get_text(strip=True)
        
        # 3. meta标签中的日期
        for meta_name in ['publish_date', 'article:published_time', 'date']:
            meta = soup.find('meta', attrs={'name': meta_name}) or soup.find('meta', attrs={'property': meta_name})
            if meta and meta.get('content'):
                return meta.get('content')
        
        # 4. 尝试从文本中找到日期模式
        # 常见日期格式，如：January 1, 2023, Jan 1, 2023, 01/01/2023, 2023-01-01
        date_patterns = [
            r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{1,2}-\d{1,2}\b'
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, str(soup))
            if date_match:
                return date_match.group(0)
        
        return None
    
    def _extract_article_content(self, soup: BeautifulSoup) -> str:
        """
        提取文章内容
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            文章内容的Markdown格式
        """
        # 查找主要内容容器
        content_elem = None
        
        # 内容容器的优先级：
        # 1. article标签
        content_elem = soup.find('article')
        
        # 2. 带有role="main"属性的元素
        if not content_elem:
            content_elem = soup.select_one('[role="main"]')
        
        # 3. main标签
        if not content_elem:
            content_elem = soup.find('main')
        
        # 4. 如果上述都没有找到，查找包含最多<p>标签的div
        if not content_elem:
            # 查找所有div
            divs = soup.find_all('div')
            if divs:
                # 找出包含最多<p>标签的div
                content_divs = [(div, len(div.find_all('p'))) for div in divs]
                # 过滤掉少于3个段落的div
                content_divs = [(div, count) for div, count in content_divs if count >= 3]
                if content_divs:
                    # 选择包含最多段落的div
                    content_elem = max(content_divs, key=lambda x: x[1])[0]
        
        # 5. 如果仍然没有找到，使用body
        if not content_elem:
            content_elem = soup.body
        
        # 清理内容元素，移除不必要的元素
        if content_elem:
            # 深度复制以避免修改原始对象
            content_elem = BeautifulSoup(str(content_elem), 'lxml')
            
            # 移除导航、页眉、页脚、侧边栏等
            for selector in ['nav', 'header', 'footer', 'aside', '[role="complementary"]', '[role="navigation"]']:
                for el in content_elem.select(selector):
                    el.decompose()
            
            # 修复图片和链接
            self._fix_images_and_links(content_elem)
            
            # 转换为Markdown
            content_html = str(content_elem)
            content_markdown = self.html_converter.handle(content_html)
            
            # 清理Markdown
            content_markdown = self._clean_markdown(content_markdown)
            
            return content_markdown
        
        return "无法提取文章内容。"
    
    def _fix_images_and_links(self, content_elem: BeautifulSoup) -> None:
        """
        修复文章中的图片和链接
        
        Args:
            content_elem: 文章内容元素
        """
        # 处理图片
        for img in content_elem.find_all('img'):
            # 获取图片的src属性
            src = img.get('src', '')
            data_src = img.get('data-src', '')
            lazy_src = img.get('data-lazy-src', '')
            srcset = img.get('srcset', '')
            
            # 尝试从各种可能的属性中获取图片链接
            img_url = src or data_src or lazy_src
            
            # 如果没有找到图片链接，尝试从srcset中提取
            if not img_url and srcset:
                parts = srcset.split(',')
                if parts:
                    first_part = parts[0].strip()
                    img_url = first_part.split(' ')[0]
            
            # 如果找到了图片链接
            if img_url:
                # 检查图片链接是否为相对路径
                if not img_url.startswith(('http://', 'https://', '//')):
                    # 将相对路径转为绝对路径
                    img_url = urljoin(self.start_url, img_url)
                    
                # 处理以//开头的链接
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                
                # 如果是数据URL（base64），保留原样
                if img_url.startswith('data:'):
                    continue
                
                # 更新alt属性，如果没有alt，使用空字符串
                alt_text = img.get('alt', '') or ''
                
                # 创建Markdown格式的图片链接
                img_markdown = f'![{alt_text}]({img_url})'
                img.replace_with(BeautifulSoup(img_markdown, 'html.parser'))
        
        # 处理链接
        for a in content_elem.find_all('a'):
            href = a.get('href', '')
            # 如果链接不为空且不是锚点链接
            if href and not href.startswith('#'):
                # 处理相对路径的链接
                if not href.startswith(('http://', 'https://', '//')):
                    href = urljoin(self.start_url, href)
                
                # 处理以//开头的链接
                if href.startswith('//'):
                    href = 'https:' + href
                    
                # 获取链接文本，如果为空，使用链接本身
                link_text = a.get_text().strip() or href
                
                # 检查链接是否指向图片文件
                img_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff', '.ico']
                is_image_link = any(href.lower().endswith(ext) for ext in img_extensions)
                
                if is_image_link:
                    # 将图片链接转换为Markdown图片
                    img_markdown = f'![{link_text}]({href})'
                    a.replace_with(BeautifulSoup(img_markdown, 'html.parser'))
                else:
                    # 将链接转换为Markdown链接
                    a_markdown = f'[{link_text}]({href})'
                    a.replace_with(BeautifulSoup(a_markdown, 'html.parser'))
    
    def _clean_markdown(self, markdown_content: str) -> str:
        """
        清理和美化Markdown内容
        
        Args:
            markdown_content: 原始Markdown内容
            
        Returns:
            清理后的Markdown内容
        """
        # 1. 移除社交媒体分享链接 (通常出现在文章开头)
        # 这些链接通常没有链接文本，格式为 [](<url>) 或其他格式
        social_media_patterns = [
            r'\* \[\]\(https?://(?:x|twitter)\.com/intent/tweet[^\)]+\)\s*',
            r'\* \[\]\(https?://(?:www\.)?linkedin\.com/shareArticle[^\)]+\)\s*',
            r'\* \[\]\(https?://(?:www\.)?facebook\.com/sharer[^\)]+\)\s*',
            r'\* \[\]\(mailto:[^\)]+\)\s*',
            r'\* \[https?://(?:x|twitter)\.com/intent/tweet[^\]]*\]\(https?://(?:x|twitter)\.com/intent/tweet[^\)]+\)\s*',
            r'\* \[https?://(?:www\.)?linkedin\.com/shareArticle[^\]]*\]\(https?://(?:www\.)?linkedin\.com/shareArticle[^\)]+\)\s*',
            r'\* \[https?://(?:www\.)?facebook\.com/sharer[^\]]*\]\(https?://(?:www\.)?facebook\.com/sharer[^\)]+\)\s*',
            r'\* \[mailto:[^\]]*\]\(mailto:[^\)]+\)\s*'
        ]
        
        for pattern in social_media_patterns:
            markdown_content = re.sub(pattern, '', markdown_content)
        
        # 2. 移除"Related articles"部分 (通常出现在文章末尾)
        related_articles_pattern = r'(?:#{1,6}\s*Related articles[\s\S]+)$'
        markdown_content = re.sub(related_articles_pattern, '', markdown_content)
        
        # 移除"Share"部分 (如果存在)
        share_pattern = r'#{1,6}\s*Share\s*\n[\s\S]*?(?=\n#{1,6}|\Z)'
        markdown_content = re.sub(share_pattern, '', markdown_content)
        
        # 移除可能的推广块，但保留"Learn more"部分
        promo_patterns = [
            r'\*\*\s*Get started with Google Cloud\s*\*\*[\s\S]*?(?=\n#{1,6}|Learn more|\Z)',
            r'\*\*\s*Try it yourself\s*\*\*[\s\S]*?(?=\n#{1,6}|Learn more|\Z)'
        ]
        
        for pattern in promo_patterns:
            markdown_content = re.sub(pattern, '', markdown_content)
        
        # 去除连续多个空行
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        
        # 美化代码块
        markdown_content = re.sub(r'```([^`]+)```', r'\n\n```\1```\n\n', markdown_content)
        
        # 美化图片格式，确保图片前后有空行
        markdown_content = re.sub(r'([^\n])!\[', r'\1\n\n![', markdown_content)
        markdown_content = re.sub(r'\.((?:jpg|jpeg|png|gif|webp|svg))\)([^\n])', r'.\1)\n\n\2', markdown_content)
        
        # 修复重复的图片链接问题
        markdown_content = re.sub(r'(!\[[^\]]*\]\([^\)]+\))\s*\n+\s*\1', r'\1', markdown_content)
        
        # 修复可能的链接问题
        markdown_content = re.sub(r'\]\(\/(?!http)', r'](https://cloud.google.com/', markdown_content)
        
        # 移除任何空链接文本的链接
        markdown_content = re.sub(r'\* \[\]\([^\)]+\)\s*', '', markdown_content)
        
        # 移除引用格式的链接列表
        markdown_content = re.sub(r'>\s*\* \[[^\]]*\]\([^\)]+\)\s*', '', markdown_content)
        
        # 删除末尾的参考链接区，但保留Posted in部分
        reference_section_pattern = r'\n\s*\[\d+\]:\s*http[^\n]+(?:\n\s*\[\d+\]:\s*http[^\n]+)*\s*$'
        posted_in_pattern = r'Posted in.*?(?=\n#{1,6}|\Z)'
        
        # 先查找是否存在Posted in部分
        posted_in_match = re.search(posted_in_pattern, markdown_content)
        posted_in_content = posted_in_match.group(0) if posted_in_match else None
        
        # 删除参考链接
        markdown_content = re.sub(reference_section_pattern, '', markdown_content)
        
        # 移除带有图片链接的相关文章部分，但保留Learn more和Posted in部分
        related_with_images = r'\[[^\]]*\n\n!\[[^\]]*\]\([^\)]+\)\n\n[^\]]*\]\([^\)]+\)'
        markdown_content = re.sub(related_with_images, '', markdown_content)
        
        # 确保Learn more和Posted in部分保留在内容中
        if posted_in_content and posted_in_content not in markdown_content:
            markdown_content += f"\n\n{posted_in_content}"
        
        return markdown_content.strip()
    
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
    
    def _is_likely_blog_post(self, url: str) -> bool:
        """
        判断URL是否可能是博客文章
        
        Args:
            url: 要检查的URL
            
        Returns:
            True如果URL可能是博客文章，否则False
        """
        # 检查URL是否符合GCP博客文章的模式
        url_lower = url.lower()
        
        # 排除明显不是文章的URL
        exclusions = [
            'twitter.com',
            'x.com',
            'facebook.com',
            'linkedin.com',
            'youtube.com',
            'instagram.com',
            'myaccount.google.com',
            'accounts.google.com',
            'console.cloud.google.com',
            'termsofservice',
            'privacy',
            'legal',
            'cookies'
        ]
        
        # 类别页面和主题页面的路径关键词
        category_keywords = [
            '/topics/',
            '/categories/',
            '/tags/',
            '/authors/',
            '/products/',
            '/solutions/'
        ]
        
        # 检查是否在排除列表中
        is_excluded = any(exclusion in url_lower for exclusion in exclusions)
        if is_excluded:
            return False
           
        # 如果URL中包含典型的类别关键词且路径结构简单，很可能是类别页面而非具体文章
        for keyword in category_keywords:
            if keyword in url_lower:
                # 分析URL路径
                url_parts = urlparse(url_lower).path.split('/')
                # 类别页面通常路径较短且没有文章特征（如长数字或日期格式）
                if len(url_parts) <= 4 and not any(re.search(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', part) for part in url_parts):
                    # 检查最后一部分是否是单个词（类别名）而不是文章标题（通常有连字符）
                    last_part = url_parts[-1] if url_parts and url_parts[-1] else ''
                    if not '-' in last_part and not re.search(r'\d{4,}', last_part):
                        return False
            
        # 如果URL包含blog且和原始URL域名相同，则很可能是一篇博客文章
        if '/blog/' in url_lower:
            # 确保是Google Cloud博客而不是外部链接
            if 'cloud.google.com' in url_lower:
                # 分析URL的路径部分
                url_parts = urlparse(url_lower).path.split('/')
                
                # 以下情况很可能是文章而非类别页面：
                # 1. 路径很深（超过4层）
                # 2. 最后一部分包含连字符（常见于文章标题）
                # 3. 最后一部分包含日期格式
                if (len(url_parts) > 4 or 
                    (len(url_parts) > 2 and '-' in url_parts[-1]) or
                    any(re.search(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', part) for part in url_parts)):
                    return True
                
                # 针对products/networking，确保我们爬取这个类别下的文章
                if '/products/networking' in url_lower and len(url_parts) > 4:
                    return True
                
                # 如果是以下模式，则可能是类别页面
                # 例如: /blog/products/networking, /blog/topics/security
                if (len(url_parts) <= 4 and 
                    not any('-' in part for part in url_parts) and
                    ('/products/' in url_lower or '/topics/' in url_lower)):
                    return False
                
                # 其它有/blog/的链接可能是文章
                return True
                
        # 检查URL是否包含明确的文章标识特征
        article_indicators = [
            # 日期格式的路径
            r'/\d{4}/\d{1,2}/\d{1,2}/',  # /2023/04/12/
            r'/\d{4}-\d{1,2}-\d{1,2}/',  # /2023-04-12/
            # 文章ID格式
            r'/post[_-]\d+',             # /post-123456
            r'/article[_-]\d+',          # /article-123456
            # 多段连字符标题（典型的文章slug）
            r'/[a-z0-9]+-[a-z0-9]+-[a-z0-9]+-[a-z0-9]+' # /this-is-article-title
        ]
        
        for pattern in article_indicators:
            if re.search(pattern, url_lower):
                return True
        
        # 默认情况下，我们更谨慎地认为链接不是文章
        return False
