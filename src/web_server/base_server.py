#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器 - 基础服务器类

提供Web服务器的基本初始化和运行功能。
"""

import os
import logging
from flask import Flask, request, g
from datetime import datetime

class BaseServer:
    """基础Web服务器类"""
    
    def __init__(self, data_dir: str, host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
        """
        初始化基础Web服务器
        
        Args:
            data_dir: 数据目录路径
            host: 服务器主机地址
            port: 服务器端口
            debug: 是否启用调试模式
        """
        self.logger = logging.getLogger(__name__)
        self.data_dir = os.path.abspath(data_dir)
        self.raw_dir = os.path.join(self.data_dir, 'raw')
        self.analyzed_dir = os.path.join(self.data_dir, 'analysis')
        self.host = host
        self.port = port
        self.debug = debug
        
        # 检查数据目录
        self._check_data_directories()
        
        # 创建Flask应用
        self.app = Flask(
            __name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static')
        )
        
        # 配置Flask应用
        self._configure_app()
        
        # 注册上下文处理器
        self._register_context_processors()
        
        self.logger.info(f"基础Web服务器初始化完成，数据目录: {self.data_dir}")
    
    def _check_data_directories(self):
        """检查数据目录是否存在，如果不存在则创建"""
        if not os.path.exists(self.raw_dir):
            self.logger.warning(f"原始数据目录不存在: {self.raw_dir}")
        
        if not os.path.exists(self.analyzed_dir):
            self.logger.warning(f"分析数据目录不存在: {self.analyzed_dir}")
            try:
                os.makedirs(self.analyzed_dir, exist_ok=True)
                self.logger.info(f"已创建分析数据目录: {self.analyzed_dir}")
            except Exception as e:
                self.logger.error(f"创建分析数据目录失败: {e}")
    
    def _configure_app(self):
        """配置Flask应用"""
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传大小为16MB
        self.app.config['SECRET_KEY'] = os.urandom(24)  # 用于会话加密
    
    def _register_context_processors(self):
        """注册上下文处理器"""
        @self.app.context_processor
        def inject_now():
            return {'now': datetime.now()}
    
    def register_access_logger(self, stats_manager, document_manager=None):
        """
        注册访问记录中间件
        
        Args:
            stats_manager: 统计管理器实例
            document_manager: 文档管理器实例，用于获取文档标题
        """
        @self.app.before_request
        def before_request():
            # 忽略静态文件请求
            if not request.path.startswith('/static/'):
                g.stats_manager = stats_manager
                g.document_manager = document_manager
        
        @self.app.after_request
        def after_request(response):
            # 忽略静态文件请求
            if not request.path.startswith('/static/'):
                # 记录访问详情
                if hasattr(g, 'stats_manager'):
                    g.stats_manager.record_access(document_manager=g.document_manager if hasattr(g, 'document_manager') else None)
            return response
    
    def run(self):
        """启动Web服务器"""
        self.logger.info(f"启动Web服务器: http://{self.host}:{self.port}")
        self.app.run(
            host=self.host,
            port=self.port,
            debug=self.debug
        )
