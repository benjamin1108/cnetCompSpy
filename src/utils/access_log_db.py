#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
访问日志数据库管理器

使用SQLite数据库存储访问日志，提供高性能的读写操作。
"""

import os
import sqlite3
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
import queue

# 导入项目的线程池工具
from src.utils.thread_pool import get_thread_pool

class AccessLogDB:
    """访问日志数据库管理器"""
    
    def __init__(self, db_path: str):
        """
        初始化访问日志数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self.lock = threading.RLock()
        
        # 异步写入相关
        self._async_enabled = True
        self._write_queue = queue.Queue()
        self._thread_pool = None
        self._batch_size = 5  # 减少批量写入大小，提高响应性
        self._batch_timeout = 1.0  # 减少批量写入超时时间（秒）
        
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 初始化数据库
        self._init_database()
        
        # 启动异步写入
        self._start_async_writer()
        
        self.logger.info(f"访问日志数据库初始化完成: {db_path}")
    
    def _init_database(self):
        """初始化数据库表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建访问日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER NOT NULL,
                    time TEXT NOT NULL,
                    date TEXT NOT NULL,
                    ip TEXT NOT NULL,
                    path TEXT NOT NULL,
                    method TEXT NOT NULL,
                    status_code INTEGER NOT NULL,
                    title TEXT,
                    user_agent TEXT,
                    device_type TEXT,
                    os TEXT,
                    browser TEXT,
                    is_bot INTEGER DEFAULT 0,
                    referer TEXT,
                    path_exists INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引以提高查询性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON access_logs(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON access_logs(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip ON access_logs(ip)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_path ON access_logs(path)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_path_exists ON access_logs(path_exists)')
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _start_async_writer(self):
        """启动异步写入线程"""
        if not self._async_enabled:
            return
            
        try:
            # 获取线程池实例（使用较低的API限制，因为这是数据库写入）
            self._thread_pool = get_thread_pool(
                api_rate_limit=300,  # 每分钟300次写入
                initial_threads=1,
                max_threads=2,
                monitor_interval=60
            )
            self._thread_pool.start()
            
            # 添加批量写入任务
            self._thread_pool.add_task(
                self._batch_writer_loop,
                task_meta={'identifier': 'AccessLogBatchWriter'}
            )
            
            self.logger.info("异步访问日志写入器已启动")
            
        except Exception as e:
            self.logger.error(f"启动异步写入器失败: {e}")
            self._async_enabled = False
    
    def _batch_writer_loop(self):
        """批量写入循环"""
        batch = []
        last_write_time = time.time()
        
        while True:
            try:
                # 尝试从队列获取数据
                try:
                    access_info = self._write_queue.get(timeout=0.5)
                    if access_info is None:  # 停止信号
                        break
                    batch.append(access_info)
                except queue.Empty:
                    pass
                
                current_time = time.time()
                
                # 检查是否需要写入批次
                should_write = (
                    len(batch) >= self._batch_size or
                    (batch and (current_time - last_write_time) >= self._batch_timeout)
                )
                
                if should_write and batch:
                    self._write_batch(batch)
                    batch.clear()
                    last_write_time = current_time
                    
            except Exception as e:
                self.logger.error(f"批量写入循环错误: {e}")
                time.sleep(1)
    
    def _write_batch(self, batch: List[Dict[str, Any]]):
        """批量写入访问记录到数据库"""
        if not batch:
            return
            
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # 准备批量插入数据
                    insert_data = []
                    for access_info in batch:
                        user_agent_info = access_info.get('user_agent_info', {})
                        insert_data.append((
                            access_info.get('timestamp', int(time.time())),
                            access_info.get('time', ''),
                            access_info.get('date', ''),
                            access_info.get('ip', ''),
                            access_info.get('path', ''),
                            access_info.get('method', ''),
                            access_info.get('status_code', 0),
                            access_info.get('title', ''),
                            access_info.get('user_agent', ''),
                            user_agent_info.get('device_type', ''),
                            user_agent_info.get('os', ''),
                            user_agent_info.get('browser', ''),
                            1 if user_agent_info.get('is_bot', False) else 0,
                            access_info.get('referer'),
                            1 if access_info.get('path_exists', True) else 0
                        ))
                    
                    # 批量插入
                    cursor.executemany('''
                        INSERT INTO access_logs (
                            timestamp, time, date, ip, path, method, status_code,
                            title, user_agent, device_type, os, browser, is_bot,
                            referer, path_exists
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', insert_data)
                    
                    conn.commit()
                    
                    self.logger.debug(f"批量写入 {len(batch)} 条访问记录")
                    
        except Exception as e:
            self.logger.error(f"批量写入访问记录失败: {e}")
    
    def record_access(self, access_info: Dict[str, Any], force_sync: bool = False):
        """
        记录访问信息到数据库
        
        Args:
            access_info: 访问信息字典
            force_sync: 是否强制同步写入，默认False（异步写入）
        """
        try:
            if force_sync or not self._async_enabled:
                # 同步写入
                self._write_batch([access_info])
            else:
                # 异步写入
                self._write_queue.put(access_info)
                
        except Exception as e:
            self.logger.error(f"记录访问信息失败: {e}")
            # 如果异步写入失败，尝试同步写入
            if not force_sync:
                try:
                    self._write_batch([access_info])
                except Exception as sync_e:
                    self.logger.error(f"同步写入也失败: {sync_e}")
    
    def flush_pending_writes(self):
        """刷新所有待写入的记录"""
        if not self._async_enabled:
            return
            
        try:
            # 等待队列清空
            start_time = time.time()
            while not self._write_queue.empty() and (time.time() - start_time) < 10:
                time.sleep(0.1)
                
            self.logger.info("已刷新所有待写入的访问记录")
            
        except Exception as e:
            self.logger.error(f"刷新待写入记录失败: {e}")
    
    def shutdown(self):
        """关闭异步写入器"""
        if not self._async_enabled or not self._thread_pool:
            return
            
        try:
            # 刷新待写入记录
            self.flush_pending_writes()
            
            # 发送停止信号
            self._write_queue.put(None)
            
            # 关闭线程池
            self._thread_pool.shutdown(wait=True)
            
            self.logger.info("异步访问日志写入器已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭异步写入器失败: {e}")
    
    def get_access_details(self, limit: int = 1000, include_non_existent: bool = True) -> List[Dict[str, Any]]:
        """
        获取访问详情
        
        Args:
            limit: 最大记录数
            include_non_existent: 是否包含不存在路径的访问
            
        Returns:
            访问详情列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建查询条件
                where_clause = ""
                if not include_non_existent:
                    where_clause = "WHERE path_exists = 1"
                
                cursor.execute(f'''
                    SELECT * FROM access_logs 
                    {where_clause}
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                
                # 转换为字典格式
                access_details = []
                for row in rows:
                    access_info = {
                        'time': row['time'],
                        'date': row['date'],
                        'ip': row['ip'],
                        'path': row['path'],
                        'method': row['method'],
                        'status_code': row['status_code'],
                        'title': row['title'],
                        'user_agent': row['user_agent'],
                        'user_agent_info': {
                            'device_type': row['device_type'],
                            'os': row['os'],
                            'browser': row['browser'],
                            'is_bot': bool(row['is_bot'])
                        },
                        'timestamp': row['timestamp'],
                        'referer': row['referer'],
                        'path_exists': bool(row['path_exists'])
                    }
                    access_details.append(access_info)
                
                return access_details
                
        except Exception as e:
            self.logger.error(f"获取访问详情失败: {e}")
            return []
    
    def get_access_stats(self) -> Dict[str, Any]:
        """
        获取访问统计数据
        
        Returns:
            访问统计数据字典
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 计算总PV和UV
                cursor.execute('SELECT COUNT(*) as total_pv FROM access_logs WHERE path_exists = 1')
                total_pv = cursor.fetchone()['total_pv']
                
                cursor.execute('SELECT COUNT(DISTINCT ip) as total_uv FROM access_logs WHERE path_exists = 1')
                total_uv = cursor.fetchone()['total_uv']
                
                # 计算今日PV和UV
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute('SELECT COUNT(*) as today_pv FROM access_logs WHERE date = ? AND path_exists = 1', (today,))
                today_pv = cursor.fetchone()['today_pv']
                
                cursor.execute('SELECT COUNT(DISTINCT ip) as today_uv FROM access_logs WHERE date = ? AND path_exists = 1', (today,))
                today_uv = cursor.fetchone()['today_uv']
                
                # 计算本周PV和UV
                week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
                cursor.execute('SELECT COUNT(*) as week_pv FROM access_logs WHERE date >= ? AND path_exists = 1', (week_start,))
                week_pv = cursor.fetchone()['week_pv']
                
                cursor.execute('SELECT COUNT(DISTINCT ip) as week_uv FROM access_logs WHERE date >= ? AND path_exists = 1', (week_start,))
                week_uv = cursor.fetchone()['week_uv']
                
                # 设备类型分布
                cursor.execute('''
                    SELECT device_type, COUNT(*) as count 
                    FROM access_logs 
                    WHERE path_exists = 1 AND device_type != ''
                    GROUP BY device_type
                ''')
                device_types = [{'name': row['device_type'], 'value': row['count']} for row in cursor.fetchall()]
                
                # 操作系统分布
                cursor.execute('''
                    SELECT os, COUNT(*) as count 
                    FROM access_logs 
                    WHERE path_exists = 1 AND os != ''
                    GROUP BY os
                ''')
                os_types = [{'name': row['os'], 'value': row['count']} for row in cursor.fetchall()]
                
                # 浏览器分布
                cursor.execute('''
                    SELECT browser, COUNT(*) as count 
                    FROM access_logs 
                    WHERE path_exists = 1 AND browser != ''
                    GROUP BY browser
                ''')
                browser_types = [{'name': row['browser'], 'value': row['count']} for row in cursor.fetchall()]
                
                # 最近30天PV趋势
                thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                cursor.execute('''
                    SELECT date, COUNT(*) as pv 
                    FROM access_logs 
                    WHERE date >= ? AND path_exists = 1
                    GROUP BY date 
                    ORDER BY date
                ''', (thirty_days_ago,))
                
                daily_pv_data = {row['date']: row['pv'] for row in cursor.fetchall()}
                
                # 填充缺失的日期
                daily_pv_trend = []
                for i in range(30):
                    date = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
                    pv = daily_pv_data.get(date, 0)
                    daily_pv_trend.append({'date': date, 'pv': pv})
                
                # 热门页面
                cursor.execute('''
                    SELECT title, COUNT(*) as views 
                    FROM access_logs 
                    WHERE path_exists = 1 AND title != ''
                    GROUP BY title 
                    ORDER BY views DESC 
                    LIMIT 10
                ''')
                top_pages = [{'title': row['title'], 'views': row['views']} for row in cursor.fetchall()]
                
                return {
                    'total_pv': total_pv,
                    'total_uv': total_uv,
                    'today_pv': today_pv,
                    'today_uv': today_uv,
                    'week_pv': week_pv,
                    'week_uv': week_uv,
                    'device_types': device_types,
                    'os_types': os_types,
                    'browser_types': browser_types,
                    'daily_pv_trend': daily_pv_trend,
                    'top_pages': top_pages,
                    'server_start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except Exception as e:
            self.logger.error(f"获取访问统计数据失败: {e}")
            return self._get_empty_stats()
    
    def _get_empty_stats(self) -> Dict[str, Any]:
        """返回空的统计数据"""
        return {
            'total_pv': 0,
            'total_uv': 0,
            'today_pv': 0,
            'today_uv': 0,
            'week_pv': 0,
            'week_uv': 0,
            'device_types': [],
            'os_types': [],
            'browser_types': [],
            'daily_pv_trend': [],
            'top_pages': [],
            'server_start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def migrate_from_jsonl(self, jsonl_file: str):
        """
        从JSONL文件迁移数据到SQLite数据库
        
        Args:
            jsonl_file: JSONL文件路径
        """
        if not os.path.exists(jsonl_file):
            self.logger.warning(f"JSONL文件不存在: {jsonl_file}")
            return
        
        try:
            migrated_count = 0
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            access_info = json.loads(line)
                            self.record_access(access_info)
                            migrated_count += 1
                        except json.JSONDecodeError:
                            continue
            
            self.logger.info(f"成功从 {jsonl_file} 迁移 {migrated_count} 条记录到数据库")
            
        except Exception as e:
            self.logger.error(f"从JSONL文件迁移数据失败: {e}")
    
    def cleanup_old_records(self, days: int = 90):
        """
        清理旧的访问记录
        
        Args:
            days: 保留天数，默认90天
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('DELETE FROM access_logs WHERE date < ?', (cutoff_date,))
                    deleted_count = cursor.rowcount
                    
                    conn.commit()
                    
                    self.logger.info(f"清理了 {deleted_count} 条超过 {days} 天的访问记录")
                    
        except Exception as e:
            self.logger.error(f"清理旧记录失败: {e}")
    
    def get_database_size(self) -> Dict[str, Any]:
        """
        获取数据库大小信息
        
        Returns:
            数据库大小信息字典
        """
        try:
            # 文件大小
            file_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 记录总数
                cursor.execute('SELECT COUNT(*) as total_records FROM access_logs')
                total_records = cursor.fetchone()['total_records']
                
                # 有效记录数（path_exists=1）
                cursor.execute('SELECT COUNT(*) as valid_records FROM access_logs WHERE path_exists = 1')
                valid_records = cursor.fetchone()['valid_records']
                
                return {
                    'file_size_bytes': file_size,
                    'file_size_mb': round(file_size / 1024 / 1024, 2),
                    'total_records': total_records,
                    'valid_records': valid_records,
                    'invalid_records': total_records - valid_records
                }
                
        except Exception as e:
            self.logger.error(f"获取数据库大小信息失败: {e}")
            return {
                'file_size_bytes': 0,
                'file_size_mb': 0,
                'total_records': 0,
                'valid_records': 0,
                'invalid_records': 0
            } 