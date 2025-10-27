# 设计文档：分析文件Metadata重构

## 概述

本设计文档描述了如何重构分析文件中metadata的存储位置和格式。当前系统将metadata信息嵌入在分析文件的AI_TASK标记内容中（特别是AI全文翻译部分），导致提取复杂且效率低下。新设计将metadata统一放置在文件头部，采用标准化格式，并提供迁移脚本将所有旧文件转换为新格式。

## 架构

### 当前架构问题

1. **Metadata位置分散**：
   - 发布时间、厂商、类型等信息嵌入在AI全文翻译任务块中
   - 需要解析AI_TASK标记才能提取metadata
   - DocumentManager需要复杂的正则表达式来提取信息

2. **代码复杂度高**：
   - `_extract_document_meta`方法需要读取大量文件内容（16KB）
   - 多个正则表达式模式匹配不同的日期格式
   - rebuild_metadata.py中有大量重复的解析逻辑

3. **维护困难**：
   - metadata格式不统一
   - 新增字段需要修改多处代码
   - 难以确保一致性

### 新架构设计

```
分析文件结构：
┌─────────────────────────────────────┐
│ **发布时间:** 2025-10-13            │  ← Metadata块（新增）
│ **厂商:** AWS                       │
│ **类型:** BLOG                      │
│ **原始链接:** https://...          │
│ ---                                 │  ← 分隔线
├─────────────────────────────────────┤
│ <!-- AI_TASK_START: AI标题翻译 --> │  ← AI任务块
│ [解决方案] 标题内容                 │
│ <!-- AI_TASK_END: AI标题翻译 -->   │
├─────────────────────────────────────┤
│ <!-- AI_TASK_START: AI竞争分析 --> │
│ 分析内容...                         │
│ <!-- AI_TASK_END: AI竞争分析 -->   │
└─────────────────────────────────────┘
```

## 组件和接口

### 1. AnalysisExecutionStage（分析执行阶段）

**职责**：生成分析文件时写入metadata到文件头部

**修改点**：
- `_process_single_file`方法中的文件写入逻辑
- 在打开输出文件后，首先写入metadata块
- 然后写入分隔线
- 最后写入各个AI任务块

**新增方法**：
```python
def _write_metadata_header(self, outfile, embedded_meta: Dict[str, Any]) -> None:
    """
    写入metadata头部到分析文件
    
    Args:
        outfile: 文件对象
        embedded_meta: 从原始文件提取的metadata字典
    """
    # 按顺序写入metadata字段
    if embedded_meta.get('publish_date'):
        outfile.write(f"**发布时间:** {embedded_meta['publish_date']}\n\n")
    if embedded_meta.get('vendor'):
        outfile.write(f"**厂商:** {embedded_meta['vendor']}\n\n")
    if embedded_meta.get('type'):
        outfile.write(f"**类型:** {embedded_meta['type']}\n\n")
    if embedded_meta.get('original_url'):
        outfile.write(f"**原始链接:** {embedded_meta['original_url']}\n\n")
    outfile.write("---\n\n")
    outfile.flush()
```

**修改后的写入流程**：
```python
with open(analysis_output_file_path, 'w', encoding='utf-8') as outfile:
    # 1. 写入metadata头部（新增）
    self._write_metadata_header(outfile, embedded_meta)
    
    # 2. 执行AI任务并写入结果
    for task_config in defined_tasks:
        # ... 执行任务
        outfile.write(f"\n<!-- AI_TASK_START: {task_type} -->\n")
        outfile.write(f"{cleaned_result}\n")
        outfile.write(f"<!-- AI_TASK_END: {task_type} -->\n\n")
```

### 2. DocumentManager（文档管理器）

**职责**：从分析文件头部提取metadata用于前端展示

**修改点**：
- 简化`_extract_document_meta`方法
- 移除从AI_TASK标记中提取metadata的逻辑
- 只从文件头部（前20行）提取metadata

**简化后的方法**：
```python
def _extract_document_meta(self, file_path: str) -> Dict[str, str]:
    """
    从文档头部提取元数据（简化版）
    
    Args:
        file_path: 文档路径
        
    Returns:
        文档元数据
    """
    meta = {
        'title': os.path.basename(file_path).replace('.md', '').replace('_', ' '),
        'date': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 只读取前20行，metadata应该在这里
            lines = [f.readline() for _ in range(20)]
            content = ''.join(lines)
        
        # 提取标题（从第一个#标题）
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            meta['title'] = title_match.group(1).strip()
        
        # 提取metadata字段（支持中英文冒号）
        patterns = {
            'date': r'\*\*发布时间[：:]\*\*\s*(.+)',
            'vendor': r'\*\*厂商[：:]\*\*\s*(.+)',
            'source_type': r'\*\*类型[：:]\*\*\s*(.+)',
            'author': r'\*\*作者[：:]\*\*\s*(.+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                value = match.group(1).strip()
                # 清理星号
                value = value.replace('**', '').strip()
                meta[key] = value
        
    except Exception as e:
        self.logger.error(f"提取文档元数据时出错: {e}")
    
    return meta
```

