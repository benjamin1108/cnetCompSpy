---
inclusion: manual
---
# 元数据架构

## 概述

项目使用两类核心元数据文件来管理爬虫抓取的内容和AI分析的状态。这些元数据由 `src/utils/metadata_manager.py` 模块集中管理，并辅以 `src/utils/metadata_utils.py` 中的通用函数进行读写操作。元数据的重建和校验逻辑主要在 `src/utils/rebuild_metadata.py` 中实现。

## 核心组件

1.  **`MetadataManager` (在 `src/utils/metadata_manager.py`)**
    *   **职责**: 作为元数据操作的统一入口，负责加载、管理、更新和保存爬虫元数据及分析元数据。
    *   **线程安全**: 内部实现多层次的 `threading.RLock` 来保证对内存中元数据和文件I/O操作的线程安全。包括针对不同元数据文件（爬虫/分析）的锁，以及针对爬虫元数据中不同 `vendor` 和 `source_type` 的细粒度锁。
    *   **主要功能**:
        *   初始化时加载现有元数据文件。
        *   提供获取和更新特定条目或整个元数据块的方法（如 `get_crawler_metadata`, `update_crawler_metadata_entry`, `update_analysis_metadata`）。
        *   支持批量更新爬虫元数据 (`update_crawler_metadata_entries_batch`) 以提高效率。
        *   提供辅助方法，如根据文件路径获取爬虫元数据、获取指定厂商和类型的文件列表等。
        *   包含旧版元数据迁移逻辑 (`migrate_legacy_metadata`)。

2.  **`metadata_utils.py`**
    *   **`load_metadata(file_path, lock, ...)`**: 通用的元数据加载函数，支持线程锁。
    *   **`save_metadata(file_path, metadata, lock, ...)`**: 通用的元数据保存函数。通过先写入临时文件然后使用 `os.replace()` 进行重命名的方式，确保文件保存的原子性，防止数据损坏。支持线程锁。

## 元数据文件及结构

元数据文件默认存储在项目根目录下的 `data/metadata/` 路径中。

### 1. 爬虫元数据 (`crawler_metadata.json`)

*   **用途**: 记录爬虫抓取到的所有原始内容的信息。
*   **结构**:
    ```json
    {
      "aws": { // 厂商 (vendor)
        "blog": { // 来源类型 (source_type)
          "https://aws.amazon.com/blogs/aws/new-feature-x": { // URL 或文件路径作为键
            "title": "AWS Announces New Feature X",
            "url": "https://aws.amazon.com/blogs/aws/new-feature-x",
            "crawl_time": "2023-01-15T08:45:30.123456", // ISO 8601 格式
            "filepath": "data/raw/aws/blog/2023_01_15_abcdef12.md", // 对应存储的原始文件路径 (相对项目根目录)
            "vendor": "aws", // 小写
            "source_type": "blog" // 小写
          }
          // ... more URLs for this vendor/type
        }
        // ... more source_types for this vendor
      }
      // ... more vendors
    }
    ```
*   **关键字段**:
    *   `title`: 文章原始标题。
    *   `url`: 文章原始URL。
    *   `crawl_time`: 抓取时的精确时间，ISO 8601 格式 (由 `datetime.now().isoformat()` 生成)。
    *   `filepath`: 抓取的原始内容存储的相对路径。
    *   `vendor`: 内容所属厂商 (小写, e.g., "aws", "azure")。
    *   `source_type`: 内容来源类型 (小写, e.g., "blog", "docs")。

### 2. 分析元数据 (`analysis_metadata.json`)

