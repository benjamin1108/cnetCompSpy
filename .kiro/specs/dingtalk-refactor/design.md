# 设计文档

## 概述

本设计重构钉钉通知系统，对所有时间范围统一使用基于报告的方法。重构消除了过时的推送模式（weekly、daily），并将 recent 模式转换为使用与当前 weekly_report 模式相同的高质量 AI 生成报告格式。

关键的架构变更是将 `generate_weekly_report.py` 转换为通用的 `report_generator.py` 模块，该模块可以为任何日期范围生成报告，并更新钉钉通知系统仅使用基于报告的推送。

## 架构

### 高层组件结构

```
┌─────────────────────────────────────────────────────────────┐
│                         run.sh                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  dingpush 命令处理器                                  │   │
│  │  - weekly-report: 调用 report_generator + pushfile   │   │
│  │  - recent-report N: 调用 report_generator + pushfile │   │
│  │  - pushfile: 直接调用 dingtalk.py                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├─────────────────┬───────────────┐
                            ▼                 ▼               ▼
                ┌───────────────────┐  ┌──────────────┐  ┌──────────────┐
                │ report_generator  │  │ dingtalk.py  │  │ 配置文件     │
                │                   │  │              │  │              │
                │ - ReportGenerator │  │ - DingTalk   │  │ - main.yaml  │
                │   类              │  │   Notifier   │  │ - reporting  │
                │ - generate()      │  │ - send_      │  │   .yaml      │
                │ - collect_        │  │   report_    │  │              │
                │   articles()      │  │   file()     │  │              │
                └───────────────────┘  └──────────────┘  └──────────────┘
```

### 数据流

1. **用户调用命令**: `./run.sh dingpush recent-report 7`
2. **run.sh 处理**: 验证参数，激活虚拟环境
3. **run.sh 调用 report_generator**: `python -m src.utils.report_generator --days 7`
4. **report_generator**:
   - 计算日期范围（今天 - 7 天到今天）
   - 从 data/raw 收集匹配日期范围的文章
   - 将所有文章发送到 LLM 生成摘要
   - 将原始 URL 替换为内部链接
   - 生成格式化的 markdown 报告
   - 保存到 data/reports/recent_N_days_report_YYYY-MM-DD.md
5. **run.sh 调用 dingtalk**: `python -m src.utils.dingtalk pushfile --filepath <report_path>`
6. **dingtalk.py**: 读取文件并发送到配置的机器人

## 组件和接口

### 1. report_generator.py（原 generate_weekly_report.py）

**位置**: `src/utils/report_generator.py`

**目的**: 为任何日期范围生成 AI 驱动的 markdown 报告

**关键类**:

```python
class ReportGenerator:
    """为日期范围内的云厂商更新生成格式化报告"""
    
    def __init__(self, config: dict, start_date: date, end_date: date):
        """
        初始化报告生成器
        
        参数:
            config: 完整配置字典
            start_date: 日期范围开始（包含）
            end_date: 日期范围结束（包含）
        """
        
    def collect_articles(self) -> List[Dict[str, str]]:
        """
        收集日期范围内的所有文章
        
        返回:
            文章数据字典列表，包含以下键:
            - raw_content: 文章 markdown 内容
            - vendor: 云厂商名称
            - subcategory: 文章类别
            - original_filename: 源文件名
            - source_info_for_llm: 格式化的源字符串
            - original_url: 原始文章 URL
            - date_published: 发布日期（ISO 格式）
        """
        
    def generate_report(self) -> Optional[str]:
        """
        生成完整的 markdown 报告
        
        返回:
            Markdown 报告内容，如果生成失败则返回 None
        """
        
    def save_report(self, content: str) -> str:
        """
        保存报告到文件
        
        参数:
            content: Markdown 报告内容
            
        返回:
            保存的报告文件路径
        """
```

**关键函数**:

```python
def generate_weekly_report(config: dict) -> Optional[str]:
    """
    生成当前周（周一到今天）的报告
    
    参数:
        config: 配置字典
        
    返回:
        生成的报告文件路径，如果失败则返回 None
    """
    
def generate_recent_report(config: dict, days: int) -> Optional[str]:
    """
    生成最近 N 天的报告
    
    参数:
        config: 配置字典
        days: 回溯的天数
        
    返回:
        生成的报告文件路径，如果失败则返回 None
    """
```

