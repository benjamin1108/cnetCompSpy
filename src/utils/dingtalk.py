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
        self.reporting_config: Dict[str, Any] = {} # 添加reporting配置
        self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str] = None) -> None:
        self.config = {"enabled": False, "keyword": "云计算竞争本周动态", "robots": []}
        self.reporting_config = {}
        try:
            # Assuming config_loader is in src.utils, this import is fine if script is run as a module
            from src.utils.config_loader import get_config 
            loaded_config = get_config(config_path=config_path)
            
            # 加载钉钉配置
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
                    
            # 加载reporting配置
            if loaded_config and "reporting" in loaded_config:
                self.reporting_config = loaded_config["reporting"]
                self.logger.info("已加载reporting配置用于URL构建")
            else:
                self.logger.warning("未找到reporting配置，将使用默认URL配置")
                # 设置默认配置
                self.reporting_config = {
                    "site_base_url": "http://cnetspy.site",
                    "url_paths": {
                        "document_analysis": "/analysis/document/{vendor}/{doc_type}/{filename}",
                        "weekly_updates": "/weekly-updates",
                        "daily_updates": "/daily-updates",
                        "recent_updates": "/recent-updates?days={days}",
                        "home": "/"
                    },
                    "beautification": {
                        "platform_url": "http://cnetspy.site"
                    }
                }
                
        except ImportError:
            self.logger.error("无法导入 src.utils.config_loader。请确保PYTHONPATH设置正确或从项目根目录以模块方式运行。")
            self.config["enabled"] = False # Disable if config can't be loaded
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            self.config["enabled"] = False # Disable on other errors too
        self._init_robots()
        if not self.config.get("enabled"):
            self.logger.warning("钉钉机器人通知功能未启用 (配置加载后)")
        elif not self.robots:
            self.logger.error("未配置有效的钉钉机器人 (配置加载后)")
            self.config["enabled"] = False
    
    def _build_url(self, path_key: str, **kwargs) -> str:
        """根据配置构建URL"""
        base_url = self.reporting_config.get("site_base_url", "http://cnetspy.site")
        url_paths = self.reporting_config.get("url_paths", {})
        
        if path_key not in url_paths:
            self.logger.warning(f"URL路径配置中未找到 {path_key}，使用默认值")
            # 提供默认路径
            default_paths = {
                "document_analysis": "/analysis/document/{vendor}/{doc_type}/{filename}",
                "weekly_updates": "/weekly-updates",
                "daily_updates": "/daily-updates",
                "recent_updates": "/recent-updates?days={days}",
                "home": "/"
            }
            path_template = default_paths.get(path_key, "/")
        else:
            path_template = url_paths[path_key]
        
        # 格式化路径模板
        try:
            formatted_path = path_template.format(**kwargs)
        except KeyError as e:
            self.logger.error(f"格式化URL路径时缺少参数: {e}")
            formatted_path = path_template
        
        return f"{base_url.rstrip('/')}{formatted_path}"
    
    def _get_platform_url(self) -> str:
        """获取平台首页URL"""
        return self.reporting_config.get("beautification", {}).get("platform_url") or \
               self.reporting_config.get("site_base_url", "http://cnetspy.site")
            
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
        
        # 使用配置构建URL而不是硬编码
        url = self._build_url(
            "document_analysis",
            vendor=vendor or 'unknown',
            doc_type=doc_type.lower() or 'unknown',
            filename=filename or 'unknown'
        )
        
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
        site_url = self._build_url("weekly_updates")
        site_home = self._get_platform_url()
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
        site_url = self._build_url("daily_updates")
        site_home = self._get_platform_url()
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
        site_url = self._build_url("recent_updates", days=days)
        site_home = self._get_platform_url()
        md_content += f"\n\n---\n> [🔍 查看最近{days}天所有更新]({site_url})\n\n---\n*本消息由[云网络竞争分析平台]({site_home})自动发送*"
        return self._send_to_robots(title, md_content, robot_names)

    def send_markdown_file(self, filepath: str, robot_names: Optional[List[str]] = None) -> bool:
        """读取指定的Markdown文件并将其内容推送到钉钉。"""
        if not self.config.get("enabled") or not self.robots:
            self.logger.warning(f"钉钉文件推送条件不满足（未启用/无机器人）: {filepath}")
            return False
        
        try:
            if not os.path.exists(filepath) or not os.path.isfile(filepath):
                self.logger.error(f"要推送的Markdown文件未找到或不是一个文件: {filepath}")
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            if not file_content.strip():
                self.logger.warning(f"Markdown文件内容为空: {filepath}")
                # 考虑是否要发送一个空消息的通知，或者直接返回True/False
                # 为保持一致性，如果内容为空，不发送但认为操作"成功"完成（没有发生错误）
                return True 

            # 尝试从文件名提取标题 (移除日期和扩展名)
            report_filename = os.path.basename(filepath)
            title = report_filename.replace("weekly_competitor_summary_", "").replace(".md", "").replace("_to_", " 到 ")
            # 如果文件名解析不出合适的标题，可以尝试从文件第一行H1提取，或使用固定标题
            if not title or report_filename == title: # 简单检查是否解析成功
                 # 尝试从文件第一行读取标题
                first_line = file_content.splitlines()[0] if file_content.splitlines() else ""
                if first_line.startswith("# "):
                    title = first_line[2:].strip()
                else:
                    title = f"Markdown文件推送: {report_filename}" # 后备标题

            # 可以在这里对 file_content 进行一些预处理，如果钉钉对总长度或格式有特殊要求
            # 例如，确保关键字在文本中 (如果机器人有关键字限制且文件内容本身可能不包含)
            # 目前直接发送原始内容
            
            # 确保消息包含关键字 (如果机器人有此设置)
            # 这是一个简化的处理，实际可能需要更复杂的逻辑来决定如何以及是否添加关键字
            keyword_to_check = self.config.get("keyword", "")
            if keyword_to_check and keyword_to_check not in file_content:
                # 对于Markdown文件推送，如果文件本身不包含关键字，可以考虑不强制添加，
                # 或者只为某些类型的机器人添加。这里简单地不添加。
                self.logger.debug(f"文件内容可能不包含配置的关键字 '{keyword_to_check}'。按原样发送。")

            return self._send_to_robots(title, file_content, robot_names)
            
        except Exception as e:
            self.logger.error(f"推送Markdown文件 {filepath} 时发生错误: {e}", exc_info=True)
            return False

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
    
    # 1. 创建通用参数的父解析器
    common_options_parser = argparse.ArgumentParser(add_help=False)
    common_options_parser.add_argument(
        "--config", 
        type=str, 
        default=None, # 明确设置默认值
        help="自定义配置文件路径 (例如: config/notification.yaml)"
    )
    common_options_parser.add_argument(
        "--debug", 
        action="store_true", 
        help="启用调试日志"
    )
    common_options_parser.add_argument(
        "--robot", 
        action="append", 
        dest="robots", # 保持原来的 dest
        default=None, # 明确设置默认值
        help="指定机器人名称(可多次使用，例如 --robot name1 --robot name2)"
    )

    subparsers = parser.add_subparsers(dest="command", help="推送命令", title="可用命令", required=True) # 添加 title
    
    # 2. 让所有子解析器继承通用参数
    weekly_parser = subparsers.add_parser(
        "weekly", 
        help="推送本周更新", 
        parents=[common_options_parser]
    )
    
    daily_parser = subparsers.add_parser(
        "daily", 
        help="推送今日更新", 
        parents=[common_options_parser]
    )
    
    recent_parser = subparsers.add_parser(
        "recent", 
        help="推送最近n天更新", 
        parents=[common_options_parser]
    )
    recent_parser.add_argument("days", type=int, help="天数")
    
    pushfile_parser = subparsers.add_parser(
        "pushfile", 
        help="推送指定的Markdown文件内容", 
        parents=[common_options_parser]
    )
    pushfile_parser.add_argument(
        "--filepath", 
        type=str, 
        required=True, 
        help="要推送的Markdown文件的路径"
    )
    
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
        elif args.command == "pushfile":
            logger.info(f"推送指定的Markdown文件内容...")
            success = notifier.send_markdown_file(args.filepath)
        
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