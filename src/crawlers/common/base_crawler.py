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
        
        # 创建保存目录，使用相对于项目根目录的路径
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.output_dir = os.path.join(base_dir, 'data', 'raw', vendor, source_type)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _init_driver(self) -> None:
        """初始化WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # 使用新的无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')  # 禁用软件光栅化
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')  # 禁用显示合成器
        chrome_options.add_argument('--mute-audio')  # 静音，避免声音相关问题
        
        # 从配置中获取是否使用有界面模式
        if not self.crawler_config.get('headless', True):
            # 移除无头模式参数
            chrome_options.arguments = [arg for arg in chrome_options.arguments if not arg.startswith('--headless')]
            logger.debug("使用有界面模式")
        
        try:
            # 获取项目根目录路径
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            
            # 从配置文件获取驱动路径
            config_path = os.path.join(base_dir, 'drivers', 'webdriver_config.json')
            
            if not os.path.exists(config_path):
                logger.error(f"WebDriver配置文件不存在: {config_path}")
                logger.error("请先运行 'bash scripts/setup_latest_driver.sh' 安装驱动")
                raise FileNotFoundError(f"WebDriver配置文件不存在: {config_path}")
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            chrome_path = config.get('chrome_path')
            chromedriver_path = config.get('chromedriver_path')
            chrome_version = config.get('version')
            
            # 验证路径是否存在
            if not chrome_path or not os.path.exists(chrome_path):
                logger.error(f"chrome-headless-shell不存在: {chrome_path}")
                logger.error("请先运行 'bash scripts/setup_latest_driver.sh' 安装驱动")
                raise FileNotFoundError(f"chrome-headless-shell不存在: {chrome_path}")
            
            if not chromedriver_path or not os.path.exists(chromedriver_path):
                logger.error(f"chromedriver不存在: {chromedriver_path}")
                logger.error("请先运行 'bash scripts/setup_latest_driver.sh' 安装驱动")
                raise FileNotFoundError(f"chromedriver不存在: {chromedriver_path}")
            
            # 验证驱动程序是否可执行
            try:
                import subprocess
                result = subprocess.run([chrome_path, '--version'], capture_output=True, text=True, timeout=5)
                if result.stdout:
                    logger.debug(f"chrome-headless-shell版本: {result.stdout.strip()}")
                
                if result.returncode != 0:
                    error_msg = result.stderr.strip() if result.stderr else "未知错误"
                    if "error while loading shared libraries" in error_msg:
                        missing_lib = error_msg.split("error while loading shared libraries:")[1].split(":")[0].strip()
                        logger.error(f"chrome-headless-shell缺少系统依赖库: {missing_lib}")
                        logger.error("请运行 'bash scripts/setup_latest_driver.sh' 查看并安装缺少的依赖")
                        raise RuntimeError(f"chrome-headless-shell缺少系统依赖库: {missing_lib}")
                    else:
                        logger.warning(f"chrome-headless-shell执行测试发出警告: {error_msg}")
            except subprocess.TimeoutExpired:
                logger.warning("chrome-headless-shell版本检测超时，继续执行")
            except Exception as e:
                logger.warning(f"chrome-headless-shell版本检测失败: {e}，继续执行")
            
            # 设置chrome二进制文件位置
            chrome_options.binary_location = chrome_path
            logger.debug(f"使用chrome-headless-shell: {chrome_path}, 版本: {chrome_version}")
            
            # 初始化WebDriver (添加更多错误处理)
            service = Service(executable_path=chromedriver_path)
            try:
                self.driver = webdriver.Chrome(options=chrome_options, service=service)
                logger.debug(f"使用ChromeDriver: {chromedriver_path}, 版本: {chrome_version}")
            except Exception as e:
                # 如果使用--no-sandbox仍然失败，则尝试几种备选方案
                if "--no-sandbox" in chrome_options.arguments:
                    logger.warning(f"使用--no-sandbox模式初始化WebDriver失败: {e}")
                    logger.warning("尝试使用其他配置...")
                    
                    # 尝试方案1: 移除--headless参数
                    try:
                        logger.debug("尝试方案1: 移除--headless参数")
                        alt_options = Options()
                        alt_options.binary_location = chrome_path
                        alt_options.add_argument('--no-sandbox')
                        alt_options.add_argument('--disable-dev-shm-usage')
                        alt_options.add_argument('--disable-gpu')
                        self.driver = webdriver.Chrome(options=alt_options, service=service)
                        logger.debug("方案1成功：非无头模式")
                    except Exception as e1:
                        logger.warning(f"方案1失败: {e1}")
                        
                        # 尝试方案2: 仅使用基本参数
                        try:
                            logger.debug("尝试方案2: 仅使用基本参数")
                            alt_options = Options()
                            alt_options.binary_location = chrome_path
                            alt_options.add_argument('--no-sandbox')
                            alt_options.add_argument('--disable-dev-shm-usage')
                            self.driver = webdriver.Chrome(options=alt_options, service=service)
                            logger.debug("方案2成功：使用最小参数集")
                        except Exception as e2:
                            logger.warning(f"方案2失败: {e2}")
                            raise Exception(f"无法初始化WebDriver: 所有方法都失败。\n原始错误: {e}\n尝试运行 'bash scripts/setup_latest_driver.sh' 检查并修复依赖问题。")
                else:
                    raise
            
            # 设置不同类型的超时
            self.driver.set_page_load_timeout(self.crawler_config.get('page_load_timeout', 45))
            self.driver.set_script_timeout(self.crawler_config.get('script_timeout', 30))
            # 设置隐式等待 - 所有元素查找操作的基础等待
            self.driver.implicitly_wait(self.crawler_config.get('implicit_wait', 10))
            
            logger.debug(f"WebDriver初始化成功，配置了多级超时机制")
        except Exception as e:
            logger.error(f"WebDriver初始化失败: {e}")
            if "cannot find Chrome binary" in str(e):
                logger.error(f"无法找到Chrome二进制文件。请确保chrome-headless-shell已正确安装并且具有执行权限。")
                logger.error(f"尝试运行 'bash scripts/setup_latest_driver.sh' 重新安装驱动。")
            elif "session not created" in str(e) and "user data directory" in str(e):
                logger.error(f"WebDriver会话创建失败。这可能是由于Chrome配置文件问题导致的。")
                logger.error(f"请尝试在启动脚本之前关闭所有Chrome实例，或者运行 'rm -rf ~/.config/google-chrome' 清理配置文件。")
            elif "error while loading shared libraries" in str(e):
                logger.error(f"缺少系统依赖库。请运行 'bash scripts/setup_latest_driver.sh' 检测并安装缺少的依赖。")
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
    
    def wait_for_element(self, by, value, timeout=None, condition=EC.presence_of_element_located):
        """
        智能等待元素
        
        Args:
            by: 定位方法 (By.ID, By.CSS_SELECTOR等)
            value: 元素定位值
            timeout: 超时时间，如果为None则使用默认值
            condition: 等待条件，默认为元素存在
        
        Returns:
            找到的WebElement对象
        """
        if timeout is None:
            timeout = self.crawler_config.get('default_element_timeout', 15)
        
        return WebDriverWait(self.driver, timeout).until(
            condition((by, value))
        )

    def wait_for_page_load(self):
        """等待页面完全加载"""
        # 等待DOM准备就绪
        WebDriverWait(self.driver, self.crawler_config.get('page_load_timeout', 45)).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 等待页面上的Ajax加载完成
        try:
            script = "return document.readyState === 'complete'"
            WebDriverWait(self.driver, self.crawler_config.get('page_load_timeout', 45)).until(
                lambda driver: driver.execute_script(script)
            )
        except Exception as e:
            logger.warning(f"等待页面readyState完成时超时: {e}")
            # 继续处理，因为页面可能已经加载了足够的内容
    
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
                # 使用改进的页面加载等待
                self.wait_for_page_load()
                
                # 对于特别复杂的页面，可以添加额外等待
                if any(keyword in url.lower() for keyword in ['azure', 'cloud.google', 'complex']):
                    # 使用更长的超时等待复杂页面上的关键元素
                    long_timeout = self.crawler_config.get('long_element_timeout', 25)
                    try:
                        # 等待主要内容出现
                        self.wait_for_element(
                            By.CSS_SELECTOR, 
                            "article, .content, main, #main-content", 
                            timeout=long_timeout
                        )
                    except Exception as content_e:
                        # 超时但页面可能已经有足够内容，继续处理
                        logger.warning(f"页面主要内容等待超时，但继续处理: {url} - {content_e}")
                
                return self.driver.page_source
            except Exception as e:
                logger.warning(f"Selenium请求失败 (尝试 {i+1}/{self.retry}): {url} - {e}")
                if i < self.retry - 1:
                    # 增加指数退避重试间隔
                    retry_interval = self.interval * (i + 1)
                    time.sleep(retry_interval)
        
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