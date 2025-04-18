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
            
            email_content = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ padding: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .content {{ margin: 20px 0; }}
        .footer {{ font-size: 12px; color: #666; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .partial {{ color: orange; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>云计算网络竞争动态分析 - 任务状态通知</h2>
        </div>
        <div class="content">
            <p>状态: <span class="{status.lower() if status in ['成功', '失败', '部分成功'] else ''}">{status}</span></p>
            <p>消息: {message}</p>
            <p>执行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>主机名: {hostname}</p>
            <p>IP地址: {ip_address}</p>
            
            {f'<h3>日志内容:</h3><pre>{self._get_log_content(log_file)}</pre>' if log_file else ''}
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
    
    def _get_log_content(self, log_file):
        """
        获取日志文件内容
        
        Args:
            log_file: 日志文件路径
        
        Returns:
            str: 日志文件内容，如果文件不存在或读取失败则返回错误信息
        """
        if not log_file or not os.path.exists(log_file):
            return "日志文件不存在"
        
        try:
            # 读取最后100行日志
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) > 100:
                    return "...\n" + ''.join(lines[-100:])
                return ''.join(lines)
        except Exception as e:
            return f"读取日志文件失败: {str(e)}"


def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description='发送邮件通知')
    parser.add_argument('--status', required=True, help='通知状态，如"成功"、"失败"、"部分成功"等')
    parser.add_argument('--message', required=True, help='通知消息内容')
    parser.add_argument('--log-file', help='日志文件路径，如果提供则会附加日志内容')
    parser.add_argument('--config', help='配置文件路径，默认为项目根目录下的config.yaml')
    parser.add_argument('--secret-config', help='敏感配置文件路径，默认为项目根目录下的config.secret.yaml')
    
    args = parser.parse_args()
    
    notifier = EmailNotifier(args.config, args.secret_config)
    result = notifier.send_notification(args.status, args.message, args.log_file)
    
    # 根据发送结果设置退出码
    sys.exit(0 if result else 1)


if __name__ == '__main__':
    main()