**移除的方法**：
- 删除所有从AI_TASK标记中提取metadata的逻辑
- 删除复杂的日期格式匹配逻辑（华为月度格式等）
- 删除从文件名提取日期的回退逻辑

### 3. rebuild_metadata.py（元数据重建脚本）

**职责**：从分析文件中提取metadata并更新analysis_metadata.json

**修改点**：
- 简化metadata提取逻辑
- 从文件头部读取metadata，不再从AI_TASK标记中提取
- 保留从AI标题翻译块提取中文标题的逻辑（这是必要的）

**简化后的提取逻辑**：
```python
def extract_metadata_from_analysis_file(filepath: str) -> Dict[str, Any]:
    """
    从分析文件头部提取metadata
    
    Args:
        filepath: 分析文件路径
        
    Returns:
        提取的metadata字典
    """
    metadata = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # 读取前20行
            lines = [f.readline() for _ in range(20)]
            header_content = ''.join(lines)
        
        # 提取metadata字段
        patterns = {
            'publish_date': r'\*\*发布时间[：:]\*\*\s*(.+)',
            'vendor': r'\*\*厂商[：:]\*\*\s*(.+)',
            'type': r'\*\*类型[：:]\*\*\s*(.+)',
            'original_url': r'\*\*原始链接[：:]\*\*\s*(.+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, header_content, re.MULTILINE)
            if match:
                value = match.group(1).strip()
                value = value.replace('**', '').strip()
                metadata[key] = value
        
        return metadata
        
    except Exception as e:
        logger.error(f"从分析文件提取metadata失败: {filepath} - {e}")
        return {}
```

**移除的逻辑**：
- 删除从AI全文翻译块提取发布日期的代码（约30行）
- 删除从原始文件提取发布日期的回退逻辑（约40行）
- 简化metadata组装逻辑

### 4. 迁移脚本（migrate_analysis_metadata.py）

**职责**：将所有旧格式的分析文件转换为新格式

**设计**：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import logging
import shutil
from typing import Dict, Any, List, Tuple
from datetime import datetime

