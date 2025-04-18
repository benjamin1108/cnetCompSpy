#!/bin/bash
#
# 激活虚拟环境（相对于项目根目录）
cd "$(dirname "$0")/.."
source venv/bin/activate

# 传递所有参数给Python脚本，如果没有指定参数，则使用默认值
if [ $# -eq 0 ]; then
    python -m src.web_server.run --host 0.0.0.0 --port 8080
else
    python -m src.web_server.run "$@"
fi
