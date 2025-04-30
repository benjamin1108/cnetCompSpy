#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import sys
import os
from src.utils.dingtalk_notifier import send_weekly_updates_to_dingtalk

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="钉钉机器人推送weekly-updates工具")
    
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
    
    # 发送通知
    logger.info("开始推送weekly-updates到钉钉...")
    
    if args.robots:
        logger.info(f"指定使用机器人: {', '.join(args.robots)}")
    
    success = send_weekly_updates_to_dingtalk(args.config, args.robots)
    
    if success:
        logger.info("钉钉推送成功")
        return 0
    else:
        logger.error("钉钉推送失败")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 