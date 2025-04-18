#!/bin/bash

# 获取脚本所在目录和项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 检查当前目录是否存在venv目录
if [ -d "venv" ]; then
    echo "找到venv目录，正在激活..."
    source venv/bin/activate
else
    echo "未找到venv目录，正在创建..."
    python3 -m venv venv
    echo "venv目录已创建，正在激活..."
    source venv/bin/activate
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
