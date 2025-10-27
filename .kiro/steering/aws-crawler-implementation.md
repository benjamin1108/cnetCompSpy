---
inclusion: manual
---
# AWS爬虫实现

## AWS爬虫模块结构

AWS爬虫模块包含多个专门爬虫类，各负责不同的数据来源：

- [crawlers/vendors/aws/blog_crawler.py](mdc:src/crawlers/vendors/aws/blog_crawler.py) - AWS博客爬虫
- [crawlers/vendors/aws/whatsnew_crawler.py](mdc:src/crawlers/vendors/aws/whatsnew_crawler.py) - AWS新功能公告爬虫

## 功能实现

### 博客爬虫 (BlogCrawler)

AWS博客爬虫主要从AWS官方博客网站抓取文章：

```python
# BlogCrawler的核心方法
def crawl(self):
    # 1. 获取博客文章列表页
    blog_list_urls = self._get_blog_list_urls()
    
    # 2. 解析列表页获取文章URL
    article_urls = []
    for list_url in blog_list_urls:
        page_urls = self._parse_blog_list(list_url)
        article_urls.extend(page_urls)
    
    # 3. 过滤已爬取的文章
    new_urls = self._filter_existing_articles(article_urls)
    
    # 4. 使用线程池并行爬取新文章
    if new_urls:
        self._crawl_articles_with_threadpool(new_urls)
```

### 新功能公告爬虫 (WhatsNewCrawler)

AWS新功能公告爬虫通过API获取最新公告：

```python
# WhatsNewCrawler的核心方法
def crawl(self):
    # 1. 获取公告列表页
    announcements_url = self._get_whatsnew_url()
    
    # 2. 获取API数据并解析公告列表
    announcement_data = self._fetch_api_data()
    announcement_urls = self._parse_announcements(announcement_data)
    
    # 3. 过滤已爬取的公告
    new_urls = self._filter_existing_announcements(announcement_urls)
    
    # 4. 使用线程池并行爬取新公告
    if new_urls:
        self._crawl_announcements_with_threadpool(new_urls)
```

## 关键技术细节

1. **数据解析**：

   AWS公告页面通常使用JavaScript动态加载内容，爬虫使用两种方式获取数据：
   - 直接请求HTML页面并解析DOM
   - 调用背后的API获取JSON数据

2. **元数据管理**：

   ```python
   def _filter_existing_articles(self, urls):
       """过滤已存在的文章URL"""
       new_urls = []
       for url in urls:
           # 计算URL的唯一标识
           url_id = self._get_url_id(url)
           
           # 检查是否已爬取过
           if not self.metadata_manager.is_url_crawled(url, url_id):
               new_urls.append(url)
           else:
               # 已存在则跳过
               logger.info(f"跳过已存在的文章: {url}")
       
       return new_urls
   ```

3. **线程池使用**：

   ```python
   def _crawl_articles_with_threadpool(self, urls):
       """使用线程池并行爬取文章"""
       # 创建线程池
       thread_pool = get_thread_pool(
           initial_threads=2,
           max_threads=10,
           api_rate_limit=60  # 每分钟最多60个请求
       )
       
       # 添加爬取任务
       for url in urls:
           thread_pool.add_task(self._crawl_single_article, url)
       
       # 等待所有任务完成
       thread_pool.wait_for_completion()
   ```

## 常见问题与解决方案

1. **线程池关闭问题**：

   当WhatsNewCrawler使用线程池爬取多个公告并行时，可能在`wait_for_completion()`处卡住：
   
   ```python
   # 问题代码
   def _crawl_announcements_with_threadpool(self, urls):
       thread_pool = get_thread_pool(...)
       for url in urls:
           thread_pool.add_task(self._crawl_single_announcement, url)
       # 这里可能卡住
       thread_pool.wait_for_completion()
   ```
   
   解决方案是确保：
   - 单个爬取任务不会无限阻塞
   - 线程池有合理的超时设置
   - 爬取任务中的异常被正确捕获并记录

2. **增量爬取逻辑**：

   确保元数据记录的更新是线程安全的，特别是多个爬虫并行运行时：
   
   ```python
   # 线程安全的元数据更新
   with self.metadata_lock:
       self.metadata_manager.add_or_update_entry(url, url_id, metadata)
   ```
