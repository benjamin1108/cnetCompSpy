#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re
import sys
import time
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests
import markdown
import html2text

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

from src.crawlers.common.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)

class AwsBlogCrawler(BaseCrawler):
    """AWS博客爬虫实现"""
    
    def __init__(self, config: Dict[str, Any], vendor: str, source_type: str):
        """初始化AWS博客爬虫"""
        super().__init__(config, vendor, source_type)
        self.source_config = config.get('sources', {}).get(vendor, {}).get(source_type, {})
        self.start_url = self.source_config.get('url')
        
        # 初始化HTML到Markdown转换器
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.ignore_tables = False
        self.html_converter.body_width = 0  # 不限制宽度
        self.html_converter.use_automatic_links = True  # 使用自动链接
        self.html_converter.emphasis_mark = '*'  # 强调使用星号
        self.html_converter.strong_mark = '**'  # 加粗使用双星号
        self.html_converter.wrap_links = False  # 不换行链接
        self.html_converter.pad_tables = True  # 表格填充
    
    def _crawl(self) -> List[str]:
        """
        爬取AWS博客
        
        Returns:
            保存的文件路径列表
        """
        if not self.start_url:
            logger.error("未配置起始URL")
            return []
        
        saved_files = []
        
        try:
            # 获取博客列表页
            logger.info(f"获取博客列表页: {self.start_url}")
            html = self._get_selenium(self.start_url)
            if not html:
                logger.error(f"获取博客列表页失败: {self.start_url}")
                return []
            
            # 解析博客列表，获取文章链接
            article_links = self._parse_article_links(html)
            logger.info(f"解析到 {len(article_links)} 篇文章链接")
            
            # 爬取每篇文章
            for idx, (title, url) in enumerate(article_links, 1):
                logger.info(f"正在爬取第 {idx}/{len(article_links)} 篇文章: {title}")
                
                try:
                    # 获取文章内容
                    article_html = self._get_selenium(url)
                    if not article_html:
                        logger.warning(f"获取文章内容失败: {url}")
                        continue
                    
                    # 解析文章内容
                    article_content = self._parse_article_content(url, article_html)
                    
                    # 保存为Markdown
                    file_path = self.save_to_markdown(url, title, article_content)
                    saved_files.append(file_path)
                    logger.info(f"已保存文章: {title} -> {file_path}")
                    
                    # 间隔一段时间再爬取下一篇
                    if idx < len(article_links):
                        time.sleep(self.interval)
                    
                except Exception as e:
                    logger.error(f"爬取文章失败: {url} - {e}")
            
            return saved_files
        except Exception as e:
            logger.error(f"爬取AWS博客过程中发生错误: {e}")
            return saved_files
    
    def _parse_article_links(self, html: str) -> List[Tuple[str, str]]:
        """
        从博客列表页解析文章链接
        
        Args:
            html: 博客列表页HTML
            
        Returns:
            文章链接列表，每项为(标题, URL)元组
        """
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # AWS博客文章通常在具有特定类的div元素中
        # 更新选择器以匹配实际的AWS博客页面结构
        try:
            # 尝试多种可能的文章容器选择器
            article_containers = soup.select('.blog-post, .blog-card, .aws-card, .lb-card, article, .blog-media, .blog-entry, .aws-blog-post')
            
            if not article_containers:
                # 如果特定选择器没找到，尝试查找包含链接的所有div
                logger.warning("未找到指定文章容器，尝试使用通用选择器")
                # 找到所有可能是博客文章的链接
                links = soup.select('a[href*="/blogs/"]')
                
                for link in links:
                    if link.get('href') and '/blogs/' in link.get('href'):
                        title = link.get_text(strip=True)
                        if not title:
                            title = "AWS博客文章"  # 默认标题
                        url = urljoin(self.start_url, link['href'])
                        if url not in [x[1] for x in articles]:  # 避免重复
                            articles.append((title, url))
            else:
                # 处理找到的文章容器
                for container in article_containers:
                    # 尝试多种可能的标题和链接选择器
                    title_elem = (container.select_one('h1, h2, h3, h4, .lb-txt-bold, .blog-title, .aws-blog-title') or 
                                 container.select_one('a') or container)
                    
                    if title_elem:
                        # 获取标题
                        title = title_elem.get_text(strip=True)
                        
                        # 获取链接
                        link = title_elem.find('a') if title_elem.name != 'a' else title_elem
                        link = container.find('a') if not link else link
                        
                        if link and link.get('href') and '/blogs/' in link.get('href'):
                            url = urljoin(self.start_url, link['href'])
                            if url not in [x[1] for x in articles]:  # 避免重复
                                articles.append((title, url))
            
            logger.info(f"找到 {len(articles)} 篇潜在的博客文章链接")
        
        except Exception as e:
            logger.error(f"解析文章链接出错: {e}")
        
        # 判断是否为测试模式
        test_mode = self.source_config.get('test_mode', False)
        
        # 如果是测试模式，只爬取1篇文章
        if test_mode:
            logger.info("测试模式：仅爬取1篇文章")
            return articles[:1]
        
        # 否则根据配置的限制数量爬取
        limit = self.crawler_config.get('article_limit', 50)
        logger.info(f"爬取模式：限制爬取{limit}篇文章")
        return articles[:limit]
    
    def _parse_article_content(self, url: str, html: str) -> str:
        """
        解析文章内容
        
        Args:
            url: 文章URL
            html: 文章页面HTML
            
        Returns:
            Markdown内容
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # 1. 移除页头、页尾、侧边栏等非内容区域
        self._clean_non_content(soup)
        
        # 2. 尝试更精确地定位文章主体内容
        article = self._locate_article_content(soup, url)
        
        if not article:
            logger.warning(f"未找到文章主体: {url}")
            return ""
        
        # 3. 处理图片 - 使用原始URL而不是下载到本地
        for img in article.find_all('img'):
            if not img.get('src'):
                continue
            
            # 将相对URL转换为绝对URL
            img_url = urljoin(url, img['src'])
            img['src'] = img_url
        
        # 4. 提取正文内容并转换为Markdown
        article_md = self._html_to_markdown(article)
        
        return article_md
    
    def _clean_non_content(self, soup: BeautifulSoup) -> None:
        """
        移除页头、页尾、侧边栏等非内容区域
        
        Args:
            soup: BeautifulSoup对象
        """
        # 移除常见的页头元素
        for header in soup.select('header, .header, #header, .top-nav, .aws-header, .navigation, nav, .top-bar, .lb-header'):
            header.decompose()
        
        # 移除常见的页尾元素
        for footer in soup.select('footer, .footer, #footer, .aws-footer, .bottom-bar, .lb-footer'):
            footer.decompose()
        
        # 移除常见的侧边栏元素
        for sidebar in soup.select('.sidebar, #sidebar, .side-nav, .aws-sidebar, .column-right, .column-left, aside'):
            sidebar.decompose()
        
        # 移除常见的广告和推广元素
        for promo in soup.select('.ad, .ads, .advertisement, .promo, .promotion, .banner, .aws-promo, .aws-banner'):
            promo.decompose()
        
        # 移除导航元素
        for nav in soup.select('.breadcrumb, .breadcrumbs, .navigation, .nav, .menu'):
            nav.decompose()
        
        # 移除评论区
        for comments in soup.select('.comments, #comments, .comment-section, .disqus, .discourse'):
            comments.decompose()
        
        # 移除社交媒体分享按钮
        for social in soup.select('.share, .social, .social-media, .social-buttons, .aws-social'):
            social.decompose()
        
        # 移除相关文章推荐
        for related in soup.select('.related, .related-posts, .suggested, .aws-related, .recommended'):
            related.decompose()
        
        # 移除脚本、样式等无关元素
        for tag in soup.find_all(['script', 'style', 'noscript', 'iframe', 'svg']):
            tag.decompose()
    
    def _locate_article_content(self, soup: BeautifulSoup, url: str) -> Optional[BeautifulSoup]:
        """
        更精确地定位文章主体内容
        
        Args:
            soup: BeautifulSoup对象
            url: 文章URL
            
        Returns:
            包含文章主体内容的BeautifulSoup对象，或None
        """
        # 优先级从高到低尝试找到文章主体
        selectors = [
            # 最可能的文章内容选择器
            'article .lb-post-content',
            'article .lb-grid-content',
            '.blog-post-content',
            '.post-content',
            '.article-content',
            '.entry-content',
            '.post-body',
            '.content-body',
            
            # 次优先级选择器
            'main article',
            'main .content',
            'article',
            '.post',
            '#content .post',
            '.blog-content',
            '.lb-grid-container > div > div',  # AWS博客通常使用的容器结构
            
            # 最后的备选选择器
            'main',
            '#content',
            '.content',
            '.container'
        ]
        
        # 尝试所有选择器
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                # 找到内容最长的元素，这通常是正文
                main_element = max(elements, key=lambda x: len(str(x)))
                logger.debug(f"找到文章主体，使用选择器: {selector}")
                return main_element
        
        # 如果还是找不到，尝试一个启发式方法：寻找最长的<div>或<section>
        candidates = []
        for tag in soup.find_all(['div', 'section']):
            # 排除明显不是内容的元素
            if tag.has_attr('class') and any(c in str(tag['class']) for c in ['header', 'footer', 'sidebar', 'menu', 'nav']):
                continue
            
            # 排除太短的内容
            if len(str(tag)) < 1000:  # 文章通常至少有1000个字符
                continue
            
            # 判断是否包含文章特征(段落、标题等)
            if len(tag.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol'])) > 5:
                candidates.append(tag)
        
        if candidates:
            # 找到内容最长的候选元素
            main_element = max(candidates, key=lambda x: len(str(x)))
            logger.debug("使用启发式方法找到文章主体")
            return main_element
        
        # 最后的备选：返回<body>
        body = soup.find('body')
        if body:
            logger.warning(f"未找到具体文章主体，使用<body>: {url}")
            return body
        
        return None
    
    def _html_to_markdown(self, article: BeautifulSoup) -> str:
        """
        将HTML转换为Markdown，并进行额外的清理
        
        Args:
            article: 包含文章内容的BeautifulSoup对象
            
        Returns:
            清理后的Markdown内容
        """
        # 移除推广链接和无关元素
        for tag in article.find_all(['button', 'input', 'form']):
            tag.decompose()
        
        # 去掉空链接
        for a in article.find_all('a'):
            if not a.get_text(strip=True):
                a.replace_with_children()
        
        # 保留文章主体内容
        article_html = str(article)
        
        # 使用html2text转换为Markdown
        article_md = self.html_converter.handle(article_html)
        
        # 清理Markdown
        article_md = self._clean_markdown(article_md)
        
        return article_md
    
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
        
        # 去除可能的推广内容（通常在文章末尾）
        promo_patterns = [
            r'关注我们的.*?\n\n',
            r'想了解更多.*?\n\n',
            r'更多AWS.*?\n\n',
            r'follow us on.*?\n\n',
            r'learn more about.*?\n\n',
        ]
        
        for pattern in promo_patterns:
            markdown_text = re.sub(pattern, '\n\n', markdown_text, flags=re.IGNORECASE | re.DOTALL)
        
        # 修复可能被错误转换的链接
        markdown_text = re.sub(r'\]\(\/(?!http)', r'](https://aws.amazon.com/', markdown_text)
        
        # 美化标题格式，确保标题前后有空行
        markdown_text = re.sub(r'([^\n])(#{1,6} )', r'\1\n\n\2', markdown_text)
        markdown_text = re.sub(r'(#{1,6} .+)([^\n])\n', r'\1\2\n\n', markdown_text)
        
        # 美化列表，确保列表项前后有适当的空间
        markdown_text = re.sub(r'\n\n([\*\-\+] )', r'\n\1', markdown_text)
        markdown_text = re.sub(r'([\*\-\+] .+)\n([^\*\-\+\n])', r'\1\n\n\2', markdown_text)
        
        # 美化引用块
        markdown_text = re.sub(r'\n\n(> )', r'\n\1', markdown_text)
        markdown_text = re.sub(r'(>.+)\n([^>\n])', r'\1\n\n\2', markdown_text)
        
        # 美化代码块
        markdown_text = re.sub(r'```([^`]+)```', r'\n\n```\1```\n\n', markdown_text)
        
        # 美化图片格式，确保图片前后有空行
        markdown_text = re.sub(r'([^\n])!\[', r'\1\n\n![', markdown_text)
        markdown_text = re.sub(r'\.(?:jpg|jpeg|png|gif|webp|svg)\)([^\n])', r'.jpg)\n\n\1', markdown_text)
        
        return markdown_text
    
    def _create_filename(self, title: str, ext: str) -> str:
        """
        根据标题创建合法的文件名
        
        Args:
            title: 文章标题
            ext: 文件扩展名（如.md）
            
        Returns:
            合法的文件名
        """
        # 移除非法字符
        filename = re.sub(r'[\\/:*?"<>|]', '', title)
        # 将空格替换为下划线
        filename = filename.replace(' ', '_')
        # 限制长度
        if len(filename) > 100:
            filename = filename[:100]
        # 添加扩展名
        return filename + ext
    
    def save_to_markdown(self, url: str, title: str, content: str) -> str:
        """
        保存内容为Markdown文件
        
        Args:
            url: 文章URL
            title: 文章标题
            content: 文章内容
            
        Returns:
            保存的文件路径
        """
        # 创建用于存储的文件名（从标题生成）
        filename = self._create_filename(title, ".md")
        filepath = os.path.join(self.output_dir, filename)
        
        # 构建Markdown内容
        metadata = [
            f"# {title}",
            "",
            f"原始链接: {url}",
            "",
            f"爬取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"厂商: {self.vendor}",
            "",
            f"类型: {self.source_type}",
            "",
            "---",
            "",
        ]
        
        # 组合最终内容
        final_content = "\n".join(metadata) + content
        
        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_content)
            
        return filepath 