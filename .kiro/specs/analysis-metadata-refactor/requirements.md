# 需求文档：分析文件Metadata重构

## 简介

本需求旨在重构分析文件中metadata的存储位置和格式。当前metadata信息嵌入在分析文件的全文翻译部分（通过AI_TASK标记），导致后续提取和使用不便。需要将metadata统一放置在分析文件的头部，并更新所有相关的读写和展示逻辑。

## 术语表

- **Analysis File (分析文件)**: AI分析器生成的markdown文件，包含对原始文档的AI分析结果
- **Metadata (元数据)**: 描述文档的结构化信息，包括发布时间、厂商、类型、原始链接等
- **AI_TASK标记**: 用于标识AI任务结果的HTML注释标记，格式为`<!-- AI_TASK_START: 任务名 -->`和`<!-- AI_TASK_END: 任务名 -->`
- **AnalysisExecutionStage (分析执行阶段)**: AI分析流水线中负责执行分析任务并写入结果的阶段
- **DocumentManager (文档管理器)**: Web服务器中负责读取和展示文档的模块
- **MetadataManager (元数据管理器)**: 负责管理analysis_metadata.json文件的模块

## 需求

### 需求 1：Metadata格式标准化

**用户故事:** 作为系统维护者，我希望分析文件的metadata采用统一的格式存储在文件头部，以便于解析和维护。

#### 验收标准

1. WHEN 生成新的分析文件时，THE AnalysisExecutionStage SHALL 将metadata以标准格式写入文件头部
2. THE metadata格式 SHALL 包含以下字段：发布时间(publish_date)、厂商(vendor)、类型(type)、原始链接(original_url)
3. THE metadata格式 SHALL 使用markdown粗体格式（`**字段名:** 值`）
4. THE metadata块 SHALL 以水平分隔线(`---`)结束
5. THE metadata块 SHALL 位于所有AI_TASK标记之前

### 需求 2：分析文件写入逻辑更新

**用户故事:** 作为AI分析器，我需要在生成分析文件时将metadata写入正确的位置，确保文件结构清晰。

#### 验收标准

1. WHEN AnalysisExecutionStage执行文件分析时，THE System SHALL 首先写入metadata块到文件头部
2. WHEN 写入metadata时，THE System SHALL 从原始文件的embedded_metadata中提取信息
3. WHEN metadata写入完成后，THE System SHALL 写入水平分隔线
4. WHEN 执行AI任务时，THE System SHALL 在metadata块之后写入AI_TASK标记和结果
5. IF embedded_metadata中缺少某个字段，THEN THE System SHALL 跳过该字段的写入

### 需求 3：Metadata提取逻辑更新

**用户故事:** 作为文档管理器，我需要能够从分析文件头部正确提取metadata，以便在前端展示。

#### 验收标准

1. WHEN DocumentManager读取分析文件时，THE System SHALL 从文件头部提取metadata
2. THE System SHALL 支持提取以下字段：发布时间、厂商、类型、原始链接
3. THE System SHALL 正确处理中英文冒号（`:` 和 `：`）
4. THE System SHALL 正确处理带星号和不带星号的字段格式
5. WHEN metadata提取失败时，THE System SHALL 记录错误并返回空值

### 需求 4：前端展示逻辑简化

**用户故事:** 作为Web服务器用户，我希望前端能够正确展示重构后的分析文件，不影响现有功能。

#### 验收标准

1. WHEN 前端请求分析文档时，THE DocumentManager SHALL 从文件头部提取并返回metadata
2. THE 前端展示 SHALL 保持与重构前一致的用户体验
3. THE System SHALL 移除所有处理旧格式的代码逻辑
4. THE DocumentManager SHALL 简化metadata提取逻辑，仅从文件头部读取

### 需求 5：元数据管理器集成

**用户故事:** 作为元数据管理系统，我需要确保analysis_metadata.json中的信息与分析文件头部的metadata保持一致。

#### 验收标准

1. WHEN 分析文件生成时，THE System SHALL 同时更新analysis_metadata.json
2. THE analysis_metadata.json SHALL 包含与文件头部metadata相同的信息
3. THE System SHALL 使用MetadataManager的线程安全机制更新元数据
4. WHEN 提取到中文标题时，THE System SHALL 将其保存到metadata的info.chinese_title字段
5. WHEN 提取到update_type时，THE System SHALL 将其保存到metadata的info.update_type字段

### 需求 6：旧格式迁移脚本

**用户故事:** 作为系统管理员，我需要一个迁移脚本将所有旧格式的分析文件批量转换为新格式，确保系统完全使用统一的metadata格式。

#### 验收标准

1. THE System SHALL 提供一个独立的迁移脚本（migrate_analysis_metadata.py）
2. WHEN 执行迁移脚本时，THE Script SHALL 扫描所有分析文件目录
3. THE Script SHALL 识别旧格式文件（metadata在文件内容中而非头部）
4. WHEN 处理旧格式文件时，THE Script SHALL 提取现有的metadata信息
5. THE Script SHALL 将metadata重新格式化并写入文件头部
6. THE Script SHALL 保留所有AI_TASK标记和内容不变
7. THE Script SHALL 创建备份文件（.bak后缀）在修改原文件之前
8. THE Script SHALL 记录迁移统计信息（成功、失败、跳过的文件数）
9. THE Script SHALL 支持dry-run模式，仅显示将要修改的文件而不实际修改
10. WHEN 迁移失败时，THE Script SHALL 记录错误并继续处理其他文件

### 需求 7：日志和错误处理

**用户故事:** 作为开发者，我需要清晰的日志来追踪metadata的提取和写入过程，便于调试和维护。

#### 验收标准

1. WHEN 写入metadata时，THE System SHALL 记录debug级别的日志
2. WHEN metadata提取失败时，THE System SHALL 记录warning级别的日志
3. THE 日志 SHALL 包含文件路径和具体的错误信息
4. THE System SHALL 使用统一的colored_logger模块记录日志
5. WHEN 发生异常时，THE System SHALL 不中断整个分析流程，而是记录错误并继续
