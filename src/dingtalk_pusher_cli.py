#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
钉钉推送命令行工具

支持以下子命令：
- weekly: 推送本周更新
- daily: 推送今日更新
- recent: 推送最近n天更新
"""

import argparse
import logging
import sys
from typing import List, Optional
from src.utils.dingtalk_notifier import (
    send_weekly_updates_to_dingtalk,
    send_daily_updates_to_dingtalk,
    send_recently_updates_to_dingtalk
)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="钉钉机器人推送工具")
    
    parser.add_argument(
        "--config", 
        type=str, 
        help="自定义配置文件路径"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="启用调试日志"
    )
    
    parser.add_argument(
        "--robot", 
        action="append",
        dest="robots",
        help="指定要使用的机器人名称，可以多次使用此参数指定多个机器人"
    )
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest="command", help="推送命令")
    
    # weekly 子命令
    weekly_parser = subparsers.add_parser("weekly", help="推送本周更新")
    
    # daily 子命令
    daily_parser = subparsers.add_parser("daily", help="推送今日更新")
    
    # recent 子命令
    recent_parser = subparsers.add_parser("recent", help="推送最近n天更新")
    recent_parser.add_argument(
        "days", 
        type=int, 
        help="天数，获取最近几天的更新"
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 配置日志
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger = logging.getLogger("DingTalkPusher")
    
    # 检查是否指定了子命令
    if not args.command:
        logger.error("必须指定一个子命令: weekly, daily 或 recent")
        return 1
    
    # 根据子命令执行相应的推送
    if args.robots:
        logger.info(f"指定使用机器人: {', '.join(args.robots)}")
    
    if args.command == "weekly":
        logger.info("开始推送weekly-updates到钉钉...")
        success = send_weekly_updates_to_dingtalk(args.config, args.robots)
    elif args.command == "daily":
        logger.info("开始推送daily-updates到钉钉...")
        success = send_daily_updates_to_dingtalk(args.config, args.robots)
    elif args.command == "recent":
        logger.info(f"开始推送recent-updates({args.days}天)到钉钉...")
        success = send_recently_updates_to_dingtalk(args.days, args.config, args.robots)
    else:
        logger.error(f"未知的子命令: {args.command}")
        return 1
    
    if success:
        logger.info("钉钉推送成功")
        return 0
    else:
        logger.error("钉钉推送失败")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 