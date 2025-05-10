# 云计算网络竞争情报分析系统

本系统旨在自动收集、分析和推送云计算厂商的网络产品和技术最新动态，帮助用户及时了解市场竞争情况和技术发展趋势。

## 功能特点

- **多源数据采集**：支持从AWS、Azure、GCP、腾讯云、华为云等多个云厂商的博客、产品更新、技术文档等渠道爬取数据
- **AI驱动分析**：利用OpenAI、阿里云灵积模型等AI能力进行内容分析和摘要生成
- **灵活配置系统**：模块化配置文件结构，便于自定义采集源和分析策略
- **多渠道推送**：支持邮件、钉钉等多种通知方式
- **Web可视化界面**：提供直观的数据浏览和管理界面

## 系统要求

- Python 3.8+
- Chrome浏览器（用于Selenium爬虫）
- Miniforge/Conda（推荐用于环境管理）
- 足够的网络带宽和存储空间

## 环境准备

本项目提供了`run.sh`脚本用于自动化环境设置，推荐使用这种方式进行环境准备。

### 使用run.sh设置环境（推荐）

1. 克隆代码库

```bash
git clone https://github.com/benjamin1108/cnetCompSpy.git
cd cnetCompSpy
```

2. 给脚本执行权限

```bash
chmod +x run.sh
```

3. 使用setup命令设置环境

```bash
./run.sh setup
```

这个命令会自动执行以下步骤：
- 检查Miniforge是否已安装（如未安装会提供安装指南）
- 创建并激活名为"venv"的conda虚拟环境
- 在虚拟环境中安装项目所需的所有依赖

4. 下载WebDriver（用于Selenium爬虫）

```bash
./run.sh driver
```

### 手动设置环境（替代方案）

如果您不希望使用run.sh脚本或遇到问题，也可以手动设置环境：

1. 安装Miniforge（如果尚未安装）
   - Linux: `wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh && bash Miniforge3-Linux-x86_64.sh`
   - macOS: `curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh && bash Miniforge3-MacOSX-x86_64.sh`
   - Windows: 下载并运行 [Miniforge安装程序](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe)

2. 创建并激活虚拟环境

```bash
conda create -y -n venv python=3.11
conda activate venv
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 手动安装WebDriver（需要与您的Chrome版本匹配）

## 配置系统

1. 复制示例配置文件并按需修改：

```bash
cp config.example.yaml config.secret.yaml
```

2. 根据需要编辑`config.secret.yaml`文件，特别是各个API密钥和通知设置。

## 配置说明

系统配置分为以下几个主要部分：

1. **通知配置（notification）**：设置邮件、钉钉等通知渠道
2. **爬虫配置（crawler）**：设置爬虫的全局参数如超时、重试等
3. **数据源配置（sources）**：定义各个云厂商的数据来源
4. **AI分析配置（ai_analyzer）**：配置AI模型参数和分析策略
5. **日志配置（logging）**：设置日志级别和输出位置

详细配置说明请参考`config.example.yaml`中的注释和`CONFIGURATION.md`文档。

## 使用方法

### 使用run.sh脚本

项目根目录下的`run.sh`脚本是操作系统的主要工具，提供多种功能：

```bash
# 显示帮助信息
./run.sh help
```

#### 基本命令

```bash
# 爬取数据
./run.sh crawl [--vendor aws|azure|gcp] [--source 类型] [--limit 数量] [--clean] [--force]

# 分析数据
./run.sh analyze [--vendor aws|azure|gcp|tencent|huawei|volcano] [--file 文件路径] [--limit 数量]

# 启动Web服务器
./run.sh server [--host 主机地址] [--port 端口号]

# 设置环境(创建虚拟环境并安装依赖)
./run.sh setup

# 下载最新的WebDriver
./run.sh driver

# 比较元数据和实际文件统计
./run.sh stats [--detailed]

# 检查任务完成状态
./run.sh check-tasks [--tasks-only]
```

#### 数据管理命令

```bash
# 清理文件
./run.sh clean [--all] [--pyc] [--logs] [--temp] [--data]

