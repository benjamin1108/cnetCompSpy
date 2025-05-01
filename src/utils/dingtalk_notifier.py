#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import hmac
import base64
import hashlib
import requests
from typing import Dict, List, Any, Optional, Union
from urllib.parse import quote_plus
import yaml
import os
import logging
from datetime import datetime, timedelta

class DingTalkRobot:
    """
    单个钉钉机器人
    """
    def __init__(self, name: str, webhook_url: str, secret: str = "", keyword: str = ""):
        """
        初始化钉钉机器人
        
        Args:
            name: 机器人名称
            webhook_url: 机器人webhook地址
            secret: 机器人安全设置的加签密钥
            keyword: 机器人安全设置的自定义关键词
        """
        self.name = name
        self.webhook_url = webhook_url
        self.secret = secret
        self.keyword = keyword
        self.logger = logging.getLogger(f"DingTalkRobot.{name}")
    
    def _sign(self) -> Dict[str, str]:
        """
        计算钉钉机器人消息签名
        
        根据钉钉官方文档：
        https://open.dingtalk.com/document/robots/customize-robot-security-settings
        
        Returns:
            包含timestamp和sign的字典
        """
        if not self.secret:
            return {}
        
        # 第一步：获取当前时间戳，单位是毫秒
        timestamp = str(round(time.time() * 1000))
        
        # 第二步：拼接签名字符串 string_to_sign = timestamp + "\n" + secret
        string_to_sign = timestamp + "\n" + self.secret
        
        # 第三步：计算签名
        # 需要使用HmacSHA256算法，使用secret作为密钥，string_to_sign作为待签名字符串
        hmac_code = hmac.new(
            self.secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        # 第四步：进行Base64编码
        sign = base64.b64encode(hmac_code).decode('utf-8')
        
        # 第五步：对签名进行URL安全的Base64编码
        sign = quote_plus(sign)
        
        return {
            "timestamp": timestamp,
            "sign": sign
        }
    
    def send_markdown(self, title: str, text: str) -> bool:
        """
        发送markdown消息
        
        Args:
            title: 消息标题
            text: markdown格式的消息内容
        
        Returns:
            发送成功返回True，否则返回False
        """
        if not self.webhook_url:
            self.logger.warning(f"机器人 {self.name} 未配置webhook")
            return False
        
        # 构造请求参数
        params = self._sign()
        webhook_url = self.webhook_url
        if params:
            # 检查URL中是否已经有参数，决定使用&还是?
            connector = "&" if "?" in webhook_url else "?"
            webhook_url = f"{webhook_url}{connector}timestamp={params['timestamp']}&sign={params['sign']}"
        
        # 构造请求体
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            }
        }
        
        # 发送请求
        try:
            response = requests.post(
                webhook_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(data)
            )
            result = response.json()
            
            if result.get("errcode") == 0:
                self.logger.info(f"机器人 {self.name} 消息发送成功")
                return True
            else:
                self.logger.error(f"机器人 {self.name} 消息发送失败: {result}")
                return False
        except Exception as e:
            self.logger.error(f"机器人 {self.name} 消息发送异常: {e}")
            return False


