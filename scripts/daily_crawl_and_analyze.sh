#!/bin/bash

# 云计算网络竞争动态分析工具 - 每日自动爬取与分析脚本
# 此脚本用于每日自动运行爬虫功能，并在爬虫完成后调用分析功能

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # 无颜色

# 获取脚本所在目录和项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 日志文件设置
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/daily_crawl_analyze_$TIMESTAMP.log"

# 日志函数
log() {
    local level="$1"
    local message="$2"
    local color=""
    
    case "$level" in
        "INFO") color="$GREEN" ;;
        "WARNING") color="$YELLOW" ;;
        "ERROR") color="$RED" ;;
        *) color="$NC" ;;
    esac
    
    echo -e "${color}[$(date +'%Y-%m-%d %H:%M:%S')] [$level] $message${NC}" | tee -a "$LOG_FILE"
}

# 激活虚拟环境
activate_venv() {
    log "INFO" "正在激活Python虚拟环境..."
    # 使用venv.sh脚本激活conda环境
    source "$SCRIPT_DIR/venv.sh" > /dev/null
    if [ $? -eq 0 ]; then
        log "INFO" "Python虚拟环境已激活"
        return 0
    else
        log "ERROR" "激活Python虚拟环境失败"
        return 1
    fi
}

# 运行爬虫功能
run_crawler() {
    log "INFO" "开始运行爬虫功能..."
    
    # 解析命令行参数
    local crawler_args=""
    while [[ $# -gt 0 ]]; do
        crawler_args="$crawler_args $1"
        shift
    done
    
    # 运行爬虫，并将输出重定向到日志文件
    log "INFO" "执行命令: python -m src.main --mode crawl $crawler_args"
    python -m src.main --mode crawl $crawler_args 2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        log "INFO" "爬虫功能成功完成"
        return 0
    else
        log "ERROR" "爬虫功能执行失败，退出代码: $exit_code"
        return $exit_code
    fi
}

# 运行分析功能
run_analyzer() {
    log "INFO" "开始运行分析功能..."
    
    # 初始化参数
    local analyzer_args=""
    local limit_flag=""
    local limit_value=""
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        # 检查是否有--limit参数
        if [[ "$1" == "--limit" ]]; then
            limit_flag="--limit"
            if [[ $# -gt 1 ]]; then
                limit_value="$2"
                shift 2
            else
                shift
            fi
        else
            analyzer_args="$analyzer_args $1"
            shift
        fi
    done
    
    # 构建完整的命令参数
    local full_args="$analyzer_args"
    if [[ "$limit_flag" != "" && "$limit_value" != "" ]]; then
        full_args="$full_args $limit_flag $limit_value"
        log "INFO" "设置分析文件数量限制为: $limit_value"
    fi
    
    # 运行分析，并将输出重定向到日志文件
    log "INFO" "执行命令: python -m src.main --mode analyze $full_args"
    python -m src.main --mode analyze $full_args 2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        log "INFO" "分析功能成功完成"
        return 0
    else
        log "ERROR" "分析功能执行失败，退出代码: $exit_code"
        return $exit_code
    fi
}

# 发送通知
send_notification() {
    local status="$1"
    local message="$2"
    
    log "INFO" "通知: $status - $message"
    
    # 使用Python邮件通知模块发送通知
    if [ -f "$PROJECT_ROOT/src/utils/email_notifier.py" ]; then
        log "INFO" "正在使用Python邮件通知模块发送通知..."
        
        # 检查敏感配置文件是否存在
        SECRET_CONFIG="$PROJECT_ROOT/config.secret.yaml"
        SECRET_CONFIG_PARAM=""
        if [ -f "$SECRET_CONFIG" ]; then
            log "INFO" "找到敏感配置文件: $SECRET_CONFIG"
            SECRET_CONFIG_PARAM="--secret-config $SECRET_CONFIG"
        else
            log "WARNING" "未找到敏感配置文件，邮件发送可能会失败"
        fi
        
        python -m src.utils.email_notifier --status "$status" --message "$message" --log-file "$LOG_FILE" $SECRET_CONFIG_PARAM
        
        if [ $? -eq 0 ]; then
            log "INFO" "邮件通知发送成功"
        else
            log "WARNING" "邮件通知发送失败，这可能是因为邮件功能未启用或配置不正确"
        fi
    else
        log "WARNING" "未找到邮件通知模块，跳过发送邮件"
    fi
}

# 主函数
main() {
    log "INFO" "===== 开始每日爬取与分析任务 ====="
    
    # 激活虚拟环境
    activate_venv
    if [ $? -ne 0 ]; then
        send_notification "失败" "无法激活Python虚拟环境"
        log "ERROR" "任务终止"
        exit 1
    fi
    
    # 运行爬虫
    log "INFO" "开始爬取数据..."
    run_crawler "$@"
    local crawler_exit_code=$?
    
    # 检查爬虫是否成功
    if [ $crawler_exit_code -ne 0 ]; then
        send_notification "失败" "爬虫功能执行失败，无法继续执行分析"
        log "ERROR" "由于爬虫失败，任务终止"
        exit $crawler_exit_code
    fi
    
    # 运行分析
    log "INFO" "爬虫成功完成，开始分析数据..."
    run_analyzer "$@"
    local analyzer_exit_code=$?
    
    # 检查分析是否成功
    if [ $analyzer_exit_code -ne 0 ]; then
        send_notification "部分成功" "爬虫成功完成，但分析功能执行失败"
        log "ERROR" "分析失败，任务部分完成"
        exit $analyzer_exit_code
    fi
    
    # 任务成功完成
    send_notification "成功" "每日爬取与分析任务成功完成"
    log "INFO" "===== 每日爬取与分析任务成功完成 ====="
    exit 0
}

# 执行主函数，传递所有命令行参数
main "$@"
