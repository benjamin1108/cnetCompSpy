# 云计算网络竞争动态分析工具

## 项目介绍
该项目是一个基于Python的云计算网络竞争动态分析工具。该工具可以从配置文件中指定的URL爬取各大云厂商（如AWS、Azure、GCP、腾讯云、华为云、火山云等）的博客、文档等内容，通过AI进行分析。

## 最近更新
- **2025-04-19**: 脚本系统重构
  - 重构脚本系统，解决虚拟环境激活问题
  - 创建统一的run.sh入口脚本，负责环境激活和命令分发
  - 将WebDriver管理和环境管理功能移至专用Python模块
  - 添加tabulate依赖，支持表格化显示统计信息
  - 优化脚本结构，减少多层bash调用
  - 更新文档，反映新的脚本系统结构

- **2025-04-18 (2)**: 分析模块功能增强
  - 为analyze模块增加metadata功能，实现智能防重复分析
  - 给分析模块运行脚本增加vendor参数选项，支持只分析特定厂商数据
  - 增加指定文件的分析参数，支持只分析特定文件
  - 优化AI模型输出处理，自动清理额外文本，提高分析结果质量

- **2025-04-18 (1)**: 代码优化，移除冗余代码，提高代码复用性
  - 将HTML到Markdown的转换、日期解析和文件保存功能抽象到BaseCrawler类中
  - 移除各爬虫实现中的重复代码
  - 清理未使用的测试目录
  - 整合所有Shell脚本为一个统一的run.sh脚本，提供更友好的命令行界面

## 功能特点
- **多源爬虫**：支持从多个云厂商的不同信息源（博客、文档等）爬取内容
- **智能分析**：利用AI技术对爬取的内容进行翻译、摘要和竞争分析
- **竞争情报**：通过AI分析生成竞争对手产品和战略的深度洞察
- **格式友好**：保存为MD格式，保持原始文档的结构和风格
- **自动化管理**：自动管理webdriver，无需用户手动下载
- **模块化设计**：爬虫和分析可以分离运行，提高灵活性
- **灵活配置**：可通过命令行参数和配置文件灵活控制爬取数量和测试模式
- **统一文件格式**：使用统一的文件命名和元数据格式，便于管理和查询
- **智能防重复**：使用metadata记录分析状态，避免重复分析已处理的文件
- **精细控制**：支持按厂商或特定文件进行分析，提高工作效率

## 项目结构
```
cloud-comp-spy/
├── data/               # 数据存储目录
│   ├── raw/            # 原始爬取数据
│   └── analysis/       # 分析结果
├── logs/               # 日志文件目录
├── scripts/            # 脚本文件
│   ├── compare_stats.py  # 统计比较脚本
│   ├── daily_crawl_and_analyze.sh  # 每日自动爬取与分析脚本
│   ├── daily_crawl_and_analyze_README.md  # 每日脚本使用说明
│   └── backup/         # 备份的旧脚本
├── src/                # 源代码
│   ├── crawlers/       # 爬虫模块
│   │   ├── common/     # 通用爬虫组件
│   │   └── vendors/    # 厂商特定爬虫
│   ├── ai_analyzer/    # AI分析模块
│   ├── utils/          # 工具类
│   │   ├── driver_manager.py  # WebDriver管理模块
│   │   ├── environment_manager.py  # 环境管理模块
│   │   └── ...         # 其他工具类
│   └── web_server/     # Web服务器模块
├── requirements.txt    # 项目依赖
├── setup.py            # 安装脚本（仅开发用途）
├── config.yaml         # 基本配置文件（不包含敏感信息）
├── config.secret.yaml  # 敏感配置文件（包含API密钥等）
├── run.sh              # 主运行脚本（统一入口）
└── README.md           # 项目说明
```

## 系统要求

### Python版本
- **推荐版本**: Python 3.10
- **最低支持版本**: Python 3.8
- **最高测试版本**: Python 3.11

### 操作系统
- **Linux**: Ubuntu 20.04+, CentOS 7+
- **Windows**: Windows 10, Windows 11
- **macOS**: macOS 10.15 (Catalina)及以上版本

