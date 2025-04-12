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

from crawlers.common.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)

class GcpBlogCrawler(BaseCrawler):
    """GCP博客爬虫实现"""
    
    def __init__(self, config: Dict[str, Any], vendor: str, source_type: str):
        """初始化GCP博客爬虫"""
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
            logger.error(f"爬取GCP博客过程中发生错误: {e}")
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
            
            # 如果没有找到任何文章链接，检查当前页面是否就是一篇博客文章
            if not articles and self._is_likely_blog_post(self.start_url):
                logger.info("当前页面可能是单篇博客文章，直接处理")
                title = self._extract_page_title(soup)
                articles.append((title, self.start_url))
            
            return articles
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
        
        # GCP特定策略: 在开发者和实践者页面上有特定的文章卡片
        # 找到所有带有博客文章缩略图的链接，这些通常是实际文章
        thumbnail_links = soup.select('a[href*="/blog/"]')
        # 额外检查: 图片链接通常是完整的博客文章
        for link in thumbnail_links:
            if link.find('img'):
                blog_links.append(link)
                
        # GCP特定策略: 查找带有分钟阅读时间的链接
        # 例如 "5-minute read" 这类文本通常出现在博客文章链接中
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
                    blog_links.append(parent_link)
                # 如果父元素不是链接，尝试找最近的链接祖先或兄弟
                else:
                    parent = element.parent
                    if parent:
                        # 查找父元素的所有链接
                        links = parent.find_all('a', href=True)
                        blog_links.extend(links)
        
        # 策略1: 查找带有文章角色的容器中的链接
        article_roles = soup.select('[role="article"]')
        for container in article_roles:
            links = container.find_all('a', href=True)
            blog_links.extend(links)
        
        # 策略2: 查找文章标签中的链接
        articles = soup.find_all('article')
        for article in articles:
            links = article.find_all('a', href=True)
            blog_links.extend(links)
        
        # 策略3: 查找在标题中的链接
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            links = heading.find_all('a', href=True)
            blog_links.extend(links)
            
            # 同时查找标题后面紧跟的链接
            next_elem = heading.find_next_sibling()
            if next_elem:
                links = next_elem.find_all('a', href=True)
                blog_links.extend(links)
        
        # 策略4: 查找section中的链接（GCP博客常用section组织内容）
        sections = soup.find_all('section')
        for section in sections:
            # 先找标题
            heading = section.find(['h2', 'h3', 'h4'])
            if heading:
                # 然后找链接
                links = section.find_all('a', href=True)
                # 选择性添加链接 - 标题相关的链接更可能是文章链接
                for link in links:
                    # 如果链接文本长度合适，更可能是文章链接
                    link_text = link.get_text(strip=True)
                    if link_text and len(link_text) > 10:
                        blog_links.append(link)
        
        # 策略5: 直接查找可能的博客URL模式链接
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            if href and self._is_likely_blog_post(href):
                blog_links.append(link)
        
        # 去重
        unique_links = []
        seen_hrefs = set()
        for link in blog_links:
            href = link.get('href', '')
            if href and href not in seen_hrefs:
                seen_hrefs.add(href)
                unique_links.append(link)
        
        # 额外过滤 - 只保留可能是博客文章的链接
        filtered_links = []
        for link in unique_links:
            href = link.get('href', '')
            if self._is_likely_blog_post(href):
                filtered_links.append(link)
        
        return filtered_links
    
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
            return aria_label
        
        # 2. 尝试获取链接的文本内容
        link_text = link.get_text(strip=True)
        if link_text and len(link_text) > 5:
            return link_text
        
        # 3. 查找链接周围的内容
        # 检查父元素是否为标题
        parent = link.parent
        if parent and parent.name in ['h1', 'h2', 'h3', 'h4']:
            return parent.get_text(strip=True)
        
        # 4. 查找最近的标题元素
        ancestor = link.find_parent(['div', 'section', 'article'])
        if ancestor:
            heading = ancestor.find(['h1', 'h2', 'h3', 'h4'])
            if heading:
                return heading.get_text(strip=True)
        
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
                    return title_from_url
        
        # 默认标题
        return "Google Cloud Blog Article"
    
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
        
        # 提取文章标题 - 使用HTML结构而非类名
        title = self._extract_article_title(soup)
        
        # 提取发布日期 - 使用HTML结构而非类名
        date = self._extract_article_date(soup)
        
        # 提取作者 - 使用HTML结构而非类名
        author = self._extract_article_author(soup)
        
        # 提取文章内容 - 使用HTML结构而非类名
        content_markdown = self._extract_article_content(soup)
        
        # 提取标签/分类 - 使用HTML结构而非类名
        tags = self._extract_article_tags(soup)
        
        # 返回完整的文章内容字典
        return {
            'title': title,
            'date': date,
            'author': author,
            'content': content_markdown,
            'tags': tags,
            'url': url
        }
    
    def _extract_article_title(self, soup: BeautifulSoup) -> str:
        """
        提取文章标题
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            文章标题
        """
        # 标题的优先级：
        # 1. 主标题h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # 2. 页面标题
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            # 移除网站名称（如果存在）
            return re.sub(r'\s*\|\s*Google Cloud.*$', '', title_text)
        
        # 3. 默认标题
        return "Untitled GCP Blog Post"
    
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
    
    def _extract_article_author(self, soup: BeautifulSoup) -> Optional[str]:
        """
        提取文章作者
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            作者名称，如果找不到则返回None
        """
        # 作者的优先级：
        # 1. rel="author"属性的元素
        author_link = soup.select_one('[rel="author"]')
        if author_link:
            return author_link.get_text(strip=True)
        
        # 2. meta标签中的作者
        for meta_name in ['author', 'article:author', 'dc.creator']:
            meta = soup.find('meta', attrs={'name': meta_name}) or soup.find('meta', attrs={'property': meta_name})
            if meta and meta.get('content'):
                return meta.get('content')
        
        # 3. 包含作者关键词的元素
        author_keywords = ['author', 'by', 'written by', 'posted by']
        for keyword in author_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                # 检查元素是否是字符串
                if isinstance(element, str):
                    parent = element.parent
                    if parent:
                        text = parent.get_text(strip=True)
                        # 使用正则表达式提取作者名
                        author_match = re.search(r'(?:by|author|written by|posted by)[:\s]+([^,\n]+)', text, re.IGNORECASE)
                        if author_match:
                            return author_match.group(1).strip()
        
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
            
            # 转换为Markdown
            content_html = str(content_elem)
            content_markdown = self.html_converter.handle(content_html)
            
            # 清理Markdown
            content_markdown = self._clean_markdown(content_markdown)
            
            return content_markdown
        
        return "无法提取文章内容。"
    
    def _extract_article_tags(self, soup: BeautifulSoup) -> List[str]:
        """
        提取文章标签
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            标签列表
        """
        tags = []
        
        # 优先级：
        # 1. 带有rel="tag"属性的链接
        tag_links = soup.select('a[rel="tag"]')
        for link in tag_links:
            tag = link.get_text(strip=True)
            if tag and tag not in tags:
                tags.append(tag)
        
        # 2. 常见标签容器中的链接
        tag_containers = soup.select('.tags, .categories, .topics, .labels')
        for container in tag_containers:
            links = container.find_all('a')
            for link in links:
                tag = link.get_text(strip=True)
                if tag and tag not in tags:
                    tags.append(tag)
        
        # 3. 带有标签相关关键词的元素
        tag_keywords = ['tag', 'category', 'topic', 'label']
        for keyword in tag_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                parent = element.parent
                if parent:
                    links = parent.find_all('a')
                    for link in links:
                        tag = link.get_text(strip=True)
                        if tag and tag not in tags:
                            tags.append(tag)
        
        return tags
    
    def _is_likely_blog_post(self, url: str) -> bool:
        """
        判断URL是否可能是博客文章
        
        Args:
            url: 要判断的URL
            
        Returns:
            True如果URL可能是博客文章，否则False
        """
        # 检查URL是否符合GCP博客文章的模式
        url_lower = url.lower()
        
        # GCP博客文章URL通常包含以下路径之一
        blog_indicators = [
            '/blog/products/',
            '/blog/topics/',
        ]
        
        # 更具体的博客文章指示器 - 这些通常指向具体文章
        specific_indicators = [
            '-is-transforming-',
            '-with-google-cloud',
            '-on-google-cloud',
            '-for-ai-',
            '-service-with-',
            '-guide-to-',
        ]
        
        # 排除明显不是文章的URL
        exclusions = [
            '/tag/', 
            '/category/', 
            '/author/', 
            '/archive/', 
            '/search/', 
            '/feed/', 
            '/about/',
            '/contact/',
            '/docs/',
            '/terms/',
            '/privacy/',
            '/help/',
            '/support/',
            'twitter.com',
            'x.com',
            'facebook.com',
            'linkedin.com',
            'youtube.com',
            'instagram.com',
            # 排除列表页面
            '/developers-practitioners',
            '/inside-google-cloud',
            '/products/ai-machine-learning',
            '/products/networking'
        ]
        
        # 检查URL是否符合条件
        is_general_blog = any(indicator in url_lower for indicator in blog_indicators)
        is_specific_blog = any(indicator in url_lower for indicator in specific_indicators)
        is_excluded = any(exclusion in url_lower for exclusion in exclusions)
        
        # 分析URL结构 - 博客文章URL通常有较深的路径结构
        path_segments = url_lower.split('/')
        is_deep_path = len(path_segments) >= 6  # 一个合理的深度阈值
        
        # 针对Google Cloud特殊的URL模式
        # 例如： https://cloud.google.com/blog/products/ai-machine-learning/how-signal-iduna-supercharges-customer-service-with-gen-ai
        # 这种URL包含很长的标题段，通常是实际文章
        has_long_title_segment = False
        for segment in path_segments:
            if len(segment) > 20 and '-' in segment:  # 长标题段通常包含连字符
                has_long_title_segment = True
                break
        
        # 综合判断
        return (is_general_blog or is_specific_blog or has_long_title_segment) and not is_excluded
    
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
            return "gcp_blog_post"
            
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
            return "gcp_blog_post"
            
        # 确保文件名不过长，最多保留80个字符
        if len(filename) > 80:
            filename = filename[:77] + '...'
        
        return filename 