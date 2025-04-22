#!/bin/bash

# 脚本用于将Markdown文件中的日期格式从下划线格式(YYYY_MM_DD)改为中划线格式(YYYY-MM-DD)
# 作者: Cline
# 日期: 2025-04-23

# 设置日志文件
LOG_FILE="logs/fix_date_format_$(date +%Y%m%d_%H%M%S).log"
mkdir -p $(dirname $LOG_FILE)

# 日志函数
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a $LOG_FILE
}

log "开始执行日期格式修复脚本"

# 查找所有raw和analysis目录下的Azure相关的md文件
RAW_FILES=$(find data/raw/azure -type f -name "*.md")
ANALYSIS_FILES=$(find data/analysis/azure -type f -name "*.md")

# 合并文件列表
ALL_FILES="$RAW_FILES $ANALYSIS_FILES"

# 计数器
TOTAL_FILES=0
MODIFIED_FILES=0

# 处理每个文件
for file in $ALL_FILES; do
    TOTAL_FILES=$((TOTAL_FILES + 1))
    
    # 检查文件是否包含下划线格式的日期
    if grep -q "发布时间:.*[0-9]\{4\}_[0-9]\{2\}_[0-9]\{2\}" "$file"; then
        log "处理文件: $file"
        
        # 创建临时文件
        TEMP_FILE=$(mktemp)
        
        # 使用sed替换日期格式
        # 将"发布时间: YYYY_MM_DD"替换为"发布时间: YYYY-MM-DD"
        sed 's/\(发布时间:.*\)\([0-9]\{4\}\)_\([0-9]\{2\}\)_\([0-9]\{2\}\)/\1\2-\3-\4/g' "$file" > "$TEMP_FILE"
        
        # 检查替换是否成功
        if grep -q "发布时间:.*[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}" "$TEMP_FILE"; then
            # 替换成功，将临时文件内容写回原文件
            mv "$TEMP_FILE" "$file"
            MODIFIED_FILES=$((MODIFIED_FILES + 1))
            log "成功修改文件: $file"
        else
            # 替换失败，删除临时文件
            rm "$TEMP_FILE"
            log "警告: 文件 $file 中未找到匹配的日期格式或替换失败"
        fi
    else
        log "跳过文件: $file (未找到下划线格式的日期)"
    fi
done

log "脚本执行完成"
log "总文件数: $TOTAL_FILES"
log "修改文件数: $MODIFIED_FILES"

echo "日期格式修复完成! 详细日志请查看: $LOG_FILE"