class DingTalkNotifier:
    """钉钉机器人通知工具，用于推送weekly-updates数据到钉钉群"""
    
    def __init__(self, config_path: str = None):
        """
        初始化钉钉机器人通知工具
        
        Args:
            config_path: 配置文件路径，默认为None，使用默认配置文件
        """
        self.logger = logging.getLogger("DingTalkNotifier")
        self.robots = []  # 存储多个机器人
        
        # 加载配置
        self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str] = None) -> None:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
        """
        # 默认配置
        self.config = {
            "enabled": False,
            "keyword": "云计算竞争本周动态",
            "robots": []
        }
        
        # 基础配置文件路径
        base_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.yaml")
        
        # 敏感配置文件路径
        secret_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.secret.yaml")
        
        # 加载基础配置
        if os.path.exists(base_config_path):
            try:
                with open(base_config_path, 'r', encoding='utf-8') as f:
                    base_config = yaml.safe_load(f)
                    if base_config and "dingtalk" in base_config:
                        # 更新非敏感配置
                        for key in ["enabled", "keyword"]:
                            if key in base_config["dingtalk"]:
                                self.config[key] = base_config["dingtalk"][key]
            except Exception as e:
                self.logger.error(f"加载基础配置文件失败: {e}")
        
        # 加载敏感配置
        if os.path.exists(secret_config_path):
            try:
                with open(secret_config_path, 'r', encoding='utf-8') as f:
                    secret_config = yaml.safe_load(f)
                    if secret_config and "dingtalk" in secret_config:
                        # 检查是否有机器人配置
                        if "robots" in secret_config["dingtalk"]:
                            self.config["robots"] = secret_config["dingtalk"]["robots"]
                        # 处理旧版配置格式向后兼容
                        elif "webhook_url" in secret_config["dingtalk"]:
                            self.logger.warning("检测到旧版配置格式，建议更新为新的robots列表格式")
                            self.config["robots"] = [{
                                "name": "默认机器人",
                                "webhook_url": secret_config["dingtalk"].get("webhook_url", ""),
                                "secret": secret_config["dingtalk"].get("secret", "")
                            }]
            except Exception as e:
                self.logger.error(f"加载敏感配置文件失败: {e}")
        
        # 如果指定了配置文件，使用指定的配置文件覆盖默认配置
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    custom_config = yaml.safe_load(f)
                    if custom_config and "dingtalk" in custom_config:
                        # 更新全部配置
                        for key in custom_config["dingtalk"]:
                            self.config[key] = custom_config["dingtalk"][key]
            except Exception as e:
                self.logger.error(f"加载自定义配置文件失败: {e}")
        
        # 初始化机器人
        self._init_robots()
        
        # 检查必要配置
        if not self.config["enabled"]:
            self.logger.warning("钉钉机器人通知功能未启用")
        elif not self.robots:
            self.logger.error("未配置有效的钉钉机器人")
            self.config["enabled"] = False
    
    def _init_robots(self) -> None:
        """初始化所有机器人"""
        self.robots = []
        for robot_config in self.config["robots"]:
            if not robot_config.get("webhook_url"):
                self.logger.warning(f"机器人 {robot_config.get('name', '未命名')} 未配置webhook_url，跳过")
                continue
            
            robot = DingTalkRobot(
                name=robot_config.get("name", "未命名机器人"),
                webhook_url=robot_config.get("webhook_url", ""),
                secret=robot_config.get("secret", ""),
                keyword=self.config.get("keyword", "")
            )
            self.robots.append(robot)
        
        self.logger.info(f"初始化了 {len(self.robots)} 个机器人")
    
    def _format_update_item(self, index: int, update: Dict[str, Any]) -> str:
        """
        格式化单个更新项的Markdown内容
        
        Args:
            index: 更新项的序号
            update: 更新项数据
            
        Returns:
            格式化后的Markdown内容
        """
        # 提取标题
        title = update.get('translated_title') or update.get('original_title')
        date = update.get('date', '').replace('_', '-')
        doc_type = update.get('doc_type', '').upper()
        
        # 构建文档URL
        vendor = update.get('vendor', '')
        filename = update.get('filename', '')
        url = f"http://cnetspy.site/analysis/document/{vendor}/{doc_type.lower()}/{filename}"
        
        # 格式化Markdown内容
        md_content = f"{index}. **[{title}]({url})**\n\n"
        md_content += f"   • 类型: {doc_type}  \n"
        md_content += f"   • 日期: {date}\n\n"
        
        return md_content
    
    def send_weekly_updates(self, weekly_updates: Dict[str, List[Dict[str, Any]]], robot_names: Optional[List[str]] = None) -> bool:
        """
        发送本周更新到钉钉群
        
        Args:
            weekly_updates: 本周更新数据，格式与vendor_manager.get_weekly_updates()相同
            robot_names: 指定要发送的机器人名称列表，如果为None则发送给所有机器人
            
        Returns:
            至少有一个机器人发送成功返回True，否则返回False
        """
        if not self.config["enabled"]:
            self.logger.warning("钉钉机器人通知功能未启用")
            return False
        
        if not self.robots:
            self.logger.warning("未配置有效的钉钉机器人")
            return False
        
        if not weekly_updates:
            self.logger.warning("本周无更新数据，不发送通知")
            return False
        
        # 计算本周的日期范围
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_week = datetime(start_of_week.year, start_of_week.month, start_of_week.day)
        end_of_week = start_of_week + timedelta(days=6)
        
        # 构造消息
        title = f"{self.config['keyword']} ({start_of_week.strftime('%Y.%m.%d')}-{end_of_week.strftime('%Y.%m.%d')})"
        
        # 构造markdown内容
        md_content = f"# {title}\n\n"
        
        # 统计总数
        total_count = sum(len(updates) for updates in weekly_updates.values())
        md_content += f"📊 本周共有 **{total_count}** 条云计算网络竞争情报\n\n"
        
        # 按厂商分组展示
        for vendor, updates in weekly_updates.items():
            # 厂商图标
            vendor_icon = "☁️"
            if vendor.lower() == "aws":
                vendor_icon = "🟠"
            elif vendor.lower() == "azure":
                vendor_icon = "🔵"
            elif vendor.lower() == "gcp":
                vendor_icon = "🔴"
            
            md_content += f"## {vendor_icon} {vendor.upper()} ({len(updates)}条)\n\n"
            
            # 按日期排序，最新的在前面
            sorted_updates = sorted(updates, key=lambda x: x.get('date', ''), reverse=True)
            
            # 展示更新
            for i, update in enumerate(sorted_updates):
                md_content += self._format_update_item(i+1, update)
        
        # 添加页面链接
        site_url = "http://cnetspy.site/weekly-updates"
        site_home = "http://cnetspy.site"
        md_content += f"\n> [🔍 查看本周所有更新]({site_url})"
        md_content += f"\n\n---\n*本消息由[云网络竞争分析平台]({site_home})自动发送*"
        
        # 发送到指定机器人或所有机器人
        success = False
        robots_to_use = []
        
        if robot_names:
            # 使用指定的机器人
            robots_to_use = [robot for robot in self.robots if robot.name in robot_names]
            if not robots_to_use:
                self.logger.warning(f"指定的机器人 {robot_names} 不存在，尝试使用所有机器人")
                robots_to_use = self.robots
        else:
            # 使用所有机器人
            robots_to_use = self.robots
        
        for robot in robots_to_use:
            if robot.send_markdown(title, md_content):
                success = True
                self.logger.info(f"通过机器人 {robot.name} 发送钉钉通知成功")
            else:
                self.logger.error(f"通过机器人 {robot.name} 发送钉钉通知失败")
        
        return success
    
    def send_daily_updates(self, daily_updates: Dict[str, List[Dict[str, Any]]], robot_names: Optional[List[str]] = None) -> bool:
        """
        发送今日更新到钉钉群
        
        Args:
            daily_updates: 今日更新数据，格式与vendor_manager.get_daily_updates()相同
            robot_names: 指定要发送的机器人名称列表，如果为None则发送给所有机器人
            
        Returns:
            至少有一个机器人发送成功返回True，否则返回False
        """
        if not self.config["enabled"]:
            self.logger.warning("钉钉机器人通知功能未启用")
            return False
        
        if not self.robots:
            self.logger.warning("未配置有效的钉钉机器人")
            return False
        
        if not daily_updates:
            self.logger.warning("今日无更新数据，不发送通知")
            return False
        
        # 获取今天的日期
        today = datetime.now()
        
        # 构造消息
        title = f"云计算竞争今日动态 ({today.strftime('%Y.%m.%d')})"
        
        # 构造markdown内容
        md_content = f"# {title}\n\n"
        
        # 统计总数
        total_count = sum(len(updates) for updates in daily_updates.values())
        md_content += f"📊 今日共有 **{total_count}** 条云计算网络竞争情报\n\n"
        
        # 按厂商分组展示
        for vendor, updates in daily_updates.items():
            # 厂商图标
            vendor_icon = "☁️"
            if vendor.lower() == "aws":
                vendor_icon = "🟠"
            elif vendor.lower() == "azure":
                vendor_icon = "🔵"
            elif vendor.lower() == "gcp":
                vendor_icon = "🔴"
            
            md_content += f"## {vendor_icon} {vendor.upper()} ({len(updates)}条)\n\n"
            
            # 按日期排序，最新的在前面
            sorted_updates = sorted(updates, key=lambda x: x.get('date', ''), reverse=True)
            
            # 展示更新
            for i, update in enumerate(sorted_updates):
                md_content += self._format_update_item(i+1, update)
        
        # 添加页面链接
        site_url = "http://cnetspy.site/daily-updates"
        site_home = "http://cnetspy.site"
        md_content += f"\n\n---\n> [🔍 查看今日所有更新]({site_url})"
        md_content += f"\n\n---\n*本消息由[云网络竞争分析平台]({site_home})自动发送*"
        
        # 发送到指定机器人或所有机器人
        success = False
        robots_to_use = []
        
        if robot_names:
            # 使用指定的机器人
            robots_to_use = [robot for robot in self.robots if robot.name in robot_names]
            if not robots_to_use:
                self.logger.warning(f"指定的机器人 {robot_names} 不存在，尝试使用所有机器人")
                robots_to_use = self.robots
        else:
            # 使用所有机器人
            robots_to_use = self.robots
        
        for robot in robots_to_use:
            if robot.send_markdown(title, md_content):
                success = True
                self.logger.info(f"通过机器人 {robot.name} 发送钉钉通知成功")
            else:
                self.logger.error(f"通过机器人 {robot.name} 发送钉钉通知失败")
        
        return success
    
    def send_recently_updates(self, recently_updates: Dict[str, List[Dict[str, Any]]], days: int, robot_names: Optional[List[str]] = None) -> bool:
        """
        发送最近几天更新到钉钉群
        
        Args:
            recently_updates: 最近更新数据，格式与vendor_manager.get_recently_updates()相同
            days: 天数，最近几天的更新
            robot_names: 指定要发送的机器人名称列表，如果为None则发送给所有机器人
            
        Returns:
            至少有一个机器人发送成功返回True，否则返回False
        """
        if not self.config["enabled"]:
            self.logger.warning("钉钉机器人通知功能未启用")
            return False
        
        if not self.robots:
            self.logger.warning("未配置有效的钉钉机器人")
            return False
        
        if not recently_updates:
            self.logger.warning(f"最近{days}天无更新数据，不发送通知")
            return False
        
        # 计算最近几天的日期范围
        today = datetime.now()
        today_date = datetime(today.year, today.month, today.day)
        start_date = today_date - timedelta(days=days-1)  # days-1是因为包含今天在内的days天
        
        # 构造消息
        title = f"云计算竞争近{days}天动态 ({start_date.strftime('%Y.%m.%d')}-{today_date.strftime('%Y.%m.%d')})"
        
        # 构造markdown内容
        md_content = f"# {title}\n\n"
        
        # 统计总数
        total_count = sum(len(updates) for updates in recently_updates.values())
        md_content += f"📊 近{days}天共有 **{total_count}** 条云计算网络竞争情报\n\n"
        
        # 按厂商分组展示
        for vendor, updates in recently_updates.items():
            # 厂商图标
            vendor_icon = "☁️"
            if vendor.lower() == "aws":
                vendor_icon = "🟠"
            elif vendor.lower() == "azure":
                vendor_icon = "🔵"
            elif vendor.lower() == "gcp":
                vendor_icon = "🔴"
            
            md_content += f"## {vendor_icon} {vendor.upper()} ({len(updates)}条)\n\n"
            
            # 按日期排序，最新的在前面
            sorted_updates = sorted(updates, key=lambda x: x.get('date', ''), reverse=True)
            
            # 展示更新
            for i, update in enumerate(sorted_updates):
                md_content += self._format_update_item(i+1, update)
        
        # 添加网站链接
        site_url = "http://cnetspy.site/"
        md_content += f"\n\n---\n*本消息由[云网络竞争分析平台]({site_url})自动发送*"
        
        # 发送到指定机器人或所有机器人
        success = False
        robots_to_use = []
        
        if robot_names:
            # 使用指定的机器人
            robots_to_use = [robot for robot in self.robots if robot.name in robot_names]
            if not robots_to_use:
                self.logger.warning(f"指定的机器人 {robot_names} 不存在，尝试使用所有机器人")
                robots_to_use = self.robots
        else:
            # 使用所有机器人
            robots_to_use = self.robots
        
        for robot in robots_to_use:
            if robot.send_markdown(title, md_content):
                success = True
                self.logger.info(f"通过机器人 {robot.name} 发送近{days}天更新通知成功")
            else:
                self.logger.error(f"通过机器人 {robot.name} 发送近{days}天更新通知失败")
        
        return success


def send_updates_to_dingtalk(update_type: str = "weekly", days: int = 3, config_path: str = None, robot_names: Optional[List[str]] = None) -> bool:
    """
    发送各类型更新到钉钉群的统一函数
    
    Args:
        update_type: 更新类型，可选值为 "weekly"(本周更新)、"daily"(今日更新)、"recent"(最近几天更新)
        days: 当update_type为"recent"时有效，获取最近几天的更新，默认为3天
        config_path: 配置文件路径，默认为None，使用默认配置文件
        robot_names: 指定要发送的机器人名称列表，如果为None则发送给所有机器人
        
    Returns:
        发送成功返回True，否则返回False
    """
    try:
        # 动态导入，避免循环导入
        import sys
        import os
        
        # 确保src目录在Python路径中
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if src_dir not in sys.path:
            sys.path.append(src_dir)
        
        # 导入vendor_manager模块
        from src.web_server.vendor_manager import VendorManager
        from src.web_server.document_manager import DocumentManager
        
        # 设置默认路径
        raw_dir = os.path.join(os.path.dirname(src_dir), "data", "raw")
        analyzed_dir = os.path.join(os.path.dirname(src_dir), "data", "analysis")
        
        # 创建DocumentManager和VendorManager实例
        document_manager = DocumentManager(raw_dir, analyzed_dir)
        vendor_manager = VendorManager(raw_dir, analyzed_dir, document_manager)
        
        # 根据更新类型获取相应的更新数据
        notifier = DingTalkNotifier(config_path)
        
        if update_type == "weekly":
            # 获取本周更新
            updates = vendor_manager.get_weekly_updates()
            return notifier.send_weekly_updates(updates, robot_names)
        elif update_type == "daily":
            # 获取今日更新
            updates = vendor_manager.get_daily_updates()
            return notifier.send_daily_updates(updates, robot_names)
        elif update_type == "recent":
            # 获取最近几天更新
            updates = vendor_manager.get_recently_updates(days)
            return notifier.send_recently_updates(updates, days, robot_names)
        else:
            logging.error(f"未知的更新类型: {update_type}")
            return False
    except Exception as e:
        logging.error(f"发送钉钉通知出错: {e}")
        return False


# 为了向后兼容，保留原有函数名，但实现调用统一函数
def send_weekly_updates_to_dingtalk(config_path: str = None, robot_names: Optional[List[str]] = None) -> bool:
    """发送本周更新到钉钉群（向后兼容）"""
    return send_updates_to_dingtalk("weekly", config_path=config_path, robot_names=robot_names)

def send_daily_updates_to_dingtalk(config_path: str = None, robot_names: Optional[List[str]] = None) -> bool:
    """发送今日更新到钉钉群（向后兼容）"""
    return send_updates_to_dingtalk("daily", config_path=config_path, robot_names=robot_names)

def send_recently_updates_to_dingtalk(days: int = 3, config_path: str = None, robot_names: Optional[List[str]] = None) -> bool:
    """发送最近几天更新到钉钉群（向后兼容）"""
    return send_updates_to_dingtalk("recent", days=days, config_path=config_path, robot_names=robot_names)

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 发送周报
    success = send_updates_to_dingtalk("weekly")
    
    # 显示结果
    if success:
        print("✅ 钉钉周报推送成功")
    else:
        print("❌ 钉钉周报推送失败")
        import sys
        sys.exit(1) 