# 执行每日爬取与分析任务
./run.sh daily [--no-email] [--no-stats] [--no-crawl] [--no-analyze] [--no-dingtalk]

# 重建元数据
./run.sh rebuild-md [--type crawler|analysis|all] [--force] [--deep-check]

# 钉钉推送通知
./run.sh dingpush weekly|daily|recent [天数] [--robot 机器人名称] [--config 配置文件]
```

#### 调试选项

所有命令都支持`--debug`参数启用调试模式：

```bash
./run.sh --debug crawl
```

#### 配置文件选项

许多命令支持通过`--config`指定配置文件：

```bash
./run.sh crawl --config /path/to/config
```

### src/main.py - 主入口模块详解

系统的核心功能由`src/main.py`提供，它是项目的主要入口点，支持多种运行模式和参数：

```bash
python -m src.main [选项]
```

#### 主要参数

- `--mode`: 指定运行模式，可选值：
  - `crawl`: 爬取数据模式
  - `analyze`: 分析数据模式
  - `test`: 测试模式（会同时进行爬取和分析，且设置测试标志）

- `--vendor`: 指定要处理的云服务提供商，如 aws, azure, gcp 等
- `--source`: 指定要处理的数据来源类型，如 blog, whatsnew 等
- `--clean`: 清理所有中间文件
- `--limit`: 限制爬取或分析的文章数量，如设置为5则每个来源只处理5篇
- `--config`: 指定配置文件路径
- `--force`: 强制执行，忽略本地metadata或文件是否已存在
- `--file`: 指定要分析的文件路径（仅在analyze模式下有效）
- `--debug`: 启用调试模式，输出详细的日志信息

#### 爬取模式 (crawl)

```bash
python -m src.main --mode crawl [--vendor aws] [--source blog] [--limit 10] [--force] [--debug]
```

爬取模式会执行以下操作：
1. 加载配置文件
2. 基于`--vendor`和`--source`参数过滤要处理的数据源
3. 应用`--limit`和`--force`参数
4. 创建并运行CrawlerManager来爬取数据
5. 将爬取的内容保存到`data/raw/{vendor}/{source}`目录

#### 分析模式 (analyze)

```bash
python -m src.main --mode analyze [--vendor aws] [--file path/to/file.md] [--limit 10] [--force] [--debug]
```

分析模式会执行以下操作：
1. 创建AIAnalyzer实例并加载配置
2. 基于参数决定要分析的内容:
   - 如果指定了`--file`，只分析该文件
   - 如果设置了`--force`，重新分析所有符合条件的文件
   - 否则，根据元数据选择未分析的文件进行分析
3. 分析结果保存到`data/analysis/{vendor}/{source}`目录

#### 测试模式 (test)

```bash
python -m src.main --mode test [--debug]
```

测试模式将：
1. 为所有数据源设置测试模式（每个源只爬取少量文章）
2. 依次执行爬取和分析操作
3. 适用于快速验证系统功能

### 直接使用其他Python模块

```bash
# 启动Web服务器
python -m src.web_server.run [选项]
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行带覆盖率测试
pytest --cov=src
```

## 项目结构

```
cnetCompSpy/
├── config/                 # 模块化配置文件目录
├── data/                   # 数据存储目录
├── logs/                   # 日志目录
├── src/                    # 源代码
│   ├── ai_analyzer/        # AI分析模块
│   ├── crawlers/           # 爬虫模块
│   ├── utils/              # 工具类
│   ├── web_server/         # Web服务器
│   └── main.py             # 主程序入口
├── scripts/                # 辅助脚本
├── prompt/                 # AI提示词模板
├── drivers/                # WebDriver驱动
├── config.example.yaml     # 配置文件模板
├── run.sh                  # 项目管理和操作的主要脚本
└── requirements.txt        # 依赖列表
```

## 许可证

[指定您的许可证]

## 贡献指南

欢迎提交Issues和Pull Requests！ 