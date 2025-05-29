#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
访问日志迁移脚本

将现有的JSONL格式访问日志迁移到SQLite数据库。
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.access_log_db import AccessLogDB
from src.utils.colored_logger import setup_colored_logging

def main():
    """主函数"""
    # 设置日志
    setup_colored_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("开始访问日志迁移...")
    
    # 项目目录
    data_dir = project_root / "data"
    logs_dir = project_root / "logs"
    
    # JSONL文件路径
    main_jsonl = data_dir / "access_log_lines.jsonl"
    all_jsonl = logs_dir / "all_access_log_lines.jsonl"
    
    # SQLite数据库路径
    db_dir = data_dir / "sqlite"
    db_dir.mkdir(exist_ok=True)
    
    main_db_path = db_dir / "access_logs.db"
    all_db_path = logs_dir / "all_access_logs.db"
    
    # 初始化数据库
    logger.info("初始化SQLite数据库...")
    main_db = AccessLogDB(str(main_db_path))
    all_db = AccessLogDB(str(all_db_path))
    
    # 迁移主访问日志
    if main_jsonl.exists():
        logger.info(f"迁移主访问日志: {main_jsonl}")
        main_db.migrate_from_jsonl(str(main_jsonl))
        
        # 备份原文件
        backup_file = str(main_jsonl) + ".backup"
        if not os.path.exists(backup_file):
            os.rename(str(main_jsonl), backup_file)
            logger.info(f"已备份原文件到: {backup_file}")
    else:
        logger.info("主访问日志JSONL文件不存在，跳过迁移")
    
    # 迁移完整访问日志
    if all_jsonl.exists():
        logger.info(f"迁移完整访问日志: {all_jsonl}")
        all_db.migrate_from_jsonl(str(all_jsonl))
        
        # 备份原文件
        backup_file = str(all_jsonl) + ".backup"
        if not os.path.exists(backup_file):
            os.rename(str(all_jsonl), backup_file)
            logger.info(f"已备份原文件到: {backup_file}")
    else:
        logger.info("完整访问日志JSONL文件不存在，跳过迁移")
    
    # 显示迁移结果
    logger.info("迁移完成！数据库信息:")
    
    main_info = main_db.get_database_size()
    logger.info(f"主访问日志数据库: {main_info['total_records']} 条记录, {main_info['file_size_mb']} MB")
    
    all_info = all_db.get_database_size()
    logger.info(f"完整访问日志数据库: {all_info['total_records']} 条记录, {all_info['file_size_mb']} MB")
    
    logger.info("迁移完成！现在可以重启Web服务器以使用新的SQLite数据库。")

if __name__ == "__main__":
    main() 