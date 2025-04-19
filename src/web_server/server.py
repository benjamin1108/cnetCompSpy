#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器

提供Web界面用于浏览和查看从各云服务商爬取的博客和文档内容，以及AI分析结果。
"""

import os
import logging
from typing import Dict, List, Any

from src.web_server.base_server import BaseServer
from src.web_server.document_manager import DocumentManager
from src.web_server.vendor_manager import VendorManager
from src.web_server.admin_manager import AdminManager
from src.web_server.stats_manager import StatsManager
from src.web_server.route_manager import RouteManager

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
        
        # 初始化各个管理器
        self._init_managers()
        
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
        
        # 初始化统计管理器
        self.stats_manager = StatsManager(self.data_dir)
    
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
