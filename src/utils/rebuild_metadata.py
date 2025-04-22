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
        
        # 提取URL（假设内容中有URL字段）
        url_match = re.search(r'URL: (.+)', content)
        url = url_match.group(1) if url_match else ''
        
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
    检查分析文件是否完整，包含所有必要的AI任务且任务成功完成
    
    Args:
        filepath: 分析文件路径
        required_tasks: 必要的AI任务列表
        
    Returns:
        检查结果字典，包含是否完整、缺失任务列表等信息
    """
    result = {
        'is_complete': True,
        'missing_tasks': [],
        'incomplete_tasks': [],
        'failed_tasks': [],
        'reason': None
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查每个必要任务是否存在且完整
        for task in required_tasks:
            start_tag = f"<!-- AI_TASK_START: {task} -->"
            end_tag = f"<!-- AI_TASK_END: {task} -->"
            error_tag = f"<!-- ERROR: "
            
            if start_tag not in content:
                result['is_complete'] = False
                result['missing_tasks'].append(task)
                continue
                
            if end_tag not in content:
                result['is_complete'] = False
                result['incomplete_tasks'].append(task)
                continue
                
            # 检查任务内容是否为空
            task_content = content.split(start_tag)[1].split(end_tag)[0].strip()
            if not task_content:
                result['is_complete'] = False
                result['incomplete_tasks'].append(task)
                continue
                
            # 检查任务是否失败
            if error_tag in task_content:
                result['is_complete'] = False
                result['failed_tasks'].append(task)
        
        # 设置原因
        if result['missing_tasks']:
            result['reason'] = f"缺少任务: {', '.join(result['missing_tasks'])}"
        elif result['incomplete_tasks']:
            result['reason'] = f"任务未完成: {', '.join(result['incomplete_tasks'])}"
        elif result['failed_tasks']:
            result['reason'] = f"任务执行失败: {', '.join(result['failed_tasks'])}"
            
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
    config_path = os.path.join(base_dir, 'config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 从配置中提取任务列表
        tasks = [task.get('type') for task in config.get('ai_analyzer', {}).get('tasks', [])]
        return [task for task in tasks if task]  # 过滤掉None值
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
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
        # 检查标题是否包含预期的标签前缀
        if not (content.startswith("[解决方案]") or 
                content.startswith("[新产品/新功能]") or 
                content.startswith("[新产品]") or 
                content.startswith("[新功能]") or
                content.startswith("[产品更新]") or
                content.startswith("[技术更新]") or
                content.startswith("[案例分析]")):
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
        expected_sections = ["概述", "方案", "价值", "产品", "评估"]
        section_count = 0
        
        for section in expected_sections:
            if section in content:
                section_count += 1
                
        if section_count < 3:  # 至少应包含3个预期章节
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
                    # 使用URL作为键更新元数据
                    url_key = metadata['url'] if metadata['url'] else filepath
                    # 检查是否已存在记录，如果存在则记录为覆盖
                    all_crawler_metadata = metadata_manager.get_all_crawler_metadata()
                    if vendor in all_crawler_metadata and source_type in all_crawler_metadata[vendor] and url_key in all_crawler_metadata[vendor][source_type]:
                        overwritten_crawler_metadata_count += 1
                        logger.debug(f"Overwriting existing crawler metadata for: {filepath}")
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
                raw_path = raw_path.replace('\\analysis\\', '\\raw\\')  # 兼容Windows路径
                
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
                raw_normalized_path = os.path.relpath(raw_path, metadata_manager.base_dir)
                processed_file_paths.add(raw_normalized_path)
                
                # 更新分析元数据，读取任务的实际状态和错误信息
                tasks_status = {}
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                for task in required_tasks:
                    start_tag = f"<!-- AI_TASK_START: {task} -->"
                    end_tag = f"<!-- AI_TASK_END: {task} -->"
                    error_tag = f"<!-- ERROR: "
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    if start_tag in content and end_tag in content:
                        task_content = content.split(start_tag)[1].split(end_tag)[0].strip()
                        if task_content and error_tag in task_content:
                            error_message = task_content.split(error_tag)[1].split("-->")[0].strip()
                            tasks_status[task] = {'success': False, 'error': error_message, 'timestamp': timestamp}
                        else:
                            tasks_status[task] = {'success': True, 'error': None, 'timestamp': timestamp}
                    else:
                        tasks_status[task] = {'success': False, 'error': '任务内容不完整或缺失', 'timestamp': timestamp}
                
                # 检查是否已存在记录，如果存在则记录为覆盖
                if raw_normalized_path in metadata_manager.analysis_metadata:
                    overwritten_analysis_metadata_count += 1
                    logger.debug(f"Overwriting existing analysis metadata for: {filepath}")
                metadata_manager.update_analysis_metadata(raw_normalized_path, {
                    'processed': True,
                    'tasks': tasks_status
                })
                successful_updates += 1
                logger.info(f"Successfully updated analysis metadata for: {filepath}")
            except Exception as e:
                errors.append(f"Error in {filepath}: {str(e)}")
                logger.error(f"Failed to update analysis metadata for {filepath}: {str(e)}")
        
        # 删除不完整或无效的文件，并清理对应的元数据记录
        for filepath, reason in files_to_delete:
            try:
                os.remove(filepath)
                deleted_files_count += 1
                log_error_red(f"已删除文件: {filepath}, 原因: {reason}")
                
                # 获取对应的原始文件路径
                raw_path = filepath.replace('/analysis/', '/raw/')
                raw_path = raw_path.replace('\\analysis\\', '\\raw\\')  # 兼容Windows路径
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
        invalid_records = [path for path in all_analysis_metadata if path not in processed_file_paths]
        
        # 删除无效记录
        if invalid_records:
            for path in invalid_records:
                try:
                    # 从分析元数据中删除记录
                    if path in metadata_manager.analysis_metadata:
                        del metadata_manager.analysis_metadata[path]
                        deleted_analysis_metadata_count += 1
                        logger.info(f"Removed invalid analysis metadata record: {path}")
                except Exception as e:
                    errors.append(f"Error removing invalid record {path}: {str(e)}")
                    logger.error(f"Failed to remove invalid analysis metadata record {path}: {str(e)}")
            
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
        logging.getLogger().setLevel(logging.DEBUG)
        os.makedirs("logs", exist_ok=True)
        debug_log_file = os.path.join("logs", f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        debug_handler = logging.FileHandler(debug_log_file, encoding="utf-8")
        debug_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        debug_handler.setFormatter(formatter)
        logging.getLogger().addHandler(debug_handler)
        logger.debug("调试模式已启用")
    
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
