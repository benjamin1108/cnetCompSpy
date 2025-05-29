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
from datetime import datetime, timedelta
import json
import os

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
            
            # 获取所有厂商的所有更新数据
            all_updates = {}
            if os.path.exists(self.vendor_manager.raw_dir):
                for vendor in os.listdir(self.vendor_manager.raw_dir):
                    vendor_dir = os.path.join(self.vendor_manager.raw_dir, vendor)
                    
                    if os.path.isdir(vendor_dir):
                        vendor_updates = []
                        
                        # 遍历厂商的所有文档类型
                        for doc_type in os.listdir(vendor_dir):
                            type_dir = os.path.join(vendor_dir, doc_type)
                            
                            if os.path.isdir(type_dir):
                                # 遍历此类型下的所有文件
                                for filename in os.listdir(type_dir):
                                    file_path = os.path.join(type_dir, filename)
                                    
                                    if os.path.isfile(file_path) and filename.endswith('.md'):
                                        # 检查是否有AI分析版本
                                        analysis_path = os.path.join(self.vendor_manager.analyzed_dir, vendor, doc_type, filename)
                                        if not os.path.isfile(analysis_path):
                                            continue  # 如果没有分析版本，跳过此文件
                                        
                                        # 提取文档信息
                                        meta = self.document_manager._extract_document_meta(file_path)
                                        date_str = meta.get('date', '')
                                        
                                        # 只获取有日期的文档
                                        if date_str:
                                            try:
                                                # 处理不同的日期格式
                                                import re
                                                from datetime import datetime
                                                
                                                if re.match(r'\d{4}-\d{1,2}-\d{1,2}', date_str):
                                                    doc_date = datetime.strptime(date_str, '%Y-%m-%d')
                                                elif re.match(r'\d{4}_\d{1,2}_\d{1,2}', date_str):
                                                    doc_date = datetime.strptime(date_str, '%Y_%m_%d')
                                                else:
                                                    continue
                                                
                                                # 获取分析文档的翻译标题
                                                translated_title = self.document_manager._extract_translated_title(analysis_path)
                                                original_title = meta.get('title', filename.replace('.md', ''))
                                                
                                                vendor_updates.append({
                                                    'filename': filename,
                                                    'path': f"{vendor}/{doc_type}/{filename}",
                                                    'title': translated_title if translated_title else original_title,
                                                    'original_title': original_title,
                                                    'translated_title': translated_title,
                                                    'date': date_str,
                                                    'doc_type': doc_type,
                                                    'vendor': vendor,
                                                    'size': os.path.getsize(file_path)
                                                })
                                            except (ValueError, TypeError) as e:
                                                self.logger.debug(f"解析日期出错: {date_str}, {e}")
                        
                        # 如果有更新，按日期排序并添加到结果中
                        if vendor_updates:
                            vendor_updates.sort(key=lambda x: x.get('date', ''), reverse=True)
                            all_updates[vendor] = vendor_updates
            
            # 将所有厂商的更新整合成一个按日期排序的列表
            timeline_updates = []
            for vendor, updates in all_updates.items():
                for update in updates:
                    timeline_updates.append(update)
            
            # 按日期降序排序
            timeline_updates.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            # 获取最近7个有更新的日期节点
            unique_dates = set()
            filtered_updates = []
            
            for update in timeline_updates:
                date_str = update.get('date', '')
                if date_str and date_str not in unique_dates:
                    unique_dates.add(date_str)
                    # 找出这个日期的所有更新
                    date_updates = [u for u in timeline_updates if u.get('date', '') == date_str]
                    filtered_updates.extend(date_updates)
                    # 如果已经有7个不同的日期，就停止
                    if len(unique_dates) >= 7:
                        break
            
            return render_template(
                'index.html',
                title='云服务厂商竞争分析',
                vendors=vendors,
                timeline_updates=filtered_updates
            )
        
        # 本周更新页面 - 显示所有厂商本周的更新
        @self.app.route('/weekly-updates')
        def weekly_updates():
            # 计算本周的日期范围
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())  # 周一
            start_of_week = datetime(start_of_week.year, start_of_week.month, start_of_week.day)
            end_of_week = start_of_week + timedelta(days=6)  # 周日
            
            weekly_updates = self.vendor_manager.get_weekly_updates()
            return render_template(
                'weekly_updates.html',
                title='本周更新 - 云服务厂商竞争分析',
                weekly_updates=weekly_updates,
                start_of_week=start_of_week,
                end_of_week=end_of_week
            )
        
        # 今日更新页面 - 显示所有厂商今日的更新
        @self.app.route('/daily-updates')
        def daily_updates():
            # 获取天数参数，默认为1（今日）
            days = request.args.get('days', '1')
            try:
                days = int(days)
                # 限制天数范围在1-7天之间
                days = max(1, min(7, days))
            except ValueError:
                days = 1
            
            # 获取今天的日期
            today = datetime.now()
            
            # 根据天数决定使用哪个函数获取数据
            if days == 1:
                updates = self.vendor_manager.get_daily_updates()
                page_title = '今日更新'
            else:
                updates = self.vendor_manager.get_recently_updates(days=days)
                page_title = f'近{days}天更新'
            
            return render_template(
                'daily_updates.html',
                title=f'{page_title} - 云服务厂商竞争分析',
                daily_updates=updates,
                today=today,
                days=days,
                timedelta=timedelta  # 传递timedelta给模板
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
            
            referrer = request.referrer if request.referrer else url_for('vendor_page', vendor=vendor)
            
            return render_template(
                'document.html',
                title=document_info['meta'].get('title', filename),
                vendor=vendor,
                doc_type=doc_type,
                filename=filename,
                content=document_info['content'],
                meta=document_info['meta'],
                has_analysis=document_info['has_analysis'],
                view_type='raw',
                referrer=referrer
            )
        
        # AI分析文档页面 - 显示特定文档的AI分析内容
        @self.app.route('/analysis/document/<vendor>/<doc_type>/<path:filename>')
        def analysis_document_page(vendor, doc_type, filename):
            analysis_info = self.document_manager.get_analysis_document(vendor, doc_type, filename)
            if not analysis_info:
                self.logger.warning(f"请求的分析文档不存在: {vendor}/{doc_type}/{filename}")
                # 如果没有分析文档，重定向到原始文档页面
                return redirect(url_for('document_page', vendor=vendor, doc_type=doc_type, filename=filename))
            
            referrer = request.referrer if request.referrer else url_for('analysis_page', vendor=vendor)
            
            return render_template(
                'document.html',
                title=analysis_info['title'],
                vendor=vendor,
                doc_type=doc_type,
                filename=filename,
                content=analysis_info['content'],
                meta=analysis_info['meta'],
                has_raw=analysis_info['has_raw'],
                view_type='analysis',
                referrer=referrer
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
        
        # 访问统计页面 - 需要登录
        @self.app.route('/admin/access-stats')
        def admin_access_stats():
            if not self.admin_manager.is_logged_in():
                return redirect(url_for('login', next=request.url))
            
            # Fetch stats data needed directly by the template (PV/UV, top pages)
            try:
                full_stats = self.stats_manager.get_access_stats()
                template_stats = {
                    'week_pv': full_stats.get('week_pv', 0),
                    'week_uv': full_stats.get('week_uv', 0),
                    'today_pv': full_stats.get('today_pv', 0),
                    'today_uv': full_stats.get('today_uv', 0),
                    'total_pv': full_stats.get('total_pv', 0),
                    'total_uv': full_stats.get('total_uv', 0),
                    'top_pages': full_stats.get('top_pages', [])
                }
            except Exception as e:
                 logging.getLogger(__name__).error(f"Error getting stats for template in admin_access_stats: {e}")
                 template_stats = { # Provide default empty values on error
                    'week_pv': 0, 'week_uv': 0, 'today_pv': 0, 'today_uv': 0, 
                    'total_pv': 0, 'total_uv': 0, 'top_pages': []
                 }
            
            return render_template(
                'admin/access_stats.html',
                title='访问统计',
                # Pass the specific stats needed by the template
                access_stats=template_stats 
            )
        
        # 访问详情页面 - 需要登录
        @self.app.route('/admin/access-details')
        def admin_access_details():
            if not self.admin_manager.is_logged_in():
                return redirect(url_for('login', next=request.url))
            
            limit = int(request.args.get('limit', 1000))
            
            # 获取访问详情
            access_details = self.stats_manager.get_access_details(limit=limit)
            
            return render_template(
                'admin/access_details.html',
                title='访问详情',
                access_details=access_details,
                limit=limit
            )
        
        # 数据库管理页面 - 需要登录
        @self.app.route('/admin/database')
        def admin_database():
            if not self.admin_manager.is_logged_in():
                return redirect(url_for('login', next=request.url))
            
            # 获取数据库信息
            db_info = self.stats_manager.get_database_info()
            
            return render_template(
                'admin/database.html',
                title='数据库管理',
                db_info=db_info
            )
        
        # 清理旧记录 - 需要登录
        @self.app.route('/admin/cleanup-records', methods=['POST'])
        def admin_cleanup_records():
            if not self.admin_manager.is_logged_in():
                return jsonify({'error': '用户未登录或权限不足'}), 401
            
            try:
                days = int(request.form.get('days', 90))
                if days < 7:
                    return jsonify({'error': '保留天数不能少于7天'}), 400
                
                self.stats_manager.cleanup_old_records(days)
                return jsonify({'success': True, 'message': f'已清理超过 {days} 天的访问记录'})
            except Exception as e:
                self.logger.error(f"清理旧记录失败: {e}")
                return jsonify({'error': f'清理失败: {e}'}), 500
        
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
        
        # 管理后台实时任务管理页面
        @self.app.route('/admin/tasks-realtime')
        def admin_tasks_realtime():
            if not self.admin_manager.is_logged_in():
                return redirect(url_for('login', next=request.url))
            
            return render_template(
                'admin/tasks_realtime.html',
                title='实时任务管理'
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
        
        # 管理后台进程锁管理页面
        @self.app.route('/admin/process-locks')
        def admin_process_locks():
            if not self.admin_manager.is_logged_in():
                return redirect(url_for('login', next=request.url))
            
            return render_template(
                'admin/process_locks.html',
                title='进程锁管理'
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
        
        # 获取进程锁状态API
        @self.app.route('/api/admin/process-locks')
        def api_process_locks():
            if not self.admin_manager.is_logged_in():
                return jsonify({'success': False, 'error': '未登录'}), 401
            
            try:
                # 获取进程锁状态
                lock_status = self.admin_manager.get_process_lock_status()
                return jsonify({'success': True, 'locks': lock_status})
            except Exception as e:
                self.logger.error(f"获取进程锁状态失败: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # 清除进程锁API
        @self.app.route('/api/admin/clear-process-lock', methods=['POST'])
        def api_clear_process_lock():
            if not self.admin_manager.is_logged_in():
                return jsonify({'success': False, 'error': '未登录'}), 401
            
            process_type = request.json.get('process_type')
            
            if not process_type:
                return jsonify({'success': False, 'error': '未指定进程类型'}), 400
            
            try:
                # 清除进程锁
                result = self.admin_manager.clear_process_lock(process_type)
                return jsonify(result)
            except Exception as e:
                self.logger.error(f"清除进程锁失败: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # --- 新增 API: 获取访问统计图表数据 --- 
        @self.app.route('/api/admin/access-stats-data')
        def api_access_stats_data():
            if not self.admin_manager.is_logged_in():
                return jsonify({'error': '用户未登录或权限不足'}), 401
            
            try:
                access_stats = self.stats_manager.get_access_stats()
                # 只返回图表需要的数据部分，减少传输量 (可选优化)
                chart_data = {
                    'daily_pv_trend': access_stats.get('daily_pv_trend', []),
                    'device_types': access_stats.get('device_types', []),
                    'os_types': access_stats.get('os_types', []),
                    'browser_types': access_stats.get('browser_types', []),
                    # 可以选择性地不返回 PV/UV 等其他数据
                }
                return jsonify(chart_data)
            except Exception as e:
                self.logger.error(f"获取访问统计图表数据失败: {e}")
                return jsonify({'error': f'获取统计数据失败: {e}'}), 500
        # --- 结束新增 API --- 
        
        # API: 搜索文档
        @self.app.route('/api/search')
        def api_search():
            keyword = request.args.get('keyword', '').strip()
            vendor_filter = request.args.get('vendor', '').strip()
            
            if not keyword:
                return jsonify([])
            
            try:
                # 从所有厂商的所有文档中搜索
                search_results = []
                if os.path.exists(self.vendor_manager.raw_dir):
                    for vendor in os.listdir(self.vendor_manager.raw_dir):
                        # 如果指定了厂商过滤，则只搜索指定厂商
                        if vendor_filter and vendor != vendor_filter:
                            continue
                            
                        vendor_dir = os.path.join(self.vendor_manager.raw_dir, vendor)
                        
                        if os.path.isdir(vendor_dir):
                            # 遍历厂商的所有文档类型
                            for doc_type in os.listdir(vendor_dir):
                                type_dir = os.path.join(vendor_dir, doc_type)
                                
                                if os.path.isdir(type_dir):
                                    # 遍历此类型下的所有文件
                                    for filename in os.listdir(type_dir):
                                        file_path = os.path.join(type_dir, filename)
                                        
                                        if os.path.isfile(file_path) and filename.endswith('.md'):
                                            # 检查是否有AI分析版本
                                            analysis_path = os.path.join(self.vendor_manager.analyzed_dir, vendor, doc_type, filename)
                                            
                                            # 提取文档信息
                                            meta = self.document_manager._extract_document_meta(file_path)
                                            title = meta.get('title', filename.replace('.md', ''))
                                            date_str = meta.get('date', '')
                                            
                                            # 获取分析文档的翻译标题
                                            translated_title = ""
                                            if os.path.isfile(analysis_path):
                                                translated_title = self.document_manager._extract_translated_title(analysis_path)
                                            
                                            # 进行关键词匹配 - 同时匹配原始标题和翻译标题
                                            keyword_lower = keyword.lower()
                                            title_match = keyword_lower in title.lower()
                                            translated_title_match = translated_title and keyword_lower in translated_title.lower()
                                            
                                            if title_match or translated_title_match:
                                                search_results.append({
                                                    'filename': filename,
                                                    'path': f"{vendor}/{doc_type}/{filename}",
                                                    'title': title,
                                                    'translated_title': translated_title,
                                                    'vendor': vendor,
                                                    'doc_type': doc_type,
                                                    'date': date_str,
                                                    'has_analysis': os.path.isfile(analysis_path)
                                                })
                
                # 最多返回50个结果
                return jsonify(search_results[:50])
            except Exception as e:
                self.logger.error(f"搜索失败: {e}")
                return jsonify({'error': str(e)}), 500
    
    def _register_error_handlers(self):
        """注册错误处理器"""
        @self.app.errorhandler(404)
        def page_not_found(e):
            # 记录404访问尝试
            if hasattr(self, 'stats_manager') and self.stats_manager:
                # For a 404, the response object isn't readily available here before rendering the template.
                # stats_manager.record_access will infer status 404 if response_obj is None and path_exists is False.
                self.stats_manager.record_access(
                    path=request.path, 
                    document_manager=None, # No specific document context for a generic 404
                    path_exists=False, 
                    response_obj=None 
                )
            return render_template('404.html', error=e, title='页面未找到'), 404
        
        @self.app.errorhandler(500)
        def server_error(e):
            return render_template('error.html', title='服务器错误', error=str(e)), 500
