# 云计算网络竞争动态分析工具

本项目旨在自动收集、分析并展示各大云计算厂商（如 AWS, Azure, GCP 等）在网络和内容分发领域的最新动态、博客文章、产品更新和技术文档，利用 AI 技术进行内容处理（如翻译、摘要、竞争分析），并通过邮件、钉钉和 Web 界面等多种方式提供情报。

## ✨ 核心功能

*   **多来源数据爬取**: 自动从各大云服务提供商的官方博客、"What's New"、技术社区、产品更新页面等渠道抓取最新信息。
*   **AI 驱动的内容分析**:
    *   标题和全文翻译。
    *   基于可配置 Prompt 的内容分析，如竞争格局分析、新产品特性解读等。
    *   支持多种 AI 大语言模型（通过 OpenAI 兼容 API，如 Grok, Qwen 等）。
*   **灵活的配置系统**:
    *   支持 YAML 格式的配置文件。
    *   提供统一的 `config.example.yaml` 模板，方便上手。
    *   支持 `config.secret.yaml` 单独管理敏感信息（如 API 密钥）。
    *   支持 `config/` 目录下的模块化配置文件。
    *   详细配置文档见 `CONFIGURATION.MD`。
*   **定时任务与调度**:
    *   每日自动执行爬取和分析任务。
    *   可通过 `run.sh` 脚本手动触发。
*   **通知系统**:
    *   支持邮件通知。
    *   支持钉钉机器人推送周报/日报/自定义更新。
*   **Web 服务**:
    *   提供一个简单的 Web 界面，用于浏览和搜索收集到的原始数据和 AI 分析结果。
*   **便捷的命令行工具**:
    *   通过 `run.sh` 脚本提供了一系列便捷命令，用于控制项目的各个方面（爬取、分析、服务启动、数据清理、钉钉推送等）。

## 🛠️ 技术栈

*   **主要语言**: Python 3.x
*   **配置**: YAML
*   **核心依赖**:
    *   `requests`, `beautifulsoup4`, `selenium`/`playwright` (用于爬虫)
    *   `openai` (用于 AI 模型交互)
    *   `PyYAML` (用于配置加载)
    *   `APScheduler` (用于任务调度)
    *   `Flask`/`FastAPI` (或其他 Python Web 框架，用于 Web 服务)
    *   具体依赖请参见 `requirements.txt`

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd cnetCompSpy
```

### 2. 环境设置

**a. (推荐) 创建并激活虚拟环境:**

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate    # Windows
```

**b. 安装依赖:**

```bash
pip install -r requirements.txt
```

**c. (可选) WebDriver 安装:**

部分爬虫可能依赖于 Selenium/Playwright，需要对应的 WebDriver。项目提供了便捷脚本下载 WebDriver：

```bash
bash run.sh driver
```
该脚本会尝试下载最新版本的 ChromeDriver。如果需要其他浏览器驱动，请手动安装。需要科学上网环境

### 3. 配置项目

**a. 创建配置文件:**

项目配置通过根目录下的 `config.yaml` 和 `config.secret.yaml` 文件管理。

1.  **主配置文件**: 复制配置模板 `config.example.yaml` 为 `config.yaml`:
    ```bash
    cp config.example.yaml config.yaml
    ```
    然后根据您的需求修改 `config.yaml` 中的配置项。`config.example.yaml` 中有详细的注释说明。