class AnalysisMetadataMigrator:
    """分析文件metadata迁移器"""
    
    def __init__(self, base_dir: str, dry_run: bool = False):
        """
        初始化迁移器
        
        Args:
            base_dir: 项目根目录
            dry_run: 是否为dry-run模式（只显示不修改）
        """
        self.base_dir = base_dir
        self.dry_run = dry_run
        self.analysis_dir = os.path.join(base_dir, 'data', 'analysis')
        
        # 统计信息
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
    def extract_metadata_from_content(self, content: str) -> Dict[str, Any]:
        """
        从文件内容中提取metadata
        支持从AI全文翻译块或文件头部提取
        """
        metadata = {}
        
        # 尝试从AI全文翻译块提取
        ai_translation_start = "<!-- AI_TASK_START: AI全文翻译 -->"
        ai_translation_end = "<!-- AI_TASK_END: AI全文翻译 -->"
        
        if ai_translation_start in content and ai_translation_end in content:
            translation_block = content.split(ai_translation_start)[1].split(ai_translation_end)[0]
            
            # 提取发布时间
            date_match = re.search(r'\*\*发布时间[：:]\*\*\s*(.+)', translation_block)
            if date_match:
                metadata['publish_date'] = date_match.group(1).strip().replace('**', '').strip()
        
        # 尝试从文件头部提取（可能已经有部分metadata）
        lines = content.split('\n')[:30]
        header_content = '\n'.join(lines)
        
        patterns = {
            'publish_date': r'\*\*发布时间[：:]\*\*\s*(.+)',
            'vendor': r'\*\*厂商[：:]\*\*\s*(.+)',
            'type': r'\*\*类型[：:]\*\*\s*(.+)',
            'original_url': r'\*\*原始链接[：:]\*\*\s*(.+)'
        }
        
        for key, pattern in patterns.items():
            if key not in metadata:  # 只在未提取到时才从头部提取
                match = re.search(pattern, header_content, re.MULTILINE)
                if match:
                    value = match.group(1).strip().replace('**', '').strip()
                    metadata[key] = value
        
        return metadata
    
    def check_if_needs_migration(self, content: str) -> bool:
        """
        检查文件是否需要迁移
        如果文件头部已经有metadata块且格式正确，则不需要迁移
        """
        lines = content.split('\n')
        
        # 检查前10行是否包含metadata
        header_lines = lines[:10]
        has_metadata = False
        has_separator = False
        
        for line in header_lines:
            if re.match(r'\*\*发布时间[：:]\*\*', line):
                has_metadata = True
            if line.strip() == '---':
                has_separator = True
        
        # 如果已经有metadata和分隔线，且metadata在分隔线之前，则不需要迁移
        if has_metadata and has_separator:
            # 进一步检查：metadata应该在第一个AI_TASK之前
            first_ai_task_pos = content.find('<!-- AI_TASK_START:')
            if first_ai_task_pos > 0:
                header_part = content[:first_ai_task_pos]
                if '**发布时间' in header_part and '---' in header_part:
                    return False
        
        return True
    
    def migrate_file(self, filepath: str) -> Tuple[bool, str]:
        """
        迁移单个文件
        
        Returns:
            (成功标志, 错误信息)
        """
        try:
            # 读取文件内容
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否需要迁移
            if not self.check_if_needs_migration(content):
                return (True, 'skipped')
            
            # 提取metadata
            metadata = self.extract_metadata_from_content(content)
            
            if not metadata:
                return (False, '无法提取metadata')
            
            # 构建新的文件内容
            new_content_parts = []
            
            # 1. 写入metadata头部
            if metadata.get('publish_date'):
                new_content_parts.append(f"**发布时间:** {metadata['publish_date']}\n")
            if metadata.get('vendor'):
                new_content_parts.append(f"**厂商:** {metadata['vendor']}\n")
            if metadata.get('type'):
                new_content_parts.append(f"**类型:** {metadata['type']}\n")
            if metadata.get('original_url'):
                new_content_parts.append(f"**原始链接:** {metadata['original_url']}\n")
            
            new_content_parts.append("\n---\n\n")
            
            # 2. 移除旧的metadata（如果在文件开头）
            content_without_old_metadata = content
            lines = content.split('\n')
            start_index = 0
            
            # 跳过开头的metadata行
            for i, line in enumerate(lines):
                if line.strip().startswith('**发布时间') or \
                   line.strip().startswith('**厂商') or \
                   line.strip().startswith('**类型') or \
                   line.strip().startswith('**原始链接') or \
                   line.strip() == '---' or \
                   line.strip() == '':
                    start_index = i + 1
                else:
                    break
            
            if start_index > 0:
                content_without_old_metadata = '\n'.join(lines[start_index:])
            
            # 3. 添加剩余内容
            new_content_parts.append(content_without_old_metadata)
            
            new_content = ''.join(new_content_parts)
            
            if self.dry_run:
                logging.info(f"[DRY-RUN] 将迁移文件: {filepath}")
                return (True, 'dry-run')
            
            # 创建备份
            backup_path = f"{filepath}.bak"
            shutil.copy2(filepath, backup_path)
            
            # 写入新内容
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return (True, '')
            
        except Exception as e:
            return (False, str(e))
    
    def migrate_all(self) -> None:
        """迁移所有分析文件"""
        logging.info(f"开始迁移分析文件metadata...")
        logging.info(f"分析目录: {self.analysis_dir}")
        logging.info(f"Dry-run模式: {self.dry_run}")
        
        # 扫描所有分析文件
        analysis_files = []
        for root, dirs, files in os.walk(self.analysis_dir):
            for file in files:
                if file.endswith('.md'):
                    analysis_files.append(os.path.join(root, file))
        
        self.stats['total'] = len(analysis_files)
        logging.info(f"找到 {self.stats['total']} 个分析文件")
        
        # 迁移每个文件
        for filepath in analysis_files:
            success, error = self.migrate_file(filepath)
            
            if error == 'skipped':
                self.stats['skipped'] += 1
                logging.debug(f"跳过（已是新格式）: {filepath}")
            elif success:
                self.stats['success'] += 1
                logging.info(f"迁移成功: {filepath}")
            else:
                self.stats['failed'] += 1
                logging.error(f"迁移失败: {filepath} - {error}")
        
        # 输出统计信息
        logging.info("\n" + "="*50)
        logging.info("迁移完成统计:")
        logging.info(f"总文件数: {self.stats['total']}")
        logging.info(f"成功迁移: {self.stats['success']}")
        logging.info(f"跳过（已是新格式）: {self.stats['skipped']}")
        logging.info(f"失败: {self.stats['failed']}")
        logging.info("="*50)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="迁移分析文件metadata到文件头部")
    parser.add_argument("--base-dir", help="项目根目录")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run模式，只显示不修改")
    
    args = parser.parse_args()
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    base_dir = args.base_dir or os.getcwd()
    migrator = AnalysisMetadataMigrator(base_dir, args.dry_run)
    migrator.migrate_all()


