# 云计算网络竞争动态分析工具

## 项目介绍
该项目是一个基于Python的云计算网络竞争动态分析工具。该工具可以从配置文件中指定的URL爬取各大云厂商（如AWS、Azure、GCP、腾讯云、华为云、火山云等）的博客、文档等内容，通过AI进行分析。

## 功能特点
- **多源爬虫**：支持从多个云厂商的不同信息源（博客、文档等）爬取内容
- **智能分析**：利用AI技术对爬取的内容进行翻译、摘要等分析
- **格式友好**：保存为MD格式，保持原始文档的结构和风格
- **自动化管理**：自动管理webdriver，无需用户手动下载
- **模块化设计**：爬虫和分析可以分离运行，提高灵活性
- **灵活配置**：可通过命令行参数和配置文件灵活控制爬取数量和测试模式

## 项目结构
```
cloud-comp-spy/
├── data/               # 数据存储目录
│   ├── raw/            # 原始爬取数据
│   └── analysis/       # 分析结果
├── scripts/            # 脚本文件
│   └── setup_webdriver.sh  # WebDriver管理脚本
├── src/                # 源代码
│   ├── crawlers/       # 爬虫模块
│   │   ├── common/     # 通用爬虫组件
│   │   └── vendors/    # 厂商特定爬虫
│   └── ai_analyzer/    # AI分析模块
├── tests/              # 测试文件
├── requirements.txt    # 项目依赖
├── setup.py            # 安装脚本（仅开发用途）
└── README.md           # 项目说明
```

## 安装使用
1. 克隆仓库
   ```
   git clone https://github.com/yourusername/cloud-comp-spy.git
   cd cloud-comp-spy
   ```

2. 设置虚拟环境
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或者
   venv\Scripts\activate  # Windows
   ```

3. 安装依赖
   ```
   pip install -r requirements.txt
   ```

4. 设置WebDriver
   ```
   bash scripts/setup_webdriver.sh
   ```

5. 运行程序

   a. 运行爬虫、分析
   ```
   # 爬取数据
   python -m src.main --mode crawl
   
   # 分析数据
   python -m src.main --mode analyze
   
   # 测试模式：清理所有数据并依次执行爬虫和分析(每个来源只爬取1篇文章)
   python -m src.main --mode test
   
   # 仅清理所有数据目录
   python -m src.main --clean
   ```

   b. 其他运行选项
   ```
   # 指定配置文件
   python -m src.main --mode analyze --config custom_config.yaml
   
   # 仅爬取指定厂商的数据
   python -m src.main --mode crawl --vendor aws
   
   # 限制每个来源爬取的文章数量(例如每个来源只爬取5篇)
   python -m src.main --mode crawl --limit 5
   
   # 指定厂商并限制爬取数量
   python -m src.main --mode crawl --vendor aws --limit 10
   
   # 使用测试模式并指定厂商
   python -m src.main --mode test --vendor aws
   ```

   c. 命令行参数完整说明
   ```
   选项:
     --mode {crawl,analyze,test}  运行模式: crawl(爬取数据), analyze(分析数据), test(测试模式)
     --vendor VENDOR            爬取指定厂商的数据, 如aws, azure等，仅在crawl模式下有效
     --clean                    清理所有中间文件
     --limit LIMIT              爬取的文章数量限制，如设置为5则每个来源只爬取5篇，0表示使用配置文件中的默认值
     --config CONFIG            指定配置文件路径(默认为根目录下的config.yaml)
     -h, --help                 显示帮助信息
   ```

   d. 常用参数组合示例
   ```
   # 基本使用 - 完整流程
   python -m src.main --mode test                     # 测试模式：清理并执行爬取+分析(每个源仅1篇)
   python -m src.main --mode crawl                    # 正常爬取(使用配置文件中的默认限制)
   python -m src.main --mode analyze                  # 分析已爬取的内容
   
   # 爬取控制
   python -m src.main --mode crawl --vendor aws       # 只爬取AWS
   python -m src.main --mode crawl --limit 20         # 每个来源爬取20篇
   python -m src.main --mode crawl --vendor aws --limit 5  # 只爬取AWS且限制5篇
   
   # 配置和清理
   python -m src.main --config production.yaml --mode crawl  # 使用自定义配置文件
   python -m src.main --clean                         # 清理所有数据目录
   python -m src.main --clean --mode crawl            # 清理后立即开始爬取
   
   # 测试组合
   python -m src.main --mode test --vendor aws        # 测试模式仅处理AWS数据
   ```

## 配置说明
在`config.yaml`文件中配置爬取源和分析参数：
```yaml
sources:
  aws:
    blog:
      url: https://aws.amazon.com/blogs/
      test_mode: false  # 测试模式开关，true时只爬取1篇文章
    docs: 
      url: https://docs.aws.amazon.com/
  azure:
    blog: 
      url: https://azure.microsoft.com/en-us/blog/
    # 更多配置...

