#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器 - 统计管理器

负责处理统计相关的功能，如分析元数据文件、获取缺失分析文件等。
"""

import os
import logging
import json
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from flask import request
import threading

# 导入SQLite访问日志数据库管理器
from src.utils.access_log_db import AccessLogDB

class StatsManager:
    """统计管理类"""
    
    def __init__(self, data_dir: str, enable_access_log: bool = True):
        """
        初始化统计管理器
        
        Args:
            data_dir: 数据目录路径
            enable_access_log: 是否启用访问日志记录，默认True
        """
        self.logger = logging.getLogger(__name__)
        
        self.data_dir = data_dir
        self.enable_access_log = enable_access_log
        
        # 如果禁用访问日志，跳过数据库初始化
        if not enable_access_log:
            self.logger.info("访问日志记录已禁用，跳过数据库初始化")
            self.main_access_db = None
            self.all_access_db = None
            self.server_start_time = datetime.now()
            self._user_agent_cache = {}
            self._user_agent_cache_lock = threading.RLock()
            self._max_cache_size = 1000
            return
        
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # 初始化SQLite数据库
        db_dir = os.path.join(data_dir, 'sqlite')
        os.makedirs(db_dir, exist_ok=True)
        
        # 主访问日志数据库（用于统计分析，不包含404等无效访问）
        self.main_db_path = os.path.join(db_dir, 'access_logs.db')
        self.main_access_db = AccessLogDB(self.main_db_path)
        
        # 完整访问日志数据库（包含所有访问记录）
        logs_dir = os.path.join(project_root, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        self.all_db_path = os.path.join(logs_dir, 'all_access_logs.db')
        self.all_access_db = AccessLogDB(self.all_db_path)
        
        # 兼容性：保留旧的文件路径用于迁移
        self.access_log_file = os.path.join(data_dir, 'access_log.json')
        self.all_access_log_file = os.path.join(logs_dir, 'all_access_log.json')
        self.access_log_lines_file = os.path.join(data_dir, 'access_log_lines.jsonl')
        self.all_access_log_lines_file = os.path.join(logs_dir, 'all_access_log_lines.jsonl')
        
        # 记录服务器启动时间
        self.server_start_time = datetime.now()
        
        # 用户代理解析缓存（提高性能）
        self._user_agent_cache = {}
        self._user_agent_cache_lock = threading.RLock()
        self._max_cache_size = 1000  # 最大缓存条目数
        
        # 迁移现有数据
        self._migrate_existing_data()
        
        self.logger.info("统计管理器初始化完成")
        self.logger.info(f"主访问日志数据库: {self.main_db_path}")
        self.logger.info(f"完整访问日志数据库: {self.all_db_path}")
    
    def _migrate_existing_data(self):
        """迁移现有的JSON/JSONL数据到SQLite数据库"""
        try:
            # 迁移主访问日志
            if os.path.exists(self.access_log_lines_file):
                self.logger.info("正在迁移主访问日志数据到SQLite数据库...")
                self.main_access_db.migrate_from_jsonl(self.access_log_lines_file)
                
                # 备份原文件
                backup_file = self.access_log_lines_file + '.backup'
                if not os.path.exists(backup_file):
                    os.rename(self.access_log_lines_file, backup_file)
                    self.logger.info(f"已备份原文件到: {backup_file}")
            
            # 迁移完整访问日志
            if os.path.exists(self.all_access_log_lines_file):
                self.logger.info("正在迁移完整访问日志数据到SQLite数据库...")
                self.all_access_db.migrate_from_jsonl(self.all_access_log_lines_file)
                
                # 备份原文件
                backup_file = self.all_access_log_lines_file + '.backup'
                if not os.path.exists(backup_file):
                    os.rename(self.all_access_log_lines_file, backup_file)
                    self.logger.info(f"已备份原文件到: {backup_file}")
                    
        except Exception as e:
            self.logger.error(f"迁移现有数据失败: {e}")
    
    def _parse_user_agent(self, user_agent_string: str) -> Dict[str, Any]:
        """
        解析用户代理字符串，优先使用 user-agents 库。
        使用缓存机制提高性能。
        
        Args:
            user_agent_string: 用户代理字符串
            
        Returns:
            解析后的用户代理信息字典，包含 device_type, os, browser, is_bot。
        """
        # 检查缓存
        with self._user_agent_cache_lock:
            if user_agent_string in self._user_agent_cache:
                return self._user_agent_cache[user_agent_string]
        
        device_type = 'Other'
        os_name = 'Unknown'
        browser_name = 'Unknown'
        is_bot = False
        
        try:
            # 尝试使用 user-agents 库
            from user_agents import parse
            user_agent = parse(user_agent_string)
            
            # 设备类型
            if user_agent.is_mobile:
                device_type = 'Mobile'
            elif user_agent.is_tablet:
                device_type = 'Tablet'
            elif user_agent.is_pc:
                device_type = 'PC'
            else:
                device_type = 'Other'
            
            # 操作系统
            if user_agent.os.family:
                os_name = f"{user_agent.os.family}"
                if user_agent.os.version_string:
                    os_name += f" {user_agent.os.version_string}"
            
            # 浏览器
            if user_agent.browser.family:
                browser_name = f"{user_agent.browser.family}"
                if user_agent.browser.version_string:
                    browser_name += f" {user_agent.browser.version_string}"
            
            # 是否为机器人
            is_bot = user_agent.is_bot
            
        except ImportError:
            # 如果没有安装 user-agents 库，使用简单的字符串匹配
            user_agent_lower = user_agent_string.lower()
            
            # 简单的设备类型检测
            if any(mobile in user_agent_lower for mobile in ['mobile', 'android', 'iphone', 'ipad']):
                if 'ipad' in user_agent_lower:
                    device_type = 'Tablet'
                else:
                    device_type = 'Mobile'
            else:
                device_type = 'PC'
            
            # 简单的操作系统检测
            if 'windows' in user_agent_lower:
                os_name = 'Windows'
            elif 'mac' in user_agent_lower or 'darwin' in user_agent_lower:
                os_name = 'macOS'
            elif 'linux' in user_agent_lower:
                os_name = 'Linux'
            elif 'android' in user_agent_lower:
                os_name = 'Android'
            elif 'ios' in user_agent_lower or 'iphone' in user_agent_lower or 'ipad' in user_agent_lower:
                os_name = 'iOS'
            
            # 简单的浏览器检测
            if 'chrome' in user_agent_lower:
                browser_name = 'Chrome'
            elif 'firefox' in user_agent_lower:
                browser_name = 'Firefox'
            elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
                browser_name = 'Safari'
            elif 'edge' in user_agent_lower:
                browser_name = 'Edge'
            
            # 简单的机器人检测
            bot_indicators = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget']
            is_bot = any(indicator in user_agent_lower for indicator in bot_indicators)
        
        except Exception as e:
            self.logger.error(f"解析用户代理失败: {e}")
        
        result = {
            'device_type': device_type,
            'os': os_name,
            'browser': browser_name,
            'is_bot': is_bot
        }
        
        # 添加到缓存
        with self._user_agent_cache_lock:
            # 如果缓存已满，清理一半的条目
            if len(self._user_agent_cache) >= self._max_cache_size:
                # 简单的LRU策略：删除前一半的条目
                cache_items = list(self._user_agent_cache.items())
                self._user_agent_cache = dict(cache_items[len(cache_items)//2:])
            
            self._user_agent_cache[user_agent_string] = result
        
        return result
    
    def _get_document_title(self, path: str, document_manager = None) -> str:
        """
        获取文档标题
        
        Args:
            path: 请求路径
            document_manager: 文档管理器实例
            
        Returns:
            文档标题或路径
        """
        if not document_manager:
            return path
        
        try:
            # 如果是分析文档路径，尝试获取文档标题
            if path.startswith('/analysis/document/'):
                # 提取文档路径参数：vendor/doc_type/filename
                doc_path = path.replace('/analysis/document/', '')
                path_parts = doc_path.split('/')
                
                if len(path_parts) >= 3:
                    vendor = path_parts[0]
                    doc_type = path_parts[1]
                    filename = '/'.join(path_parts[2:])  # 支持文件名中包含斜杠
                    
                    # 获取分析文档信息
                    analysis_info = document_manager.get_analysis_document(vendor, doc_type, filename)
                    if analysis_info and 'title' in analysis_info:
                        return analysis_info['title']
            
            # 如果是原始文档路径，尝试获取文档标题
            elif path.startswith('/document/'):
                # 提取文档路径参数：vendor/doc_type/filename
                doc_path = path.replace('/document/', '')
                path_parts = doc_path.split('/')
                
                if len(path_parts) >= 3:
                    vendor = path_parts[0]
                    doc_type = path_parts[1]
                    filename = '/'.join(path_parts[2:])  # 支持文件名中包含斜杠
                    
                    # 获取原始文档信息
                    doc_info = document_manager.get_document(vendor, doc_type, filename)
                    if doc_info and 'meta' in doc_info and 'title' in doc_info['meta']:
                        return doc_info['meta']['title']
            
            return path
        except Exception as e:
            self.logger.error(f"获取文档标题失败: {e}")
            return path
    
    def record_access(self, path: str = None, document_manager = None, path_exists: bool = True, response_obj = None):
        """
        记录访问详情
        
        Args:
            path: 请求路径，如果为None则使用当前请求的路径
            document_manager: 文档管理器实例，用于获取文档标题
            path_exists: 路径是否存在，不存在的路径（扫描访问）不会记录到主统计中
            response_obj: Flask响应对象，用于获取状态码
        """
        # 如果访问日志被禁用，直接返回
        if not self.enable_access_log or not self.main_access_db or not self.all_access_db:
            return
            
        try:
            if not path and request:
                path = request.path
            else:
                path = path or 'unknown'
            
            status_code_val = 'N/A'
            if response_obj:
                status_code_val = response_obj.status_code
            elif not path_exists:
                status_code_val = 404

            # 快速检查是否需要记录（提前过滤静态文件）
            is_static = path and (path.startswith('/static/') or path == '/favicon.ico')
            
            # 获取基本访问信息（避免不必要的计算）
            current_time = datetime.now()
            user_agent = request.headers.get('User-Agent', 'unknown') if request else 'unknown'
            
            access_info = {
                'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'date': current_time.strftime('%Y-%m-%d'),
                'ip': request.remote_addr if request else 'unknown',
                'path': path,
                'method': request.method if request else 'unknown',
                'status_code': status_code_val,
                'title': '',  # 延迟计算标题
                'user_agent': user_agent,
                'user_agent_info': {},  # 延迟解析用户代理
                'timestamp': int(time.time()),
                'referer': request.referrer if request else None,
                'path_exists': path_exists
            }
            
            # 始终记录到完整访问日志数据库（使用基本信息）
            self.all_access_db.record_access(access_info)
            
            # 如果路径不存在 (e.g., 404)
            if not path_exists:
                # 只在DEBUG级别记录404，减少日志输出
                self.logger.debug(
                    f"404访问 - IP: {access_info['ip']}, Path: {access_info['path']}"
                )
                return
            
            # 如果是静态文件或favicon，不记录到主统计日志
            if is_static:
                return
            
            # 只有对于需要记录到主数据库的请求，才进行详细计算
            access_info['title'] = self._get_document_title(path, document_manager)
            access_info['user_agent_info'] = self._parse_user_agent(user_agent)
            
            # 对于合法的、非静态/favicon的请求，记录到主访问日志数据库
            self.main_access_db.record_access(access_info)
            
            # 只在DEBUG级别记录详细访问信息，减少日志输出
            self.logger.debug(
                f"访问记录 - IP: {access_info['ip']}, Path: {access_info['path']}, Status: {access_info['status_code']}"
            )
            
        except Exception as e:
            self.logger.error(f"记录访问详情失败: {e}")
    
    def get_access_details(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        获取访问详情
        
        Args:
            limit: 最大记录数，默认1000
            
        Returns:
            访问详情列表
        """
        # 如果访问日志被禁用，返回空列表
        if not self.enable_access_log or not self.main_access_db:
            return []
            
        try:
            return self.main_access_db.get_access_details(limit=limit, include_non_existent=False)
        except Exception as e:
            self.logger.error(f"获取访问详情失败: {e}")
            return []
    
    def get_all_access_details(self, limit: int = 1000, include_non_existent: bool = True) -> List[Dict[str, Any]]:
        """
        获取完整访问详情
        
        Args:
            limit: 最大记录数，默认1000
            include_non_existent: 是否包含不存在路径的访问，默认True
            
        Returns:
            访问详情列表
        """
        # 如果访问日志被禁用，返回空列表
        if not self.enable_access_log or not self.all_access_db:
            return []
            
        try:
            return self.all_access_db.get_access_details(limit=limit, include_non_existent=include_non_existent)
        except Exception as e:
            self.logger.error(f"获取完整访问详情失败: {e}")
            return []
    
    def get_access_stats(self) -> Dict[str, Any]:
        """
        获取访问统计数据
        
        Returns:
            访问统计数据，包括PV、UV、设备类型分布等
        """
        # 如果访问日志被禁用，返回空统计数据
        if not self.enable_access_log or not self.main_access_db:
            return self._get_empty_stats()
            
        try:
            stats = self.main_access_db.get_access_stats()
            # 添加服务器启动时间
            stats['server_start_time'] = self.server_start_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 使用数据库查询计算服务器启动后的PV、UV，而不是获取大量记录
            start_timestamp = int(self.server_start_time.timestamp())
            try:
                with self.main_access_db._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # 计算服务器启动后的PV
                    cursor.execute(
                        'SELECT COUNT(*) as server_start_pv FROM access_logs WHERE timestamp >= ? AND path_exists = 1',
                        (start_timestamp,)
                    )
                    stats['server_start_pv'] = cursor.fetchone()['server_start_pv']
                    
                    # 计算服务器启动后的UV
                    cursor.execute(
                        'SELECT COUNT(DISTINCT ip) as server_start_uv FROM access_logs WHERE timestamp >= ? AND path_exists = 1',
                        (start_timestamp,)
                    )
                    stats['server_start_uv'] = cursor.fetchone()['server_start_uv']
                    
            except Exception as db_e:
                self.logger.error(f"计算服务器启动后统计数据失败: {db_e}")
                stats['server_start_pv'] = 0
                stats['server_start_uv'] = 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取访问统计数据失败: {e}")
            return self._get_empty_stats()
    
    def _get_empty_stats(self) -> Dict[str, Any]:
        """返回空的统计数据"""
        return {
            'total_pv': 0,
            'total_uv': 0,
            'server_start_pv': 0,
            'server_start_uv': 0,
            'today_pv': 0,
            'today_uv': 0,
            'week_pv': 0,
            'week_uv': 0,
            'device_types': [],
            'os_types': [],
            'browser_types': [],
            'daily_pv_trend': [],
            'top_pages': [],
            'server_start_time': self.server_start_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        获取数据库信息
        
        Returns:
            数据库信息字典
        """
        try:
            main_db_info = self.main_access_db.get_database_size()
            all_db_info = self.all_access_db.get_database_size()
            
            return {
                'main_database': {
                    'path': self.main_db_path,
                    'size_mb': main_db_info['file_size_mb'],
                    'total_records': main_db_info['total_records'],
                    'valid_records': main_db_info['valid_records']
                },
                'all_database': {
                    'path': self.all_db_path,
                    'size_mb': all_db_info['file_size_mb'],
                    'total_records': all_db_info['total_records'],
                    'valid_records': all_db_info['valid_records'],
                    'invalid_records': all_db_info['invalid_records']
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取数据库信息失败: {e}")
            return {}
    
    def cleanup_old_records(self, days: int = 90):
        """
        清理旧的访问记录
        
        Args:
            days: 保留天数，默认90天
        """
        try:
            self.main_access_db.cleanup_old_records(days)
            self.all_access_db.cleanup_old_records(days)
            self.logger.info(f"已清理超过 {days} 天的访问记录")
        except Exception as e:
            self.logger.error(f"清理旧记录失败: {e}")
    
    def analyze_metadata_files(self, detailed: bool = False) -> Dict[str, Any]:
        """
        分析metadata和文件差异
        
        Args:
            detailed: 是否返回详细信息
            
        Returns:
            分析结果
        """
        from src.utils.stats_analyzer import StatsAnalyzer
        
        # 创建统计分析器
        analyzer = StatsAnalyzer(base_dir=os.path.dirname(self.data_dir))
        
        # 分析数据
        return analyzer.generate_json_data(detailed)
    
    def get_missing_analysis_files(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        获取缺失AI分析的文件
        
        Returns:
            Dict: 按厂商和类型分组的缺失AI分析的文件列表
        """
        # 获取统计数据
        stats_data = self.analyze_metadata_files(detailed=True)
        
        # 提取缺失AI分析的文件
        missing_analysis = {}
        
        for vendor, vendor_data in stats_data.get('details', {}).items():
            for source_type, files in vendor_data.items():
                for file_info in files:
                    # 如果文件没有AI分析或者AI任务未完成
                    if not file_info.get('has_analysis') or not file_info.get('tasks_completed'):
                        if vendor not in missing_analysis:
                            missing_analysis[vendor] = {}
                        
                        if source_type not in missing_analysis[vendor]:
                            missing_analysis[vendor][source_type] = []
                        
                        missing_analysis[vendor][source_type].append({
                            'filename': file_info['filename'],
                            'title': file_info.get('title', file_info['filename']),
                            'has_analysis': file_info.get('has_analysis', False),
                            'tasks_completed': file_info.get('tasks_completed', False),
                            'path': f"{vendor}/{source_type}/{file_info['filename']}"
                        })
        
        return missing_analysis
    
    def shutdown(self):
        """
        关闭统计管理器，确保所有待写入的记录都被保存
        """
        # 如果访问日志被禁用，无需关闭数据库
        if not self.enable_access_log or not self.main_access_db or not self.all_access_db:
            self.logger.info("访问日志已禁用，跳过关闭操作")
            return
            
        try:
            self.logger.info("正在关闭统计管理器...")
            
            # 刷新所有待写入的记录
            self.main_access_db.flush_pending_writes()
            self.all_access_db.flush_pending_writes()
            
            # 关闭异步写入器
            self.main_access_db.shutdown()
            self.all_access_db.shutdown()
            
            self.logger.info("统计管理器已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭统计管理器失败: {e}")
