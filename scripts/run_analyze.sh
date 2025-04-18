#!/bin/bash
#
# 激活虚拟环境（相对于项目根目录）
cd "$(dirname "$0")/.."
source venv/bin/activate

# 初始化参数
FORCE_FLAG=""
FILE_FLAG=""
FILE_PATH=""

# 解析参数
for arg in "$@"; do
    # 检查是否有--force参数
    if [[ "$arg" == "--force" ]]; then
        FORCE_FLAG="--force"
    # 检查是否有--file参数
    elif [[ "$arg" == "--file" ]]; then
        FILE_FLAG="--file"
    # 如果前一个参数是--file，则当前参数是文件路径
    elif [[ "$FILE_FLAG" == "--file" && "$FILE_PATH" == "" ]]; then
        FILE_PATH="$arg"
    fi
done

# 如果指定了文件路径但没有--file标志，则添加--file标志
if [[ "$FILE_PATH" == "" && -f "$1" ]]; then
    FILE_FLAG="--file"
    FILE_PATH="$1"
fi

# 构建命令
CMD="python -m src.main --mode analyze"

# 添加force标志
if [[ "$FORCE_FLAG" != "" ]]; then
    CMD="$CMD $FORCE_FLAG"
fi

# 添加file标志和路径
if [[ "$FILE_FLAG" != "" && "$FILE_PATH" != "" ]]; then
    CMD="$CMD $FILE_FLAG $FILE_PATH"
else
    # 传递所有原始参数
    CMD="$CMD $*"
fi

# 执行命令
echo "执行命令: $CMD"
eval $CMD