### 环境管理
- **必需**: Miniforge（用于创建和管理虚拟环境）
  - 系统会自动检测是否安装，并在需要时提供安装指导
  - macOS安装方法：`curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh`（M1/M2 Mac使用arm64版本），然后`bash Miniforge3-MacOSX-x86_64.sh`
  - Linux安装方法：`wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh`，然后`bash Miniforge3-Linux-x86_64.sh`
  - Windows安装方法：下载并运行[Miniforge3-Windows-x86_64.exe](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe)

### 其他要求
- **内存**: 最低2GB RAM，建议4GB及以上
- **存储**: 最低1GB可用空间，根据爬取数据量可能需要更多
- **网络**: 需要稳定的互联网连接
- **浏览器**: Chrome/Chromium 114.0 或更高版本（用于驱动爬虫）

## 安装使用
1. 克隆仓库
   ```
   git clone https://github.com/yourusername/cloud-comp-spy.git
   cd cloud-comp-spy
   ```

2. 安装Miniforge（如果尚未安装）
   
   脚本会自动检测是否安装了Miniforge，如果未安装，会提供详细的安装指南。
   
   **macOS**:
   ```bash
   # 对于Intel Mac
   curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh
   bash Miniforge3-MacOSX-x86_64.sh
   
   # 对于M1/M2 Mac
   curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
   bash Miniforge3-MacOSX-arm64.sh
   ```
   
   **Linux**:
   ```bash
   wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
   bash Miniforge3-Linux-x86_64.sh
   ```
   
   **Windows**:
   - 下载 [Miniforge3-Windows-x86_64.exe](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe)
   - 运行下载的安装程序并按照提示完成安装

3. 使用run.sh脚本进行环境设置（推荐方式）
   ```bash
   # 设置环境（创建conda虚拟环境并安装依赖）
   ./run.sh setup
   ```
   
   或者手动设置：
   ```bash
   # 创建并激活conda环境
   conda create -y -n venv python=3.11
   conda activate venv
   
   # 安装依赖
   pip install -r requirements.txt
   ```

4. 设置WebDriver
   ```
   # 下载最新版的chrome-headless-shell和ChromeDriver
   bash scripts/setup_latest_driver.sh
   ```
   
   该脚本会自动：
   - 检测您的操作系统和架构
   - 从官方Chrome for Testing链接获取最新的稳定版本
   - 下载最新版本的chrome-headless-shell和ChromeDriver
   - 设置必要的执行权限
   - 创建配置文件以供程序使用

5. 设置配置文件
   创建`config.secret.yaml`文件并添加您的API密钥：
   ```yaml
   ai_analyzer:
     api_key: "your-api-key-here"
   ```

   > **注意**: 项目提供了`config.secret.yaml.example`作为模板，请复制该文件并重命名为`config.secret.yaml`，然后填入您的实际配置。`config.secret.yaml`文件已在`.gitignore`中，不会被提交到版本控制系统，以保护您的敏感信息安全。
   
   ```bash
   # 复制示例配置文件
   cp config.secret.yaml.example config.secret.yaml
   
   # 编辑配置文件填入您的API密钥
   nano config.secret.yaml
   ```