2.  **敏感信息配置**: 创建 `config.secret.yaml` 文件用于存放 API 密钥、密码、Webhook URL 等敏感信息。
    ```bash
    # touch config.secret.yaml # 创建空文件
    ```
    然后参照 `config.example.yaml` 文件末尾的 `config.secret.yaml 示例` 部分，将相关敏感配置项填入 `config.secret.yaml`。
    例如：
    ```yaml
    # config.secret.yaml
    notification:
      email:
        username: "your_smtp_username@example.com"
        password: "your_smtp_password"
      dingtalk:
        webhook: "YOUR_DINGTALK_WEBHOOK_URL"
        secret: "YOUR_DINGTALK_SECRET_IF_ANY"

    ai_analyzer:
      grok_api_key: "YOUR_GROK_X_AI_API_KEY"
      dashscope_api_key: "YOUR_ALIYUN_DASHSCOPE_API_KEY"
      # openai_api_key: "YOUR_OPENAI_API_KEY"

    webserver:
      secret_key: "a_very_strong_random_secret_key"
    ```
    **重要**: `config.secret.yaml` 已被加入 `.gitignore`，不会被提交到版本库。

**b. 理解配置加载:**

*   系统优先加载 `config.secret.yaml`，然后是 `config.yaml`。
*   也可以使用 `config/` 目录存放分模块的配置文件 (如 `config/crawler.yaml`, `config/ai_analyzer.yaml` 等)，系统会自动加载。这种方式下，根目录的 `config.yaml` 可以不存在或只包含少量全局配置。
*   更详细的配置加载逻辑和高级用法，请参考 `CONFIGURATION.MD`。

### 4. 运行项目

项目提供了强大的 `run.sh` 脚本来简化操作。

**a. 查看帮助:**

```bash
bash run.sh help
```
这将列出所有可用的命令及其选项。

**b. 常用命令:**

*   **执行每日综合任务 (爬取 + 分析 + 可能的通知):**
    ```bash
    bash run.sh daily
    ```
    可以附加参数，例如 `--vendor aws --limit 10 --no-email`。

*   **单独执行爬取任务:**
    ```bash
    bash run.sh crawl --vendor aws --source blog --limit 5
    ```

*   **单独执行分析任务:**
    ```bash
    bash run.sh analyze --vendor aws --limit 5
    # 分析特定文件
    # bash run.sh analyze --file data/raw/aws/blog/your_file_name.md
    ```

*   **启动 Web 服务:**
    ```bash
    bash run.sh server
    # 指定主机和端口
    # bash run.sh server --host 0.0.0.0 --port 8000
    ```
    启动后，默认可在 `http://localhost:8080` 访问。

*   **手动推送钉钉消息:**
    ```bash
    bash run.sh dingpush weekly # 推送本周更新
    bash run.sh dingpush daily  # 推送今日更新
    bash run.sh dingpush recent 3 # 推送最近3天更新
    ```

*   **清理数据和缓存:**
    ```bash
    bash run.sh clean --all
    ```

**c. 直接运行 Python 模块 (高级):**

虽然推荐使用 `run.sh`，但也可以直接运行 `src/main.py` 并传递相应参数：
```bash
python -m src.main crawl --vendor aws
python -m src.main analyze
python -m src.main server
python -m src.main scheduler # 启动定时调度器 (通常由 `daily` 任务管理或独立运行)
```

## 📂 项目结构

```
cnetCompSpy/
├── .git/                   # Git 仓库元数据
├── .vscode/                # VSCode 编辑器配置
├── config/                 # (可选) 模块化配置文件目录
│   ├── ai_analyzer.yaml
│   ├── crawler.yaml
│   ├── ...
│   └── main.yaml           # 模块化配置导入清单
├── data/                   # 数据存储目录
│   ├── raw/                # 爬虫下载的原始 Markdown/HTML 文件
│   ├── analysis/           # AI 分析结果
│   └── metadata/           # 元数据文件 (如 analysis_metadata.json)
├── drivers/                # WebDriver 存放目录
├── logs/                   # 日志文件目录 (e.g., app.log)
├── prompt/                 # AI Prompt 文件目录
│   ├── competitive_analysis.txt
│   ├── title_translation.txt
│   └── ...
├── scripts/                # 辅助脚本 (如 config_backup.py)
├── src/                    # 项目核心源代码
│   ├── ai_analyzer/        # AI 分析模块
│   ├── crawlers/           # 爬虫实现模块
│   ├── utils/              # 工具类 (配置加载器, 日志等)
│   ├── web_server/         # Web 服务模块
│   ├── __init__.py
│   ├── dingtalk_pusher_cli.py # 钉钉推送命令行工具
│   └── main.py             # 项目主入口和命令行接口
├── tests/                  # 测试代码目录
├── venv/                   # (推荐) Python 虚拟环境目录
├── .gitignore              # Git 忽略文件配置
├── config.example.yaml     # 配置文件模板 ✨
├── config.secret.yaml      # (需手动创建) 敏感信息配置文件 🔒
├── CONFIGURATION.MD        # 详细的配置系统说明文档 📖
├── README.md               # 本文件
├── requirements.txt        # Python 依赖包列表
├── run.sh                  # 主控制脚本 🚀
└── setup.py                # Python 项目打包配置
```

