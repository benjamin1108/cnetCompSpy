#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
为现有的分析文档添加原始元数据

这个脚本会：
1. 读取所有分析文档
2. 从对应的原始文档中提取元数据
3. 在分析文档顶部添加元数据
"""

import os
import re
import json
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_metadata_from_raw(raw_file_path: str) -> dict:
    """从原始文档中提取元数据"""
    metadata = {
        'publish_date': '',
        'vendor': '',
        'type': '',
        'original_url': ''
    }
    
    try:
        with open(raw_file_path, 'r', encoding='utf-8') as f:
            content = f.read(2048)  # 只读取前2KB
        
        lines = content.split('\n')
        for line in lines[:30]:
            line_stripped = line.strip()
            
            # 提取发布时间
            if line_stripped.startswith('**发布时间:**'):
                metadata['publish_date'] = line_stripped.split(':', 1)[1].strip().replace('**', '').strip()
            
            # 提取厂商
            elif line_stripped.startswith('**厂商:**'):
                metadata['vendor'] = line_stripped.split(':', 1)[1].strip().replace('**', '').strip()
            
            # 提取类型
            elif line_stripped.startswith('**类型:**'):
                metadata['type'] = line_stripped.split(':', 1)[1].strip().replace('**', '').strip()
            
            # 提取原始链接
            elif line_stripped.startswith('**原始链接:**'):
                url_part = line_stripped.split(':', 1)[1].strip()
                # 提取markdown链接中的URL
                url_match = re.search(r'\[(.*?)\]\((.*?)\)', url_part)
                if url_match:
                    metadata['original_url'] = url_match.group(2)
                else:
                    metadata['original_url'] = url_part
        
        # 如果没有提取到发布时间，尝试从文件名提取
        if not metadata['publish_date']:
            filename = os.path.basename(raw_file_path)
            date_match = re.match(r'^(\d{4}-\d{2}-\d{2})_', filename)
            if date_match:
                metadata['publish_date'] = date_match.group(1)
        
    except Exception as e:
        logger.error(f"提取元数据失败 {raw_file_path}: {e}")
    
    return metadata

def has_metadata_header(content: str) -> bool:
    """检查分析文档是否已经有元数据头部"""
    lines = content.split('\n')
    for line in lines[:10]:
        if line.strip().startswith('**发布时间:**') or line.strip().startswith('**厂商:**'):
            return True
    return False

def add_metadata_to_analysis_file(analysis_file_path: str, raw_file_path: str) -> bool:
    """为分析文档添加元数据"""
    try:
        # 读取分析文档
        with open(analysis_file_path, 'r', encoding='utf-8') as f:
            analysis_content = f.read()
        
        # 检查是否已经有元数据
        if has_metadata_header(analysis_content):
            logger.debug(f"跳过（已有元数据）: {analysis_file_path}")
            return False
        
        # 从原始文档提取元数据
        metadata = extract_metadata_from_raw(raw_file_path)
        
        # 构建元数据头部
        metadata_header = ""
        if metadata['publish_date']:
            metadata_header += f"**发布时间:** {metadata['publish_date']}\n\n"
        if metadata['vendor']:
            metadata_header += f"**厂商:** {metadata['vendor']}\n\n"
        if metadata['type']:
            metadata_header += f"**类型:** {metadata['type']}\n\n"
        if metadata['original_url']:
            metadata_header += f"**原始链接:** {metadata['original_url']}\n\n"
        
        if metadata_header:
            metadata_header += "---\n\n"
            
            # 写入更新后的内容
            with open(analysis_file_path, 'w', encoding='utf-8') as f:
                f.write(metadata_header)
                f.write(analysis_content)
            
            logger.info(f"✓ 已添加元数据: {analysis_file_path}")
            return True
        else:
            logger.warning(f"未找到元数据: {raw_file_path}")
            return False
            
    except Exception as e:
        logger.error(f"处理失败 {analysis_file_path}: {e}")
        return False

def main():
    """主函数"""
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    raw_dir = project_root / 'data' / 'raw'
    analysis_dir = project_root / 'data' / 'analysis'
    
    if not raw_dir.exists():
        logger.error(f"原始数据目录不存在: {raw_dir}")
        return
    
    if not analysis_dir.exists():
        logger.error(f"分析数据目录不存在: {analysis_dir}")
        return
    
    logger.info("开始为分析文档添加元数据...")
    logger.info(f"原始数据目录: {raw_dir}")
    logger.info(f"分析数据目录: {analysis_dir}")
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    # 遍历所有分析文档
    for analysis_file in analysis_dir.rglob('*.md'):
        # 构建对应的原始文档路径
        relative_path = analysis_file.relative_to(analysis_dir)
        raw_file = raw_dir / relative_path
        
        if not raw_file.exists():
            logger.warning(f"找不到对应的原始文档: {raw_file}")
            error_count += 1
            continue
        
        # 添加元数据
        if add_metadata_to_analysis_file(str(analysis_file), str(raw_file)):
            updated_count += 1
        else:
            skipped_count += 1
    
    logger.info("\n" + "="*60)
    logger.info("处理完成！")
    logger.info(f"已更新: {updated_count} 个文件")
    logger.info(f"已跳过: {skipped_count} 个文件")
    logger.info(f"错误: {error_count} 个文件")
    logger.info("="*60)

if __name__ == '__main__':
    main()
