#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
import threading
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

def load_metadata(
    file_path: str, 
    lock: Optional[threading.RLock] = None,
    normalize_path_func: Optional[Callable[[str], str]] = None,
    update_locks_func: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    通用的元数据加载函数
    
    Args:
        file_path: 元数据文件路径
        lock: 用于确保线程安全的锁对象，如果为None则不使用锁
        normalize_path_func: 用于标准化文件路径的函数，如果为None则不标准化路径
        update_locks_func: 用于更新锁的函数，如果为None则不更新锁
        
    Returns:
        元数据字典
    """
    # 使用锁确保线程安全（如果提供了锁）
    if lock:
        lock.acquire()
    
    try:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 如果提供了更新锁的函数，则调用它
                if update_locks_func:
                    update_locks_func(data)
                
                # 如果提供了标准化路径的函数，则标准化元数据中的文件路径
                if normalize_path_func and isinstance(data, dict):
                    normalized_data = {}
                    for key, value in data.items():
                        normalized_key = normalize_path_func(key)
                        normalized_data[normalized_key] = value
                        # 如果标准化后的键与原始键不同，记录日志
                        if normalized_key != key:
                            logger.debug(f"元数据路径标准化: {key} -> {normalized_key}")
                    return normalized_data
                
                return data
            except Exception as e:
                logger.warning(f"加载元数据文件失败: {file_path} - {e}")
                return {}
        return {}
    finally:
        # 确保在函数返回前释放锁
        if lock:
            lock.release()

def save_metadata(
    file_path: str, 
    metadata: Dict[str, Any], 
    lock: Optional[threading.RLock] = None,
    normalize_path_func: Optional[Callable[[str], str]] = None
) -> None:
    """
    通用的元数据保存函数
    
    Args:
        file_path: 元数据文件路径
        metadata: 要保存的元数据字典
        lock: 用于确保线程安全的锁对象，如果为None则不使用锁
        normalize_path_func: 用于标准化文件路径的函数，如果为None则不标准化路径
    """
    # 使用锁确保线程安全（如果提供了锁）
    if lock:
        lock.acquire()
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 如果提供了标准化路径的函数，则标准化元数据中的文件路径
        if normalize_path_func and isinstance(metadata, dict):
            normalized_metadata = {}
            for key, value in metadata.items():
                normalized_key = normalize_path_func(key)
                # 更新文件数据中的file字段，确保与键一致
                if isinstance(value, dict) and 'file' in value:
                    value['file'] = normalized_key
                normalized_metadata[normalized_key] = value
            metadata_to_save = normalized_metadata
        else:
            metadata_to_save = metadata
        
        # 使用临时文件写入，然后重命名，确保原子性写入
        temp_file = f"{file_path}.tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_to_save, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())  # 确保数据写入磁盘
        
        # 重命名临时文件为正式文件，这是一个原子操作
        os.replace(temp_file, file_path)
        
        # 确保正式文件权限正确
        os.chmod(file_path, 0o666)  # 所有用户可读写
        
        logger.debug(f"元数据已保存到: {file_path}")
    except Exception as e:
        logger.error(f"保存元数据文件失败: {file_path} - {e}")
    finally:
        # 确保在函数返回前释放锁
        if lock:
            lock.release()
