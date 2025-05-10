#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SQLite查询工具
用于查询和导出SQLite数据库中的备份数据
"""

import os
import sys
import json
import argparse
import sqlite3
import logging
import datetime
import pandas as pd
from tabulate import tabulate

# 将项目根目录添加到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入项目配置加载器和日志模块
from src.utils.config_loader import get_config
from src.utils.colored_logger import setup_colored_logging

# 初始化配置和日志
config = get_config()
setup_colored_logging()
logger = logging.getLogger('sqlite_query')

class SQLiteQuery:
    """SQLite查询类，用于查询和导出备份数据"""
    
    def __init__(self):
        """初始化SQLite查询类"""
        db_path = config.get('sqlite', {}).get('db_path', 'data/sqlite/cnet_comp_spy.db')
        self.db_path = os.path.abspath(db_path)
        
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"SQLite数据库文件不存在: {self.db_path}")
        
        # 连接数据库
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def export_query_to_csv(self, query, output_file):
        """将查询结果导出为CSV文件"""
        try:
            df = pd.read_sql_query(query, self.conn)
            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"已将查询结果导出到: {output_file}")
            return True
        except Exception as e:
            logger.error(f"导出查询结果失败: {str(e)}")
            return False
    
    def execute_query(self, query):
        """执行SQL查询并返回结果"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        except Exception as e:
            logger.error(f"执行查询失败: {str(e)}")
            return []
    
    def print_table(self, results):
        """打印查询结果表格"""
        if not results:
            print("查询结果为空")
            return
        
        # 将查询结果转换为列表字典
        rows = [dict(row) for row in results]
        print(tabulate(rows, headers="keys", tablefmt="grid"))
    
    def get_backup_history(self):
        """获取备份历史记录"""
        query = "SELECT * FROM backup_history ORDER BY backup_time DESC"
        return self.execute_query(query)
    
    def get_raw_data_stats(self):
        """获取原始数据统计"""
        query = """
        SELECT vendor, source_type, COUNT(*) as count
        FROM raw_data
        GROUP BY vendor, source_type
        ORDER BY vendor, source_type
        """
        return self.execute_query(query)
    
    def get_analysis_stats(self):
        """获取分析数据统计"""
        query = """
        SELECT 
            (SELECT COUNT(*) FROM analysis_data) as total_analysis,
            (SELECT COUNT(*) FROM analysis_data WHERE processed = 1) as processed_analysis,
            (SELECT COUNT(*) FROM analysis_tasks WHERE success = 1) as successful_tasks,
            (SELECT COUNT(*) FROM analysis_tasks WHERE success = 0) as failed_tasks,
            (SELECT COUNT(*) FROM analysis_data WHERE content IS NOT NULL AND content != '') as with_content
        """
        return self.execute_query(query)
    
    def search_by_title(self, keyword):
        """根据标题搜索原始数据"""
        query = f"""
        SELECT id, filepath, vendor, source_type, title, url, crawl_time
        FROM raw_data
        WHERE title LIKE '%{keyword}%'
        ORDER BY crawl_time DESC
        """
        return self.execute_query(query)
    
    def get_tasks_by_filepath(self, filepath):
        """根据文件路径获取任务数据"""
        query = f"""
        SELECT task_name, success, error, timestamp
        FROM analysis_tasks
        WHERE raw_filepath = '{filepath}'
        ORDER BY timestamp DESC
        """
        return self.execute_query(query)
    
    def get_analysis_content(self, filepath):
        """获取分析文件内容"""
        query = f"""
        SELECT analysis_filepath, last_analyzed, content
        FROM analysis_data
        WHERE analysis_filepath = '{filepath}' OR raw_filepath = '{filepath}'
        """
        return self.execute_query(query)
    
    def export_analysis_content(self, filepath, output_file):
        """导出分析文件内容到文件"""
        result = self.get_analysis_content(filepath)
        
        if not result:
            logger.error(f"未找到文件: {filepath}")
            return False
        
        try:
            content = result[0]['content']
            
            if not content:
                logger.error(f"文件内容为空: {filepath}")
                return False
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"已将内容导出到: {output_file}")
            return True
        except Exception as e:
            logger.error(f"导出内容失败: {str(e)}")
            return False
    
    def search_analysis_content(self, keyword):
        """在分析文件内容中搜索关键词"""
        query = f"""
        SELECT analysis_filepath, raw_filepath
        FROM analysis_data
        WHERE content LIKE '%{keyword}%'
        """
        return self.execute_query(query)
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='SQLite查询工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 查询备份历史
    history_parser = subparsers.add_parser('history', help='查询备份历史')
    
    # 查询原始数据统计
    raw_stats_parser = subparsers.add_parser('raw_stats', help='查询原始数据统计')
    
    # 查询分析数据统计
    analysis_stats_parser = subparsers.add_parser('analysis_stats', help='查询分析数据统计')
    
    # 根据标题搜索
    search_parser = subparsers.add_parser('search', help='根据标题搜索')
    search_parser.add_argument('keyword', help='搜索关键词')
    
    # 根据文件路径查询任务
    tasks_parser = subparsers.add_parser('tasks', help='根据文件路径查询任务')
    tasks_parser.add_argument('filepath', help='文件路径')
    
    # 获取分析文件内容
    content_parser = subparsers.add_parser('content', help='获取分析文件内容')
    content_parser.add_argument('filepath', help='文件路径')
    content_parser.add_argument('--output', help='输出文件路径')
    
    # 在分析文件内容中搜索
    search_content_parser = subparsers.add_parser('search_content', help='在分析文件内容中搜索')
    search_content_parser.add_argument('keyword', help='搜索关键词')
    
    # 自定义SQL查询
    query_parser = subparsers.add_parser('query', help='自定义SQL查询')
    query_parser.add_argument('sql', help='SQL查询语句')
    query_parser.add_argument('--output', help='输出文件路径 (CSV格式)')
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    try:
        query = SQLiteQuery()
        
        if args.command == 'history':
            results = query.get_backup_history()
            query.print_table(results)
        
        elif args.command == 'raw_stats':
            results = query.get_raw_data_stats()
            query.print_table(results)
        
        elif args.command == 'analysis_stats':
            results = query.get_analysis_stats()
            query.print_table(results)
        
        elif args.command == 'search':
            results = query.search_by_title(args.keyword)
            query.print_table(results)
        
        elif args.command == 'tasks':
            results = query.get_tasks_by_filepath(args.filepath)
            query.print_table(results)
        
        elif args.command == 'content':
            if args.output:
                query.export_analysis_content(args.filepath, args.output)
            else:
                results = query.get_analysis_content(args.filepath)
                if results and results[0]['content']:
                    print(results[0]['content'])
                else:
                    print(f"未找到文件内容: {args.filepath}")
        
        elif args.command == 'search_content':
            results = query.search_analysis_content(args.keyword)
            query.print_table(results)
        
        elif args.command == 'query':
            results = query.execute_query(args.sql)
            
            if args.output:
                query.export_query_to_csv(args.sql, args.output)
            else:
                query.print_table(results)
        
        else:
            print("请指定一个命令。使用 -h 或 --help 查看帮助。")
        
        query.close()
        return 0
    
    except Exception as e:
        logger.error(f"执行查询时发生错误: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 