6. 运行程序

   使用统一的run.sh脚本运行程序：
   
   ```bash
   # 显示帮助信息
   ./run.sh help
   
   # 设置环境（创建虚拟环境并安装依赖）
   ./run.sh setup
   
   # 下载最新的WebDriver
   ./run.sh driver
   
   # 爬取数据
   ./run.sh crawl
   
   # 分析数据
   ./run.sh analyze
   
   # 启动Web服务器
   ./run.sh server
   ```
   
   高级用法：
   
   ```bash
   # 仅爬取指定厂商的数据
   ./run.sh crawl --vendor aws
   
   # 限制每个来源爬取的文章数量
   ./run.sh crawl --limit 10
   
   # 强制爬取所有数据，忽略本地metadata
   ./run.sh crawl --force
   
   # 强制分析所有数据，忽略metadata记录
   ./run.sh analyze --force
   
   # 仅分析指定厂商的数据
   ./run.sh analyze --vendor aws
   
   # 分析特定文件
   ./run.sh analyze --file data/raw/aws/blog/2025_03_10_8c2b1da4.md
   
   # 强制分析特定文件
   ./run.sh analyze --force --file data/raw/aws/blog/2025_03_10_8c2b1da4.md
   
   # 指定主机和端口启动服务器
   ./run.sh server --host 0.0.0.0 --port 8080
   
   # 启用调试模式
   ./run.sh server --debug
   
   # 清理数据目录
   ./run.sh crawl --clean
   
   # 每日自动爬取与分析
   ./scripts/daily_crawl_and_analyze.sh
   ```
   
   你仍然可以使用原始的Python命令：
   
   ```bash
   # 爬取数据
   python -m src.main --mode crawl
   
   # 分析数据
   python -m src.main --mode analyze
   
   # 测试模式：清理所有数据并依次执行爬虫和分析(每个来源只爬取1篇文章)
   python -m src.main --mode test
   ```

   c. 命令行参数完整说明
   ```
   选项:
     --mode {crawl,analyze,test}  运行模式: crawl(爬取数据), analyze(分析数据), test(测试模式)
     --vendor VENDOR            爬取指定厂商的数据, 如aws, azure等，仅在crawl模式下有效
     --clean                    清理所有中间文件
     --limit LIMIT              爬取的文章数量限制，如设置为5则每个来源只爬取5篇，0表示使用配置文件中的默认值
     --config CONFIG            指定配置文件路径(默认为根目录下的config.yaml)
     --force                    强制执行，忽略本地metadata或文件是否已存在
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
   python -m src.main --mode crawl --force            # 强制爬取所有数据，忽略本地metadata
   
   # 分析控制
   python -m src.main --mode analyze --force          # 强制分析所有数据，忽略metadata记录
   python -m src.main --mode analyze --vendor aws     # 只分析AWS的数据
   python -m src.main --mode analyze --file path/to/file.md  # 只分析特定文件
   
   # 配置和清理
   python -m src.main --config production.yaml --mode crawl  # 使用自定义配置文件
   python -m src.main --clean                         # 清理所有数据目录
   python -m src.main --clean --mode crawl            # 清理后立即开始爬取
   
   # 测试组合
   python -m src.main --mode test --vendor aws        # 测试模式仅处理AWS数据
   ```

## Web服务器

项目提供了一个Web界面，用于浏览和查看爬取及分析的结果。服务器可以独立于主程序运行，方便部署和使用。

### 启动Web服务器

```bash
# 基本启动命令（默认在127.0.0.1:5000上运行）
python -m src.web_server.run

# 自定义主机和端口
python -m src.web_server.run --host 0.0.0.0 --port 8080

# 启用调试模式
python -m src.web_server.run --debug

# 指定数据目录
python -m src.web_server.run --data-dir /path/to/data

# 调整日志级别
python -m src.web_server.run --log-level DEBUG
```

### 命令行参数说明

- `--host`：服务器监听的主机地址，默认为`127.0.0.1`（仅本机访问）
- `--port`：服务器端口，默认为`5000`
- `--data-dir`：数据目录路径，默认为项目根目录下的`data`目录
- `--debug`：启用调试模式，便于开发和排错
- `--log-level`：日志级别，可选值为DEBUG、INFO、WARNING、ERROR、CRITICAL

### 使用说明

服务器启动后，可以通过浏览器访问相应地址（如`http://127.0.0.1:5000`）来浏览和查看：

1. 按云厂商分类的文章列表
2. 原始爬取内容
3. AI分析结果
4. 支持全文检索功能
5. 支持按日期、厂商、主题等过滤

**提示**：如果需要允许其他设备通过网络访问，请使用`--host 0.0.0.0`参数启动服务器。

## 配置说明

### 配置文件系统

项目使用两个YAML格式的配置文件进行配置，以提高安全性：
- `config.yaml`：主配置文件，包含爬虫配置、数据源配置和AI分析的基本配置
- `config.secret.yaml`：敏感配置文件，主要用于存储API密钥等敏感信息

