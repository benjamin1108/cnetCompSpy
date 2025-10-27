# 分析文件Metadata格式说明

## 概述

本文档描述了AI分析器生成的分析文件的metadata格式规范。

## 文件结构

分析文件采用Markdown格式，结构如下：

```markdown
**发布时间:** YYYY-MM-DD

**厂商:** VENDOR_NAME

**类型:** TYPE

**原始链接:** URL

---

<!-- AI_TASK_START: AI标题翻译 -->
翻译后的标题
<!-- AI_TASK_END: AI标题翻译 -->

<!-- AI_TASK_START: AI竞争分析 -->
分析内容...
<!-- AI_TASK_END: AI竞争分析 -->

<!-- AI_TASK_START: AI全文翻译 -->
翻译内容...
<!-- AI_TASK_END: AI全文翻译 -->
```

## Metadata字段

### 必需字段

1. **发布时间** (publish_date)
   - 格式：`YYYY-MM-DD`
   - 示例：`2025-10-13`
   - 说明：文档的发布日期

2. **厂商** (vendor)
   - 格式：大写字母
   - 示例：`AWS`, `AZURE`, `GCP`, `HUAWEI`
   - 说明：云服务提供商名称

3. **类型** (type)
   - 格式：大写字母
   - 示例：`BLOG`, `WHATSNEW`, `ANNOUNCEMENT`
   - 说明：文档类型

4. **原始链接** (original_url)
   - 格式：完整URL
   - 示例：`https://aws.amazon.com/blogs/...`
   - 说明：原始文档的URL地址

### 可选字段

- **作者** (author)：文档作者（如果有）

## 格式规范

1. **字段格式**：使用Markdown粗体格式 `**字段名:** 值`
2. **字段顺序**：按照发布时间、厂商、类型、原始链接的顺序排列
3. **分隔线**：metadata块后必须有`---`分隔线
4. **空行**：每个字段后有一个空行，分隔线后有一个空行

## AI任务标记

AI任务结果使用HTML注释标记包裹：

```markdown
<!-- AI_TASK_START: 任务名称 -->
任务结果内容
<!-- AI_TASK_END: 任务名称 -->
```

### 标准任务

1. **AI标题翻译**：将原始标题翻译为中文，并添加分类标签
2. **AI竞争分析**：对文档内容进行竞争分析
3. **AI全文翻译**：将整篇文档翻译为中文

## 示例

```markdown
**发布时间:** 2025-10-13

**厂商:** AWS

**类型:** BLOG

**原始链接:** https://aws.amazon.com/blogs/networking-and-content-delivery/secure-customer-resource-access-in-multi-tenant-saas-with-amazon-vpc-lattice/

---

<!-- AI_TASK_START: AI标题翻译 -->
[解决方案] 使用 Amazon VPC Lattice 安全访问多租户 SaaS 中的客户资源
<!-- AI_TASK_END: AI标题翻译 -->

<!-- AI_TASK_START: AI竞争分析 -->
# 解决方案分析
## 解决方案概述
...
<!-- AI_TASK_END: AI竞争分析 -->
```

## 迁移说明

如果需要将旧格式的分析文件转换为新格式，可以使用迁移脚本：

```bash
# Dry-run模式（只显示不修改）
python scripts/migrate_analysis_metadata.py --dry-run

# 实际执行迁移
python scripts/migrate_analysis_metadata.py
```

## 相关文件

- 生成逻辑：`src/ai_analyzer/pipeline/stages/analysis_execution_stage.py`
- 读取逻辑：`src/web_server/document_manager.py`
- 迁移脚本：`scripts/migrate_analysis_metadata.py`
