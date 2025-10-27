# 需求文档

## 简介

本规范定义了钉钉通知系统的重构，旨在精简推送模式并改进代码组织。当前系统有多个过时的推送模式（weekly、daily）已不再使用，而 weekly_report 模式是首选格式。此次重构将整合系统，对所有时间范围统一使用基于报告的格式。

## 术语表

- **钉钉系统**: 向钉钉消息平台发送格式化报告的通知系统
- **报告生成器**: 负责从文章数据生成 markdown 报告的模块
- **推送模式**: 发送的通知类型（例如：周报、最近 N 天报告）
- **文章数据**: 来自云厂商博客文章和更新的原始内容和元数据
- **内部链接**: 指向每篇文章的内部分析平台的 URL

## 需求

### 需求 1: 移除过时的推送模式

**用户故事:** 作为系统维护者，我希望移除未使用的推送模式，以便代码库更清晰、更易于维护

#### 验收标准

1. WHEN 钉钉系统被调用时，THE 钉钉系统 SHALL NOT 支持 weekly 推送模式
2. WHEN 钉钉系统被调用时，THE 钉钉系统 SHALL NOT 支持 daily 推送模式
3. WHEN 钉钉系统代码被审查时，THE 钉钉系统 SHALL NOT 包含 send_weekly_updates 或 send_daily_updates 方法
4. WHEN run.sh 帮助信息被显示时，THE run.sh SHALL NOT 列出 weekly 或 daily 作为可用的 dingpush 子命令

### 需求 2: 将 Recent 模式重构为报告格式

**用户故事:** 作为用户，我希望最近 N 天推送使用与 weekly_report 相同的高质量报告格式，以便所有通知保持一致和专业

#### 验收标准

1. WHEN 钉钉系统收到带有 N 天的 recent 推送请求时，THE 钉钉系统 SHALL 使用报告生成器生成综合报告
2. WHEN 报告生成器处理最近 N 天数据时，THE 报告生成器 SHALL 为每篇文章包含 AI 生成的摘要
3. WHEN 报告生成器创建 recent 报告时，THE 报告生成器 SHALL 将原始文章 URL 替换为内部链接 URL
4. WHEN recent 报告被发送时，THE 钉钉系统 SHALL 使用与周报相同的样式格式化消息
5. WHEN recent 命令在没有 days 参数的情况下被调用时，THE 钉钉系统 SHALL 显示错误消息，指示需要 days 参数

### 需求 3: 通用化报告生成器模块

**用户故事:** 作为开发者，我希望报告生成器是一个可重用的模块，以便它可以为任何时间范围生成报告而无需代码重复

#### 验收标准

1. WHEN 报告生成器被初始化时，THE 报告生成器 SHALL 接受时间范围参数（start_date 和 end_date）
2. WHEN 报告生成器收集文章时，THE 报告生成器 SHALL 根据提供的时间范围过滤文章
3. WHEN 报告生成器被调用生成周报时，THE 报告生成器 SHALL 自动计算当前周的日期范围
4. WHEN 报告生成器被调用生成最近 N 天报告时，THE 报告生成器 SHALL 将日期范围计算为（今天 - N 天）到今天
5. WHEN 报告生成器生成输出时，THE 报告生成器 SHALL 使用一致的格式，无论时间范围类型如何

### 需求 4: 适当重命名组件

**用户故事:** 作为开发者，我希望所有组件都有清晰、描述性的名称，以便代码自文档化且易于理解

#### 验收标准

1. WHEN generate_weekly_report.py 文件被审查时，THE 文件 SHALL 被重命名为 report_generator.py
2. WHEN 钉钉系统方法被审查时，THE 方法名称 SHALL 清楚地表明它们发送报告（而不是原始更新）
3. WHEN run.sh dingpush 子命令被列出时，THE 子命令 SHALL 使用清晰的名称，如 "weekly-report" 和 "recent-report"
4. WHEN 配置键被审查时，THE 配置键 SHALL 使用一致的命名约定（例如 report_prompt_key 而不是 weekly_update_prompt_key）

### 需求 5: 更新 Run.sh 帮助系统

**用户故事:** 作为用户，我希望有全面准确的帮助文档，以便我能正确理解如何使用 dingpush 命令

#### 验收标准

1. WHEN 用户运行 "./run.sh help" 时，THE run.sh SHALL 显示更新的 dingpush 命令文档
2. WHEN 用户运行 "./run.sh dingpush --help" 时，THE run.sh SHALL 显示所有可用的子命令及其选项
3. WHEN 帮助文本被显示时，THE 帮助文本 SHALL 包含 weekly-report 和 recent-report 使用的示例
4. WHEN 帮助文本描述 recent-report 时，THE 帮助文本 SHALL 清楚地指示需要 days 参数
5. WHEN 帮助文本被显示时，THE 帮助文本 SHALL NOT 提及已弃用的 weekly 或 daily 模式

### 需求 6: 保持 Pushfile 功能

**用户故事:** 作为用户，我希望继续使用 pushfile 命令发送任意 markdown 文件，以便我在发送到钉钉时有灵活性

#### 验收标准

1. WHEN 钉钉系统收到 pushfile 命令时，THE 钉钉系统 SHALL 读取指定的 markdown 文件
2. WHEN pushfile 命令被执行时，THE 钉钉系统 SHALL 将文件内容发送到配置的钉钉机器人
3. WHEN pushfile 命令被使用时，THE 钉钉系统 SHALL 支持 --robot 选项以指定目标机器人
4. WHEN pushfile 命令被使用时，THE 钉钉系统 SHALL 支持 --config 选项以指定自定义配置文件