这种分离确保了敏感数据不会被意外提交到版本控制系统。

```yaml
# 基础配置示例 (config.yaml)
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
  model: "${ANALYZER_MODEL}"     # 使用的AI模型
  max_tokens: 4000      # 最大令牌数
  temperature: 0.8      # 温度参数
  api_base: "${API_BASE_URL}"  # API基础URL
  system_prompt: "你是一个专业的云计算技术分析师..." # 系统提示词
  tasks:
    - type: "AI摘要"
      prompt: "请对此云服务商的内容进行总结..."
    # 更多任务...
```

```yaml
# 敏感配置示例 (config.secret.yaml)
ai_analyzer:
  # API密钥
  api_key: "your-api-key-here"
  # 可以指定实际模型名称覆盖默认值
  model: "qwen-max"
  # API基础URL
  api_base: "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
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
```

### 分析模块元数据功能

分析模块现在使用metadata记录每个文件的分析状态，提供以下优势：

1. **智能防重复分析**：系统会记录每个文件的分析状态，包括每个任务是否成功完成，避免重复分析已处理的文件
2. **任务级别跟踪**：对每个分析任务（如标题翻译、竞争分析、全文翻译等）单独跟踪成功状态
3. **错误恢复**：如果某个任务失败，下次运行时只会重新执行失败的任务
4. **强制模式**：使用`--force`参数可以忽略metadata记录，强制重新分析所有文件

metadata文件存储在`data/metadata/analysis_metadata.json`中，包含以下信息：
- 文件路径
- 最后分析时间
- 每个任务的状态（成功/失败）
- 任务执行时间戳
- 文件的元数据信息

### AI分析功能详细说明

#### 分析类型

当前支持以下几种分析类型：

1. **内容摘要**：提取文章的关键要点和主要内容
2. **竞争分析**：深入分析云厂商的产品特点、市场定位和竞争策略
3. **技术解读**：解释技术特性和创新点
4. **战略意图解读**：分析产品发布背后的战略考量
5. **市场预测**：基于新产品或功能预测市场趋势和竞争对手可能的反应

#### AI分析配置示例

```yaml
ai_analyzer:
  # 基础配置
  model: "${ANALYZER_MODEL}"  # 使用的AI模型
  max_tokens: 4000      # 最大令牌数
  temperature: 0.8      # 温度参数
  
  # 分析任务
  tasks:
    - type: "AI摘要"
      prompt: "请对此云服务商的博客内容进行专业摘要，提取关键技术点和主要公告。"
      
    - type: "竞争分析"
      prompt: "作为一名云计算竞争分析专家，请对这篇博客进行详细的竞争分析，包括：
        1. 概述：简要总结此博客所描述的产品/功能及其主要卖点
        2. 关键技术洞察：技术特性的独特之处
        3. 竞争对手对比：与AWS、Azure和GCP同类产品的详细对比
        4. 市场影响分析：此产品对市场竞争格局的影响
        5. 战略意图解读：推测该厂商发布这一产品/功能的战略考量
        6. 市场预测：预测市场和客户的反应以及竞争对手的可能回应
        7. 建议策略：给其他云厂商的应对建议"
    
    - type: "中文翻译"
      prompt: "请将以下英文内容翻译成流畅、专业的中文，保留原文的技术术语准确性："
      language: "zh"
      condition: "language != 'zh'"  # 条件：仅当原文不是中文时执行
```

#### 文件命名规范

为了便于管理和检索，本项目对爬取的内容和分析结果采用统一的文件命名规范：

1. **原始爬取文件**：
   ```
   YYYY_MM_DD_<url_hash>.md
   ```
   例如：`2025_04_08_af122aaf.md`

2. **分析结果文件**：
   ```
   <原文件名>_<分析类型>.md
   ```
   例如：`2025_04_08_af122aaf_竞争分析.md`

#### 元数据格式

每个生成的文件都包含标准化的元数据头部：

