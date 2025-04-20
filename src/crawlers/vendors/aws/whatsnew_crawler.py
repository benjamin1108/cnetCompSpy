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
from src.utils.thread_pool import get_thread_pool

logger = logging.getLogger(__name__)

class AwsWhatsnewCrawler(BaseCrawler):
    """AWS What's New 爬虫实现"""
    
    def __init__(self, config: Dict[str, Any], vendor: str, source_type: str):
        """初始化AWS What's New爬虫"""
        super().__init__(config, vendor, source_type)
        self.source_config = config.get('sources', {}).get(vendor, {}).get(source_type, {})
        self.start_url = self.source_config.get('url')
        self.max_pages = self.source_config.get('max_pages', 100)  # 从配置文件中读取最大页数，默认为100
        # 初始化线程池
        self.thread_pool = get_thread_pool(
            api_rate_limit=self.crawler_config.get('api_rate_limit', 60),
            max_threads=self.crawler_config.get('max_workers', 100)
        )
    
    def _crawl(self) -> List[str]:
        """
        爬取AWS What's New
        
        Returns:
            保存的文件路径列表
        """
        if not self.start_url:
            logger.error("未配置起始URL")
            return []
        
        saved_files = []
        
        try:
            # 获取What's New列表页
            logger.info(f"获取AWS What's New列表页: {self.start_url}")
            
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
                logger.error(f"获取What's New列表页失败: {self.start_url}")
                return []
            
            # 解析What's New列表，获取公告链接
            article_links = self._parse_article_links(html)
            logger.info(f"解析到 {len(article_links)} 篇公告链接")
            
            # 如果是测试模式或有文章数量限制，截取所需数量的文章链接
            test_mode = self.source_config.get('test_mode', False)
            
            if test_mode:
                logger.info("爬取模式：限制爬取1篇公告")
                article_links = article_links[:1]
            else:
                logger.info(f"爬取模式：限制爬取{self.max_pages}篇公告")
                article_links = article_links[:self.max_pages]
            
            # 检查是否启用了强制模式
            force_mode = self.crawler_config.get('force', False)
            if force_mode:
                logger.info("强制模式已启用，将重新爬取所有公告，忽略本地metadata")
                filtered_article_links = article_links
                logger.info(f"强制模式下爬取所有 {len(filtered_article_links)} 篇公告")
            else:
                # 非强制模式下，过滤已爬取的公告链接，避免不必要的网络请求
                filtered_article_links = []
                already_crawled_count = 0
                
                with metadata_lock:  # 使用锁确保线程安全
                    for title, url in article_links:
                        # 只有当URL在metadata中存在且文件也存在时才跳过
                        if (url in self.metadata and 
                            'filepath' in self.metadata[url] and 
                            os.path.exists(self.metadata[url]['filepath'])):
                            # 公告已爬取过且文件存在，直接添加到结果中
                            already_crawled_count += 1
                            logger.info(f"跳过已爬取的公告: {title} ({url})")
                            saved_files.append(self.metadata[url]['filepath'])
                        else:
                            # 公告未爬取过或文件不存在，添加到待爬取列表
                            if url in self.metadata:
                                logger.info(f"公告元数据存在但文件缺失，将重新爬取: {title} ({url})")
                            filtered_article_links.append((title, url))
                
                logger.info(f"过滤后: {len(filtered_article_links)} 篇新公告需要爬取，{already_crawled_count} 篇公告已存在")
            
            # 使用线程池并行爬取公告
            logger.info(f"使用线程池并行爬取 {len(filtered_article_links)} 篇公告")
            self.thread_pool.start()
            
            def crawl_article(title, url):
                try:
                    logger.info(f"线程任务: 爬取公告: {title}")
                    # 尝试获取公告内容 - 优先使用requests
                    article_html = None
                    try:
                        logger.info(f"使用requests库获取公告内容: {url}")
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                        response = requests.get(url, headers=headers, timeout=30)
                        if response.status_code == 200:
                            article_html = response.text
                            logger.info("使用requests库成功获取到公告内容")
                        else:
                            logger.error(f"请求返回非成功状态码: {response.status_code}")
                    except Exception as e:
                        logger.error(f"使用requests库获取公告失败: {e}")
                    
                    # 如果requests失败，才尝试Selenium
                    if not article_html:
                        logger.info(f"尝试使用Selenium获取公告内容: {url}")
                        article_html = self._get_selenium(url)
                    
                    if not article_html:
                        logger.warning(f"获取公告内容失败: {url}")
                        return None
                    
                    # 解析公告内容和发布日期
                    article_content_and_date = self._parse_article_content(url, article_html)
                    
                    # 保存为Markdown
                    file_path = self.save_to_markdown(url, title, article_content_and_date)
                    logger.info(f"已保存公告: {title} -> {file_path}")
                    return file_path
                except Exception as e:
                    logger.error(f"爬取公告失败: {url} - {e}")
                    return None
            
            # 添加任务到线程池
            for title, url in filtered_article_links:
                self.thread_pool.add_task(crawl_article, title, url)
            
            # 等待所有任务完成
            self.thread_pool.task_queue.join()
            logger.info("所有公告爬取任务已完成")
            
            # 获取结果
            results = self.thread_pool.get_results()
            for result in results:
                if result:
                    saved_files.append(result)
            
            return saved_files
        except Exception as e:
            logger.error(f"爬取AWS What's New过程中发生错误: {e}")
            return saved_files
        finally:
            # 关闭WebDriver
            self._close_driver()
    
    def _parse_article_links(self, html: str) -> List[Tuple[str, str]]:
        """
        从What's New页面解析公告链接
        
        Args:
            html: What's New页面HTML（备用）
            
        Returns:
            公告链接列表，每项为(标题, URL)元组
        """
        articles = []
        
        try:
            # 使用新的API端点循环爬取公告
            api_url = "https://aws.amazon.com/api/dirs/items/search"
            params = {
                "item.directoryId": "whats-new-v2",
                "sort_by": "item.additionalFields.postDateTime",
                "sort_order": "desc",
                "size": "20",
                "item.locale": "en_US",
                "tags.id": "whats-new-v2#general-products#amazon-vpc|whats-new-v2#general-products#aws-direct-connect|whats-new-v2#general-products#amazon-route-53|whats-new-v2#general-products#elastic-load-balancing|whats-new-v2#general-products#amazon-cloudfront|whats-new-v2#general-products#amazon-api-gateway|whats-new-v2#marketing-marchitecture#networking|whats-new-v2#marketing-marchitecture#networking-and-content-delivery|whats-new-v2#general-products#aws-global-accelerator|whats-new-v2#general-products#aws-transit-gateway|whats-new-v2#general-products#aws-vpn|whats-new-v2#general-products#aws-site-to-site|whats-new-v2#general-products#aws-client-vpn|whats-new-v2#general-products#aws-app-mesh"
            }
            page = 1
            total_items = 0
            
            while True:
                params["page"] = str(page)
                full_url = f"{api_url}?{requests.compat.urlencode(params)}"
                logger.info(f"请求AWS What's New API，第 {page} 页: {full_url}")
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(api_url, params=params, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("items"):
                            page_items = data["items"]
                            for item in page_items:
                                item_data = item.get("item", {})
                                headline = item_data.get("additionalFields", {}).get("headline", "")
                                url_path = item_data.get("additionalFields", {}).get("headlineUrl", "")
                                
                                if headline and url_path:
                                    full_url_item = f"https://aws.amazon.com{url_path}" if not url_path.startswith("http") else url_path
                                    articles.append((headline, full_url_item))
                            
                            total_items += len(page_items)
                            logger.info(f"从API第 {page} 页获取到 {len(page_items)} 篇公告，累计 {total_items} 篇")
                            
                            # 检查是否还有更多数据
                            if len(page_items) < int(params["size"]) or total_items >= self.max_pages:
                                logger.info(f"API数据获取完成，共 {total_items} 篇公告")
                                break
                            page += 1
                        else:
                            logger.warning(f"API第 {page} 页响应中没有找到公告项")
                            break
                    else:
                        logger.error(f"API请求失败，状态码: {response.status_code}")
                        break
                except Exception as e:
                    logger.error(f"API请求异常: {e}")
                    break
        except Exception as e:
            logger.error(f"解析公告链接出错: {e}")
        
        # 判断是否为测试模式
        test_mode = self.source_config.get('test_mode', False)
        
        # 如果是测试模式，只爬取1篇公告
        if test_mode:
            logger.info("测试模式：仅爬取1篇公告")
            return articles[:1]
        
        # 否则根据配置的限制数量爬取
        limit = self.max_pages
        logger.info(f"爬取模式：限制爬取{limit}篇公告")
        return articles[:limit]
    
    def _is_likely_whatsnew_post(self, url: str) -> bool:
        """
        判断URL是否可能是What's New公告
        
        Args:
            url: 要检查的URL
            
        Returns:
            True如果URL可能是What's New公告，否则False
        """
        # 移除协议和域名部分
        parsed = urlparse(url)
        path = parsed.path
        
        # AWS What's New公告URL的常见模式
        whatsnew_patterns = [
            r'/whats-new/[^/]+',  # 如 /whats-new/article-name
            r'/about-aws/whats-new/[^/]+',  # 如 /about-aws/whats-new/article-name
            r'/new/[^/]+',         # 如 /new/article-name
            r'/announcements/[^/]+', # 如 /announcements/article-name
        ]
        
        # 检查是否匹配任何公告模式
        for pattern in whatsnew_patterns:
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
        whatsnew_keywords = ['whats-new', 'whatsnew', 'announcement', 'new', 'release']
        for keyword in whatsnew_keywords:
            if keyword in path.lower():
                return True
                
        # 默认返回False，宁可错过也不要误报
        return False
    
    def _parse_article_content(self, url: str, html: str) -> Tuple[str, Optional[str]]:
        """
        解析公告内容和发布日期
        
        Args:
            url: 公告URL
            html: 公告页面HTML
            
        Returns:
            (Markdown内容, 发布日期)元组，如果找不到日期则日期为None
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # 提取发布日期
        pub_date = self._extract_publish_date(soup)
        
        # 1. 移除页头、页尾、侧边栏等非内容区域
        self._clean_non_content(soup)
        
        # 2. 尝试更精确地定位公告主体内容
        article = self._locate_article_content(soup, url)
        
        if not article:
            logger.warning(f"未找到公告主体: {url}")
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
        
        # 移除页面底部的"下一页"或"阅读更多"链接，这些链接通常会在Markdown中显示为 [ »]()
        for a in article.find_all('a'):
            # 检查链接文本是否只包含特殊字符或为空
            link_text = a.get_text(strip=True)
            if not link_text or link_text in ['»', '>', '→', 'Next', 'More', 'Read More']:
                a.decompose()
                logger.debug(f"移除了页面底部的导航链接: {link_text}")
        
        # 4. 提取正文内容并转换为Markdown
        article_md = self._html_to_markdown(str(article))
        
        # 移除Markdown中可能残留的 [ »]() 或类似模式
        article_md = re.sub(r'\[\s*[»→>]\s*\]\(\s*\)', '', article_md)
        article_md = re.sub(r'\[\s*(Next|More|Read More)\s*\]\(\s*\)', '', article_md)
        
        return article_md, pub_date
    
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
        更精确地定位公告主体内容
        
        Args:
            soup: BeautifulSoup对象
            url: 公告URL
            
        Returns:
            包含公告主体内容的BeautifulSoup对象，或None
        """
        # 优先级从高到低尝试找到公告主体
        selectors = [
            # 最可能的公告内容选择器
            'article .lb-post-content',
            'article .lb-grid-content',
            '.whatsnew-content',
            '.announcement-content',
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
            '.whatsnew-detail',
            '.lb-grid-container > div > div',  # AWS通常使用的容器结构
            
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
                logger.debug(f"找到公告主体，使用选择器: {selector}")
                return main_element
        
        # 如果还是找不到，尝试一个启发式方法：寻找最长的<div>或<section>
        candidates = []
        for tag in soup.find_all(['div', 'section']):
            # 排除明显不是内容的元素
            if tag.has_attr('class') and any(c in str(tag['class']) for c in ['header', 'footer', 'sidebar', 'menu', 'nav']):
                continue
            
            # 排除太短的内容
            if len(str(tag)) < 1000:  # 公告通常至少有1000个字符
                continue
            
            # 判断是否包含文章特征(段落、标题等)
            if len(tag.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol'])) > 5:
                candidates.append(tag)
        
        if candidates:
            # 找到内容最长的候选元素
            main_element = max(candidates, key=lambda x: len(str(x)))
            logger.debug("使用启发式方法找到公告主体")
            return main_element
        
        # 最后的备选：返回<body>
        body = soup.find('body')
        if body:
            logger.warning(f"未找到具体公告主体，使用<body>: {url}")
            return body
        
        return None
    
    def save_to_markdown(self, url: str, title: str, content_and_date: Tuple[str, Optional[str]]) -> str:
        """
        保存内容为Markdown文件，调用基类方法
        
        Args:
            url: 公告URL
            title: 公告标题
            content_and_date: 公告内容和发布日期的元组
            
        Returns:
            保存的文件路径
        """
        return super().save_to_markdown(url, title, content_and_date)
