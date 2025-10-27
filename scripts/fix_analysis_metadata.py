#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复分析文件的metadata，从原始文件或分析文件内容中提取正确的发布日期
"""

import os
import sys
import json
import re
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.metadata_manager import MetadataManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_publish_date_from_content(content: str) -> str:
    """从文件内容中提取发布日期"""
    lines = content.split('\n')
    
    # 检查前60行
    for line in lines[:60]:
        line_stripped = line.strip()
        
        # 匹配 **发布时间:** 格式
        if line_stripped.startswith('发布时间:') or line_stripped.startswith('**发布时间:**'):
            date_str = line_stripped.split(':', 1)[1].strip().replace('**', '').strip()
            return date_str
        
        # 匹配 发布于: 格式
        if line_stripped.startswith('发布于:') or '发布于:' in line_stripped:
            date_match = re.search(r'发布于[：:]\s*(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日|\d{4}[-/]\d{1,2}[-/]\d{1,2})', line_stripped)
            if date_match:
                date_str = date_match.group(1).strip()
                # 转换中文日期格式为标准格式
                if '年' in date_str:
                    date_str = re.sub(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', r'\1-\2-\3', date_str)
                return date_str
    
    return ''


def fix_metadata():
    """修复分析metadata"""
    base_dir = project_root
    metadata_manager = MetadataManager(base_dir=str(base_dir))
    
    analysis_dir = base_dir / 'data' / 'analysis'
    raw_dir = base_dir / 'data' / 'raw'
    
    fixed_count = 0
    total_count = 0
    
    # 遍历所有分析文件
    for vendor_dir in analysis_dir.iterdir():
        if not vendor_dir.is_dir():
            continue
        
        vendor = vendor_dir.name
        logger.info(f"处理厂商: {vendor}")
        
        for type_dir in vendor_dir.iterdir():
            if not type_dir.is_dir():
                continue
            
            doc_type = type_dir.name
            
            for analysis_file in type_dir.glob('*.md'):
                total_count += 1
                
                # 获取相对路径
                rel_path = analysis_file.relative_to(base_dir)
                rel_path_str = str(rel_path).replace('\\', '/')
                
                # 检查metadata中是否有publish_date
                current_metadata = metadata_manager.analysis_metadata.get(rel_path_str, {})
                current_publish_date = current_metadata.get('publish_date', '')
                
                # 检查日期格式是否需要标准化（月份或日期是单数字）
                needs_fix = False
                if current_publish_date:
                    date_parts = current_publish_date.split('-')
                    if len(date_parts) == 3:
                        year, month, day = date_parts
                        # 如果月份或日期不是两位数，需要修复
                        if len(month) == 1 or len(day) == 1:
                            needs_fix = True
                
                # 如果已经有正确格式的publish_date，跳过
                if current_publish_date and not current_publish_date.startswith('2025-10-27') and not needs_fix:
                    continue
                
                # 尝试从分析文件内容中提取
                try:
                    with open(analysis_file, 'r', encoding='utf-8') as f:
                        analysis_content = f.read()
                    
                    publish_date = extract_publish_date_from_content(analysis_content)
                    
                    # 如果分析文件中没有找到，尝试从原始文件中提取
                    if not publish_date:
                        raw_file = raw_dir / vendor / doc_type / analysis_file.name
                        if raw_file.exists():
                            with open(raw_file, 'r', encoding='utf-8') as f:
                                raw_content = f.read()
                            publish_date = extract_publish_date_from_content(raw_content)
                    
                    # 如果找到了发布日期，更新metadata
                    if publish_date:
                        # 标准化日期格式：确保月份和日期都是两位数
                        publish_date = publish_date.strip()
                        # 处理 YYYY-M-D 或 YYYY-MM-D 或 YYYY-M-DD 格式
                        date_parts = publish_date.split('-')
                        if len(date_parts) == 3:
                            year, month, day = date_parts
                            publish_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        
                        # 更新metadata
                        if rel_path_str not in metadata_manager.analysis_metadata:
                            metadata_manager.analysis_metadata[rel_path_str] = {}
                        
                        metadata_manager.analysis_metadata[rel_path_str]['publish_date'] = publish_date
                        
                        # 同时更新info中的publish_date
                        if 'info' in metadata_manager.analysis_metadata[rel_path_str]:
                            metadata_manager.analysis_metadata[rel_path_str]['info']['publish_date'] = publish_date
                        
                        fixed_count += 1
                        logger.info(f"修复: {rel_path_str} -> {publish_date}")
                    else:
                        logger.warning(f"未找到发布日期: {rel_path_str}")
                
                except Exception as e:
                    logger.error(f"处理文件出错 {analysis_file}: {e}")
    
    # 保存metadata
    logger.info("保存metadata...")
    metadata_manager.save_analysis_metadata()
    
    logger.info(f"完成！总共处理 {total_count} 个文件，修复了 {fixed_count} 个文件的metadata")


if __name__ == '__main__':
    fix_metadata()