```markdown
# 文章标题

**原始链接:** [链接URL](链接URL)

**发布时间:** YYYY-MM-DD

**厂商:** AWS

**类型:** BLOG

---

正文内容...
```

对于分析文件，还会包含额外的分析元数据：

```markdown
# 文章标题 - AI分析：竞争分析

**原始链接:** [链接URL](链接URL)

**发布时间:** YYYY-MM-DD

**厂商:** AWS

**类型:** BLOG

**分析类型:** 竞争分析

**分析时间:** YYYY-MM-DD HH:MM:SS

---

## AI分析结果

### 概述
...

### 关键技术洞察
...

### 竞争对手对比
...

（更多分析内容...）
```

## 常见问题 (FAQ)

### 1. 安装问题
**Q: 安装时找不到chrome-headless-shell**
A: 执行`bash scripts/setup_latest_driver.sh`重新安装WebDriver，或手动下载Chrome浏览器

**Q: 依赖安装出错**
A: 确保您的Python版本是3.8或更高版本，并且已安装pip的最新版本。尝试`pip install --upgrade pip`后重新安装

**Q: 在Windows上安装出现问题**
A: Windows用户可能需要安装Visual C++ Build Tools，或者使用WSL(Windows Subsystem for Linux)

### 2. 爬虫问题
**Q: 爬虫无法获取某些网站内容**
A: 有些网站可能有反爬虫措施。尝试以下解决方案：
- 调整`interval`参数增加请求间隔时间
- 修改`user_agent`和自定义`headers`
- 启用代理配置

**Q: 如何只爬取特定类别的内容？**
A: 在配置文件中设置`specific_categories`或`specific_tags`参数，详见"厂商爬虫配置示例"

**Q: 报错"Chrome version must be between X and Y"**
A: 执行`bash scripts/setup_latest_driver.sh`下载最新版本的chrome-headless-shell和匹配的ChromeDriver

**Q: 爬虫运行时出现ChromeDriver错误**
A: 版本兼容性问题导致。执行`bash scripts/setup_latest_driver.sh`，它会自动下载兼容的chrome-headless-shell和ChromeDriver

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

**Q: AI模型调用失败**
A: 检查您的API密钥是否正确，网络是否畅通，以及是否超出API调用限制

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

**Q: 如何确保chrome-headless-shell和ChromeDriver版本匹配？**
A: 使用`bash scripts/setup_latest_driver.sh`脚本，它会自动下载匹配的版本，确保两者兼容

**Q: 如何修改爬取的内容范围？**
A: 编辑`config.yaml`文件中相应厂商的配置，添加或修改特定类别、标签等

**Q: 如何自定义AI分析任务？**
A: 在`config.yaml`的`ai_analyzer.tasks`部分添加新的任务类型和提示词

## 安全性说明

### API密钥安全

项目中的配置文件包含API密钥等敏感信息，需要妥善管理以保证安全。请遵循以下安全最佳实践：

1. **两级配置设计**：
   - `config.yaml`：包含基本配置和环境变量占位符，可以安全地提交到版本控制系统
   - `config.secret.yaml`：包含实际API密钥和敏感信息，不应该提交到版本控制系统

2. **第一次设置**：
   ```bash
   # 克隆项目后，复制并编辑敏感配置文件
   cp config.examples/config.secret.example.yaml config.secret.yaml
   
   # 编辑敏感配置文件，添加您的API密钥
   nano config.secret.yaml
   ```

3. **保护API密钥**：
   - 不要在公共场所共享包含敏感信息的配置文件
   - 不要将包含真实API密钥的`config.secret.yaml`提交到代码库
   - `config.secret.yaml`文件已经在`.gitignore`中配置为不提交

4. **版本控制**：
   - `config.yaml`可以提交到版本控制系统，因为它只包含基本配置和占位符
   - `config.secret.yaml`不应该提交，它包含实际的API密钥和敏感信息

5. **如果需要共享配置**：
   - 始终使用占位符替换真实API密钥
   - 使用私有通道分享实际密钥

6. **密钥轮换**：
   - 定期更换API密钥
   - 如果怀疑密钥泄露，立即进行轮换

## 许可证
MIT
