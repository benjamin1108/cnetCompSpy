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
import logging.config # 导入 dictConfig
import yaml # 导入 yaml 以加载配置
from pathlib import Path
from copy import deepcopy # 用于覆盖配置
from typing import Dict, Any, Optional # 用于类型提示

# 默认配置（主要用于结构，实际值来自config.yaml）
DEFAULT_CONFIG = {
    'logging': {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': 'INFO',
                'stream': 'ext://sys.stdout'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }
}

def setup_unified_logging(config: Dict[str, Any], log_level_override: Optional[str] = None, debug_mode: bool = False):
    """使用字典配置统一设置日志系统"""
    log_config = config.get('logging')
    
    if not log_config:
        # 如果配置中没有logging部分，使用默认的基本配置
        print("警告: 配置中未找到 'logging' 配置部分，将使用默认 basicConfig。")
        level_to_set = logging.DEBUG if debug_mode else getattr(logging, log_level_override or 'INFO')
        logging.basicConfig(level=level_to_set, 
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        if debug_mode:
             logging.getLogger().info("Debug mode enabled, setting log level to DEBUG.")
        return

    try:
        # 确保日志目录存在
        log_filename = log_config.get('handlers', {}).get('file', {}).get('filename')
        if log_filename:
            # 确保路径存在
            log_dir = os.path.dirname(log_filename)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
        
        # 处理命令行或debug模式的日志级别覆盖
        if debug_mode:
            if 'console' in log_config.get('handlers', {}):
                log_config['handlers']['console']['level'] = 'DEBUG'
            print("调试模式启用，控制台日志级别设置为 DEBUG。") # 在日志系统前打印
        elif log_level_override:
            if 'console' in log_config.get('handlers', {}):
                 log_config['handlers']['console']['level'] = log_level_override.upper()

        logging.config.dictConfig(log_config)
        logging.getLogger(__name__).debug("统一日志系统配置完成。") # 使用配置后的logger

    except Exception as e:
        print(f"错误：配置日志系统失败: {e}")
        # 回退到基本配置
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).error("日志系统配置失败，回退到基本配置。", exc_info=True)
        
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
        default=None, # 默认由配置文件控制，除非debug或明确指定
        help='覆盖配置文件中的控制台日志级别'
    )
    
    return parser.parse_args()

def main():
    """
    主函数
    """
    args = parse_args()
    
    # 获取项目根目录，用于定位配置文件和数据目录
    try:
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent.parent
        
        # 加载配置
        from src.utils.config_loader import get_config
        config = get_config(base_dir=project_root)
        
        # 设置数据目录
        if args.data_dir is None:
            data_dir = os.path.join(project_root, 'data')
        else:
            data_dir = args.data_dir
            
    except Exception as e:
        print(f"错误：获取项目根目录或加载配置时出错: {e}")
        sys.exit(1)

    # 统一设置日志系统
    setup_unified_logging(config, args.log_level, args.debug)
    logger = logging.getLogger('web_server.run') # 获取配置好的logger

    # 确保数据目录存在 (在日志系统配置好之后)
    try: 
        if not os.path.isdir(data_dir):
            logger.warning(f"数据目录不存在: {data_dir}")
            os.makedirs(data_dir, exist_ok=True)
            logger.info(f"已创建数据目录: {data_dir}")
    except Exception as e:
        logger.error(f"创建数据目录失败: {e}", exc_info=True)
        sys.exit(1)
    
    # 导入WebServer类和Scheduler类 (移到日志配置之后)
    try:
        from src.web_server.server import WebServer
        from src.web_server.scheduler import Scheduler
    except ImportError:
        logger.error("导入WebServer或Scheduler类失败，请确保安装了所有依赖", exc_info=True)
        sys.exit(1)
    
    # 创建并启动Web服务器
    logger.debug(f"准备启动Web服务器: host={args.host}, port={args.port}, debug={args.debug}")
    logger.info(f"数据目录: {data_dir}")
    
    try:
        server = WebServer(
            data_dir=data_dir,
            host=args.host,
            port=args.port,
            debug=args.debug
        )
        
        # 启动定时任务，不再需要传递config_path
        scheduler = Scheduler()
        scheduler.start()
        logger.info("定时任务已启动，将根据配置文件执行每日任务")
        
        server.run()
    
    except KeyboardInterrupt:
        logger.info("收到退出信号，服务器正在关闭...")
        if 'scheduler' in locals(): # 确保scheduler已成功初始化
            scheduler.stop()
        if 'server' in locals(): # 确保server已成功初始化
            server.shutdown()
    
    except Exception as e:
        logger.error(f"服务器运行时出错: {e}", exc_info=True)
        if 'scheduler' in locals(): # 确保scheduler已成功初始化
            scheduler.stop()
        if 'server' in locals(): # 确保server已成功初始化
            server.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    main()