**CLI 接口**:

```bash
# 生成周报
python -m src.utils.report_generator --mode weekly [--loglevel DEBUG]

# 生成最近 N 天报告
python -m src.utils.report_generator --mode recent --days 7 [--loglevel DEBUG]
```

### 2. dingtalk.py（重构后）

**位置**: `src/utils/dingtalk.py`

**变更**:
- 移除 `send_weekly_updates()` 方法
- 移除 `send_daily_updates()` 方法  
- 移除 `send_recently_updates()` 方法
- 保留 `send_markdown_file()` 方法（为清晰起见重命名为 `send_report_file()`）
- 更新 CLI 仅支持 `pushfile` 子命令
- 从 argparse 中移除 `weekly`、`daily`、`recent` 子命令

**简化的 CLI 接口**:

```bash
# 发送 markdown 文件到钉钉
python -m src.utils.dingtalk pushfile --filepath <path> [--robot <name>] [--config <path>]
```

**关键方法**（保留的）:

```python
class DingTalkNotifier:
    def send_report_file(self, filepath: str, robot_names: Optional[List[str]] = None) -> bool:
        """
        发送 markdown 报告文件到钉钉机器人
        
        参数:
            filepath: Markdown 文件路径
            robot_names: 可选的机器人名称列表
            
        返回:
            如果成功发送到至少一个机器人则返回 True
        """
```

### 3. run.sh（更新后）

**dingpush 命令的变更**:

```bash
# 旧子命令（已移除）:
# - weekly
# - daily  
# - recent [days]

# 新子命令:
# - weekly-report: 生成并推送周报
# - recent-report [days]: 生成并推送最近 N 天报告
# - pushfile --filepath <path>: 推送任意 markdown 文件
```

**实现**:

```bash
run_dingpush() {
    local subcmd="${1:-}"
    
    case "$subcmd" in
        weekly-report)
            # 生成周报
            python -m src.utils.report_generator --mode weekly
            # 查找生成的文件
            local report_file=$(find_latest_weekly_report)
            # 推送到钉钉
            python -m src.utils.dingtalk pushfile --filepath "$report_file" "${@:2}"
            ;;
            
        recent-report)
            local days="${2:-}"
            if [[ ! "$days" =~ ^[0-9]+$ ]]; then
                show_error "recent-report 需要一个数字类型的 days 参数"
            fi
            # 生成最近报告
            python -m src.utils.report_generator --mode recent --days "$days"
            # 查找生成的文件
            local report_file=$(find_latest_recent_report "$days")
            # 推送到钉钉
            python -m src.utils.dingtalk pushfile --filepath "$report_file" "${@:3}"
            ;;
            
        pushfile)
            # 直接文件推送
            python -m src.utils.dingtalk pushfile "${@:2}"
            ;;
            
        *)
            show_error "未知的 dingpush 子命令: $subcmd"
            ;;
    esac
}
```

## 数据模型

### 文章数据结构

```python
{
    "raw_content": str,           # 完整 markdown 内容
    "vendor": str,                # "aws" | "azure" | "gcp" | "huawei"
    "subcategory": str,           # "blog" | "whatsnew" | "updates" 等
    "original_filename": str,     # "YYYY_MM_DD_title.md"
    "source_info_for_llm": str,   # "来源: vendor/subcategory/date/filename"
    "original_url": str,          # 原始文章 URL 或 PLACEHOLDER_*
    "date_published": str         # "YYYY-MM-DD"
}
```

### 报告元数据

```python
{
    "report_type": str,           # "weekly" | "recent"
    "start_date": str,            # "YYYY-MM-DD"
    "end_date": str,              # "YYYY-MM-DD"
    "article_count": int,         # 处理的文章总数
    "generated_at": str,          # ISO 时间戳
    "output_path": str            # 保存的报告路径
}
```

## 配置变更

### reporting.yaml 更新

