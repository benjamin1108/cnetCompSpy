#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import logging
import threading
import fcntl
import errno
import socket
import psutil
import datetime
from typing import Dict, Any, Optional, List, Set
from enum import Enum, auto

logger = logging.getLogger(__name__)

class ProcessType(Enum):
    """进程类型枚举"""
    CRAWLER = auto()  # 爬虫进程
    ANALYZER = auto()  # 分析进程
    WEB_SERVER = auto()  # Web服务器进程

class ProcessLockManager:
    """
    进程锁管理器，实现单例模式和进程间锁定
    
    该类使用文件锁实现跨进程的单例模式，确保同一时间只有一个特定类型的进程在运行。
    同时实现了不同类型进程间的互斥关系管理。
    """
    
    # 类变量，用于存储单例实例
    _instances: Dict[ProcessType, 'ProcessLockManager'] = {}
    _instance_lock = threading.Lock()
    
    # 进程类型互斥关系配置
    # 键为进程类型，值为该进程运行时不允许运行的其他进程类型集合
    _mutex_config = {
        ProcessType.CRAWLER: {ProcessType.ANALYZER},  # 爬虫运行时不允许分析进程运行
        ProcessType.ANALYZER: {ProcessType.CRAWLER},  # 分析进程运行时不允许爬虫进程运行
        ProcessType.WEB_SERVER: set(),  # Web服务器运行时允许其他进程运行
    }
    
    # 锁文件目录
    _lock_dir = "/tmp"
    
    # 锁超时时间（秒）
    _lock_timeout = 3600  # 默认1小时
    
    def __init__(self, process_type: ProcessType):
        """
        初始化进程锁管理器
        
        Args:
            process_type: 进程类型
        """
        self.process_type = process_type
        # 使用进程类型特定的锁文件路径来实现进程互斥
        self.lock_file_path = os.path.join(self._lock_dir, f"cnetCompSpy_{process_type.name.lower()}.lock")
        self.lock_file = None
        self.locked = False
        self.pid = os.getpid()
        self.hostname = socket.gethostname()
        self.command = " ".join(sys.argv)
        
        logger.info(f"初始化进程锁管理器: {process_type.name}, 锁文件: {self.lock_file_path}")
    
    @classmethod
    def get_instance(cls, process_type: ProcessType) -> 'ProcessLockManager':
        """
        获取进程锁管理器实例（单例模式）
        
        Args:
            process_type: 进程类型
            
        Returns:
            ProcessLockManager: 进程锁管理器实例
        """
        with cls._instance_lock:
            if process_type not in cls._instances:
                cls._instances[process_type] = cls(process_type)
            return cls._instances[process_type]
    
    def acquire_lock(self) -> bool:
        """
        获取进程锁
        
        Returns:
            bool: 是否成功获取锁
        """
        if self.locked:
            logger.debug(f"进程锁已获取: {self.process_type.name}")
            return True
        
        # 首先检查同类型进程是否正在运行
        if self.is_same_type_process_running():
            logger.warning(f"同类型进程已在运行，无法获取锁: {self.process_type.name}")
            return False
        
        # 检查互斥进程是否正在运行
        for mutex_type in self._mutex_config.get(self.process_type, set()):
            if self.is_process_running(mutex_type):
                logger.warning(f"互斥进程正在运行: {mutex_type.name}，无法获取锁: {self.process_type.name}")
                return False
        
        # 即使没有进程持有排他锁，也检查锁文件是否存在且有效
        if os.path.exists(self.lock_file_path):
            try:
                with open(self.lock_file_path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        lock_info = json.loads(content)
                        timestamp = lock_info.get("timestamp", 0)
                        pid = lock_info.get("pid", 0)
                        if pid > 0 and (time.time() - timestamp) <= self._lock_timeout:
                            try:
                                process = psutil.Process(pid)
                                if process.is_running() and process.status() != psutil.STATUS_ZOMBIE:
                                    logger.warning(f"锁文件存在且进程仍在运行，无法获取锁: {self.process_type.name}")
                                    return False
                            except psutil.NoSuchProcess:
                                pass
            except Exception as e:
                logger.warning(f"检查锁文件内容时发生错误: {e}")
        
        try:
            # 创建锁文件目录（如果不存在）
            os.makedirs(self._lock_dir, exist_ok=True)
            
            # 打开锁文件
            self.lock_file = open(self.lock_file_path, 'w+')
            
            # 尝试获取文件锁（非阻塞模式）
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # 写入锁信息
            current_time = time.time()
            lock_info = {
                "pid": self.pid,
                "process_type": self.process_type.name,
                "timestamp": current_time,
                "timestamp_formatted": datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S'),
                "hostname": self.hostname,
                "command": self.command,
                "start_method": "web" if "web_server" in self.command else "shell"
            }
            max_retries = 3
            temp_file_path = self.lock_file_path + ".tmp"
            for attempt in range(max_retries):
                try:
                    # 使用临时文件写入锁信息
                    with open(temp_file_path, 'w') as temp_file:
                        json.dump(lock_info, temp_file, ensure_ascii=False, indent=2)
                        temp_file.flush()
                        os.fsync(temp_file.fileno())
                        logger.debug(f"成功写入临时锁文件内容: {lock_info}")
                    
                    # 原子性地替换目标文件
                    os.rename(temp_file_path, self.lock_file_path)
                    logger.debug(f"成功将临时文件替换为锁文件: {self.lock_file_path}")
                    
                    # 验证写入内容
                    with open(self.lock_file_path, 'r') as verify_file:
                        content = verify_file.read().strip()
                        if content:
                            try:
                                loaded_info = json.loads(content)
                                if loaded_info.get("pid") == self.pid:
                                    logger.debug(f"成功验证锁文件内容: {loaded_info}")
                                    break
                            except json.JSONDecodeError:
                                logger.warning(f"锁文件内容无法解析为JSON，重试写入 ({attempt+1}/{max_retries})")
                        else:
                            logger.warning(f"锁文件内容为空，重试写入 ({attempt+1}/{max_retries})")
                    
                    if attempt == max_retries - 1:
                        raise Exception("锁文件内容写入后为空或无法解析，达到最大重试次数")
                except Exception as e:
                    logger.error(f"写入锁文件内容时发生错误 ({attempt+1}/{max_retries}): {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(0.5)  # 短暂等待后重试
                    # 清理临时文件（如果存在）
                    if os.path.exists(temp_file_path):
                        try:
                            os.remove(temp_file_path)
                        except Exception:
                            pass
            
            self.locked = True
            logger.info(f"成功获取进程锁: {self.process_type.name}")
            return True
            
        except IOError as e:
            # 如果是因为文件被锁定而失败
            if e.errno == errno.EAGAIN or e.errno == errno.EACCES:
                logger.warning(f"无法获取进程锁: {self.process_type.name}，锁已被其他进程持有")
                
                logger.warning(f"无法获取进程锁: {self.process_type.name}，锁已被其他进程持有")
            
            # 关闭文件（如果已打开）
            if self.lock_file:
                self.lock_file.close()
                self.lock_file = None
            
            return False
            
        except Exception as e:
            logger.error(f"获取进程锁时发生异常: {e}")
            
            # 关闭文件（如果已打开）
            if self.lock_file:
                self.lock_file.close()
                self.lock_file = None
            
            return False
    
    def release_lock(self) -> bool:
        """
        释放进程锁
        
        Returns:
            bool: 是否成功释放锁
        """
        if not self.locked or not self.lock_file:
            logger.debug(f"进程锁未获取，无需释放: {self.process_type.name}")
            return True
        
        try:
            # 释放文件锁
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
            
            # 关闭锁文件，但不删除它
            self.lock_file.close()
            self.lock_file = None
            
            self.locked = False
            logger.info(f"成功释放进程锁: {self.process_type.name}")
            return True
            
        except Exception as e:
            logger.error(f"释放进程锁时发生异常: {e}")
            return False
    
    def is_same_type_process_running(self) -> bool:
        """
        检查同类型的进程是否正在运行
        
        Returns:
            bool: 是否有同类型进程正在运行
        """
        return self.is_process_running(self.process_type)
    
    def is_process_running(self, process_type: ProcessType) -> bool:
        """
        检查指定类型的进程是否正在运行
        
        Args:
            process_type: 进程类型
            
        Returns:
            bool: 是否正在运行
        """
        # 如果检查的是当前进程类型，并且已经获取了锁，则返回False（自己不会阻止自己）
        if process_type == self.process_type and self.locked:
            return False
            
        lock_file_path = os.path.join(self._lock_dir, f"cnetCompSpy_{process_type.name.lower()}.lock")
        
        if not os.path.exists(lock_file_path):
            return False
        
        # 检查文件大小，如果为0则认为是无效锁
        try:
            if os.path.getsize(lock_file_path) == 0:
                logger.warning(f"锁文件为空: {process_type.name}")
                return False
        except Exception:
            # 如果无法获取文件大小，可能是文件已被删除
            return False
        
        try:
            with open(lock_file_path, 'r') as f:
                try:
                    # 尝试获取共享锁（非阻塞模式）
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
                    # 如果成功获取共享锁，说明没有进程持有排他锁，即进程不在运行
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    
                    # 检查锁是否过期
                    try:
                        content = f.read().strip()
                        # 检查文件内容是否为空
                        if not content:
                            logger.warning(f"锁文件内容为空: {process_type.name}")
                            return False
                            
                        lock_info = json.loads(content)
                        timestamp = lock_info.get("timestamp", 0)
                        pid = lock_info.get("pid", 0)
                        
                        # 检查时间戳是否超过超时时间
                        if time.time() - timestamp > self._lock_timeout:
                            logger.warning(f"检测到过期的锁: {process_type.name}")
                            return False
                            
                        # 检查进程是否仍在运行
                        if pid > 0:
                            try:
                                process = psutil.Process(pid)
                                # 如果进程存在但已经结束
                                if process.status() == psutil.STATUS_ZOMBIE:
                                    logger.warning(f"持有锁的进程是僵尸进程: {pid}")
                                    return False
                            except psutil.NoSuchProcess:
                                logger.warning(f"持有锁的进程不存在: {pid}")
                                return False
                    except (json.JSONDecodeError, IOError) as e:
                        logger.warning(f"读取锁信息时发生错误: {e}")
                        return False
                    
                    return False
                except IOError:
                    # 如果无法获取共享锁，说明有进程持有排他锁，即进程正在运行
                    # 额外检查持有锁的进程是否仍在运行
                    try:
                        # 尝试读取锁文件内容
                        f.seek(0)
                        content = f.read().strip()
                        if content:
                            try:
                                lock_info = json.loads(content)
                                timestamp = lock_info.get("timestamp", 0)
                                pid = lock_info.get("pid", 0)
                                if pid > 0:
                                    try:
                                        process = psutil.Process(pid)
                                        # 检查进程是否仍在运行
                                        if not process.is_running() or process.status() == psutil.STATUS_ZOMBIE:
                                            logger.warning(f"持有锁的进程已经结束或为僵尸进程: {pid}")
                                            return False
                                    except psutil.NoSuchProcess:
                                        logger.warning(f"持有锁的进程不存在: {pid}")
                                        return False
                                # 检查时间戳是否超过超时时间
                                if time.time() - timestamp > self._lock_timeout:
                                    logger.warning(f"检测到过期的锁: {process_type.name}")
                                    return False
                            except json.JSONDecodeError:
                                logger.warning(f"无法解析锁文件内容: {process_type.name}")
                                return False
                    except Exception as e:
                        logger.warning(f"读取锁文件内容时发生错误: {e}")
                        return False
                    
                    # 如果以上检查都通过，则认为进程正在运行
                    logger.info(f"检测到进程正在运行: {process_type.name}")
                    return True
        except Exception as e:
            logger.error(f"检查进程运行状态时发生异常: {e}")
            return False
    
    def is_lock_expired(self) -> bool:
        """
        检查锁是否过期
        
        Returns:
            bool: 是否过期
        """
        if not os.path.exists(self.lock_file_path):
            return False
        
        try:
            # 检查文件大小，如果为0则认为是无效锁
            if os.path.getsize(self.lock_file_path) == 0:
                logger.warning(f"锁文件为空: {self.process_type.name}")
                return True
                
            with open(self.lock_file_path, 'r') as f:
                try:
                    content = f.read().strip()
                    # 检查文件内容是否为空
                    if not content:
                        logger.warning(f"锁文件内容为空: {self.process_type.name}")
                        return True
                        
                    lock_info = json.loads(content)
                    timestamp = lock_info.get("timestamp", 0)
                    pid = lock_info.get("pid", 0)
                    
                    # 检查时间戳是否超过超时时间
                    if time.time() - timestamp > self._lock_timeout:
                        logger.warning(f"锁已过期: {self.process_type.name}, 超过 {self._lock_timeout} 秒")
                        return True
                    
                    # 检查进程是否仍在运行
                    if pid > 0:
                        try:
                            process = psutil.Process(pid)
                            # 如果进程存在但已经结束
                            if process.status() == psutil.STATUS_ZOMBIE:
                                logger.warning(f"持有锁的进程是僵尸进程: {pid}")
                                return True
                        except psutil.NoSuchProcess:
                            logger.warning(f"持有锁的进程不存在: {pid}")
                            return True
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"读取锁信息时发生错误: {e}")
                    # 如果无法读取锁信息，认为锁已损坏，可以清除
                    return True
        except Exception as e:
            logger.error(f"检查锁是否过期时发生异常: {e}")
            # 如果发生任何异常，认为锁可能已损坏
            return True
        
        return False
    
    def force_clear_lock(self, caller_is_script_or_web=False) -> bool:
        """
        强制清除锁，只有在调用者是脚本或Web页面时才允许
        
        Args:
            caller_is_script_or_web: 是否由脚本或Web页面调用
            
        Returns:
            bool: 是否成功清除
        """
        if not caller_is_script_or_web:
            logger.warning(f"非脚本或Web页面调用，禁止强制清除锁: {self.process_type.name}")
            return False
            
        if not os.path.exists(self.lock_file_path):
            return True
        
        try:
            os.remove(self.lock_file_path)
            logger.info(f"成功强制清除锁: {self.process_type.name}")
            return True
        except Exception as e:
            logger.error(f"强制清除锁时发生异常: {e}")
            return False
    
    def __enter__(self):
        """上下文管理器入口"""
        self.acquire_lock()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.release_lock()
    
    @classmethod
    def check_lock_status(cls) -> Dict[str, Dict[str, Any]]:
        """
        检查所有进程锁的状态
        
        Returns:
            Dict: 锁状态信息
        """
        status = {}
        for process_type in ProcessType:
            lock_file = os.path.join(cls._lock_dir, f"cnetCompSpy_{process_type.name.lower()}.lock")
            if os.path.exists(lock_file):
                try:
                    with open(lock_file, 'r') as f:
                        try:
                            # 尝试获取共享锁（非阻塞模式）
                            fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
                            # 如果成功获取共享锁，说明没有进程持有排他锁
                            has_exclusive_lock = False
                            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        except IOError:
                            # 如果无法获取共享锁，说明有进程持有排他锁
                            has_exclusive_lock = True
                        
                        try:
                            f.seek(0)
                            content = f.read().strip()
                            
                            # 检查文件内容是否为空
                            if not content:
                                status[process_type.name] = {
                                    'locked': has_exclusive_lock,
                                    'error': '锁文件内容为空'
                                }
                                continue
                                
                            data = json.loads(content)
                            timestamp = data.get('timestamp', 0)
                            pid = data.get('pid', 0)
                            process_type_name = data.get('process_type', 'UNKNOWN')
                            
                            # 检查进程是否仍在运行
                            process_exists = False
                            if pid > 0:
                                try:
                                    process = psutil.Process(pid)
                                    process_exists = process.is_running() and process.status() != psutil.STATUS_ZOMBIE
                                except psutil.NoSuchProcess:
                                    pass
                            
                            # 如果进程存在且未过期，强制将 locked 设置为 true，即使未持有排他锁
                            expired = (time.time() - timestamp) > cls._lock_timeout
                            effective_locked = has_exclusive_lock or (process_exists and not expired)
                            
                            if process_type.name == process_type_name:
                                status[process_type.name] = {
                                    'locked': effective_locked,
                                    'pid': pid,
                                    'process_exists': process_exists,
                                    'timestamp': timestamp,
                                    'timestamp_formatted': data.get('timestamp_formatted', ''),
                                    'age': time.time() - timestamp,
                                    'expired': expired,
                                    'hostname': data.get('hostname', ''),
                                    'command': data.get('command', ''),
                                    'start_method': data.get('start_method', 'unknown')
                                }
                            else:
                                status[process_type.name] = {'locked': False}
                        except json.JSONDecodeError as e:
                            status[process_type.name] = {
                                'locked': has_exclusive_lock,
                                'error': f'无法解析锁文件内容: {str(e)}'
                            }
                except Exception as e:
                    status[process_type.name] = {
                        'locked': True,
                        'error': f'读取锁文件时发生错误: {str(e)}'
                    }
            else:
                status[process_type.name] = {'locked': False}
        
        return status
    
    @classmethod
    def force_clear_lock_by_type(cls, process_type: ProcessType) -> bool:
        """
        强制清除指定类型的进程锁，只有在调用者是脚本或Web页面时才允许
        
        Args:
            process_type: 进程类型
            
        Returns:
            bool: 是否成功清除
        """
        lock_file = os.path.join(cls._lock_dir, f"cnetCompSpy_{process_type.name.lower()}.lock")
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
                logger.info(f"成功强制清除锁: {process_type.name}")
                return True
            except Exception as e:
                logger.error(f"强制清除锁时发生异常: {e}")
                return False
        return True  # 文件不存在，视为清除成功
