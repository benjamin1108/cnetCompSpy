#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复分析文件metadata格式问题

修复metadata值前面的多余星号和空格
例如：**发布时间:** ** 2025-09-18 -> **发布时间:** 2025-09-18
"""

import os
import re
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fix_file(filepath: str) -> bool:
    """
    修复单个文件的metadata格式
    
    Returns:
        True if file was modified, False otherwise
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否需要修复
        if ':** **' not in content and ':** *' not in content:
            return False
        
        # 修复metadata格式
        # 匹配模式：**字段:** ** 值 或 **字段:** * 值
        fixed_content = re.sub(
            r'(\*\*[^:]+:\*\*)\s+\*+\s+',  # 匹配 **字段:** ** 或 **字段:** *
            r'\1 ',  # 替换为 **字段:** 
            content
        )
        
        if fixed_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"处理文件失败: {filepath} - {e}")
        return False


def main():
    """主函数"""
    base_dir = os.getcwd()
    analysis_dir = os.path.join(base_dir, 'data', 'analysis')
    
    if not os.path.exists(analysis_dir):
        logger.error(f"分析目录不存在: {analysis_dir}")
        return 1
    
    logger.info("开始修复metadata格式问题...")
    logger.info(f"分析目录: {analysis_dir}\n")
    
    # 扫描所有分析文件
    analysis_files = []
    for root, dirs, files in os.walk(analysis_dir):
        for file in files:
            if file.endswith('.md'):
                analysis_files.append(os.path.join(root, file))
    
    logger.info(f"找到 {len(analysis_files)} 个分析文件\n")
    
    # 修复每个文件
    fixed_count = 0
    for i, filepath in enumerate(analysis_files, 1):
        if i % 50 == 0:
            logger.info(f"进度: {i}/{len(analysis_files)}")
        
        if fix_file(filepath):
            fixed_count += 1
            logger.debug(f"已修复: {os.path.relpath(filepath, base_dir)}")
    
    # 输出统计信息
    logger.info("\n" + "="*60)
    logger.info("修复完成统计:")
    logger.info(f"  总文件数: {len(analysis_files)}")
    logger.info(f"  已修复: {fixed_count}")
    logger.info(f"  无需修复: {len(analysis_files) - fixed_count}")
    logger.info("="*60)
    
    return 0


if __name__ == "__main__":
    exit(main())
