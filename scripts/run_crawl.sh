#!/bin/bash
#
# 激活虚拟环境（相对于项目根目录）
cd "$(dirname "$0")/.."
source venv/bin/activate

# 检查是否有--force参数
FORCE_FLAG=""
if [[ "$*" == *"--force"* ]]; then
    FORCE_FLAG="--force"
fi

# 传递所有参数给Python脚本，如果指定了--force，则添加force标志
python -m src.main --mode crawl $FORCE_FLAG "$@"
