#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分析文件Metadata迁移脚本

将旧格式的分析文件（metadata在AI_TASK标记中）转换为新格式（metadata在文件头部）
"""

import os
import re
import logging
import shutil
import argparse
from typing import Dict, Any, List, Tuple
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
        
        # 失败文件列表
        self.failed_files = []
        
    def extract_metadata_from_content(self, content: str) -> Dict[str, Any]:
        """
        从文件内容中提取metadata
        支持从AI全文翻译块或文件头部提取
        
        Args:
            content: 文件内容
            
        Returns:
            提取的metadata字典
        """
        metadata = {}
        
        # 尝试从AI全文翻译块提取
        ai_translation_start = "<!-- AI_TASK_START: AI全文翻译 -->"
        ai_translation_end = "<!-- AI_TASK_END: AI全文翻译 -->"
        
        if ai_translation_start in content and ai_translation_end in content:
            try:
                translation_block = content.split(ai_translation_start)[1].split(ai_translation_end)[0]
                
                # 提取发布时间
                date_patterns = [
                    r'\*\*发布时间[：:]\*\*\s*(\d{4}-\d{2}-\d{2})',
                    r'\*\*发布时间[：:]\*\*\s*\*\*\s*(\d{4}-\d{2}-\d{2})',
                    r'发布于[：:]\s*(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)',
                ]
                
                for pattern in date_patterns:
                    date_match = re.search(pattern, translation_block)
                    if date_match:
                        date_str = date_match.group(1).strip()
                        # 处理中文日期格式
                        if '年' in date_str:
                            date_str = date_str.replace(' ', '').replace('年', '-').replace('月', '-').replace('日', '')
                            parts = date_str.split('-')
                            if len(parts) == 3:
                                year, month, day = parts
                                date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        metadata['publish_date'] = date_str
                        break
            except Exception as e:
                logger.debug(f"从AI全文翻译块提取metadata失败: {e}")
        
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
                    value = match.group(1).strip()
                    # 清理星号和空格
                    value = value.replace('**', '').strip()
                    metadata[key] = value
        
        return metadata
    
    def check_if_needs_migration(self, content: str) -> bool:
        """
        检查文件是否需要迁移
        如果文件头部已经有metadata块且格式正确，则不需要迁移
        
        Args:
            content: 文件内容
            
        Returns:
            True表示需要迁移，False表示不需要
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
        
        Args:
            filepath: 文件路径
            
        Returns:
            (成功标志, 错误信息或状态)
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
                new_content_parts.append(f"**发布时间:** {metadata['publish_date']}\n\n")
            if metadata.get('vendor'):
                new_content_parts.append(f"**厂商:** {metadata['vendor']}\n\n")
            if metadata.get('type'):
                new_content_parts.append(f"**类型:** {metadata['type']}\n\n")
            if metadata.get('original_url'):
                new_content_parts.append(f"**原始链接:** {metadata['original_url']}\n\n")
            
            new_content_parts.append("---\n\n")
            
            # 2. 移除旧的metadata（如果在文件开头）
            content_without_old_metadata = content
            lines = content.split('\n')
            start_index = 0
            
            # 跳过开头的metadata行和空行
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('**发布时间') or \
                   stripped.startswith('**厂商') or \
                   stripped.startswith('**类型') or \
                   stripped.startswith('**原始链接') or \
                   stripped == '---' or \
                   stripped == '':
                    start_index = i + 1
                elif stripped.startswith('<!--'):
                    # 遇到AI_TASK标记，停止跳过
                    break
                else:
                    # 遇到其他内容，停止跳过
                    break
            
            if start_index > 0:
                content_without_old_metadata = '\n'.join(lines[start_index:])
            
            # 3. 添加剩余内容
            new_content_parts.append(content_without_old_metadata)
            
            new_content = ''.join(new_content_parts)
            
            if self.dry_run:
                logger.info(f"[DRY-RUN] 将迁移文件: {filepath}")
                logger.debug(f"[DRY-RUN] 提取的metadata: {metadata}")
                return (True, 'dry-run')
            
            # 创建备份
            backup_path = f"{filepath}.bak"
            shutil.copy2(filepath, backup_path)
            logger.debug(f"已创建备份: {backup_path}")
            
            # 写入新内容
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return (True, '')
            
        except Exception as e:
            logger.error(f"迁移文件失败: {filepath} - {e}", exc_info=True)
            return (False, str(e))
    
    def migrate_all(self) -> None:
        """迁移所有分析文件"""
        logger.info("="*60)
        logger.info("开始迁移分析文件metadata...")
        logger.info(f"分析目录: {self.analysis_dir}")
        logger.info(f"Dry-run模式: {self.dry_run}")
        logger.info("="*60)
        
        # 扫描所有分析文件
        analysis_files = []
        for root, dirs, files in os.walk(self.analysis_dir):
            for file in files:
                if file.endswith('.md'):
                    analysis_files.append(os.path.join(root, file))
        
        self.stats['total'] = len(analysis_files)
        logger.info(f"找到 {self.stats['total']} 个分析文件\n")
        
        # 迁移每个文件
        for i, filepath in enumerate(analysis_files, 1):
            logger.info(f"[{i}/{self.stats['total']}] 处理: {os.path.relpath(filepath, self.base_dir)}")
            success, error = self.migrate_file(filepath)
            
            if error == 'skipped':
                self.stats['skipped'] += 1
                logger.info("  ✓ 跳过（已是新格式）")
            elif error == 'dry-run':
                self.stats['success'] += 1
                logger.info("  ✓ [DRY-RUN] 将被迁移")
            elif success:
                self.stats['success'] += 1
                logger.info("  ✓ 迁移成功")
            else:
                self.stats['failed'] += 1
                self.failed_files.append((filepath, error))
                logger.error(f"  ✗ 迁移失败: {error}")
        
        # 输出统计信息
        logger.info("\n" + "="*60)
        logger.info("迁移完成统计:")
        logger.info(f"  总文件数: {self.stats['total']}")
        logger.info(f"  成功迁移: {self.stats['success']}")
        logger.info(f"  跳过（已是新格式）: {self.stats['skipped']}")
        logger.info(f"  失败: {self.stats['failed']}")
        logger.info("="*60)
        
        # 输出失败文件列表
        if self.failed_files:
            logger.error("\n失败文件列表:")
            for filepath, error in self.failed_files:
                logger.error(f"  - {os.path.relpath(filepath, self.base_dir)}: {error}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="迁移分析文件metadata到文件头部",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # Dry-run模式（只显示不修改）
  python scripts/migrate_analysis_metadata.py --dry-run
  
  # 实际执行迁移
  python scripts/migrate_analysis_metadata.py
  
  # 指定项目根目录
  python scripts/migrate_analysis_metadata.py --base-dir /path/to/project
        """
    )
    parser.add_argument(
        "--base-dir",
        help="项目根目录（默认为当前目录）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-run模式，只显示将要执行的操作而不实际修改文件"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试日志"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 确定项目根目录
    base_dir = args.base_dir or os.getcwd()
    
    # 验证目录存在
    analysis_dir = os.path.join(base_dir, 'data', 'analysis')
    if not os.path.exists(analysis_dir):
        logger.error(f"分析目录不存在: {analysis_dir}")
        logger.error("请确保在项目根目录下运行此脚本，或使用--base-dir指定正确的路径")
        return 1
    
    # 创建迁移器并执行
    migrator = AnalysisMetadataMigrator(base_dir, args.dry_run)
    migrator.migrate_all()
    
    # 返回退出码
    return 0 if migrator.stats['failed'] == 0 else 1


if __name__ == "__main__":
    exit(main())
