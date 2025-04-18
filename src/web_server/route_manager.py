#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器 - 路由管理器

负责注册和管理所有的Web路由。
"""

import logging
from typing import Any, Dict, List, Optional
from flask import Flask, render_template, abort, request, jsonify
from flask import redirect, url_for, session, flash

class RouteManager:
    """路由管理器类"""
    
    def __init__(self, app: Flask, document_manager: Any, vendor_manager: Any, 
                 admin_manager: Any, stats_manager: Any):
        """
        初始化路由管理器
        
        Args:
            app: Flask应用实例
            document_manager: 文档管理器实例
            vendor_manager: 厂商管理器实例
            admin_manager: 管理员管理器实例
            stats_manager: 统计管理器实例
        """
        self.logger = logging.getLogger(__name__)
        self.app = app
        self.document_manager = document_manager
        self.vendor_manager = vendor_manager
        self.admin_manager = admin_manager
        self.stats_manager = stats_manager
        
        # 注册所有路由
        self._register_routes()
        
        self.logger.info("路由管理器初始化完成")
    
    def _register_routes(self):
        """注册所有路由"""
        self._register_public_routes()
        self._register_document_routes()
        self._register_admin_routes()
        self._register_api_routes()
        self._register_error_handlers()
    
    def _register_public_routes(self):
        """注册公共路由"""
        # 首页 - 显示所有厂商列表
        @self.app.route('/')
        def index():
            vendors = self.vendor_manager.get_vendors()
            return render_template(
                'index.html',
                title='云服务厂商竞争分析',
                vendors=vendors
            )
        
        # 厂商页面 - 显示特定厂商的所有文档
        @self.app.route('/vendor/<vendor>')
        def vendor_page(vendor):
            if not self.vendor_manager.vendor_exists(vendor):
                abort(404)
            
            docs = self.vendor_manager.get_vendor_docs(vendor)
            has_analysis = self.vendor_manager.vendor_has_analysis(vendor)
            
            return render_template(
                'vendor.html',
                title=f'{vendor.upper()} - 竞争分析',
                vendor=vendor,
                docs=docs,
                has_analysis=has_analysis,
                view_type='raw'
            )
        
        # AI分析厂商页面 - 显示特定厂商的所有AI分析文档
        @self.app.route('/analysis/<vendor>')
        def analysis_page(vendor):
            if not self.vendor_manager.vendor_exists(vendor):
                abort(404)
            
            analysis_docs = self.vendor_manager.get_vendor_analysis(vendor)
            if not analysis_docs:
                self.logger.warning(f"厂商 {vendor} 没有分析文档")
                # 如果没有分析文档，重定向到原始文档页面
                return redirect(url_for('vendor_page', vendor=vendor))
            
            return render_template(
                'vendor.html',
                title=f'{vendor.upper()} - AI分析',
                vendor=vendor,
                docs=analysis_docs,
                has_analysis=True,
                view_type='analysis'
            )
    
    def _register_document_routes(self):
        """注册文档相关路由"""
        # 文档页面 - 显示特定文档内容
        @self.app.route('/document/<vendor>/<doc_type>/<path:filename>')
        def document_page(vendor, doc_type, filename):
            document_info = self.document_manager.get_document(vendor, doc_type, filename)
            if not document_info:
                abort(404)
            
            return render_template(
                'document.html',
                title=document_info['meta'].get('title', filename),
                vendor=vendor,
                doc_type=doc_type,
                filename=filename,
                content=document_info['content'],
                meta=document_info['meta'],
                has_analysis=document_info['has_analysis'],
                view_type='raw'
            )
        
        # AI分析文档页面 - 显示特定文档的AI分析内容
        @self.app.route('/analysis/document/<vendor>/<doc_type>/<path:filename>')
        def analysis_document_page(vendor, doc_type, filename):
            analysis_info = self.document_manager.get_analysis_document(vendor, doc_type, filename)
            if not analysis_info:
                self.logger.warning(f"请求的分析文档不存在: {vendor}/{doc_type}/{filename}")
                # 如果没有分析文档，重定向到原始文档页面
                return redirect(url_for('document_page', vendor=vendor, doc_type=doc_type, filename=filename))
            
            return render_template(
                'document.html',
                title=analysis_info['title'],
                vendor=vendor,
                doc_type=doc_type,
                filename=filename,
                content=analysis_info['content'],
                meta=analysis_info['meta'],
                has_raw=analysis_info['has_raw'],
                view_type='analysis'
            )
        
        # 原始文件 - 提供原始Markdown文件下载
        @self.app.route('/raw/<vendor>/<doc_type>/<path:filename>')
        def raw_file(vendor, doc_type, filename):
            return self.document_manager.get_raw_file(vendor, doc_type, filename)
        
        # 分析文件 - 提供AI分析Markdown文件下载
        @self.app.route('/analysis/raw/<vendor>/<doc_type>/<path:filename>')
        def analysis_raw_file(vendor, doc_type, filename):
            return self.document_manager.get_analysis_raw_file(vendor, doc_type, filename)
    
    def _register_admin_routes(self):
        """注册管理员相关路由"""
        # 统计页面 - 显示文件统计对比（需要登录）
        @self.app.route('/admin/stats')
        def admin_stats_page():
            if not self.admin_manager.is_logged_in():
                return redirect(url_for('login', next=request.url))
                
            return render_template(
                'admin/stats.html',
                title='文件统计对比'
            )
        
        # 兼容旧路径，重定向到新路径
        @self.app.route('/stats')
        def stats_page():
            if not self.admin_manager.is_logged_in():
                return redirect(url_for('login', next=url_for('admin_stats_page')))
            
            return redirect(url_for('admin_stats_page'))
        
        # 登录页面
        @self.app.route('/admin/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                
                if self.admin_manager.authenticate(username, password):
                    next_url = request.args.get('next')
                    if next_url and next_url.startswith('/admin'):
                        return redirect(next_url)
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('用户名或密码错误', 'danger')
            
            return render_template('admin/login.html', title='管理员登录')
        
        # 登出
        @self.app.route('/admin/logout')
        def logout():
            self.admin_manager.logout()
            flash('已成功登出', 'success')
            return redirect(url_for('index'))
        
        # 管理后台首页
        @self.app.route('/admin')
        @self.app.route('/admin/dashboard')
        def admin_dashboard():
            if not self.admin_manager.is_logged_in():
                return redirect(url_for('login', next=request.url))
            
            # 获取统计数据
            stats_data = self.stats_manager.analyze_metadata_files(detailed=False)
            
            return render_template(
                'admin/dashboard.html',
                title='管理后台',
                stats=stats_data
            )
        
        # 管理后台任务页面
        @self.app.route('/admin/tasks')
        def admin_tasks():
            if not self.admin_manager.is_logged_in():
                return redirect(url_for('login', next=request.url))
            
            # 获取可用任务列表
            tasks = self.admin_manager.get_available_tasks()
            
            return render_template(
                'admin/tasks.html',
                title='任务管理',
                tasks=tasks
            )
        
        # 管理后台AI分析任务页面
        @self.app.route('/admin/ai-tasks')
        def admin_ai_tasks():
            if not self.admin_manager.is_logged_in():
                return redirect(url_for('login', next=request.url))
            
            # 获取缺失AI分析的文件
            missing_analysis = self.stats_manager.get_missing_analysis_files()
            
            return render_template(
                'admin/ai_tasks.html',
                title='AI分析任务',
                missing_analysis=missing_analysis
            )
    
    def _register_api_routes(self):
        """注册API路由"""
        # API: 获取统计数据
        @self.app.route('/api/stats')
        def api_stats():
            detailed = request.args.get('detailed', 'false').lower() == 'true'
            
            try:
                # 直接在服务器中分析metadata和文件差异
                stats_data = self.stats_manager.analyze_metadata_files(detailed)
                return jsonify(stats_data)
            except Exception as e:
                self.logger.error(f"获取统计数据失败: {e}")
                return jsonify({'error': str(e)}), 500
        
        # 执行任务API
        @self.app.route('/api/admin/run-task', methods=['POST'])
        def api_run_task():
            if not self.admin_manager.is_logged_in():
                return jsonify({'success': False, 'error': '未登录'}), 401
            
            task = request.json.get('task')
            params = request.json.get('params', {})
            
            if not task:
                return jsonify({'success': False, 'error': '未指定任务'}), 400
            
            try:
                # 执行任务
                result = self.admin_manager.run_task(task, params)
                return jsonify({'success': True, 'result': result})
            except Exception as e:
                self.logger.error(f"执行任务失败: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
    
    def _register_error_handlers(self):
        """注册错误处理器"""
        @self.app.errorhandler(404)
        def page_not_found(e):
            return render_template('404.html', title='页面未找到'), 404
        
        @self.app.errorhandler(500)
        def server_error(e):
            return render_template('error.html', title='服务器错误', error=str(e)), 500
