#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器 - 管理员管理器

负责处理管理员相关的功能，如登录验证、任务管理等。
"""

import os
import logging
import yaml
import subprocess
import tempfile
from typing import Dict, List, Any, Optional
from flask import session

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
                'id': 'analyze_file',
                'name': '分析单个文件',
                'description': '对指定的单个文件进行AI分析',
                'command': './run.sh analyze --file {file}',
                'params': ['file']
            },
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
        执行指定的任务
        
        Args:
            task_id: 任务ID
            params: 任务参数
            
        Returns:
            Dict: 任务执行结果
        """
        # 获取任务信息
        tasks = self.get_available_tasks()
        task = next((t for t in tasks if t['id'] == task_id), None)
        
        if not task:
            raise ValueError(f"未找到任务: {task_id}")
        
        # 构建命令
        command = task['command']
        
        # 替换命令中的占位符
        if params:
            for param_name, param_value in params.items():
                if param_value:
                    placeholder = '{' + param_name + '}'
                    if placeholder in command:
                        command = command.replace(placeholder, param_value)
                    else:
                        command += f" --{param_name} {param_value}"
        
        # 执行命令
        self.logger.info(f"执行任务: {task['name']}, 命令: {command}")
        
        # 创建临时文件用于存储输出
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # 执行命令，将输出重定向到临时文件
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self.base_dir,
                text=True
            )
            
            # 读取输出并写入临时文件
            with open(temp_path, 'w') as f:
                for line in process.stdout:
                    f.write(line)
            
            # 等待进程结束
            return_code = process.wait()
            
            # 读取输出
            with open(temp_path, 'r') as f:
                output = f.read()
            
            # 删除临时文件
            os.unlink(temp_path)
            
            # 返回结果
            return {
                'success': return_code == 0,
                'output': output,
                'return_code': return_code
            }
            
        except Exception as e:
            self.logger.error(f"执行任务失败: {e}")
            
            # 删除临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            # 返回错误信息
            return {
                'success': False,
                'error': str(e)
            }
    
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
