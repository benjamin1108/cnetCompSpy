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


class TencentcloudWhatsnewCrawler(BaseCrawler):
    """腾讯云网络产品What's New更新爬虫实现"""
    
    def __init__(self, config: Dict[str, Any], vendor: str, source_type: str):
        """初始化腾讯云What's New更新爬虫"""
        super().__init__(config, vendor, source_type)
        # 获取whatsnew下的所有子源配置
        self.source_config = config.get('sources', {}).get(vendor, {}).get(source_type, {})
        
        # 提取所有网络服务的子源
        self.sub_sources = {}
        for key, value in self.source_config.items():
            if isinstance(value, dict) and 'url' in value:
                self.sub_sources[key] = value
        
        logger.info(f"发现 {len(self.sub_sources)} 个腾讯云网络服务子源: {list(self.sub_sources.keys())}")
    
    def _crawl(self) -> List[str]:
        """
        爬取腾讯云网络产品文档更新
        采用多线程处理多个子源，按月份汇总所有产品更新
        
        Returns:
            保存的文件路径列表
        """
        if not self.sub_sources:
            logger.error("未找到腾讯云网络服务子源配置")
            return []
        
        saved_files = []
        
        try:
            # 检查是否启用了强制模式
            force_mode = self.crawler_config.get('force', False)
            
            # 收集所有子源的更新条目，按月份分组
            updates_by_month = {}
            
            # 使用线程池处理多个子源
            thread_pool = get_thread_pool()
            max_workers = min(len(self.sub_sources), thread_pool.current_threads_target // 2)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_source = {}
                
                for idx, (source_name, source_config) in enumerate(self.sub_sources.items()):
                    # 慢启动延迟
                    if idx > 0:
                        time.sleep(0.5)
                    
                    future = executor.submit(self._crawl_single_source, source_name, source_config, force_mode)
                    future_to_source[future] = source_name
                    logger.info(f"已提交任务: {source_name} ({idx + 1}/{len(self.sub_sources)})")
                
                # 收集结果并按月份分组
                for future in concurrent.futures.as_completed(future_to_source):
                    source_name = future_to_source[future]
                    try:
                        source_updates = future.result(timeout=120)
                        
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
            logger.info(f"总共收集到 {total_updates} 条腾讯云网络更新，分为 {len(updates_by_month)} 个月份")
            
            # 为每个月份创建汇总文档
            for month_key, month_data in updates_by_month.items():
                try:
                    file_path = self._save_monthly_updates(month_key, month_data)
                    if file_path:
                        saved_files.append(file_path)
                        logger.debug(f"已保存月度更新汇总: {month_key} -> {file_path}")
                except Exception as e:
                    logger.error(f"保存月度更新汇总失败: {month_key} - {e}")
            
            logger.info(f"成功保存 {len(saved_files)} 个腾讯云月度更新汇总文件")
            return saved_files
            
        except Exception as e:
            logger.error(f"爬取腾讯云网络更新过程中发生错误: {e}")
            return saved_files
        finally:
            self._close_driver()
    
    def _crawl_single_source(self, source_name: str, source_config: Dict[str, Any], force_mode: bool) -> List[Dict[str, Any]]:
        """
        爬取单个腾讯云网络服务的更新
        
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
            html = self._get_page_content(url)
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
    
    def _get_page_content(self, url: str) -> Optional[str]:
        """获取页面内容"""
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
                logger.debug(f"使用requests成功获取页面: {url}")
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
        解析腾讯云What's New页面，提取更新条目
        腾讯云的产品动态页面使用#docArticleContent容器，内容为表格形式
        
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
            # 腾讯云文档页面主内容区域
            content_area = soup.select_one('#docArticleContent')
            if not content_area:
                content_area = soup.select_one('.J-articleContent')
            if not content_area:
                content_area = soup.find('body')
            
            # 查找所有表格
            tables = content_area.find_all('table') if content_area else soup.find_all('table')
            
            if not tables:
                logger.warning(f"在 {source_name} 中未找到表格结构")
                return []
            
            logger.debug(f"在 {source_name} 中找到 {len(tables)} 个表格")
            
            # 腾讯云产品动态表格按年份分组，年份标题是 H2 元素
            # 查找所有 h2/h3 并匹配年份
            year_headers = content_area.find_all(['h2', 'h3']) if content_area else []
            
            # 建立年份和表格的映射关系
            table_year_map = {}
            current_year = datetime.date.today().strftime('%Y')
            
            for header in year_headers:
                header_text = header.get_text(strip=True).replace('\u200b', '').replace('\ufeff', '')
                year_match = re.search(r'(20[1-2][0-9])年', header_text)
                if year_match:
                    year = year_match.group(1)
                    # 查找该年份标题后的第一个表格
                    next_table = header.find_next('table')
                    if next_table:
                        table_year_map[id(next_table)] = year
                        logger.debug(f"找到年份映射: {year}年 -> 表格")
            
            # 解析每个表格
            for table in tables:
                table_id = id(table)
                table_year = table_year_map.get(table_id, current_year)
                table_updates = self._parse_tencent_table(table, source_name, url, table_year)
                updates.extend(table_updates)
            
            logger.info(f"从 {source_name} 解析到 {len(updates)} 条更新")
            return updates
            
        except Exception as e:
            logger.error(f"解析 {source_name} 页面时发生错误: {e}")
            return []
    
    def _parse_tencent_table(self, table, source_name: str, url: str, year: str) -> List[Dict[str, Any]]:
        """
        解析腾讯云的标准表格结构
        腾讯云表格格式：动态名称 | 动态描述 | 发布时间 | 相关文档
        
        Args:
            table: BeautifulSoup表格元素
            source_name: 服务名称
            url: 页面URL  
            year: 默认年份
            
        Returns:
            更新条目列表
        """
        updates = []
        
        try:
            rows = table.find_all('tr')
            if not rows:
                return updates
            
            # 检测表头，确定列的含义
            header_row = rows[0]
            headers = [cell.get_text(strip=True).replace('\u200b', '') for cell in header_row.find_all(['th', 'td'])]
            
            # 列索引映射
            title_col = -1  # 动态名称
            desc_col = -1   # 动态描述
            date_col = -1   # 发布时间
            doc_col = -1    # 相关文档
            
            for idx, header in enumerate(headers):
                header_clean = header.lower()
                if '名称' in header_clean or 'name' in header_clean:
                    title_col = idx
                elif '描述' in header_clean or '说明' in header_clean or '内容' in header_clean or '变更' in header_clean:
                    desc_col = idx
                elif '时间' in header_clean or '日期' in header_clean:
                    date_col = idx
                elif '文档' in header_clean or '链接' in header_clean:
                    doc_col = idx
            
            # 默认布局：动态名称 | 动态描述 | 发布时间 | 相关文档
            if title_col == -1:
                title_col = 0
            if desc_col == -1:
                desc_col = 1 if len(headers) > 1 else 0
            if date_col == -1:
                date_col = 2 if len(headers) > 2 else -1
            if doc_col == -1:
                doc_col = 3 if len(headers) > 3 else -1
            
            # 处理数据行
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                
                try:
                    # 提取动态名称
                    title = cells[title_col].get_text(strip=True) if title_col < len(cells) else ""
                    
                    # 提取动态描述
                    description = cells[desc_col].get_text(strip=True) if desc_col >= 0 and desc_col < len(cells) else ""
                    
                    # 提取发布时间
                    date_text = cells[date_col].get_text(strip=True) if date_col >= 0 and date_col < len(cells) else ""
                    publish_date = self._parse_date(date_text, year)
                    
                    # 提取文档链接
                    doc_links = []
                    if doc_col >= 0 and doc_col < len(cells):
                        links = cells[doc_col].find_all('a', href=True)
                        for link in links:
                            href = link.get('href', '')
                            link_text = link.get_text(strip=True)
                            if href:
                                if href.startswith('/'):
                                    full_url = urljoin('https://cloud.tencent.com', href)
                                elif href.startswith('http'):
                                    full_url = href
                                else:
                                    full_url = urljoin(url, href)
                                doc_links.append({'text': link_text, 'url': full_url})
                    
                    # 过滤无效行
                    if not title or len(title) < 2:
                        continue
                    
                    # 构建内容
                    content_parts = [title]
                    if description and description != title:
                        content_parts.append(f"动态描述：{description}")
                    if doc_links:
                        content_parts.append("相关文档：")
                        for doc_link in doc_links:
                            content_parts.append(f"- [{doc_link['text']}]({doc_link['url']})")
                    
                    update = {
                        'title': title,
                        'description': description,
                        'publish_date': publish_date,
                        'service_name': source_name,
                        'source_url': url,
                        'content': '\n\n'.join(content_parts),
                        'doc_links': doc_links
                    }
                    
                    updates.append(update)
                    logger.debug(f"解析到更新: {title[:30]}... ({publish_date})")
                    
                except Exception as e:
                    logger.debug(f"解析表格行时出错: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"解析腾讯云表格时出错: {e}")
        
        return updates
    
    def _parse_date(self, date_text: str, default_year: str) -> str:
        """
        解析日期字符串，返回YYYY-MM格式
        
        Args:
            date_text: 日期文本
            default_year: 默认年份
            
        Returns:
            格式化的日期字符串
        """
        # 清理零宽字符
        date_text = date_text.replace('\u200b', '').replace('\ufeff', '').strip()
        
        # 尝试匹配 YYYY-MM-DD 格式
        match = re.search(r'(20[1-2][0-9])-([0-1]?[0-9])-([0-3]?[0-9])', date_text)
        if match:
            return f"{match.group(1)}-{match.group(2).zfill(2)}"
        
        # 尝试匹配 YYYY-MM 格式（腾讯云常见格式）
        match = re.search(r'(20[1-2][0-9])-([0-1]?[0-9])(?:\D|$)', date_text)
        if match:
            return f"{match.group(1)}-{match.group(2).zfill(2)}"
        
        # 尝试匹配 YYYY年MM月 格式
        match = re.search(r'(20[1-2][0-9])年([0-1]?[0-9])月', date_text)
        if match:
            return f"{match.group(1)}-{match.group(2).zfill(2)}"
        
        # 尝试匹配 MM月DD日 格式（使用默认年份）
        match = re.search(r'([0-1]?[0-9])月([0-3]?[0-9])日', date_text)
        if match:
            return f"{default_year}-{match.group(1).zfill(2)}"
        
        # 默认返回当前月份
        return datetime.date.today().strftime('%Y-%m')
    
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
            'clb': 'CLB',
            'gwlb': 'GWLB',
            'vpc': 'VPC',
            'nat': 'NAT',
            'bwp': 'BWP',
            'stp': 'STP',
            'ipv6': 'IPv6',
            'eip': 'EIP',
            'ihpn': 'IHPN',
            'privatelink': 'PrivateLink',
            'dc': 'DC',
            'ccn': 'CCN',
            'vpn': 'VPN',
            'gaap': 'GAAP'
        }
        return product_mapping.get(source_name.lower(), source_name.upper())
    
    def _save_monthly_updates(self, month_key: str, month_data: Dict[str, List[Dict[str, Any]]]) -> Optional[str]:
        """将产品月度更新保存为Markdown文件"""
        try:
            filename = f"{month_key}.md"
            filepath = os.path.join(self.output_dir, filename)
            
            markdown_content = self._generate_monthly_updates_content(month_key, month_data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            update_url_key = f"tencentcloud_monthly_{month_key.replace('-', '_')}"
            with BaseCrawler.metadata_lock:
                self.metadata[update_url_key] = {
                    'title': f"腾讯云网络服务月度更新 - {month_key}",
                    'publish_date': month_key,
                    'service_name': '腾讯云网络服务',
                    'source_url': '',
                    'filepath': filepath,
                    'crawl_time': datetime.datetime.now().isoformat(),
                    'file_hash': hashlib.md5(markdown_content.encode('utf-8')).hexdigest()
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
            f"# 腾讯云网络服务月度更新 - {month_key}",
            "",
            f"**发布时间:** {month_key}-01",
            "",
            f"**厂商:** 腾讯云",
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
        
        for product_name, updates in month_data.items():
            main_updates = updates[:3]
            main_update_titles = [update.get('title', '')[:30] + ('...' if len(update.get('title', '')) > 30 else '') for update in main_updates]
            main_content = '; '.join(main_update_titles)
            if len(updates) > 3:
                main_content += f" 等{len(updates)}项更新"
            markdown_lines.append(f"| {product_name} | {len(updates)}条 | {main_content} |")
        
        markdown_lines.extend(["", "---", ""])
        
        # 为每个产品生成详细更新内容
        for product_name, updates in month_data.items():
            updates.sort(key=lambda x: x.get('publish_date', ''), reverse=True)
            
            markdown_lines.extend([
                f"## {product_name} 产品更新",
                "",
                f"**更新数量:** {len(updates)} 条",
                "",
                "### 更新列表",
                "",
                "| 序号 | 更新内容 | 发布日期 |",
                "|------|----------|----------|"
            ])
            
            for idx, update in enumerate(updates, 1):
                title = update.get('title', '').replace('|', '\\|')[:50]
                date = update.get('publish_date', '')
                markdown_lines.append(f"| {idx} | {title} | {date} |")
            
            markdown_lines.extend(["", "### 详细更新内容", ""])
            
            for idx, update in enumerate(updates, 1):
                title = update.get('title', '')
                description = update.get('description', '')
                doc_links = update.get('doc_links', [])
                
                markdown_lines.extend([
                    f"#### {idx}. {title}",
                    "",
                    f"**发布日期:** {update.get('publish_date', '')}",
                    ""
                ])
                
                if description and description != title:
                    markdown_lines.extend([
                        f"**变更说明:** {description}",
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
            "本文档内容来源于腾讯云官方产品动态页面，具体更新详情请访问:",
            ""
        ])
        
        source_urls = set()
        for updates in month_data.values():
            for update in updates:
                source_url = update.get('source_url', '')
                if source_url:
                    source_urls.add(source_url)
        
        for source_url in sorted(source_urls):
            markdown_lines.append(f"- {source_url}")
        
        markdown_lines.extend([
            "",
            f"**生成时间:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ])
        
        return "\n".join(markdown_lines)
