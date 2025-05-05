#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import logging
from typing import Dict, Any, List, Optional
from copy import deepcopy

logger = logging.getLogger(__name__)

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    深度合并配置字典
    
    Args:
        base_config: 基础配置字典
        override_config: 覆盖配置字典
        
    Returns:
        合并后的配置字典
    """
    result = deepcopy(base_config)
    
    for key, value in override_config.items():
        # 如果键存在且两个值都是字典，则递归合并
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            # 否则直接覆盖或添加
            result[key] = value
            
    return result

def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    加载YAML文件
    
    Args:
        file_path: YAML文件路径
        
    Returns:
        Dict: YAML文件内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        logger.warning(f"配置文件不存在: {file_path}")
        return {}
    except Exception as e:
        logger.error(f"加载配置文件时出错: {e}")
        return {}

def load_config_directory(config_dir: str) -> Dict[str, Any]:
    """
    加载配置目录中的所有配置文件
    
    Args:
        config_dir: 配置文件目录路径
        
    Returns:
        Dict: 合并后的配置字典
    """
    # 先查找main.yaml作为主配置文件
    main_config_path = os.path.join(config_dir, 'main.yaml')
    if not os.path.exists(main_config_path):
        # 如果没有main.yaml，则按字母顺序加载所有yaml文件
        logger.warning(f"在配置目录 {config_dir} 中未找到main.yaml，将按字母顺序加载所有yaml文件")
        return load_all_yaml_files(config_dir)
    
    # 加载main.yaml
    main_config = load_yaml_file(main_config_path)
    
    # 检查main.yaml中是否有imports字段
    if 'imports' not in main_config:
        logger.warning(f"main.yaml中没有imports字段，将仅使用main.yaml中的配置")
        return main_config
    
    # 创建最终合并的配置
    final_config = {}
    
    # 按照imports列表顺序加载配置文件
    for import_file in main_config.get('imports', []):
        import_path = os.path.join(config_dir, import_file)
        if os.path.exists(import_path):
            config_data = load_yaml_file(import_path)
            final_config = merge_configs(final_config, config_data)
            logger.info(f"已加载配置文件: {import_file}")
        else:
            logger.warning(f"导入的配置文件不存在: {import_path}")
    
    # 移除imports字段，避免干扰实际配置
    if 'imports' in main_config:
        del main_config['imports']
    
    # 将main.yaml中的其他配置合并到最终配置中
    if main_config:
        final_config = merge_configs(final_config, main_config)
    
    return final_config

def load_all_yaml_files(config_dir: str) -> Dict[str, Any]:
    """
    按字母顺序加载目录中的所有yaml文件
    
    Args:
        config_dir: 配置文件目录路径
        
    Returns:
        Dict: 合并后的配置字典
    """
    merged_config = {}
    
    # 获取目录中所有的yaml文件，并按字母顺序排序
    yaml_files = sorted([f for f in os.listdir(config_dir) 
                         if f.endswith('.yaml') or f.endswith('.yml')])
    
    # 依次加载每个文件
    for yaml_file in yaml_files:
        file_path = os.path.join(config_dir, yaml_file)
        try:
            config_data = load_yaml_file(file_path)
            merged_config = merge_configs(merged_config, config_data)
            logger.info(f"已加载配置文件: {yaml_file}")
        except Exception as e:
            logger.warning(f"加载配置文件 {yaml_file} 失败: {e}")
    
    return merged_config

def get_config(base_dir: Optional[str] = None, config_path: Optional[str] = None, default_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    加载配置，优先级：
    1. 指定的配置文件或目录 (config_path)
    2. 项目根目录下的 config 目录
    3. 项目根目录下的 config.yaml 文件
    4. 默认配置 (default_config)
    
    Args:
        base_dir: 项目根目录路径，如果为None则自动确定
        config_path: 指定的配置文件或目录路径
        default_config: 默认配置字典
        
    Returns:
        Dict: 加载的配置字典
    """
    # 如果没有提供默认配置，使用空字典
    if default_config is None:
        default_config = {}
    
    config = deepcopy(default_config)
    
    # 如果没有提供项目根目录，自动确定
    if base_dir is None:
        # 获取当前文件所在目录的上一级目录的上一级目录（即项目根目录）
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    # 如果提供了指定的配置路径
    if config_path:
        # 处理相对路径
        if not os.path.isabs(config_path):
            config_path = os.path.abspath(os.path.join(base_dir, config_path))
        
        # 判断是文件还是目录
        if os.path.isdir(config_path):
            logger.info(f"从指定的配置目录加载: {config_path}")
            config_data = load_config_directory(config_path)
        else:
            logger.info(f"从指定的配置文件加载: {config_path}")
            config_data = load_yaml_file(config_path)
        
        # 合并配置
        config = merge_configs(config, config_data)
    else:
        # 尝试从config目录加载
        config_dir = os.path.join(base_dir, 'config')
        if os.path.exists(config_dir) and os.path.isdir(config_dir):
            logger.info(f"从配置目录加载: {config_dir}")
            config_data = load_config_directory(config_dir)
            config = merge_configs(config, config_data)
        else:
            # 回退到从单一配置文件加载
            config_file = os.path.join(base_dir, 'config.yaml')
            if os.path.exists(config_file):
                logger.info(f"从配置文件加载: {config_file}")
                config_data = load_yaml_file(config_file)
                config = merge_configs(config, config_data)
            else:
                logger.warning(f"未找到配置文件或目录，使用默认配置")
    
    # 加载敏感配置文件
    secret_config_path = os.path.join(base_dir, 'config.secret.yaml')
    if os.path.exists(secret_config_path):
        logger.info(f"加载敏感配置文件: {secret_config_path}")
        secret_config_data = load_yaml_file(secret_config_path)
        config = merge_configs(config, secret_config_data)
    
    return config 