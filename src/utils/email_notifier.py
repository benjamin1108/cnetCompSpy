#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
邮件通知模块
用于发送爬虫和分析任务的状态通知
"""

import os
import sys
import smtplib
import yaml
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
import datetime
import socket

# 导入彩色日志模块（如果存在）
try:
    from src.utils.colored_logger import ColoredLogger
    logger = ColoredLogger('EmailNotifier')
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('EmailNotifier')


class EmailNotifier:
    """邮件通知类，用于发送任务状态通知"""
    
    def __init__(self, config_path=None, secret_config_path=None):
        """
        初始化邮件通知器
        
        Args:
            config_path: 配置文件路径，默认为项目根目录下的config.yaml
            secret_config_path: 敏感配置文件路径，默认为项目根目录下的config.secret.yaml
        """
        self.config = {}
        self.secret_config = {}
        self.email_config = {}
        
        # 如果未指定配置文件路径，尝试在项目根目录查找
        if config_path is None or secret_config_path is None:
            # 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 推测项目根目录（假设utils是src下的子目录）
            project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
            
            if config_path is None:
                config_path = os.path.join(project_root, 'config.yaml')
                
            if secret_config_path is None:
                secret_config_path = os.path.join(project_root, 'config.secret.yaml')
        
        # 加载主配置文件
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
                
            # 检查是否存在email配置部分
            if 'email' not in self.config:
                logger.warning("配置文件中未找到email部分，将使用默认配置")
                # 设置默认配置
                self.email_config = {
                    'enabled': False,
                    'smtp_server': 'smtp.example.com',
                    'smtp_port': 587,
                    'use_tls': True,
                    'sender': 'your_email@example.com',
                    'recipients': ['recipient@example.com'],
                    'subject_prefix': '[云计算网络竞争动态分析]'
                }
            else:
                self.email_config = self.config['email']
                
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            # 设置默认配置
            self.email_config = {
                'enabled': False,
                'smtp_server': 'smtp.example.com',
                'smtp_port': 587,
                'use_tls': True,
                'sender': 'your_email@example.com',
                'recipients': ['recipient@example.com'],
                'subject_prefix': '[云计算网络竞争动态分析]'
            }
            
        # 加载敏感配置文件
        try:
            if os.path.exists(secret_config_path):
                with open(secret_config_path, 'r', encoding='utf-8') as f:
                    self.secret_config = yaml.safe_load(f)
                logger.info("成功加载敏感配置文件")
            else:
                logger.warning(f"敏感配置文件不存在: {secret_config_path}")
        except Exception as e:
            logger.error(f"加载敏感配置文件失败: {str(e)}")
    
    def _determine_real_status(self, summary, status):
        """
        根据日志摘要信息确定真实的任务状态
        
        Args:
            summary: 日志摘要信息
            status: 原始状态
            
        Returns:
            str: 真实状态（"成功"、"部分成功"或"失败"）
        """
        # 如果没有摘要信息，返回原始状态
        if not summary:
            return status
        
        # 检查是否有错误
        if summary.get('errors', 0) > 0:
            # 检查爬虫和分析任务的成功情况
            crawl_success = summary.get('crawl_tasks', {}).get('success', 0)
            crawl_total = summary.get('crawl_tasks', {}).get('total', 0)
            analyze_success = summary.get('analyze_tasks', {}).get('success', 0)
            analyze_total = summary.get('analyze_tasks', {}).get('total', 0)
            
            # 如果爬虫和分析任务都失败，则返回"失败"
            if crawl_success == 0 and analyze_success == 0:
                return "失败"
            
            # 如果爬虫成功但分析失败，或者有部分任务成功，则返回"部分成功"
            return "部分成功"
        
        # 检查API调用情况
        api_success = summary.get('api_calls', {}).get('success', 0)
        api_total = summary.get('api_calls', {}).get('total', 0)
        api_failed = summary.get('api_calls', {}).get('failed', 0)
        
        # 如果有API调用失败，则返回"部分成功"
        if api_failed > 0 and api_total > 0:
            return "部分成功"
        
        # 检查AI分析任务情况
        ai_success = summary.get('analyze_tasks', {}).get('ai_success', 0)
        ai_total = summary.get('analyze_tasks', {}).get('ai_total', 0)
        ai_failed = summary.get('analyze_tasks', {}).get('ai_failed', 0)
        
        # 如果有AI分析任务失败，则返回"部分成功"
        if ai_failed > 0 and ai_total > 0:
            return "部分成功"
        
        # 如果没有错误和失败，则返回"成功"
        return "成功"
    
    def _generate_status_message(self, summary, status):
        """
        根据日志摘要信息生成状态消息
        
        Args:
            summary: 日志摘要信息
            status: 任务状态
            
        Returns:
            str: 状态消息
        """
        if not summary:
            return "任务执行完成"
        
        messages = []
        
        # 添加爬虫任务信息
        crawl_success = summary.get('crawl_tasks', {}).get('success', 0)
        crawl_total = summary.get('crawl_tasks', {}).get('total', 0)
        crawl_files = summary.get('crawl_files', 0)
        
        if crawl_total > 0:
            if crawl_success == crawl_total:
                messages.append(f"爬虫任务全部成功完成，共爬取 {crawl_files} 个文件")
            elif crawl_success > 0:
                messages.append(f"爬虫任务部分完成 ({crawl_success}/{crawl_total})，共爬取 {crawl_files} 个文件")
            else:
                messages.append("爬虫任务全部失败")
        
        # 添加分析任务信息
        analyze_success = summary.get('analyze_tasks', {}).get('success', 0)
        analyze_total = summary.get('analyze_tasks', {}).get('total', 0)
        analyze_files = summary.get('analyze_files', 0)
        
        if analyze_total > 0:
            if analyze_success == analyze_total:
                messages.append(f"分析任务全部成功完成，共分析 {analyze_files} 个文件")
            elif analyze_success > 0:
                messages.append(f"分析任务部分完成 ({analyze_success}/{analyze_total})，共分析 {analyze_files} 个文件")
            else:
                messages.append("分析任务全部失败")
        
        # 添加AI分析任务信息
        ai_success = summary.get('analyze_tasks', {}).get('ai_success', 0)
        ai_total = summary.get('analyze_tasks', {}).get('ai_total', 0)
        ai_failed = summary.get('analyze_tasks', {}).get('ai_failed', 0)
        
        if ai_total > 0:
            if ai_success == ai_total:
                messages.append(f"AI分析任务全部成功完成 ({ai_success}/{ai_total})")
            elif ai_success > 0:
                messages.append(f"AI分析任务部分完成 ({ai_success}/{ai_total})")
            else:
                messages.append("AI分析任务全部失败")
        
        # 添加错误和警告信息
        errors = summary.get('errors', 0)
        warnings = summary.get('warnings', 0)
        
        if errors > 0 or warnings > 0:
            messages.append(f"执行过程中出现 {errors} 个错误和 {warnings} 个警告")
        
        # 组合消息
        if messages:
            return "，".join(messages)
        else:
            return "任务执行完成"
    
    def send_notification(self, status, message, log_file=None):
        """
        发送通知邮件
        
        Args:
            status: 状态，如"成功"、"失败"、"部分成功"等
            message: 通知消息内容
            log_file: 日志文件路径，如果提供则会附加日志内容
        
        Returns:
            bool: 发送成功返回True，否则返回False
        """
        # 检查邮件功能是否启用
        if not self.email_config.get('enabled', False):
            logger.info("邮件通知功能未启用，跳过发送")
            return False
        
        try:
            # 获取日志内容和摘要信息
            formatted_log = ""
            summary = {}
            if log_file:
                formatted_log, summary = self._get_log_content(log_file)
                
                # 根据日志分析结果确定真实状态
                real_status = self._determine_real_status(summary, status)
                if real_status != status:
                    logger.info(f"根据日志分析，将状态从 {status} 调整为 {real_status}")
                    status = real_status
                
                # 生成更详细的状态消息
                detailed_message = self._generate_status_message(summary, status)
                if detailed_message != message:
                    logger.info(f"根据日志分析，生成更详细的状态消息: {detailed_message}")
                    message = detailed_message
            
            # 创建邮件对象
            msg = MIMEMultipart()
            
            # 设置邮件主题
            subject_prefix = self.email_config.get('subject_prefix', '[云计算网络竞争动态分析]')
            msg['Subject'] = Header(f"{subject_prefix} {status} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'utf-8')
            
            # 从敏感配置文件中获取用户名
            username = ''
            if self.secret_config and 'email' in self.secret_config and 'username' in self.secret_config['email']:
                username = self.secret_config['email']['username']
            
            # 设置发件人
            sender = self.email_config.get('sender', username)
            msg['From'] = sender
            
            # 设置收件人
            recipients = self.email_config.get('recipients', [])
            if isinstance(recipients, list):
                msg['To'] = ', '.join(recipients)
            else:
                msg['To'] = str(recipients)
            
            # 构建邮件内容
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            # 构建任务详情表格
            task_details = ""
            if summary:
                # 构建爬虫任务详情
                crawl_success = summary.get('crawl_tasks', {}).get('success', 0)
                crawl_total = summary.get('crawl_tasks', {}).get('total', 0)
                crawl_rate = f"{crawl_success}/{crawl_total}" if crawl_total > 0 else "0/0"
                
                # 构建分析任务详情
                analyze_success = summary.get('analyze_tasks', {}).get('success', 0)
                analyze_total = summary.get('analyze_tasks', {}).get('total', 0)
                analyze_rate = f"{analyze_success}/{analyze_total}" if analyze_total > 0 else "0/0"
                
                # 构建AI分析任务详情
                ai_success = summary.get('analyze_tasks', {}).get('ai_success', 0)
                ai_total = summary.get('analyze_tasks', {}).get('ai_total', 0)
                ai_rate = f"{ai_success}/{ai_total}" if ai_total > 0 else "0/0"
                
                # 构建API调用详情
                api_success = summary.get('api_calls', {}).get('success', 0)
                api_total = summary.get('api_calls', {}).get('total', 0)
                api_rate = f"{api_success}/{api_total}" if api_total > 0 else "0/0"
                
                task_details = f"""
                <div class="task-details">
                    <h3>任务详情</h3>
                    <table class="task-table">
                        <tr>
                            <th>任务类型</th>
                            <th>成功率</th>
                            <th>状态</th>
                        </tr>
                        <tr>
                            <td>爬虫任务</td>
                            <td>{crawl_rate}</td>
                            <td class="{self._get_status_class(crawl_success, crawl_total)}">{self._get_status_text(crawl_success, crawl_total)}</td>
                        </tr>
                        <tr>
                            <td>分析任务</td>
                            <td>{analyze_rate}</td>
                            <td class="{self._get_status_class(analyze_success, analyze_total)}">{self._get_status_text(analyze_success, analyze_total)}</td>
                        </tr>
                        <tr>
                            <td>AI分析任务</td>
                            <td>{ai_rate}</td>
                            <td class="{self._get_status_class(ai_success, ai_total)}">{self._get_status_text(ai_success, ai_total)}</td>
                        </tr>
                        <tr>
                            <td>API调用</td>
                            <td>{api_rate}</td>
                            <td class="{self._get_status_class(api_success, api_total)}">{self._get_status_text(api_success, api_total)}</td>
                        </tr>
                    </table>
                </div>
                """
            
            # 构建摘要表格
            summary_table = ""
            if summary:
                vendors_str = ', '.join(summary['vendors']) if summary['vendors'] else '无'
                duration_str = summary['duration'] if summary['duration'] else '未知'
                
                summary_table = f"""
                <div class="summary">
                    <h3>任务摘要</h3>
                    <table class="summary-table">
                        <tr>
                            <th>开始时间</th>
                            <td>{summary.get('start_time', '未知')}</td>
                            <th>结束时间</th>
                            <td>{summary.get('end_time', '未知')}</td>
                        </tr>
                        <tr>
                            <th>持续时间</th>
                            <td>{duration_str}</td>
                            <th>处理厂商</th>
                            <td>{vendors_str}</td>
                        </tr>
                        <tr>
                            <th>爬取文件数</th>
                            <td>{summary.get('crawl_files', 0)}</td>
                            <th>分析文件数</th>
                            <td>{summary.get('analyze_files', 0)}</td>
                        </tr>
                        <tr>
                            <th>错误数</th>
                            <td class="error-count">{summary.get('errors', 0)}</td>
                            <th>警告数</th>
                            <td class="warning-count">{summary.get('warnings', 0)}</td>
                        </tr>
                    </table>
                </div>
                """
            
            # 构建错误和警告详情
            error_warning_details = ""
            if summary and (summary.get('error_details') or summary.get('warning_details')):
                error_warning_details = "<div class='error-warning-details'><h3>错误和警告详情</h3>"
                
                if summary.get('error_details'):
                    error_warning_details += "<div class='error-details'><h4>错误详情</h4><ul>"
                    for error in summary['error_details']:
                        error_warning_details += f"<li>{error}</li>"
                    error_warning_details += "</ul></div>"
                
                if summary.get('warning_details'):
                    error_warning_details += "<div class='warning-details'><h4>警告详情</h4><ul>"
                    for warning in summary['warning_details']:
                        error_warning_details += f"<li>{warning}</li>"
                    error_warning_details += "</ul></div>"
                
                error_warning_details += "</div>"
            
            email_content = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4285f4; color: white; padding: 15px; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #fff; padding: 20px; border-radius: 0 0 5px 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #666; text-align: center; }}
        .status-box {{ padding: 10px; margin-bottom: 15px; border-radius: 5px; }}
        .success {{ background-color: #d4edda; color: #155724; }}
        .failure {{ background-color: #f8d7da; color: #721c24; }}
        .partial {{ background-color: #fff3cd; color: #856404; }}
        .info-box {{ background-color: #e9ecef; padding: 10px; margin-bottom: 15px; border-radius: 5px; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow: auto; font-size: 13px; }}
        .summary {{ margin: 20px 0; }}
        .summary-table, .task-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        .summary-table th, .summary-table td, .task-table th, .task-table td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        .summary-table th, .task-table th {{ background-color: #f2f2f2; width: 25%; }}
        .error-count {{ color: #dc3545; font-weight: bold; }}
        .warning-count {{ color: #ffc107; font-weight: bold; }}
        .log-container {{ margin-top: 20px; }}
        .log-section {{ margin-bottom: 20px; }}
        .error-section h4 {{ color: #dc3545; }}
        .warning-section h4 {{ color: #ffc107; }}
        .info-section h4 {{ color: #17a2b8; }}
        .error-log {{ border-left: 4px solid #dc3545; }}
        .warning-log {{ border-left: 4px solid #ffc107; }}
        .info-log {{ border-left: 4px solid #17a2b8; }}
        .error-warning-details {{ margin: 20px 0; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }}
        .error-details h4 {{ color: #dc3545; }}
        .warning-details h4 {{ color: #ffc107; }}
        .error-details ul, .warning-details ul {{ margin: 10px 0; padding-left: 20px; }}
        .error-details li {{ color: #721c24; }}
        .warning-details li {{ color: #856404; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>云计算网络竞争动态分析 - 任务状态通知</h2>
        </div>
        <div class="content">
            <div class="status-box {status.lower() if status in ['成功', '失败', '部分成功'] else ''}">
                <strong>状态:</strong> {status}
            </div>
            
            <div class="info-box">
                <p><strong>消息:</strong> {message}</p>
                <p><strong>执行时间:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>主机名:</strong> {hostname}</p>
                <p><strong>IP地址:</strong> {ip_address}</p>
            </div>
            
            {task_details}
            
            {summary_table}
            
            {error_warning_details}
            
            {formatted_log if log_file else ''}
        </div>
        <div class="footer">
            <p>此邮件由系统自动发送，请勿回复。</p>
        </div>
    </div>
</body>
</html>
"""
            
            # 添加HTML内容
            msg.attach(MIMEText(email_content, 'html', 'utf-8'))
            
            # 添加日志文件作为附件（完整原始日志）
            if log_file and os.path.exists(log_file):
                try:
                    # 读取完整的原始日志文件
                    with open(log_file, 'rb') as f:
                        log_content = f.read()
                    
                    # 创建附件
                    log_attachment = MIMEApplication(log_content)
                    log_attachment.add_header('Content-Disposition', 'attachment', 
                                             filename=f"完整日志_{os.path.basename(log_file)}")
                    msg.attach(log_attachment)
                    
                    logger.info(f"已添加完整原始日志文件作为附件: {log_file} (大小: {len(log_content)} 字节)")
                except Exception as e:
                    logger.warning(f"添加日志文件附件失败: {str(e)}")
            
            # 连接SMTP服务器并发送邮件
            smtp_server = self.email_config.get('smtp_server', '')
            smtp_port = self.email_config.get('smtp_port', 587)
            use_tls = self.email_config.get('use_tls', True)
            
            # 从敏感配置文件中获取用户名和密码
            username = ''
            password = ''
            if self.secret_config and 'email' in self.secret_config:
                if 'username' in self.secret_config['email']:
                    username = self.secret_config['email']['username']
                else:
                    logger.warning("未在敏感配置文件中找到邮箱用户名，邮件发送可能会失败")
                
                if 'password' in self.secret_config['email']:
                    password = self.secret_config['email']['password']
                else:
                    logger.warning("未在敏感配置文件中找到邮箱密码，邮件发送可能会失败")
            else:
                logger.warning("未在敏感配置文件中找到email配置，邮件发送可能会失败")
            
            logger.info(f"正在连接SMTP服务器: {smtp_server}:{smtp_port}")
            server = smtplib.SMTP(smtp_server, smtp_port)
            
            if use_tls:
                logger.info("启用TLS加密")
                server.starttls()
            
            if username and password:
                logger.info(f"使用账号 {username} 登录")
                server.login(username, password)
            
            logger.info(f"正在发送邮件到: {recipients}")
            server.sendmail(sender, recipients if isinstance(recipients, list) else [recipients], msg.as_string())
            server.quit()
            
            logger.info("邮件发送成功")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            return False
    
    def _get_status_class(self, success, total):
        """
        根据成功率获取状态样式类
        
        Args:
            success: 成功数量
            total: 总数量
            
        Returns:
            str: 状态样式类
        """
        if total == 0:
            return ""
        
        rate = success / total
        if rate == 1:
            return "success"
        elif rate >= 0.5:
            return "partial"
        else:
            return "failure"
    
    def _get_status_text(self, success, total):
        """
        根据成功率获取状态文本
        
        Args:
            success: 成功数量
            total: 总数量
            
        Returns:
            str: 状态文本
        """
        if total == 0:
            return "无任务"
        
        rate = success / total
        if rate == 1:
            return "全部成功"
        elif rate >= 0.5:
            return "部分成功"
        else:
            return "大部分失败"
    
    def _remove_ansi_colors(self, text):
        """
        移除文本中的ANSI颜色代码
        
        Args:
            text: 包含ANSI颜色代码的文本
            
        Returns:
            str: 移除颜色代码后的文本
        """
        import re
        # 匹配ANSI颜色代码的正则表达式
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _parse_log_for_summary(self, log_content):
        """
        从日志内容中解析出摘要信息
        
        Args:
            log_content: 日志内容
            
        Returns:
            dict: 包含摘要信息的字典
        """
        import re
        
        summary = {
            'crawl_files': 0,
            'analyze_files': 0,
            'vendors': set(),
            'errors': 0,
            'warnings': 0,
            'start_time': '',
            'end_time': '',
            'duration': '',
            'crawl_tasks': {'total': 0, 'success': 0, 'failed': 0},
            'analyze_tasks': {'total': 0, 'success': 0, 'failed': 0},
            'api_calls': {'total': 0, 'success': 0, 'failed': 0},
            'error_details': [],
            'warning_details': []
        }
        
        # 查找开始时间
        start_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[INFO\] ===== 开始每日爬取与分析任务', log_content)
        if start_match:
            summary['start_time'] = start_match.group(1)
        
        # 查找结束时间
        end_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[INFO\] ===== 每日爬取与分析任务(成功)?完成', log_content)
        if end_match:
            summary['end_time'] = end_match.group(1)
        else:
            # 尝试从其他日志行中提取结束时间
            alt_end_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[INFO\] 分析功能成功完成', log_content)
            if alt_end_match:
                summary['end_time'] = alt_end_match.group(1)
            else:
                # 如果找不到结束时间，使用最后一条日志的时间
                last_time_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', log_content.strip().split('\n')[-1])
                if last_time_match:
                    summary['end_time'] = last_time_match.group(1)
        
        # 如果有开始和结束时间，计算持续时间
        if summary['start_time'] and summary['end_time']:
            try:
                from datetime import datetime
                start = datetime.strptime(summary['start_time'], '%Y-%m-%d %H:%M:%S')
                end = datetime.strptime(summary['end_time'], '%Y-%m-%d %H:%M:%S')
                duration = end - start
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                summary['duration'] = f"{hours}小时{minutes}分钟{seconds}秒"
            except Exception:
                summary['duration'] = '未知'
        
        # 查找爬虫任务信息
        crawl_start = re.search(r'\[INFO\] 开始爬取数据', log_content)
        if crawl_start:
            summary['crawl_tasks']['total'] += 1
            
            # 检查爬虫是否成功完成
            if re.search(r'\[INFO\] 爬虫功能成功完成', log_content):
                summary['crawl_tasks']['success'] += 1
            else:
                summary['crawl_tasks']['failed'] += 1
        
        # 查找分析任务信息
        analyze_start = re.search(r'\[INFO\] 开始分析数据', log_content)
        if analyze_start:
            summary['analyze_tasks']['total'] += 1
            
            # 检查分析是否成功完成
            if re.search(r'\[INFO\] 分析功能成功完成', log_content):
                summary['analyze_tasks']['success'] += 1
            else:
                summary['analyze_tasks']['failed'] += 1
        
        # 如果找到了分析文件数，但分析任务数为0，则设置分析任务数为1
        if summary.get('analyze_files', 0) > 0 and summary['analyze_tasks']['total'] == 0:
            summary['analyze_tasks']['total'] = 1
            summary['analyze_tasks']['success'] = 1
            logger.info(f"根据分析文件数({summary['analyze_files']})推断分析任务数为1")
        
        # 查找处理的厂商
        vendor_match = re.search(r'--vendor (\w+)', log_content)
        if vendor_match:
            vendor = vendor_match.group(1)
            summary['vendors'].add(vendor)
            logger.info(f"从命令行参数中识别到厂商: {vendor}")
        
        # 查找爬取的文件数量（汇总所有厂商）
        crawl_files_total = 0
        for match in re.finditer(r'爬取完成: (\w+) \w+, 共 (\d+) 个文件', log_content):
            vendor = match.group(1)
            files = int(match.group(2))
            crawl_files_total += files
            summary['vendors'].add(vendor)
        
        # 如果在日志中找到了爬取文件数量，则使用该值
        if crawl_files_total > 0:
            summary['crawl_files'] = crawl_files_total
        else:
            # 尝试从其他日志行中提取爬取文件数量
            alt_crawl_match = re.search(r'共爬取 (\d+) 个文件', log_content)
            if alt_crawl_match:
                summary['crawl_files'] = int(alt_crawl_match.group(1))
        
        # 查找分析的文件数量
        analyze_match = re.search(r'找到 (\d+) 个文件需要分析', log_content)
        if analyze_match:
            summary['analyze_files'] = int(analyze_match.group(1))
        else:
            # 尝试从其他日志行中提取分析文件数量
            alt_analyze_match = re.search(r'将分析 (\d+) 个文件', log_content)
            if alt_analyze_match:
                summary['analyze_files'] = int(alt_analyze_match.group(1))
            else:
                # 尝试从强制模式日志中提取
                force_analyze_match = re.search(r'强制模式已启用，将分析 (\d+) 个文件', log_content)
                if force_analyze_match:
                    summary['analyze_files'] = int(force_analyze_match.group(1))
        
        # 查找AI分析任务信息
        ai_tasks_total = len(re.findall(r'执行任务 \[\d+/\d+\]:', log_content))
        ai_tasks_success = len(re.findall(r'已将任务 .+ 的分析结果写入文件', log_content))
        ai_tasks_failed = len(re.findall(r'任务 .+ 执行失败', log_content))
        
        # 如果找不到任务信息，尝试从其他日志行中提取
        if ai_tasks_total == 0:
            # 尝试从"将执行 X 个分析任务"中提取
            ai_tasks_match = re.search(r'将执行 (\d+) 个分析任务', log_content)
            if ai_tasks_match:
                ai_tasks_total = int(ai_tasks_match.group(1))
        
        # 如果找不到成功任务数，但有总任务数，尝试计算
        if ai_tasks_success == 0 and ai_tasks_total > 0 and ai_tasks_failed > 0:
            ai_tasks_success = ai_tasks_total - ai_tasks_failed
        
        summary['analyze_tasks']['ai_total'] = ai_tasks_total
        summary['analyze_tasks']['ai_success'] = ai_tasks_success
        summary['analyze_tasks']['ai_failed'] = ai_tasks_failed
        
        # 查找API调用信息
        api_calls_total = len(re.findall(r'开始调用AI模型进行', log_content))
        api_calls_success = len(re.findall(r'API调用成功: 状态码 200', log_content))
        api_calls_failed = len(re.findall(r'API调用失败', log_content))
        
        # 如果找不到API调用失败数，尝试从错误日志中提取
        if api_calls_failed == 0:
            api_calls_failed = len(re.findall(r'达到最大重试次数', log_content))
        
        # 如果找不到API调用成功数，但有总调用数，尝试计算
        if api_calls_success == 0 and api_calls_total > 0 and api_calls_failed > 0:
            api_calls_success = api_calls_total - api_calls_failed
        
        summary['api_calls']['total'] = api_calls_total
        summary['api_calls']['success'] = api_calls_success
        summary['api_calls']['failed'] = api_calls_failed
        
        # 查找错误和警告数量
        errors = re.findall(r'\[ERROR\]', log_content)
        warnings = re.findall(r'\[WARNING\]', log_content)
        summary['errors'] = len(errors)
        summary['warnings'] = len(warnings)
        
        # 提取错误和警告详情
        error_lines = []
        warning_lines = []
        
        for line in log_content.split('\n'):
            if '[ERROR]' in line:
                # 提取错误信息，去除时间戳和日志级别
                error_msg = re.sub(r'^\[.*?\] \[ERROR\] ', '', line).strip()
                if error_msg and len(error_msg) > 5:  # 过滤掉太短的错误信息
                    error_lines.append(error_msg)
            elif '[WARNING]' in line:
                # 提取警告信息，去除时间戳和日志级别
                warning_msg = re.sub(r'^\[.*?\] \[WARNING\] ', '', line).strip()
                if warning_msg and len(warning_msg) > 5:  # 过滤掉太短的警告信息
                    warning_lines.append(warning_msg)
        
        # 去重并保留最重要的错误和警告（最多10条）
        summary['error_details'] = list(dict.fromkeys(error_lines))[:10]
        summary['warning_details'] = list(dict.fromkeys(warning_lines))[:10]
        
        return summary
    
    def _format_log_content(self, log_content):
        """
        格式化日志内容，按级别分类并添加HTML样式
        
        Args:
            log_content: 原始日志内容
            
        Returns:
            str: 格式化后的HTML内容
        """
        import re
        
        # 移除ANSI颜色代码
        clean_log = self._remove_ansi_colors(log_content)
        
        # 将日志按级别分类
        info_logs = []
        warning_logs = []
        error_logs = []
        
        for line in clean_log.split('\n'):
            if '[ERROR]' in line:
                error_logs.append(line)
            elif '[WARNING]' in line:
                warning_logs.append(line)
            elif '[INFO]' in line:
                info_logs.append(line)
        
        # 构建HTML格式的日志内容
        html_log = '<div class="log-container">'
        
        if error_logs:
            html_log += '<div class="log-section error-section">'
            html_log += '<h4>错误日志</h4>'
            html_log += '<pre class="error-log">'
            html_log += '\n'.join(error_logs)
            html_log += '</pre></div>'
        
        if warning_logs:
            html_log += '<div class="log-section warning-section">'
            html_log += '<h4>警告日志</h4>'
            html_log += '<pre class="warning-log">'
            html_log += '\n'.join(warning_logs)
            html_log += '</pre></div>'
        
        html_log += '<div class="log-section info-section">'
        html_log += '<h4>信息日志</h4>'
        html_log += '<pre class="info-log">'
        html_log += '\n'.join(info_logs[-50:]) if len(info_logs) > 50 else '\n'.join(info_logs)
        html_log += '</pre></div>'
        
        html_log += '</div>'
        
        return html_log
    
    def _get_log_content(self, log_file):
        """
        获取日志文件内容，并进行格式化处理
        
        Args:
            log_file: 日志文件路径
        
        Returns:
            tuple: (格式化后的日志内容, 日志摘要信息)
        """
        if not log_file or not os.path.exists(log_file):
            return "日志文件不存在", {}
        
        try:
            # 读取日志文件内容
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # 解析日志获取摘要信息
            summary = self._parse_log_for_summary(log_content)
            
            # 格式化日志内容
            formatted_log = self._format_log_content(log_content)
            
            return formatted_log, summary
        except Exception as e:
            return f"读取日志文件失败: {str(e)}", {}


def main():
    """
    命令行入口函数
    """
    parser = argparse.ArgumentParser(description="邮件通知工具")
    parser.add_argument("--status", default="成功", help="通知状态，如'成功'、'失败'、'部分成功'等")
    parser.add_argument("--message", default="任务执行完成", help="通知消息内容")
    parser.add_argument("--log-file", dest="log_file", help="日志文件路径，如果提供则会附加日志内容")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--secret-config", dest="secret_config", help="敏感配置文件路径")
    
    args = parser.parse_args()
    
    # 创建邮件通知器
    notifier = EmailNotifier(args.config, args.secret_config)
    
    # 发送通知
    result = notifier.send_notification(args.status, args.message, args.log_file)
    
    # 根据发送结果设置退出代码
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
