#!/bin/bash

# 云计算网络竞争动态分析工具 - 每日自动爬取与分析脚本
# 此脚本用于每日自动运行爬虫功能，并在爬虫完成后调用分析功能

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 获取项目根目录
ROOT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 默认参数
NO_EMAIL=false
NO_STATS=false
NO_CRAWL=false
NO_ANALYZE=false
NO_DINGTALK=true  # 默认不在每日任务中执行钉钉推送
DEBUG=""
VENDOR=""
LIMIT=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-email)
            NO_EMAIL=true
            shift
            ;;
        --no-stats)
            NO_STATS=true
            shift
            ;;
        --no-crawl)
            NO_CRAWL=true
            shift
            ;;
        --no-analyze)
            NO_ANALYZE=true
            shift
            ;;
        --no-dingtalk)  # 保留参数，但默认已经设为true
            NO_DINGTALK=true
            shift
            ;;
        --debug)
            DEBUG="--debug"
            shift
            ;;
        --vendor)
            VENDOR="--vendor $2"
            shift 2
            ;;
        --limit)
            LIMIT="--limit $2"
            shift 2
            ;;
        *)
            echo -e "${RED}错误: 未知参数 $1${NC}"
            exit 1
            ;;
    esac
done

# 显示任务信息
echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}           每日爬取与分析任务               ${NC}"
echo -e "${BLUE}===================================================${NC}"
echo -e "${YELLOW}时间: $(date)${NC}"
echo -e "${YELLOW}执行选项:${NC}"
echo -e "  - 爬取: $(if [ "$NO_CRAWL" = true ]; then echo "${RED}禁用${NC}"; else echo "${GREEN}启用${NC}"; fi)"
echo -e "  - 分析: $(if [ "$NO_ANALYZE" = true ]; then echo "${RED}禁用${NC}"; else echo "${GREEN}启用${NC}"; fi)"
echo -e "  - 统计: $(if [ "$NO_STATS" = true ]; then echo "${RED}禁用${NC}"; else echo "${GREEN}启用${NC}"; fi)"
echo -e "  - 邮件: $(if [ "$NO_EMAIL" = true ]; then echo "${RED}禁用${NC}"; else echo "${GREEN}启用${NC}"; fi)"
echo -e "  - 钉钉推送: ${RED}禁用${NC} (将在配置的每周推送时间通过定时任务单独执行)"
if [ ! -z "$VENDOR" ]; then
    echo -e "  - 厂商: ${YELLOW}${VENDOR/--vendor /}${NC}"
fi
if [ ! -z "$LIMIT" ]; then
    echo -e "  - 限制: ${YELLOW}${LIMIT/--limit /}${NC} 篇文章"
fi
echo -e "${BLUE}===================================================${NC}"

# 创建日志目录
mkdir -p "$ROOT_DIR/logs"

# 生成日志文件名
LOG_FILE="$ROOT_DIR/logs/daily_task_$(date +%Y%m%d_%H%M%S).log"
echo -e "${YELLOW}日志将保存到: ${LOG_FILE}${NC}"

# 执行爬取任务
if [ "$NO_CRAWL" != true ]; then
    echo -e "${BLUE}[$(date +%H:%M:%S)] 开始爬取任务...${NC}"
    $ROOT_DIR/run.sh crawl $VENDOR $LIMIT $DEBUG 2>&1 | tee -a "$LOG_FILE"
    CRAWL_RESULT=${PIPESTATUS[0]}
    
    if [ $CRAWL_RESULT -eq 0 ]; then
        echo -e "${GREEN}[$(date +%H:%M:%S)] 爬取任务成功完成${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "${RED}[$(date +%H:%M:%S)] 爬取任务失败，退出代码: $CRAWL_RESULT${NC}" | tee -a "$LOG_FILE"
        # 但不退出脚本，继续执行后续任务
    fi
else
    echo -e "${YELLOW}[$(date +%H:%M:%S)] 爬取任务已禁用，跳过${NC}" | tee -a "$LOG_FILE"
fi

# 执行分析任务
if [ "$NO_ANALYZE" != true ]; then
    echo -e "${BLUE}[$(date +%H:%M:%S)] 开始分析任务...${NC}"
    $ROOT_DIR/run.sh analyze $VENDOR $LIMIT $DEBUG 2>&1 | tee -a "$LOG_FILE"
    ANALYZE_RESULT=${PIPESTATUS[0]}
    
    if [ $ANALYZE_RESULT -eq 0 ]; then
        echo -e "${GREEN}[$(date +%H:%M:%S)] 分析任务成功完成${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "${RED}[$(date +%H:%M:%S)] 分析任务失败，退出代码: $ANALYZE_RESULT${NC}" | tee -a "$LOG_FILE"
            fi
        else
    echo -e "${YELLOW}[$(date +%H:%M:%S)] 分析任务已禁用，跳过${NC}" | tee -a "$LOG_FILE"
fi

# 执行统计任务
if [ "$NO_STATS" != true ]; then
    echo -e "${BLUE}[$(date +%H:%M:%S)] 开始统计任务...${NC}"
    $ROOT_DIR/run.sh stats 2>&1 | tee -a "$LOG_FILE"
    STATS_RESULT=${PIPESTATUS[0]}
    
    if [ $STATS_RESULT -eq 0 ]; then
        echo -e "${GREEN}[$(date +%H:%M:%S)] 统计任务成功完成${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "${RED}[$(date +%H:%M:%S)] 统计任务失败，退出代码: $STATS_RESULT${NC}" | tee -a "$LOG_FILE"
    fi
    
    # 检查未完成任务
    echo -e "${BLUE}[$(date +%H:%M:%S)] 检查未完成的任务...${NC}"
    $ROOT_DIR/run.sh check-tasks --tasks-only 2>&1 | tee -a "$LOG_FILE"
else
    echo -e "${YELLOW}[$(date +%H:%M:%S)] 统计任务已禁用，跳过${NC}" | tee -a "$LOG_FILE"
fi

# 移除钉钉推送任务部分 - 将通过定时任务在配置的每周时间单独执行

# 发送电子邮件通知
if [ "$NO_EMAIL" != true ]; then
    echo -e "${BLUE}[$(date +%H:%M:%S)] 发送电子邮件通知...${NC}"
    python -m src.utils.send_email --log "$LOG_FILE" $DEBUG 2>&1 | tee -a "$LOG_FILE"
    EMAIL_RESULT=${PIPESTATUS[0]}
    
    if [ $EMAIL_RESULT -eq 0 ]; then
        echo -e "${GREEN}[$(date +%H:%M:%S)] 电子邮件发送成功${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "${RED}[$(date +%H:%M:%S)] 电子邮件发送失败，退出代码: $EMAIL_RESULT${NC}" | tee -a "$LOG_FILE"
    fi
else
    echo -e "${YELLOW}[$(date +%H:%M:%S)] 电子邮件通知已禁用，跳过${NC}" | tee -a "$LOG_FILE"
fi

echo -e "${BLUE}===================================================${NC}"
echo -e "${GREEN}每日任务执行完成!${NC}"
echo -e "${YELLOW}详细日志已保存到: ${LOG_FILE}${NC}"
echo -e "${BLUE}===================================================${NC}"
