#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务管理器

负责管理任务的生命周期、状态和输出。
支持任务的创建、执行、状态查询和输出获取。
"""

import os
import json
import time
import uuid
import logging
import threading
import subprocess
import datetime
from typing import Dict, List, Any, Optional, Callable
from enum import Enum, auto

from src.utils.process_lock_manager import ProcessLockManager, ProcessType

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = auto()    # 等待执行
    RUNNING = auto()    # 正在执行
    COMPLETED = auto()  # 已完成
    FAILED = auto()     # 执行失败
    CANCELED = auto()   # 已取消

class Task:
    """任务类，表示一个具体的任务实例"""
    
    def __init__(self, task_id: str, name: str, command: str, params: Dict[str, Any] = None):
        """
        初始化任务
        
        Args:
            task_id: 任务ID
            name: 任务名称
            command: 执行命令
            params: 任务参数
        """
        self.task_id = task_id
        self.name = name
        self.command = command
        self.params = params or {}
        self.status = TaskStatus.PENDING
        self.created_at = time.time()
        self.started_at = None
        self.completed_at = None
        self.output = []
        self.return_code = None
        self.error = None
        self.process = None
        self.output_callbacks = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将任务转换为字典
        
        Returns:
            Dict: 任务字典
        """
        return {
            'task_id': self.task_id,
            'name': self.name,
            'command': self.command,
            'params': self.params,
            'status': self.status.name,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'output': self.output,
            'return_code': self.return_code,
            'error': self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        从字典创建任务
        
        Args:
            data: 任务字典
            
        Returns:
            Task: 任务实例
        """
        task = cls(
            task_id=data['task_id'],
            name=data['name'],
            command=data['command'],
            params=data['params']
        )
        task.status = TaskStatus[data['status']]
        task.created_at = data['created_at']
        task.started_at = data['started_at']
        task.completed_at = data['completed_at']
        task.output = data['output']
        task.return_code = data['return_code']
        task.error = data['error']
        return task
    
    def add_output_callback(self, callback: Callable[[str], None]):
        """
        添加输出回调函数
        
        Args:
            callback: 回调函数，接收输出行作为参数
        """
        self.output_callbacks.append(callback)
    
    def add_output(self, line: str):
        """
        添加输出行
        
        Args:
            line: 输出行
        """
        self.output.append(line)
        
        # 调用所有回调函数
        for callback in self.output_callbacks:
            try:
                callback(line)
            except Exception as e:
                logger.error(f"调用输出回调函数失败: {e}")

class TaskManager:
    """任务管理器，负责管理所有任务"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """单例模式"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TaskManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, base_dir: str = None):
        """
        初始化任务管理器
        
        Args:
            base_dir: 项目根目录路径
        """
        # 避免重复初始化
        if self._initialized:
            return
        
        self.logger = logging.getLogger(__name__)
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # 任务存储目录
        self.tasks_dir = os.path.join(self.base_dir, 'data', 'tasks')
        os.makedirs(self.tasks_dir, exist_ok=True)
        
        # 任务字典，键为任务ID，值为任务实例
        self.tasks = {}
        
        # 任务锁，用于保护任务字典
        self.task_lock = threading.RLock()
        
        # 加载已有任务
        self._load_tasks()
        
        self._initialized = True
        self.logger.info("任务管理器初始化完成")
    
    def _load_tasks(self):
        """加载已有任务"""
        try:
            # 遍历任务目录
            for filename in os.listdir(self.tasks_dir):
                if filename.endswith('.json'):
                    task_id = filename[:-5]  # 去掉.json后缀
                    task_path = os.path.join(self.tasks_dir, filename)
                    
                    try:
                        with open(task_path, 'r', encoding='utf-8') as f:
                            task_data = json.load(f)
                        
                        # 创建任务实例
                        task = Task.from_dict(task_data)
                        
                        # 添加到任务字典
                        with self.task_lock:
                            self.tasks[task_id] = task
                    except json.JSONDecodeError as e:
                        self.logger.error(f"加载任务失败: {task_path} - JSON格式错误: {e}")
                        # 备份格式错误的JSON文件
                        backup_dir = os.path.join(self.tasks_dir, 'backup')
                        os.makedirs(backup_dir, exist_ok=True)
                        backup_path = os.path.join(backup_dir, f"{task_id}_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                        try:
                            import shutil
                            shutil.copy2(task_path, backup_path)
                            self.logger.info(f"已备份格式错误的JSON文件到: {backup_path}")
                        except Exception as backup_err:
                            self.logger.error(f"备份JSON文件失败: {task_path} - {backup_err}")
                    except Exception as e:
                        self.logger.error(f"加载任务失败: {task_path} - {e}")
            
            self.logger.info(f"已加载 {len(self.tasks)} 个任务")
        except Exception as e:
            self.logger.error(f"加载任务目录失败: {e}")
    
    def _save_task(self, task: Task):
        """
        保存任务到文件
        
        Args:
            task: 任务实例
        """
        try:
            # 确保任务目录存在
            os.makedirs(self.tasks_dir, exist_ok=True)
            
            task_path = os.path.join(self.tasks_dir, f"{task.task_id}.json")
            
            # 保存任务数据
            with open(task_path, 'w', encoding='utf-8') as f:
                json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
                try:
                    # 确保数据写入磁盘
                    f.flush()
                    os.fsync(f.fileno())
                except (ValueError, OSError) as e:
                    self.logger.warning(f"同步任务文件到磁盘时发生错误: {task.task_id} - {e}")
        except Exception as e:
            self.logger.error(f"保存任务失败: {task.task_id} - {e}")
    
    def create_task(self, name: str, command: str, params: Dict[str, Any] = None) -> str:
        """
        创建新任务
        
        Args:
            name: 任务名称
            command: 执行命令
            params: 任务参数
            
        Returns:
            str: 任务ID
        """
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务实例
        task = Task(task_id, name, command, params)
        
        # 添加到任务字典
        with self.task_lock:
            self.tasks[task_id] = task
        
        # 保存任务
        self._save_task(task)
        
        self.logger.info(f"创建任务: {task_id} - {name}")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[Task]: 任务实例，如果不存在则返回None
        """
        with self.task_lock:
            return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        获取所有任务
        
        Returns:
            List[Dict[str, Any]]: 任务列表
        """
        with self.task_lock:
            return [task.to_dict() for task in self.tasks.values()]
    
    def get_running_tasks(self) -> List[Dict[str, Any]]:
        """
        获取正在运行的任务
        
        Returns:
            List[Dict[str, Any]]: 任务列表
        """
        with self.task_lock:
            return [task.to_dict() for task in self.tasks.values() 
                   if task.status == TaskStatus.RUNNING]
    
    def run_task(self, task_id: str, output_callback: Callable[[str], None] = None) -> bool:
        """
        运行任务
        
        Args:
            task_id: 任务ID
            output_callback: 输出回调函数，接收输出行作为参数
            
        Returns:
            bool: 是否成功启动任务
        """
        task = self.get_task(task_id)
        if not task:
            self.logger.error(f"任务不存在: {task_id}")
            return False
        
        # 如果任务已经在运行，直接返回
        if task.status == TaskStatus.RUNNING:
            self.logger.warning(f"任务已在运行: {task_id}")
            return True
        
        # 如果任务已经完成，重置状态
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELED]:
            task.status = TaskStatus.PENDING
            task.started_at = None
            task.completed_at = None
            task.output = []
            task.return_code = None
            task.error = None
        
        # 添加输出回调
        if output_callback:
            task.add_output_callback(output_callback)
        
        # 启动任务线程
        thread = threading.Thread(target=self._run_task_thread, args=(task,))
        thread.daemon = True
        thread.start()
        
        self.logger.info(f"启动任务: {task_id}")
        return True
    
    def _run_task_thread(self, task: Task):
        """
        任务线程
        
        Args:
            task: 任务实例
        """
        # 确定任务类型，用于进程锁
        process_type = None
        if 'crawl' in task.command:
            process_type = ProcessType.CRAWLER
        elif 'analyze' in task.command:
            process_type = ProcessType.ANALYZER
        
        # 获取进程锁管理器
        process_lock_manager = None
        lock_acquired = False
        
        if process_type:
            process_lock_manager = ProcessLockManager.get_instance(process_type)
        
        try:
            # 如果需要进程锁，先获取锁
            if process_lock_manager:
                self.logger.info(f"尝试获取{process_type.name}进程锁，任务: {task.task_id}")
                if not process_lock_manager.acquire_lock():
                    task.status = TaskStatus.FAILED
                    task.error = f"无法获取{process_type.name}进程锁，可能有其他{process_type.name}进程正在运行"
                    task.completed_at = time.time()
                    task.return_code = 1  # 设置非零返回码表示失败
                    self._save_task(task)
                    self.logger.error(f"任务失败: {task.task_id} - {task.error}")
                    return
                
                lock_acquired = True
                self.logger.info(f"已成功获取{process_type.name}进程锁，开始执行任务: {task.task_id}")
            
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            self._save_task(task)
            
            # 构建命令
            command = task.command
            
            # 替换命令中的占位符
            if task.params:
                for param_name, param_value in task.params.items():
                    if param_value:
                        placeholder = '{' + param_name + '}'
                        if placeholder in command:
                            command = command.replace(placeholder, param_value)
                        else:
                            command += f" --{param_name} {param_value}"
            
            # 执行命令
            self.logger.info(f"执行命令: {command}")
            
            # 创建进程
            # 使用bash执行命令，确保环境变量和别名可用
            task.process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self.base_dir,
                text=True,
                bufsize=1,  # 行缓冲
                executable='/bin/bash'  # 明确指定使用bash
            )
            
            # 读取输出
            for line in task.process.stdout:
                line = line.rstrip()
                task.add_output(line)
                self._save_task(task)
            
            # 等待进程结束
            return_code = task.process.wait()
            task.return_code = return_code
            
            # 更新任务状态
            task.completed_at = time.time()
            if return_code == 0:
                task.status = TaskStatus.COMPLETED
                self.logger.info(f"任务完成: {task.task_id}")
            else:
                task.status = TaskStatus.FAILED
                task.error = f"命令返回非零状态码: {return_code}"
                self.logger.error(f"任务失败: {task.task_id} - {task.error}")
            
            # 保存任务
            self._save_task(task)
            
        except Exception as e:
            # 更新任务状态
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = time.time()
            
            # 保存任务
            self._save_task(task)
            
            self.logger.error(f"执行任务异常: {task.task_id} - {e}")
        finally:
            # 释放进程锁
            if process_lock_manager and lock_acquired:
                process_lock_manager.release_lock()
                self.logger.info(f"已释放{process_type.name}进程锁，任务: {task.task_id}")
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功取消任务
        """
        task = self.get_task(task_id)
        if not task:
            self.logger.error(f"任务不存在: {task_id}")
            return False
        
        # 如果任务不在运行，直接返回
        if task.status != TaskStatus.RUNNING:
            self.logger.warning(f"任务未在运行: {task_id}")
            return False
        
        # 终止进程
        if task.process:
            try:
                task.process.terminate()
                
                # 等待进程结束
                try:
                    task.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # 如果进程没有在5秒内结束，强制终止
                    task.process.kill()
                
                # 更新任务状态
                task.status = TaskStatus.CANCELED
                task.completed_at = time.time()
                task.error = "任务被取消"
                
                # 保存任务
                self._save_task(task)
                
                # 确定任务类型，用于进程锁
                process_type = None
                if 'crawl' in task.command:
                    process_type = ProcessType.CRAWLER
                elif 'analyze' in task.command:
                    process_type = ProcessType.ANALYZER
                
                # 释放进程锁
                if process_type:
                    process_lock_manager = ProcessLockManager.get_instance(process_type)
                    process_lock_manager.release_lock()
                    self.logger.info(f"已释放{process_type.name}进程锁，任务: {task_id}")
                
                self.logger.info(f"取消任务: {task_id}")
                return True
            except Exception as e:
                self.logger.error(f"取消任务失败: {task_id} - {e}")
                return False
        
        return False
    
    def delete_task(self, task_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功删除任务
        """
        task = self.get_task(task_id)
        if not task:
            self.logger.error(f"任务不存在: {task_id}")
            return False
        
        # 如果任务在运行，先取消
        if task.status == TaskStatus.RUNNING:
            self.cancel_task(task_id)
        
        # 删除任务文件
        try:
            task_path = os.path.join(self.tasks_dir, f"{task_id}.json")
            if os.path.exists(task_path):
                os.remove(task_path)
        except Exception as e:
            self.logger.error(f"删除任务文件失败: {task_id} - {e}")
        
        # 从任务字典中删除
        with self.task_lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
        
        self.logger.info(f"删除任务: {task_id}")
        return True
    
    def clean_old_tasks(self, days: int = 7) -> int:
        """
        清理旧任务
        
        Args:
            days: 保留天数，默认7天
            
        Returns:
            int: 清理的任务数量
        """
        # 计算截止时间
        cutoff_time = time.time() - days * 24 * 60 * 60
        
        # 找出需要清理的任务
        tasks_to_clean = []
        with self.task_lock:
            for task_id, task in self.tasks.items():
                # 只清理已完成、失败或取消的任务
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELED]:
                    # 如果完成时间早于截止时间，则清理
                    if task.completed_at and task.completed_at < cutoff_time:
                        tasks_to_clean.append(task_id)
        
        # 清理任务
        for task_id in tasks_to_clean:
            self.delete_task(task_id)
        
        self.logger.info(f"清理了 {len(tasks_to_clean)} 个旧任务")
        return len(tasks_to_clean)
