#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SQLite备份脚本
用于将文件系统中的数据备份到SQLite数据库中
不改变现有的数据读写逻辑，只作为数据备份
"""

import os
import sys
import json
import sqlite3
import logging
import datetime
from pathlib import Path

# 将项目根目录添加到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入项目配置加载器和日志模块
from src.utils.config_loader import get_config
from src.utils.colored_logger import setup_colored_logging

# 初始化配置和日志
config = get_config()
setup_colored_logging()
logger = logging.getLogger('sqlite_backup')

class SQLiteBackup:
    """SQLite备份类，负责将文件系统数据备份到SQLite数据库中"""
    
    def __init__(self):
        """初始化SQLite备份类"""
        db_path = config.get('sqlite', {}).get('db_path', 'data/sqlite/cnet_comp_spy.db')
        self.db_path = os.path.abspath(db_path)
        self.db_dir = os.path.dirname(self.db_path)
        
        # 确保数据库目录存在
        os.makedirs(self.db_dir, exist_ok=True)
        
        # 连接数据库
        self.conn = self._connect_db()
        
        # 源数据路径
        self.raw_dir = os.path.abspath(config.get('paths', {}).get('raw_data_dir', 'data/raw'))
        self.analysis_dir = os.path.abspath(config.get('paths', {}).get('analysis_data_dir', 'data/analysis'))
        self.metadata_dir = os.path.abspath(config.get('paths', {}).get('metadata_dir', 'data/metadata'))
        
    def _connect_db(self):
        """连接数据库"""
        logger.info(f"连接数据库: {self.db_path}")
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库，创建表结构"""
        logger.info("初始化数据库表结构")
        cursor = self.conn.cursor()
        
        # 创建Raw数据表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT UNIQUE,
            vendor TEXT,
            source_type TEXT,
            title TEXT,
            url TEXT,
            crawl_time TIMESTAMP,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建Analysis数据表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_filepath TEXT,
            analysis_filepath TEXT UNIQUE,
            last_analyzed TIMESTAMP,
            processed BOOLEAN,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (raw_filepath) REFERENCES raw_data(filepath)
        )
        ''')
        
        # 检查analysis_data表是否已存在且需要增加content列
        cursor.execute("PRAGMA table_info(analysis_data)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # 如果表已存在但没有content列，则添加它
        if 'content' not in column_names:
            try:
                logger.info("在analysis_data表中添加content字段")
                cursor.execute("ALTER TABLE analysis_data ADD COLUMN content TEXT")
            except sqlite3.OperationalError as e:
                # 如果发生错误(例如列已存在)，记录但继续执行
                logger.warning(f"添加content列时出错: {e}")
        
        # 创建Analysis任务表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_filepath TEXT,
            task_name TEXT,
            success BOOLEAN,
            error TEXT,
            timestamp TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (raw_filepath) REFERENCES raw_data(filepath),
            UNIQUE(raw_filepath, task_name)
        )
        ''')
        
        # 创建Raw信息表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_filepath TEXT UNIQUE,
            title TEXT,
            original_url TEXT,
            crawl_time TEXT,
            vendor TEXT,
            type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (raw_filepath) REFERENCES raw_data(filepath)
        )
        ''')
        
        # 创建备份记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS backup_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            backup_time TIMESTAMP,
            raw_count INTEGER,
            analysis_count INTEGER,
            status TEXT,
            message TEXT
        )
        ''')
        
        self.conn.commit()
        logger.info("数据库表结构初始化完成")
    
    def _fix_analysis_filepath(self, raw_path):
        """修复分析文件路径，将data/raw/替换为data/analysis/"""
        if raw_path and raw_path.startswith('data/raw/'):
            return raw_path.replace('data/raw/', 'data/analysis/', 1)
        return raw_path
        
    def backup_crawler_metadata(self):
        """备份爬虫元数据到SQLite"""
        logger.info("开始备份爬虫元数据")
        
        metadata_file = os.path.join(self.metadata_dir, 'crawler_metadata.json')
        if not os.path.exists(metadata_file):
            logger.error(f"爬虫元数据文件不存在: {metadata_file}")
            return 0
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            cursor = self.conn.cursor()
            count = 0
            
            for vendor, source_types in metadata.items():
                for source_type, items in source_types.items():
                    for filepath, item in items.items():
                        # 读取原始文件内容
                        content = ""
                        raw_filepath = item.get('filepath')
                        if raw_filepath and os.path.exists(raw_filepath):
                            try:
                                with open(raw_filepath, 'r', encoding='utf-8') as f:
                                    content = f.read()
                            except Exception as e:
                                logger.warning(f"读取文件 {raw_filepath} 失败: {str(e)}")
                        
                        # 插入数据
                        cursor.execute('''
                        INSERT OR REPLACE INTO raw_data 
                        (filepath, vendor, source_type, title, url, crawl_time, content)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            filepath,
                            vendor,
                            source_type,
                            item.get('title', ''),
                            item.get('url', ''),
                            item.get('crawl_time', ''),
                            content
                        ))
                        count += 1
            
            self.conn.commit()
            logger.info(f"成功备份 {count} 条爬虫元数据")
            return count
        except Exception as e:
            logger.error(f"备份爬虫元数据失败: {str(e)}")
            return 0
    
    def backup_analysis_metadata(self):
        """备份分析元数据到SQLite"""
        logger.info("开始备份分析元数据")
        
        metadata_file = os.path.join(self.metadata_dir, 'analysis_metadata.json')
        if not os.path.exists(metadata_file):
            logger.error(f"分析元数据文件不存在: {metadata_file}")
            return 0
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            cursor = self.conn.cursor()
            count = 0
            tasks_count = 0
            analysis_files_count = 0
            failed_files_count = 0
            
            for raw_filepath, item in metadata.items():
                # 获取并修复分析文件路径
                original_path = item.get('file', '')
                analysis_filepath = self._fix_analysis_filepath(original_path)
                
                # 读取分析文件内容
                content = ""
                if analysis_filepath and os.path.exists(analysis_filepath):
                    try:
                        with open(analysis_filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        analysis_files_count += 1
                        logger.debug(f"成功读取分析文件: {analysis_filepath}")
                    except Exception as e:
                        logger.warning(f"读取分析文件 {analysis_filepath} 失败: {str(e)}")
                        failed_files_count += 1
                elif analysis_filepath != original_path:
                    logger.debug(f"分析文件路径已修复但文件不存在: {analysis_filepath}")
                    failed_files_count += 1
                else:
                    logger.debug(f"分析文件不存在且无法修复路径: {original_path}")
                    failed_files_count += 1
                
                # 插入分析数据
                cursor.execute('''
                INSERT OR REPLACE INTO analysis_data 
                (raw_filepath, analysis_filepath, last_analyzed, processed, content)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    raw_filepath,
                    analysis_filepath,
                    item.get('last_analyzed', ''),
                    1 if item.get('processed', False) else 0,
                    content
                ))
                count += 1
                
                # 插入任务数据
                if 'tasks' in item:
                    for task_name, task_info in item['tasks'].items():
                        cursor.execute('''
                        INSERT OR REPLACE INTO analysis_tasks 
                        (raw_filepath, task_name, success, error, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                        ''', (
                            raw_filepath,
                            task_name,
                            1 if task_info.get('success', False) else 0,
                            task_info.get('error', ''),
                            task_info.get('timestamp', '')
                        ))
                        tasks_count += 1
                
                # 插入Raw信息
                if 'info' in item:
                    cursor.execute('''
                    INSERT OR REPLACE INTO raw_info 
                    (raw_filepath, title, original_url, crawl_time, vendor, type)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        raw_filepath,
                        item['info'].get('title', ''),
                        item['info'].get('original_url', ''),
                        item['info'].get('crawl_time', ''),
                        item['info'].get('vendor', ''),
                        item['info'].get('type', '')
                    ))
            
            self.conn.commit()
            logger.info(f"成功备份 {count} 条分析元数据和 {tasks_count} 条任务数据")
            logger.info(f"成功备份 {analysis_files_count} 个分析文件内容 (失败: {failed_files_count})")
            return count
        except Exception as e:
            logger.error(f"备份分析元数据失败: {str(e)}")
            return 0
    
    def record_backup_history(self, raw_count, analysis_count, status="完成", message=""):
        """记录备份历史"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO backup_history 
            (backup_time, raw_count, analysis_count, status, message)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                raw_count,
                analysis_count,
                status,
                message
            ))
            self.conn.commit()
            logger.info("备份历史记录成功")
        except Exception as e:
            logger.error(f"记录备份历史失败: {str(e)}")
    
    def run_backup(self):
        """运行完整备份流程"""
        logger.info("开始数据备份到SQLite")
        
        try:
            # 初始化数据库
            self.init_database()
            
            # 备份爬虫元数据
            raw_count = self.backup_crawler_metadata()
            
            # 备份分析元数据
            analysis_count = self.backup_analysis_metadata()
            
            # 记录备份历史
            self.record_backup_history(raw_count, analysis_count)
            
            logger.info("SQLite数据备份完成")
            return True
        except Exception as e:
            logger.error(f"数据备份失败: {str(e)}")
            self.record_backup_history(0, 0, "失败", str(e))
            return False
        finally:
            self.close()
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")

def main():
    """主函数"""
    logger.info("开始SQLite备份")
    try:
        backup = SQLiteBackup()
        success = backup.run_backup()
        if success:
            logger.info("SQLite备份成功完成")
            return 0
        else:
            logger.error("SQLite备份失败")
            return 1
    except Exception as e:
        logger.error(f"SQLite备份过程中发生错误: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 