# 爬虫配置  
crawler:
  article_limit: 50     # 每个来源最多爬取的文章数量(命令行--limit参数会覆盖此设置)
  max_workers: 4        # 并发爬虫数量
  timeout: 30           # 请求超时时间(秒)
  retry: 3              # 请求失败重试次数
  interval: 2           # 请求间隔时间(秒)
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"  # 自定义User-Agent
  
# AI分析配置
ai_analyzer:
  model: "qwen-max"                  # 使用的AI模型
  max_tokens: 4000                   # 最大令牌数
  temperature: 0.8                   # 温度参数
  api_key: ""                        # API密钥（请填写您的API密钥）
  api_base: ""                       # API基础URL（请填写您使用的模型提供商的API端点）
  system_prompt: "你是一个专业的云计算技术分析师..." # 系统提示词
  tasks:
    - type: "summary"
      prompt: "请对此云服务商的内容进行总结..."
    # 更多任务...
```

### 爬虫配置
爬虫支持两种模式：
1. **正常模式**：按照配置文件中的`article_limit`设置或命令行`--limit`参数爬取指定数量的文章
2. **测试模式**：通过配置文件中的`test_mode: true`或使用`--mode test`命令启用，每个来源只爬取1篇文章

命令行参数的优先级高于配置文件：
- `--limit` 参数会覆盖配置文件中的 `article_limit` 设置
- `--mode test` 会将所有来源的 `test_mode` 设置为 `true`

### 厂商爬虫配置示例

#### 完整配置示例
```yaml
sources:
  # AWS配置
  aws:
    # AWS博客
    blog:
      url: https://aws.amazon.com/blogs/
      test_mode: false  # 测试模式开关
      specific_categories:  # 可选，特定博客类别
        - networking-content-delivery
        - architecture
      exclude_categories:  # 可选，排除的博客类别
        - gametech
    # AWS文档
    docs:
      url: https://docs.aws.amazon.com/
      specific_services:  # 可选，特定服务文档
        - vpc
        - route53
  
  # Azure配置
  azure:
    blog:
      url: https://azure.microsoft.com/en-us/blog/
      test_mode: false
      specific_tags:  # 可选，特定标签
        - networking
        - security
    
  # 谷歌云配置
  google_cloud:
    blog:
      url: https://cloud.google.com/blog/
      categories:  # 可选，特定分类
        - networking
        - security
      
  # 阿里云配置
  aliyun:
    blog:
      url: https://www.alibabacloud.com/blog/
      test_mode: false
