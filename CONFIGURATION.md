# 云计算网络竞争情报系统 - 配置指南

本文档详细说明了云计算网络竞争情报系统的配置方法，包括各个模块的配置选项和示例。

## 目录

1. [配置文件加载机制](#配置文件加载机制)
2. [配置文件格式](#配置文件格式)
3. [模块化配置](#模块化配置)
4. [通知配置](#通知配置)
5. [爬虫配置](#爬虫配置)
6. [数据源配置](#数据源配置)
7. [AI分析配置](#ai分析配置)
8. [日志配置](#日志配置)
9. [Web服务器配置](#web服务器配置)
10. [调度器配置](#调度器配置)
11. [环境变量](#环境变量)
12. [配置文件示例](#配置文件示例)

## 配置文件加载机制

系统按以下优先级加载配置：

1. 命令行参数指定的配置文件或目录 (`--config path/to/your/config`)
2. 项目根目录下的 `config/` 目录 (如果存在且包含 `main.yaml` 或其他 `.yaml` 文件)
3. 项目根目录下的 `config.secret.yaml` (如果存在，建议用于存放敏感信息)
4. 项目根目录下的 `config.yaml` (如果存在)
5. 默认配置 (硬编码在代码中的配置)

## 配置文件格式

系统使用YAML格式的配置文件，支持以下特性：

- 按模块组织配置项
- 注释（以`#`开头）
- 支持字符串、数字、布尔值、列表和嵌套对象等多种数据类型

## 模块化配置

除了使用单一的配置文件外，系统还支持将配置拆分到多个文件中，放在`config/`目录下：

- `config/main.yaml`: 主配置文件，可以通过`imports`字段导入其他配置文件
- `config/crawler.yaml`: 爬虫相关配置
- `config/ai_analyzer.yaml`: AI分析相关配置
- `config/notification.yaml`: 通知相关配置
- `config/logging.yaml`: 日志相关配置
- `config/webserver.yaml`: Web服务器相关配置
- `config/scheduler.yaml`: 调度器相关配置
- `config/sources.yaml`: 数据源相关配置

示例 `config/main.yaml`:

```yaml
# 主配置文件
imports:
  - crawler.yaml
  - ai_analyzer.yaml
  - notification.yaml
  - logging.yaml
  - webserver.yaml
  - scheduler.yaml
  - sources.yaml

# 主配置文件中的配置项会覆盖导入的配置文件中的同名配置项
```

## 通知配置

通知配置位于`notification`部分，支持邮件和钉钉两种通知方式。

### 邮件通知

```yaml
notification:
  email:
    enabled: true                      # 是否启用邮件通知功能
    smtp_server: "smtp.example.com"    # SMTP 服务器地址
    smtp_port: 587                     # SMTP 端口
    use_tls: true                      # 是否启用 TLS 加密
    use_ssl: false                     # 是否启用 SSL 加密
    username: "your_username"          # SMTP 用户名
    password: "your_password"          # SMTP 密码
    sender: "your_email@example.com"   # 发件人邮箱地址
    recipients:                        # 收件人邮箱列表
      - "user1@example.com"
      - "user2@example.com"
    subject_prefix: "[竞争情报]"       # 邮件主题前缀
```

### 钉钉通知

```yaml
notification:
  dingtalk:
    enabled: true                      # 是否启用钉钉机器人通知功能
    keyword: "竞争情报"                # 钉钉机器人安全设置的自定义关键词
    webhook: "https://oapi.dingtalk.com/robot/send?access_token=xxx" # 钉钉机器人的 Webhook URL
    secret: "SECxxx"                   # 钉钉机器人加签密钥
    weekly_push_time: "10:00"          # 每周定时推送时间 (HH:MM, 24小时制)
    weekly_push_day: 5                 # 每周几推送 (1=周一, ..., 7=周日)
```

## 爬虫配置

爬虫配置位于`crawler`部分，主要控制爬虫的行为。

```yaml
crawler:
  timeout: 30                         # 全局请求超时时间 (秒)
  retry: 3                            # 请求失败时的重试次数
  interval: 2                         # 两次请求之间的基本间隔时间 (秒)
  article_limit: 50                   # 每个数据源默认最多爬取的文章数量
  max_workers: 10                     # 全局爬虫并发工作线程数
  page_load_timeout: 45               # 浏览器页面加载超时时间 (秒)
  script_timeout: 30                  # 浏览器执行 JavaScript 脚本的超时时间 (秒)
  implicit_wait: 10                   # 浏览器查找元素的隐式等待时间 (秒)
  default_element_timeout: 15         # 显式等待时，等待元素出现的默认超时时间 (秒)
  long_element_timeout: 25            # 显式等待时，等待某些加载较慢元素的超时时间 (秒)
  screenshot_debug: false             # 是否在发生错误或特定步骤时保存页面截图用于调试
  user_agent: "Mozilla/5.0 ..."       # 默认 User-Agent
```

## 数据源配置

数据源配置位于`sources`部分，定义了各个爬取目标。每个云厂商可以有多个来源类型。

```yaml
sources:
  aws:                                # 厂商名称
    blog:                             # 来源类型
      name: "AWS Blog - Networking"   # 人类可读名称
      enabled: true                   # 是否启用
      url: "https://aws.amazon.com/blogs/networking-and-content-delivery/"  # 目标URL
      type: "blog"                    # 对应爬虫类型
      test_mode: false                # 是否处于测试模式
      article_limit: 20               # 可覆盖全局 article_limit
    whatsnew:
      # ... 其他数据源配置
      
  azure:
    # ... 其他厂商配置
```

支持的来源类型:
- `blog`: 博客文章
- `whatsnew`: 产品更新
- `tech-blog`: 技术博客
- `updates`: 技术更新
- 其他由特定厂商爬虫实现的类型

## AI分析配置

AI分析配置位于`ai_analyzer`部分，控制AI模型的行为和分析流程。

```yaml
ai_analyzer:
  # API Keys (建议放在 config.secret.yaml 中)
  dashscope_api_key: "YOUR_ALIYUN_DASHSCOPE_API_KEY"
  openai_api_key: "YOUR_OPENAI_API_KEY"

  active_model_profile: "qwen"            # 默认使用的模型配置

  model_profiles:
    # 通义千问 (Qwen) 模型配置
    qwen:
      type: "openai_compatible"           # 使用 OpenAI 兼容接口
      config:
        model: "qwen-max"                 # 模型名称
        max_tokens: 8000                  # 最大输出 token 数
        temperature: 0.5                  # 生成文本的随机性
    
    # OpenAI GPT 模型配置
    gpt:
      type: "openai"
      config:
        model: "gpt-4o"
        max_tokens: 4000
        temperature: 0.7

  # 分析pipeline配置
  pipeline:
    summary:
      enabled: true
      max_length: 500                     # 摘要最大长度
    keywords:
      enabled: true
      max_count: 10                       # 最大关键词数量
    sentiment:
      enabled: true                       # 是否进行情感分析
    categories:
      enabled: true                       # 是否进行分类
      taxonomy:                           # 分类体系
        - "网络"
        - "CDN"
        - "安全"
        - "DNS"
        - "负载均衡"
        - "VPC"
        - "边缘计算"
```

## 日志配置

日志配置位于`logging`部分，使用Python标准库的`logging.config.dictConfig`格式。

```yaml
logging:
  version: 1
  disable_existing_loggers: false
  formatters:
    standard:
      format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
      datefmt: "%Y-%m-%d %H:%M:%S"
    colored:
      (): src.utils.colored_logger.ColoredFormatter
      format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
      datefmt: "%Y-%m-%d %H:%M:%S"
  handlers:
    console:
      class: logging.StreamHandler
      level: INFO
      formatter: colored
      stream: ext://sys.stdout
    file:
      class: logging.handlers.RotatingFileHandler
      level: DEBUG
      formatter: standard
      filename: logs/app.log
      maxBytes: 10485760                  # 10MB
      backupCount: 10
      encoding: utf8
  loggers:
    # 第三方库日志级别
    urllib3:
      level: WARNING
    selenium:
      level: WARNING
    filelock:
      level: WARNING
  root:
    level: INFO
    handlers: [console, file]
    propagate: true
```

## Web服务器配置

Web服务器配置位于`webserver`部分，控制内置Web服务器的行为。

```yaml
webserver:
  host: "0.0.0.0"                     # 监听地址，0.0.0.0表示所有网络接口
  port: 5000                          # 监听端口
  debug: false                        # 是否启用调试模式
  secret_key: "your_secret_key"       # Flask secret_key
  session_lifetime: 1800              # 会话生存时间(秒)
  
  # 管理员账户配置
  admin:
    username: "admin"
    password: "your_password"         # 建议使用强密码
  
  # 静态文件配置
  static:
    cache_timeout: 3600               # 静态文件缓存时间(秒)
```

## 调度器配置

调度器配置位于`scheduler`部分，控制自动任务的调度。

```yaml
scheduler:
  crawl_interval: 86400               # 爬虫任务调度间隔(秒)，默认每天运行一次
  analyze_interval: 3600              # 分析任务调度间隔(秒)，默认每小时运行一次
  push_interval: 604800               # 推送任务调度间隔(秒)，默认每周运行一次
  
  # 定时任务配置 (cron格式)
  crawl_schedule: "0 2 * * *"         # 每天凌晨2点运行爬虫
  analyze_schedule: "0 */3 * * *"     # 每3小时运行分析
  push_schedule: "0 10 * * 5"         # 每周五上午10点推送报告
```

## 环境变量

系统也支持通过环境变量来设置一些敏感配置项，这些环境变量会覆盖配置文件中的同名配置项。主要支持的环境变量包括：

- `OPENAI_API_KEY`: OpenAI API密钥
- `DASHSCOPE_API_KEY`: 阿里云灵积DashScope API密钥
- `DINGTALK_WEBHOOK`: 钉钉机器人Webhook URL
- `DINGTALK_SECRET`: 钉钉机器人加签密钥
- `SMTP_USERNAME`: SMTP用户名
- `SMTP_PASSWORD`: SMTP密码
- `FLASK_SECRET_KEY`: Flask secret key

## 配置文件示例

完整的配置文件示例可以参考项目根目录下的`config.example.yaml`文件或`config.template.yaml`文件。

建议将包含敏感信息的配置项（如API密钥、密码等）放在`config.secret.yaml`文件中，该文件已被`.gitignore`忽略，不会提交到版本库。 