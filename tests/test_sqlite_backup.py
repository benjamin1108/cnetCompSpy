#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SQLite备份功能的单元测试
"""

import os
import sys
import json
import unittest
import tempfile
import sqlite3
import logging
from unittest.mock import patch, MagicMock

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入被测试模块
from scripts.sqlite_backup import SQLiteBackup

class TestSQLiteBackup(unittest.TestCase):
    """测试SQLite备份功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录和文件
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # 创建临时SQLite数据库
        self.db_path = os.path.join(self.temp_dir.name, 'test.db')
        
        # 创建临时元数据目录和文件
        self.metadata_dir = os.path.join(self.temp_dir.name, 'metadata')
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        # 创建临时爬虫元数据文件
        self.crawler_metadata = {
            'test_vendor': {
                'test_source': {
                    '/path/to/file1.md': {
                        'title': 'Test Title 1',
                        'url': 'http://example.com/1',
                        'crawl_time': '2025-01-01T00:00:00',
                        'filepath': '/path/to/file1.md',
                        'vendor': 'test_vendor',
                        'source_type': 'test_source'
                    }
                }
            }
        }
        
        self.crawler_metadata_path = os.path.join(self.metadata_dir, 'crawler_metadata.json')
        with open(self.crawler_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.crawler_metadata, f)
        
        # 创建临时分析元数据文件
        self.analysis_metadata = {
            '/path/to/file1.md': {
                'file': '/path/to/analysis/file1.md',
                'last_analyzed': '2025-01-01 00:00:00',
                'tasks': {
                    'test_task': {
                        'success': True,
                        'error': None,
                        'timestamp': '2025-01-01 00:00:00'
                    }
                },
                'info': {
                    'title': 'Test Title 1',
                    'original_url': 'http://example.com/1',
                    'crawl_time': '2025-01-01',
                    'vendor': 'test_vendor',
                    'type': 'TEST'
                },
                'processed': True
            }
        }
        
        self.analysis_metadata_path = os.path.join(self.metadata_dir, 'analysis_metadata.json')
        with open(self.analysis_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_metadata, f)
        
        # 模拟配置
        self.mock_config = {
            'sqlite': {
                'db_path': self.db_path
            },
            'paths': {
                'metadata_dir': self.metadata_dir
            }
        }
        
    def tearDown(self):
        """测试后的清理工作"""
        # 清理临时目录
        self.temp_dir.cleanup()
    
    @patch('scripts.sqlite_backup.get_config')
    @patch('scripts.sqlite_backup.setup_colored_logging')
    @patch('scripts.sqlite_backup.logging.getLogger')
    def test_init_database(self, mock_get_logger, mock_setup_logging, mock_get_config):
        """测试初始化数据库"""
        # 设置模拟对象
        mock_get_config.return_value = self.mock_config
        mock_get_logger.return_value = MagicMock()
        
        # 创建SQLiteBackup实例
        backup = SQLiteBackup()
        backup.init_database()
        
        # 检查数据库表是否创建成功
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        # 验证表是否存在
        self.assertIn('raw_data', table_names)
        self.assertIn('analysis_data', table_names)
        self.assertIn('analysis_tasks', table_names)
        self.assertIn('raw_info', table_names)
        self.assertIn('backup_history', table_names)
        
        conn.close()
    
    @patch('scripts.sqlite_backup.get_config')
    @patch('scripts.sqlite_backup.setup_colored_logging')
    @patch('scripts.sqlite_backup.logging.getLogger')
    def test_backup_crawler_metadata(self, mock_get_logger, mock_setup_logging, mock_get_config):
        """测试备份爬虫元数据"""
        # 设置模拟对象
        mock_get_config.return_value = self.mock_config
        mock_get_logger.return_value = MagicMock()
        
        # 创建SQLiteBackup实例
        backup = SQLiteBackup()
        backup.init_database()
        
        # 备份爬虫元数据
        count = backup.backup_crawler_metadata()
        
        # 验证备份数量
        self.assertEqual(count, 1)
        
        # 验证数据是否正确备份
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM raw_data")
        raw_data = cursor.fetchall()
        
        self.assertEqual(len(raw_data), 1)
        
        conn.close()
    
    @patch('scripts.sqlite_backup.get_config')
    @patch('scripts.sqlite_backup.setup_colored_logging')
    @patch('scripts.sqlite_backup.logging.getLogger')
    def test_backup_analysis_metadata(self, mock_get_logger, mock_setup_logging, mock_get_config):
        """测试备份分析元数据"""
        # 设置模拟对象
        mock_get_config.return_value = self.mock_config
        mock_get_logger.return_value = MagicMock()
        
        # 创建SQLiteBackup实例
        backup = SQLiteBackup()
        backup.init_database()
        
        # 备份分析元数据
        count = backup.backup_analysis_metadata()
        
        # 验证备份数量
        self.assertEqual(count, 1)
        
        # 验证数据是否正确备份
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM analysis_data")
        analysis_data = cursor.fetchall()
        
        self.assertEqual(len(analysis_data), 1)
        
        cursor.execute("SELECT * FROM analysis_tasks")
        analysis_tasks = cursor.fetchall()
        
        self.assertEqual(len(analysis_tasks), 1)
        
        cursor.execute("SELECT * FROM raw_info")
        raw_info = cursor.fetchall()
        
        self.assertEqual(len(raw_info), 1)
        
        conn.close()
    
    @patch('scripts.sqlite_backup.get_config')
    @patch('scripts.sqlite_backup.setup_colored_logging')
    @patch('scripts.sqlite_backup.logging.getLogger')
    def test_run_backup(self, mock_get_logger, mock_setup_logging, mock_get_config):
        """测试运行完整备份流程"""
        # 设置模拟对象
        mock_get_config.return_value = self.mock_config
        mock_get_logger.return_value = MagicMock()
        
        # 创建SQLiteBackup实例
        backup = SQLiteBackup()
        
        # 运行完整备份流程
        success = backup.run_backup()
        
        # 验证备份是否成功
        self.assertTrue(success)
        
        # 验证备份历史是否记录
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM backup_history")
        history = cursor.fetchall()
        
        self.assertEqual(len(history), 1)
        
        conn.close()

if __name__ == '__main__':
    unittest.main() 