#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re
import sys
import time
import json
import hashlib
import datetime
import concurrent.futures
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

from src.crawlers.common.base_crawler import BaseCrawler
from src.utils.thread_pool import get_thread_pool

logger = logging.getLogger(__name__)

# 直接从JS全局变量提取数据的脚本
EXTRACT_ROUTER_DATA_SCRIPT = '''
() => {
    try {
        if (window._ROUTER_DATA) return window._ROUTER_DATA;
        if (window.__INITIAL_STATE__) return window.__INITIAL_STATE__;
        return null;
    } catch (e) {
        return null;
    }
}
'''


class VolcengineWhatsnewCrawler(BaseCrawler):
    """火山引擎网络产品What's New更新爬虫实现"""
    
    def __init__(self, config: Dict[str, Any], vendor: str, source_type: str):
        """初始化火山引擎What's New更新爬虫"""
        super().__init__(config, vendor, source_type)
        # 获取whatsnew下的所有子源配置
        self.source_config = config.get('sources', {}).get(vendor, {}).get(source_type, {})
        
        # 提取所有网络服务的子源
        self.sub_sources = {}
        for key, value in self.source_config.items():
            if isinstance(value, dict) and 'url' in value:
                self.sub_sources[key] = value
        
        logger.info(f"发现 {len(self.sub_sources)} 个火山引擎网络服务子源: {list(self.sub_sources.keys())}")
    
    def _crawl(self) -> List[str]:
        """
        爬取火山引擎网络产品文档更新
        使用Playwright串行爬取（sync_api不支持多线程共享）
        按月份汇总所有产品更新
        
        Returns:
            保存的文件路径列表
        """
        if not self.sub_sources:
            logger.error("未找到火山引擎网络服务子源配置")
            return []
        
        saved_files = []
        self._new_count = 0
        self._existing_count = 0
        
        try:
            force_mode = self.crawler_config.get('force', False)
            updates_by_month = {}
            
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage'],
                    proxy=getattr(self, 'playwright_proxy', None)
                )
                
                try:
                    total_sources = len(self.sub_sources)
                    for idx, (source_name, source_config) in enumerate(sorted(self.sub_sources.items())):
                        logger.info(f"正在处理: {source_name} ({idx + 1}/{total_sources})")
                        
                        try:
                            source_updates = self._crawl_with_browser(browser, source_name, source_config, force_mode)
                            
                            for update in source_updates:
                                product_name = self._extract_product_name(source_name)
                                month_key = update.get('publish_date', '')[:7]
                                
                                if month_key not in updates_by_month:
                                    updates_by_month[month_key] = {}
                                if product_name not in updates_by_month[month_key]:
                                    updates_by_month[month_key][product_name] = []
                                updates_by_month[month_key][product_name].append(update)
                            
                            logger.info(f"完成源 {source_name}: 收集到 {len(source_updates)} 条更新")
                        except Exception as e:
                            logger.error(f"爬取源 {source_name} 失败: {e}")
                finally:
                    browser.close()
            
            total_updates = sum(
                sum(len(product_updates) for product_updates in month_data.values()) 
                for month_data in updates_by_month.values()
            )
            logger.info(f"总共收集到 {total_updates} 条火山引擎网络更新，分为 {len(updates_by_month)} 个月份")
            
            # 为每个月份创建汇总文档
            for month_key, month_data in sorted(updates_by_month.items()):
                try:
                    file_path = self._save_monthly_updates(month_key, month_data)
                    if file_path:
                        saved_files.append(file_path)
                        logger.info(f"保存月度汇总: {month_key}")
                except Exception as e:
                    logger.error(f"保存月度更新汇总失败: {month_key} - {e}")
            
            logger.info(f"成功保存 {len(saved_files)} 个火山引擎月度更新汇总文件")
            return saved_files
            
        except Exception as e:
            logger.error(f"爬取火山引擎网络更新过程中发生错误: {e}")
            return saved_files
    
    def _crawl_with_browser(self, browser, source_name: str, source_config: Dict[str, Any], force_mode: bool) -> List[Dict[str, Any]]:
        """
        使用已有浏览器实例爬取单个源
        优化策略：屏蔽不必要资源，等待表格渲染后用HTML解析
        """
        url = source_config.get('url')
        if not url:
            return []
        
        try:
            # 创建context并设置资源拦截以加速
            context = browser.new_context()
            
            # 屏蔽不必要的资源：图片、CSS、字体、监控脚本
            context.route("**/*.{png,jpg,jpeg,gif,webp,woff,woff2,ico,svg}", lambda route: route.abort())
            context.route("**/*slardar*", lambda route: route.abort())  # 屏蔽slardar监控
            context.route("**/*sentry*", lambda route: route.abort())   # 屏蔽sentry监控
            context.route("**/*collect*", lambda route: route.abort())  # 屏蔽数据收集
            context.route("**/*analytics*", lambda route: route.abort()) # 屏蔽分析脚本
            
            page = context.new_page()
            updates = []
            
            try:
                page.set_default_timeout(15000)
                
                # 加载页面
                try:
                    page.goto(url, wait_until='domcontentloaded', timeout=15000)
                except Exception as e:
                    logger.warning(f"页面加载超时，尝试继续: {source_name} - {e}")
                
                # 智能等待表格渲染（最多1秒）
                for _ in range(5):  # 最多等待1秒
                    page.wait_for_timeout(200)
                    # 检查页面是否包含表格结构
                    html_check = page.content()
                    if '.ace-line' in html_check or '.ace-table' in html_check or '<table' in html_check:
                        break
                
                # 使用HTML解析（表格结构更可靠）
                html = page.content()
                updates = self._parse_whatsnew_page(html, source_name, url)
            finally:
                context.close()
            
            if not force_mode:
                updates = self._filter_existing_updates(updates, source_name)
            
            return updates
            
        except Exception as e:
            logger.error(f"爬取源 {source_name} 失败: {e}")
            return []
    
    def _crawl_with_playwright_context(self, browser, source_name: str, source_config: Dict[str, Any], force_mode: bool) -> List[Dict[str, Any]]:
        """
        使用Playwright context爬取单个源（用于并发）
        
        Args:
            browser: Playwright浏览器实例
            source_name: 服务名称
            source_config: 服务配置
            force_mode: 是否强制模式
            
        Returns:
            更新条目列表
        """
        url = source_config.get('url')
        if not url:
            logger.warning(f"源 {source_name} 没有配置URL")
            return []
        
        logger.debug(f"正在爬取 {source_name}: {url}")
        
        try:
            # 优先尝试requests
            html = self._get_page_content_requests(url)
            
            if not (html and ('.ace-line' in html or 'ace-table' in html)):
                # 使用Playwright context
                context = browser.new_context()
                try:
                    page = context.new_page()
                    page.set_default_timeout(30000)
                    # 使用domcontentloaded更快，然后等待关键元素
                    page.goto(url, wait_until='domcontentloaded')
                    
                    try:
                        page.wait_for_selector('.ace-line, .volc-doceditor-container, article', timeout=10000)
                    except:
                        pass
                    
                    page.wait_for_timeout(500)
                    html = page.content()
                finally:
                    context.close()
            
            if not html:
                logger.error(f"获取页面内容失败: {source_name}")
                return []
            
            updates = self._parse_whatsnew_page(html, source_name, url)
            
            if not force_mode:
                updates = self._filter_existing_updates(updates, source_name)
            
            return updates
            
        except Exception as e:
            logger.error(f"爬取源 {source_name} 失败: {e}")
            return []
    
    def _crawl_single_source(self, source_name: str, source_config: Dict[str, Any], force_mode: bool) -> List[Dict[str, Any]]:
        """
        爬取单个火山引擎网络服务的更新
        优先尝试requests，失败后回退到Selenium
        
        Args:
            source_name: 服务名称
            source_config: 服务配置
            force_mode: 是否强制模式
            
        Returns:
            更新条目列表
        """
        url = source_config.get('url')
        if not url:
            logger.warning(f"源 {source_name} 没有配置URL")
            return []
        
        logger.info(f"正在爬取 {source_name}: {url}")
        
        try:
            # 优先尝试使用requests获取
            html = self._get_page_content_requests(url)
            
            # 检查是否有有效内容
            if html and ('.ace-line' in html or 'ace-table' in html):
                logger.debug(f"使用requests成功获取 {source_name}")
            else:
                # 回退到Selenium
                logger.debug(f"requests未获取到有效内容，尝试Selenium: {source_name}")
                html = self._get_page_content_selenium(url)
            
            if not html:
                logger.error(f"获取页面内容失败: {source_name} - {url}")
                return []
            
            updates = self._parse_whatsnew_page(html, source_name, url)
            
            if not force_mode:
                updates = self._filter_existing_updates(updates, source_name)
            
            logger.info(f"源 {source_name} 解析到 {len(updates)} 条新更新")
            return updates
            
        except Exception as e:
            logger.error(f"爬取源 {source_name} 时发生错误: {e}")
            return []
    
    def _get_page_content_requests(self, url: str) -> Optional[str]:
        """
        尝试使用requests获取火山引擎页面
        火山引擎部分页面可能支持服务端渲染
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
            
            response = requests.get(url, headers=headers, timeout=30, proxies=getattr(self, 'proxies', None))
            response.raise_for_status()
            
            logger.info(f"获取页面成功: {url}")
            return response.text
            
        except Exception as e:
            logger.debug(f"requests获取页面失败: {url} - {e}")
            return None
    
    def _get_page_content_selenium(self, url: str) -> Optional[str]:
        """
        使用Playwright获取火山引擎SPA页面内容
        Playwright比Selenium更稳定，特别是对于SPA页面
        """
        try:
            logger.debug(f"使用Playwright获取火山引擎页面: {url}")
            
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                # 使用Chromium无头模式
                browser = p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage'],
                    proxy=getattr(self, 'playwright_proxy', None)
                )
                
                try:
                    page = browser.new_page()
                    page.set_default_timeout(30000)  # 30秒超时
                    
                    # 访问页面，使用domcontentloaded更快
                    page.goto(url, wait_until='domcontentloaded')
                    
                    # 等待内容加载
                    try:
                        page.wait_for_selector('.ace-line, .volc-doceditor-container, article', timeout=10000)
                    except:
                        logger.warning(f"等待选择器超时，继续获取内容: {url}")
                    
                    # 等待动态内容渲染
                    page.wait_for_timeout(500)
                    
                    html = page.content()
                    logger.debug(f"成功获取火山引擎页面: {url}")
                    return html
                    
                finally:
                    browser.close()
            
        except Exception as e:
            logger.error(f"Playwright获取火山引擎页面失败: {url} - {e}")
            return None
    
    def _parse_whatsnew_page(self, html: str, source_name: str, url: str) -> List[Dict[str, Any]]:
        """
        解析火山引擎What's New页面，提取更新条目
        火山引擎使用volc-doceditor容器，内容包含表格
        
        Args:
            html: 页面HTML
            source_name: 服务名称  
            url: 页面URL
            
        Returns:
            更新条目列表
        """
        soup = BeautifulSoup(html, 'lxml')
        updates = []
        
        try:
            # 火山引擎使用 .ace-line 容器，时间标题和表格都在其中
            # 按顺序遍历 ace-line，记录时间标题，将后续表格与之关联
            ace_lines = soup.select('.ace-line')
            
            if not ace_lines:
                # 回退到通用选择器
                ace_lines = soup.select('.volc-doceditor-container *')
            
            current_time = None
            current_month = datetime.date.today().strftime('%Y-%m')
            tables_with_time = []  # [(table, time), ...]
            
            for line in ace_lines:
                # 获取文本，去除零宽字符
                text = line.get_text(strip=True).replace('\u200b', '').replace('\ufeff', '')
                
                # 匹配时间标题：2025年11月 或 2025年10月14日
                time_match = re.match(r'^(20[1-2][0-9])年([0-1]?[0-9])月(?:[0-3]?[0-9]日)?$', text)
                if time_match:
                    year = time_match.group(1)
                    month = time_match.group(2).zfill(2)
                    current_time = f"{year}-{month}"
                    logger.debug(f"找到时间标题: {current_time}")
                    continue
                
                # 查找该行中的表格，直接保存表格对象和时间
                table = line.select_one('table')
                if table:
                    tables_with_time.append((table, current_time or current_month))
            
            # 先转换火山引擎特殊链接格式
            self._convert_volcengine_links(soup)
            
            if not tables_with_time:
                logger.warning(f"在 {source_name} 中未找到表格结构")
                return []
            
            logger.debug(f"在 {source_name} 中找到 {len(tables_with_time)} 个表格")
            
            # 解析每个表格
            for table, table_time in tables_with_time:
                table_updates = self._parse_volcengine_table(table, source_name, url, table_time)
                updates.extend(table_updates)
                if table_updates:
                    logger.debug(f"表格解析到 {len(table_updates)} 条更新，时间: {table_time}")
            
            logger.info(f"从 {source_name} 解析到 {len(updates)} 条更新")
            return updates
            
        except Exception as e:
            logger.error(f"解析 {source_name} 页面时发生错误: {e}")
            return []
    
    def _extract_doc_id(self, url: str) -> Optional[str]:
        """
        从URL中提取文档ID
        例如: https://www.volcengine.com/docs/6401/67803 -> "67803"
        """
        try:
            match = re.search(r'/docs/\d+/(\d+)', url)
            if match:
                return match.group(1)
            # 备用方法：取URL最后一个数字段
            parts = url.rstrip('/').split('/')
            for part in reversed(parts):
                if part.isdigit():
                    return part
        except Exception as e:
            logger.debug(f"提取文档ID失败: {url} - {e}")
        return None
    
    def _parse_router_data(self, data: Dict[str, Any], source_name: str, url: str, doc_id: Optional[str]) -> List[Dict[str, Any]]:
        """
        \u89e3\u6790\u4ece_ROUTER_DATA\u83b7\u53d6\u7684JSON\u6570\u636e
        \u706b\u5c71\u5f15\u64ce\u7684Content\u662fQuill Delta\u683c\u5f0f\uff0c\u76f4\u63a5\u89e3\u6790ops\u6570\u636e
        """
        updates = []
            
        try:
            # \u627e\u5230Content\u5b57\u6bb5
            content_str = self._find_content_in_router_data(data, doc_id)
                
            if not content_str:
                logger.debug(f"\u5728_ROUTER_DATA\u4e2d\u672a\u627e\u5230\u5185\u5bb9: {source_name}")
                return []
                
            # Content\u662fJSON\u5b57\u7b26\u4e32\uff0c\u89e3\u6790\u5b83
            try:
                content_data = json.loads(content_str)
            except:
                # \u5982\u679c\u4e0d\u662fJSON\uff0c\u53ef\u80fd\u662fHTML\uff0c\u56de\u9000\u5230HTML\u89e3\u6790
                logger.debug(f"Content\u4e0d\u662fJSON\u683c\u5f0f\uff0c\u5c1d\u8bd5HTML\u89e3\u6790: {source_name}")
                return self._parse_whatsnew_page(content_str, source_name, url)
                
            # \u4eceDelta\u683c\u5f0f\u63d0\u53d6\u66f4\u65b0
            updates = self._parse_delta_content(content_data, source_name, url)
            logger.debug(f"\u4eceDelta\u6570\u636e\u89e3\u6790\u5230 {len(updates)} \u6761\u66f4\u65b0: {source_name}")
                
        except Exception as e:
            logger.error(f"\u89e3\u6790_ROUTER_DATA\u65f6\u51fa\u9519: {source_name} - {e}")
            
        return updates
        
    def _parse_delta_content(self, content_data: Dict[str, Any], source_name: str, url: str) -> List[Dict[str, Any]]:
        """
        \u89e3\u6790Quill Delta\u683c\u5f0f\u7684\u5185\u5bb9
        \u706b\u5c71\u5f15\u64ce\u7684\u8868\u683c\u6570\u636e\u5b58\u50a8\u5728xr\u524d\u7f00\u7684section\u4e2d
        """
        updates = []
        current_month = datetime.date.today().strftime('%Y-%m')
            
        try:
            data_section = content_data.get('data', {})
                
            # \u4ece\u4e3b\u5185\u5bb9(section 0)\u4e2d\u63d0\u53d6\u65f6\u95f4\u6807\u9898
            time_marks = self._extract_time_marks_from_delta(data_section)
            current_time = time_marks[0] if time_marks else current_month
                
            # \u6536\u96c6\u6240\u6709xr section\u7684\u5185\u5bb9 (\u8868\u683c\u5355\u5143\u683c)
            cell_contents = {}
            for sid, section in data_section.items():
                if not sid.startswith('xr') or not isinstance(section, dict):
                    continue
                ops = section.get('ops', [])
                texts = []
                for op in ops:
                    if isinstance(op, dict):
                        insert = op.get('insert', '')
                        if isinstance(insert, str):
                            texts.append(insert)
                content = ''.join(texts).strip()
                if content:
                    cell_contents[sid] = content
                
            # \u5c06\u5185\u5bb9\u7ec4\u7ec7\u6210\u66f4\u65b0\u6761\u76ee
            # \u8868\u683c\u901a\u5e38\u662f: \u5e8f\u53f7 | \u529f\u80fd\u540d\u79f0 | \u529f\u80fd\u63cf\u8ff0 | \u9636\u6bb5 | \u6587\u6863
            updates = self._group_cells_into_updates(cell_contents, source_name, url, current_time, time_marks)
                
        except Exception as e:
            logger.error(f"\u89e3\u6790Delta\u5185\u5bb9\u65f6\u51fa\u9519: {source_name} - {e}")
            
        return updates
        
    def _extract_time_marks_from_delta(self, data_section: Dict) -> List[str]:
        """
        \u4ece\u4e3b\u5185\u5bb9section\u63d0\u53d6\u65f6\u95f4\u6807\u9898
        """
        time_marks = []
        time_pattern = re.compile(r'^(20[1-2][0-9])\u5e74([0-1]?[0-9])\u6708')
            
        main_section = data_section.get('0', {})
        if isinstance(main_section, dict):
            ops = main_section.get('ops', [])
            for op in ops:
                if isinstance(op, dict):
                    insert = op.get('insert', '')
                    if isinstance(insert, str):
                        for line in insert.split('\n'):
                            line = line.strip().replace('\u200b', '').replace('\ufeff', '')
                            match = time_pattern.match(line)
                            if match:
                                year, month = match.groups()
                                time_marks.append(f"{year}-{month.zfill(2)}")
            
        return time_marks
        
    def _group_cells_into_updates(self, cell_contents: Dict[str, str], source_name: str, url: str, 
                                  default_time: str, time_marks: List[str]) -> List[Dict[str, Any]]:
        """
        \u5c06\u5355\u5143\u683c\u5185\u5bb9\u7ec4\u7ec7\u6210\u66f4\u65b0\u6761\u76ee
        \u901a\u8fc7\u5206\u6790\u5185\u5bb9\u7279\u5f81\u6765\u8bc6\u522b\u529f\u80fd\u540d\u79f0\u548c\u63cf\u8ff0
        """
        updates = []
        current_time = default_time
        time_idx = 0
            
        # \u5206\u7ec4:\u529f\u80fd\u540d\u79f0\u901a\u5e38\u8f83\u77ed\uff0c\u63cf\u8ff0\u8f83\u957f
        # \u8fc7\u6ee4\u6389\u8868\u5934\u548c\u65e0\u6548\u5185\u5bb9
        skip_keywords = ['\u529f\u80fd\u540d\u79f0', '\u529f\u80fd\u63cf\u8ff0', '\u53d1\u5e03\u9636\u6bb5', '\u76f8\u5173\u6587\u6863', '\u5e8f\u53f7', '\u540d\u79f0', '\u63cf\u8ff0', '\u9636\u6bb5', '\u6587\u6863']
            
        # \u6309section ID\u6392\u5e8f\u4fdd\u6301\u987a\u5e8f
        sorted_cells = sorted(cell_contents.items(), key=lambda x: x[0])
            
        # \u5c1d\u8bd5\u8bc6\u522b\u529f\u80fd\u540d\u79f0\u548c\u63cf\u8ff0\u7684\u914d\u5bf9
        i = 0
        while i < len(sorted_cells):
            sid, content = sorted_cells[i]
                
            # \u8df3\u8fc7\u8868\u5934
            if any(kw in content for kw in skip_keywords) and len(content) < 20:
                i += 1
                continue
                
            # \u8df3\u8fc7\u7eaf\u6570\u5b57(\u5e8f\u53f7)
            if content.isdigit():
                i += 1
                continue
                
            # \u68c0\u67e5\u662f\u5426\u662f\u529f\u80fd\u540d\u79f0(\u8f83\u77ed\uff0c\u4e0d\u5305\u542b\u53e5\u53f7)
            if len(content) > 3 and len(content) < 50 and '\u3002' not in content:
                function_name = content
                function_desc = ''
                stage = ''
                    
                # \u67e5\u627e\u540e\u7eed\u7684\u63cf\u8ff0\u548c\u9636\u6bb5
                if i + 1 < len(sorted_cells):
                    next_content = sorted_cells[i + 1][1]
                    if len(next_content) > 20 or '\u3002' in next_content:
                        function_desc = next_content
                        i += 1
                    
                if i + 1 < len(sorted_cells):
                    next_content = sorted_cells[i + 1][1]
                    if next_content in ['\u90c0\u6d4b', '\u516c\u6d4b', '\u5546\u7528', 'GA', 'Preview', 'Beta', '\u5168\u91cf']:
                        stage = next_content
                        i += 1
                    
                update = {
                    'title': function_name,
                    'description': function_desc,
                    'publish_date': current_time,
                    'service_name': source_name,
                    'source_url': url,
                    'content': function_name + ('\n\n' + function_desc if function_desc else ''),
                    'stage': stage,
                    'doc_links': []
                }
                updates.append(update)
                
            i += 1
            
        return updates
    
    def _find_content_in_router_data(self, obj: Any, target_id: Optional[str] = None) -> Optional[str]:
        """
        在_ROUTER_DATA中递归查找文档内容
        尝试多种数据结构模式
        
        Args:
            obj: 要搜索的对象
            target_id: 目标文档ID
            
        Returns:
            找到的内容字符串，或None
        """
        if obj is None:
            return None
        
        if isinstance(obj, dict):
            # 模式1: 直接查找Content或MDContent字段
            if 'Content' in obj and isinstance(obj['Content'], str) and len(obj['Content']) > 500:
                return obj['Content']
            if 'MDContent' in obj and isinstance(obj['MDContent'], str) and len(obj['MDContent']) > 500:
                return obj['MDContent']
            
            # 模式2: loaderData -> [docId] -> value -> Content
            if 'loaderData' in obj:
                loader_data = obj['loaderData']
                if isinstance(loader_data, dict):
                    for key, value in loader_data.items():
                        # 如果有目标ID，优先查找匹配的
                        if target_id and target_id in key:
                            result = self._find_content_in_router_data(value, target_id)
                            if result:
                                return result
                        # 否则遍历所有
                        result = self._find_content_in_router_data(value, target_id)
                        if result:
                            return result
            
            # 模式3: value -> Content
            if 'value' in obj and isinstance(obj['value'], dict):
                result = self._find_content_in_router_data(obj['value'], target_id)
                if result:
                    return result
            
            # 模式4: 如果有target_id，查找匹配的key
            if target_id and target_id in obj:
                result = self._find_content_in_router_data(obj[target_id], target_id)
                if result:
                    return result
            
            # 遍历所有键值
            for key, value in obj.items():
                result = self._find_content_in_router_data(value, target_id)
                if result:
                    return result
        
        elif isinstance(obj, list):
            for item in obj:
                result = self._find_content_in_router_data(item, target_id)
                if result:
                    return result
        
        return None
    
    def _convert_volcengine_links(self, content) -> None:
        """
        将火山云特殊的链接格式转换为标准的<a href>标签
        火山云使用 class="url hyperlink-href:https://..." 格式存储链接
        """
        if not content:
            return
        
        try:
            # 查找所有包含 hyperlink-href 的元素
            elements = content.find_all(class_=re.compile(r'hyperlink-href:'))
            for elem in elements:
                class_str = ' '.join(elem.get('class', []))
                match = re.search(r'hyperlink-href:(\S+)', class_str)
                if match:
                    href = match.group(1)
                    text = elem.get_text(strip=True)
                    # 创建新的<a>标签 - 使用BeautifulSoup创建确保兼容性
                    new_soup = BeautifulSoup(f'<a href="{href}">{text}</a>', 'html.parser')
                    new_tag = new_soup.a
                    if new_tag:
                        elem.replace_with(new_tag)
        except Exception as e:
            logger.debug(f"转换火山云链接时出错: {e}")
    
    def _parse_volcengine_table(self, table, source_name: str, url: str, time_prefix: str) -> List[Dict[str, Any]]:
        """
        解析火山引擎的标准表格结构
        火山引擎表格通常格式为：序号 | 功能名称 | 功能描述 | 阶段 | 相关文档
        
        Args:
            table: BeautifulSoup表格元素
            source_name: 服务名称
            url: 页面URL  
            time_prefix: 时间前缀 (如 "2025-04")
            
        Returns:
            更新条目列表
        """
        updates = []
        
        try:
            rows = table.find_all('tr')
            if not rows:
                return updates
            
            # 检测表头
            header_row = rows[0]
            headers = [cell.get_text(strip=True) for cell in header_row.find_all(['th', 'td'])]
            
            # 尝试识别列含义
            seq_col = -1
            name_col = -1
            desc_col = -1
            stage_col = -1
            doc_col = -1
            
            for idx, header in enumerate(headers):
                header_lower = header.lower()
                if '序号' in header or header.isdigit():
                    seq_col = idx
                elif '功能名称' in header or '名称' in header:
                    name_col = idx
                elif '功能描述' in header or '描述' in header or '说明' in header:
                    desc_col = idx
                elif '阶段' in header or '状态' in header:
                    stage_col = idx
                elif '文档' in header or '链接' in header:
                    doc_col = idx
            
            # 默认布局：序号|功能名称|功能描述|阶段|相关文档
            if name_col == -1:
                name_col = 1 if len(headers) > 1 else 0
            if desc_col == -1:
                desc_col = 2 if len(headers) > 2 else -1
            if stage_col == -1:
                stage_col = 3 if len(headers) > 3 else -1
            if doc_col == -1:
                doc_col = 4 if len(headers) > 4 else -1
            
            # 处理数据行
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                
                try:
                    # 提取功能名称
                    function_name = cells[name_col].get_text(strip=True) if name_col < len(cells) else ""
                    
                    # 提取功能描述
                    function_desc = cells[desc_col].get_text(strip=True) if desc_col >= 0 and desc_col < len(cells) else ""
                    
                    # 提取阶段
                    stage = cells[stage_col].get_text(strip=True) if stage_col >= 0 and stage_col < len(cells) else ""
                    
                    # 提取文档链接
                    doc_links = []
                    if doc_col >= 0 and doc_col < len(cells):
                        links = cells[doc_col].find_all('a', href=True)
                        for link in links:
                            href = link.get('href', '')
                            link_text = link.get_text(strip=True)
                            if href:
                                if href.startswith('/'):
                                    full_url = urljoin('https://www.volcengine.com', href)
                                elif href.startswith('http'):
                                    full_url = href
                                else:
                                    full_url = urljoin(url, href)
                                doc_links.append({'text': link_text, 'url': full_url})
                    
                    # 过滤无效行
                    if not function_name or len(function_name) < 3:
                        continue
                    
                    # 构建内容
                    content_parts = [function_name]
                    if function_desc:
                        content_parts.append(f"功能描述：{function_desc}")
                    if stage:
                        content_parts.append(f"发布阶段：{stage}")
                    if doc_links:
                        content_parts.append("文档链接：")
                        for doc_link in doc_links:
                            content_parts.append(f"- [{doc_link['text']}]({doc_link['url']})")
                    
                    update = {
                        'title': function_name,
                        'description': function_desc,
                        'publish_date': time_prefix,
                        'service_name': source_name,
                        'source_url': url,
                        'content': '\n\n'.join(content_parts),
                        'stage': stage,
                        'doc_links': doc_links
                    }
                    
                    updates.append(update)
                    logger.debug(f"解析到更新: {function_name[:30]}... ({time_prefix})")
                    
                except Exception as e:
                    logger.debug(f"解析表格行时出错: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"解析火山引擎表格时出错: {e}")
        
        return updates
    
    def _filter_existing_updates(self, updates: List[Dict[str, Any]], source_name: str) -> List[Dict[str, Any]]:
        """过滤已存在的更新条目"""
        filtered_updates = []
        
        with BaseCrawler.metadata_lock:
            for update in updates:
                update_id = self._generate_update_id(update)
                
                if update_id in self.metadata:
                    filepath = self.metadata[update_id].get('filepath', '')
                    if os.path.exists(filepath):
                        logger.debug(f"跳过已存在的更新: {update['title']}")
                        continue
                
                filtered_updates.append(update)
        
        logger.info(f"源 {source_name}: {len(updates)} -> {len(filtered_updates)} (过滤后)")
        return filtered_updates
    
    def _generate_update_id(self, update: Dict[str, Any]) -> str:
        """为更新条目生成唯一ID"""
        content = f"{update.get('title', '')}{update.get('publish_date', '')}{update.get('service_name', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
    
    def _extract_product_name(self, source_name: str) -> str:
        """从源名称提取产品名称"""
        product_mapping = {
            'vpc': 'VPC',
            'eip': 'EIP',
            'shared_bandwidth_package': 'BWP',
            'nat_gateway': 'NAT',
            'ipv6_gateway': 'IPv6',
            'cen': 'CEN',
            'transit_router': 'TR',
            'clb': 'CLB',
            'clb_release': 'CLB',
            'alb': 'ALB',
            'direct_connect': 'DC',
            'vpn_connection': 'VPN',
            'private_link': 'PrivateLink',
            'nic': 'NIC',
            'cloud_connector': 'CC',
            'shared_traffic_package': 'STP'
        }
        return product_mapping.get(source_name.lower(), source_name.upper())
    
    def _save_monthly_updates(self, month_key: str, month_data: Dict[str, List[Dict[str, Any]]]) -> Optional[str]:
        """将产品月度更新保存为Markdown文件"""
        try:
            filename = f"{month_key}.md"
            filepath = os.path.join(self.output_dir, filename)
            
            markdown_content = self._generate_monthly_updates_content(month_key, month_data)
            new_hash = hashlib.md5(markdown_content.encode('utf-8')).hexdigest()
            
            # 检查文件是否已存在且内容相同
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                existing_hash = hashlib.md5(existing_content.encode('utf-8')).hexdigest()
                if existing_hash == new_hash:
                    logger.info(f"月度汇总内容未变化，跳过: {month_key}")
                    self._existing_count += 1
                    return None
                else:
                    self._existing_count += 1
            else:
                self._new_count += 1
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            update_url_key = f"volcengine_monthly_{month_key.replace('-', '_')}"
            with BaseCrawler.metadata_lock:
                self.metadata[update_url_key] = {
                    'title': f"火山引擎网络服务月度更新 - {month_key}",
                    'publish_date': month_key,
                    'service_name': '火山引擎网络服务',
                    'source_url': '',
                    'filepath': filepath,
                    'crawl_time': datetime.datetime.now().isoformat(),
                    'file_hash': new_hash
                }
                self.metadata_manager.update_crawler_metadata(self.vendor, self.source_type, self.metadata)
            
            return filepath
            
        except Exception as e:
            logger.error(f"保存月度更新汇总失败: {e}")
            return None
    
    def _generate_monthly_updates_content(self, month_key: str, month_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """生成月度更新内容的Markdown格式"""
        total_updates = sum(len(updates) for updates in month_data.values())
        
        markdown_lines = [
            f"# 火山引擎网络服务月度更新 - {month_key}",
            "",
            f"**发布时间:** {month_key}-01",
            "",
            f"**厂商:** 火山引擎",
            "",
            f"**产品线:** 网络服务",
            "",
            f"**类型:** 月度更新汇总",
            "",
            f"**产品数量:** {len(month_data)} 个",
            "",
            f"**总更新数量:** {total_updates} 条",
            "",
            "---",
            "",
            "## 产品更新概览",
            "",
            "| 产品 | 更新数量 | 主要更新内容 |",
            "|------|----------|--------------|"
        ]
        
        for product_name, updates in sorted(month_data.items()):
            main_updates = updates[:3]
            main_update_titles = [update.get('title', '')[:30] + ('...' if len(update.get('title', '')) > 30 else '') for update in main_updates]
            main_content = '; '.join(main_update_titles)
            if len(updates) > 3:
                main_content += f" 等{len(updates)}项更新"
            markdown_lines.append(f"| {product_name} | {len(updates)}条 | {main_content} |")
        
        markdown_lines.extend(["", "---", ""])
        
        # 为每个产品生成详细更新内容
        for product_name, updates in sorted(month_data.items()):
            updates.sort(key=lambda x: (x.get('publish_date', ''), x.get('title', '')), reverse=True)
            
            markdown_lines.extend([
                f"## {product_name} 产品更新",
                "",
                f"**更新数量:** {len(updates)} 条",
                "",
                "### 更新列表",
                "",
                "| 序号 | 功能名称 | 发布阶段 | 发布日期 |",
                "|------|----------|----------|----------|"
            ])
            
            for idx, update in enumerate(updates, 1):
                title = update.get('title', '').replace('|', '\\|')[:50]
                stage = update.get('stage', '').replace('|', '\\|')
                date = update.get('publish_date', '')
                markdown_lines.append(f"| {idx} | {title} | {stage} | {date} |")
            
            markdown_lines.extend(["", "### 详细更新内容", ""])
            
            for idx, update in enumerate(updates, 1):
                title = update.get('title', '')
                description = update.get('description', '')
                stage = update.get('stage', '')
                doc_links = update.get('doc_links', [])
                
                markdown_lines.extend([
                    f"#### {idx}. {title}",
                    "",
                    f"**发布日期:** {update.get('publish_date', '')}",
                    ""
                ])
                
                if description:
                    markdown_lines.extend([
                        f"**功能描述:** {description}",
                        ""
                    ])
                
                if stage:
                    markdown_lines.extend([
                        f"**发布阶段:** {stage}",
                        ""
                    ])
                
                if doc_links:
                    markdown_lines.extend(["**相关文档:**", ""])
                    for doc_link in doc_links:
                        markdown_lines.append(f"- [{doc_link['text']}]({doc_link['url']})")
                    markdown_lines.append("")
                
                markdown_lines.extend(["---", ""])
        
        # 添加页脚信息
        markdown_lines.extend([
            "## 数据来源",
            "",
            "本文档内容来源于火山引擎官方产品动态页面，具体更新详情请访问:",
            ""
        ])
        
        source_urls = set()
        for updates in sorted(month_data.values(), key=lambda x: x[0].get('service_name', '') if x else ''):
            for update in updates:
                source_url = update.get('source_url', '')
                if source_url:
                    source_urls.add(source_url)
        
        for source_url in sorted(source_urls):
            markdown_lines.append(f"- {source_url}")
        
        markdown_lines.append("")
        
        return "\n".join(markdown_lines)
