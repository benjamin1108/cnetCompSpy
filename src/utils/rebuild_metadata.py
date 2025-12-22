#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import logging
import re
import yaml
import shutil
from typing import Dict, Any, Optional, List, Set
from datetime import datetime

print("DEBUG: rebuild_metadata.py SCRIPT HAS STARTED AND THIS PRINT IS VISIBLE") # TEST PRINT

from src.utils.colored_logger import setup_colored_logging
from src.utils.metadata_manager import MetadataManager

# 设置日志
setup_colored_logging()
logger = logging.getLogger(__name__)

# 定义红色日志函数
def log_error_red(message: str) -> None:
    """使用红色输出错误日志"""
    logger.error(f"\033[91m{message}\033[0m")

def parse_md_file(filepath: str) -> Optional[Dict[str, Any]]:
    """
    解析MD文件，提取元数据信息
    
    Args:
        filepath: MD文件路径
        
    Returns:
        提取的元数据字典，如果解析失败则返回None
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取标题
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else os.path.basename(filepath)
        
        # 提取URL（尝试匹配多种URL格式）
        url = ''
        # 首先尝试匹配 "URL: " 格式
        url_match = re.search(r'URL: (.+)', content)
        if url_match:
            url = url_match.group(1).strip()
        else:
            # 如果没有找到，尝试匹配 "**原始链接:** [URL](URL)" 格式
            url_match = re.search(r'\*\*原始链接[:：]*\*\*.*?\[(.*?)\]\((.*?)\)', content)
            if url_match:
                url = url_match.group(2).strip()
            else:
                # 再尝试匹配 "**原始链接:** URL" 格式
                url_match = re.search(r'\*\*原始链接[:：]*\*\*.*?(https?://[^\s\)]+)', content)
                if url_match:
                    url = url_match.group(1).strip()
        
        # 提取日期（假设内容中有日期字段）
        date_match = re.search(r'Date: (.+)', content)
        crawl_time = date_match.group(1) if date_match else datetime.now().isoformat()
        
        # 提取厂商和来源类型（从文件路径中推断）
        # 标准化路径格式，确保使用正斜杠
        normalized_path = filepath.replace('\\', '/')
        
        # 检查路径中是否包含 data/raw/vendor/type 模式
        if '/data/raw/' in normalized_path:
            parts = normalized_path.split('/data/raw/')[1].split('/')
            if len(parts) >= 2:
                vendor = parts[0]
                source_type = parts[1]
            else:
                vendor = 'unknown'
                source_type = 'unknown'
        else:
            # 尝试使用相对路径提取
            rel_path = os.path.relpath(filepath, os.path.dirname(os.path.dirname(filepath)))
            parts = rel_path.split(os.sep)
            if len(parts) >= 3:
                vendor = parts[1]
                source_type = parts[2]
            else:
                vendor = 'unknown'
                source_type = 'unknown'
            
        return {
            'title': title,
            'url': url,
            'crawl_time': crawl_time,
            'filepath': filepath,
            'vendor': vendor,
            'source_type': source_type
        }
    except Exception as e:
        logger.error(f"解析MD文件失败: {filepath} - {e}")
        return None

def check_analysis_file_completeness(filepath: str, required_tasks: List[str]) -> Dict[str, Any]:
    """
    检查分析文件是否完整，包含所有必要的AI任务。
    一个任务块如果存在错误标记，则该任务失败，但文件结构仍被视为针对该任务是存在的。
    """
    result = {
        'is_complete': True,      # 初始假设文件是完整的
        'missing_tasks': [],    # 任务的 start_tag 或 end_tag 完全缺失
        'incomplete_tasks': [], # 任务标记存在，但内容为空 (且非错误)
        'failed_tasks': [],     # 任务标记存在，且内容包含 ERROR 标记
        'reason': None
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查每个必要任务是否存在且完整
        for task in required_tasks:
            start_tag = f"<!-- AI_TASK_START: {task} -->"
            end_tag = f"<!-- AI_TASK_END: {task} -->"
            error_tag_pattern = r"<!-- ERROR:.*?-->" # 正则表达式以匹配错误标记及其内容
            
            has_start_tag = start_tag in content
            has_end_tag = end_tag in content

            if not has_start_tag or not has_end_tag:
                result['is_complete'] = False # 标记缺失，文件结构不完整
                result['missing_tasks'].append(task)
            else:
                # 标记都存在，提取任务内容
                task_content = "" # Default to empty string
                try:
                    task_content_full = content.split(start_tag)[1]
                    task_content = task_content_full.split(end_tag)[0].strip()
                except IndexError:
                    result['is_complete'] = False
                    result['missing_tasks'].append(f"{task} (标记存在但无法提取内容)")
                    # This task cannot be further processed, but other tasks might still be checked.
                    # The overall is_complete is already False.
                    continue # Move to the next task for checking its presence

                is_error_task = bool(re.search(error_tag_pattern, task_content, re.IGNORECASE))

                if is_error_task:
                    result['failed_tasks'].append(task) # 记录任务失败
                elif not task_content:
                    # 任务标记存在，不是错误任务，但内容为空
                    result['is_complete'] = False # 成功任务但内容为空，视为文件不完整
                    result['incomplete_tasks'].append(f"{task} (内容为空且非错误)")
        
        # 设置最终原因
        if not result['is_complete']:
            reasons = []
            if result['missing_tasks']:
                reasons.append(f"缺少任务标记: {', '.join(result['missing_tasks'])}")
            if result['incomplete_tasks']:
                # Corrected f-string
                reasons.append(f"成功任务内容为空或不完整: {', '.join(result['incomplete_tasks'])}") 
            result['reason'] = "; ".join(reasons) if reasons else "文件结构不完整 (未知原因)" # Added a fallback for unknown reason
        elif result['failed_tasks']:
            result['reason'] = f"文件结构完整但包含失败任务: {', '.join(result['failed_tasks'])}"
        else:
            result['reason'] = "文件完整且所有定义的AI任务块均存在且非空（或标记为错误）"
            
        return result
    except Exception as e:
        result['is_complete'] = False
        result['reason'] = f"检查文件时出错: {str(e)}"
        return result

def load_required_tasks(base_dir: str) -> List[str]:
    """
    从配置文件中加载必要的AI任务列表
    
    Args:
        base_dir: 项目根目录
        
    Returns:
        必要的AI任务列表
    """
    try:
        # 使用通用配置加载器
        from src.utils.config_loader import get_config
        
        # 加载配置
        config = get_config(base_dir=base_dir)
        
        # 从配置中提取任务列表
        tasks = [task.get('type') for task in config.get('ai_analyzer', {}).get('tasks', [])]
        return [task for task in tasks if task]  # 过滤掉None值
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        # 返回默认任务列表
        return ["AI标题翻译", "AI竞争分析", "AI全文翻译"]

def validate_task_content(task_type: str, content: str) -> Dict[str, Any]:
    """
    深入验证任务内容是否符合预期，检测'假完成'问题
    
    Args:
        task_type: 任务类型
        content: 任务内容
        
    Returns:
        验证结果字典，包含是否有效、问题描述等信息
    """
    result = {
        'is_valid': True,
        'reason': None
    }
    
    # 去除内容首尾空白字符
    content = content.strip()
    
    # 如果内容为空，直接判定为无效
    if not content:
        result['is_valid'] = False
        result['reason'] = f"{task_type}任务内容为空"
        return result
    
    # 检查内容是否过短（根据任务类型设置不同的最小长度）
    min_length_map = {
        "AI标题翻译": 5,  # 标题至少5个字符
        "AI竞争分析": 100,  # 竞争分析至少100个字符
        "AI全文翻译": 200   # 全文翻译至少200个字符
    }
    
    min_length = min_length_map.get(task_type, 30)  # 默认至少30个字符
    
    if len(content) < min_length:
        result['is_valid'] = False
        result['reason'] = f"{task_type}任务内容过短（仅{len(content)}字符，期望至少{min_length}字符）"
        return result
    
    # 根据任务类型进行特定验证
    if task_type == "AI标题翻译":
        # 去掉markdown标题前缀（如 "# "）后再检查
        title_content = content.lstrip('#').strip()
        
        # 检查标题是否包含预期的标签前缀
        # 注意：月度更新汇总类文档（标题包含"月"或"更新"且为年月格式）不需要前缀
        is_monthly_update = ("年" in title_content and "月" in title_content) or ("网络服务" in title_content and "更新" in title_content)
        
        if not is_monthly_update:
            if not (title_content.startswith("[解决方案]") or 
                    title_content.startswith("[新产品/新功能]") or 
                    title_content.startswith("[新产品]") or 
                    title_content.startswith("[新功能]") or
                    title_content.startswith("[产品更新]") or
                    title_content.startswith("[技术更新]") or
                    title_content.startswith("[案例分析]")):
                result['is_valid'] = False
                result['reason'] = "AI标题翻译缺少预期的标签前缀，如[解决方案]、[新功能]等"
                return result
            
        # 检查标题是否包含非中文内容（允许部分专有名词如AWS、Azure等）
        # 这里使用一个简单的启发式方法：如果非ASCII字符太少，可能没有正确翻译成中文
        # non_ascii_chars = sum(1 for c in content if ord(c) > 127)
        # if non_ascii_chars < len(content) * 0.3:  # 假设至少30%应该是中文字符
        #     result['is_valid'] = False
        #     result['reason'] = "AI标题翻译可能未正确翻译成中文"
        #     return result
            
    elif task_type == "AI全文翻译":
        # # 检查是否包含足够的中文内容
        # non_ascii_chars = sum(1 for c in content if ord(c) > 127)
        # if non_ascii_chars < len(content) * 0.3:  # 假设至少30%应该是中文字符
        #     result['is_valid'] = False
        #     result['reason'] = "AI全文翻译可能未正确翻译成中文，中文字符占比过低"
        #     return result
            
        # 检查是否存在常见的未完成翻译特征
        incomplete_markers = [
            "I'll translate", "Here's the translation", "翻译如下", 
            "以下是翻译", "Translation:", "The translation is",
            "[以下内容已省略]", "[更多内容已省略]",
            "to be continued", "未完待续"
        ]
        
        for marker in incomplete_markers:
            if marker.lower() in content.lower():
                result['is_valid'] = False
                result['reason'] = f"AI全文翻译可能未完成，包含'{marker}'等特征文本"
                return result
                
        # 检查全文翻译是否有章节结构，大多数完整翻译应该包含标题结构
        if not ('#' in content or '##' in content or '###' in content):
            # 这是一个软性检查，只在内容较长时才执行
            if len(content) > 1000 and '\n\n' not in content:
                result['is_valid'] = False
                result['reason'] = "AI全文翻译可能不完整，缺少章节结构或段落格式"
                return result
    
    elif task_type == "AI竞争分析":
        # 检查竞争分析是否包含预期的章节
        # 支持两种模板：产品功能分析模板 和 月度更新汇总模板
        expected_sections = ["概述", "方案", "价值", "产品", "评估"]
        monthly_sections = ["更新总览", "更新详情", "重点更新", "趋势", "概览"]
        
        section_count = 0
        for section in expected_sections:
            if section in content:
                section_count += 1
        
        monthly_section_count = 0
        for section in monthly_sections:
            if section in content:
                monthly_section_count += 1
                
        # 至少应满足其中一种模板的要求
        if section_count < 3 and monthly_section_count < 2:
            result['is_valid'] = False
            result['reason'] = "AI竞争分析内容不完整，缺少关键章节"
            return result
    
    return result

def deep_check_analysis_file(filepath: str, required_tasks: List[str]) -> Dict[str, Any]:
    """
    深入检查分析文件内容是否符合预期，包括检测"假完成"问题
    
    Args:
        filepath: 分析文件路径
        required_tasks: 必要的AI任务列表
        
    Returns:
        检查结果字典，包含是否有效、问题描述等信息
    """
    result = {
        'is_valid': True,
        'invalid_tasks': [],
        'reason': None
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查每个必要任务的内容
        for task in required_tasks:
            start_tag = f"<!-- AI_TASK_START: {task} -->"
            end_tag = f"<!-- AI_TASK_END: {task} -->"
            
            if start_tag not in content or end_tag not in content:
                # 任务标记不存在，由基本检查处理，这里跳过
                continue
            
            # 提取任务内容
            task_content = content.split(start_tag)[1].split(end_tag)[0].strip()
            
            # 验证任务内容
            validation_result = validate_task_content(task, task_content)
            
            if not validation_result['is_valid']:
                result['is_valid'] = False
                result['invalid_tasks'].append({
                    'task': task,
                    'reason': validation_result['reason']
                })
        
        # 设置总体原因
        if not result['is_valid']:
            reasons = [f"{item['task']}: {item['reason']}" for item in result['invalid_tasks']]
            result['reason'] = "; ".join(reasons)
            
        return result
    except Exception as e:
        result['is_valid'] = False
        result['reason'] = f"检查文件内容时出错: {str(e)}"
        return result

def rebuild_metadata(base_dir: Optional[str] = None, type: str = 'all', force_clear: bool = False, deep_check: bool = False, delete_invalid: bool = False) -> None:
    """
    重建元数据，从本地MD文件解析并更新元数据
    
    Args:
        base_dir: 项目根目录，如果为None则使用当前目录
        type: 元数据类型，crawler、analysis 或 all（默认刷新所有类型）
        force_clear: 是否强制清空原有元数据
        deep_check: 是否启用深度内容验证，检测"假完成"问题
        delete_invalid: 是否删除检测到的无效文件，仅在deep_check=True时有效
    """
    processed_files = 0
    successful_updates = 0
    errors = []
    deleted_files_count = 0
    deleted_crawler_metadata_count = 0
    deleted_analysis_metadata_count = 0
    overwritten_crawler_metadata_count = 0
    overwritten_analysis_metadata_count = 0
    invalid_content_files_count = 0
    
    # 用于记录检测到的问题文件（不删除时使用）
    problem_files = []
    
    # 创建用于记录问题文件的日志文件
    if deep_check and not delete_invalid:
        os.makedirs("logs", exist_ok=True)
        deep_check_log_file = os.path.join("logs", f"deep-check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logger.info(f"深度检查结果将被记录到: {deep_check_log_file}")
    
    # 记录所有处理过的文件路径，用于清理无效记录
    processed_file_paths = set()
    # 初始化元数据管理器
    metadata_manager = MetadataManager(base_dir)
    
    if force_clear:
        if type == 'crawler':
            metadata_manager.crawler_metadata.clear()
            metadata_manager._save_metadata(metadata_manager.crawler_metadata_file, metadata_manager.crawler_metadata)
            logger.info("已清空爬虫元数据记录")
        elif type == 'analysis':
            metadata_manager.analysis_metadata.clear()
            metadata_manager._save_metadata(metadata_manager.analysis_metadata_file, metadata_manager.analysis_metadata)
            logger.info("已清空分析元数据记录")
        elif type == 'all':
            metadata_manager.crawler_metadata.clear()
            metadata_manager.analysis_metadata.clear()
            metadata_manager._save_metadata(metadata_manager.crawler_metadata_file, metadata_manager.crawler_metadata)
            metadata_manager._save_metadata(metadata_manager.analysis_metadata_file, metadata_manager.analysis_metadata)
            logger.info("已清空所有元数据记录")
    
    if type == 'crawler' or type == 'all':
        raw_dir = os.path.join(metadata_manager.base_dir, 'data', 'raw')
        md_files = [os.path.join(root, file) for root, dirs, files in os.walk(raw_dir) for file in files if file.endswith('.md')]
        # 记录所有存在的文件路径，用于清理无效记录
        existing_file_paths = set(md_files)
        for filepath in md_files:
            processed_files += 1
            logger.debug(f"Processing crawler file: {filepath}")
            metadata = parse_md_file(filepath)
            if metadata:
                try:
                    # 从元数据中获取厂商和来源类型，确保不是 'unknown'
                    vendor = metadata['vendor']
                    source_type = metadata['source_type']
                    
                    # 如果厂商或来源类型是 'unknown'，尝试从文件路径中提取
                    if vendor == 'unknown' or source_type == 'unknown':
                        # 标准化路径格式，确保使用正斜杠
                        normalized_path = filepath.replace('\\', '/')
                        
                        # 检查路径中是否包含 data/raw/vendor/type 模式
                        if '/data/raw/' in normalized_path:
                            parts = normalized_path.split('/data/raw/')[1].split('/')
                            if len(parts) >= 2:
                                vendor = parts[0]
                                source_type = parts[1]
                                # 更新元数据中的厂商和来源类型
                                metadata['vendor'] = vendor
                                metadata['source_type'] = source_type
                    
                    # 确保filepath字段正确设置，这对于StatsAnalyzer非常重要
                    metadata['filepath'] = filepath
                    # 使用URL作为键更新元数据，如果URL为空则使用filepath
                    url_key = metadata['url'] if metadata['url'] else filepath
                    
                    # 获取现有的爬虫元数据以供检查
                    all_crawler_metadata = metadata_manager.get_all_crawler_metadata()
                    existing_entry = None
                    old_url_key_if_filepath_changed = None

                    if vendor in all_crawler_metadata and source_type in all_crawler_metadata[vendor]:
                        # 检查是否有基于 Filepath 的现有记录 (首选匹配方式)
                        for key, entry_val in all_crawler_metadata[vendor][source_type].items():
                            if entry_val.get('filepath') == filepath:
                                existing_entry = entry_val
                                old_url_key_if_filepath_changed = key # 记录旧的key，如果url_key改变了，需要用这个来删除旧条目
                                break
                        # 如果没有基于 Filepath 的匹配，再尝试基于 URL Key (作为后备)
                        if not existing_entry and url_key in all_crawler_metadata[vendor][source_type]:
                             existing_entry = all_crawler_metadata[vendor][source_type][url_key]
                             # old_url_key_if_filepath_changed 此时应与 url_key 相同，或为 None (如果之前没有记录)

                    if existing_entry:
                        # 记录已存在，保留原有的 crawl_time
                        metadata['crawl_time'] = existing_entry.get('crawl_time', metadata['crawl_time']) # 保留旧时间，如果不存在则用新的
                        overwritten_crawler_metadata_count += 1
                        logger.debug(f"Overwriting existing crawler metadata for: {filepath} but preserving original crawl_time if possible.")
                        
                        # 如果因为URL变化导致url_key改变了，但filepath匹配上了，需要删除旧key的条目
                        if old_url_key_if_filepath_changed and old_url_key_if_filepath_changed != url_key:
                            if vendor in metadata_manager.crawler_metadata and \
                               source_type in metadata_manager.crawler_metadata[vendor] and \
                               old_url_key_if_filepath_changed in metadata_manager.crawler_metadata[vendor][source_type]:
                                del metadata_manager.crawler_metadata[vendor][source_type][old_url_key_if_filepath_changed]
                                logger.debug(f"Removed old metadata entry with key {old_url_key_if_filepath_changed} for: {filepath} due to URL key change.")
                    
                    # 批量更新（实际上这里是单个更新，但保持了原有函数调用）
                    metadata_manager.update_crawler_metadata_entries_batch(vendor, source_type, {url_key: metadata})
                    successful_updates += 1
                    logger.info(f"Successfully updated crawler metadata for: {filepath}")
                except Exception as e:
                    errors.append(f"Error in {filepath}: {str(e)}")
                    logger.error(f"Failed to update crawler metadata for {filepath}: {str(e)}")
            else:
                errors.append(f"Failed to parse {filepath}")
                logger.error(f"Failed to parse crawler file {filepath}")
        
        # 清理无效的爬虫元数据记录
        all_crawler_metadata = metadata_manager.get_all_crawler_metadata()
        invalid_crawler_records = []
        for vendor in all_crawler_metadata:
            for source_type in all_crawler_metadata[vendor]:
                for url_key, entry in list(all_crawler_metadata[vendor][source_type].items()):
                    filepath = entry.get('filepath', '')
                    if filepath and filepath not in existing_file_paths:
                        invalid_crawler_records.append((vendor, source_type, url_key, filepath))
        
        # 如果有无效记录，直接修改metadata_manager中的crawler_metadata
        if invalid_crawler_records:
            for vendor, source_type, url_key, filepath in invalid_crawler_records:
                try:
                    if vendor in metadata_manager.crawler_metadata and source_type in metadata_manager.crawler_metadata[vendor] and url_key in metadata_manager.crawler_metadata[vendor][source_type]:
                        del metadata_manager.crawler_metadata[vendor][source_type][url_key]
                        deleted_crawler_metadata_count += 1
                        logger.info(f"Removed invalid crawler metadata record: {filepath}")
                except Exception as e:
                    errors.append(f"Error removing invalid crawler record {filepath}: {str(e)}")
                    logger.error(f"Failed to remove invalid crawler metadata record {filepath}: {str(e)}")
            
            # 保存更改后的爬虫元数据
            metadata_manager.save_crawler_metadata()
            logger.info(f"已保存清理后的爬虫元数据")
    
    
    if type == 'analysis' or type == 'all':
        analysis_dir = os.path.join(metadata_manager.base_dir, 'data', 'analysis')
        analysis_files = [os.path.join(root, file) for root, dirs, files in os.walk(analysis_dir) for file in files if file.endswith('.md')]
        
        # 获取原始文件路径，用于检查分析文件是否有对应的原始文件
        raw_dir = os.path.join(metadata_manager.base_dir, 'data', 'raw')
        raw_files = [os.path.join(root, file) for root, dirs, files in os.walk(raw_dir) for file in files if file.endswith('.md')]
        raw_file_paths = set(raw_files)
        
        # 加载必要的AI任务列表
        required_tasks = load_required_tasks(metadata_manager.base_dir)
        logger.info(f"加载必要的AI任务列表: {', '.join(required_tasks)}")
        
        # 记录需要删除的文件
        files_to_delete = []
        
        for filepath in analysis_files:
            processed_files += 1
            logger.debug(f"Processing analysis file: {filepath}")
            try:
                # 标准化文件路径，这对于MetadataManager非常重要
                normalized_path = os.path.relpath(filepath, metadata_manager.base_dir)
                
                # 获取对应的原始文件路径
                raw_path = filepath.replace('/analysis/', '/raw/')
                raw_path = raw_path.replace('\\\\analysis\\', '\\\\raw\\')  # 兼容Windows路径
                raw_normalized_path = os.path.relpath(raw_path, metadata_manager.base_dir) # 定义 raw_normalized_path

                # 获取现有的分析元数据（如果存在）- 移动到更前面
                existing_analysis_entry = metadata_manager.get_analysis_metadata(raw_normalized_path)
                existing_info_data = existing_analysis_entry.get('info', {}) if existing_analysis_entry else {}
                existing_tasks_data = existing_analysis_entry.get('tasks', {}) if existing_analysis_entry else {}

                # 初始化 info_data - 关键修改：确保在任何任务块处理前初始化
                info_data = existing_info_data.copy()
                logger.debug(f"[DEBUG-LIFECYCLE] File: {filepath} - Initialized info_data from existing_info_data. Keys: {list(info_data.keys())}")

                # 检查原始文件是否存在
                if raw_path not in raw_file_paths:
                    reason = f"对应的原始文件不存在: {raw_path}"
                    log_error_red(f"需要删除文件 {filepath}: {reason}")
                    files_to_delete.append((filepath, reason))
                    continue
                
                # 检查分析文件是否完整
                completeness_result = check_analysis_file_completeness(filepath, required_tasks)
                if not completeness_result['is_complete']:
                    reason = completeness_result['reason']
                    log_error_red(f"需要删除文件 {filepath}: {reason}")
                    files_to_delete.append((filepath, reason))
                    continue
                
                # 深入检查分析文件内容是否符合预期（检测"假完成"问题）
                if deep_check:
                    validation_result = deep_check_analysis_file(filepath, required_tasks)
                    if not validation_result['is_valid']:
                        reason = validation_result['reason']
                        if delete_invalid:
                            # 删除模式：将文件加入删除列表
                            log_error_red(f"需要删除内容异常的文件 {filepath}: {reason}")
                            files_to_delete.append((filepath, reason))
                            invalid_content_files_count += 1
                            continue
                        else:
                            # 只记录模式：将问题文件记录到列表中，稍后写入日志文件
                            log_error_red(f"检测到内容异常的文件 {filepath}: {reason}")
                            problem_files.append((filepath, reason))
                            # 虽然检测到问题，但仍继续处理，不跳过
                
                # 记录处理过的文件路径
                processed_file_paths.add(raw_normalized_path)
                
                publish_date_to_store = None
                chinese_title_to_store = info_data.get('chinese_title') # 从已初始化的 info_data 获取，或 None

                # --- 优先从分析文件中提取中文标题（从AI标题翻译任务块） ---
                ai_title_task_name = "AI标题翻译"
                start_tag_title = f"<!-- AI_TASK_START: {ai_title_task_name} -->"
                end_tag_title = f"<!-- AI_TASK_END: {ai_title_task_name} -->"
                
                current_analysis_file_content = ""
                try:
                    with open(filepath, 'r', encoding='utf-8') as f_analysis_content:
                        current_analysis_file_content = f_analysis_content.read()
                except Exception as e_read_analysis:
                    logger.error(f"无法读取分析文件 {filepath} 以提取信息: {e_read_analysis}")

                if current_analysis_file_content and start_tag_title in current_analysis_file_content and end_tag_title in current_analysis_file_content:
                    try:
                        title_block_content = current_analysis_file_content.split(start_tag_title)[1].split(end_tag_title)[0].strip()
                        logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - Original title_block_content: '{title_block_content}'")

                        if title_block_content:
                            update_type = ""
                            pure_title_content = title_block_content # 默认为原始内容
                            logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - Initial pure_title_content: '{pure_title_content}'")

                            # 提取方括号内的标签作为 update_type
                            update_type_match = re.match(r'^\[(.*?)\]', title_block_content)
                            logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - update_type_match result: {update_type_match}")
                            if update_type_match:
                                update_type = update_type_match.group(1).strip()
                                logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - Extracted update_type from match: '{update_type}'")
                                # 移除标签，得到纯净标题
                                pure_title_content = re.sub(r'^\[.*?\]\s*', '', title_block_content).strip()
                                logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - pure_title_content after re.sub: '{pure_title_content}'")
                            else:
                                logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - No update_type_match found. update_type will be empty, pure_title_content remains original.")
                            
                            logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - Before assigning to info_data - update_type: '{update_type}', pure_title_content: '{pure_title_content}'")
                            
                            if 'update_type' not in info_data and 'chinese_title' not in info_data: # 简单检查是否是空字典
                                logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - info_data seems to be a new dict here. This might be unintended if existing_info_data was expected.")
                            
                            info_data['update_type'] = update_type
                            chinese_title_to_store = pure_title_content # 使用处理后的标题
                            logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - After assigning to info_data - info_data.update_type: '{info_data.get('update_type')}', chinese_title_to_store: '{chinese_title_to_store}'")
                            logger.debug("从 AI 标题翻译块提取到 update_type: '%s', chinese_title: '%s' (文件: %s)", 
                                         update_type, chinese_title_to_store, filepath)
                        else: # title_block_content 为空
                            logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - title_block_content is empty.")
                            info_data['update_type'] = ""
                            chinese_title_to_store = ""
                            logger.debug(f"AI 标题翻译块内容为空，update_type 和 chinese_title 设置为空 (文件: {filepath})")

                    except Exception as e_parse_title:
                        logger.error(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - Error parsing title block: {e_parse_title}", exc_info=True)
                        # 即使解析出错，也尝试设置默认空值，避免字段缺失
                        info_data['update_type'] = ""
                        # chinese_title_to_store 保持上一个状态或默认值
                        logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - Exception caught, set update_type to empty, chinese_title_to_store: '{chinese_title_to_store}'")


                # --- 优先从分析文件的AI全文翻译任务块中解析发布日期 ---
                ai_translation_task_name = "AI全文翻译"
                start_tag_translate = f"<!-- AI_TASK_START: {ai_translation_task_name} -->"
                end_tag_translate = f"<!-- AI_TASK_END: {ai_translation_task_name} -->"
                
                # 'content' 变量应已包含当前分析文件 (filepath) 的内容
                # 这是在后续的 tasks_status 构建循环之前读取的
                current_analysis_file_content = ""
                try:
                    with open(filepath, 'r', encoding='utf-8') as f_analysis_content:
                        current_analysis_file_content = f_analysis_content.read()
                except Exception as e_read_analysis:
                    logger.error(f"无法读取分析文件 {filepath} 以提取发布日期: {e_read_analysis}")

                if current_analysis_file_content and start_tag_translate in current_analysis_file_content and end_tag_translate in current_analysis_file_content:
                    try:
                        translation_block_content = current_analysis_file_content.split(start_tag_translate)[1].split(end_tag_translate)[0].strip()
                        if translation_block_content:
                            date_match_ai = re.search(r'\*\*发布时间:\*\*\s*(\d{4}-\d{2}-\d{2})', translation_block_content)
                            if date_match_ai:
                                publish_date_to_store = date_match_ai.group(1)
                                logger.debug(f"从 AI 全文翻译块提取到发布日期 '{publish_date_to_store}' (文件: {filepath})")
                    except Exception as e_parse_ai:
                        logger.debug(f"从 AI 全文翻译块解析发布日期时出错 (文件: {filepath}): {e_parse_ai}")
                
                # --- 如果未能从AI翻译块获取，尝试从对应的原始 (raw) 文件中解析 ---
                if not publish_date_to_store:
                    logger.debug(f"AI块中未找到发布日期 (文件: {filepath})。尝试读取原始文件: {raw_path}")
                    try:
                        if os.path.exists(raw_path):
                            with open(raw_path, 'r', encoding='utf-8') as f_raw:
                                raw_content = f_raw.read()
                            
                            # 首先尝试 '**发布时间:** YYYY-MM-DD'
                            date_match_raw_primary = re.search(r'\*\*发布时间:\*\*\s*(\d{4}-\d{2}-\d{2})', raw_content)
                            if date_match_raw_primary:
                                publish_date_to_store = date_match_raw_primary.group(1)
                                logger.debug(f"从原始文件提取到发布日期 '{publish_date_to_store}' (使用 '**发布时间:**' 模式，文件: {raw_path})")
                            else:
                                # 如果主要模式失败, 尝试 'Date: YYYY-MM-DD' (或包含时间的ISO格式)
                                date_match_raw_alt = re.search(r'^Date:\s*(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[-+]\d{2}:\d{2})?)?)', raw_content, re.MULTILINE)
                                if date_match_raw_alt:
                                    publish_date_to_store = date_match_raw_alt.group(1).split('T')[0] # 只取日期部分
                                    logger.debug(f"从原始文件提取到发布日期 '{publish_date_to_store}' (使用 'Date:' 模式，文件: {raw_path})")
                                else:
                                    logger.debug(f"原始文件中未找到发布日期 (使用 '**发布时间:**' 或 'Date:' 模式，文件: {raw_path})")
                        else:
                            logger.warning(f"对应的原始文件不存在，无法提取发布日期: {raw_path}")
                    except Exception as e_parse_raw:
                        logger.error(f"读取或解析原始文件以提取发布日期时出错 (文件: {raw_path}): {e_parse_raw}")

                # 更新分析元数据，读取任务的实际状态和错误信息
                tasks_status = {}
                current_time_for_new_tasks = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 获取现有的分析元数据（如果存在）
                existing_analysis_entry = metadata_manager.get_analysis_metadata(raw_normalized_path)
                existing_tasks_data = existing_analysis_entry.get('tasks', {}) if existing_analysis_entry else {}
                # 保留现有的info块（如果存在）
                existing_info_data = existing_analysis_entry.get('info', {}) if existing_analysis_entry else {}

                # 尝试从爬虫元数据获取info信息
                crawler_info = {}
                try:
                    # 获取vendor和source_type
                    parts = raw_normalized_path.split('/')
                    if len(parts) >= 4 and parts[0] == 'data' and parts[1] == 'raw':
                        vendor = parts[2]
                        source_type = parts[3]
                        # 尝试找到爬虫元数据中对应的条目
                        crawler_metadata = metadata_manager.get_all_crawler_metadata()
                        if vendor in crawler_metadata and source_type in crawler_metadata[vendor]:
                            # 首先尝试通过filepath查找
                            for url_key, entry in crawler_metadata[vendor][source_type].items():
                                if entry.get('filepath') == raw_path:
                                    crawler_info = entry.copy()
                                    logger.debug(f"找到爬虫元数据：通过filepath匹配 {raw_path}")
                                    break
                            
                            # 如果通过filepath未找到，尝试使用文件名作为备选匹配方法
                            if not crawler_info:
                                filename = os.path.basename(raw_path)
                                for url_key, entry in crawler_metadata[vendor][source_type].items():
                                    if entry.get('filepath') and os.path.basename(entry.get('filepath')) == filename:
                                        crawler_info = entry.copy()
                                        logger.debug(f"找到爬虫元数据：通过文件名匹配 {filename}")
                                        break
                except Exception as e:
                    logger.error(f"尝试获取爬虫元数据时出错: {e}")

                # 构建或更新info块
                # info_data = existing_info_data.copy() # REMOVE THIS LINE - info_data should already be initialized and potentially contain update_type
                # logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - Initialized info_data with existing_info_data. Keys: {list(info_data.keys())}")
                # The line above was: logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - Initialized info_data with existing_info_data. Keys: {list(info_data.keys())}")
                # We are removing the re-initialization of info_data here.
                # info_data at this point should be the one initialized at the start of the loop and updated with update_type and chinese_title_to_store from the title block.

                # 如果找到爬虫元数据，优先使用其内容更新 info_data
                # 但是要注意，不要覆盖掉我们已经从分析文件标题块中精心提取的 update_type 和 chinese_title
                if crawler_info:
                    # 先保存我们已有的 update_type 和 chinese_title (如果存在)
                    current_update_type = info_data.get('update_type')
                    current_chinese_title = info_data.get('chinese_title')

                    # 提取基本信息，并更新到 info_data
                    info_data.update({
                        'title': crawler_info.get('title', info_data.get('title', '')),
                        'original_url': crawler_info.get('url', info_data.get('original_url', '')),
                        'crawl_time': crawler_info.get('crawl_time', info_data.get('crawl_time', '')),
                        'vendor': crawler_info.get('vendor', info_data.get('vendor', '')),
                        'type': crawler_info.get('source_type', info_data.get('type', ''))
                    })
                    
                    # 恢复/确保我们从分析文件标题块得到的 update_type 和 chinese_title 优先
                    if current_update_type is not None: # 只有当之前提取到时才设置
                        info_data['update_type'] = current_update_type
                    if current_chinese_title is not None: # 只有当之前提取到时才设置
                        info_data['chinese_title'] = current_chinese_title
                
                # 添加中文标题到info字段 (这一步其实在上面 crawler_info 处理时已经考虑了, 但为了逻辑清晰可以保留或调整)
                # 如果 chinese_title_to_store (从标题块解析的) 非空，且 info_data 中还没有 chinese_title，或者需要强制覆盖，则更新
                # 当前逻辑是，如果 crawler_info 中没有 chinese_title, 那么 current_chinese_title 会是 None 或来自 existing_info_data
                # 如果 chinese_title_to_store 有值, 它应该优先于来自 crawler_info 的空值或旧值。
                if chinese_title_to_store is not None and info_data.get('chinese_title') != chinese_title_to_store : # 确保赋值
                    info_data['chinese_title'] = chinese_title_to_store
                    logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - Ensured chinese_title_to_store ('{chinese_title_to_store}') is in info_data['chinese_title']")
                
                # update_type 已经在前面处理 title_block_content 时加入初始的 info_data，这里需要确保它没被 crawler_info 意外覆盖掉
                # (上面的 crawler_info 处理逻辑已经考虑了这一点)
                logger.debug(f"[DEBUG-TITLE-EXTRACTION] File: {filepath} - Final info_data before update_analysis_metadata: {info_data}")
                
                # 添加或更新file字段
                info_data['file'] = raw_normalized_path
                
                # 处理publish_date（按优先级使用上面解析的结果）
                if publish_date_to_store:
                    # 已经通过分析文件或原始文件内容解析到了发布日期
                    info_data['publish_date'] = publish_date_to_store
                elif 'publish_date' in info_data:
                    # 保留现有的publish_date
                    publish_date_to_store = info_data['publish_date']
                elif 'crawl_time' in info_data and info_data['crawl_time']:
                    # 回退到crawl_time，假设它可能是发布日期
                    info_data['publish_date'] = info_data['crawl_time']
                    publish_date_to_store = info_data['crawl_time']
                    logger.debug(f"未找到明确的发布日期，回退使用crawl_time: {publish_date_to_store}")
                else:
                    logger.info(f"无法确定发布日期 (分析文件: {filepath}, 对应原始文件key: {raw_normalized_path})")

                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                for task in required_tasks:
                    start_tag = f"<!-- AI_TASK_START: {task} -->"
                    end_tag = f"<!-- AI_TASK_END: {task} -->"
                    error_tag = f"<!-- ERROR: "
                    
                    task_success = False
                    task_error = '任务内容不完整或缺失' # Default error message
                    # 默认使用当前时间，但如果任务已存在，则会被覆盖
                    task_timestamp = current_time_for_new_tasks 

                    if start_tag in content and end_tag in content:
                        task_content = content.split(start_tag)[1].split(end_tag)[0].strip()
                        if task_content and error_tag in task_content:
                            task_error = task_content.split(error_tag)[1].split("-->")[0].strip()
                            task_success = False
                        elif task_content: # 内容存在且没有错误标记
                            task_error = None
                            task_success = True
                        # else: 内容为空, task_success 保持 False, task_error 保持默认值
                    
                    # 检查现有元数据中是否已有此任务
                    if task in existing_tasks_data:
                        # 任务已存在，保留原有时间戳
                        task_timestamp = existing_tasks_data[task].get('timestamp', current_time_for_new_tasks)
                    # else: 新任务，使用 current_time_for_new_tasks
                        
                    tasks_status[task] = {'success': task_success, 'error': task_error, 'timestamp': task_timestamp}
                
                # 检查是否已存在记录，如果存在则记录为覆盖
                if existing_analysis_entry:
                    overwritten_analysis_metadata_count += 1
                    logger.debug(f"Overwriting existing analysis metadata for: {filepath} while preserving task timestamps where possible.")
                
                # 组装完整的更新数据
                update_data = {
                    'processed': True,
                    'tasks': tasks_status,
                    'info': info_data,
                    'last_analyzed': current_time_for_new_tasks
                }
                
                # 顶层也添加publish_date以便向后兼容
                if publish_date_to_store:
                    update_data['publish_date'] = publish_date_to_store

                logger.debug(f"[DEBUG-METADATA-SAVE] File: {filepath} - update_data before calling update_analysis_metadata: {update_data}") # ADDED DEBUG LOG
                metadata_manager.update_analysis_metadata(raw_normalized_path, update_data)
                successful_updates += 1
                logger.info(f"Successfully updated analysis metadata for: {filepath}")
            except Exception as e:
                errors.append(f"Error in {filepath}: {str(e)}")
                logger.error(f"Failed to update analysis metadata for {filepath}: {str(e)}", exc_info=True) # Added exc_info for more detail
        
        # 删除不完整或无效的文件，并清理对应的元数据记录
        for filepath, reason in files_to_delete:
            try:
                os.remove(filepath)
                deleted_files_count += 1
                log_error_red(f"已删除文件: {filepath}, 原因: {reason}")
                
                # 获取对应的原始文件路径
                raw_path = filepath.replace('/analysis/', '/raw/')
                raw_path = raw_path.replace('\\\\analysis\\', '\\\\raw\\')  # 兼容Windows路径
                raw_normalized_path = os.path.relpath(raw_path, metadata_manager.base_dir)
                
                # 从分析元数据中删除记录
                if raw_normalized_path in metadata_manager.analysis_metadata:
                    del metadata_manager.analysis_metadata[raw_normalized_path]
                    deleted_analysis_metadata_count += 1
                    logger.info(f"Removed analysis metadata record for deleted file: {raw_normalized_path}")
            except Exception as e:
                errors.append(f"Error deleting {filepath}: {str(e)}")
                logger.error(f"Failed to delete file {filepath}: {str(e)}")
        
        # 清理无效的分析元数据记录
        # 获取所有分析元数据
        all_analysis_metadata = metadata_manager.get_all_analysis_metadata()
        
        # 找出不在处理过的文件路径中的记录
        # processed_file_paths 包含的是那些在本次运行中被成功处理的、有效的原始文件的相对路径
        # 如果一个元数据键 (也是原始文件的相对路径) 不在这里面，说明它对应的分析文件可能已被删除，
        # 或者原始文件不存在，或者分析文件不完整等。
        invalid_records_to_delete = []
        for path_key in all_analysis_metadata:
            if path_key not in processed_file_paths:
                invalid_records_to_delete.append(path_key)
        
        # 删除无效记录
        if invalid_records_to_delete:
            for path_key_to_delete in invalid_records_to_delete:
                try:
                    # 从分析元数据中删除记录
                    if path_key_to_delete in metadata_manager.analysis_metadata:
                        del metadata_manager.analysis_metadata[path_key_to_delete]
                        deleted_analysis_metadata_count += 1
                        # 使用 log_error_red 并提供原因
                        reason = "对应的分析文件未在本次扫描中被更新或确认有效 (可能已被删除，或其原始文件不存在/分析不完整)"
                        log_error_red(f"删除了无效的分析元数据记录: '{path_key_to_delete}', 原因: {reason}")
                except Exception as e:
                    # 保持原有错误处理
                    errors.append(f"Error removing invalid analysis record for {path_key_to_delete}: {str(e)}")
                    logger.error(f"Failed to remove invalid analysis metadata record {path_key_to_delete}: {str(e)}")
            
            # 保存更改后的分析元数据
            metadata_manager.save_analysis_metadata()
            logger.info(f"已保存清理后的分析元数据")
    # Obsolete code removed to fix NameError
    
    if type == 'crawler':
        metadata_manager.save_crawler_metadata()
    elif type == 'analysis':
        metadata_manager.save_analysis_metadata()
    elif type == 'all':
        metadata_manager.save_crawler_metadata()
        metadata_manager.save_analysis_metadata()
    
    # 总结统计信息
    logger.info(f"重建任务总结: 处理了 {processed_files} 个文件")
    logger.info(f"成功更新: {successful_updates} 个文件")
    if type == 'crawler' or type == 'all':
        logger.info(f"覆盖爬虫元数据记录: {overwritten_crawler_metadata_count} 个")
        if deleted_crawler_metadata_count > 0:
            log_error_red(f"删除了 {deleted_crawler_metadata_count} 个无效的爬虫元数据记录")
    if type == 'analysis' or type == 'all':
        logger.info(f"覆盖分析元数据记录: {overwritten_analysis_metadata_count} 个")
        if deleted_files_count > 0:
            log_error_red(f"删除了 {deleted_files_count} 个不完整或无效的分析文件")
        if invalid_content_files_count > 0:
            log_error_red(f"删除了 {invalid_content_files_count} 个内容异常的分析文件（'假完成'问题）")
        if deleted_analysis_metadata_count > 0:
            log_error_red(f"删除了 {deleted_analysis_metadata_count} 个无效的分析元数据记录")
    
    if len(problem_files) > 0:
        log_error_red(f"检测到 {len(problem_files)} 个内容异常的分析文件，但未删除（详见日志）")
    
    if errors:
        logger.error(f"错误数: {len(errors)}")
        for error in errors:
            logger.error(f"错误详情: {error}")
    else:
        logger.info("无错误发生")
    logger.info(f"{type} 元数据重建完成")

    # 如果有检测到问题文件但选择不删除，将它们记录到日志文件中
    if deep_check and not delete_invalid and problem_files:
        try:
            with open(deep_check_log_file, 'w', encoding='utf-8') as f:
                f.write(f"# 深度检查结果 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"## 共检测到 {len(problem_files)} 个内容异常的文件\n\n")
                
                for filepath, reason in problem_files:
                    f.write(f"### 文件：{filepath}\n")
                    f.write(f"- 问题原因：{reason}\n")
                    f.write(f"- 修改时间：{datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')}\n")
                    
                    # 尝试读取文件内容的一部分，帮助用户判断问题
                    try:
                        with open(filepath, 'r', encoding='utf-8') as content_file:
                            content = content_file.read(1000)  # 只读取前1000个字符
                        f.write("\n```\n")
                        f.write(f"{content}...")
                        f.write("\n```\n\n")
                    except Exception as e:
                        f.write(f"\n无法读取文件内容：{str(e)}\n\n")
                    
                    f.write("---\n\n")
                    
            logger.info(f"已将检测到的问题文件信息写入日志文件: {deep_check_log_file}")
        except Exception as e:
            logger.error(f"写入问题文件日志时出错: {str(e)}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="重建元数据，从本地MD文件解析并更新元数据")
    parser.add_argument("--base-dir", help="项目根目录，如果未指定则使用当前目录")
    parser.add_argument("--type", default="all", help="指定元数据类型 (crawler、analysis 或 all)")
    parser.add_argument("--force_clear", action="store_true", help="强制清空原有元数据")
    parser.add_argument("--force", action="store_true", help="强制重建元数据，即使元数据已存在")
    parser.add_argument("--deep-check", action="store_true", help="深度检查分析文件内容，识别'假完成'问题")
    parser.add_argument("--delete", action="store_true", help="配合--deep-check使用，删除检测到的问题文件，否则只记录不删除")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        # 设置根 logger 级别为 DEBUG
        logging.getLogger().setLevel(logging.DEBUG)

        # 设置已存在的控制台 StreamHandler（如果有）的级别为 DEBUG
        # setup_colored_logging() 应该已经添加了一个 StreamHandler
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(logging.DEBUG)
                # 可选：为控制台handler也设置更详细的formatter
                # console_formatter = logging.Formatter(\"%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)\")
                # handler.setFormatter(console_formatter)
        
        os.makedirs("logs", exist_ok=True)
        debug_log_file = os.path.join("logs", f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        debug_handler = logging.FileHandler(debug_log_file, encoding="utf-8")
        debug_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        debug_handler.setFormatter(formatter)
        logging.getLogger().addHandler(debug_handler)
        logger.debug("调试模式已启用，控制台和文件日志均设置为DEBUG级别")
    
    # 记录深度检查模式
    if args.deep_check:
        if args.delete:
            logger.info("深度内容验证模式已启用，将检测并删除分析文件中的'假完成'问题")
        else:
            logger.info("深度内容验证模式已启用，将检测分析文件中的'假完成'问题但不删除文件")
    
    # 调用重建元数据函数
    rebuild_metadata(args.base_dir, args.type, args.force_clear, args.deep_check, args.delete)

if __name__ == "__main__":
    main()
