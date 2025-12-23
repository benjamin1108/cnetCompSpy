#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re
import sys
import time
import hashlib
import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

from src.crawlers.common.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class GcpWhatsnewCrawler(BaseCrawler):
    """GCP网络产品Release Notes爬虫实现"""
    
    def __init__(self, config: Dict[str, Any], vendor: str, source_type: str):
        """初始化GCP Release Notes爬虫"""
        super().__init__(config, vendor, source_type)
        # 获取whatsnew下的所有子源配置
        self.source_config = config.get('sources', {}).get(vendor, {}).get(source_type, {})
        
        # 提取所有网络服务的子源
        self.sub_sources = {}
        for key, value in self.source_config.items():
            if isinstance(value, dict) and 'url' in value:
                self.sub_sources[key] = value
        
        logger.info(f"发现 {len(self.sub_sources)} 个GCP网络服务子源: {list(self.sub_sources.keys())}")
    
    def _crawl(self) -> List[str]:
        """
        爬取GCP网络产品Release Notes
        串行爬取以避免Playwright多线程冲突
        
        Returns:
            保存的文件路径列表
        """
        if not self.sub_sources:
            logger.error("未找到GCP网络服务子源配置")
            return []
        
        saved_files = []
        self._new_count = 0
        self._existing_count = 0
        
        try:
            # 检查是否启用了强制模式
            force_mode = self.crawler_config.get('force', False)
            
            # 收集所有子源的更新条目，按月份分组
            updates_by_month = {}
            
            # 串行爬取以避免Playwright多线程冲突
            for idx, (source_name, source_config) in enumerate(self.sub_sources.items()):
                logger.info(f"开始爬取源 {source_name} ({idx + 1}/{len(self.sub_sources)})")
                
                try:
                    source_updates = self._crawl_single_source(source_name, source_config, force_mode)
                    
                    # 按月份分组
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
                
                # 源之间间隔0.5秒
                if idx < len(self.sub_sources) - 1:
                    time.sleep(0.5)
            
            total_updates = sum(
                sum(len(product_updates) for product_updates in month_data.values()) 
                for month_data in updates_by_month.values()
            )
            logger.info(f"总共收集到 {total_updates} 条GCP网络更新，分为 {len(updates_by_month)} 个月份")
            
            # 如果是测试模式，只处理前几个月
            test_mode = self.source_config.get('test_mode', False)
            if test_mode:
                limited_months = dict(list(updates_by_month.items())[:1])
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
            
            logger.info(f"成功保存 {len(saved_files)} 个GCP月度更新汇总文件")
            return saved_files
            
        except Exception as e:
            logger.error(f"爬取GCP网络更新过程中发生错误: {e}")
            return saved_files
    
    def _crawl_single_source(self, source_name: str, source_config: Dict[str, Any], force_mode: bool) -> List[Dict[str, Any]]:
        """
        爬取单个GCP网络服务的Release Notes
        
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
            updates = self._parse_release_notes_page(html, source_name, url)
            
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
        使用requests获取GCP页面内容（GCP release-notes是服务端渲染）
        
        Args:
            url: 页面URL
            
        Returns:
            页面HTML内容
        """
        import requests
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = requests.get(url, headers=headers, timeout=30, proxies=getattr(self, 'proxies', None))
            response.raise_for_status()
            
            logger.info(f"获取GCP页面成功: {url}, 内容长度: {len(response.text)}")
            return response.text
            
        except Exception as e:
            logger.error(f"获取GCP页面失败: {url} - {e}")
            return None
    
    def _parse_release_notes_page(self, html: str, source_name: str, url: str) -> List[Dict[str, Any]]:
        """
        解析GCP Release Notes页面，提取更新条目
        直接遍历.devsite-release-note元素，通过find_previous_sibling找日期
        
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
            # 直接查找所有.devsite-release-note元素
            notes = soup.select('.devsite-release-note')
            logger.debug(f"在 {source_name} 中找到 {len(notes)} 个更新条目")
            
            for note in notes:
                # 找前一个兄弟节点作为标题（日期）
                date_header = note.find_previous_sibling('h2')
                if not date_header:
                    # 尝试查找父元素中的h2
                    parent = note.parent
                    while parent and not date_header:
                        date_header = parent.find_previous('h2')
                        parent = parent.parent
                
                if not date_header:
                    continue
                
                header_text = date_header.get_text(strip=True)
                
                # 解析日期格式: "November 14, 2025"
                date_match = re.search(
                    r'(January|February|March|April|May|June|July|August|September|October|November|December|'
                    r'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s*(\d{4})',
                    header_text
                )
                
                if not date_match:
                    continue
                
                month_str, day, year = date_match.groups()
                
                # 转换月份
                month_mapping = {
                    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
                    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'Jun': 6,
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                }
                month_num = month_mapping.get(month_str, 1)
                publish_date = f"{year}-{str(month_num).zfill(2)}-{day.zfill(2)}"
                
                # 提取更新类型
                label_elem = note.select_one('.devsite-label')
                update_type = label_elem.get_text(strip=True) if label_elem else 'Feature'
                
                # 提取内容
                content_elem = note.select_one('div > p')
                if content_elem:
                    description = content_elem.get_text(strip=True)
                else:
                    # 回退到获取整个div内容
                    content_div = note.find('div')
                    if content_div:
                        description = content_div.get_text(strip=True)
                    else:
                        description = note.get_text(strip=True)
                        if label_elem:
                            description = description.replace(label_elem.get_text(strip=True), '', 1).strip()
                
                if not description:
                    continue
                
                # 提取相关文档链接
                doc_links = []
                for link in note.find_all('a', href=True):
                    href = link.get('href', '')
                    link_text = link.get_text(strip=True)
                    if href and link_text:
                        if href.startswith('/'):
                            href = f"https://cloud.google.com{href}"
                        doc_links.append({'text': link_text, 'url': href})
                
                # 生成标题
                title = description[:80] + '...' if len(description) > 80 else description
                title = title.split('\n')[0]
                
                update = {
                    'title': title,
                    'description': description,
                    'publish_date': publish_date,
                    'service_name': source_name,
                    'source_url': url,
                    'content': description,
                    'stage': update_type,
                    'doc_links': doc_links
                }
                updates.append(update)
            
            logger.info(f"从 {source_name} 解析到 {len(updates)} 条更新")
            return updates
            
        except Exception as e:
            logger.error(f"解析 {source_name} 页面时发生错误: {e}")
            return []
    
    def _filter_existing_updates(self, updates: List[Dict[str, Any]], source_name: str) -> List[Dict[str, Any]]:
        """
        过滤已存在的更新条目
        """
        filtered_updates = []
        
        with BaseCrawler.metadata_lock:
            for update in updates:
                update_id = self._generate_update_id(update)
                
                if update_id in self.metadata:
                    filepath = self.metadata[update_id].get('filepath', '')
                    if os.path.exists(filepath):
                        logger.debug(f"跳过已存在的更新: {update['title'][:30]}...")
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
        # 特殊映射
        product_mapping = {
            'vpc': 'VPC',
            'load-balancing': 'Cloud Load Balancing',
            'cdn': 'Cloud CDN',
            'dns': 'Cloud DNS',
            'nat': 'Cloud NAT',
            'interconnect': 'Cloud Interconnect',
            'vpn': 'Cloud VPN',
            'network-connectivity': 'Network Connectivity Center',
            'armor': 'Cloud Armor',
            'service-directory': 'Service Directory',
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
            
            update_url_key = f"gcp_monthly_{month_key.replace('-', '_')}"
            with BaseCrawler.metadata_lock:
                self.metadata[update_url_key] = {
                    'title': f"GCP网络服务月度更新 - {month_key}",
                    'publish_date': month_key,
                    'service_name': 'GCP网络服务',
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
            f"# GCP网络服务月度更新 - {month_key}",
            "",
            f"**发布时间:** {month_key}-01",
            "",
            f"**厂商:** Google Cloud Platform",
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
            main_update_titles = [update.get('title', '')[:40] + ('...' if len(update.get('title', '')) > 40 else '') for update in main_updates]
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
            updates.sort(key=lambda x: (x.get('publish_date', ''), x.get('title', '')), reverse=True)
            
            markdown_lines.extend([
                f"## {product_name} 产品更新",
                "",
                f"**更新数量:** {len(updates)} 条",
                "",
                "### 更新列表",
                "",
                "| 序号 | 功能名称 | 更新类型 | 发布日期 |",
                "|------|----------|----------|----------|"
            ])
            
            for idx, update in enumerate(updates, 1):
                title = update.get('title', '').replace('|', '\\|')[:50]
                stage = update.get('stage', 'Feature').replace('|', '\\|')
                date = update.get('publish_date', '')
                markdown_lines.append(f"| {idx} | {title} | {stage} | {date} |")
            
            markdown_lines.extend([
                "",
                "### 详细更新内容",
                ""
            ])
            
            for idx, update in enumerate(updates, 1):
                title = update.get('title', '')
                description = update.get('description', '')
                stage = update.get('stage', 'Feature')
                doc_links = update.get('doc_links', [])
                
                markdown_lines.extend([
                    f"#### {idx}. {title[:80]}",
                    "",
                    f"**发布日期:** {update.get('publish_date', '')}",
                    "",
                    f"**更新类型:** {stage}",
                    ""
                ])
                
                if description:
                    markdown_lines.extend([
                        f"**功能描述:** {description}",
                        ""
                    ])
                
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
        
        # 添加页脚信息
        markdown_lines.extend([
            "## 数据来源",
            "",
            "本文档内容来源于GCP官方Release Notes页面，具体更新详情请访问:",
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
