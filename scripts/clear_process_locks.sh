#!/bin/bash

# 清除进程锁脚本
# 用于手动清除进程锁，防止系统因进程异常退出而锁死

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 导入Python环境
cd "$PROJECT_ROOT"

# 显示帮助信息
show_help() {
    echo "进程锁管理工具"
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  -s, --status   显示所有锁的状态"
    echo "  -c, --clear    清除所有锁"
    echo "  --clear-crawler 清除爬虫锁"
    echo "  --clear-analyzer 清除分析器锁"
    echo "  --clear-webserver 清除Web服务器锁"
}

# 显示锁状态
show_status() {
    echo "检查进程锁状态..."
    python -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from src.utils.process_lock_manager import ProcessLockManager, ProcessType
import json

status = ProcessLockManager.check_lock_status()
print(json.dumps(status, indent=2))
"
}

# 清除所有锁
clear_all_locks() {
    echo "清除所有进程锁..."
    python -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from src.utils.process_lock_manager import ProcessLockManager, ProcessType

for process_type in ProcessType:
    if ProcessLockManager.force_clear_lock_by_type(process_type):
        print(f'已清除 {process_type.name} 锁')
    else:
        print(f'清除 {process_type.name} 锁失败')
"
}

# 清除特定类型的锁
clear_lock_by_type() {
    local type=$1
    echo "清除 $type 进程锁..."
    python -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from src.utils.process_lock_manager import ProcessLockManager, ProcessType

process_type = ProcessType.$type
if ProcessLockManager.force_clear_lock_by_type(process_type):
    print(f'已清除 {process_type.name} 锁')
else:
    print(f'清除 {process_type.name} 锁失败')
"
}

# 解析命令行参数
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--status)
            show_status
            exit 0
            ;;
        -c|--clear)
            clear_all_locks
            exit 0
            ;;
        --clear-crawler)
            clear_lock_by_type "CRAWLER"
            exit 0
            ;;
        --clear-analyzer)
            clear_lock_by_type "ANALYZER"
            exit 0
            ;;
        --clear-webserver)
            clear_lock_by_type "WEB_SERVER"
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
    shift
done
