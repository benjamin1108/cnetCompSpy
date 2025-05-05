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

class StatsManager:
    """统计管理类"""
    
    def __init__(self, data_dir: str):
        """
        初始化统计管理器
        
        Args:
            data_dir: 数据目录路径
        """
        self.logger = logging.getLogger(__name__)
        # 移除强制设置级别，级别将由统一配置决定
        # self.logger.setLevel(logging.DEBUG)
        
        self.data_dir = data_dir
        self.access_log_file = os.path.join(data_dir, 'access_log.json')
        
        # 修改: 使用项目根目录下的logs文件夹，而不是相对路径
        # 获取当前脚本的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 项目根目录是web_server的父目录的父目录
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.log_dir = os.path.join(project_root, 'logs')
        self.all_access_log_file = os.path.join(self.log_dir, 'all_access_log.json')
        
        # 确保访问日志文件存在
        self._ensure_access_log_file()
        self._ensure_all_access_log_file()
        
        # 记录服务器启动时间
        self.server_start_time = datetime.now()
        
        self.logger.info("统计管理器初始化完成")
        self.logger.info(f"日志目录: {self.log_dir}")
        self.logger.info(f"访问日志文件: {self.access_log_file}")
        self.logger.info(f"完整访问日志文件: {self.all_access_log_file}")
    
    def _ensure_access_log_file(self):
        """确保访问日志文件存在"""
        if not os.path.exists(os.path.dirname(self.access_log_file)):
            os.makedirs(os.path.dirname(self.access_log_file), exist_ok=True)
        
        if not os.path.exists(self.access_log_file):
            with open(self.access_log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
            self.logger.info(f"已创建访问日志文件: {self.access_log_file}")
    
    def _ensure_all_access_log_file(self):
        """确保完整访问日志文件存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
        
        if not os.path.exists(self.all_access_log_file):
            with open(self.all_access_log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
            self.logger.info(f"已创建完整访问日志文件: {self.all_access_log_file}")
    
    def _parse_user_agent(self, user_agent_string: str) -> Dict[str, Any]:
        """
        解析用户代理字符串，优先使用 user-agents 库。
        
        Args:
            user_agent_string: 用户代理字符串
            
        Returns:
            解析后的用户代理信息字典，包含 device_type, os, browser, is_bot。
        """
        device_type = 'Other'
        os_name = 'Unknown'
        browser_name = 'Unknown'
        is_bot = False
        
        # 尝试使用 user-agents 库解析
        try:
            from user_agents import parse as ua_parse
            ua = ua_parse(user_agent_string)
            
            if ua:
                # 使用库的解析结果
                if ua.is_bot:
                    device_type = 'Bot'
                    is_bot = True
                    # 对于 Bot，OS 和 Browser 可能意义不大，可以保留 Unknown 或尝试获取
                    os_name = f"{ua.os.family.strip()} {ua.os.version_string.strip()}".strip() if ua.os.family else 'Unknown'
                    browser_name = f"{ua.browser.family.strip()} {ua.browser.version_string.strip()}".strip() if ua.browser.family else 'Unknown'
                elif ua.is_mobile:
                    device_type = 'Mobile'
                elif ua.is_tablet:
                    device_type = 'Tablet'
                elif ua.is_pc:
                    device_type = 'PC'
                    # else: device_type 保持 'Other'
                
                # 如果不是 Bot，则填充 OS 和浏览器信息
                if not is_bot:
                    os_name = f"{ua.os.family.strip()} {ua.os.version_string.strip()}".strip() if ua.os.family else 'Unknown'
                    browser_name = f"{ua.browser.family.strip()} {ua.browser.version_string.strip()}".strip() if ua.browser.family else 'Unknown'
                    
                # 修正可能的空字符串结果
                if not os_name: os_name = 'Unknown'
                if not browser_name: browser_name = 'Unknown'
                
                # 成功解析，直接返回结果
                return {
                    'device_type': device_type,
                    'os': os_name,
                    'browser': browser_name,
                    'is_bot': is_bot
                }

        except ImportError:
            self.logger.warning("user-agents 库未安装，将使用基础字符串匹配。 pip install user-agents")
        except Exception as e:
            self.logger.warning(f"使用 user-agents 库解析失败: {e}，将使用基础字符串匹配。")

        # 如果 user-agents 库解析失败或不可用，执行基础字符串匹配作为回退
        try:
            lower_ua = user_agent_string.lower()
            is_bot = 'bot' in lower_ua # 简单判断是否是 bot
            
            if is_bot:
                device_type = 'Bot'
                # os 和 browser 保持 Unknown
            elif any(keyword in lower_ua for keyword in ['mobile', 'android', 'iphone', 'ipod']):
                device_type = 'Mobile'
            elif any(keyword in lower_ua for keyword in ['ipad', 'tablet']):
                device_type = 'Tablet'
            elif any(keyword in lower_ua for keyword in ['windows', 'macintosh', 'linux', 'x11']):
                 device_type = 'PC'
            # else: device_type 保持 'Other'

            # 对于回退逻辑，不再尝试猜测 OS 和浏览器，保持 Unknown
            # 这样可以避免之前 "Other " 的问题
            os_name = 'Unknown'
            browser_name = 'Unknown'
            
        except Exception as e:
             self.logger.error(f"基础字符串匹配解析用户代理失败: {e}")
             # 确保返回默认值
             device_type = 'Other'
             os_name = 'Unknown'
             browser_name = 'Unknown'
             is_bot = False

        return {
            'device_type': device_type,
            'os': os_name,
            'browser': browser_name,
            'is_bot': is_bot
        }
    
    def _get_document_title(self, path: str, document_manager = None) -> str:
        """
        获取文档标题
        
        Args:
            path: 请求路径
            document_manager: 文档管理器实例
            
        Returns:
            文档标题，如果无法获取则返回路径
        """
        # 如果是文档页面，尝试获取文档标题
        try:
            if document_manager:
                # 检查是否是文档页面
                doc_match = re.match(r'/document/([^/]+)/([^/]+)/(.+)', path)
                if doc_match:
                    vendor, doc_type, filename = doc_match.groups()
                    doc_info = document_manager.get_document(vendor, doc_type, filename)
                    if doc_info and 'meta' in doc_info and 'title' in doc_info['meta']:
                        return doc_info['meta']['title']
                
                # 检查是否是分析文档页面
                analysis_match = re.match(r'/analysis/document/([^/]+)/([^/]+)/(.+)', path)
                if analysis_match:
                    vendor, doc_type, filename = analysis_match.groups()
                    analysis_info = document_manager.get_analysis_document(vendor, doc_type, filename)
                    if analysis_info and 'title' in analysis_info:
                        return analysis_info['title']
            
            # 如果无法获取标题，返回路径
            return path
        except Exception as e:
            self.logger.error(f"获取文档标题失败: {e}")
            return path
    
    def record_access(self, path: str = None, document_manager = None, path_exists: bool = True):
        """
        记录访问详情
        
        Args:
            path: 请求路径，如果为None则使用当前请求的路径
            document_manager: 文档管理器实例，用于获取文档标题
            path_exists: 路径是否存在，不存在的路径（扫描访问）不会记录到主统计中
        """
        try:
            if not path and request:
                path = request.path
            
            # 获取访问详情
            access_info = {
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'ip': request.remote_addr if request else 'unknown',
                'path': path or 'unknown',
                'title': self._get_document_title(path, document_manager),
                'user_agent': request.headers.get('User-Agent', 'unknown'),
                'user_agent_info': self._parse_user_agent(request.headers.get('User-Agent', 'unknown')),
                'timestamp': int(time.time()),
                'referer': request.referrer if request else None,
                'path_exists': path_exists  # 添加路径是否存在的标记
            }
            
            # 始终记录到完整访问日志
            self._record_to_all_access_log(access_info)
            
            # 如果是静态文件或favicon，或者路径不存在，不记录到主统计中
            if path and (path.startswith('/static/') or path == '/favicon.ico' or not path_exists):
                return
            
            # 记录到主访问日志（用于统计分析）
            self._record_to_main_access_log(access_info)
            
        except Exception as e:
            self.logger.error(f"记录访问详情失败: {e}")
    
    def _record_to_all_access_log(self, access_info: Dict[str, Any]):
        """
        记录到完整访问日志
        
        Args:
            access_info: 访问信息字典
        """
        try:
            # 加载现有完整访问日志
            all_access_details = []
            try:
                with open(self.all_access_log_file, 'r', encoding='utf-8') as f:
                    all_access_details = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.logger.warning(f"读取完整访问日志文件失败，将创建新文件: {self.all_access_log_file}")
                all_access_details = []
            
            # 添加新的访问记录
            all_access_details.append(access_info)
            
            # 限制日志大小（只保留最近的50000条记录）
            if len(all_access_details) > 50000:
                all_access_details = all_access_details[-50000:]
            
            # 保存完整访问日志
            with open(self.all_access_log_file, 'w', encoding='utf-8') as f:
                json.dump(all_access_details, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"记录到完整访问日志失败: {e}")
    
    def _record_to_main_access_log(self, access_info: Dict[str, Any]):
        """
        记录到主访问日志（用于统计分析）
        
        Args:
            access_info: 访问信息字典
        """
        try:
            # 加载现有访问日志
            access_details = []
            try:
                with open(self.access_log_file, 'r', encoding='utf-8') as f:
                    access_details = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.logger.warning(f"读取访问日志文件失败，将创建新文件: {self.access_log_file}")
                access_details = []
            
            # 添加新的访问记录
            access_details.append(access_info)
            
            # 限制日志大小（只保留最近的10000条记录）
            if len(access_details) > 10000:
                access_details = access_details[-10000:]
            
            # 保存访问日志
            with open(self.access_log_file, 'w', encoding='utf-8') as f:
                json.dump(access_details, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"记录到主访问日志失败: {e}")
    
    def get_access_details(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        获取访问详情
        
        Args:
            limit: 最大记录数，默认1000
            
        Returns:
            访问详情列表
        """
        try:
            if not os.path.exists(self.access_log_file):
                return []
            
            with open(self.access_log_file, 'r', encoding='utf-8') as f:
                access_details = json.load(f)
            
            # 按时间戳倒序排序
            access_details.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            # 限制记录数
            return access_details[:limit]
        
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
        try:
            if not os.path.exists(self.all_access_log_file):
                return []
            
            with open(self.all_access_log_file, 'r', encoding='utf-8') as f:
                all_access_details = json.load(f)
            
            # 按时间戳倒序排序
            all_access_details.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            # 是否过滤不存在路径的访问
            if not include_non_existent:
                all_access_details = [record for record in all_access_details if record.get('path_exists', True)]
            
            # 限制记录数
            return all_access_details[:limit]
        
        except Exception as e:
            self.logger.error(f"获取完整访问详情失败: {e}")
            return []
    
    def get_access_stats(self) -> Dict[str, Any]:
        """
        获取访问统计数据
        
        Returns:
            访问统计数据，包括PV、UV、设备类型分布等
        """
        try:
            if not os.path.exists(self.access_log_file):
                return self._get_empty_stats()
            
            with open(self.access_log_file, 'r', encoding='utf-8') as f:
                access_details = json.load(f)
            
            # 如果没有访问记录，返回空统计数据
            if not access_details:
                return self._get_empty_stats()
            
            # 计算总PV
            total_pv = len(access_details)
            
            # 计算总UV
            unique_ips = set(record.get('ip', '') for record in access_details)
            total_uv = len(unique_ips)
            
            # 计算服务器启动后的PV、UV
            start_time = self.server_start_time
            start_timestamp = int(start_time.timestamp())
            server_start_records = [r for r in access_details if r.get('timestamp', 0) >= start_timestamp]
            server_start_pv = len(server_start_records)
            server_start_uv = len(set(r.get('ip', '') for r in server_start_records))
            
            # 计算今日PV、UV
            today = datetime.now().date()
            today_str = today.strftime('%Y-%m-%d')
            today_records = [r for r in access_details if r.get('date', '') == today_str]
            today_pv = len(today_records)
            today_uv = len(set(r.get('ip', '') for r in today_records))
            
            # 计算本周PV、UV
            week_start = today - timedelta(days=today.weekday())
            week_start_timestamp = int(datetime.combine(week_start, datetime.min.time()).timestamp())
            week_records = [r for r in access_details if r.get('timestamp', 0) >= week_start_timestamp]
            week_pv = len(week_records)
            week_uv = len(set(r.get('ip', '') for r in week_records))
            
            # 计算设备类型分布
            device_types = {}
            for record in access_details:
                if 'user_agent_info' in record and 'device_type' in record['user_agent_info']:
                    device_type = record['user_agent_info']['device_type']
                    device_types[device_type] = device_types.get(device_type, 0) + 1
            
            # 计算操作系统分布
            os_types = {}
            for record in access_details:
                if 'user_agent_info' in record and 'os' in record['user_agent_info']:
                    os_type = record['user_agent_info']['os']
                    os_types[os_type] = os_types.get(os_type, 0) + 1
            
            # 计算浏览器分布
            browser_types = {}
            for record in access_details:
                if 'user_agent_info' in record and 'browser' in record['user_agent_info']:
                    browser_type = record['user_agent_info']['browser']
                    browser_types[browser_type] = browser_types.get(browser_type, 0) + 1
            
            # 计算最近30天每天的PV趋势
            daily_pv = {}
            for i in range(30):
                date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
                daily_pv[date] = 0
            
            for record in access_details:
                date = record.get('date', '')
                if date in daily_pv:
                    daily_pv[date] += 1
            
            # 将daily_pv转换为列表，便于前端处理
            daily_pv_trend = [{'date': date, 'pv': pv} for date, pv in sorted(daily_pv.items())]
            
            # 计算热门页面
            page_views = {}
            for record in access_details:
                title = record.get('title', record.get('path', 'unknown'))
                page_views[title] = page_views.get(title, 0) + 1
            
            # 获取前10个热门页面
            top_pages = [{'title': title, 'views': views} 
                         for title, views in sorted(page_views.items(), key=lambda x: x[1], reverse=True)[:10]]
            
            return {
                'total_pv': total_pv,
                'total_uv': total_uv,
                'server_start_pv': server_start_pv,
                'server_start_uv': server_start_uv,
                'today_pv': today_pv,
                'today_uv': today_uv,
                'week_pv': week_pv,
                'week_uv': week_uv,
                'device_types': [{'name': k, 'value': v} for k, v in device_types.items()],
                'os_types': [{'name': k, 'value': v} for k, v in os_types.items()],
                'browser_types': [{'name': k, 'value': v} for k, v in browser_types.items()],
                'daily_pv_trend': daily_pv_trend,
                'top_pages': top_pages,
                'server_start_time': self.server_start_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.logger.error(f"获取访问统计数据失败: {e}")
            return self._get_empty_stats()
    
    def _get_empty_stats(self) -> Dict[str, Any]:
        """
        获取空的统计数据
        
        Returns:
            空统计数据
        """
        today = datetime.now().date()
        daily_pv_trend = []
        for i in range(30):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_pv_trend.append({'date': date, 'pv': 0})
        
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
            'daily_pv_trend': sorted(daily_pv_trend, key=lambda x: x['date']),
            'top_pages': [],
            'server_start_time': self.server_start_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
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