```yaml
reporting:
  # 报告生成设置
  report_generator:
    weekly_prompt_key: "weekly_updates"      # 周报的提示模板
    recent_prompt_key: "weekly_updates"      # 最近报告使用相同提示
    model_profile: "deepseek_chat"           # 使用的 AI 模型
    
  # 输出路径
  output_paths:
    reports_dir: "data/reports"
    weekly_filename_pattern: "weekly_report_{start_date}_to_{end_date}.md"
    recent_filename_pattern: "recent_{days}_days_report_{end_date}.md"
    
  # 报告格式化
  beautification:
    banner_url: "https://example.com/banner.png"
    report_title_prefix: "【云技术周报】"
    recent_title_prefix: "【云技术动态】"
    intro_text: "汇集本周主要云厂商的技术产品动态，助您快速掌握核心变化。"
    recent_intro_text: "汇集近期主要云厂商的技术产品动态，助您快速掌握核心变化。"
    # ... 其他格式化选项
```

## 错误处理

### 报告生成错误

1. **未找到文章**: 生成包含"无更新"消息的报告
2. **LLM API 失败**: 记录错误，使用后备文本，继续生成报告
3. **文件写入失败**: 记录错误，返回 None，中止推送
4. **无效日期范围**: 验证日期，显示错误，退出

### 钉钉推送错误

1. **文件未找到**: 显示清晰的错误消息和预期路径
2. **空文件**: 警告用户，可选择发送关于空内容的通知
3. **机器人配置缺失**: 显示错误，列出可用机器人
4. **网络失败**: 使用指数退避重试（现有行为）

### CLI 参数错误

1. **缺少 days 参数**: 显示错误和使用示例
2. **无效的 days 值**: 显示错误，要求正整数
3. **未知子命令**: 显示错误，列出有效子命令
4. **缺少 filepath**: 显示错误和使用示例

## 测试策略

### 单元测试

1. **ReportGenerator 类**:
   - 测试 weekly 模式的日期范围计算
   - 测试 recent 模式的日期范围计算
   - 测试各种日期范围的文章收集
   - 测试 URL 替换逻辑
   - 测试报告格式化

2. **dingtalk.py**:
   - 测试 send_report_file() 使用有效文件
   - 测试 send_report_file() 使用缺失文件
   - 测试机器人选择逻辑
   - 测试配置加载

### 集成测试

1. **端到端报告生成**:
   - 使用真实数据生成周报
   - 使用真实数据生成最近 7 天报告
   - 验证输出文件格式和内容

2. **端到端推送流程**:
   - 生成报告 → 推送到测试机器人
   - 验证在钉钉中收到消息
   - 测试多个机器人

### 手动测试

1. 测试所有 run.sh dingpush 子命令
2. 验证帮助文本准确性
3. 测试无效输入的错误消息
4. 验证钉钉应用中的报告格式

## 迁移说明

### 破坏性变更

1. **移除的 CLI 命令**:
   - `./run.sh dingpush weekly` → 使用 `./run.sh dingpush weekly-report`
   - `./run.sh dingpush daily` → 无替代（已弃用）
   - `./run.sh dingpush recent N` → 使用 `./run.sh dingpush recent-report N`

2. **重命名的 Python 模块**:
   - `scripts/generate_weekly_report.py` → `src/utils/report_generator.py`

3. **移除的 Python API**:
   - `DingTalkNotifier.send_weekly_updates()` → 无替代
   - `DingTalkNotifier.send_daily_updates()` → 无替代
   - `DingTalkNotifier.send_recently_updates()` → 无替代

### 迁移路径

对于当前使用旧命令的用户:

```bash
# 旧: ./run.sh dingpush weekly
# 新: ./run.sh dingpush weekly-report

# 旧: ./run.sh dingpush recent 7
# 新: ./run.sh dingpush recent-report 7

# 旧: 直接 Python 调用 send_weekly_updates()
# 新: 生成报告文件，然后使用 send_report_file()
```

## 性能考虑

1. **LLM API 调用**: 对所有文章进行单次批量调用（现有行为）
2. **文件 I/O**: 最小化 - 读取文章一次，写入报告一次
3. **日期过滤**: 在读取内容之前基于文件名的高效过滤
4. **内存使用**: 将日期范围内的所有文章加载到内存中（对于典型数量可接受）

## 安全考虑

1. **配置文件**: 确保机密信息（webhook URL、API 密钥）保留在 config.secret.yaml 中
2. **文件路径**: 验证所有文件路径以防止目录遍历
3. **URL 替换**: 清理 URL 以防止注入攻击
4. **LLM 输入**: 没有用户控制的输入进入 LLM（仅文章内容）
