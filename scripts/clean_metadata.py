#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys

# 添加项目根目录到路径
base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, base_dir)

def normalize_file_path(file_path: str) -> str:
    """
    标准化文件路径，确保使用相对路径
    
    Args:
        file_path: 文件路径（可能是相对路径或绝对路径）
        
    Returns:
        标准化后的文件路径（相对于项目根目录）
    """
    # 获取项目根目录的绝对路径
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # 如果是绝对路径，转换为相对于项目根目录的路径
    if os.path.isabs(file_path):
        try:
            # 尝试将绝对路径转换为相对于项目根目录的路径
            rel_path = os.path.relpath(file_path, base_dir)
            print(f"将绝对路径 {file_path} 转换为相对路径 {rel_path}")
            return rel_path
        except ValueError:
            # 如果路径在不同的驱动器上（Windows），则保留原始路径
            print(f"无法将路径 {file_path} 转换为相对路径，保留原始路径")
            return file_path
    
    return file_path

def clean_metadata(metadata_file: str) -> None:
    """
    清理元数据文件，将所有绝对路径转换为相对路径
    
    Args:
        metadata_file: 元数据文件路径
    """
    # 检查文件是否存在
    if not os.path.exists(metadata_file):
        print(f"元数据文件不存在: {metadata_file}")
        return
    
    # 加载元数据
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"已加载元数据: {len(metadata)} 条记录")
    except Exception as e:
        print(f"加载元数据失败: {e}")
        return
    
    # 标准化元数据中的文件路径
    normalized_metadata = {}
    for file_path, file_data in metadata.items():
        normalized_path = normalize_file_path(file_path)
        # 更新文件数据中的file字段，确保与键一致
        if 'file' in file_data:
            file_data['file'] = normalized_path
        normalized_metadata[normalized_path] = file_data
    
    # 保存标准化后的元数据
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(normalized_metadata, f, ensure_ascii=False, indent=2)
        print(f"已保存标准化后的元数据: {len(normalized_metadata)} 条记录")
    except Exception as e:
        print(f"保存元数据失败: {e}")

if __name__ == "__main__":
    # 默认元数据文件路径
    metadata_file = os.path.join(base_dir, "data", "metadata", "analysis_metadata.json")
    
    # 如果提供了命令行参数，使用指定的元数据文件路径
    if len(sys.argv) > 1:
        metadata_file = sys.argv[1]
    
    print(f"清理元数据文件: {metadata_file}")
    clean_metadata(metadata_file)
