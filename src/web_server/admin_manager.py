#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器 - 管理员管理器

负责处理管理员相关的功能，如登录验证、任务管理等。
"""

import os
import logging
import yaml
import json
from typing import Dict, List, Any, Optional
from flask import session

from src.utils.process_lock_manager import ProcessLockManager, ProcessType
from src.utils.task_manager import TaskManager

class AdminManager:
    """管理员管理器类"""
    
    def __init__(self, base_dir: str):
        """
        初始化管理员管理器
        
        Args:
            base_dir: 项目根目录路径
        """
        self.logger = logging.getLogger(__name__)
        self.base_dir = base_dir
        
        # 加载管理员账户信息
        self.admin_credentials = self._load_admin_credentials()
        
        # 初始化任务管理器
        self.task_manager = TaskManager(base_dir)
        
        self.logger.info("管理员管理器初始化完成")
    
    def is_logged_in(self) -> bool:
        """
        检查用户是否已登录
        
        Returns:
            是否已登录
        """
        return 'logged_in' in session and session['logged_in']
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        验证用户凭据
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            验证是否成功
        """
        if (username == self.admin_credentials['username'] and 
            password == self.admin_credentials['password']):
            session['logged_in'] = True
            session['username'] = username
            return True
        return False
    
    def logout(self):
        """登出用户"""
        session.pop('logged_in', None)
        session.pop('username', None)
    
    def get_available_tasks(self) -> List[Dict[str, Any]]:
        """
        获取可用的任务列表
        
        Returns:
            List: 任务列表
        """
        # 定义可用任务
        tasks = [
            {
                'id': 'crawl_all',
                'name': '爬取所有厂商数据',
                'description': '爬取所有厂商的最新博客和文档',
                'command': './run.sh crawl',
                'params': []
            },
            {
                'id': 'crawl_aws',
                'name': '爬取AWS数据',
                'description': '仅爬取AWS的最新博客和文档',
                'command': './run.sh crawl --vendor aws',
                'params': []
            },
            {
                'id': 'crawl_azure',
                'name': '爬取Azure数据',
                'description': '仅爬取Azure的最新博客和文档',
                'command': './run.sh crawl --vendor azure',
                'params': []
            },
            {
                'id': 'crawl_gcp',
                'name': '爬取GCP数据',
                'description': '仅爬取GCP的最新博客和文档',
                'command': './run.sh crawl --vendor gcp',
                'params': []
            },
            {
                'id': 'analyze_all',
                'name': '分析所有数据',
                'description': '对所有爬取的数据进行AI分析',
                'command': './run.sh analyze',
                'params': []
            },
            {
                'id': 'analyze_aws',
                'name': '分析AWS数据',
                'description': '仅对AWS的数据进行AI分析',
                'command': './run.sh analyze --vendor aws',
                'params': []
            },
            {
                'id': 'analyze_azure',
                'name': '分析Azure数据',
                'description': '仅对Azure的数据进行AI分析',
                'command': './run.sh analyze --vendor azure',
                'params': []
            },
            {
                'id': 'analyze_gcp',
                'name': '分析GCP数据',
                'description': '仅对GCP的数据进行AI分析',
                'command': './run.sh analyze --vendor gcp',
                'params': []
            },
            {
                'id': 'crawl_force',
                'name': '强制爬取所有数据',
                'description': '强制爬取所有厂商的数据，忽略本地metadata',
                'command': './run.sh crawl --force',
                'params': []
            },
            {
                'id': 'analyze_force',
                'name': '强制分析所有数据',
                'description': '强制分析所有数据，忽略文件是否已存在',
                'command': './run.sh analyze --force',
                'params': []
            },
            {
                'id': 'daily',
                'name': '执行每日任务',
                'description': '执行每日爬取与分析任务',
                'command': './run.sh daily',
                'params': []
            },
            {
                'id': 'check_tasks',
                'name': '检查任务完成状态',
                'description': '检查任务完成状态，显示未完成任务的文件',
                'command': './run.sh check-tasks',
                'params': []
            }
        ]
        
        return tasks
    
    def run_task(self, task_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行指定的任务 - 简化：让子进程自己处理进程锁
        
        Args:
            task_id: 任务ID
            params: 任务参数
            
        Returns:
            Dict: 任务执行结果
        """
        # 获取任务信息
        tasks = self.get_available_tasks()
        task_info = next((t for t in tasks if t['id'] == task_id), None)
        
        if not task_info:
            raise ValueError(f"未找到任务: {task_id}")
        
        # 创建任务
        real_task_id = self.task_manager.create_task(
            name=task_info['name'],
            command=task_info['command'],
            params=params or {}
        )
        
        # 运行任务（异步执行）
        success = self.task_manager.run_task(real_task_id)
        
        if success:
            self.logger.info(f"成功启动任务: {task_id} (实际ID: {real_task_id})")
            return {
                'success': True,
                'task_id': real_task_id,
                'message': f'任务已启动: {task_info["name"]}'
            }
        else:
            self.logger.error(f"启动任务失败: {task_id}")
            return {
                'success': False,
                'error': f'启动任务失败: {task_info["name"]}'
            }
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 任务信息
        """
        task = self.task_manager.get_task(task_id)
        if not task:
            return {'success': False, 'error': f'任务不存在: {task_id}'}
        
        return {'success': True, 'task': task.to_dict()}
    
    def get_all_tasks(self) -> Dict[str, Any]:
        """
        获取所有任务
        
        Returns:
            Dict: 任务列表
        """
        tasks = self.task_manager.get_all_tasks()
        return {'success': True, 'tasks': tasks}
    
    def get_running_tasks(self) -> Dict[str, Any]:
        """
        获取正在运行的任务
        
        Returns:
            Dict: 任务列表
        """
        tasks = self.task_manager.get_running_tasks()
        return {'success': True, 'tasks': tasks}
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 操作结果
        """
        result = self.task_manager.cancel_task(task_id)
        if result:
            return {'success': True, 'message': f'成功取消任务: {task_id}'}
        else:
            return {'success': False, 'error': f'取消任务失败: {task_id}'}
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 操作结果
        """
        result = self.task_manager.delete_task(task_id)
        if result:
            return {'success': True, 'message': f'成功删除任务: {task_id}'}
        else:
            return {'success': False, 'error': f'删除任务失败: {task_id}'}
    
    def get_process_lock_status(self) -> Dict[str, Any]:
        """
        获取进程锁状态
        
        Returns:
            Dict: 进程锁状态信息
        """
        try:
            # 获取所有进程锁的状态
            lock_status = ProcessLockManager.check_lock_status()
            
            # 格式化时间戳
            for process_type, status in lock_status.items():
                if 'timestamp' in status:
                    timestamp = status['timestamp']
                    import datetime
                    status['timestamp_formatted'] = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
                if 'age' in status:
                    age = status['age']
                    # 格式化为小时:分钟:秒
                    hours, remainder = divmod(age, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    status['age_formatted'] = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            
            return lock_status
        except Exception as e:
            self.logger.error(f"获取进程锁状态失败: {e}")
            return {"error": str(e)}
    
    def clear_process_lock(self, process_type_name: str) -> Dict[str, Any]:
        """
        清除指定类型的进程锁
        
        Args:
            process_type_name: 进程类型名称 (CRAWLER, ANALYZER)
            
        Returns:
            Dict: 操作结果
        """
        try:
            # 将字符串转换为ProcessType枚举
            if process_type_name.upper() == 'CRAWLER':
                process_type = ProcessType.CRAWLER
            elif process_type_name.upper() == 'ANALYZER':
                process_type = ProcessType.ANALYZER
            else:
                return {'success': False, 'error': f'不支持的进程类型: {process_type_name}'}
            
            # 强制清除进程锁
            result = ProcessLockManager.force_clear_lock_by_type(process_type)
            
            if result:
                self.logger.info(f"成功清除{process_type_name}进程锁")
                return {'success': True, 'message': f'成功清除{process_type_name}进程锁'}
            else:
                self.logger.warning(f"清除{process_type_name}进程锁失败")
                return {'success': False, 'error': f'清除{process_type_name}进程锁失败'}
                
        except Exception as e:
            self.logger.error(f"清除进程锁时发生异常: {e}")
            return {'success': False, 'error': str(e)}
    
    def _load_admin_credentials(self) -> Dict[str, str]:
        """
        从配置文件加载管理员账户信息
        
        Returns:
            Dict: 包含用户名和密码的字典
        """
        # 默认凭据
        default_credentials = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        try:
            config_path = os.path.join(self.base_dir, 'config.secret.yaml')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                if config and 'admin' in config:
                    admin_config = config['admin']
                    if 'username' in admin_config and 'password' in admin_config:
                        self.logger.info("已从配置文件加载管理员账户信息")
                        return {
                            'username': admin_config['username'],
                            'password': admin_config['password']
                        }
            
            self.logger.warning("未找到管理员账户配置，使用默认凭据")
            return default_credentials
            
        except Exception as e:
            self.logger.error(f"加载管理员账户信息失败: {e}")
            return default_credentials
