#!/bin/bash

# SQLite备份脚本
# 用于定时运行SQLite备份

# 项目根目录
PROJECT_ROOT=$(dirname "$(dirname "$(readlink -f "$0")")")
cd "$PROJECT_ROOT" || exit 1

# 日志路径
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/sqlite_backup_$(date +%Y%m%d).log"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 记录日志的函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查是否有另一个备份正在运行
PID_FILE="/tmp/sqlite_backup.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null; then
        log "错误: 另一个备份进程 (PID: $PID) 正在运行，退出"
        exit 1
    else
        log "警告: 发现过期的PID文件，将继续执行"
    fi
fi

# 写入当前PID
echo $$ > "$PID_FILE"

# 清理函数
cleanup() {
    log "清理临时文件"
    rm -f "$PID_FILE"
    exit $1
}

# 捕获退出信号
trap 'cleanup 1' INT TERM

log "开始SQLite备份"

# 激活虚拟环境(如果存在)
if [ -d "venv" ]; then
    log "激活虚拟环境"
    source venv/bin/activate
fi

# 运行备份脚本
log "运行SQLite备份脚本"
python scripts/sqlite_backup.py
BACKUP_STATUS=$?

if [ $BACKUP_STATUS -eq 0 ]; then
    log "SQLite备份完成"
else
    log "SQLite备份失败，错误码: $BACKUP_STATUS"
fi

# 删除超过30天的备份日志
log "清理旧的备份日志"
find "$LOG_DIR" -name "sqlite_backup_*.log" -type f -mtime +30 -delete

# 清理并退出
cleanup $BACKUP_STATUS 