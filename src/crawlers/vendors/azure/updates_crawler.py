#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import logging
import json
import hashlib
import time
import os
from datetime import datetime
from typing import List, Dict

from src.crawlers.common.base_crawler import BaseCrawler
from src.crawlers.common.base_crawler import BaseCrawler, metadata_lock

from typing import Any

logger = logging.getLogger(__name__)

class AzureUpdatesCrawler(BaseCrawler):
    """Azure Updates爬虫"""

    def __init__(self, config: Dict[str, Any], vendor: str, source_type: str):
        super().__init__(config, vendor, source_type)
        self.batch_mode = False  # 添加 batch_mode 属性
        self.api_url = "https://www.microsoft.com/releasecommunications/api/v2/azure"
        self.params = {
            "$count": "true",
            "includeFacets": "true",
            "top": "20",
            "skip": "0",
            "filter": "products/any(f:f%20in%20(%27Application%20Gateway%27,%20%27Azure%20Bastion%27,%20%27Azure%20DDoS%20Protection%27,%20%27Azure%20DNS%27,%20%27Azure%20ExpressRoute%27,%20%27Azure%20Firewall%27,%20%27Azure%20Firewall%20Manager%27,%20%27Azure%20Front%20Door%27,%20%27Azure%20NAT%20Gateway%27,%20%27Azure%20Private%20Link%27,%20%27Azure%20Route%20Server%27,%20%27Azure%20Virtual%20Network%20Manager%27,%20%27Content%20Delivery%20Network%27,%20%27Load%20Balancer%27,%20%27Network%20Watcher%27,%20%27Traffic%20Manager%27,%20%27Virtual%20Network%27,%20%27Virtual%20WAN%27,%20%27VPN%20Gateway%27,%20%27Web%20Application%20Firewall%27))",
            "orderby": "modified%20desc"
        }
        
        # 记录已处理的更新
        self.processed_updates = set()

    def _crawl(self) -> List[str]:
        """具体爬虫逻辑"""
        logger.info("Starting Azure Updates Crawler")
        updates = self.fetch_updates()
        if not updates:
            logger.warning("No updates fetched from Azure API")
            return []

        file_paths = self.save_updates(updates)
        logger.info(f"Fetched and saved {len(file_paths)} updates")
        return file_paths

    def fetch_updates(self) -> List[Dict[str, Any]]:
        """从Azure API获取更新"""
        updates = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        while True:
            url_with_params = f"{self.api_url}?{'&'.join(f'{k}={v}' for k, v in self.params.items())}"
            logger.info(f"Fetching updates from Azure API: {url_with_params}")
            response = requests.get(url_with_params, headers=headers)
            if response.status_code != 200:
                logger.error(f"Failed to fetch updates from Azure API: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                break

            # 打印响应内容以调试
            logger.debug(f"Response content: {response.text}")

            try:
                data = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON response: {e}")
                logger.error(f"Response content: {response.text}")
                break

            updates.extend(data.get('value', []))
            next_link = data.get('@odata.nextLink')
            if not next_link:
                break

            # 解析下一页的skip参数
            skip_param = next_link.split('skip=')[1].split('&')[0]
            self.params['skip'] = skip_param

            # 增加请求间隔
            time.sleep(1)

        return updates
    
    def check_if_update_exists(self, title: str, created: str) -> bool:
        """
        检查更新是否已存在
        
        Args:
            title: 更新标题
            created: 创建时间
            
        Returns:
            True如果更新已存在，否则False
        """
        # 首先检查是否在本次爬取中已处理过
        if created in self.processed_updates:
            return True
            
        # 检查元数据中是否存在
        with BaseCrawler.metadata_lock:
            # 检查标题对应的哈希值文件是否存在
            pub_date = created.split('T')[0]  # 提取日期部分
            filename = f"{pub_date}_{hashlib.md5(title.encode()).hexdigest()[:8]}.md"
            file_path = os.path.join(self.output_dir, filename)
            
            # 检查文件是否存在
            if os.path.exists(file_path):
                logger.info(f"Update already exists: {title} ({created})")
                return True
                
            # 检查created是否在metadata中
            if created in self.metadata:
                logger.info(f"Update metadata exists: {title} ({created})")
                return True
                
            return False

    def save_updates(self, updates: List[Dict[str, Any]]) -> List[str]:
        """保存更新到Markdown文件"""
        file_paths = []
        new_updates_count = 0
        existing_updates_count = 0
        
        for update in updates:
            title = update.get('title')
            created = update.get('created')
            description = update.get('description')

            if not title or not created or not description:
                logger.warning(f"Incomplete update record: {update}")
                continue
                
            # 检查更新是否已存在
            if self.check_if_update_exists(title, created):
                existing_updates_count += 1
                continue
                
            # 记录已处理的更新
            self.processed_updates.add(created)
            new_updates_count += 1

            # 创建文件名
            pub_date = created.split('T')[0]  # 提取日期部分
            filename = f"{pub_date}_{hashlib.md5(title.encode()).hexdigest()[:8]}.md"
            file_path = os.path.join(self.output_dir, filename)

            # 将日期格式保持为ISO格式，以便前端JavaScript可以正确解析
            display_date = pub_date  # 保持YYYY-MM-DD格式

            # 构建Markdown内容
            metadata_lines = [
                f"# {title}",
                "",
                f"**发布时间:** {display_date}",
                "",
                f"**厂商:** Azure",
                "",
                f"**类型:** Updates",
                "",
                "---",
                "",
            ]
            final_content = "\n".join(metadata_lines) + description

            # 线程安全地写入文件
            with self.lock:
                # 确保目录存在
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(final_content)

                # 创建metadata条目
                metadata_entry = {
                    'filepath': file_path,
                    'title': title,
                    'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'vendor': self.vendor,
                    'source_type': self.source_type
                }

                # 更新内存中的metadata
                with BaseCrawler.metadata_lock:
                    self.metadata[created] = metadata_entry

                # 如果是批量更新模式，则收集metadata条目，不立即写入文件
                if self.batch_mode:
                    self._pending_metadata_updates[created] = metadata_entry
                else:
                    # 否则立即更新metadata文件
                    with BaseCrawler.metadata_lock:
                        self.metadata_manager.update_crawler_metadata_entry(self.vendor, self.source_type, created, metadata_entry)

            file_paths.append(file_path)
            logger.info(f"Saved update to {file_path}")
            
        # 输出统计信息
        if existing_updates_count > 0:
            logger.info(f"跳过了 {existing_updates_count} 个已存在的更新")
        if new_updates_count == 0:
            logger.info("没有新的Azure更新需要爬取")

        return file_paths
