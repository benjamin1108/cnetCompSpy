#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WebSocket管理器

负责管理WebSocket连接和事件处理。
"""

import logging
import json
from typing import Dict, Any, List, Set
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room

from src.utils.task_manager import TaskManager

logger = logging.getLogger(__name__)

class SocketManager:
    """WebSocket管理器类"""
    
    def __init__(self, app: Flask):
        """
        初始化WebSocket管理器
        
        Args:
            app: Flask应用实例
        """
        self.logger = logging.getLogger(__name__)
        self.app = app
        
        # 创建SocketIO实例
        # 不指定 async_mode，让 Flask-SocketIO 自动选择最佳模式
        self.socketio = SocketIO(app, cors_allowed_origins="*")
        
        # 获取任务管理器实例
        self.task_manager = TaskManager()
        
        # 注册事件处理函数
        self._register_event_handlers()
        
        # 任务订阅字典，键为任务ID，值为订阅该任务的会话ID集合
        self.task_subscriptions: Dict[str, Set[str]] = {}
        
        self.logger.info("WebSocket管理器初始化完成")
    
    def _register_event_handlers(self):
        """注册事件处理函数"""
        # 连接事件
        @self.socketio.on('connect')
        def handle_connect(auth):
            from flask import request
            self.logger.info(f"客户端连接: {request.sid}")
        
        # 断开连接事件
        @self.socketio.on('disconnect')
        def handle_disconnect(reason):
            from flask import request
            session_id = request.sid
            self.logger.info(f"客户端断开连接: {session_id}, 原因: {reason}")
            
            # 清理该会话的所有订阅
            self._clean_subscriptions(session_id)
        
        # 订阅任务事件
        @self.socketio.on('subscribe_task')
        def handle_subscribe_task(data):
            from flask import request
            session_id = request.sid
            task_id = data.get('task_id')
            
            if not task_id:
                self.logger.warning(f"订阅任务失败: 未提供任务ID")
                emit('error', {'message': '未提供任务ID'})
                return
            
            # 获取任务信息
            task = self.task_manager.get_task(task_id)
            if not task:
                self.logger.warning(f"订阅任务失败: 任务不存在 - {task_id}")
                emit('error', {'message': f'任务不存在: {task_id}'})
                return
            
            # 加入任务房间
            join_room(f"task_{task_id}")
            
            # 添加到订阅字典
            if task_id not in self.task_subscriptions:
                self.task_subscriptions[task_id] = set()
            self.task_subscriptions[task_id].add(session_id)
            
            self.logger.debug(f"客户端 {session_id} 订阅任务: {task_id}")
            
            # 发送任务初始状态
            emit('task_update', task.to_dict())
            
            # 如果任务正在运行，添加输出回调
            if task.status.name == 'RUNNING':
                task.add_output_callback(lambda line: self._emit_task_output(task_id, line))
        
        # 取消订阅任务事件
        @self.socketio.on('unsubscribe_task')
        def handle_unsubscribe_task(data):
            from flask import request
            session_id = request.sid
            task_id = data.get('task_id')
            
            if not task_id:
                self.logger.warning(f"取消订阅任务失败: 未提供任务ID")
                emit('error', {'message': '未提供任务ID'})
                return
            
            # 离开任务房间
            leave_room(f"task_{task_id}")
            
            # 从订阅字典中移除
            if task_id in self.task_subscriptions:
                if session_id in self.task_subscriptions[task_id]:
                    self.task_subscriptions[task_id].remove(session_id)
                
                # 如果没有订阅者，清理订阅
                if not self.task_subscriptions[task_id]:
                    del self.task_subscriptions[task_id]
            
            self.logger.debug(f"客户端 {session_id} 取消订阅任务: {task_id}")
            emit('unsubscribed', {'task_id': task_id})
        
        # 获取所有任务事件
        @self.socketio.on('get_all_tasks')
        def handle_get_all_tasks():
            tasks = self.task_manager.get_all_tasks()
            emit('all_tasks', {'tasks': tasks})
        
        # 获取运行中的任务事件
        @self.socketio.on('get_running_tasks')
        def handle_get_running_tasks():
            tasks = self.task_manager.get_running_tasks()
            emit('running_tasks', {'tasks': tasks})
        
        # 获取任务详情事件
        @self.socketio.on('get_task_details')
        def handle_get_task_details(data):
            task_id = data.get('task_id')
            
            if not task_id:
                self.logger.warning(f"获取任务详情失败: 未提供任务ID")
                emit('error', {'message': '未提供任务ID'})
                return
            
            # 获取任务信息
            task = self.task_manager.get_task(task_id)
            if not task:
                self.logger.warning(f"获取任务详情失败: 任务不存在 - {task_id}")
                emit('error', {'message': f'任务不存在: {task_id}'})
                return
            
            emit('task_details', task.to_dict())
        
        # 取消任务事件
        @self.socketio.on('cancel_task')
        def handle_cancel_task(data):
            task_id = data.get('task_id')
            
            if not task_id:
                self.logger.warning(f"取消任务失败: 未提供任务ID")
                emit('error', {'message': '未提供任务ID'})
                return
            
            # 取消任务
            result = self.task_manager.cancel_task(task_id)
            
            if result:
                self.logger.info(f"取消任务成功: {task_id}")
                
                # 获取最新任务状态
                task = self.task_manager.get_task(task_id)
                if task:
                    # 广播任务状态更新
                    self.socketio.emit('task_update', task.to_dict(), room=f"task_{task_id}")
                
                emit('task_canceled', {'task_id': task_id, 'success': True})
            else:
                self.logger.warning(f"取消任务失败: {task_id}")
                emit('task_canceled', {'task_id': task_id, 'success': False})
        
        # 删除任务事件
        @self.socketio.on('delete_task')
        def handle_delete_task(data):
            task_id = data.get('task_id')
            
            if not task_id:
                self.logger.warning(f"删除任务失败: 未提供任务ID")
                emit('error', {'message': '未提供任务ID'})
                return
            
            # 删除任务
            result = self.task_manager.delete_task(task_id)
            
            if result:
                self.logger.info(f"删除任务成功: {task_id}")
                
                # 广播任务删除事件
                self.socketio.emit('task_deleted', {'task_id': task_id}, room=f"task_{task_id}")
                
                emit('task_deleted', {'task_id': task_id, 'success': True})
            else:
                self.logger.warning(f"删除任务失败: {task_id}")
                emit('task_deleted', {'task_id': task_id, 'success': False})
    
    def _get_session_id(self) -> str:
        """
        获取当前会话ID
        
        Returns:
            str: 会话ID
        """
        from flask import request
        return request.sid
    
    def _clean_subscriptions(self, session_id: str):
        """
        清理指定会话的所有订阅
        
        Args:
            session_id: 会话ID
        """
        # 遍历所有任务订阅
        for task_id in list(self.task_subscriptions.keys()):
            if session_id in self.task_subscriptions[task_id]:
                self.task_subscriptions[task_id].remove(session_id)
                
                # 如果没有订阅者，清理订阅
                if not self.task_subscriptions[task_id]:
                    del self.task_subscriptions[task_id]
    
    def _emit_task_output(self, task_id: str, line: str):
        """
        发送任务输出
        
        Args:
            task_id: 任务ID
            line: 输出行
        """
        self.socketio.emit('task_output', {
            'task_id': task_id,
            'line': line
        }, room=f"task_{task_id}")
    
    def emit_task_update(self, task_id: str, task_data: Dict[str, Any]):
        """
        发送任务状态更新
        
        Args:
            task_id: 任务ID
            task_data: 任务数据
        """
        self.socketio.emit('task_update', task_data, room=f"task_{task_id}")
    
    def register_task_output_callback(self, task_id: str):
        """
        注册任务输出回调
        
        Args:
            task_id: 任务ID
        """
        task = self.task_manager.get_task(task_id)
        if task and task.status.name == 'RUNNING':
            task.add_output_callback(lambda line: self._emit_task_output(task_id, line))
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """
        运行WebSocket服务器
        
        Args:
            host: 主机地址
            port: 端口
            debug: 是否启用调试模式
        """
        self.socketio.run(self.app, host=host, port=port, debug=debug)