if __name__ == "__main__":
    main()
```

## 数据模型

### Metadata字段定义

```python
{
    "publish_date": str,      # 发布时间，格式：YYYY-MM-DD
    "vendor": str,            # 厂商名称，如：AWS, Azure, GCP
    "type": str,              # 类型，如：BLOG, WHATSNEW
    "original_url": str       # 原始链接URL
}
```

### 分析文件格式

```markdown
**发布时间:** 2025-10-13

**厂商:** AWS

**类型:** BLOG

**原始链接:** https://aws.amazon.com/...

---

<!-- AI_TASK_START: AI标题翻译 -->
[解决方案] 使用 Amazon VPC Lattice 安全访问多租户 SaaS 中的客户资源
<!-- AI_TASK_END: AI标题翻译 -->

<!-- AI_TASK_START: AI竞争分析 -->
# 解决方案分析
...
<!-- AI_TASK_END: AI竞争分析 -->
```

## 错误处理

### 1. 文件写入错误

**场景**：AnalysisExecutionStage写入文件时失败

**处理**：
- 捕获异常并记录到日志
- 更新analysis_metadata.json中的last_error字段
- 不中断整个分析流程

### 2. Metadata提取失败

**场景**：DocumentManager无法从文件头部提取metadata

**处理**：
- 记录warning级别日志
- 返回默认值（文件名、修改时间等）
- 不影响文件展示

### 3. 迁移脚本错误

**场景**：迁移单个文件时失败

**处理**：
- 记录错误信息到日志
- 继续处理其他文件
- 最后输出失败文件列表

## 测试策略

### 1. 单元测试

**测试AnalysisExecutionStage**：
- 测试`_write_metadata_header`方法正确写入metadata
- 测试metadata字段缺失时的处理
- 测试特殊字符的转义

**测试DocumentManager**：
- 测试从文件头部正确提取metadata
- 测试中英文冒号的处理
- 测试metadata缺失时的默认值

**测试迁移脚本**：
- 测试识别需要迁移的文件
- 测试metadata提取的准确性
- 测试新文件内容的正确性

### 2. 集成测试

**端到端测试**：
1. 运行AI分析生成新格式文件
2. 验证文件头部metadata格式正确
3. 通过Web界面访问文件
4. 验证前端正确展示metadata

**迁移测试**：
1. 准备旧格式测试文件
2. 运行迁移脚本（dry-run模式）
3. 验证识别正确
4. 运行实际迁移
5. 验证迁移后文件格式正确
6. 验证备份文件存在

### 3. 性能测试

**DocumentManager性能**：
- 对比重构前后的metadata提取时间
- 目标：提取时间减少50%以上（从读取16KB到读取前20行）

**迁移脚本性能**：
- 测试迁移1000个文件的时间
- 目标：每个文件平均处理时间<100ms

## 实施计划

### 阶段1：代码修改（不影响现有系统）

1. 修改AnalysisExecutionStage，添加metadata头部写入逻辑
2. 新生成的文件将采用新格式
3. 旧文件保持不变

### 阶段2：迁移脚本开发和测试

1. 开发migrate_analysis_metadata.py
2. 在测试环境验证迁移逻辑
3. 使用dry-run模式在生产环境预检

### 阶段3：执行迁移

1. 备份data/analysis目录
2. 运行迁移脚本
3. 验证迁移结果

### 阶段4：代码清理

1. 简化DocumentManager的metadata提取逻辑
2. 简化rebuild_metadata.py的metadata提取逻辑
3. 删除所有处理旧格式的代码
4. 更新相关文档

## 回滚计划

如果迁移后发现问题：

1. **立即回滚**：
   - 停止AI分析服务
   - 从备份恢复data/analysis目录
   - 或使用.bak文件恢复单个文件

2. **代码回滚**：
   - 恢复DocumentManager的旧版本代码
   - 恢复AnalysisExecutionStage的旧版本代码

3. **验证**：
   - 验证Web界面正常展示
   - 验证rebuild_metadata.py正常工作
