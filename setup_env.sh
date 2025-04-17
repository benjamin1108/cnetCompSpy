#!/bin/bash

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

echo "Python虚拟环境已激活

