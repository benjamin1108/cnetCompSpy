#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器

提供Web界面用于浏览和查看从各云服务商爬取的博客和文档内容，以及AI分析结果。
"""

import os
import logging
import atexit
from typing import Dict, List, Any

from src.web_server.base_server import BaseServer
from src.web_server.document_manager import DocumentManager
from src.web_server.vendor_manager import VendorManager
from src.web_server.admin_manager import AdminManager
from src.web_server.stats_manager import StatsManager
from src.web_server.route_manager import RouteManager
from src.utils.process_lock_manager import ProcessLockManager, ProcessType
from src.web_server.socket_manager import SocketManager
from src.utils.config_loader import get_config

class WebServer(BaseServer):
    """竞争分析Web服务器类"""
    
    def __init__(self, data_dir: str, host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
        """
        初始化Web服务器
        
        Args:
            data_dir: 数据目录路径
            host: 服务器主机地址
            port: 服务器端口
            debug: 是否启用调试模式
        """
        # 调用父类初始化方法
        super().__init__(data_dir, host, port, debug)
        
        # 获取项目根目录
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # 初始化进程锁管理器 - 仅在非Debug模式下获取锁
        self.process_lock_manager = None
        if not self.debug:
            self.process_lock_manager = ProcessLockManager.get_instance(ProcessType.WEB_SERVER)
            # 获取进程锁
            if not self.process_lock_manager.acquire_lock():
                self.logger.error("无法获取Web服务器进程锁，可能有其他Web服务器实例正在运行")
                self.logger.error("请先关闭现有的Web服务器实例，或使用clear_process_locks.sh脚本清除锁")
                # 抛出异常，阻止Web服务器启动
                raise RuntimeError("无法获取Web服务器进程锁，服务器启动失败")
            
            self.logger.info("已获取Web服务器进程锁")
            # 注册退出时释放锁的函数
            atexit.register(self._release_lock)
        else:
            self.logger.warning("调试模式已启用，进程锁检查被禁用")
        
        # 初始化各个管理器
        enable_access_log = self._init_managers()
        
        # 注册访问记录中间件
        self.register_access_logger(self.stats_manager, self.document_manager, enable_access_log)
        
        # 初始化WebSocket管理器
        self.socket_manager = SocketManager(self.app)
        
        # 注册路由
        self._register_routes()
        
        self.logger.info("Web服务器初始化完成")
    
    def _init_managers(self):
        """初始化各个管理器"""
        # 初始化文档管理器
        self.document_manager = DocumentManager(self.raw_dir, self.analyzed_dir)
        
        # 初始化厂商管理器
        self.vendor_manager = VendorManager(self.raw_dir, self.analyzed_dir, self.document_manager)
        
        # 初始化管理员管理器
        self.admin_manager = AdminManager(self.base_dir)
        
        # 从配置中读取是否启用访问日志
        config = get_config()
        enable_access_log = config.get('webserver', {}).get('enable_access_log', True)
        
        # 初始化统计管理器
        self.stats_manager = StatsManager(self.data_dir, enable_access_log)
        
        return enable_access_log
    
    def _register_routes(self):
        """注册路由"""
        # 初始化路由管理器
        self.route_manager = RouteManager(
            self.app,
            self.document_manager,
            self.vendor_manager,
            self.admin_manager,
            self.stats_manager
        )
    
    def _release_lock(self):
        """释放进程锁"""
        # 仅当 process_lock_manager 存在时才尝试释放（即非Debug模式）
        if hasattr(self, 'process_lock_manager') and self.process_lock_manager:
            self.process_lock_manager.release_lock()
            self.logger.info("已释放Web服务器进程锁")
    
    def shutdown(self):
        """
        关闭Web服务器，确保所有资源被正确释放
        """
        try:
            self.logger.info("正在关闭Web服务器...")
            
            # 关闭统计管理器
            if hasattr(self, 'stats_manager') and self.stats_manager:
                self.stats_manager.shutdown()
            
            # 释放进程锁
            self._release_lock()
            
            self.logger.info("Web服务器已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭Web服务器时出错: {e}")
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        """
        运行Web服务器
        
        Args:
            host: 主机地址，如果为None则使用初始化时的值
            port: 端口，如果为None则使用初始化时的值
            debug: 是否启用调试模式，如果为None则使用初始化时的值
        """
        # 使用初始化时的值作为默认值
        host = host or self.host
        port = port or self.port
        debug = debug if debug is not None else self.debug
        
        # 使用SocketIO运行服务器
        self.logger.info(f"启动Web服务器: {host}:{port}, 调试模式: {debug}")
        self.socket_manager.run(host=host, port=port, debug=debug)
