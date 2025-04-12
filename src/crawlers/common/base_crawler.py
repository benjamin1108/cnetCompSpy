#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import time
import json
import platform
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    """爬虫基类，提供基础爬虫功能"""
    
    def __init__(self, config: Dict[str, Any], vendor: str, source_type: str):
        """
        初始化爬虫
        
        Args:
            config: 配置信息
            vendor: 厂商名称（如aws, azure等）
            source_type: 源类型（如blog, docs等）
        """
        self.config = config
        self.vendor = vendor
        self.source_type = source_type
        self.crawler_config = config.get('crawler', {})
        self.timeout = self.crawler_config.get('timeout', 30)
        self.retry = self.crawler_config.get('retry', 3)
        self.interval = self.crawler_config.get('interval', 2)
        self.headers = self.crawler_config.get('headers', {})
        self.driver = None
        
        # 创建保存目录
        self.output_dir = os.path.join('data', 'raw', vendor, source_type)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _init_driver(self) -> None:
        """初始化WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        try:
            # 获取ChromeDriver路径
            chromedriver_path = os.path.join('drivers', 'chromedriver')
            if platform.system().lower() == 'windows':
                chromedriver_path += '.exe'
            
            # 尝试使用已安装的chrome-headless-shell
            config_path = os.path.join('drivers', 'webdriver_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                chrome_path = config.get('chrome_path')
                if chrome_path and os.path.exists(chrome_path):
                    chrome_options.binary_location = chrome_path
                    logger.debug(f"使用chrome-headless-shell: {chrome_path}")
            
            # 尝试多种方式初始化WebDriver
            try:
                # 方法1: 使用我们自己下载的chromedriver
                if os.path.exists(chromedriver_path):
                    logger.debug(f"使用已下载的ChromeDriver: {chromedriver_path}")
                    service = Service(executable_path=chromedriver_path)
                    self.driver = webdriver.Chrome(options=chrome_options, service=service)
                    logger.debug("方法1成功：使用下载的ChromeDriver初始化WebDriver")
                else:
                    raise FileNotFoundError(f"ChromeDriver不存在: {chromedriver_path}")
            except Exception as e1:
                logger.warning(f"方法1失败: {e1}")
                
                try:
                    # 方法2: 直接使用Service()，让系统查找ChromeDriver
                    service = Service()
                    self.driver = webdriver.Chrome(options=chrome_options, service=service)
                    logger.debug("方法2成功：使用默认Service初始化WebDriver")
                except Exception as e2:
                    logger.warning(f"方法2失败: {e2}")
                    
                    try:
                        # 方法3: 使用webdriver_manager自动下载
                        from webdriver_manager.chrome import ChromeDriverManager
                        service = Service(ChromeDriverManager().install())
                        self.driver = webdriver.Chrome(options=chrome_options, service=service)
                        logger.debug("方法3成功：使用webdriver_manager初始化WebDriver")
                    except Exception as e3:
                        logger.warning(f"方法3失败: {e3}")
                        
                        try:
                            # 方法4: 尝试使用系统Chrome/Chromium
                            potential_paths = []
                            
                            if platform.system().lower() == 'darwin':  # macOS
                                potential_paths = [
                                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                                    "/Applications/Chromium.app/Contents/MacOS/Chromium"
                                ]
                            elif platform.system().lower() == 'linux':
                                potential_paths = [
                                    "/usr/bin/google-chrome",
                                    "/usr/bin/chromium-browser",
                                    "/usr/bin/chromium"
                                ]
                            elif platform.system().lower() == 'windows':
                                potential_paths = [
                                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                                ]
                                
                            for path in potential_paths:
                                if os.path.exists(path):
                                    chrome_options.binary_location = path
                                    self.driver = webdriver.Chrome(options=chrome_options)
                                    logger.debug(f"方法4成功：使用系统Chrome: {path}")
                                    break
                            else:
                                raise Exception("未找到系统Chrome")
                        except Exception as e4:
                            logger.error(f"方法4失败: {e4}")
                            raise Exception(f"无法初始化WebDriver: 所有方法都失败")
            
            self.driver.set_page_load_timeout(self.timeout)
            logger.debug(f"WebDriver初始化成功")
        except Exception as e:
            logger.error(f"WebDriver初始化失败: {e}")
            raise
    
    def _close_driver(self) -> None:
        """关闭WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.debug("WebDriver已关闭")
    
    def _get_http(self, url: str) -> Optional[str]:
        """
        使用requests获取网页内容
        
        Args:
            url: 目标URL
            
        Returns:
            网页HTML内容或None（如果失败）
        """
        for i in range(self.retry):
            try:
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.warning(f"HTTP请求失败 (尝试 {i+1}/{self.retry}): {url} - {e}")
                if i < self.retry - 1:
                    time.sleep(self.interval)
        
        return None
    
    def _get_selenium(self, url: str) -> Optional[str]:
        """
        使用Selenium获取网页内容
        
        Args:
            url: 目标URL
            
        Returns:
            网页HTML内容或None（如果失败）
        """
        if not self.driver:
            self._init_driver()
        
        for i in range(self.retry):
            try:
                self.driver.get(url)
                # 等待页面加载完成
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                return self.driver.page_source
            except Exception as e:
                logger.warning(f"Selenium请求失败 (尝试 {i+1}/{self.retry}): {url} - {e}")
                if i < self.retry - 1:
                    time.sleep(self.interval)
        
        return None
    
    def save_to_markdown(self, url: str, title: str, content: str, images: List[Dict[str, str]]) -> str:
        """
        将爬取内容保存为Markdown格式
        
        Args:
            url: 原始URL
            title: 内容标题
            content: HTML内容
            images: 图片列表，每个项包含{url, path}
            
        Returns:
            保存的文件路径
        """
        # 生成文件名
        filename = f"{self._sanitize_filename(title)}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # 构建Markdown内容
        md_content = f"# {title}\n\n"
        md_content += f"原始链接: {url}\n\n"
        md_content += f"爬取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += f"厂商: {self.vendor}\n\n"
        md_content += f"类型: {self.source_type}\n\n"
        md_content += "---\n\n"
        md_content += content
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"已保存Markdown文件: {filepath}")
        return filepath
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def run(self) -> List[str]:
        """
        运行爬虫
        
        Returns:
            保存的文件路径列表
        """
        try:
            logger.info(f"开始爬取 {self.vendor} {self.source_type}")
            results = self._crawl()
            logger.info(f"爬取完成 {self.vendor} {self.source_type}, 共爬取 {len(results)} 个文件")
            return results
        except Exception as e:
            logger.error(f"爬取失败 {self.vendor} {self.source_type}: {e}")
            return []
        finally:
            self._close_driver()
    
    @abstractmethod
    def _crawl(self) -> List[str]:
        """
        具体爬虫逻辑，由子类实现
        
        Returns:
            保存的文件路径列表
        """
        pass 