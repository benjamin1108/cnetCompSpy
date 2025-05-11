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
import argparse
import sys

# --- Core DingTalk Logic (independent of web_server) ---

class DingTalkRobot:
    """
    单个钉钉机器人
    """
    def __init__(self, name: str, webhook_url: str, secret: str = "", keyword: str = ""):
        self.name = name
        self.webhook_url = webhook_url
        self.secret = secret
        self.keyword = keyword
        self.logger = logging.getLogger(f"DingTalkRobot.{name}")
    
    def _sign(self) -> Dict[str, str]:
        if not self.secret:
            return {}
        timestamp = str(round(time.time() * 1000))
        string_to_sign = timestamp + "\n" + self.secret
        hmac_code = hmac.new(
            self.secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        sign = quote_plus(sign)
        return {"timestamp": timestamp, "sign": sign}
    
    def send_markdown(self, title: str, text: str) -> bool:
        if not self.webhook_url:
            self.logger.warning(f"机器人 {self.name} 未配置webhook")
            return False
        params = self._sign()
        webhook_url_signed = self.webhook_url
        if params:
            connector = "&" if "?" in webhook_url_signed else "?"
            webhook_url_signed = f"{webhook_url_signed}{connector}timestamp={params['timestamp']}&sign={params['sign']}"
        data = {"msgtype": "markdown", "markdown": {"title": title, "text": text}}
        try:
            response = requests.post(
                webhook_url_signed,
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
    """钉钉机器人通知工具"""
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger("DingTalkNotifier")
        self.robots: List[DingTalkRobot] = [] # Type hint for clarity
        self.config: Dict[str, Any] = {} # Type hint
        self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str] = None) -> None:
        self.config = {"enabled": False, "keyword": "云计算竞争本周动态", "robots": []}
        try:
            # Assuming config_loader is in src.utils, this import is fine if script is run as a module
            from src.utils.config_loader import get_config 
            loaded_config = get_config(config_path=config_path)
            if loaded_config and "dingtalk" in loaded_config:
                dingtalk_config = loaded_config["dingtalk"]
                for key in ["enabled", "keyword"]:
                    if key in dingtalk_config:
                        self.config[key] = dingtalk_config[key]
                if "robots" in dingtalk_config:
                    self.config["robots"] = dingtalk_config["robots"]
                elif "webhook_url" in dingtalk_config: # Backward compatibility
                    self.logger.warning("检测到旧版配置格式，建议更新为新的robots列表格式")
                    self.config["robots"] = [{
                        "name": "默认机器人",
                        "webhook_url": dingtalk_config.get("webhook_url", ""),
                        "secret": dingtalk_config.get("secret", "")
                    }]
        except ImportError:
            self.logger.error("无法导入 src.utils.config_loader。请确保PYTHONPATH设置正确或从项目根目录以模块方式运行。")
            self.config["enabled"] = False # Disable if config can't be loaded
        except Exception as e:
            self.logger.error(f"加载钉钉配置失败: {e}")
            self.config["enabled"] = False # Disable on other errors too
        self._init_robots()
        if not self.config.get("enabled"):
            self.logger.warning("钉钉机器人通知功能未启用 (配置加载后)")
        elif not self.robots:
            self.logger.error("未配置有效的钉钉机器人 (配置加载后)")
            self.config["enabled"] = False
            
    def _init_robots(self) -> None:
        self.robots = []
        for robot_config in self.config.get("robots", []):
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
        title = update.get('translated_title') or update.get('original_title')
        date = update.get('date', '').replace('_', '-')
        doc_type = update.get('doc_type', '').upper()
        vendor = update.get('vendor', '')
        filename = update.get('filename', '')
        # Ensure these fields exist, provide defaults if necessary or handle missing data
        url = f"http://cnetspy.site/analysis/document/{vendor or 'unknown'}/{doc_type.lower() or 'unknown'}/{filename or 'unknown'}"
        md_content = f"{index}. **[{title or '[无标题]'}]({url})**\n\n"
        md_content += f"   • 类型: {doc_type or 'N/A'}  \n"
        md_content += f"   • 日期: {date or 'N/A'}\n\n"
        return md_content

    def send_weekly_updates(self, weekly_updates_data: Dict[str, List[Dict[str, Any]]], robot_names: Optional[List[str]] = None) -> bool:
        if not self.config.get("enabled") or not self.robots:
            self.logger.warning("钉钉周报推送条件不满足（未启用/无机器人）")
            return False # Cannot send if not enabled or no robots
        if not weekly_updates_data or sum(len(v) for v in weekly_updates_data.values()) == 0:
            self.logger.info("本周无更新数据 (传递给 DingTalkNotifier.send_weekly_updates)，不发送通知")
            return True # Consistent with original logic: if no data, it's a "successful" non-send

        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_week = datetime(start_of_week.year, start_of_week.month, start_of_week.day)
        end_of_week = start_of_week + timedelta(days=6)
        title = f"{self.config.get('keyword', '本周动态')} ({start_of_week.strftime('%Y.%m.%d')}-{end_of_week.strftime('%Y.%m.%d')})"
        total_count = sum(len(updates) for updates in weekly_updates_data.values())
        md_content = f"# {title}\n\n📊 本周共有 **{total_count}** 条云计算网络竞争情报\n\n"
        for vendor, updates in weekly_updates_data.items():
            vendor_icon = {"aws": "🟠", "azure": "🔵", "gcp": "🔴"}.get(vendor.lower(), "☁️")
            md_content += f"## {vendor_icon} {vendor.upper()} ({len(updates)}条)\n\n"
            sorted_updates = sorted(updates, key=lambda x: x.get('date', ''), reverse=True)
            for i, update_item in enumerate(sorted_updates):
                md_content += self._format_update_item(i+1, update_item)
        site_url = "http://cnetspy.site/weekly-updates"
        site_home = "http://cnetspy.site"
        md_content += f"\n> [🔍 查看本周所有更新]({site_url})\n\n---\n*本消息由[云网络竞争分析平台]({site_home})自动发送*"
        return self._send_to_robots(title, md_content, robot_names)

    def send_daily_updates(self, daily_updates_data: Dict[str, List[Dict[str, Any]]], robot_names: Optional[List[str]] = None) -> bool:
        if not self.config.get("enabled") or not self.robots:
            self.logger.warning("钉钉日报推送条件不满足（未启用/无机器人）")
            return False
        if not daily_updates_data or sum(len(v) for v in daily_updates_data.values()) == 0:
            self.logger.info("今日无更新数据 (传递给 DingTalkNotifier.send_daily_updates)，不发送通知")
            return True
        today = datetime.now()
        title = f"云计算竞争今日动态 ({today.strftime('%Y.%m.%d')})"
        total_count = sum(len(updates) for updates in daily_updates_data.values())
        md_content = f"# {title}\n\n📊 今日共有 **{total_count}** 条云计算网络竞争情报\n\n"
        for vendor, updates in daily_updates_data.items():
            vendor_icon = {"aws": "🟠", "azure": "🔵", "gcp": "🔴"}.get(vendor.lower(), "☁️")
            md_content += f"## {vendor_icon} {vendor.upper()} ({len(updates)}条)\n\n"
            sorted_updates = sorted(updates, key=lambda x: x.get('date', ''), reverse=True)
            for i, update_item in enumerate(sorted_updates):
                md_content += self._format_update_item(i+1, update_item)
        site_url = "http://cnetspy.site/daily-updates"
        site_home = "http://cnetspy.site"
        md_content += f"\n\n---\n> [🔍 查看今日所有更新]({site_url})\n\n---\n*本消息由[云网络竞争分析平台]({site_home})自动发送*"
        return self._send_to_robots(title, md_content, robot_names)

    def send_recently_updates(self, recently_updates_data: Dict[str, List[Dict[str, Any]]], days: int, robot_names: Optional[List[str]] = None) -> bool:
        if not self.config.get("enabled") or not self.robots:
            self.logger.warning(f"钉钉近{days}日推送条件不满足（未启用/无机器人）")
            return False
        if not recently_updates_data or sum(len(v) for v in recently_updates_data.values()) == 0:
            self.logger.info(f"最近{days}天无更新数据 (传递给 DingTalkNotifier.send_recently_updates)，不发送通知")
            return True
        today = datetime.now()
        today_date = datetime(today.year, today.month, today.day)
        start_date = today_date - timedelta(days=days-1)
        title = f"云计算竞争近{days}天动态 ({start_date.strftime('%Y.%m.%d')}-{today_date.strftime('%Y.%m.%d')})"
        total_count = sum(len(updates) for updates in recently_updates_data.values())
        md_content = f"# {title}\n\n📊 近{days}天共有 **{total_count}** 条云计算网络竞争情报\n\n"
        for vendor, updates in recently_updates_data.items():
            vendor_icon = {"aws": "🟠", "azure": "🔵", "gcp": "🔴"}.get(vendor.lower(), "☁️")
            md_content += f"## {vendor_icon} {vendor.upper()} ({len(updates)}条)\n\n"
            sorted_updates = sorted(updates, key=lambda x: x.get('date', ''), reverse=True)
            for i, update_item in enumerate(sorted_updates):
                md_content += self._format_update_item(i+1, update_item)
        site_url = f"http://cnetspy.site/recent-updates?days={days}"
        site_home = "http://cnetspy.site"
        md_content += f"\n\n---\n> [🔍 查看最近{days}天所有更新]({site_url})\n\n---\n*本消息由[云网络竞争分析平台]({site_home})自动发送*"
        return self._send_to_robots(title, md_content, robot_names)

    def _send_to_robots(self, title: str, md_content: str, robot_names: Optional[List[str]] = None) -> bool:
        success = False
        robots_to_use = self.robots
        if robot_names:
            robots_to_use = [robot for robot in self.robots if robot.name in robot_names]
            if not robots_to_use:
                self.logger.warning(f"指定的机器人 {robot_names} 不存在，尝试使用所有已配置的机器人")
                robots_to_use = self.robots # Fallback to all configured robots
        
        if not robots_to_use:
            self.logger.error("最终没有可用的机器人来发送消息 (检查机器人配置和传入的robot_names)。")
            return False

        for robot in robots_to_use:
            if robot.send_markdown(title, md_content):
                success = True
                self.logger.info(f"通过机器人 {robot.name} 发送钉钉通知成功")
            else:
                self.logger.error(f"通过机器人 {robot.name} 发送钉钉通知失败")
        return success

