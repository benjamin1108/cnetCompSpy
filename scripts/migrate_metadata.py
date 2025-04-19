#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging

# 添加项目根目录到路径
base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, base_dir)

from src.utils.metadata_manager import MetadataManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """迁移旧的元数据文件到新的聚合文件"""
    logger.info("开始迁移元数据文件...")
    
    # 创建元数据管理器
    metadata_manager = MetadataManager()
    
    # 迁移元数据
    metadata_manager.migrate_legacy_metadata()
    
    logger.info("元数据迁移完成")

if __name__ == "__main__":
    main()
