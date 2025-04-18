#!/bin/bash

# 获取脚本所在目录和项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 检查是否存在名为venv的conda环境
if conda env list | grep -q "^venv "; then
    echo "找到venv环境，正在激活..."
    eval "$(conda shell.bash hook)"
    conda activate venv
else
    echo "未找到venv环境，正在创建..."
    eval "$(conda shell.bash hook)"
    conda create -y -n venv python=3.11
    echo "venv环境已创建，正在激活..."
    conda activate venv
fi

echo "Python虚拟环境已激活"

# 安装依赖
echo "正在安装项目依赖..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "依赖安装成功"
else
    echo "依赖安装失败，请检查网络连接和requirements.txt文件"
    exit 1
fi

echo "环境设置完成"
