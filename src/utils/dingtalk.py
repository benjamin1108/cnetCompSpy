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

    def send_report_file(self, filepath: str, robot_names: Optional[List[str]] = None) -> bool:
        """
        发送 markdown 报告文件到钉钉机器人
        
        参数:
            filepath: Markdown 文件路径
            robot_names: 可选的机器人名称列表
            
        返回:
            如果成功发送到至少一个机器人则返回 True
        """
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
    
    # 创建通用参数的父解析器
    common_options_parser = argparse.ArgumentParser(add_help=False)
    common_options_parser.add_argument(
        "--config", 
        type=str, 
        default=None,
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
        dest="robots",
        default=None,
        help="指定机器人名称(可多次使用，例如 --robot name1 --robot name2)"
    )

    subparsers = parser.add_subparsers(dest="command", help="推送命令", title="可用命令", required=True)
    
    # 仅保留 pushfile 子命令
    pushfile_parser = subparsers.add_parser(
        "pushfile", 
        help="推送指定的Markdown报告文件", 
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

    notifier = DingTalkNotifier(args.config)
    if not notifier.config.get("enabled"):
        logger.warning("DingTalkNotifier 未启用，无法推送。请检查配置。")
        return 1

    success = False
    
    try:
        if args.command == "pushfile":
            logger.info(f"推送指定的Markdown报告文件...")
            success = notifier.send_report_file(args.filepath, args.robots)
        else:
            logger.error(f"未知命令: {args.command}")
            return 1
        
    except Exception as e:
        logger.error(f"执行钉钉推送时发生错误: {e}", exc_info=True)
        return 1

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