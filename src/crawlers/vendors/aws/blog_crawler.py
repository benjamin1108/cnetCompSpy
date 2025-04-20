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

from src.crawlers.common.base_crawler import BaseCrawler, metadata_lock

logger = logging.getLogger(__name__)

class AwsBlogCrawler(BaseCrawler):
    """AWS博客爬虫实现"""
    
    def __init__(self, config: Dict[str, Any], vendor: str, source_type: str):
        """初始化AWS博客爬虫"""
        super().__init__(config, vendor, source_type)
        self.source_config = config.get('sources', {}).get(vendor, {}).get(source_type, {})
        self.start_url = self.source_config.get('url')
    
    def _crawl(self) -> List[str]:
        """
        爬取AWS博客
        
        Returns:
            保存的文件路径列表
        """
        if not self.start_url:
            logger.error("未配置起始URL")
            return []
        
        saved_files = []
        
        try:
            # 获取博客列表页
            logger.info(f"获取AWS博客列表页: {self.start_url}")
            
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
            
            # 检查是否启用了强制模式
            force_mode = self.crawler_config.get('force', False)
            if force_mode:
                logger.info("强制模式已启用，将重新爬取所有文章，忽略本地metadata")
                filtered_article_links = article_links
                logger.info(f"强制模式下爬取所有 {len(filtered_article_links)} 篇文章")
            else:
                # 非强制模式下，过滤已爬取的文章链接，避免不必要的网络请求
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
                    
                    # 解析文章内容和发布日期
                    article_content_and_date = self._parse_article_content(url, article_html)
                    
                    # 保存为Markdown
                    file_path = self.save_to_markdown(url, title, article_content_and_date)
                    saved_files.append(file_path)
                    logger.info(f"已保存文章: {title} -> {file_path}")
                    
                    # 间隔一段时间再爬取下一篇
                    if idx < len(filtered_article_links):
                        time.sleep(self.interval)
                    
                except Exception as e:
                    logger.error(f"爬取文章失败: {url} - {e}")
            
            return saved_files
        except Exception as e:
            logger.error(f"爬取AWS博客过程中发生错误: {e}")
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
            # 新版AWS博客页面的文章选择器
            # 先尝试获取所有可能的文章容器
            article_containers = soup.select('.blog-post, .blog-card, .aws-card, .aws-card-blog, .lb-card, article, .blog-media, .blog-entry, .aws-blog-post, .blog-post-group, .blog-post-card')
            
            if not article_containers:
                # 使用更通用的选择器
                logger.warning("未找到指定文章容器，尝试使用通用选择器")
                
                # 首先尝试找到博客主区域
                content_area = (
                    soup.select_one('main, .main-content, #main, .content, .blog-content, #content') or 
                    soup.select_one('.lb-main, .aws-main, .blog-list') or 
                    soup.body
                )
                
                # 从主区域中找到所有链接
                all_links = content_area.find_all('a', href=True) if content_area else soup.find_all('a', href=True)
                
                # 筛选博客文章链接
                blog_links = []
                for link in all_links:
                    href = link.get('href', '')
                    # AWS博客文章URL通常包含 /blogs/ 或 /blog/ 路径
                    if '/blogs/' in href or '/blog/' in href or 'aws.amazon.com' in href and '/post/' in href:
                        if not any(x in href for x in ['category', 'tag', 'archive', 'author', 'about', 'contact', 'feed']):
                            # 获取标题文本
                            title = link.get_text(strip=True)
                            if not title or len(title) < 5:  # 忽略太短的标题
                                continue
                                
                            # 构建完整URL
                            url = href if href.startswith('http') else urljoin(self.start_url, href)
                            
                            # 避免重复
                            if url not in [x[1] for x in blog_links]:
                                blog_links.append((title, url))
                
                # 使用URL模式进一步筛选链接
                for title, url in blog_links:
                    if self._is_likely_blog_post(url):
                        articles.append((title, url))
            else:
                # 处理找到的文章容器
                for container in article_containers:
                    # 尝试找到标题元素
                    title_elem = (
                        container.select_one('h1, h2, h3, h4, h5, .lb-txt-bold, .blog-title, .aws-blog-title, .blog-post-title') or 
                        container.select_one('.title, .post-title, .entry-title') or
                        container.select_one('a')
                    )
                    
                    if title_elem:
                        # 获取标题
                        title = title_elem.get_text(strip=True)
                        
                        # 获取链接元素
                        link_elem = None
                        if title_elem.name == 'a':
                            link_elem = title_elem
                        else:
                            # 在标题元素或容器中查找链接
                            link_elem = title_elem.find('a') or container.find('a', href=True)
                        
                        if link_elem and link_elem.get('href'):
                            href = link_elem['href']
                            # 构建完整URL
                            url = href if href.startswith('http') else urljoin(self.start_url, href)
                            
                            # 检查是否为有效的博客文章URL
                            if self._is_likely_blog_post(url):
                                # 避免重复
                                if url not in [x[1] for x in articles]:
                                    articles.append((title, url))
            
            logger.info(f"找到 {len(articles)} 篇潜在的博客文章链接")
            
            # 如果没有找到任何文章，尝试直接爬取当前页面
            if not articles and self._is_likely_blog_post(self.start_url):
                page_title = soup.find('title')
                title = page_title.text.strip() if page_title else "AWS Blog Post"
                articles.append((title, self.start_url))
                logger.info(f"未找到文章列表，将当前页面作为博客文章处理: {title}")
        
        except Exception as e:
            logger.error(f"解析文章链接出错: {e}")
        
        # 判断是否为测试模式
        test_mode = self.source_config.get('test_mode', False)
        
        # 如果是测试模式，只爬取1篇文章
        if test_mode:
            logger.info("测试模式：仅爬取1篇文章")
            return articles[:1]
        
        # 否则根据配置的限制数量爬取
        limit = self.crawler_config.get('article_limit', 50)
        logger.info(f"爬取模式：限制爬取{limit}篇文章")
        return articles[:limit]
    
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
        
        # AWS博客文章URL的常见模式
        blog_patterns = [
            r'/blogs/[^/]+/[^/]+',  # 如 /blogs/networking-and-content-delivery/article-name
            r'/blog/[^/]+',         # 如 /blog/article-name
            r'/post/[^/]+',         # 如 /post/article-name
            r'/\d{4}/\d{2}/[^/]+',  # 如 /2022/01/article-name (日期格式)
            r'/news/[^/]+',         # 如 /news/article-name
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
    
    def _parse_article_content(self, url: str, html: str) -> Tuple[str, Optional[str]]:
        """
        解析文章内容和发布日期
        
        Args:
            url: 文章URL
            html: 文章页面HTML
            
        Returns:
            (Markdown内容, 发布日期)元组，如果找不到日期则日期为None
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # 提取发布日期
        pub_date = self._extract_publish_date(soup)
        
        # 1. 移除页头、页尾、侧边栏等非内容区域
        self._clean_non_content(soup)
        
        # 2. 尝试更精确地定位文章主体内容
        article = self._locate_article_content(soup, url)
        
        if not article:
            logger.warning(f"未找到文章主体: {url}")
            return "", pub_date
        
        # 3. 处理图片 - 使用原始URL而不是下载到本地
        for img in article.find_all('img'):
            if not img.get('src'):
                continue
            
            # 将相对URL转换为绝对URL
            img_url = urljoin(url, img['src'])
            img['src'] = img_url
            
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
        
        # 4. 提取正文内容并转换为Markdown
        article_md = self._html_to_markdown(article)
        
        return article_md, pub_date
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """
        从文章中提取发布日期
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            发布日期字符串 (YYYY_MM_DD格式)，如果找不到则返回None
        """
        date_format = "%Y_%m_%d"
        
        # 特别针对AWS博客的日期提取 - 优先检查time标签
        time_elements = soup.find_all('time')
        if time_elements:
            for time_elem in time_elements:
                # 检查具有datePublished属性的time标签
                if time_elem.get('property') == 'datePublished' and time_elem.get('datetime'):
                    datetime_str = time_elem.get('datetime')
                    try:
                        # 处理ISO格式的日期时间 "2025-04-08T17:34:26-07:00"
                        # 从datetime属性中提取日期部分
                        date_part = datetime_str.split('T')[0]
                        parsed_date = datetime.datetime.strptime(date_part, '%Y-%m-%d')
                        logger.info(f"从time标签的datetime属性解析到日期: {parsed_date.strftime(date_format)}")
                        return parsed_date.strftime(date_format)
                    except (ValueError, IndexError) as e:
                        logger.debug(f"解析time标签的datetime属性失败: {e}")
                
                # 如果没有datetime属性或解析失败，尝试解析标签文本
                date_text = time_elem.get_text().strip()
                if date_text:
                    try:
                        # 尝试解析 "08 APR 2025" 格式
                        parsed_date = datetime.datetime.strptime(date_text, '%d %b %Y')
                        logger.info(f"从time标签的文本内容解析到日期: {parsed_date.strftime(date_format)}")
                        return parsed_date.strftime(date_format)
                    except ValueError:
                        try:
                            # 尝试解析 "April 08, 2025" 格式
                            parsed_date = datetime.datetime.strptime(date_text, '%B %d, %Y')
                            logger.info(f"从time标签的文本内容解析到日期: {parsed_date.strftime(date_format)}")
                            return parsed_date.strftime(date_format)
                        except ValueError:
                            continue

        # 查找元数据中的日期 - AWS博客页面通常在meta标签中也有日期信息
        meta_published = soup.find('meta', property='article:published_time') or soup.find('meta', property='publish_date')
        if meta_published and meta_published.get('content'):
            try:
                content = meta_published.get('content')
                # 处理ISO格式日期
                if 'T' in content:
                    date_part = content.split('T')[0]
                    parsed_date = datetime.datetime.strptime(date_part, '%Y-%m-%d')
                else:
                    parsed_date = datetime.datetime.strptime(content, '%Y-%m-%d')
                logger.info(f"从meta标签解析到日期: {parsed_date.strftime(date_format)}")
                return parsed_date.strftime(date_format)
            except (ValueError, IndexError) as e:
                logger.debug(f"解析meta标签日期失败: {e}")
        
        # 尝试不同的选择器来定位日期元素
        date_selectors = [
            '.lb-blog-header__date', '.blog-date', '.date', '.published-date', '.post-date',
            '.post-meta time', '.post-meta .date', '.entry-date', '.meta-date',
            'time', '[itemprop="datePublished"]', '.aws-blog-post-date', '.aws-date'
        ]
        
        # 遍历所有可能的选择器
        for selector in date_selectors:
            date_elements = soup.select(selector)
            
            if date_elements:
                for date_elem in date_elements:
                    # 尝试获取datetime属性
                    date_str = date_elem.get('datetime') or date_elem.text.strip()
                    if date_str:
                        try:
                            # 尝试多种日期格式
                            for date_pattern in [
                                '%Y-%m-%d', '%Y/%m/%d', '%b %d, %Y', '%B %d, %Y',
                                '%d %b %Y', '%d %B %Y', '%m/%d/%Y', '%d-%m-%Y',
                                '%Y年%m月%d日', '%Y.%m.%d'
                            ]:
                                try:
                                    # 提取日期字符串
                                    # 如果字符串中包含时间，只保留日期部分
                                    if ' ' in date_str and not any(month in date_str for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'January', 'February', 'March', 'April', 'June', 'July', 'August', 'September', 'October', 'November', 'December']):
                                        date_str = date_str.split(' ')[0]
                                    
                                    parsed_date = datetime.datetime.strptime(date_str, date_pattern)
                                    logger.info(f"从选择器 {selector} 解析到日期: {parsed_date.strftime(date_format)}")
                                    return parsed_date.strftime(date_format)
                                except ValueError:
                                    continue
                        except Exception as e:
                            logger.debug(f"日期解析错误: {e}")
        
        # 如果通过选择器没找到，尝试在文本中搜索日期模式
        try:
            text = soup.get_text()
            
            # 常见日期格式的正则表达式
            date_patterns = [
                # YYYY-MM-DD
                r'(\d{4}-\d{1,2}-\d{1,2})',
                # YYYY/MM/DD
                r'(\d{4}/\d{1,2}/\d{1,2})',
                # Month DD, YYYY
                r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}',
                # DD Month YYYY
                r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
                r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',
                # MM/DD/YYYY
                r'(\d{1,2}/\d{1,2}/\d{4})',
            ]
            
            for pattern in date_patterns:
                matches = re.search(pattern, text)
                if matches:
                    date_str = matches.group(0)
                    try:
                        # 尝试解析找到的日期
                        if '-' in date_str:
                            parsed_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                        elif '/' in date_str:
                            # 尝试两种不同的日期格式（YYYY/MM/DD 或 MM/DD/YYYY）
                            try:
                                parsed_date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
                            except ValueError:
                                parsed_date = datetime.datetime.strptime(date_str, '%m/%d/%Y')
                        elif ',' in date_str:
                            try:
                                parsed_date = datetime.datetime.strptime(date_str, '%B %d, %Y')
                            except ValueError:
                                parsed_date = datetime.datetime.strptime(date_str, '%b %d, %Y')
                        else:
                            try:
                                parsed_date = datetime.datetime.strptime(date_str, '%d %B %Y')
                            except ValueError:
                                parsed_date = datetime.datetime.strptime(date_str, '%d %b %Y')
                        
                        logger.info(f"从文本内容解析到日期: {parsed_date.strftime(date_format)}")
                        return parsed_date.strftime(date_format)
                    except ValueError:
                        continue
        except Exception as e:
            logger.debug(f"从文本提取日期错误: {e}")
        
        # 如果找不到日期，使用当前日期
        logger.warning("未找到发布日期，使用当前日期")
        return datetime.datetime.now().strftime(date_format)
    
    def _clean_non_content(self, soup: BeautifulSoup) -> None:
        """
        移除页头、页尾、侧边栏等非内容区域
        
        Args:
            soup: BeautifulSoup对象
        """
        # 移除常见的页头元素
        for header in soup.select('header, .header, #header, .top-nav, .aws-header, .navigation, nav, .top-bar, .lb-header'):
            header.decompose()
        
        # 移除常见的页尾元素
        for footer in soup.select('footer, .footer, #footer, .aws-footer, .bottom-bar, .lb-footer'):
            footer.decompose()
        
        # 移除常见的侧边栏元素
        for sidebar in soup.select('.sidebar, #sidebar, .side-nav, .aws-sidebar, .column-right, .column-left, aside'):
            sidebar.decompose()
        
        # 移除常见的广告和推广元素
        for promo in soup.select('.ad, .ads, .advertisement, .promo, .promotion, .banner, .aws-promo, .aws-banner'):
            promo.decompose()
        
        # 移除导航元素
        for nav in soup.select('.breadcrumb, .breadcrumbs, .navigation, .nav, .menu'):
            nav.decompose()
        
        # 移除评论区
        for comments in soup.select('.comments, #comments, .comment-section, .disqus, .discourse'):
            comments.decompose()
        
        # 移除社交媒体分享按钮
        for social in soup.select('.share, .social, .social-media, .social-buttons, .aws-social'):
            social.decompose()
        
        # 移除相关文章推荐
        for related in soup.select('.related, .related-posts, .suggested, .aws-related, .recommended'):
            related.decompose()
        
        # 移除脚本、样式等无关元素
        for tag in soup.find_all(['script', 'style', 'noscript', 'iframe', 'svg']):
            tag.decompose()
    
    def _locate_article_content(self, soup: BeautifulSoup, url: str) -> Optional[BeautifulSoup]:
        """
        更精确地定位文章主体内容
        
        Args:
            soup: BeautifulSoup对象
            url: 文章URL
            
        Returns:
            包含文章主体内容的BeautifulSoup对象，或None
        """
        # 优先级从高到低尝试找到文章主体
        selectors = [
            # 最可能的文章内容选择器
            'article .lb-post-content',
            'article .lb-grid-content',
            '.blog-post-content',
            '.post-content',
            '.article-content',
            '.entry-content',
            '.post-body',
            '.content-body',
            
            # 次优先级选择器
            'main article',
            'main .content',
            'article',
            '.post',
            '#content .post',
            '.blog-content',
            '.lb-grid-container > div > div',  # AWS博客通常使用的容器结构
            
            # 最后的备选选择器
            'main',
            '#content',
            '.content',
            '.container'
        ]
        
        # 尝试所有选择器
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                # 找到内容最长的元素，这通常是正文
                main_element = max(elements, key=lambda x: len(str(x)))
                logger.debug(f"找到文章主体，使用选择器: {selector}")
                return main_element
        
        # 如果还是找不到，尝试一个启发式方法：寻找最长的<div>或<section>
        candidates = []
        for tag in soup.find_all(['div', 'section']):
            # 排除明显不是内容的元素
            if tag.has_attr('class') and any(c in str(tag['class']) for c in ['header', 'footer', 'sidebar', 'menu', 'nav']):
                continue
            
            # 排除太短的内容
            if len(str(tag)) < 1000:  # 文章通常至少有1000个字符
                continue
            
            # 判断是否包含文章特征(段落、标题等)
            if len(tag.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol'])) > 5:
                candidates.append(tag)
        
        if candidates:
            # 找到内容最长的候选元素
            main_element = max(candidates, key=lambda x: len(str(x)))
            logger.debug("使用启发式方法找到文章主体")
            return main_element
        
        # 最后的备选：返回<body>
        body = soup.find('body')
        if body:
            logger.warning(f"未找到具体文章主体，使用<body>: {url}")
            return body
        
        return None
    
    def _html_to_markdown(self, article: BeautifulSoup) -> str:
        """
        将HTML转换为Markdown，并进行额外的清理
        
        Args:
            article: 包含文章内容的BeautifulSoup对象
            
        Returns:
            清理后的Markdown内容
        """
        # 移除推广链接和无关元素
        for tag in article.find_all(['button', 'input', 'form']):
            tag.decompose()
        
        # 去掉空链接
        for a in article.find_all('a'):
            if not a.get_text(strip=True):
                a.replace_with_children()
        
        # 保留文章主体内容
        article_html = str(article)
        
        # 使用html2text转换为Markdown
        article_md = self.html_converter.handle(article_html)
        
        # 清理Markdown
        article_md = self._clean_markdown(article_md)
        
        return article_md
    
    def _clean_markdown(self, markdown_text: str) -> str:
        """
        清理Markdown文本，去除多余内容并美化格式
        
        Args:
            markdown_text: 原始Markdown文本
            
        Returns:
            清理后的Markdown文本
        """
        # 去除连续多个空行
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        # 美化代码块
        markdown_text = re.sub(r'```([^`]+)```', r'\n\n```\1```\n\n', markdown_text)
        
        # 美化图片格式，确保图片前后有空行
        markdown_text = re.sub(r'([^\n])!\[', r'\1\n\n![', markdown_text)
        markdown_text = re.sub(r'\.((?:jpg|jpeg|png|gif|webp|svg))\)([^\n])', r'.\1)\n\n\2', markdown_text)
        
        return markdown_text
    
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
