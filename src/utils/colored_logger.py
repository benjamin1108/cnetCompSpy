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
        # 保存原始的格式字符串
        original_fmt = self._style._fmt
        
        if self.use_colors and record.levelno in self.LEVEL_COLORS:
            # 为不同级别的日志添加不同的颜色
            color = self.LEVEL_COLORS[record.levelno]
            self._style._fmt = f"{color}{original_fmt}{Colors.RESET}"
        
        # 格式化日志记录
        result = logging.Formatter.format(self, record)
        
        # 恢复原始的格式字符串
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

class CategoryLogger:
    """
    分类日志记录器，支持不同分类使用不同颜色
    """
    # 不同类别的默认颜色
    CATEGORY_COLORS = {
        "crawl": Colors.BLUE,
        "parse": Colors.CYAN,
        "save": Colors.GREEN,
        "network": Colors.MAGENTA,
        "db": Colors.YELLOW,
        "api": Colors.BRIGHT_CYAN,
        "analysis": Colors.BRIGHT_MAGENTA,
        "system": Colors.BRIGHT_WHITE,
        "default": Colors.WHITE
    }
    
    def __init__(self, name: str, categories: Dict[str, str] = None):
        """
        初始化分类日志记录器
        
        Args:
            name: 日志记录器名称
            categories: 自定义分类和颜色映射，格式为 {分类名: 颜色代码}
                       如果为None，则使用默认分类颜色
        """
        self.logger = logging.getLogger(name)
        self.categories = self.CATEGORY_COLORS.copy()
        
        # 更新自定义分类
        if categories:
            self.categories.update(categories)
    
    def _log(self, level: int, category: str, msg: str, *args, **kwargs):
        """
        记录日志的内部方法
        
        Args:
            level: 日志级别
            category: 日志分类
            msg: 日志消息
            args: 格式化参数
            kwargs: 关键字参数
        """
        # 获取分类的颜色
        color = self.categories.get(category, self.categories["default"])
        
        # 格式化分类前缀
        category_prefix = f"{color}[{category}]{Colors.RESET} "
        
        # 记录带有分类前缀的日志
        self.logger.log(level, category_prefix + msg, *args, **kwargs)
    
    def debug(self, category: str, msg: str, *args, **kwargs):
        """记录调试级别的日志"""
        self._log(logging.DEBUG, category, msg, *args, **kwargs)
    
    def info(self, category: str, msg: str, *args, **kwargs):
        """记录信息级别的日志"""
        self._log(logging.INFO, category, msg, *args, **kwargs)
    
    def warning(self, category: str, msg: str, *args, **kwargs):
        """记录警告级别的日志"""
        self._log(logging.WARNING, category, msg, *args, **kwargs)
    
    def error(self, category: str, msg: str, *args, **kwargs):
        """记录错误级别的日志"""
        self._log(logging.ERROR, category, msg, *args, **kwargs)
    
    def critical(self, category: str, msg: str, *args, **kwargs):
        """记录严重错误级别的日志"""
        self._log(logging.CRITICAL, category, msg, *args, **kwargs)
    
    def set_category_color(self, category: str, color: str):
        """设置分类的颜色"""
        self.categories[category] = color

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
    
    # 创建分类日志记录器
    category_logger = CategoryLogger("category_example")
    
    # 使用不同分类输出日志
    category_logger.info("crawl", "开始爬取网页")
    category_logger.info("parse", "解析页面内容")
    category_logger.warning("network", "网络连接不稳定")
    category_logger.error("db", "数据库连接失败")
    category_logger.critical("system", "系统内存不足")
    
    # 自定义分类颜色
    category_logger.set_category_color("custom", Colors.BRIGHT_GREEN)
    category_logger.info("custom", "自定义分类的日志") 