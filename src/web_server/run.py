#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
竞争分析Web服务器启动脚本

此脚本用于独立启动竞争分析Web服务器，提供一个界面用于浏览和查看分析结果。
可以独立于主程序运行，方便部署和使用。
"""

import os
import sys
import argparse
import logging
from pathlib import Path


def parse_args():
    """
    解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description='启动竞争分析Web服务器',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='服务器主机地址'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='服务器端口'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        default=None,
        help='数据目录路径，默认为项目根目录下的data目录'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='日志级别'
    )
    
    return parser.parse_args()


def setup_logging(log_level):
    """
    设置日志配置

    Args:
        log_level (str): 日志级别
    """
    # 配置根日志
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    logger = logging.getLogger('web_server.run')
    
    # 获取项目根目录
    try:
        # 获取脚本所在目录
        script_dir = Path(__file__).resolve().parent
        # 项目根目录应该是脚本所在目录的上两级
        project_root = script_dir.parent.parent
        
        # 设置数据目录
        if args.data_dir is None:
            data_dir = os.path.join(project_root, 'data')
        else:
            data_dir = args.data_dir
        
        # 确保目录存在
        if not os.path.isdir(data_dir):
            logger.warning(f"数据目录不存在: {data_dir}")
            os.makedirs(data_dir, exist_ok=True)
            logger.info(f"已创建数据目录: {data_dir}")
    
    except Exception as e:
        logger.error(f"获取项目根目录时出错: {e}", exc_info=True)
        sys.exit(1)
    
    # 导入WebServer类
    try:
        from src.web_server.server import WebServer
    except ImportError:
        logger.error("导入WebServer类失败，请确保安装了所有依赖", exc_info=True)
        sys.exit(1)
    
    # 创建并启动Web服务器
    logger.info(f"启动Web服务器: host={args.host}, port={args.port}, debug={args.debug}")
    logger.info(f"数据目录: {data_dir}")
    
    try:
        server = WebServer(
            data_dir=data_dir,
            host=args.host,
            port=args.port,
            debug=args.debug
        )
        
        server.run()
    
    except KeyboardInterrupt:
        logger.info("收到退出信号，服务器正在关闭...")
    
    except Exception as e:
        logger.error(f"服务器运行时出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 