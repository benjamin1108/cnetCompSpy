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
   
   # 使用自定义配置文件爬取数据
   ./run.sh crawl --config custom.yaml
   
   # 强制分析所有数据，忽略metadata记录
   ./run.sh analyze --force
   
   # 仅分析指定厂商的数据
   ./run.sh analyze --vendor aws
   
   # 分析特定文件
   ./run.sh analyze --file data/raw/aws/blog/2025_03_10_8c2b1da4.md
   
   # 使用自定义配置文件分析数据
   ./run.sh analyze --config prod.yaml
   
   # 比较元数据和实际文件统计
   ./run.sh stats
   
   # 显示详细的文件对比信息
   ./run.sh stats --detailed
   
   # 检查任务完成状态，显示未完成任务的文件
   ./run.sh check-tasks
   
   # 清理所有中间文件和临时文件
   ./run.sh clean
   
   # 只清理Python字节码文件
   ./run.sh clean --pyc
   
   # 只清理日志文件
   ./run.sh clean --logs
   
   # 清理data目录
   ./run.sh clean --data
   
   # 重建元数据，从本地MD文件更新元数据
   ./run.sh rebuild-md
   
   # 强制重建元数据，即使元数据已存在
   ./run.sh rebuild-md --force
   
   # 深度检查分析文件内容，识别"假完成"问题
   ./run.sh rebuild-md --deep-check
   
   # 深度检查并删除问题文件
   ./run.sh rebuild-md --deep-check --delete
   
   # 指定主机和端口启动服务器
   ./run.sh server --host 0.0.0.0 --port 8080
   
   # 启用调试模式
   ./run.sh server --debug
   
   # 执行每日自动爬取与分析
   ./run.sh daily
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

## 命令参考

### 主要命令

| 命令         | 说明                               | 常用选项                                  |
|-------------|-----------------------------------|------------------------------------------|
| crawl       | 爬取数据                           | --vendor, --limit, --config, --force     |
| analyze     | 分析数据                           | --vendor, --file, --limit, --config, --force |
| server      | 启动Web服务器                      | --host, --port, --debug                  |
| setup       | 设置环境                           | 无参数                                    |
| driver      | 下载最新的WebDriver                | 无参数                                    |
| stats       | 比较元数据和实际文件统计            | --detailed                                |
| check-tasks | 检查任务完成状态                   | --tasks-only                              |
| clean       | 清理中间文件和临时文件              | --all, --pyc, --logs, --temp, --data     |
| daily       | 执行每日爬取与分析任务              | 无参数                                    |
| rebuild-md  | 重建元数据                         | --type, --force, --deep-check, --delete  |
| help        | 显示帮助信息                       | 无参数                                    |

### 通用选项

| 选项          | 适用命令                  | 说明                                       |
|--------------|--------------------------|-------------------------------------------|
| --vendor     | crawl, analyze           | 指定厂商 (aws\|azure\|gcp\|tencent\|huawei\|volcano) |
| --limit      | crawl, analyze           | 限制爬取/分析的文章数量                      |
| --config     | crawl, analyze           | 指定配置文件路径                             |
| --force      | crawl, analyze, rebuild-md | 强制执行，忽略local metadata或文件是否已存在 |
| --debug      | server                   | 启用调试模式                                |
| --clean      | crawl, analyze           | 清理数据目录                                |

### 爬虫和分析流程

完整的数据处理流程通常包括以下步骤：

1. **爬取数据**：从各厂商网站爬取原始数据
   ```bash
   ./run.sh crawl
   ```

2. **分析数据**：对爬取的数据进行AI分析
   ```bash
   ./run.sh analyze
   ```

3. **检查分析结果**：验证分析完整性
   ```bash
   ./run.sh check-tasks
   ```

4. **元数据维护**：重建或更新元数据
   ```bash
   ./run.sh rebuild-md
   ```

5. **查看统计信息**：了解爬取和分析的情况
   ```bash
   ./run.sh stats --detailed
   ```

每次爬取或分析完成后，系统会自动运行`rebuild-md`命令进行元数据更新和深度检查（不会删除文件），确保数据完整性。

## 自动化任务

系统支持自动化任务，可以通过以下命令执行每日爬取与分析：

```bash
./run.sh daily
```

该命令会按顺序执行：
1. 爬取所有厂商的新数据
2. 分析新爬取的数据
3. 重建元数据
4. 生成统计报告
5. 通过电子邮件发送结果摘要（如果在配置中启用）

您可以通过crontab设置此命令的自动执行，例如：

```bash
# 每天凌晨2点执行爬取和分析
0 2 * * * cd /path/to/cloud-comp-spy && ./run.sh daily
```

## 元数据管理

元数据是系统的重要组成部分，用于跟踪爬取和分析状态。可以通过以下命令管理元数据：

```bash
# 重建所有元数据
./run.sh rebuild-md

# 只重建爬虫元数据
./run.sh rebuild-md --type crawler

# 只重建分析元数据
./run.sh rebuild-md --type analysis

# 深度检查分析文件（识别"假完成"问题）
./run.sh rebuild-md --deep-check

# 删除有问题的文件（谨慎使用）
./run.sh rebuild-md --deep-check --delete
```

深度检查功能可以识别分析中的"假完成"问题（内容异常但标记为已完成的文件），并可选择性地删除这些文件。检查结果会保存到日志文件中，以便进一步分析。

## 网络服务器

系统内置了Web服务器，可以通过浏览器查看爬取和分析结果：

```bash
# 启动默认服务器（localhost:5000）
./run.sh server

# 绑定到特定地址和端口
./run.sh server --host 0.0.0.0 --port 8080
```

Web界面提供以下功能：
- 按厂商浏览爬取的内容
- 查看分析结果和摘要
- 检查任务完成状态
- 导出统计数据和报告

## 系统维护

定期维护可以保持系统运行良好：

```bash
# 清理所有临时文件（不包括数据）
./run.sh clean

# 清理旧日志文件
./run.sh clean --logs

# 更新WebDriver到最新版本
./run.sh driver
```

建议定期执行元数据重建和统计分析，以保持系统数据的一致性。

## 排错指南

如果遇到问题，请尝试以下步骤：

1. **检查日志文件**：
   ```bash
   cat logs/cnetCompSpy_*.log
   ```

2. **验证元数据完整性**：
   ```bash
   ./run.sh rebuild-md --force
   ```

3. **检查未完成的任务**：
   ```bash
   ./run.sh check-tasks
   ```

4. **更新WebDriver**：
   ```bash
   ./run.sh driver
   ```

5. **清理缓存和临时文件**：
   ```bash
   ./run.sh clean --all
   ```

如有其他问题，请查看项目源代码或提交issue。

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