# --- CLI Handling (depends on web_server for data fetching) ---

def parse_arguments_for_cli():
    parser = argparse.ArgumentParser(description="钉钉机器人推送工具")
    parser.add_argument("--config", type=str, help="自定义配置文件路径")
    parser.add_argument("--debug", action="store_true", help="启用调试日志")
    parser.add_argument("--robot", action="append", dest="robots", help="指定机器人名称(可多次使用)")
    subparsers = parser.add_subparsers(dest="command", help="推送命令", required=True)
    subparsers.add_parser("weekly", help="推送本周更新")
    subparsers.add_parser("daily", help="推送今日更新")
    recent_parser = subparsers.add_parser("recent", help="推送最近n天更新")
    recent_parser.add_argument("days", type=int, help="天数")
    return parser.parse_args()

def cli_main():
    args = parse_arguments_for_cli()
    
    log_level = logging.DEBUG if args.debug else logging.INFO
    # Ensure basicConfig is only called if no handlers are already configured
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)]
        )
    else: # If already configured, just set the level for the root logger
        logging.getLogger().setLevel(log_level)

    logger = logging.getLogger("DingTalkCLI")
        
    if args.robots:
        logger.info(f"指定使用机器人: {', '.join(args.robots)}")

    notifier = DingTalkNotifier(args.config) # Initialize notifier once with config
    if not notifier.config.get("enabled"): # Check if notifier is enabled after loading config
        logger.warning("DingTalkNotifier 未启用，无法推送。请检查配置。")
        # Depending on desired behavior, could exit here or let specific send methods handle it.
        # For now, let it proceed, send_x_updates methods also check for enabled status.

    fetched_data: Optional[Dict[str, List[Dict[str, Any]]]] = None
    success = False
    
    try:
        # Dynamically import web_server components only when script is run
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.dirname(current_file_dir) # Assumes this file is in src/utils/
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir) # Insert at the beginning for priority
        
        # It's generally better if PYTHONPATH is set correctly or the module is run with `python -m`
        # so that these imports work without sys.path manipulation.
        from web_server.vendor_manager import VendorManager
        from web_server.document_manager import DocumentManager

        project_root = os.path.dirname(src_dir)
        raw_dir = os.path.join(project_root, "data", "raw")
        analyzed_dir = os.path.join(project_root, "data", "analysis")
        
        document_manager = DocumentManager(raw_dir, analyzed_dir)
        vendor_manager = VendorManager(raw_dir, analyzed_dir, document_manager)

        if args.command == "weekly":
            logger.info("获取本周更新数据...")
            fetched_data = vendor_manager.get_weekly_updates()
            logger.info(f"准备推送周报数据 ({sum(len(v) for v in fetched_data.values()) if fetched_data else 0} 条)")
            success = notifier.send_weekly_updates(fetched_data, args.robots)
        elif args.command == "daily":
            logger.info("获取每日更新数据...")
            fetched_data = vendor_manager.get_daily_updates()
            logger.info(f"准备推送日报数据 ({sum(len(v) for v in fetched_data.values()) if fetched_data else 0} 条)")
            success = notifier.send_daily_updates(fetched_data, args.robots)
        elif args.command == "recent":
            logger.info(f"获取最近{args.days}天更新数据...")
            fetched_data = vendor_manager.get_recently_updates(args.days)
            logger.info(f"准备推送近{args.days}日数据 ({sum(len(v) for v in fetched_data.values()) if fetched_data else 0} 条)")
            success = notifier.send_recently_updates(fetched_data, args.days, args.robots)
        
    except ImportError as ie:
        logger.error(f"导入 web_server 组件失败: {ie}。请确保从项目根目录使用 'python -m src.utils.dingtalk' 运行，或 PYTHONPATH 配置正确。", exc_info=True)
        return 1 # Indicate failure
    except Exception as e:
        logger.error(f"执行钉钉推送 cli_main 时发生错误: {e}", exc_info=True)
        return 1 # Indicate failure

    if success:
        logger.info("钉钉推送操作成功完成")
        return 0
    else:
        logger.error("钉钉推送操作未成功 (可能部分成功，或未发送任何消息)")
        return 1

if __name__ == "__main__":
    # Initial basic logging setup for the script itself before CLI args are parsed
    # This ensures logs from DingTalkNotifier/Robot classes are captured if they init before cli_main's logging setup
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO, 
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)]
        )
    sys.exit(cli_main()) 