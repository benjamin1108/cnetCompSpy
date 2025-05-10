#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
from typing import Optional, Dict, Any

class Colors:
    """ANSI颜色代码"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # 前景色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # 高亮前景色
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # 背景色
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

class ColoredFormatter(logging.Formatter):
    """自定义的彩色日志格式化器"""
    
    LEVEL_COLORS = {
        logging.DEBUG: Colors.BLUE,
        logging.INFO: Colors.BRIGHT_BLACK,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BG_RED + Colors.WHITE + Colors.BOLD,
    }
    
    def __init__(self, fmt: str = None, datefmt: str = None, use_colors: bool = True):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.use_colors = use_colors
    
    def format(self, record):
        original_fmt = self._style._fmt
        
        color_override = getattr(record, 'color_override', None)

        if self.use_colors:
            if color_override:
                self._style._fmt = f"{color_override}{original_fmt}{Colors.RESET}"
            elif record.levelno in self.LEVEL_COLORS:
                color = self.LEVEL_COLORS[record.levelno]
                self._style._fmt = f"{color}{original_fmt}{Colors.RESET}"
            # If no override and not a standard level with color, use default (no color for this part)
            # else: pass # Or handle explicitly if needed
        
        result = logging.Formatter.format(self, record)
        self._style._fmt = original_fmt
        return result

def setup_colored_logging(level: int = logging.INFO, 
                         log_file: Optional[str] = None,
                         fmt: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                         datefmt: str = '%Y-%m-%d %H:%M:%S',
                         use_colors: bool = True) -> None:
    """
    设置彩色日志系统
    
    Args:
        level: 日志级别
        log_file: 日志文件路径，如果为None则不输出到文件
        fmt: 日志格式
        datefmt: 日期格式
        use_colors: 是否使用彩色输出
    """
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # 使用彩色格式化器
    colored_formatter = ColoredFormatter(fmt=fmt, datefmt=datefmt, use_colors=use_colors)
    console_handler.setFormatter(colored_formatter)
    root_logger.addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        # 确保日志文件目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # 创建不带颜色的格式化器(文件中不需要ANSI颜色代码)
        file_formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
    return root_logger

# 使用示例
if __name__ == "__main__":
    # 设置彩色日志
    setup_colored_logging(level=logging.DEBUG)
    
    # 创建普通日志记录器
    logger = logging.getLogger("example")
    
    # 输出不同级别的日志
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.critical("这是一条严重错误日志") 