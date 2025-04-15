#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
import time
import random

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.utils.colored_logger import setup_colored_logging, CategoryLogger, Colors

def simulate_crawler_activity():
    """模拟爬虫活动"""
    logger = logging.getLogger("crawler_simulation")
    cat_logger = CategoryLogger("crawler", {
        "network": Colors.BLUE,
        "parser": Colors.BRIGHT_CYAN,
        "storage": Colors.GREEN,
        "error": Colors.BRIGHT_RED,
        "cache": Colors.YELLOW
    })
    
    # 模拟爬虫工作过程
    websites = ["example.com", "blog.example.org", "docs.example.net", "api.example.io"]
    
    logger.info("开始模拟爬虫活动")
    
    for website in websites:
        # 模拟网络请求
        cat_logger.info("network", f"正在连接到 {website}...")
        time.sleep(0.5)
        
        # 随机模拟连接错误
        if random.random() < 0.3:
            cat_logger.error("network", f"连接到 {website} 失败！重试中...")
            time.sleep(0.3)
            cat_logger.info("network", f"重新连接到 {website} 成功")
        
        # 模拟解析内容
        cat_logger.info("parser", f"开始解析 {website} 的内容")
        time.sleep(0.2)
        
        # 模拟解析结果
        articles = random.randint(3, 10)
        cat_logger.info("parser", f"在 {website} 上找到 {articles} 篇文章")
        
        # 模拟缓存操作
        cat_logger.debug("cache", f"正在缓存 {website} 的内容...")
        
        # 模拟存储操作
        cat_logger.info("storage", f"正在保存来自 {website} 的 {articles} 篇文章")
        
        # 随机模拟存储错误
        if random.random() < 0.2:
            cat_logger.error("storage", f"保存文章时发生错误: 磁盘空间不足")
            cat_logger.warning("storage", "尝试使用备用存储路径")
            time.sleep(0.2)
            cat_logger.info("storage", "使用备用路径成功保存文章")
    
    logger.info("爬虫模拟活动完成")

def simulate_analysis():
    """模拟分析数据活动"""
    logger = logging.getLogger("analysis_simulation")
    cat_logger = CategoryLogger("analysis", {
        "data": Colors.MAGENTA,
        "model": Colors.BRIGHT_BLUE,
        "result": Colors.BRIGHT_GREEN,
        "error": Colors.RED,
        "warning": Colors.YELLOW
    })
    
    # 模拟数据分析过程
    datasets = ["aws_news", "azure_updates", "gcp_releases"]
    
    logger.info("开始模拟数据分析")
    
    for dataset in datasets:
        # 模拟数据加载
        cat_logger.info("data", f"正在加载数据集 {dataset}...")
        time.sleep(0.5)
        
        # 模拟数据验证
        if random.random() < 0.25:
            cat_logger.warning("data", f"数据集 {dataset} 中存在部分缺失值")
            cat_logger.info("data", "正在处理缺失值...")
            time.sleep(0.3)
        
        # 模拟模型训练或应用
        cat_logger.info("model", f"对 {dataset} 应用分析模型")
        time.sleep(0.7)
        
        # 模拟结果
        insights = random.randint(5, 15)
        cat_logger.info("result", f"从 {dataset} 中发现 {insights} 个见解")
        
        # 随机模拟警告
        if random.random() < 0.4:
            cat_logger.warning("warning", f"模型对 {dataset} 的分析置信度较低")
            
    # 模拟严重错误
    if random.random() < 0.3:
        cat_logger.critical("error", "分析引擎内存不足，部分任务被中止")
    
    logger.info("数据分析模拟完成")

def main():
    # 设置彩色日志
    log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "example.log")
    
    # 确保日志目录存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 初始化彩色日志
    setup_colored_logging(
        level=logging.DEBUG,
        log_file=log_file,
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 常规日志记录示例
    logger = logging.getLogger("example")
    logger.info("彩色日志工具示例程序启动")
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.critical("这是一条严重错误日志")
    
    # 分隔符
    print("\n" + "="*50 + "\n")
    
    # 模拟爬虫活动
    simulate_crawler_activity()
    
    # 分隔符
    print("\n" + "="*50 + "\n")
    
    # 模拟分析活动
    simulate_analysis()
    
    # 结束
    logger.info("彩色日志工具示例程序结束")

if __name__ == "__main__":
    main() 