*   **用途**: 记录对原始文件（通常是 `.md` 文件）进行AI分析处理的状态和结果。
*   **结构**:
    ```json
    {
      "data/raw/aws/blog/2023_01_15_abcdef12.md": { // 键是对应 *原始文件* 的相对路径
        "file": "data/raw/aws/blog/2023_01_15_abcdef12.md", // 再次存储原始文件相对路径
        "last_analyzed": "2023-01-16T10:30:45", // YYYY-MM-DD HH:MM:SS 格式 (注意: rebuild_metadata.py生成的是HH:MM:SS)
        "publish_date": "2023-01-15", // YYYY-MM-DD 格式, 从分析内容或原始文件提取
        "tasks": {
          "AI标题翻译": {
            "success": true,
            "error": null,
            "timestamp": "2023-01-16T10:28:15" // YYYY-MM-DD HH:MM:SS 格式
          },
          "AI竞争分析": {
            "success": false,
            "error": "API call failed due to timeout.",
            "timestamp": "2023-01-16T10:29:32" // YYYY-MM-DD HH:MM:SS 格式
          }
          // ... 其他 AI 任务
        },
        "info": {
          "title": "AWS Announces New Feature X", // 原始标题 (来自 crawler_metadata)
          "original_url": "https://aws.amazon.com/blogs/aws/new-feature-x", // 原始URL (来自 crawler_metadata)
          "crawl_time": "2023-01-15T08:45:30.123456", // 原始抓取时间 (来自 crawler_metadata, ISO 格式)
          "vendor": "aws", // 大写 (rebuild_metadata.py 倾向于大写)
          "type": "blog",  // 大写 (rebuild_metadata.py 倾向于大写)
          "chinese_title": "AWS宣布新功能X", // 从 "AI标题翻译" 任务提取的中文标题
          "update_type": "新功能", // 从 "AI标题翻译" 任务提取的更新类型 (如：[新功能], [解决方案])
          "publish_date": "2023-01-15", // YYYY-MM-DD 格式 (可能与顶层 publish_date 重复)
          "file": "data/raw/aws/blog/2023_01_15_abcdef12.md" // 原始文件路径，与主键相同
        },
        "processed": false // 标记所有必需的AI任务是否都已成功完成
      }
      // ... more files
    }
    ```
*   **关键字段**:
    *   `file`: (顶层和 `info` 块内) 对应的原始文件相对路径，作为此记录的主要标识。
    *   `last_analyzed`: 最后一次对此文件进行分析操作的时间戳 (`YYYY-MM-DD HH:MM:SS`)。
    *   `publish_date`: (顶层和 `info` 块内) 从文件内容中提取的发布日期 (`YYYY-MM-DD`)。优先级：分析文件AI翻译块 -> 原始文件内容 -> crawl_time。
    *   `tasks`: 一个字典，记录各个AI分析任务的状态。
        *   `task_name`: (e.g., "AI标题翻译", "AI全文翻译", "AI竞争分析")
            *   `success`: `boolean`, 任务是否成功。
            *   `error`: `string | null`, 如果失败，记录错误信息。
            *   `timestamp`: `string`, 任务执行的时间戳 (`YYYY-MM-DD HH:MM:SS`)。
    *   `info`: 包含有关原始文件的综合信息。
        *   `title`: 原始英文标题。
        *   `original_url`: 原始链接。
        *   `crawl_time`: 原始抓取时间 (ISO 格式)。
        *   `vendor`: 所属厂商 (通常大写，如 "AWS")。
        *   `type`: 内容类型 (通常大写，如 "BLOG")。
        *   `chinese_title`: 由 "AI标题翻译" 任务生成的中文标题（不含类别标签）。
        *   `update_type`: 由 "AI标题翻译" 任务生成的类别标签 (如 "新产品/新功能", "解决方案")。
    *   `processed`: `boolean`, 指示是否所有必需的AI分析任务都已成功完成。

## 线程安全机制

*   **锁管理**: `MetadataManager` 使用 `threading.RLock` 实现多层次的锁机制：
    1.  **类级别文件锁 (`_file_locks`)**: 每个元数据文件（`crawler_metadata.json`, `analysis_metadata.json`）在进行磁盘I/O时，会由各自的类级别锁保护，防止多实例或多线程并发写文件冲突。
    2.  **实例级别内存锁**: `crawler_lock` 和 `analysis_lock` 用于保护内存中 `self.crawler_metadata` 和 `self.analysis_metadata` 字典的并发访问。
    3.  **细粒度爬虫锁 (`crawler_vendor_locks`)**: 为了提高爬虫元数据操作的并发性，为每个 `vendor` 下的每个 `source_type` 维护一个独立的锁。这允许对不同厂商/类型的数据进行并发修改，减少锁争用。
*   **原子写入**: `src/utils/metadata_utils.py` 中的 `save_metadata` 函数通过先写入临时文件，然后调用 `os.replace()`（原子操作）来替换旧文件，确保了文件保存的原子性，防止因写入中断导致元数据文件损坏。

## 关键操作流程

### 1. 文件抓取 (Crawlers)

