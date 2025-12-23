#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re
import sys
import time
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

class HuaweiWhatsnewCrawler(BaseCrawler):
    """华为云网络产品What's New更新爬虫实现"""
    
    def __init__(self, config: Dict[str, Any], vendor: str, source_type: str):
        """初始化华为云What's New更新爬虫"""
        super().__init__(config, vendor, source_type)
        # 获取whatsnew下的所有子源配置
        self.source_config = config.get('sources', {}).get(vendor, {}).get(source_type, {})
        
        # 提取所有网络服务的子源
        self.sub_sources = {}
        for key, value in self.source_config.items():
            if isinstance(value, dict) and 'url' in value:
                self.sub_sources[key] = value
        
        logger.info(f"发现 {len(self.sub_sources)} 个华为云网络服务子源: {list(self.sub_sources.keys())}")
    
    def _crawl(self) -> List[str]:
        """
        爬取华为云网络产品文档更新
        采用多线程处理多个子源，按月份汇总所有产品更新
        
        Returns:
            保存的文件路径列表
        """
        if not self.sub_sources:
            logger.error("未找到华为云网络服务子源配置")
            return []
        
        saved_files = []
        self._new_count = 0
        self._existing_count = 0
        
        try:
            # 检查是否启用了强制模式
            force_mode = self.crawler_config.get('force', False)
            
            # 收集所有子源的更新条目，按月份分组
            updates_by_month = {}
            
            # 使用线程池处理多个子源，实现慢启动
            thread_pool = get_thread_pool()
            max_workers = min(len(self.sub_sources), thread_pool.current_threads_target // 2)  # 避免占用过多线程
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 慢启动：逐步提交任务而不是一次性提交所有任务
                future_to_source = {}
                
                for idx, (source_name, source_config) in enumerate(self.sub_sources.items()):
                    # 慢启动延迟
                    if idx > 0:
                        time.sleep(0.5)  # 每个源之间间隔0.5秒
                    
                    future = executor.submit(self._crawl_single_source, source_name, source_config, force_mode)
                    future_to_source[future] = source_name
                    logger.info(f"已提交任务: {source_name} ({idx + 1}/{len(self.sub_sources)})")
                
                # 收集结果并按月份分组
                for future in concurrent.futures.as_completed(future_to_source):
                    source_name = future_to_source[future]
                    try:
                        source_updates = future.result(timeout=120)  # 2分钟超时
                        
                        # 按月份分组，在每个月份中按产品分组
                        for update in source_updates:
                            product_name = self._extract_product_name(source_name)
                            month_key = update.get('publish_date', '')[:7]  # YYYY-MM
                            
                            if month_key not in updates_by_month:
                                updates_by_month[month_key] = {}
                            
                            if product_name not in updates_by_month[month_key]:
                                updates_by_month[month_key][product_name] = []
                            
                            updates_by_month[month_key][product_name].append(update)
                        
                        logger.info(f"完成源 {source_name}: 收集到 {len(source_updates)} 条更新")
                    except Exception as e:
                        logger.error(f"爬取源 {source_name} 失败: {e}")
            
            total_updates = sum(
                sum(len(product_updates) for product_updates in month_data.values()) 
                for month_data in updates_by_month.values()
            )
            logger.info(f"总共收集到 {total_updates} 条华为云网络更新，分为 {len(updates_by_month)} 个月份")
            
            # 如果是测试模式，只处理前几个月
            test_mode = self.source_config.get('test_mode', False)
            if test_mode:
                limited_months = dict(list(updates_by_month.items())[:1])  # 测试模式只取1个月
                updates_by_month = limited_months
                logger.info(f"测试模式：限制处理 {len(updates_by_month)} 个月份")
            
            # 为每个月份创建汇总文档
            for month_key, month_data in updates_by_month.items():
                try:
                    file_path = self._save_monthly_updates(month_key, month_data)
                    if file_path:
                        saved_files.append(file_path)
                        logger.info(f"保存月度汇总: {month_key}")
                except Exception as e:
                    logger.error(f"保存月度更新汇总失败: {month_key} - {e}")
            
            logger.info(f"成功保存 {len(saved_files)} 个华为云月度更新汇总文件")
            return saved_files
            
        except Exception as e:
            logger.error(f"爬取华为云网络更新过程中发生错误: {e}")
            return saved_files
        finally:
            # 关闭WebDriver
            self._close_driver()
    
    def _crawl_single_source(self, source_name: str, source_config: Dict[str, Any], force_mode: bool) -> List[Dict[str, Any]]:
        """
        爬取单个华为云网络服务的更新
        
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
            # 获取页面内容
            html = self._get_page_content(url)
            if not html:
                logger.error(f"获取页面内容失败: {source_name} - {url}")
                return []
            
            # 解析更新条目
            updates = self._parse_whatsnew_page(html, source_name, url)
            
            # 过滤已处理的更新（除非是强制模式）
            if not force_mode:
                updates = self._filter_existing_updates(updates, source_name)
            
            logger.info(f"源 {source_name} 解析到 {len(updates)} 条新更新")
            return updates
            
        except Exception as e:
            logger.error(f"爬取源 {source_name} 时发生错误: {e}")
            return []
    
    def _get_page_content(self, url: str) -> Optional[str]:
        """
        获取页面内容，优先使用requests，失败时使用selenium
        
        Args:
            url: 页面URL
            
        Returns:
            页面HTML内容
        """
        # 首先尝试使用requests
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                logger.info(f"获取页面成功: {url}")
                return response.text
            else:
                logger.warning(f"requests返回状态码 {response.status_code}: {url}")
                
        except Exception as e:
            logger.warning(f"requests获取页面失败: {url} - {e}")
        
        # 如果requests失败，尝试使用selenium
        try:
            logger.debug(f"尝试使用selenium获取页面: {url}")
            html = self._get_selenium(url)
            if html:
                logger.debug(f"使用selenium成功获取页面: {url}")
                return html
        except Exception as e:
            logger.error(f"selenium获取页面失败: {url} - {e}")
        
        return None
    
    def _parse_whatsnew_page(self, html: str, source_name: str, url: str) -> List[Dict[str, Any]]:
        """
        解析华为云What's New页面，提取更新条目
        
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
            # 华为云文档页面使用标准的表格结构，按时间分组
            # 查找所有表格
            tables = soup.find_all('table')
            
            if not tables:
                logger.warning(f"在 {source_name} 中未找到表格结构")
                return self._fallback_parse_method(soup, source_name, url)
            
            logger.debug(f"在 {source_name} 中找到 {len(tables)} 个表格")
            
            # 查找时间标题来确定更新的发布时间
            # 华为云使用 h4 标题格式：#### 2025年04月，支持2010-2029年
            time_headers = soup.find_all('h4', string=re.compile(r'20[1-2][0-9]年[0-1]?[0-9]月'))
            time_map = {}
            
            logger.debug(f"在 {source_name} 中找到 {len(time_headers)} 个时间标题")
            
            # 建立时间标题和表格的映射关系
            current_month = datetime.date.today().strftime('%Y-%m')
            
            for header in time_headers:
                # 解析时间格式：2025年04月 -> 2025-04，支持2010-2029年
                time_match = re.search(r'(20[1-2][0-9])年([0-1]?[0-9])月', header.get_text())
                if time_match:
                    year = time_match.group(1)
                    month = time_match.group(2).zfill(2)
                    time_key = f"{year}-{month}"
                    
                    # 查找该时间标题后的第一个表格
                    next_table = None
                    current = header
                    
                    # 向下查找下一个兄弟元素
                    while current:
                        current = current.find_next_sibling()
                        if not current:
                            break
                            
                        # 如果是表格，直接使用
                        if current.name == 'table':
                            next_table = current
                            break
                            
                        # 如果是包含表格的容器，查找其中的表格
                        if hasattr(current, 'find') and current.find('table'):
                            next_table = current.find('table')
                            break
                            
                        # 如果遇到下一个时间标题，停止查找
                        if current.name == 'h4' and re.search(r'20[1-2][0-9]年[0-1]?[0-9]月', current.get_text()):
                            break
                    
                    if next_table:
                        time_map[next_table] = time_key
                        logger.debug(f"找到时间映射: {time_key} -> 表格")
                        
                        # 如果是当前月份，记录找到
                        if time_key == current_month:
                            logger.info(f"找到当前月份 {current_month} 的更新内容")
                    else:
                        logger.debug(f"未找到时间 {time_key} 对应的表格")
            
            # 如果没有找到时间映射，记录警告但不处理任何表格
            # 避免将历史数据错误标记为当前月份
            if not time_map:
                logger.warning(f"在 {source_name} 中未找到当前月份 {current_month} 的时间标题映射")
                logger.info(f"源 {source_name} 在当前月份无新更新，跳过处理")
                return []
            
            # 解析每个表格
            for table in tables:
                table_time = time_map.get(table)
                if table_time:  # 只处理有明确时间映射的表格
                    table_updates = self._parse_huawei_table(table, source_name, url, table_time)
                    updates.extend(table_updates)
                    logger.debug(f"从表格解析到 {len(table_updates)} 条更新 (时间: {table_time})")
                else:
                    logger.debug(f"跳过没有时间映射的表格")
            
            logger.info(f"从 {source_name} 解析到 {len(updates)} 条更新")
            return updates
            
        except Exception as e:
            logger.error(f"解析 {source_name} 页面时发生错误: {e}")
            return []
    
    def _parse_huawei_table(self, table, source_name: str, url: str, time_prefix: str) -> List[Dict[str, Any]]:
        """
        解析华为云的标准表格结构
        
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
            # 查找表格的所有行
            rows = table.find_all('tr')
            if not rows:
                return updates
            
            # 跳过表头行，从第二行开始处理数据
            for row in rows[1:]:  # 跳过表头
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:  # 至少需要序号、功能名称、功能描述
                    continue
                
                try:
                    # 华为云表格结构：序号 | 功能名称 | 功能描述 | 阶段 | 相关文档
                    sequence = cells[0].get_text(strip=True) if len(cells) > 0 else ""
                    function_name = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                    function_desc = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                    stage = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                    related_docs_text = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                    
                    # 提取相关文档的链接
                    doc_links = []
                    if len(cells) > 4:
                        # 查找相关文档单元格中的所有链接
                        doc_cell = cells[4]
                        links = doc_cell.find_all('a', href=True)
                        for link in links:
                            href = link.get('href', '')
                            link_text = link.get_text(strip=True)
                            if href:
                                # 处理相对链接
                                if href.startswith('/'):
                                    full_url = urljoin('https://support.huaweicloud.com', href)
                                elif href.startswith('http'):
                                    full_url = href
                                else:
                                    full_url = urljoin(url, href)
                                
                                doc_links.append({
                                    'text': link_text,
                                    'url': full_url
                                })
                    
                    # 过滤无效行
                    if not function_name or len(function_name) < 3:
                        continue
                    
                    # 构建更新条目
                    # 华为云没有具体的发布日期，只有年月信息
                    # 直接使用time_prefix作为发布日期（格式：2025-05）
                    publish_date = time_prefix
                    
                    # 组合详细内容
                    content_parts = [function_name]
                    if function_desc:
                        content_parts.append(f"功能描述：{function_desc}")
                    if stage:
                        content_parts.append(f"发布阶段：{stage}")
                    if related_docs_text:
                        content_parts.append(f"相关文档：{related_docs_text}")
                    
                    # 添加文档链接
                    if doc_links:
                        content_parts.append("文档链接：")
                        for doc_link in doc_links:
                            content_parts.append(f"- [{doc_link['text']}]({doc_link['url']})")
                    
                    update = {
                        'title': function_name,
                        'description': function_desc,
                        'publish_date': publish_date,
                        'service_name': source_name,
                        'source_url': url,
                        'content': '\n\n'.join(content_parts),
                        'stage': stage,
                        'sequence': sequence,
                        'related_docs': related_docs_text,
                        'doc_links': doc_links
                    }
                    
                    updates.append(update)
                    logger.debug(f"解析到更新: {function_name} ({publish_date}) - {len(doc_links)} 个文档链接")
                    
                except Exception as e:
                    logger.debug(f"解析表格行时出错: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"解析华为云表格时出错: {e}")
        
        return updates
    
    def _fallback_parse_method(self, soup: BeautifulSoup, source_name: str, url: str) -> List[Dict[str, Any]]:
        """
        备用解析方法，当标准表格解析失败时使用
        
        Args:
            soup: BeautifulSoup对象
            source_name: 服务名称
            url: 页面URL
            
        Returns:
            更新条目列表
        """
        updates = []
        
        try:
            # 尝试查找包含日期模式的元素
            date_elements = soup.find_all(string=re.compile(r'202[0-9]-[0-1][0-9]-[0-3][0-9]'))
            if date_elements:
                logger.debug(f"使用备用方法：在 {source_name} 中找到 {len(date_elements)} 个日期元素")
                updates = self._extract_updates_by_date_elements(soup, date_elements, source_name, url)
            else:
                # 尝试查找其他容器
                containers = soup.select('.devui-table, .devui-timeline, .content-list, .update-list, article, .doc-content, .main-content')
                for container in containers:
                    container_updates = self._extract_updates_from_container(container, source_name, url)
                    updates.extend(container_updates)
                    
                if not updates:
                    logger.warning(f"备用方法也未能在 {source_name} 中找到更新内容")
            
        except Exception as e:
            logger.error(f"备用解析方法失败: {e}")
        
        return updates
    
    def _extract_updates_by_date_elements(self, soup: BeautifulSoup, date_elements: List, source_name: str, url: str) -> List[Dict[str, Any]]:
        """
        基于日期元素提取更新条目
        
        Args:
            soup: BeautifulSoup对象
            date_elements: 包含日期的元素列表
            source_name: 服务名称
            url: 页面URL
            
        Returns:
            更新条目列表
        """
        updates = []
        
        for date_str in date_elements[:10]:  # 最多处理10个日期元素
            try:
                # 查找包含这个日期的父元素
                date_parent = date_str.parent
                if not date_parent:
                    continue
                
                # 查找日期前后的内容作为标题和描述
                title = ""
                description = ""
                
                # 向上查找可能的标题元素
                for ancestor in [date_parent] + list(date_parent.parents)[:3]:
                    title_candidates = ancestor.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b'])
                    if title_candidates:
                        title = title_candidates[0].get_text(strip=True)
                        break
                
                # 如果没找到标题，使用日期所在行的文本
                if not title:
                    title = date_parent.get_text(strip=True)
                
                # 查找描述内容
                desc_candidates = date_parent.find_next_siblings(['p', 'div', 'span'])
                if desc_candidates:
                    description = desc_candidates[0].get_text(strip=True)[:500]  # 限制描述长度
                
                # 提取日期
                date_match = re.search(r'(202[0-9]-[0-1][0-9]-[0-3][0-9])', str(date_str))
                publish_date = date_match.group(1) if date_match else ""
                
                if title and publish_date:
                    update = {
                        'title': title,
                        'description': description,
                        'publish_date': publish_date,
                        'service_name': source_name,
                        'source_url': url,
                        'content': f"{title}\n\n{description}" if description else title
                    }
                    updates.append(update)
                    
            except Exception as e:
                logger.debug(f"处理日期元素时出错: {e}")
                continue
        
        return updates
    
    def _extract_updates_from_container(self, container, source_name: str, url: str) -> List[Dict[str, Any]]:
        """
        从容器中提取更新条目
        
        Args:
            container: BeautifulSoup容器元素
            source_name: 服务名称
            url: 页面URL
            
        Returns:
            更新条目列表
        """
        updates = []
        
        try:
            # 查找容器内的更新项目
            items = container.find_all(['tr', 'li', 'div', 'article'], limit=50)  # 限制数量避免过载
            
            for item in items:
                # 提取标题
                title_elem = item.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b', 'a'])
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                if len(title) < 5:  # 过滤太短的标题
                    continue
                
                # 提取日期
                date_match = re.search(r'(202[0-9]-[0-1][0-9]-[0-3][0-9])', item.get_text())
                publish_date = date_match.group(1) if date_match else ""
                
                # 提取描述
                description = ""
                desc_elem = item.find(['p', 'span', 'div'])
                if desc_elem:
                    description = desc_elem.get_text(strip=True)[:500]
                
                # 如果没有明确的描述，使用项目的全部文本（除了标题）
                if not description:
                    full_text = item.get_text(strip=True)
                    if full_text != title:
                        description = full_text[:500]
                
                if title:
                    update = {
                        'title': title,
                        'description': description,
                        'publish_date': publish_date or datetime.date.today().strftime('%Y-%m-%d'),
                        'service_name': source_name,
                        'source_url': url,
                        'content': f"{title}\n\n{description}" if description else title
                    }
                    updates.append(update)
                    
        except Exception as e:
            logger.debug(f"从容器提取更新时出错: {e}")
        
        return updates
    
    def _filter_existing_updates(self, updates: List[Dict[str, Any]], source_name: str) -> List[Dict[str, Any]]:
        """
        过滤已存在的更新条目
        
        Args:
            updates: 更新条目列表
            source_name: 服务名称
            
        Returns:
            过滤后的更新列表
        """
        filtered_updates = []
        
        with BaseCrawler.metadata_lock:
            for update in updates:
                # 生成更新的唯一标识
                update_id = self._generate_update_id(update)
                
                # 检查是否已存在
                if update_id in self.metadata:
                    filepath = self.metadata[update_id].get('filepath', '')
                    if os.path.exists(filepath):
                        logger.debug(f"跳过已存在的更新: {update['title']}")
                        continue
                
                filtered_updates.append(update)
        
        logger.info(f"源 {source_name}: {len(updates)} -> {len(filtered_updates)} (过滤后)")
        return filtered_updates
    
    def _generate_update_id(self, update: Dict[str, Any]) -> str:
        """
        为更新条目生成唯一ID
        
        Args:
            update: 更新条目
            
        Returns:
            唯一ID字符串
        """
        # 使用标题、发布日期和服务名称生成唯一ID
        content = f"{update.get('title', '')}{update.get('publish_date', '')}{update.get('service_name', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
    
    def _save_update_to_markdown(self, update: Dict[str, Any]) -> Optional[str]:
        """
        将更新条目保存为Markdown文件
        
        Args:
            update: 更新条目
            
        Returns:
            保存的文件路径，失败时返回None
        """
        try:
            # 生成文件名
            update_id = self._generate_update_id(update)
            publish_date = update.get('publish_date', datetime.date.today().strftime('%Y-%m-%d'))
            filename = f"{publish_date}_{update_id}.md"
            filepath = os.path.join(self.output_dir, filename)
            
            # 生成Markdown内容
            markdown_content = self._generate_markdown_content(update)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # 更新元数据
            update_url_key = self._generate_update_id(update)  # 使用ID作为URL键
            with BaseCrawler.metadata_lock:
                self.metadata[update_url_key] = {
                    'title': update.get('title', ''),
                    'publish_date': publish_date,
                    'service_name': update.get('service_name', ''),
                    'source_url': update.get('source_url', ''),
                    'filepath': filepath,
                    'crawl_time': datetime.datetime.now().isoformat(),
                    'file_hash': hashlib.md5(markdown_content.encode('utf-8')).hexdigest()
                }
                
                # 更新元数据管理器
                self.metadata_manager.update_crawler_metadata(self.vendor, self.source_type, self.metadata)
            
            return filepath
            
        except Exception as e:
            logger.error(f"保存更新到Markdown失败: {e}")
            return None
    
    def _generate_markdown_content(self, update: Dict[str, Any]) -> str:
        """
        生成Markdown格式的更新内容
        
        Args:
            update: 更新条目
            
        Returns:
            Markdown内容字符串
        """
        title = update.get('title', '无标题')
        publish_date = update.get('publish_date', '')
        service_name = update.get('service_name', '')
        source_url = update.get('source_url', '')
        description = update.get('description', '')
        content = update.get('content', '')
        
        # 构建Markdown内容
        markdown_lines = [
            f"# {title}",
            "",
            f"**发布时间:** {publish_date}",
            "",
            f"**厂商:** 华为云",
            "",
            f"**服务:** {service_name}",
            "",
            f"**类型:** 产品更新",
            "",
            f"**原始链接:** {source_url}",
            "",
            "---",
            ""
        ]
        
        if description and description != title:
            markdown_lines.extend([
                "## 更新说明",
                "",
                description,
                ""
            ])
        
        if content and content != title and content != description:
            markdown_lines.extend([
                "## 详细内容", 
                "",
                content,
                ""
            ])
        
        return "\n".join(markdown_lines)
    
    def _extract_product_name(self, source_name: str) -> str:
        """
        从源名称提取产品名称
        
        Args:
            source_name: 源名称 (如 'vpc-whatsnew', 'elb-whatsnew')
            
        Returns:
            产品名称 (如 'VPC', 'ELB')
        """
        # 移除常见后缀并转为大写
        product_name = source_name.replace('-whatsnew', '').replace('_whatsnew', '').upper()
        
        # 特殊映射
        product_mapping = {
            'VPC': 'VPC',
            'EIP': 'EIP', 
            'ELB': 'ELB',
            'NATGATEWAY': 'NAT',
            'DC': 'DC',
            'VPN': 'VPN',
            'CC': 'CC',
            'VPCEP': 'VPCEP',
            'ER': 'ER',
            'GA': 'GA'
        }
        
        return product_mapping.get(product_name, product_name)
    
    def _save_monthly_updates(self, month_key: str, month_data: Dict[str, List[Dict[str, Any]]]) -> Optional[str]:
        """
        将产品月度更新保存为Markdown文件
        
        Args:
            month_key: 月份
            month_data: 产品月度更新数据
            
        Returns:
            保存的文件路径，失败时返回None
        """
        try:
            # 生成文件名
            filename = f"{month_key}.md"
            filepath = os.path.join(self.output_dir, filename)
            
            # 生成Markdown内容
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
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # 更新元数据
            # 使用月份作为唯一键
            update_url_key = f"huawei_monthly_{month_key.replace('-', '_')}"
            with BaseCrawler.metadata_lock:
                self.metadata[update_url_key] = {
                    'title': f"华为云网络服务月度更新 - {month_key}",
                    'publish_date': month_key,
                    'service_name': '华为云网络服务',
                    'source_url': '',
                    'filepath': filepath,
                    'crawl_time': datetime.datetime.now().isoformat(),
                    'file_hash': new_hash
                }
                
                # 更新元数据管理器
                self.metadata_manager.update_crawler_metadata(self.vendor, self.source_type, self.metadata)
            
            return filepath
            
        except Exception as e:
            logger.error(f"保存月度更新汇总失败: {e}")
            return None
    
    def _generate_monthly_updates_content(self, month_key: str, month_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        生成月度更新内容的Markdown格式，包含所有产品的更新
        
        Args:
            month_key: 月份 (如 "2025-05")
            month_data: 按产品分组的月度更新数据 {产品名: [更新列表]}
            
        Returns:
            Markdown内容字符串
        """
        # 计算总更新数量
        total_updates = sum(len(updates) for updates in month_data.values())
        
        # 构建Markdown内容
        markdown_lines = [
            f"# 华为云网络服务月度更新 - {month_key}",
            "",
            f"**发布时间:** {month_key}-01",  # 修改：添加具体日期用于排序
            "",
            f"**厂商:** 华为云",
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
        ]
        
        # 添加产品概览表格
        markdown_lines.extend([
            "| 产品 | 更新数量 | 主要更新内容 |",
            "|------|----------|--------------|"
        ])
        
        for product_name, updates in sorted(month_data.items()):
            # 获取前3个主要更新作为概览
            main_updates = updates[:3]
            main_update_titles = [update.get('title', '')[:30] + ('...' if len(update.get('title', '')) > 30 else '') for update in main_updates]
            main_content = '; '.join(main_update_titles)
            if len(updates) > 3:
                main_content += f" 等{len(updates)}项更新"
            
            markdown_lines.append(f"| {product_name} | {len(updates)}条 | {main_content} |")
        
        markdown_lines.extend([
            "",
            "---",
            ""
        ])
        
        # 为每个产品生成详细更新内容
        for product_name, updates in sorted(month_data.items()):
            # 按发布日期排序更新（最新的在前）
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
            
            # 添加更新概览表格
            for idx, update in enumerate(updates, 1):
                title = update.get('title', '').replace('|', '\\|')
                stage = update.get('stage', '').replace('|', '\\|')
                date = update.get('publish_date', '')
                markdown_lines.append(f"| {idx} | {title} | {stage} | {date} |")
            
            markdown_lines.extend([
                "",
                "### 详细更新内容",
                ""
            ])
            
            # 添加每个更新的详细内容
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
                
                # 添加文档链接
                if doc_links:
                    markdown_lines.extend([
                        "**相关文档:**",
                        ""
                    ])
                    for doc_link in doc_links:
                        markdown_lines.append(f"- [{doc_link['text']}]({doc_link['url']})")
                    markdown_lines.append("")
                
                markdown_lines.extend([
                    "---",
                    ""
                ])
            
            markdown_lines.extend([
                "",
                ""
            ])
        
        # 添加页脚信息
        markdown_lines.extend([
            "## 数据来源",
            "",
            "本文档内容来源于华为云官方What's New页面，具体更新详情请访问:",
            ""
        ])
        
        # 添加所有源URL（去重）
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