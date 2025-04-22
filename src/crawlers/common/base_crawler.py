#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import time
import json
import platform
import re
import hashlib
import datetime
import threading
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from src.utils.metadata_manager import MetadataManager

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 尝试导入html2text，如果不可用则提供一个简单的替代方案
try:
    import html2text
    HTML2TEXT_AVAILABLE = True
except ImportError:
    HTML2TEXT_AVAILABLE = False
    logging.warning("html2text库未安装，将使用简单的HTML到文本转换")

logger = logging.getLogger(__name__)

# 全局锁，用于保护元数据管理器的访问
metadata_lock = threading.RLock()
# WebDriver管理锁，防止同时创建多个driver实例
webdriver_init_lock = threading.RLock()

# 引入全局锁
from threading import RLock

# 全局锁，用于保护元数据管理器的访问
metadata_lock = RLock()

class BaseCrawler(ABC):
    """爬虫基类，提供基础爬虫功能"""
    
    # 类属性，用于保护元数据管理器的访问
    metadata_lock = metadata_lock
    
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
        
        # 创建每个爬虫实例的线程锁
        self.lock = threading.RLock()
        
        # 创建保存目录，使用相对于项目根目录的路径
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.output_dir = os.path.join(base_dir, 'data', 'raw', vendor, source_type)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化元数据管理器 - 使用线程安全的方式
        with metadata_lock:
            self.metadata_manager = MetadataManager(base_dir)
            self.metadata = self.metadata_manager.get_crawler_metadata(vendor, source_type)
        
        # 初始化HTML到Markdown转换器
        self.html_converter = self._init_html_converter()
        
        # 初始化待更新的元数据字典，用于批量更新
        self._pending_metadata_updates = {}
    
    def _init_driver(self) -> None:
        """
        初始化WebDriver，使用全局锁确保线程安全
        
        在多线程环境下，确保一次只有一个线程在初始化WebDriver
        """
        # 使用全局锁确保WebDriver初始化的线程安全
        with webdriver_init_lock:
            if self.driver:
                # 如果已经有WebDriver实例，直接返回
                return

            # 下面的内容与原方法相同
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
        """关闭WebDriver，使用锁确保线程安全"""
        with self.lock:
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
    
    # 这些方法已经被MetadataManager类替代

    def _init_html_converter(self):
        """
        初始化HTML到Markdown转换器
        
        Returns:
            HTML2Text对象或None
        """
        if HTML2TEXT_AVAILABLE:
            converter = html2text.HTML2Text()
            converter.ignore_links = False
            converter.ignore_images = False
            converter.ignore_tables = False
            converter.body_width = 0  # 不限制宽度
            converter.use_automatic_links = True  # 使用自动链接
            converter.emphasis_mark = '*'  # 强调使用星号
            converter.strong_mark = '**'  # 加粗使用双星号
            converter.wrap_links = False  # 不换行链接
            converter.pad_tables = True  # 表格填充
            return converter
        return None
    
    def save_to_markdown(self, url: str, title: str, content_and_date: Tuple[str, Optional[str]], metadata_extra: Dict[str, Any] = None, batch_mode: bool = True) -> str:
        """
        将爬取的内容保存为Markdown文件
        
        Args:
            url: 文章URL
            title: 文章标题
            content_and_date: 文章内容和发布日期元组
            metadata_extra: 额外的元数据字段，子类可传入定制化信息
            batch_mode: 是否为批量更新模式，如果为True则不立即写入metadata，而是收集到_pending_metadata_updates中
                        默认为True，以减少文件写入次数
            
        Returns:
            保存的文件路径
        """
        content, pub_date = content_and_date
        
        if not pub_date:
            pub_date = datetime.datetime.now().strftime("%Y_%m_%d")
        
        # 创建文件名
        filename = self._create_filename(url, pub_date, '.md')
        file_path = os.path.join(self.output_dir, filename)
        
        # 将日期格式转换为更友好的显示格式
        display_date = pub_date.replace('_', '-') if pub_date else "未知"
        
        # 构建Markdown内容
        metadata_lines = [
            f"# {title}",
            "",
            f"**原始链接:** [{url}]({url})",
            "",
            f"**发布时间:** {display_date}",
            "",
            f"**厂商:** {self.vendor.upper()}",
            "",
            f"**类型:** {self.source_type.upper()}",
            "",
            "---",
            "",
        ]
        final_content = "\n".join(metadata_lines) + content
        
        # 线程安全地写入文件
        with self.lock:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            # 创建metadata条目
            metadata_entry = {
                'filepath': file_path,
                'title': title,
                'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'vendor': self.vendor,
                'source_type': self.source_type
            }
            if metadata_extra:
                metadata_entry.update(metadata_extra)
            
            # 更新内存中的metadata
            with metadata_lock:
                self.metadata[url] = metadata_entry
            
            # 如果是批量更新模式，则收集metadata条目，不立即写入文件
            if batch_mode:
                self._pending_metadata_updates[url] = metadata_entry
            else:
                # 否则立即更新metadata文件
                with metadata_lock:
                    self.metadata_manager.update_crawler_metadata_entry(self.vendor, self.source_type, url, metadata_entry)
        
        return file_path
    
    def _create_filename(self, url: str, pub_date: str, ext: str) -> str:
        """
        根据发布日期和URL哈希值创建文件名
        
        Args:
            url: 文章URL
            pub_date: 发布日期（YYYY_MM_DD格式）
            ext: 文件扩展名（如.md）
            
        Returns:
            格式为: YYYY_MM_DD_URLHASH.md 的文件名
        """
        # 生成URL的哈希值（取前8位作为短哈希）
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # 组合日期和哈希值
        filename = f"{pub_date}_{url_hash}{ext}"
        
        return filename
    
    def _extract_publish_date(self, soup: BeautifulSoup, list_date: Optional[str] = None, url: str = None) -> str:
        """
        从文章中提取发布日期
        
        Args:
            soup: BeautifulSoup对象
            list_date: 从列表页获取的日期（可选）
            url: 文章URL（可选）
            
        Returns:
            发布日期字符串 (YYYY_MM_DD格式)，如果找不到则返回None
        """
        date_format = "%Y_%m_%d"
        
        # 特别针对博客的日期提取 - 优先检查time标签
        time_elements = soup.find_all('time')
        if time_elements:
            for time_elem in time_elements:
                # 检查具有datePublished属性的time标签
                if time_elem.get('property') == 'datePublished' and time_elem.get('datetime'):
                    datetime_str = time_elem.get('datetime')
                    try:
                        # 处理ISO格式的日期时间 "2025-04-08T17:34:26-07:00"
                        # 从datetime属性中提取日期部分
                        date_part = datetime_str.split('T')[0]
                        parsed_date = datetime.datetime.strptime(date_part, '%Y-%m-%d')
                        logging.info(f"从time标签的datetime属性解析到日期: {parsed_date.strftime(date_format)}")
                        return parsed_date.strftime(date_format)
                    except (ValueError, IndexError) as e:
                        logging.debug(f"解析time标签的datetime属性失败: {e}")
                
                # 如果没有datetime属性或解析失败，尝试解析标签文本
                date_text = time_elem.get_text().strip()
                if date_text:
                    try:
                        # 尝试解析 "08 APR 2025" 格式
                        parsed_date = datetime.datetime.strptime(date_text, '%d %b %Y')
                        logging.info(f"从time标签的文本内容解析到日期: {parsed_date.strftime(date_format)}")
                        return parsed_date.strftime(date_format)
                    except ValueError:
                        try:
                            # 尝试解析 "April 08, 2025" 格式
                            parsed_date = datetime.datetime.strptime(date_text, '%B %d, %Y')
                            logging.info(f"从time标签的文本内容解析到日期: {parsed_date.strftime(date_format)}")
                            return parsed_date.strftime(date_format)
                        except ValueError:
                            continue

        # 查找元数据中的日期
        meta_published = soup.find('meta', property='article:published_time') or soup.find('meta', property='publish_date')
        if meta_published and meta_published.get('content'):
            try:
                content = meta_published.get('content')
                # 处理ISO格式日期
                if 'T' in content:
                    date_part = content.split('T')[0]
                    parsed_date = datetime.datetime.strptime(date_part, '%Y-%m-%d')
                else:
                    parsed_date = datetime.datetime.strptime(content, '%Y-%m-%d')
                logging.info(f"从meta标签解析到日期: {parsed_date.strftime(date_format)}")
                return parsed_date.strftime(date_format)
            except (ValueError, IndexError) as e:
                logging.debug(f"解析meta标签日期失败: {e}")
        
        # 尝试不同的选择器来定位日期元素
        date_selectors = [
            '.lb-blog-header__date', '.blog-date', '.date', '.published-date', '.post-date',
            '.post-meta time', '.post-meta .date', '.entry-date', '.meta-date',
            'time', '[itemprop="datePublished"]', '.aws-blog-post-date', '.aws-date'
        ]
        
        # 遍历所有可能的选择器
        for selector in date_selectors:
            date_elements = soup.select(selector)
            
            if date_elements:
                for date_elem in date_elements:
                    # 尝试获取datetime属性
                    date_str = date_elem.get('datetime') or date_elem.text.strip()
                    if date_str:
                        try:
                            # 尝试多种日期格式
                            for date_pattern in [
                                '%Y-%m-%d', '%Y/%m/%d', '%b %d, %Y', '%B %d, %Y',
                                '%d %b %Y', '%d %B %Y', '%m/%d/%Y', '%d-%m-%Y',
                                '%Y年%m月%d日', '%Y.%m.%d'
                            ]:
                                try:
                                    # 提取日期字符串
                                    # 如果字符串中包含时间，只保留日期部分
                                    if ' ' in date_str and not any(month in date_str for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'January', 'February', 'March', 'April', 'June', 'July', 'August', 'September', 'October', 'November', 'December']):
                                        date_str = date_str.split(' ')[0]
                                    
                                    parsed_date = datetime.datetime.strptime(date_str, date_pattern)
                                    logging.info(f"从选择器 {selector} 解析到日期: {parsed_date.strftime(date_format)}")
                                    return parsed_date.strftime(date_format)
                                except ValueError:
                                    continue
                        except Exception as e:
                            logging.debug(f"日期解析错误: {e}")
        
        # 如果通过选择器没找到，尝试在文本中搜索日期模式
        try:
            text = soup.get_text()
            
            # 常见日期格式的正则表达式
            date_patterns = [
                # YYYY-MM-DD
                r'(\d{4}-\d{1,2}-\d{1,2})',
                # YYYY/MM/DD
                r'(\d{4}/\d{1,2}/\d{1,2})',
                # Month DD, YYYY
                r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}',
                # DD Month YYYY
                r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
                r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',
                # MM/DD/YYYY
                r'(\d{1,2}/\d{1,2}/\d{4})',
            ]
            
            for pattern in date_patterns:
                matches = re.search(pattern, text)
                if matches:
                    date_str = matches.group(0)
                    try:
                        # 尝试解析找到的日期
                        if '-' in date_str:
                            parsed_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                        elif '/' in date_str:
                            # 尝试两种不同的日期格式（YYYY/MM/DD 或 MM/DD/YYYY）
                            try:
                                parsed_date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
                            except ValueError:
                                parsed_date = datetime.datetime.strptime(date_str, '%m/%d/%Y')
                        elif ',' in date_str:
                            try:
                                parsed_date = datetime.datetime.strptime(date_str, '%B %d, %Y')
                            except ValueError:
                                parsed_date = datetime.datetime.strptime(date_str, '%b %d, %Y')
                        else:
                            try:
                                parsed_date = datetime.datetime.strptime(date_str, '%d %B %Y')
                            except ValueError:
                                parsed_date = datetime.datetime.strptime(date_str, '%d %b %Y')
                        
                        logging.info(f"从文本内容解析到日期: {parsed_date.strftime(date_format)}")
                        return parsed_date.strftime(date_format)
                    except ValueError:
                        continue
        except Exception as e:
            logging.debug(f"从文本提取日期错误: {e}")
        
        # 如果从文章中没有找到日期，使用从列表页获取的日期
        if list_date:
            logging.info(f"使用从列表页获取的日期: {list_date}")
            return list_date
            
        # 如果从URL中寻找可能的日期模式
        if url:
            url_date_match = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', url)
            if url_date_match:
                try:
                    year, month, day = url_date_match.groups()
                    parsed_date = datetime.datetime(int(year), int(month), int(day))
                    logging.info(f"从URL提取到日期: {parsed_date.strftime(date_format)}")
                    return parsed_date.strftime(date_format)
                except (ValueError, TypeError) as e:
                    logging.debug(f"从URL提取日期出错: {e}")
        
        # 如果找不到日期，使用当前日期
        logging.warning("未找到发布日期，使用当前日期")
        return datetime.datetime.now().strftime(date_format)
    
    def _html_to_markdown(self, html_content: str) -> str:
        """
        将HTML转换为Markdown
        
        Args:
            html_content: HTML内容
            
        Returns:
            Markdown内容
        """
        if self.html_converter:
            markdown_content = self.html_converter.handle(html_content)
        else:
            # 简单的HTML到文本转换
            soup = BeautifulSoup(html_content, 'lxml')
            markdown_content = soup.get_text("\n\n", strip=True)
        
        # 清理Markdown
        markdown_content = self._clean_markdown(markdown_content)
        
        return markdown_content
    
    def _clean_markdown(self, markdown_text: str) -> str:
        """
        清理Markdown文本，去除多余内容并美化格式
        
        Args:
            markdown_text: 原始Markdown文本
            
        Returns:
            清理后的Markdown文本
        """
        # 去除连续多个空行
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        # 美化代码块
        markdown_text = re.sub(r'```([^`]+)```', r'\n\n```\1```\n\n', markdown_text)
        
        # 美化图片格式，确保图片前后有空行
        markdown_text = re.sub(r'([^\n])!\[', r'\1\n\n![', markdown_text)
        markdown_text = re.sub(r'\.((?:jpg|jpeg|png|gif|webp|svg))\)([^\n])', r'.\1)\n\n\2', markdown_text)
        
        return markdown_text
    
    def _is_likely_blog_post(self, url: str) -> bool:
        """
        判断URL是否可能是博客文章
        
        Args:
            url: 要检查的URL
            
        Returns:
            True如果URL可能是博客文章，否则False
        """
        # 移除协议和域名部分
        parsed = urlparse(url)
        path = parsed.path
        
        # 博客文章URL的常见模式
        blog_patterns = [
            r'/blogs/[^/]+/[^/]+',  # 如 /blogs/networking-and-content-delivery/article-name
            r'/blog/[^/]+',         # 如 /blog/article-name
            r'/post/[^/]+',         # 如 /post/article-name
            r'/\d{4}/\d{2}/[^/]+',  # 如 /2022/01/article-name (日期格式)
            r'/news/[^/]+',         # 如 /news/article-name
            r'/announcements/[^/]+', # 如 /announcements/article-name
        ]
        
        # 检查是否匹配任何博客文章模式
        for pattern in blog_patterns:
            if re.search(pattern, path):
                return True
        
        # 排除明显的非文章页面
        exclude_patterns = [
            r'/tag/', r'/tags/', r'/category/', r'/categories/',
            r'/author/', r'/about/', r'/contact/', r'/feed/',
            r'/archive/', r'/archives/', r'/page/\d+', r'/search/'
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, path):
                return False
                
        # 检查是否在URL路径中包含特定关键词
        blog_keywords = ['post', 'article', 'blog', 'news', 'announcement']
        for keyword in blog_keywords:
            if keyword in path.lower():
                return True
                
        # 默认返回False，宁可错过也不要误报
        return False
    
    def process_articles_in_batches(self, article_info: List[Tuple], batch_size: int = 10) -> List[str]:
        """
        分批处理文章，减少锁的竞争和文件写入次数
        
        Args:
            article_info: 文章信息列表，每项为(标题, URL, 日期)元组
            batch_size: 每批处理的文章数量，默认为10
            
        Returns:
            保存的文件路径列表
        """
        saved_files = []
        
        # 检查是否启用了强制模式
        force_mode = self.crawler_config.get('force', False)
        if force_mode:
            logger.info("强制模式已启用，将重新爬取所有文章，忽略本地metadata")
        
        # 分批处理文章
        for i in range(0, len(article_info), batch_size):
            batch = article_info[i:i+batch_size]
            logger.info(f"处理第 {i//batch_size + 1} 批文章，共 {len(batch)} 篇")
            
            # 在处理每批文章前刷新metadata，确保内存中的metadata是最新的
            self.refresh_metadata()
            
            # 过滤已爬取的文章（如果不是强制模式）
            filtered_batch = []
            for title, url, list_date in batch:
                if force_mode:
                    # 强制模式下，不跳过任何文章
                    filtered_batch.append((title, url, list_date))
                    logger.info(f"强制模式：将重新爬取文章: {title} ({url})")
                else:
                    # 非强制模式下，跳过已爬取的文章
                    # 减少锁的持有时间，只在检查URL是否在metadata中时使用锁
                    is_url_in_metadata = False
                    with metadata_lock:
                        is_url_in_metadata = url in self.metadata and 'filepath' in self.metadata[url] and os.path.exists(self.metadata[url]['filepath'])
                    
                    if is_url_in_metadata:
                        logger.info(f"跳过已爬取的文章: {title} ({url})")
                        saved_files.append(self.metadata[url]['filepath'])
                    else:
                        filtered_batch.append((title, url, list_date))
            
            # 处理这一批文章
            for idx, (title, url, list_date) in enumerate(filtered_batch, 1):
                try:
                    logger.info(f"正在爬取第 {idx}/{len(filtered_batch)} 篇文章: {title}")
                    
                    # 获取文章内容
                    article_html = self._get_article_html(url)
                    if not article_html:
                        logger.warning(f"获取文章内容失败: {url}")
                        continue
                    
                    # 解析文章内容和日期
                    article_content, pub_date = self._parse_article_content(url, article_html, list_date)
                    
                    # 保存为Markdown，使用批量更新模式
                    file_path = self.save_to_markdown(url, title, (article_content, pub_date), batch_mode=True)
                    saved_files.append(file_path)
                    logger.info(f"已保存文章: {title} -> {file_path}")
                    
                    # 间隔一段时间再爬取下一篇
                    if idx < len(filtered_batch):
                        time.sleep(self.interval)
                        
                except Exception as e:
                    logger.error(f"爬取文章失败: {url} - {e}")
            
            # 批量更新这一批文章的metadata
            if self._pending_metadata_updates:
                self.batch_update_metadata()
        
        return saved_files
    
    def _get_article_html(self, url: str) -> Optional[str]:
        """
        获取文章HTML内容，优先使用requests，失败时使用Selenium
        
        Args:
            url: 文章URL
            
        Returns:
            文章HTML内容或None（如果失败）
        """
        # 尝试使用requests获取文章内容
        try:
            logger.info(f"使用requests库获取文章内容: {url}")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                logger.info("使用requests库成功获取到文章内容")
                return response.text
            else:
                logger.error(f"请求返回非成功状态码: {response.status_code}")
        except Exception as e:
            logger.error(f"使用requests库获取文章失败: {e}")
        
        # 如果requests失败，尝试使用Selenium
        if not self.driver:
            self._init_driver()
        
        try:
            logger.info(f"尝试使用Selenium获取文章内容: {url}")
            return self._get_selenium(url)
        except Exception as e:
            logger.warning(f"使用Selenium获取文章失败: {e}")
        
        return None
    
    def _parse_article_content(self, url: str, html: str, list_date: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """
        从文章页面解析文章内容和发布日期
        
        Args:
            url: 文章URL
            html: 文章页面HTML
            list_date: 从列表页获取的日期（可能为None）
            
        Returns:
            (文章内容, 发布日期)元组，如果找不到日期则使用列表页日期或当前日期
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # 提取发布日期
        pub_date = self._extract_publish_date(soup, list_date, url)
        
        # 提取文章内容
        article_content = self._extract_article_content(soup, url)
        
        return article_content, pub_date
    
    def _extract_article_content(self, soup: BeautifulSoup, url: str) -> str:
        """
        从文章页面提取文章内容
        
        Args:
            soup: BeautifulSoup对象
            url: 文章URL
            
        Returns:
            Markdown格式的文章内容
        """
        # 尝试定位文章主体内容
        content_selectors = [
            'article', 
            '.entry-content', 
            '.post-content', 
            '.article-content', 
            '.main-content',
            '.blog-post',
            '.content-container',
            'main',
            '#main-content'
        ]
        
        article_elem = None
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                # 选择最长的元素作为文章主体
                article_elem = max(elements, key=lambda x: len(str(x)))
                break
        
        # 如果没有找到文章主体，使用页面主体
        if not article_elem:
            article_elem = soup.find('body')
            
        if not article_elem:
            logger.warning(f"未找到文章主体: {url}")
            return "无法提取文章内容"
        
        # 清理非内容元素
        for elem in article_elem.select('header, footer, sidebar, .sidebar, nav, .navigation, .ad, .ads, .comments, .social-share'):
            elem.decompose()
        
        # 转换为Markdown
        html = str(article_elem)
        if self.html_converter:
            markdown_content = self.html_converter.handle(html)
        else:
            # 简单的HTML到文本转换
            markdown_content = article_elem.get_text("\n\n", strip=True)
        
        # 清理和美化Markdown
        markdown_content = self._clean_markdown(markdown_content)
        
        return markdown_content
    
    def batch_update_metadata(self) -> None:
        """
        批量更新所有待更新的metadata条目，减少文件写入次数
        
        在爬取完成后调用此方法，一次性更新所有收集的metadata条目
        """
        if not self._pending_metadata_updates:
            logger.info("没有待更新的metadata条目")
            return
        
        logger.info(f"批量更新 {len(self._pending_metadata_updates)} 个metadata条目")
        with metadata_lock:
            self.metadata_manager.update_crawler_metadata_entries_batch(
                self.vendor, 
                self.source_type, 
                self._pending_metadata_updates
            )
        
        # 清空待更新列表
        self._pending_metadata_updates = {}
        logger.info("批量更新metadata完成")
    
    def refresh_metadata(self) -> None:
        """
        刷新内存中的metadata，确保与文件同步
        
        在处理一批文章前调用，确保内存中的metadata是最新的
        """
        logger.info(f"刷新 {self.vendor}/{self.source_type} 的metadata")
        with metadata_lock:
            self.metadata = self.metadata_manager.get_crawler_metadata(self.vendor, self.source_type)
        logger.info(f"metadata刷新完成，共 {len(self.metadata)} 条记录")
    
    def should_crawl(self, url: str) -> bool:
        """
        检查是否需要爬取某个URL
        
        注意：此方法不推荐在爬取流程中直接使用，因为这样会导致先请求网页内容再检查URL，
        浪费网络资源。推荐的做法是在解析URL列表后，立即过滤掉已爬取的URL，然后再进行爬取。
        
        Args:
            url: 要检查的URL
            
        Returns:
            True 如果需要爬取，False 如果不需要（已存在）
        """
        # 减少锁的持有时间，只在检查URL是否在metadata中时使用锁
        is_url_in_metadata = False
        with metadata_lock:
            is_url_in_metadata = url in self.metadata
        
        if is_url_in_metadata:
            logger.info(f"跳过已爬取的URL: {url}")
            return False
        return True

    def run(self) -> List[str]:
        """
        运行爬虫
        
        Returns:
            保存的文件路径列表
        """
        try:
            logger.info(f"开始爬取 {self.vendor} {self.source_type}")
            
            # 在爬取前刷新metadata，确保内存中的metadata是最新的
            self.refresh_metadata()
            
            # 清空待更新列表，确保每次运行都是从空列表开始
            self._pending_metadata_updates = {}
            
            results = self._crawl()
            
            # 强制批量更新metadata，无论爬虫子类是否显式调用
            # 这确保了即使爬虫子类没有调用batch_update_metadata，metadata也会被正确更新
            logger.info(f"爬取完成，检查是否有待更新的metadata条目")
            if self._pending_metadata_updates:
                logger.info(f"发现 {len(self._pending_metadata_updates)} 个待更新的metadata条目，执行批量更新")
                self.batch_update_metadata()
            else:
                logger.info("没有待更新的metadata条目，跳过批量更新")
                
            logger.info(f"爬取完成 {self.vendor} {self.source_type}, 共爬取 {len(results)} 个文件")
            return results
        except Exception as e:
            logger.error(f"爬取失败 {self.vendor} {self.source_type}: {e}")
            # 即使爬取失败，也尝试更新已收集的metadata
            if self._pending_metadata_updates:
                logger.info(f"爬取失败，但仍有 {len(self._pending_metadata_updates)} 个待更新的metadata条目，执行批量更新")
                try:
                    self.batch_update_metadata()
                except Exception as update_e:
                    logger.error(f"批量更新metadata失败: {update_e}")
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