*   **执行者**: `src/crawlers/` 目录下的各厂商和类型的爬虫模块。
*   **目标**: 从外部源获取最新内容，存储为本地文件，并记录抓取元数据。
*   **与 `MetadataManager` 的交互**:
    1.  **检查重复抓取 (可选但推荐)**:
        *   在尝试抓取一个URL之前，爬虫可以调用 `metadata_manager.get_crawler_metadata(vendor, source_type)` 来获取特定厂商和来源的已有抓取记录。
        *   通过检查返回的字典中是否存在该URL，以及其 `crawl_time` 是否在可接受的时间范围内（例如，避免在短时间内重复抓取同一内容），来决定是否跳过本次抓取。
        *   **方法示例**: `existing_metadata = metadata_manager.get_crawler_metadata(vendor='aws', source_type='blog')`
                      `if url in existing_metadata and is_recent(existing_metadata[url]['crawl_time']): continue`
    2.  **内容抓取与存储**:
        *   如果决定抓取，爬虫下载内容并将其保存为 `.md` 文件到项目的 `data/raw/{vendor}/{source_type}/` 目录下。文件名通常包含日期和内容的唯一标识符。
    3.  **记录抓取元数据**:
        *   成功保存文件后，爬虫必须更新 `crawler_metadata.json`。
        *   **单个文件更新**: 调用 `metadata_manager.update_crawler_metadata_entry(vendor, source_type, url, data, batch=False)`。
            *   `vendor`: 爬虫对应的厂商名 (小写)。
            *   `source_type`: 爬虫对应的来源类型 (小写)。
            *   `url`: 被抓取内容的原始URL。
            *   `data`: 一个字典，包含：
                *   `title`: 文章原始标题。
                *   `url`: 文章原始URL (与键一致或更规范化)。
                *   `crawl_time`: `datetime.now().isoformat()` 生成的当前时间戳。
                *   `filepath`: 保存的 `.md` 文件的相对路径 (e.g., `data/raw/aws/blog/2023-01-01_feature_x.md`)。
                *   `vendor`: 厂商名 (小写)。
                *   `source_type`: 来源类型 (小写)。
        *   **批量文件更新 (推荐)**: 如果一个爬虫任务一次性抓取了多个文件，应使用 `metadata_manager.update_crawler_metadata_entries_batch(vendor, source_type, entries)`。
            *   `entries`: 一个字典，键为URL，值为上述 `data` 字典。这样可以减少文件I/O次数，提高效率。
    4.  **创建对应的分析文件占位符 (推荐)**:
        *   为了后续AI分析流程的统一性，爬虫在成功抓取并记录元数据后，可以考虑在 `data/analysis/{vendor}/{source_type}/` 目录下创建一个与原始文件同名的空 `.md` 文件，或者一个包含基本结构（如原始文件路径链接、AI任务占位符注释块）的分析文件模板。
        *   这一步有助于 `rebuild_metadata.py` 脚本更好地识别和初始化分析元数据，即使AI分析尚未开始。

### 2. AI分析 (AI Analyzer)

