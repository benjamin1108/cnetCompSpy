#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"错误: 需要Python {required_version[0]}.{required_version[1]}或更高版本")
        print(f"当前版本: {current_version[0]}.{current_version[1]}.{current_version[2]}")
        return False
    
    return True

def check_conda():
    """检查是否安装了conda"""
    try:
        subprocess.check_output(["conda", "--version"], stderr=subprocess.STDOUT)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def create_conda_env():
    """创建conda环境"""
    try:
        # 检查是否存在名为venv的conda环境
        result = subprocess.run(["conda", "env", "list"], capture_output=True, text=True)
        if "venv" in result.stdout:
            print("找到venv环境，正在激活...")
        else:
            print("未找到venv环境，正在创建...")
            subprocess.check_call(["conda", "create", "-y", "-n", "venv", "python=3.11"])
        
        # 激活环境并安装依赖
        if platform.system() == "Windows":
            activate_cmd = ["conda", "activate", "venv", "&&"]
        else:
            # 在Linux/Mac上，需要通过source激活环境，这需要在shell中执行
            print("请手动激活conda环境: conda activate venv")
            print("然后运行: pip install -r requirements.txt")
            return True
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"创建conda环境失败: {e}")
        return False

def check_dependencies():
    """检查系统依赖"""
    system = platform.system()
    
    if system == "Linux":
        # 在Linux上检查必要的依赖
        dependencies = [
            "libatk1.0-0", "libatk-bridge2.0-0", "libasound2", "libcups2",
            "libdrm2", "libgtk-3-0", "libgbm1", "libnss3"
        ]
        
        missing = []
        for dep in dependencies:
            try:
                subprocess.check_call(["dpkg", "-s", dep], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                missing.append(dep)
        
        if missing:
            print("警告: 以下系统依赖可能缺失:")
            for dep in missing:
                print(f"  - {dep}")
            print("这些依赖可能是运行Chrome headless所必需的。")
    
    return True

def install_requirements():
    """安装项目依赖"""
    project_root = Path(__file__).resolve().parent.parent.parent
    requirements_file = project_root / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"错误: 找不到requirements.txt文件: {requirements_file}")
        return False
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        print("依赖安装成功")
        return True
    except subprocess.CalledProcessError:
        print("依赖安装失败")
        return False

def setup_environment():
    """设置环境"""
    if not check_python_version():
        return 1
    
    # 检查conda
    if check_conda():
        print("检测到conda已安装")
        if not create_conda_env():
            return 1
    else:
        print("未检测到conda，将使用系统Python")
    
    if not check_dependencies():
        print("警告: 系统依赖检查失败，但将继续执行")
    
    if not install_requirements():
        return 1
    
    print("环境设置完成")
    return 0

if __name__ == "__main__":
    sys.exit(setup_environment())
