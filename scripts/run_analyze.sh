#!/bin/bash
#
# 激活虚拟环境（相对于项目根目录）
cd "$(dirname "$0")/.."
source "$(dirname "$0")/venv.sh"

# 初始化参数
FORCE_FLAG=""
FILE_FLAG=""
FILE_PATH=""
LIMIT_FLAG=""
LIMIT_VALUE=""

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
    # 检查是否有--limit参数
    elif [[ "$arg" == "--limit" ]]; then
        LIMIT_FLAG="--limit"
    # 如果前一个参数是--limit，则当前参数是限制数量
    elif [[ "$LIMIT_FLAG" == "--limit" && "$LIMIT_VALUE" == "" ]]; then
        LIMIT_VALUE="$arg"
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

# 添加limit标志和值
if [[ "$LIMIT_FLAG" != "" && "$LIMIT_VALUE" != "" ]]; then
    CMD="$CMD $LIMIT_FLAG $LIMIT_VALUE"
fi

# 添加file标志和路径
if [[ "$FILE_FLAG" != "" && "$FILE_PATH" != "" ]]; then
    CMD="$CMD $FILE_FLAG $FILE_PATH"
else
    # 如果没有指定文件，则传递所有原始参数
    # 但如果已经处理了force和limit参数，则不要重复传递
    if [[ "$FORCE_FLAG" != "" || "$LIMIT_FLAG" != "" ]]; then
        # 过滤掉已处理的参数
        FILTERED_ARGS=""
        SKIP_NEXT=false
        for arg in "$@"; do
            if $SKIP_NEXT; then
                SKIP_NEXT=false
                continue
            fi
            
            if [[ "$arg" == "--force" ]]; then
                continue
            elif [[ "$arg" == "--limit" ]]; then
                SKIP_NEXT=true
                continue
            else
                FILTERED_ARGS="$FILTERED_ARGS $arg"
            fi
        done
        
        CMD="$CMD$FILTERED_ARGS"
    else
        # 如果没有处理任何参数，则传递所有原始参数
        CMD="$CMD $*"
    fi
fi

# 执行命令
echo "执行命令: $CMD"
eval $CMD
