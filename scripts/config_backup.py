#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置备份和迁移工具

这个脚本用于：
1. 备份当前的 config.yaml 到 config.yaml.bak
2. 测试新的配置系统是否正常工作
"""

import os
import sys
import shutil
import yaml
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
sys.path.insert(0, base_dir)

def backup_config_file():
    """备份当前的配置文件"""
    config_file = os.path.join(base_dir, 'config.yaml')
    if not os.path.exists(config_file):
        print(f"警告: 配置文件不存在: {config_file}")
        return False
    
    # 创建带有时间戳的备份文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{config_file}.bak.{timestamp}"
    
    try:
        shutil.copy2(config_file, backup_file)
        print(f"已备份配置文件到: {backup_file}")
        return True
    except Exception as e:
        print(f"备份配置文件失败: {e}")
        return False

def test_new_config_system():
    """测试新的配置系统是否正常工作"""
    try:
        from src.utils.config_loader import get_config
        
        # 尝试从原始配置文件加载配置
        print("\n1. 从原始配置文件加载配置:")
        original_config = get_config(config_path=os.path.join(base_dir, 'config.yaml'))
        print(f"成功加载原始配置文件，包含 {len(original_config)} 个顶级配置项")
        
        # 尝试从配置目录加载配置
        print("\n2. 从配置目录加载配置:")
        directory_config = get_config(config_path=os.path.join(base_dir, 'config'))
        print(f"成功加载配置目录，包含 {len(directory_config)} 个顶级配置项")
        
        # 比较两种配置
        print("\n3. 配置比较:")
        original_keys = set(original_config.keys())
        directory_keys = set(directory_config.keys())
        
        print(f"原始配置顶级键: {', '.join(sorted(original_keys))}")
        print(f"目录配置顶级键: {', '.join(sorted(directory_keys))}")
        
        missing_keys = original_keys - directory_keys
        if missing_keys:
            print(f"警告: 目录配置中缺少以下键: {', '.join(sorted(missing_keys))}")
        
        extra_keys = directory_keys - original_keys
        if extra_keys:
            print(f"信息: 目录配置中新增了以下键: {', '.join(sorted(extra_keys))}")
        
        # 检查配置内容是否一致
        common_keys = original_keys.intersection(directory_keys)
        conflicts = []
        
        for key in common_keys:
            if key in original_config and key in directory_config:
                if isinstance(original_config[key], dict) and isinstance(directory_config[key], dict):
                    # 对于字典，我们可以简单地比较键的数量
                    if len(original_config[key]) != len(directory_config[key]):
                        conflicts.append(key)
                elif original_config[key] != directory_config[key]:
                    conflicts.append(key)
        
        if conflicts:
            print(f"警告: 以下配置项在两种配置中不一致: {', '.join(conflicts)}")
        else:
            print("成功: 共有配置项在两种配置中一致")
        
        return True
    except Exception as e:
        print(f"测试配置系统失败: {e}")
        return False

def main():
    """主函数"""
    print("=== 配置备份和迁移工具 ===")
    
    # 备份配置文件
    print("\n[步骤1] 备份当前配置文件")
    backup_success = backup_config_file()
    
    if not backup_success:
        print("警告: 跳过备份步骤")
    
    # 测试新配置系统
    print("\n[步骤2] 测试新配置系统")
    test_success = test_new_config_system()
    
    if test_success:
        print("\n配置系统测试完成，可以安全使用新的配置系统")
    else:
        print("\n警告: 新配置系统测试失败，请检查日志并修复问题")
    
    return 0 if test_success else 1

if __name__ == "__main__":
    sys.exit(main()) 