## ⚙️ 配置系统简述

*   **加载器**: `src/utils/config_loader.py` 中的 `get_config()` 是统一的配置加载入口。
*   **优先级**: 命令行参数 > `config/` 目录 > `config.secret.yaml` > `config.yaml` > 代码内默认值。
*   **敏感信息**: 务必将 API 密钥、密码等放入 `config.secret.yaml`，此文件不纳入版本控制。
*   **模块化**: 可以在 `config/` 目录下按模块组织 `.yaml` 文件，通过 `config/main.yaml` 的 `imports` 字段控制加载顺序，或让系统自动按字母序加载。

详细信息请参阅 `CONFIGURATION.MD`。

## 🧠 AI 分析模块

*   **模型配置**: 在 `ai_analyzer.model_profiles` (位于 `config.yaml` 或 `config/ai_analyzer.yaml`) 中配置不同的 AI 模型（如 Grok, Qwen, OpenAI GPT 系列）。
*   **当前激活模型**: 通过 `ai_analyzer.active_model_profile` 指定当前默认使用的模型。
*   **Prompt 管理**:
    *   Prompt 文件存放在 `prompt/` 目录下。
    *   在配置文件的 `ai_analyzer.prompt_settings.task_prompt_map` 中，将任务类型映射到具体的 Prompt 文件。
*   **任务定义**: 在配置文件的 `ai_analyzer.tasks` 列表中定义需要执行的 AI 分析任务及其类型。

## 🕷️ 爬虫模块

*   **通用配置**: 在 `crawler` 部分 (位于 `config.yaml` 或 `config/crawler.yaml`) 配置全局爬虫参数，如超时、重试、并发数等。
*   **数据源**: 在 `sources` 部分定义各个云厂商及其下的具体信息来源 (URL, 类型等)。
    *   每个数据源可以有独立的 `enabled`, `test_mode`, `article_limit` 等配置。
    *   `type` 字段用于关联到 `src/crawlers/` 下的具体爬虫实现类。

## 🌐 Web 服务

*   通过 `webserver` (位于 `config.yaml` 或 `config/webserver.yaml`) 配置 Web 服务的启用、主机、端口等。
*   `show_raw_data` 控制是否在界面上直接展示原始的 Markdown 文本。

## 📜 日志

*   日志配置在 `logging` 部分 (位于 `config.yaml` 或 `config/logging.yaml`)，遵循 Python 标准 logging 模块的字典配置格式。
*   默认情况下，日志会输出到控制台和 `logs/app.log` 文件。
*   可以为特定模块（如 `werkzeug`, `src.crawlers`）设置不同的日志级别。

## 🤝 贡献

欢迎各种形式的贡献！如果您有任何建议、发现 Bug 或希望添加新功能，请随时通过 Issues 或 Pull Requests 与我们联系。

## 📄 许可证

(如果项目有许可证，在此说明，例如 MIT, Apache 2.0 等)

---

希望这份 README 能帮助您快速开始！如果您在配置或使用过程中遇到任何问题，请先查阅 `CONFIGURATION.MD` 或 `run.sh help`，或随时提出 Issue。 