```

#### 高级爬虫配置
```yaml
crawler:
  # 基础设置
  article_limit: 50      # 每个来源最多爬取的文章数量
  max_workers: 4         # 并发爬虫数量
  
  # 网络请求设置
  timeout: 30            # 请求超时时间(秒)
  retry: 3               # 请求失败重试次数
  interval: 2            # 请求间隔时间(秒)
  
  # 浏览器设置
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  headers:               # 自定义请求头
    Accept-Language: "en-US,en;q=0.9"
    DNT: "1"
  
  # Selenium设置
  selenium:
    headless: true       # 无头模式(不显示浏览器窗口)
    wait_time: 10        # 等待元素加载的时间(秒)
    window_size:         # 浏览器窗口大小
      width: 1920
      height: 1080
    
  # 代理设置(可选)
  proxy:
    enabled: false
    http: "http://proxy.example.com:8080"
    https: "https://proxy.example.com:8080"
    
  # 过滤设置
  filters:
    min_content_length: 1000  # 最小内容长度(字符数)
    date_range:               # 日期范围
      start: "2023-01-01"
      end: "2023-12-31"
    keywords:                 # 关键词过滤(包含这些关键词的文章才会被保存)
      - "网络"
      - "安全"
      - "架构"
```

### AI分析器配置
AI分析器支持多种不同的大语言模型提供商，包括OpenAI、阿里云通义千问、Azure OpenAI、百度文心一言和讯飞星火等。

1. **基础配置**:
   - `model`: 要使用的模型名称，根据您选择的提供商而定
   - `max_tokens`: 生成的最大token数量
   - `temperature`: 生成文本的创造性/随机性，0.0-1.0之间
   
2. **API配置**:
   - `api_key`: 您的API密钥，需要从模型提供商处获取
   - `api_base`: API的基础URL，根据您使用的模型提供商而定
   
3. **提示词配置**:
   - `system_prompt`: 系统级提示词，定义AI助手的角色和行为
   - `tasks`: 分析任务列表，每个任务包含类型和提示词

查看 [model_configuration.md](docs/model_configuration.md) 获取不同模型提供商的详细配置示例。

如果未提供API密钥或API基础URL，系统将自动使用模拟模式，返回预设的响应而不是实际调用AI模型。

### 不同大模型提供商的配置示例

#### OpenAI
```yaml
ai_analyzer:
  model: "gpt-4"
  max_tokens: 4000
  temperature: 0.7
  api_key: "sk-..."  # OpenAI API密钥
  api_base: "https://api.openai.com/v1"  # OpenAI API端点
```

#### 阿里云通义千问
```yaml
ai_analyzer:
  model: "qwen-max"  # 或 qwen-plus、qwen-turbo
  max_tokens: 4000
  temperature: 0.7
  api_key: "your-api-key"  # 阿里云API密钥
  api_base: "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
```

#### Azure OpenAI
```yaml
ai_analyzer:
  model: "gpt-4"
  max_tokens: 4000
  temperature: 0.7
  api_key: "your-api-key"  # Azure API密钥
  api_base: "https://your-resource-name.openai.azure.com/openai/deployments/your-deployment-name"
  api_version: "2023-05-15"  # Azure API版本
```

#### 百度文心一言
```yaml
ai_analyzer:
  model: "ernie-bot-4"  # 或 ernie-bot、ernie-bot-turbo
  max_tokens: 4000
  temperature: 0.7
  api_key: "your-api-key"  # 百度API密钥
  api_secret: "your-api-secret"  # 百度API秘钥
  api_base: "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat"
```

### 测试AI分析器
您可以使用测试脚本来测试AI分析器的功能：
```bash
# 使用配置文件中的设置运行
python test_ai.py -c config.yaml

# 使用模拟模式运行（无需API密钥）
python test_ai.py -c config.yaml --mock
```

确保在使用实际API调用时，在`config.yaml`中设置了有效的API密钥和API基础URL。

### 分析流程
1. 爬虫爬取云厂商的博客和文档内容，保存为Markdown格式
2. AI分析器读取这些内容，使用配置的AI模型进行分析
3. 分析结果保存为Markdown和JSON格式，便于查看和进一步处理

## 输出格式与目录结构

### 原始爬取数据
爬虫爬取的原始数据保存在`data/raw/{vendor}/{source_type}/`目录中，例如：
```
data/raw/
  ├── aws/
  │   ├── blog/
  │   │   ├── AWS_introduces_Storage_Lens_default_dashboard_settings.md
  │   │   └── Exploring_Data_Transfer_Costs_for_AWS_Network_Load_Balancers.md
  │   └── docs/
  │       └── ...
  ├── azure/
  │   └── blog/
  │       └── ...
  └── ...