*   **执行者**: `src/ai_analyzer/analyzer.py` 及其相关的 `pipeline` 和 `clients` 模块。
*   **目标**: 对 `data/analysis/` 目录下的文件执行一系列AI任务（如翻译、摘要、情感分析等），并将结果写回分析文件，同时更新分析元数据。
*   **与 `MetadataManager` 的交互**:
    1.  **获取待分析文件列表与状态**:
        *   AI分析器首先需要确定哪些文件需要处理。它可以调用 `metadata_manager.get_all_analysis_metadata()` 获取所有分析元数据。
        *   遍历这些元数据，检查每个文件条目的 `processed` 标志，或者特定任务（如 `tasks['AI标题翻译']['success']`）的状态，来决定是否需要对该文件执行某个或某些AI任务。
        *   或者，直接扫描 `data/analysis/` 目录，然后对每个文件调用 `metadata_manager.get_analysis_metadata(raw_file_path)` 获取其当前状态。(`raw_file_path` 需要从分析文件路径转换得到，例如 `analysis_filepath.replace('/analysis/', '/raw/')`)
    2.  **获取上下文信息**:
        *   在对一个分析文件（例如 `data/analysis/aws/blog/some_file.md`）执行AI任务前，通常需要原始文件的上下文信息。
        *   分析器使用对应的原始文件路径 (`raw_file_path = 'data/raw/aws/blog/some_file.md'`) 调用 `metadata_manager.get_crawler_metadata_by_filepath(raw_file_path)` 来获取其在 `crawler_metadata.json` 中的条目。
        *   这将返回包含原始 `title`, `original_url`, `crawl_time`, `vendor`, `source_type` 的字典。这些信息将用于填充 `analysis_metadata.json` 中对应条目的 `info` 块。
    3.  **执行AI任务并更新分析文件**:
        *   AI分析器调用相应的AI模型（通过 `src/ai_analyzer/clients/` 和 `src/ai_analyzer/model_manager.py`）对分析文件内容或其引用的原始文件内容执行任务。
        *   任务结果（如翻译后的文本、分析报告）会被写回到分析文件（`data/analysis/.../some_file.md`）中预定义的AI任务块内 (e.g., `<!-- AI_TASK_START: AI全文翻译 --> ... <!-- AI_TASK_END: AI全文翻译 -->`)。如果任务失败，错误信息也会被记录在这些块中。
    4.  **更新分析元数据**:
        *   在AI任务完成（成功或失败）后，分析器必须更新 `analysis_metadata.json`。
        *   调用 `metadata_manager.update_analysis_metadata(raw_file_path, update_data)`。
            *   `raw_file_path`: 对应**原始文件**的相对路径，作为 `analysis_metadata.json` 的键。
            *   `update_data`: 一个字典，包含需要更新的字段。通常结构如下：
                ```python
                current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Fetch existing analysis data first to preserve other task states and info
                existing_analysis_data = metadata_manager.get_analysis_metadata(raw_file_path)
                
                # Initialize info from crawler_metadata if not already well-populated
                if not existing_analysis_data.get('info', {}).get('original_url'):
                    crawler_entry = metadata_manager.get_crawler_metadata_by_filepath(raw_file_path)
                    existing_analysis_data['info'] = {
                        'title': crawler_entry.get('title', ''),
                        'original_url': crawler_entry.get('url', ''),
                        'crawl_time': crawler_entry.get('crawl_time', ''),
                        'vendor': crawler_entry.get('vendor', '').upper(),
                        'type': crawler_entry.get('source_type', '').upper(),
                        'file': raw_file_path
                        # chinese_title, update_type, publish_date will be added/updated next
                    }

                update_data = {
                    'tasks': existing_analysis_data.get('tasks', {}), # Preserve other tasks
                    'info': existing_analysis_data.get('info', {}),   # Preserve existing info
                    'last_analyzed': current_time_str
                }

                # Update specific task status
                update_data['tasks']['AI标题翻译'] = {
                    'success': True, # or False
                    'error': None, # or error message string
                    'timestamp': current_time_str 
                }
                
                # Update info based on AI task results
                if update_data['tasks']['AI标题翻译']['success']:
                    # (Assuming title_block_content is extracted from the analysis file)
                    # update_type, pure_chinese_title = parse_title_block(title_block_content)
                    update_data['info']['update_type'] = update_type 
                    update_data['info']['chinese_title'] = pure_chinese_title
                
                # Update publish_date (can be from translation block or raw file)
                # update_data['info']['publish_date'] = extracted_publish_date
                # update_data['publish_date'] = extracted_publish_date # Top level for compatibility

                # Determine overall 'processed' status
                all_required_tasks_done = True
                # for task_name in REQUIRED_AI_TASKS:
                #     if not update_data['tasks'].get(task_name, {}).get('success'):
                #         all_required_tasks_done = False
                #         break
                update_data['processed'] = all_required_tasks_done
                ```
        *   **注意**: 在更新时，应先获取已有的分析元数据，然后只修改相关的任务状态和 `info` 字段，避免覆盖其他任务的信息或重要的已有 `info` 数据。`rebuild_metadata.py` 中的逻辑可作为如何构造 `update_data` 的参考。

## 日期和路径格式约定

*   **`crawler_metadata.json`**:
    *   `crawl_time`: ISO 8601 字符串 (e.g., `YYYY-MM-DDTHH:MM:SS.ffffff`)。
*   **`analysis_metadata.json`**:
    *   `last_analyzed`: `YYYY-MM-DD HH:MM:SS`。
    *   `tasks.{task_name}.timestamp`: `YYYY-MM-DD HH:MM:SS`。
    *   `publish_date` (顶层及 `info` 块内): `YYYY-MM-DD`。
    *   `info.crawl_time`: ISO 8601 字符串 (与 `crawler_metadata.crawl_time` 一致)。
*   **文件路径**: 在 `analysis_metadata.json` 中，主键和 `info.file` 字段存储的路径是相对于项目根目录的**原始文件**路径 (e.g., `data/raw/aws/blog/file.md`)。`MetadataManager` 内部使用 `os.path.relpath()` 进行路径规范化。

## 维护与校验

*   `rebuild_metadata.py` 脚本是主要的维护和校验工具。它能够：
    *   从物理文件重新生成元数据。
    *   识别并处理（记录或删除）不完整、无效或孤立的元数据条目和对应的分析文件。
    *   通过深度内容检查来识别AI任务的"假完成"情况。
*   日志记录: 详细的日志（通过 `utils.colored_logger`）记录了元数据操作和重建过程中的活动和问题。
