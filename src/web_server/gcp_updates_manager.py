#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GCP更新管理器

负责解析GCP月度汇总文件，提取产品和更新数据，支持按产品和月份筛选。
"""

import os
import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime


class GcpUpdatesManager:
    """GCP更新管理器类"""
    
    def __init__(self, raw_dir: str):
        """
        初始化GCP更新管理器
        
        Args:
            raw_dir: 原始数据目录路径
        """
        self.logger = logging.getLogger(__name__)
        self.raw_dir = raw_dir
        self.gcp_whatsnew_dir = os.path.join(raw_dir, 'gcp', 'whatsnew')
        
        # 缓存解析后的数据
        self._cache = None
        self._cache_time = None
        self._cache_ttl = 300  # 缓存5分钟
        
        self.logger.info("GCP更新管理器初始化完成")
    
    def get_all_updates(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        获取所有GCP更新数据
        
        Args:
            force_refresh: 是否强制刷新缓存
            
        Returns:
            包含所有更新数据的字典，包括产品列表、月份列表和更新详情
        """
        # 检查缓存
        if not force_refresh and self._cache is not None:
            if self._cache_time and (datetime.now() - self._cache_time).seconds < self._cache_ttl:
                return self._cache
        
        # 解析所有月度文件
        all_updates = []
        products = set()
        months = set()
        
        if not os.path.exists(self.gcp_whatsnew_dir):
            self.logger.warning(f"GCP whatsnew目录不存在: {self.gcp_whatsnew_dir}")
            return {
                'updates': [],
                'products': [],
                'months': [],
                'total_count': 0
            }
        
        # 遍历所有月度文件
        for filename in sorted(os.listdir(self.gcp_whatsnew_dir), reverse=True):
            if not filename.endswith('.md'):
                continue
            
            file_path = os.path.join(self.gcp_whatsnew_dir, filename)
            month_key = filename.replace('.md', '')
            months.add(month_key)
            
            # 解析文件
            file_updates = self._parse_monthly_file(file_path, month_key)
            for update in file_updates:
                products.add(update['product'])
                all_updates.append(update)
        
        # 按日期排序（最新在前）
        all_updates.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # 构建结果
        result = {
            'updates': all_updates,
            'products': sorted(list(products)),
            'months': sorted(list(months), reverse=True),
            'total_count': len(all_updates)
        }
        
        # 更新缓存
        self._cache = result
        self._cache_time = datetime.now()
        
        self.logger.info(f"解析完成: {len(all_updates)} 条更新, {len(products)} 个产品, {len(months)} 个月份")
        return result
    
    def get_filtered_updates(self, product: Optional[str] = None, 
                             month: Optional[str] = None,
                             update_type: Optional[str] = None,
                             page: int = 1,
                             per_page: int = 20) -> Dict[str, Any]:
        """
        获取过滤后的更新数据
        
        Args:
            product: 产品名称筛选
            month: 月份筛选 (格式: YYYY-MM)
            update_type: 更新类型筛选
            page: 页码
            per_page: 每页数量
            
        Returns:
            过滤后的更新数据，包含分页信息
        """
        all_data = self.get_all_updates()
        updates = all_data['updates']
        
        # 应用过滤器
        if product:
            updates = [u for u in updates if u['product'] == product]
        
        if month:
            updates = [u for u in updates if u['month'] == month]
        
        if update_type:
            updates = [u for u in updates if u.get('type', '').lower() == update_type.lower()]
        
        # 计算分页
        total = len(updates)
        total_pages = (total + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'updates': updates[start:end],
            'products': all_data['products'],
            'months': all_data['months'],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'filter': {
                'product': product,
                'month': month,
                'update_type': update_type
            }
        }
    
    def get_products_summary(self) -> List[Dict[str, Any]]:
        """
        获取产品摘要列表
        
        Returns:
            产品列表，包含每个产品的更新数量
        """
        all_data = self.get_all_updates()
        updates = all_data['updates']
        
        # 统计每个产品的更新数量
        product_counts = {}
        product_latest = {}
        
        for update in updates:
            product = update['product']
            if product not in product_counts:
                product_counts[product] = 0
                product_latest[product] = update.get('date', '')
            product_counts[product] += 1
            # 记录最新日期
            if update.get('date', '') > product_latest[product]:
                product_latest[product] = update['date']
        
        # 构建结果列表
        result = []
        for product in sorted(product_counts.keys()):
            result.append({
                'name': product,
                'count': product_counts[product],
                'latest_date': product_latest[product]
            })
        
        # 按更新数量排序
        result.sort(key=lambda x: x['count'], reverse=True)
        return result
    
    def get_months_summary(self) -> List[Dict[str, Any]]:
        """
        获取月份摘要列表
        
        Returns:
            月份列表，包含每个月份的更新数量
        """
        all_data = self.get_all_updates()
        updates = all_data['updates']
        
        # 统计每个月份的更新数量
        month_counts = {}
        month_products = {}
        
        for update in updates:
            month = update['month']
            product = update['product']
            
            if month not in month_counts:
                month_counts[month] = 0
                month_products[month] = set()
            
            month_counts[month] += 1
            month_products[month].add(product)
        
        # 构建结果列表
        result = []
        for month in sorted(month_counts.keys(), reverse=True):
            result.append({
                'month': month,
                'count': month_counts[month],
                'product_count': len(month_products[month])
            })
        
        return result
    
    def _parse_monthly_file(self, file_path: str, month_key: str) -> List[Dict[str, Any]]:
        """
        解析月度汇总文件
        
        Args:
            file_path: 文件路径
            month_key: 月份键值 (YYYY-MM)
            
        Returns:
            更新列表
        """
        updates = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分割产品部分
            # 查找 "## XXXX 产品更新" 格式的标题
            product_sections = re.split(r'\n## ([^\n]+) 产品更新\n', content)
            
            # 第一部分是头部信息，跳过
            for i in range(1, len(product_sections), 2):
                if i + 1 >= len(product_sections):
                    break
                    
                product_name = product_sections[i].strip()
                section_content = product_sections[i + 1]
                
                # 解析详细更新内容部分
                # 查找 "#### N. 标题" 格式
                detail_pattern = r'#### \d+\.\s+([^\n]+)\n+(.*?)(?=\n#### \d+\.|---\n## |\n## 数据来源|$)'
                details = re.findall(detail_pattern, section_content, re.DOTALL)
                
                for title, detail_content in details:
                    update = self._parse_update_detail(title.strip(), detail_content.strip(), product_name, month_key)
                    if update:
                        updates.append(update)
            
            self.logger.debug(f"从 {file_path} 解析到 {len(updates)} 条更新")
            
        except Exception as e:
            self.logger.error(f"解析文件失败 {file_path}: {e}")
        
        return updates
    
    def _parse_update_detail(self, title: str, content: str, product: str, month_key: str) -> Optional[Dict[str, Any]]:
        """
        解析单条更新详情
        
        Args:
            title: 更新标题
            content: 更新内容
            product: 产品名称
            month_key: 月份键值
            
        Returns:
            更新字典
        """
        try:
            # 提取发布日期
            date_match = re.search(r'\*\*发布日期:\*\*\s*(\d{4}-\d{2}-\d{2})', content)
            date = date_match.group(1) if date_match else f"{month_key}-01"
            
            # 提取更新类型
            type_match = re.search(r'\*\*更新类型:\*\*\s*(\w+)', content)
            update_type = type_match.group(1) if type_match else 'Feature'
            
            # 提取功能描述
            desc_match = re.search(r'\*\*功能描述:\*\*\s*(.+?)(?=\n\*\*|$)', content, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else ''
            
            # 提取相关文档链接
            doc_links = []
            link_pattern = r'\- \[([^\]]+)\]\(([^\)]+)\)'
            for link_match in re.finditer(link_pattern, content):
                doc_links.append({
                    'text': link_match.group(1),
                    'url': link_match.group(2)
                })
            
            return {
                'title': title,
                'product': product,
                'date': date,
                'month': month_key,
                'type': update_type,
                'description': description,
                'doc_links': doc_links
            }
            
        except Exception as e:
            self.logger.error(f"解析更新详情失败: {e}")
            return None
    
    def get_update_types(self) -> List[str]:
        """
        获取所有更新类型
        
        Returns:
            更新类型列表
        """
        all_data = self.get_all_updates()
        types = set()
        
        for update in all_data['updates']:
            update_type = update.get('type', '')
            if update_type:
                types.add(update_type)
        
        return sorted(list(types))