```

### 分析结果
AI分析结果保存在`data/analysis/{vendor}/{source_type}/`目录中，例如：
```
data/analysis/
  ├── aws/
  │   ├── blog/
  │   │   ├── AWS_introduces_Storage_Lens_default_dashboard_settings.md
  │   │   └── Exploring_Data_Transfer_Costs_for_AWS_Network_Load_Balancers.md
  │   └── docs/
  │       └── ...
  ├── azure/
  │   └── blog/
  │       └── ...
  └── ...
```

### 分析文件格式
分析后的Markdown文件结构如下：
```markdown
---
title: 文章标题
original_link: 原始文章链接
vendor: 云厂商名称
type: 文章类型(blog/docs)
date: 发布日期
crawl_date: 爬取时间
---

## 摘要
AI生成的摘要内容，提炼出文章的主要观点和结论。

## 翻译
完整的中文翻译内容，保留原文的段落结构、列表和格式等。

## 分析
AI生成的技术分析和竞争情报，包括：
- 技术要点分析
- 相关背景信息
- 市场影响评估
- 同类产品对比
- 应用场景建议
```

## 常见问题解答(FAQ)

### 1. 安装问题
**Q: 安装时找不到chrome-headless-shell**
A: 执行`bash scripts/setup_webdriver.sh`重新安装WebDriver，或手动下载Chrome浏览器

**Q: 依赖安装出错**
A: 确保您的Python版本是3.8或更高版本，并且已安装pip的最新版本

### 2. 爬虫问题
**Q: 爬虫无法获取某些网站内容**
A: 有些网站可能有反爬虫措施。尝试以下解决方案：
- 调整`interval`参数增加请求间隔时间
- 修改`user_agent`和自定义`headers`
- 启用代理配置

**Q: 如何只爬取特定类别的内容？**
A: 在配置文件中设置`specific_categories`或`specific_tags`参数，详见"厂商爬虫配置示例"

### 3. AI分析问题
**Q: AI分析没有生成结果**
A: 检查以下几点：
- 确认API密钥和API基础URL是否正确设置
- 检查网络连接是否正常
- 查看日志文件中是否有更详细的错误信息

**Q: 如何优化AI分析质量？**
A: 可以调整以下参数：
- 修改`system_prompt`以更精确地定义AI助手的角色
- 调整`temperature`参数（较低的值会使输出更确定性，较高的值会增加随机性）
- 自定义`tasks`中的具体提示词

### 4. 性能与优化
**Q: 爬虫运行很慢**
A: 可以尝试以下优化：
- 增加`max_workers`参数以提高并发爬取能力
- 减少`wait_time`参数以缩短页面加载等待时间
- 使用特定参数限制爬取范围，如`specific_categories`

**Q: 如何减少API调用次数？**
A: 可以使用以下策略：
- 设置合理的`article_limit`以限制处理的文章数量
- 使用`filters`过滤掉不相关的内容
- 先使用`--mode test`进行小规模测试

## 安全性说明

### API密钥安全

项目中的`config.yaml`文件包含API密钥等敏感信息，不应该直接提交到版本控制系统。请遵循以下安全最佳实践：

1. **第一次设置**：
   ```bash
   # 复制模板配置文件
   cp config.examples/config.template.yaml config.yaml
   
   # 编辑配置文件，添加您的API密钥
   nano config.yaml
   ```

2. **保护API密钥**：
   - 不要在公共场所共享配置文件
   - 不要将包含真实API密钥的配置文件提交到公共代码库
   - 考虑使用环境变量替代配置文件中的敏感信息

3. **如果需要共享配置**：
   - 始终使用占位符替换真实API密钥: `api_key: "YOUR_API_KEY"`
   - 使用私有通道分享实际密钥

4. **密钥轮换**：
   - 定期更换API密钥
   - 如果怀疑密钥泄露，立即进行轮换

`.gitignore`文件已配置为排除`config.yaml`，以防止意外提交。

## 许可证
MIT