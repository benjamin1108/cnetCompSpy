#!/bin/bash

# 检查当前目录是否存在venv目录
if [ -d "venv" ]; then
    echo "找到venv目录，正在激活..."
    source ./venv/bin/activate
else
    echo "未找到venv目录，正在创建..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo "venv目录已创建，正在激活..."
        source ./venv/bin/activate
    else
        echo "创建venv失败，请检查python3和venv模块是否可用。"
        exit 1
    fi
fi

echo "Python虚拟环境已激活"
