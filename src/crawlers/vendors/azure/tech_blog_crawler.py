#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re
import time
import json
import hashlib
from typing import Dict, Any, List, Tuple, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.crawlers.common.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)

class AzureTechBlogCrawler(BaseCrawler):
    """Azure技术博客爬虫"""
    
    def __init__(self, config: Dict[str, Any], vendor: str, source_type: str):
        """初始化爬虫"""
        super().__init__(config, vendor, source_type)
        
        # 获取源配置
        self.source_config = config.get('sources', {}).get(vendor, {}).get(source_type, {})
        self.start_url = self.source_config.get('url')
        
        # 如果未指定URL，使用默认值
        if not self.start_url:
            self.start_url = "https://techcommunity.microsoft.com/t5/azure-networking-blog/bg-p/AzureNetworkingBlog"
        
        # 设置HTML转Markdown转换器
        self._init_html_converter()
    
    def _init_html_converter(self) -> None:
        """初始化HTML到Markdown的转换器"""
        try:
            import html2text
            self.h2t = html2text.HTML2Text()
            self.h2t.ignore_links = False
            self.h2t.wrap_links = False
            self.h2t.ignore_images = False
            self.h2t.images_to_alt = False
            self.h2t.wrap_list_items = True
            self.h2t.inline_links = True
            self.h2t.protect_links = True
            self.h2t.unicode_snob = True
            self.h2t.body_width = 0  # 禁用文本折行
            self.h2t.ignore_emphasis = False  # 保留强调格式
            logger.debug("已初始化html2text转换器")
        except ImportError:
            logger.warning("未找到html2text库，将使用基本转换")
            self.h2t = None
    
    def _crawl(self) -> List[str]:
        """爬取Azure技术博客"""
        saved_files = []
        
        try:
            # 获取博客列表页
            logger.info(f"获取Azure技术博客列表页: {self.start_url}")
            
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
                try:
                    logger.info("requests获取失败，尝试使用Selenium")
                    # 初始化WebDriver（如果未初始化）
                    if not self.driver:
                        self._init_driver()
                    
                    html = self._get_selenium(self.start_url)
                except Exception as e:
                    logger.warning(f"使用Selenium获取页面失败: {e}，将尝试使用备用URL")
                    # 尝试备用URL
                    try:
                        backup_url = "https://techcommunity.microsoft.com/t5/azure-networking-blog/bg-p/AzureNetworkingBlog"
                        if backup_url != self.start_url:
                            logger.info(f"尝试使用备用URL: {backup_url}")
                            response = requests.get(backup_url, headers=headers, timeout=30)
                            if response.status_code == 200:
                                html = response.text
                                logger.info("使用备用URL成功获取到页面内容")
                    except Exception as backup_e:
                        logger.error(f"使用备用URL获取页面失败: {backup_e}")
            
            if not html:
                logger.error(f"获取博客列表页失败: {self.start_url}")
                return []
            
            # 获取所有文章链接
            all_article_info = []
            
            # 解析第一页博客列表
            article_info = self._parse_article_links(html)
            logger.info(f"首页解析到 {len(article_info)} 篇文章链接")
            all_article_info.extend(article_info)
            
            # 禁用分页功能，只处理首页文章
            logger.info("根据要求，仅抓取首页显示的文章，跳过分页操作")
            
            # 如果是测试模式或有文章数量限制，截取所需数量的文章链接
            test_mode = self.source_config.get('test_mode', False)
            # 将默认的文章数量限制从50改为10
            article_limit = self.crawler_config.get('article_limit', 10)
            
            if test_mode:
                logger.info("爬取模式：限制爬取1篇文章")
                all_article_info = all_article_info[:1]
            elif article_limit > 0:
                logger.info(f"爬取模式：限制爬取{article_limit}篇文章")
                all_article_info = all_article_info[:article_limit]
            
            logger.info(f"共有 {len(all_article_info)} 篇文章等待检查")
            
            # 修改：先过滤已爬取的文章链接，避免不必要的网络请求
            filtered_article_info = []
            already_crawled_count = 0
            
            with BaseCrawler.metadata_lock:  # 使用锁确保线程安全
                for title, url, list_date in all_article_info:
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
                        filtered_article_info.append((title, url, list_date))
            
            logger.info(f"过滤后: {len(filtered_article_info)} 篇新文章需要爬取，{already_crawled_count} 篇文章已存在")
            
            # 爬取每篇新文章
            for idx, (title, url, list_date) in enumerate(filtered_article_info, 1):
                logger.info(f"正在爬取第 {idx}/{len(filtered_article_info)} 篇文章: {title}")
                
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
                    if not article_html and self.driver:
                        try:
                            article_html = self._get_selenium(url)
                        except Exception as e:
                            logger.warning(f"使用Selenium获取文章失败: {e}")
                    
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
            logger.error(f"爬取Azure技术博客过程中发生错误: {e}")
            return saved_files
        finally:
            # 关闭WebDriver
            self._close_driver()
            
    def _get_selenium(self, url: str) -> str:
        """
        使用Selenium获取页面内容
        
        Args:
            url: 页面URL
            
        Returns:
            页面HTML内容
        """
        try:
            logger.info(f"使用Selenium获取页面: {url}")
            self.driver.get(url)
            
            # 减少等待时间，避免长时间卡住
            wait_time = 10
            logger.info(f"等待页面加载，超时时间: {wait_time}秒")
            
            try:
                # 等待页面主体内容加载完成
                WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((By.TAG_NAME, "main"))
                )
                logger.info("找到main元素，页面基本结构已加载")
            except Exception as e:
                logger.warning(f"等待main元素超时: {e}")
                try:
                    # 如果找不到main标签，尝试等待article标签
                    WebDriverWait(self.driver, wait_time).until(
                        EC.presence_of_element_located((By.TAG_NAME, "article"))
                    )
                    logger.info("找到article元素，页面基本结构已加载")
                except Exception as e:
                    logger.warning(f"等待article元素超时: {e}")
                    # 如果找不到article标签，尝试等待body加载完成
                    WebDriverWait(self.driver, wait_time).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    logger.info("找到body元素，继续等待内容加载")
            
            # 简化滚动操作，减少等待时间
            logger.info("执行简化的滚动操作")
            
            # 初始等待
            time.sleep(2)
            
            # 执行滚动操作，触发懒加载内容
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(1)
            
            # 滚动到底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # 滚动回顶部
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # 不再尝试点击"显示更多"按钮
            # 根据用户要求，只获取首页文章，无需加载更多
            
            # 获取最终页面内容
            html = self.driver.page_source
            logger.info(f"成功获取页面内容，大小: {len(html)} 字节")
            return html
            
        except Exception as e:
            logger.error(f"Selenium获取页面内容失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise e
    
    def _parse_article_links(self, html: str) -> List[Tuple[str, str, Optional[str]]]:
        """
        解析HTML，提取文章链接
        
        Args:
            html: 页面HTML内容
            
        Returns:
            提取的文章链接列表，每个元素为 (标题, URL, 日期) 三元组
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            processed_articles = []
        
            # 调试信息
            debug_info = {
                "candidates": [],
                "accepted": [],
                "rejected": [],
                "final_count": 0
            }
            
            logger.info("开始基于DOM结构解析Azure博客文章...")
            
            # 1. 首先尝试通过MessageViewCard类来识别文章卡片 - TechCommunity站点特有的类
            article_cards = soup.select('.MessageViewCard_lia-message__6_xUN, article.styles_lia-g-card__y_snR')
            
            if article_cards:
                logger.info(f"找到 {len(article_cards)} 篇文章卡片(通过MessageViewCard类)")
                debug_info["candidates"].append({
                    "selector": ".MessageViewCard_lia-message__6_xUN, article.styles_lia-g-card__y_snR",
                    "count": len(article_cards),
                    "elements": [{"tag": card.name, "class": str(card.get("class", []))} for card in article_cards[:5]] + (["..."] if len(article_cards) > 5 else [])
                })
            else:
                # 2. 如果没有找到特定类的文章卡片，尝试通过点赞/反馈按钮来识别文章
                logger.info("未找到MessageViewCard类文章卡片，尝试通过点赞/反馈按钮识别文章...")
                
                # 查找所有含有点赞图标或反馈按钮的容器
                like_containers = soup.select('[aria-label*="like"], [aria-label*="赞"], [data-testid*="like"], .KudoButton, .like-button')
                
                # 从点赞按钮向上查找包含文章的父容器
                article_cards = []
                for like_button in like_containers:
                    # 向上查找3层，寻找可能的文章容器
                    parent = like_button.parent
                    for _ in range(3):  # 最多向上查找3层
                        if not parent:
                            break
                            
                        # 检查是否是文章容器
                        if parent.name == 'article' or (parent.get('class') and any(c.lower() in ['card', 'article', 'post', 'message'] for c in parent.get('class'))):
                            if parent not in article_cards:  # 避免重复
                                article_cards.append(parent)
                                break
                                
                        parent = parent.parent
                
                if article_cards:
                    logger.info(f"找到 {len(article_cards)} 篇文章(通过点赞按钮)")
                    debug_info["candidates"].append({
                        "selector": "通过点赞按钮识别",
                        "count": len(article_cards),
                        "elements": [{"tag": card.name, "class": str(card.get("class", []))} for card in article_cards[:5]] + (["..."] if len(article_cards) > 5 else [])
                    })
                else:
                    # 3. 如果通过点赞按钮也找不到，尝试基于文章卡片的通用特征
                    logger.info("未通过点赞按钮找到文章，尝试基于通用文章卡片特征...")
                    
                    # 查找结构化的卡片元素
                    card_candidates = soup.select('article, .card, .article-card, .post-card, .blog-card, .message-card, .entry')
                    
                    # 过滤出真正的文章卡片
                    for card in card_candidates:
                        # 检查是否包含标题和链接
                        has_title = bool(card.select_one('h1, h2, h3, h4, h5, .title, .subject'))
                        has_link = bool(card.select_one('a[href]'))
                        
                        # 检查是否包含其他文章特征元素
                        has_date = bool(card.select_one('time, .date, .meta-date, .timestamp'))
                        has_content = bool(card.select_one('p, .content, .description, .excerpt'))
                        
                        # 如果具备文章特征，添加到文章列表
                        if has_title and has_link and (has_date or has_content):
                            article_cards.append(card)
                    
                    if article_cards:
                        logger.info(f"找到 {len(article_cards)} 篇文章(通过通用文章卡片特征)")
                        debug_info["candidates"].append({
                            "selector": "通过通用文章卡片特征",
                            "count": len(article_cards),
                            "elements": [{"tag": card.name, "class": str(card.get("class", []))} for card in article_cards[:5]] + (["..."] if len(article_cards) > 5 else [])
                        })
            
            # 如果未找到任何文章卡片，尝试解析整个页面
            if not article_cards:
                logger.warning("未找到任何文章卡片，尝试提取页面中的所有链接")
                
                # 提取页面中的所有链接
                all_links = soup.find_all('a', href=True)
                
                # 筛选出可能是文章的链接
                for link in all_links:
                    href = link.get('href', '')
                    # 构建完整URL
                    url = href if href.startswith('http') else urljoin(self.start_url, href)
                    
                    # 只接受Azure网络博客链接
                    if '/blog/azurenetworkingblog/' in url:
                        title = link.get_text(strip=True)
                        title = self._clean_title(title)  # 清理标题，移除"MIN READ"等无关信息
                        if not title:
                            # 尝试从title属性或父元素获取标题
                            title = link.get('title', '') or link.get('aria-label', '')
                            if not title and link.parent:
                                title_elem = link.parent.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                                if title_elem:
                                    title = title_elem.get_text(strip=True)
                                    title = self._clean_title(title)  # 清理标题，移除"MIN READ"等无关信息
                        
                        if title and len(title) > 10 and ' ' in title:
                            # 避免URL重复
                            if url not in [a[1] for a in processed_articles]:
                                processed_articles.append((title, url, None))
                                debug_info["accepted"].append({
                                    "title": title,
                                    "url": url
                                })
                
                logger.info(f"从所有链接中提取到 {len(processed_articles)} 篇文章")
                debug_info["final_count"] = len(processed_articles)

                return processed_articles
                
            # 处理找到的文章卡片
            item_details = []
            for i, card in enumerate(article_cards):
                item_detail = {
                    "index": i,
                    "tag": card.name,
                    "classes": str(card.get("class", [])),
                    "id": card.get("id", "")
                }
                
                # 添加调试信息：保存卡片的HTML结构
                if i < 2:  # 只保存前两个卡片的结构以避免调试信息过大
                    item_detail["html_structure"] = str(card)[:500] + "..." if len(str(card)) > 500 else str(card)
                
                # 提取标题
                title_elem = card.select_one('h1, h2, h3, h4, h5, .title, .subject, [class*="subject"], [class*="title"], .lia-message-subject, .MessageSubject, [data-testid="card-title"]')
                title = None
                
                # 首先检查是否有带aria-label的链接
                message_links = card.select('a[aria-label][data-testid="MessageLink"]')
                if message_links and message_links[0].get('aria-label'):
                    title = message_links[0].get('aria-label')
                    logger.info(f"从aria-label中提取到标题: {title}")
                
                # 如果没有从aria-label获取到标题，再尝试使用标题元素
                if not title and title_elem:
                    title = title_elem.get_text(strip=True)
                
                # 如果还是找不到标题，尝试更通用的方法
                if not title:
                    # 尝试其他链接
                    links = card.select('a')
                    for link in links:
                        # 先检查aria-label
                        aria_label = link.get('aria-label')
                        if aria_label and len(aria_label) > 10:
                            title = aria_label
                            logger.info(f"从链接的aria-label中提取到标题: {title}")
                            break
                        
                        # 再检查链接文本
                        link_text = link.get_text(strip=True)
                        if len(link_text) > 10 and ' ' in link_text:
                            title = link_text
                            logger.info(f"从链接文本中提取到标题: {title}")
                            break
                
                # 清理标题
                if title:
                    title = self._clean_title(title)
                
                if not title or len(title) < 5:  # 非常短的标题可能是按钮或标签
                    reason = f"标题太短或未找到: {title}"
                    item_detail["status"] = "rejected"
                    item_detail["reason"] = reason
                    debug_info["rejected"].append({
                        "index": i,
                        "title": title if title else "",
                        "reason": reason
                    })
                    item_details.append(item_detail)
                    continue
                
                item_detail["title"] = title
                if title_elem:
                    item_detail["title_elem"] = f"{title_elem.name}.{str(title_elem.get('class', []))}"
                
                # 提取链接
                link_elem = None
                
                # 首先尝试从MessageLink中获取链接
                message_links = card.select('a[data-testid="MessageLink"]')
                if message_links and message_links[0].get('href'):
                    link_elem = message_links[0]
                    logger.info(f"从MessageLink中提取到链接: {link_elem.get('href')}")
                
                # 如果没有找到MessageLink，再尝试其他方法
                if not link_elem:
                    if title_elem and title_elem.name == 'a':
                        link_elem = title_elem
                    else:
                        # 首先在标题中查找链接
                        if title_elem:
                            link_elem = title_elem.find('a')
                        
                        # 如果标题中没有链接，在卡片中查找主要链接
                        if not link_elem:
                            card_links = card.find_all('a', href=True)
                            for link in card_links:
                                href = link.get('href', '')
                                if href and '/blog/azurenetworkingblog/' in href:
                                    link_elem = link
                                    break
                            
                            # 如果没有找到符合条件的链接，使用第一个链接
                            if not link_elem and card_links:
                                link_elem = card_links[0]
                
                if not link_elem or not link_elem.get('href'):
                    reason = "找不到有效的链接"
                    item_detail["status"] = "rejected"
                    item_detail["reason"] = reason
                    debug_info["rejected"].append({
                        "index": i,
                        "title": title if title else "",
                        "reason": reason
                    })
                    item_details.append(item_detail)
                    continue
                
                href = link_elem.get('href', '')
                # 构建完整URL
                url = href if href.startswith('http') else urljoin(self.start_url, href)
                
                item_detail["href"] = href
                item_detail["url"] = url
                
                # 对于Azure网络博客，特殊处理
                if '/blog/azurenetworkingblog/' not in url:
                    # 只对非/blog/azurenetworkingblog/链接进行额外验证
                    if self._is_tag_or_category_url(url):
                        reason = f"是标签或分类URL: {url}"
                        item_detail["status"] = "rejected"
                        item_detail["reason"] = reason
                        debug_info["rejected"].append({
                            "index": i,
                            "title": title if title else "",
                            "url": url,
                            "reason": reason
                        })
                        item_details.append(item_detail)
                        continue
                
                # 提取日期信息
                date_elem = card.select_one('time, .date, .meta-date, .timestamp, [data-testid="blog-date"]')
                date_str = None
                
                if date_elem:
                    # 首先尝试从datetime属性获取日期
                    if date_elem.get('datetime'):
                        date_str = date_elem.get('datetime')
                    else:
                        date_str = date_elem.get_text(strip=True)
                    
                    # 解析日期字符串
                    date_str = self._parse_date_string(date_str)
                item_detail["date"] = date_str
                
                # 确保URL不重复
                if url in [a[1] for a in processed_articles]:
                    reason = f"URL重复: {url}"
                    item_detail["status"] = "rejected"
                    item_detail["reason"] = reason
                    debug_info["rejected"].append({
                        "index": i,
                        "title": title if title else "",
                        "url": url,
                        "reason": reason
                    })
                    item_details.append(item_detail)
                    continue
                
                # 文章通过所有验证
                processed_articles.append((title, url, date_str))
                item_detail["status"] = "accepted"
                debug_info["accepted"].append({
                    "index": i,
                    "title": title if title else "",
                    "url": url,
                    "date": date_str
                })
                logger.info(f"添加文章: {title} | {url}")
                item_details.append(item_detail)
            
       
            
            logger.info(f"总共解析到 {len(processed_articles)} 篇文章")
            return processed_articles
            
        except Exception as e:
            logger.error(f"解析文章链接出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return [] 

    def _clean_title(self, title: str) -> str:
        """清理标题，移除无关内容"""
        if not title:
            return ""
            
        # 移除常见无关内容
        title = re.sub(r'\b\d+\s+MIN READ\b', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\b\d+\s+minute read\b', '', title, flags=re.IGNORECASE)
        title = re.sub(r'Posted on.*?by.*', '', title, flags=re.IGNORECASE | re.DOTALL)
        
        # 移除前后空格和多余空格
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
        
    def _is_tag_or_category_url(self, url: str) -> bool:
        """检查URL是否为标签或分类页面"""
        return bool(re.search(r'/(tags?|categor(y|ies)|topics?|archive)/', url))
        

            
    def _parse_date_string(self, date_str: Optional[str]) -> Optional[str]:
        """解析日期字符串，转换为统一格式"""
        if not date_str:
            return None
            
        # 清理日期字符串
        date_str = date_str.strip()
        
        # 尝试从ISO格式解析
        iso_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
        if iso_match:
            return iso_match.group(1).replace('-', '_')
            
        # 尝试解析常见的日期格式
        date_formats = [
            # 月份名称格式
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (\d{1,2})(?:st|nd|rd|th)?,? (\d{4})',
            r'(\d{1,2}) (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,? (\d{4})',
            
            # 数字格式
            r'(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{4})',
            r'(\d{4})[/\.-](\d{1,2})[/\.-](\d{1,2})',
        ]
        
        for pattern in date_formats:
            match = re.search(pattern, date_str)
            if match:
                groups = match.groups()
                if len(groups) == 2:  # 月份名称格式
                    day, year = groups
                    # 提取月份
                    month_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*', date_str)
                    if month_match:
                        month_str = month_match.group(1)
                        month_map = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                                    'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
                        month = month_map.get(month_str, '01')
                        # 格式化日期
                        day = day.zfill(2)
                        return f"{year}_{month}_{day}"
                elif len(groups) == 3:  # 数字格式
                    if len(groups[0]) == 4:  # YYYY-MM-DD
                        year, month, day = groups
                    else:  # MM/DD/YYYY
                        month, day, year = groups
                    # 格式化日期
                    month = month.zfill(2)
                    day = day.zfill(2)
                    return f"{year}_{month}_{day}"
                
        # 如果无法解析，返回当前日期
        logger.warning(f"无法解析日期: {date_str}，使用当前日期")
        today = time.strftime("%Y_%m_%d")
        return today
        
    def _parse_article_content(self, url: str, html: str, list_date: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """解析文章内容和日期"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # 提取发布日期
            pub_date = self._extract_publish_date(soup)
            
            # 如果未从文章中获取到日期，使用列表页提供的日期
            if not pub_date:
                pub_date = list_date
            
            # 如果仍然没有日期，则使用当前日期
            if not pub_date:
                pub_date = time.strftime("%Y_%m_%d")
            
            # 提取文章内容
            article_content = "无法提取文章内容"
            
            # 尝试找到文章内容
            content_elem = soup.select_one('main article, #main-content, .lia-message-body-content, .lia-message-body, .message-body, .content-body, .post-body')
            
            if content_elem:
                # 清理非内容元素，但保留正文中的图片
                for elem in content_elem.select('header, footer, nav, .navigation, .sidebar, aside, .ad, .ads, .comments, .social-share, .share-buttons, .author-info, .author-avatar, .avatar, .kudo-button, .like-button, .reaction-button, button, form, input, [class*="tag"], [class*="label"], [href*="/tag/"], [href*="/category/"], [href*="/users/"], [class*="meta"], [class*="info"], [class*="profile"], [class*="join"], [class*="follow"], [class*="subscribe"]'):
                    # 检查元素是否包含图片，如果包含则保留
                    if not elem.find_all('img'):
                        elem.decompose()
                
                # 移除脚本和样式
                for elem in content_elem.find_all(['script', 'style', 'noscript']):
                    elem.decompose()
                
                # 移除非必要的图标和头像图片，但保留正文图片
                for img in content_elem.find_all('img'):
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    # 移除头像、图标、徽标等非必要图片
                    if any(keyword in src.lower() for keyword in ['avatar', 'icon', 'logo', 'profile']) or \
                       any(keyword in alt.lower() for keyword in ['avatar', 'icon', 'rank', 'microsoft']):
                        img.decompose()
                
                # 移除包含作者头像的链接
                for link in content_elem.find_all('a'):
                    href = link.get('href', '')
                    if '/users/' in href or 'avatar' in str(link).lower():
                        link.decompose()
                
                # 移除"Blog Post"文本
                for elem in content_elem.find_all(string=lambda text: text and "Blog Post" in text):
                    parent = elem.parent
                    if parent:
                        if parent.name in ['h2', 'h3', 'p', 'div', 'span']:
                            parent.decompose()
                        else:
                            # 如果父元素不是我们想要移除的，只移除文本本身
                            elem.replace_with('')
                
                # 移除空元素，但保留包含图片的元素
                for elem in content_elem.find_all(['div', 'span', 'p']):
                    if not elem.get_text(strip=True) and not elem.find_all('img'):
                        elem.decompose()
                
                # 将HTML转换为Markdown
                if self.h2t:
                    article_content = self.h2t.handle(str(content_elem))
                    # 进一步清理Markdown内容中的非必要文本
                    article_content = re.sub(r'(?i)\d+\s*(MIN|minute)\s*READ', '', article_content)
                    article_content = re.sub(r'(?i)(Posted|Published|Updated)\s+on\s+.*?(by\s+.*?)?(\n|$)', '', article_content)
                    article_content = re.sub(r'(?i)(Joined|Follow|Subscribe|View\s+Profile).*?(\n|$)', '', article_content)
                    article_content = re.sub(r'(?i)(Share\s+to|Comment).*?(\n|$)', '', article_content)
                    article_content = re.sub(r'\n{3,}', '\n\n', article_content)
                    # 清理未完成的图片链接或格式错误，但保留有效的图片链接
                    article_content = re.sub(r'\[ !\[(?:[^\]]*)\](?!\(\S*\))', '', article_content)
                    article_content = re.sub(r'\[ !\](?!\(\S*\))', '', article_content)
                    article_content = re.sub(r'(?:\*|\s)*\[ !\[(?:[^\]]*)\](?!\(\S*\))(?:(?:\*|\s)*|$)', '', article_content)
                    article_content = re.sub(r'(?:\*|\s)*\[ !\](?!\(\S*\))(?:(?:\*|\s)*|$)', '', article_content)
                    # 截断 Version 字段之后的内容
                    version_match = re.search(r'(Version\s+\d+\.\d+)', article_content, re.IGNORECASE)
                    if version_match:
                        version_index = article_content.find(version_match.group(0)) + len(version_match.group(0))
                        article_content = article_content[:version_index]
                else:
                    # 简单的HTML到文本转换
                    article_content = content_elem.get_text("\n\n", strip=True)
            else:
                logger.warning(f"无法找到文章内容元素: {url}")
            
            return article_content, pub_date
        except Exception as e:
            logger.error(f"解析文章内容失败: {url} - {e}")
            return f"解析内容出错: {str(e)}", None
            
    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """从文章页面提取发布日期"""
        # 尝试各种可能的日期选择器
        date_selectors = [
            'time', 
            '[data-testid="blog-date"]',
            '.date', 
            '.meta-date', 
            '.timestamp',
            '.published-date',
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            '.lia-message-posted-on'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_str = None
                if date_elem.name == 'meta':
                    date_str = date_elem.get('content')
                elif date_elem.get('datetime'):
                    date_str = date_elem.get('datetime')
                else:
                    date_str = date_elem.get_text(strip=True)
                
                if date_str:
                    return self._parse_date_string(date_str)
        
        # 如果未找到日期元素，尝试在文本中查找日期
        text = soup.get_text()
        date_patterns = [
            r'Posted on\s+(.+?\d{4})',
            r'Published\s+(.+?\d{4})',
            r'Date:\s+(.+?\d{4})',
            r'Updated\s+(.+?\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return self._parse_date_string(match.group(1))
        
        return None
    
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
    
    def _create_filename(self, url: str, pub_date: str, ext: str) -> str:
        """创建文件名"""
        # 生成URL的哈希值
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # 组合日期和哈希值
        filename = f"{pub_date}_{url_hash}{ext}"
        
        return filename
