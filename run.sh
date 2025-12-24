#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 确保工作目录为项目根目录
cd "$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # 无颜色

# 显示帮助信息
show_help() {
    echo -e "${BLUE}云计算网络竞争动态分析工具${NC}"
    echo -e "${YELLOW}用法:${NC}"
    echo -e "  $0 [命令] [选项]"
    echo ""
    echo -e "${YELLOW}可用命令:${NC}"
    echo -e "  ${GREEN}crawl${NC}    - 爬取数据"
    echo -e "  ${GREEN}analyze${NC}  - 分析数据"
    echo -e "  ${GREEN}server${NC}   - 启动Web服务器"
    echo -e "  ${GREEN}setup${NC}    - 设置环境（创建虚拟环境并安装依赖）"
    echo -e "  ${GREEN}driver${NC}   - 下载最新的WebDriver"
    echo -e "  ${GREEN}stats${NC}    - 比较元数据和实际文件统计"
    echo -e "  ${GREEN}check-tasks${NC} - 检查任务完成状态，显示未完成任务的文件"
    echo -e "  ${GREEN}clean${NC}    - 清理中间文件和临时文件"
    echo -e "  ${GREEN}daily${NC}    - 执行每日爬取与分析任务"
    echo -e "  ${GREEN}rebuild-md${NC} - 重建元数据，从本地MD文件更新元数据"
    echo -e "  ${GREEN}dingpush${NC} - 使用钉钉推送系统通知和更新，支持多种推送模式"
    echo -e "  ${GREEN}help${NC}     - 显示此帮助信息"
    echo ""
    
    echo -e "${YELLOW}全局选项:${NC}"
    echo -e "  ${GREEN}--debug${NC}                      - 启用调试模式（适用于所有命令）"
    echo -e "  ${GREEN}--config${NC} [配置文件]           - 指定配置文件路径"
    echo ""
    
    echo -e "${YELLOW}命令特定选项:${NC}"
    echo -e "${BLUE}crawl 命令选项:${NC}"
    echo -e "  ${GREEN}--vendor${NC} [aws|azure|gcp]     - 指定要处理的云服务提供商"
    echo -e "  ${GREEN}--source${NC} [类型]               - 指定要处理的数据来源"
    echo -e "  ${GREEN}--limit${NC} [数字]                - 限制爬取的文章数量"
    echo -e "  ${GREEN}--clean${NC}                      - 清理数据目录"
    echo -e "  ${GREEN}--force${NC}                      - 强制执行，忽略本地metadata是否已存在"
    echo ""
    
    echo -e "${BLUE}analyze 命令选项:${NC}"
    echo -e "  ${GREEN}--vendor${NC} [aws|azure|gcp|tencent|huawei|volcano]  - 指定要处理的云服务提供商"
    echo -e "  ${GREEN}--file${NC} [文件路径]              - 指定要分析的文件路径"
    echo -e "  ${GREEN}--limit${NC} [数字]                - 限制分析的文章数量"
    echo -e "  ${GREEN}--clean${NC}                      - 清理数据目录"
    echo -e "  ${GREEN}--force${NC}                      - 强制执行，忽略文件是否已存在"
    echo ""
    
    echo -e "${BLUE}server 命令选项:${NC}"
    echo -e "  ${GREEN}--host${NC} [主机地址]             - 指定服务器主机地址"
    echo -e "  ${GREEN}--port${NC} [端口号]               - 指定服务器端口"
    echo ""
    
    echo -e "${BLUE}stats 命令选项:${NC}"
    echo -e "  ${GREEN}--detailed${NC}                   - 显示详细信息"
    echo ""
    
    echo -e "${BLUE}check-tasks 命令选项:${NC}"
    echo -e "  ${GREEN}--tasks-only${NC}                 - 只显示任务信息"
    echo ""
    
    echo -e "${BLUE}clean 命令选项:${NC}"
    echo -e "  ${GREEN}--all${NC}                        - 清理所有中间文件"
    echo -e "  ${GREEN}--pyc${NC}                        - 清理Python字节码文件"
    echo -e "  ${GREEN}--logs${NC}                       - 清理日志文件"
    echo -e "  ${GREEN}--temp${NC}                       - 清理临时文件"
    echo -e "  ${GREEN}--data${NC}                       - 清理data目录"
    echo ""
    
    echo -e "${BLUE}daily 命令选项:${NC}"
    echo -e "  ${GREEN}--no-email${NC}                    - 禁用电子邮件通知"
    echo -e "  ${GREEN}--no-stats${NC}                    - 禁用统计任务"
    echo -e "  ${GREEN}--no-crawl${NC}                    - 禁用爬取任务"
    echo -e "  ${GREEN}--no-analyze${NC}                  - 禁用分析任务"
    echo -e "  ${GREEN}--no-dingtalk${NC}                 - 禁用钉钉推送"
    echo -e "  ${GREEN}--vendor${NC} [aws|azure|gcp|all]  - 指定要处理的云服务提供商"
    echo -e "  ${GREEN}--limit${NC} [数字]                 - 限制处理的文章数量"
    echo ""
    
    echo -e "${BLUE}rebuild-md 命令选项:${NC}"
    echo -e "  ${GREEN}--type${NC} [crawler|analysis|all] - 指定元数据类型"
    echo -e "  ${GREEN}--force${NC}                       - 强制重建元数据，即使元数据已存在"
    echo -e "  ${GREEN}--force_clear${NC}                 - 强制清空原有元数据"
    echo -e "  ${GREEN}--deep-check${NC}                  - 进行深度检查，检测内容问题"
    echo -e "  ${GREEN}--delete${NC}                      - 与--deep-check一起使用，删除有问题的文件"
    echo ""
    
    echo -e "${BLUE}dingpush 命令:${NC}"
    echo -e "  子命令:"
    echo -e "  ${GREEN}weekly-report${NC}                - 生成并推送每周竞品分析报告"
    echo -e "  ${GREEN}recent-report${NC} [天数]         - 生成并推送最近N天竞品分析报告"
    echo -e "  ${GREEN}monthly-domestic-report${NC}      - 生成并推送国内云厂商月报（华为/腾讯/火山）"
    echo -e "  ${GREEN}pushfile${NC} --filepath [路径]   - 推送指定的Markdown文件"
    echo -e ""
    echo -e "  选项:"
    echo -e "  ${GREEN}--robot${NC} [机器人名称]           - 使用指定的钉钉机器人推送（可指定多个）"
    echo -e "  ${GREEN}--config${NC} [配置文件]           - 指定配置文件路径"
    echo -e "  ${GREEN}--filepath${NC} [文件路径]         - 要推送的Markdown文件路径（pushfile命令必需）"
    echo ""
    
    echo -e "${YELLOW}示例用法:${NC}"
    echo -e "  $0 crawl --vendor aws --limit 10                    # 爬取AWS的数据，限制10篇文章"
    echo -e "  $0 analyze --file data/raw/aws/blog/某文件.md        # 分析特定文件"
    echo -e "  $0 server --host 0.0.0.0 --port 8080                # 指定主机和端口启动服务器"
    echo -e "  $0 daily --no-email                                 # 执行每日任务但不发送邮件"
    echo -e "  $0 rebuild-md --type analysis --force               # 强制重建分析元数据"
    echo -e "  $0 dingpush weekly-report                           # 生成并推送周报"
    echo -e "  $0 dingpush recent-report 7                         # 生成并推送最近7天报告"
    echo -e "  $0 dingpush recent-report 7 --robot 机器人1         # 使用指定机器人推送"
    echo -e "  $0 dingpush pushfile --filepath data/reports/xxx.md # 推送指定文件"
    echo -e "  $0 --debug crawl --vendor aws                       # 以调试模式爬取AWS数据"
}

# 显示错误信息
show_error() {
    echo -e "${RED}错误: $1${NC}"
    echo -e "${BLUE}使用 '$0 help' 查看完整帮助${NC}"
    exit 1
}

# 显示警告信息
show_warning() {
    echo -e "${YELLOW}警告: $1${NC}"
}

# 显示提示信息
show_info() {
    echo -e "${BLUE}提示: $1${NC}"
}

# 检查文件是否存在
check_file_exists() {
    local file="$1"
    if [ ! -f "$file" ]; then
        show_error "文件不存在: $file"
    fi
}

# 检查配置文件是否存在
check_config_exists() {
    local config="$1"
    if [[ "$config" != /* ]]; then
        # 相对路径，相对于脚本目录
        config="$SCRIPT_DIR/$config"
    fi
    
    if [ ! -f "$config" ]; then
        show_error "配置文件不存在: $config\n您可以复制config.example.yaml作为起点"
    fi
    
    # 简单验证YAML格式
    if command -v python >/dev/null 2>&1; then
        python -c "import yaml; yaml.safe_load(open('$config', 'r', encoding='utf-8'))" >/dev/null 2>&1
        if [ $? -ne 0 ]; then
            show_error "配置文件格式不正确: $config\n请检查YAML语法"
        fi
    fi
}

# 检查目录是否存在，如果不存在则创建
check_and_create_dir() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        if [ $? -ne 0 ]; then
            show_error "无法创建目录: $dir"
        else
            show_info "已创建目录: $dir"
        fi
    fi
}

# 验证参数
validate_args() {
    local cmd="$1"
    shift
    local valid_args=()
    local invalid_args=()
    
    case "$cmd" in
        crawl)
            # crawl命令有效参数
            local valid_opts=("--vendor" "--source" "--limit" "--debug" "--clean" "--force" "--config")
            local requires_value=("--vendor" "--source" "--limit" "--config")
            
            # 验证参数
            while [[ $# -gt 0 ]]; do
                local current="$1"
                local is_valid=false
                
                # 检查参数是否有效
                for opt in "${valid_opts[@]}"; do
                    if [[ "$current" == "$opt" ]]; then
                        is_valid=true
                        break
                    fi
                done
                
                # 检查需要值的参数
                for req in "${requires_value[@]}"; do
                    if [[ "$current" == "$req" ]]; then
                        if [[ -z "$2" || "$2" == --* ]]; then
                            show_error "参数 $current 需要一个值"
                        fi
                        
                        # 检查特定参数的值约束
                        if [[ "$current" == "--vendor" ]]; then
                            if [[ ! "$2" =~ ^(aws|azure|gcp)$ ]]; then
                                show_error "无效的厂商: $2\n有效值为: aws, azure, gcp"
                            fi
                        elif [[ "$current" == "--limit" ]]; then
                            if ! [[ "$2" =~ ^[0-9]+$ ]]; then
                                show_error "文章数量限制必须是一个正整数: $2"
                            fi
                            
                            if [ "$2" -eq 0 ]; then
                                show_warning "文章数量限制为0，将使用配置文件中的默认值"
                            elif [ "$2" -gt 100 ]; then
                                show_warning "文章数量限制设置很大($2)，这可能导致处理时间较长"
                            fi
                        elif [[ "$current" == "--config" ]]; then
                            check_config_exists "$2"
                        fi
                        
                        shift
                        break
                    fi
                done
                
                # 如果无效，添加到无效参数列表
                if ! $is_valid; then
                    invalid_args+=("$current")
                fi
                
                shift
            done
            ;;
            
        analyze)
            # analyze命令有效参数
            local valid_opts=("--debug" "--clean" "--force" "--vendor" "--file" "--config" "--limit")
            local requires_value=("--vendor" "--file" "--config" "--limit")
            
            # 验证参数
            while [[ $# -gt 0 ]]; do
                local current="$1"
                local is_valid=false
                
                # 检查参数是否有效
                for opt in "${valid_opts[@]}"; do
                    if [[ "$current" == "$opt" ]]; then
                        is_valid=true
                        break
                    fi
                done
                
                # 检查需要值的参数
                for req in "${requires_value[@]}"; do
                    if [[ "$current" == "$req" ]]; then
                        if [[ -z "$2" || "$2" == --* ]]; then
                            show_error "参数 $current 需要一个值"
                        fi
                        
                        # 检查特定参数的值约束
                        if [[ "$current" == "--vendor" ]]; then
                            if [[ ! "$2" =~ ^(aws|azure|gcp|tencent|huawei|volcano)$ ]]; then
                                show_error "无效的厂商: $2\n有效值为: aws, azure, gcp, tencent, huawei, volcano"
                            fi
                        elif [[ "$current" == "--file" ]]; then
                            # 检查文件是否存在
                            check_file_exists "$2"
                        elif [[ "$current" == "--config" ]]; then
                            # 检查配置文件是否存在
                            check_config_exists "$2"
                        elif [[ "$current" == "--limit" ]]; then
                            if ! [[ "$2" =~ ^[0-9]+$ ]]; then
                                show_error "文章数量限制必须是一个正整数: $2"
                            fi
                            
                            if [ "$2" -eq 0 ]; then
                                show_warning "文章数量限制为0，将使用配置文件中的默认值"
                            elif [ "$2" -gt 100 ]; then
                                show_warning "文章数量限制设置很大($2)，这可能导致处理时间较长"
                            fi
                        fi
                        
                        shift
                        break
                    fi
                done
                
                # 如果无效，添加到无效参数列表
                if ! $is_valid; then
                    invalid_args+=("$current")
                fi
                
                shift
            done
            ;;
            
        server)
            # server命令有效参数
            local valid_opts=("--host" "--port" "--debug")
            local requires_value=("--host" "--port")
            
            # 验证参数
            while [[ $# -gt 0 ]]; do
                local current="$1"
                local is_valid=false
                
                # 检查参数是否有效
                for opt in "${valid_opts[@]}"; do
                    if [[ "$current" == "$opt" ]]; then
                        is_valid=true
                        break
                    fi
                done
                
                # 检查需要值的参数
                for req in "${requires_value[@]}"; do
                    if [[ "$current" == "$req" ]]; then
                        if [[ -z "$2" || "$2" == --* ]]; then
                            show_error "参数 $current 需要一个值"
                        fi
                        
                        # 检查端口值是否为有效数字
                        if [[ "$current" == "--port" ]]; then
                            if ! [[ "$2" =~ ^[0-9]+$ ]]; then
                                show_error "端口必须是一个数字: $2"
                            fi
                            if [[ "$2" -lt 1 || "$2" -gt 65535 ]]; then
                                show_error "端口必须在1-65535范围内: $2"
                            fi
                            
                            # 常见端口冲突警告
                            if [[ "$2" -lt 1024 ]]; then
                                show_warning "端口 $2 是特权端口，可能需要管理员权限才能绑定"
                            fi
                            if [[ "$2" -eq 80 || "$2" -eq 443 || "$2" -eq 8080 ]]; then
                                show_warning "端口 $2 是常用Web端口，可能已被其他服务占用"
                            fi
                        fi
                        
                        # 检查主机地址
                        if [[ "$current" == "--host" ]]; then
                            if [[ "$2" == "0.0.0.0" ]]; then
                                show_warning "将绑定到所有网络接口(0.0.0.0)，服务将可从外部访问"
                            fi
                        fi
                        
                        shift
                        break
                    fi
                done
                
                # 如果无效，添加到无效参数列表
                if ! $is_valid; then
                    invalid_args+=("$current")
                fi
                
                shift
            done
            ;;
            
        stats)
            # stats命令有效参数
            local valid_opts=("--detailed")
            
            # 验证参数
            while [[ $# -gt 0 ]]; do
                local current="$1"
                local is_valid=false
                
                # 检查参数是否有效
                for opt in "${valid_opts[@]}"; do
                    if [[ "$current" == "$opt" ]]; then
                        is_valid=true
                        break
                    fi
                done
                
                # 如果无效，添加到无效参数列表
                if ! $is_valid; then
                    invalid_args+=("$current")
                fi
                
                shift
            done
            ;;
            
        check-tasks)
            # check-tasks命令有效参数
            local valid_opts=("--tasks-only")
            
            # 验证参数
            while [[ $# -gt 0 ]]; do
                local current="$1"
                local is_valid=false
                
                # 检查参数是否有效
                for opt in "${valid_opts[@]}"; do
                    if [[ "$current" == "$opt" ]]; then
                        is_valid=true
                        break
                    fi
                done
                
                # 如果无效，添加到无效参数列表
                if ! $is_valid; then
                    invalid_args+=("$current")
                fi
                
                shift
            done
            ;;
            
        clean)
            # clean命令有效参数
            local valid_opts=("--all" "--pyc" "--logs" "--temp" "--data")
            
            # 验证参数
            while [[ $# -gt 0 ]]; do
                local current="$1"
                local is_valid=false
                
                # 检查参数是否有效
                for opt in "${valid_opts[@]}"; do
                    if [[ "$current" == "$opt" ]]; then
                        is_valid=true
                        break
                    fi
                done
                
                # 如果无效，添加到无效参数列表
                if ! $is_valid; then
                    invalid_args+=("$current")
                fi
                
                shift
            done
            ;;
            
        daily)
            # daily命令有效参数
            local valid_opts=("--no-email" "--no-stats" "--no-crawl" "--no-analyze" "--no-dingtalk" "--debug" "--vendor" "--limit")
            local requires_value=("--vendor" "--limit")
            
            # 验证参数
            while [[ $# -gt 0 ]]; do
                local current="$1"
                local is_valid=false
                
                # 检查参数是否有效
                for opt in "${valid_opts[@]}"; do
                    if [[ "$current" == "$opt" ]]; then
                        is_valid=true
                        break
                    fi
                done
                
                # 检查需要值的参数
                for req in "${requires_value[@]}"; do
                    if [[ "$current" == "$req" ]]; then
                        if [[ -z "$2" || "$2" == --* ]]; then
                            show_error "参数 $current 需要一个值"
                        fi
                        
                        # 检查特定参数的值约束
                        if [[ "$current" == "--vendor" ]]; then
                            if [[ ! "$2" =~ ^(aws|azure|gcp|tencent|huawei|volcano|all)$ ]]; then
                                show_error "无效的厂商: $2\n有效值为: aws, azure, gcp, tencent, huawei, volcano, all"
                            fi
                        elif [[ "$current" == "--limit" ]]; then
                            if ! [[ "$2" =~ ^[0-9]+$ ]]; then
                                show_error "文章数量限制必须是一个正整数: $2"
                            fi
                        fi
                        
                        shift
                        break
                    fi
                done
                
                # 如果无效，添加到无效参数列表
                if ! $is_valid; then
                    invalid_args+=("$current")
                fi
                
                shift
            done
            ;;
            
        setup|driver|help)
            # 这些命令不接受任何参数
            if [[ $# -gt 0 ]]; then
                invalid_args=("$@")
            fi
            ;;
            
        rebuild-md)
            # rebuild-md命令有效参数
            local valid_opts=("--type" "--force" "--force_clear" "--deep-check" "--delete" "--debug")
            local requires_value=("--type")
            local has_deep_check=false
            local has_delete=false
            
            # 验证参数
            while [[ $# -gt 0 ]]; do
                local current="$1"
                local is_valid=false
                
                # 检查参数是否有效
                for opt in "${valid_opts[@]}"; do
                    if [[ "$current" == "$opt" ]]; then
                        is_valid=true
                        
                        # 记录特殊参数
                        if [[ "$current" == "--deep-check" ]]; then
                            has_deep_check=true
                        elif [[ "$current" == "--delete" ]]; then
                            has_delete=true
                        fi
                        
                        break
                    fi
                done
                
                # 检查需要值的参数
                for req in "${requires_value[@]}"; do
                    if [[ "$current" == "$req" ]]; then
                        if [[ -z "$2" || "$2" == --* ]]; then
                            show_error "参数 $current 需要一个值"
                        fi
                        
                        # 检查特定参数的值约束
                        if [[ "$current" == "--type" ]]; then
                            if [[ ! "$2" =~ ^(crawler|analysis|all)$ ]]; then
                                show_error "无效的元数据类型: $2\n有效值为: crawler, analysis, all"
                            fi
                        fi
                        
                        shift
                        break
                    fi
                done
                
                # 如果无效，添加到无效参数列表
                if ! $is_valid; then
                    invalid_args+=("$current")
                fi
                
                shift
            done
            
            # 检查--delete参数是否与--deep-check一起使用
            if [ "$has_delete" = true ] && [ "$has_deep_check" = false ]; then
                show_error "--delete参数必须与--deep-check一起使用"
            fi
            
            # 如果使用--delete，给出警告
            if [ "$has_delete" = true ]; then
                show_warning "已启用删除模式，这将删除检测到问题的文件！"
                echo -e "${YELLOW}按Ctrl+C取消，或任意键继续...${NC}"
                read -n 1 -s
            fi
            
            # 如果使用--deep-check，给出提示
            if [ "$has_deep_check" = true ] && [ "$has_delete" = false ]; then
                show_info "深度检查模式已启用，将检测分析文件中的'假完成'问题但不删除文件"
            fi
            ;;
            
        dingpush)
            # dingpush命令有效参数
            local valid_opts=("weekly-report" "recent-report" "monthly-domestic-report" "pushfile")
            local has_recent_report=false
            
            # 检查是否有子命令及其是否有效
            if [ $# -gt 0 ]; then
                local subcmd="$1"
                local is_valid=false
                
                for opt in "${valid_opts[@]}"; do
                    if [[ "$subcmd" == "$opt" ]]; then
                        is_valid=true
                        # 记录是否使用了recent-report子命令
                        if [[ "$subcmd" == "recent-report" ]]; then
                            has_recent_report=true
                        fi
                        break
                    fi
                done
                
                if ! $is_valid; then
                    invalid_args+=("$subcmd")
                fi
                
                # 如果是recent-report子命令，验证下一个参数是否为数字
                if $has_recent_report; then
                    if [ $# -lt 2 ] || ! [[ "$2" =~ ^[0-9]+$ ]]; then
                        # 这里不添加到invalid_args，因为错误会在run_dingpush中处理
                        :
                    else
                        # 验证通过，跳过子命令和天数参数的进一步检查
                        shift 2
                    fi
                else
                    # 如果不是recent-report子命令，跳过子命令参数的进一步检查
                    shift
                fi
            fi
            
            # 检查剩余参数
            local valid_extra_opts=("--config" "--robot" "--filepath" "--year" "--month")
            local requires_value=("--config" "--robot" "--filepath" "--year" "--month")
            
            while [[ $# -gt 0 ]]; do
                local current="$1"
                local is_valid=false
                
                # 检查参数是否有效
                for opt in "${valid_extra_opts[@]}"; do
                    if [[ "$current" == "$opt" ]]; then
                        is_valid=true
                        break
                    fi
                done
                
                # 检查需要值的参数
                for req in "${requires_value[@]}"; do
                    if [[ "$current" == "$req" ]]; then
                        if [[ -z "$2" || "$2" == --* ]]; then
                            show_error "参数 $current 需要一个值"
                            return 1
                        fi
                        
                        # 检查特定参数的值约束
                        if [[ "$current" == "--config" ]]; then
                            check_config_exists "$2"
                        elif [[ "$current" == "--filepath" ]]; then
                            check_file_exists "$2"
                        fi
                        
                        shift
                        break
                    fi
                done
                
                # 如果无效，添加到无效参数列表
                if ! $is_valid; then
                    invalid_args+=("$current")
                fi
                
                shift
            done
            ;;
            
        *)
            # 未知命令
            show_error "未知命令: $cmd"
            ;;
    esac
    
    # 检查是否有无效参数
    if [[ ${#invalid_args[@]} -gt 0 ]]; then
        echo -e "${RED}错误: 无效的参数: ${invalid_args[*]}${NC}"
        
        echo -e "${YELLOW}命令 '$cmd' 的有效参数:${NC}"
        
        case "$cmd" in
            crawl)
                echo -e "${GREEN}--vendor [aws|azure|gcp], --source, --limit [数字], --config [配置文件], --debug, --clean, --force${NC}"
                ;;
            analyze)
                echo -e "${GREEN}--vendor [aws|azure|gcp|tencent|huawei|volcano], --file [文件路径], --config [配置文件], --limit [数字], --debug, --clean, --force${NC}"
                ;;
            server)
                echo -e "${GREEN}--host [主机地址], --port [端口号], --debug${NC}"
                ;;
            stats)
                echo -e "${GREEN}--detailed${NC}"
                ;;
            check-tasks)
                echo -e "${GREEN}--tasks-only${NC}"
                ;;
            clean)
                echo -e "${GREEN}--all, --pyc, --logs, --temp, --data${NC}"
                ;;
            setup|driver|help)
                echo -e "${GREEN}[无参数]${NC}"
                ;;
            dingpush)
                echo -e "${GREEN}子命令: weekly, daily, recent [天数]${NC}"
                echo -e "${GREEN}选项: --config [配置文件], --robot [机器人名称]${NC}"
                ;;
        esac
        
        echo -e "${BLUE}例如: $0 $cmd ${NC}"
        echo -e "${BLUE}使用 '$0 help' 查看完整帮助${NC}"
        return 1
    fi
    return 0
}

# 检查Python环境
check_python() {
    echo -e "${BLUE}检查Python环境...${NC}"
    
    # 检查是否可以执行python3命令
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        echo -e "${GREEN}Python已安装: $PYTHON_VERSION${NC}"
        
        # 检查Python版本是否满足要求 (>= 3.8)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            echo -e "${GREEN}Python版本满足要求 (>= 3.8)${NC}"
            return 0
        else
            echo -e "${RED}Python版本过低,需要 >= 3.8${NC}"
            return 1
        fi
    else
        echo -e "${RED}未检测到Python 3${NC}"
        echo -e "${YELLOW}请按照以下步骤安装Python 3.8+:${NC}"
        echo -e ""
        
        # 根据系统类型显示不同的安装说明
        case "$(uname -s)" in
            Darwin*)    # macOS
                echo -e "${BLUE}macOS安装步骤:${NC}"
                echo -e "1. 使用Homebrew安装(推荐):"
                echo -e "   ${GREEN}brew install python@3.10${NC}"
                echo -e "2. 或从官网下载: ${GREEN}https://www.python.org/downloads/${NC}"
                ;;
            Linux*)     # Linux
                echo -e "${BLUE}Linux安装步骤:${NC}"
                echo -e "1. Ubuntu/Debian: ${GREEN}sudo apt update && sudo apt install python3 python3-venv python3-pip${NC}"
                echo -e "2. CentOS/RHEL: ${GREEN}sudo yum install python3 python3-pip${NC}"
                ;;
            CYGWIN*|MINGW*|MSYS*)  # Windows
                echo -e "${BLUE}Windows安装步骤:${NC}"
                echo -e "1. 从官网下载: ${GREEN}https://www.python.org/downloads/${NC}"
                echo -e "2. 安装时记得勾选'Add Python to PATH'"
                ;;
            *)
                echo -e "${BLUE}通用安装步骤:${NC}"
                echo -e "1. 访问 ${GREEN}https://www.python.org/downloads/${NC} 获取最新的安装包"
                ;;
        esac
        
        echo -e ""
        echo -e "${BLUE}安装完成后,请再次运行本脚本${NC}"
        return 1
    fi
}

# 激活虚拟环境
activate_venv() {
    # 检查是否存在venv目录
    if [ -d "venv" ]; then
        echo -e "${GREEN}找到venv环境,正在激活...${NC}"
        source venv/bin/activate
    else
        echo -e "${YELLOW}未找到venv环境,正在创建...${NC}"
        python3 -m venv venv
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}venv环境已创建,正在激活...${NC}"
            source venv/bin/activate
        else
            echo -e "${RED}创建venv环境失败,请检查Python安装是否正确。${NC}"
            exit 1
        fi
    fi
    echo -e "${GREEN}Python虚拟环境已激活${NC}"
}

# 安装依赖
install_dependencies() {
    echo -e "${BLUE}正在安装项目依赖...${NC}"
    
    # 创建临时日志文件
    TEMP_LOG=$(mktemp)
    echo -e "${YELLOW}安装日志将被保存到: $TEMP_LOG${NC}"
    
    # 检查是否安装了tabulate库
    if ! pip list | grep -q "tabulate"; then
        echo -e "${YELLOW}未安装tabulate库，正在安装...${NC}"
        pip install tabulate --no-cache-dir --verbose 2>&1 | tee -a "$TEMP_LOG"
    fi
    
    pip install -r "$SCRIPT_DIR/requirements.txt" --no-cache-dir --verbose 2>&1 | tee -a "$TEMP_LOG"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}依赖安装成功${NC}"
    else
        echo -e "${RED}依赖安装失败，请检查网络连接和requirements.txt文件${NC}"
        echo -e "${YELLOW}详细错误日志请查看: $TEMP_LOG${NC}"
        exit 1
    fi
}

# 设置环境
setup_environment() {
    echo -e "${BLUE}设置环境...${NC}"
    
    # 检查Python
    check_python || exit 1
    
    # 激活虚拟环境
    activate_venv
    
    # 安装依赖
    install_dependencies
    
    echo -e "${GREEN}环境设置完成${NC}"
}

# 下载WebDriver
download_driver() {
    echo -e "${BLUE}正在下载最新的WebDriver...${NC}"
    
    # 激活虚拟环境
    activate_venv
    
    # 调用Python模块
    python -m src.utils.driver_manager
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}WebDriver下载成功${NC}"
    else
        echo -e "${RED}WebDriver下载失败${NC}"
        exit 1
    fi
}

# 爬取数据
crawl_data() {
    echo -e "${BLUE}开始爬取数据...${NC}"
    
    # validate_args "crawl" "$@" || return 1 # Validation is done in main before calling
    
    # 检查data目录是否存在
    check_and_create_dir "$SCRIPT_DIR/data"
    check_and_create_dir "$SCRIPT_DIR/data/raw"
    check_and_create_dir "$SCRIPT_DIR/data/metadata"
    
    # 激活虚拟环境
    activate_venv
    
    local python_config_arg=""
    if [ -n "$GLOBAL_CONFIG_FILE_PATH" ]; then
        # Pass the specific config file to the Python script
        python_config_arg="--config \"$GLOBAL_CONFIG_FILE_PATH\""
    else
        # If no global config via run.sh, pass the default directory to Python script's --config
        # This maintains previous behavior if Python's --config expects a dir and no global file is set.
        # OR, if Python's get_config() handles default discovery, this line could be removed.
        # For now, keeping it for compatibility if Python's --config expects a value.
        python_config_arg="--config \"$SCRIPT_DIR/config\""
    fi
    
    # 调用Python模块. $@ contains FILTERED_ARGS from main, plus --debug if it was global.
    eval "python -m src.main --mode crawl $python_config_arg $@"
}

# 分析数据
analyze_data() {
    echo -e "${BLUE}开始分析数据...${NC}"
    
    # validate_args "analyze" "$@" || return 1 # Validation is done in main
    
    # 检查data目录是否存在
    check_and_create_dir "$SCRIPT_DIR/data"
    check_and_create_dir "$SCRIPT_DIR/data/raw"
    check_and_create_dir "$SCRIPT_DIR/data/analysis"
    check_and_create_dir "$SCRIPT_DIR/data/metadata"
    
    # 检查是否存在raw目录下的MD文件
    if ! find "$SCRIPT_DIR/data/raw" -name "*.md" | grep -q .; then
        show_warning "未检测到原始数据文件，请先执行爬取命令: ./run.sh crawl"
        echo -e "${BLUE}是否继续执行分析命令？这可能不会产生任何结果 [y/N]: ${NC}"
        read -r confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            show_info "已取消分析操作"
            return 1
        fi
    fi
    
    # 检查是否存在配置文件 (these checks might be redundant if global config is primary)
    # if [ ! -d "$SCRIPT_DIR/config" ]; then ... 
    # if [ ! -f "$SCRIPT_DIR/config.secret.yaml" ]; then ...
    
    # 激活虚拟环境
    activate_venv
    
    local python_config_arg=""
    if [ -n "$GLOBAL_CONFIG_FILE_PATH" ]; then
        python_config_arg="--config \"$GLOBAL_CONFIG_FILE_PATH\""
    else
        # Default to passing the standard config directory if no global file specified
        python_config_arg="--config \"$SCRIPT_DIR/config\""
    fi
    
    # 调用Python模块
    eval "python -m src.main --mode analyze $python_config_arg $@"
}

# 比较元数据和实际文件统计
compare_stats() {
    echo -e "${BLUE}开始比较元数据和实际文件统计...${NC}"
    
    # 验证参数
    validate_args "stats" "$@" || return 1
    
    # 激活虚拟环境
    activate_venv
    
    # 调用Python模块
    python -m src.utils.compare_stats "$@"
}

# 检查任务完成状态
check_tasks() {
    echo -e "${BLUE}检查任务完成状态...${NC}"
    
    # 验证参数
    validate_args "check-tasks" "$@" || return 1
    
    # 激活虚拟环境
    activate_venv
    
    # 调用Python模块，只显示未完成任务的文件
    python -m src.utils.compare_stats --detailed --tasks-only "$@"
}

# 启动Web服务器
run_server() {
    echo -e "${BLUE}启动Web服务器...${NC}"
    
    # 验证参数
    validate_args "server" "$@" || return 1
    
    # 激活虚拟环境
    activate_venv
    
    # 默认参数
    HOST="127.0.0.1"
    PORT="5000"
    DEBUG=""
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --host)
                HOST="$2"
                shift 2
                ;;
            --port)
                PORT="$2"
                shift 2
                ;;
            --debug)
                DEBUG="--debug"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    echo -e "${GREEN}服务器地址: http://$HOST:$PORT${NC}"
    python -m src.web_server.run --host $HOST --port $PORT $DEBUG
}

# 清理中间文件和临时文件
clean_files() {
    echo -e "${BLUE}开始清理文件...${NC}"
    
    # 验证参数
    validate_args "clean" "$@" || return 1
    
    # 默认不清理任何文件，除非指定了参数
    CLEAN_ALL=false
    CLEAN_PYC=false
    CLEAN_LOGS=false
    CLEAN_TEMP=false
    CLEAN_DATA=false
    
    # 如果没有参数，默认清理所有
    if [ $# -eq 0 ]; then
        CLEAN_ALL=true
    fi
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --all)
                CLEAN_ALL=true
                shift
                ;;
            --pyc)
                CLEAN_PYC=true
                shift
                ;;
            --logs)
                CLEAN_LOGS=true
                shift
                ;;
            --temp)
                CLEAN_TEMP=true
                shift
                ;;
            --data)
                CLEAN_DATA=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    # 如果指定了--all，则清理所有类型的文件（除了data目录）
    if [ "$CLEAN_ALL" = true ]; then
        CLEAN_PYC=true
        CLEAN_LOGS=true
        CLEAN_TEMP=true
        # 注意：CLEAN_DATA 不包含在CLEAN_ALL中，需要单独指定
    fi
    
    # 清理Python字节码文件
    if [ "$CLEAN_PYC" = true ]; then
        echo -e "${YELLOW}清理Python字节码文件...${NC}"
        find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find "$SCRIPT_DIR" -name "*.pyc" -delete 2>/dev/null || true
        find "$SCRIPT_DIR" -name "*.pyo" -delete 2>/dev/null || true
        find "$SCRIPT_DIR" -name "*.pyd" -delete 2>/dev/null || true
        echo -e "${GREEN}Python字节码文件已清理${NC}"
    fi
    
    # 清理日志文件
    if [ "$CLEAN_LOGS" = true ]; then
        echo -e "${YELLOW}清理日志文件...${NC}"
        find "$SCRIPT_DIR/logs" -name "*.log" -delete 2>/dev/null || true
        echo -e "${GREEN}日志文件已清理${NC}"
    fi
    
    # 清理临时文件
    if [ "$CLEAN_TEMP" = true ]; then
        echo -e "${YELLOW}清理临时文件...${NC}"
        find "$SCRIPT_DIR" -name "*.tmp" -delete 2>/dev/null || true
        find "$SCRIPT_DIR" -name "*.bak" -delete 2>/dev/null || true
        find "$SCRIPT_DIR" -name "*.swp" -delete 2>/dev/null || true
        find "$SCRIPT_DIR" -name ".DS_Store" -delete 2>/dev/null || true
        echo -e "${GREEN}临时文件已清理${NC}"
    fi
    
    # 清理data目录
    if [ "$CLEAN_DATA" = true ]; then
        echo -e "${YELLOW}清理data目录...${NC}"
        if [ -d "$SCRIPT_DIR/data" ]; then
            read -p "确定要删除data目录吗？这将删除所有爬取和分析数据 [y/N]: " confirm
            if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
                rm -rf "$SCRIPT_DIR/data"
                echo -e "${GREEN}data目录已清理${NC}"
            else
                echo -e "${BLUE}取消删除data目录${NC}"
            fi
        else
            echo -e "${BLUE}data目录不存在，无需清理${NC}"
        fi
    fi
    
    echo -e "${GREEN}文件清理完成${NC}"
}

# 执行每日爬取与分析任务
run_daily() {
    echo -e "${BLUE}执行每日爬取与分析任务...${NC}"
    
    # 激活虚拟环境
    activate_venv
    
    # 调用bash脚本
    bash "$SCRIPT_DIR/scripts/daily_crawl_and_analyze.sh" "$@"
}

# 重建元数据，从本地MD文件更新元数据
run_rebuild_metadata() {
    echo -e "${BLUE}开始重建元数据...${NC}"
    
    # 验证参数
    validate_args "rebuild-md" "$@" || return 1
    
    # 检查data目录是否存在
    check_and_create_dir "$SCRIPT_DIR/data/metadata"
    
    # 激活虚拟环境
    activate_venv
    
    # 创建临时文件存储输出
    TEMP_OUTPUT=$(mktemp)
    
    # 调用Python模块并保存输出
    python -m src.utils.rebuild_metadata "$@" > "$TEMP_OUTPUT" 2>&1
    RESULT=$?
    
    # 使用awk提取关键信息
    echo -e "${YELLOW}元数据重建结果:${NC}"
    grep -E "重建任务总结|成功更新|覆盖.*元数据记录|删除了.*个|检测到.*个内容异常|元数据重建完成" "$TEMP_OUTPUT" | 
    while read line; do
        if [[ $line == *"删除了"* ]] || [[ $line == *"检测到"* && $line == *"内容异常"* ]]; then
            echo -e "${RED}$line${NC}"
        elif [[ $line == *"重建任务总结"* ]] || [[ $line == *"成功更新"* ]]; then
            echo -e "${GREEN}$line${NC}"
        elif [[ $line == *"元数据重建完成"* ]]; then
            echo -e "${GREEN}✓ $line${NC}"
        else
            echo -e "${BLUE}$line${NC}"
        fi
    done
    
    # 如果有错误，显示错误信息
    if grep -q "错误数:" "$TEMP_OUTPUT"; then
        echo -e "${RED}发现错误:${NC}"
        grep -A 5 "错误数:" "$TEMP_OUTPUT"
    fi
    
    # 显示深度检查结果文件位置
    LOG_FILE=$(grep -o "已将检测到的问题文件信息写入日志文件: .*" "$TEMP_OUTPUT" | sed 's/.*: //')
    if [ ! -z "$LOG_FILE" ]; then
        echo -e "${YELLOW}深度检查发现问题，详细信息已保存至: ${GREEN}$LOG_FILE${NC}"
    fi
    
    # 删除临时文件
    rm -f "$TEMP_OUTPUT"
    
    return $RESULT
}

# 执行钉钉推送（支持报告生成和推送）
run_dingpush() {
    echo -e "${BLUE}开始执行钉钉推送...${NC}"
    
    # 激活虚拟环境
    activate_venv
    
    local all_args=("$@")
    local subcmd="${all_args[0]:-}"
    
    # 检查是否至少有一个参数（子命令）
    if [ -z "$subcmd" ]; then
        echo -e "${YELLOW}未指定推送子命令，将显示帮助信息...${NC}"
        python -m src.utils.dingtalk --help
        echo ""
        echo -e "${YELLOW}提示:${NC} ${BLUE}run.sh 还提供以下封装命令:${NC}"
        echo -e "  ${GREEN}weekly-report${NC}  - 生成并推送周报"
        echo -e "  ${GREEN}recent-report${NC} [天数] - 生成并推送最近N天报告"
        echo -e "  ${GREEN}monthly-domestic-report${NC} [选项] - 生成并推送国内云厂商月报"
        return 1
    fi
    
    case "$subcmd" in
        weekly-report)
            echo -e "${BLUE}正在生成每周竞品分析报告...${NC}"
            
            local gen_args=("--mode" "weekly")
            local push_args=()
            
            # 处理参数
            for arg in "${all_args[@]:1}"; do
                case "$arg" in
                    --debug)
                        gen_args+=("--loglevel" "DEBUG")
                        ;;
                    --robot|--config)
                        push_args+=("$arg")
                        ;;
                    *)
                        push_args+=("$arg")
                        ;;
                esac
            done
            
            # 添加全局配置
            if [ -n "$GLOBAL_CONFIG_FILE_PATH" ]; then
                gen_args+=("--config" "$GLOBAL_CONFIG_FILE_PATH")
            fi
            
            # 生成报告并捕获输出路径
            local report_path=$(python -m src.utils.report_generator "${gen_args[@]}" 2>&1 | tail -n 1)
            local gen_exit_code=$?
            
            if [ $gen_exit_code -eq 0 ] && [ -f "$report_path" ]; then
                echo -e "${GREEN}✓ 周报生成成功: $report_path${NC}"
                echo -e "${BLUE}现在推送到钉钉...${NC}"
                
                local dingtalk_args=("pushfile" "--filepath" "$report_path")
                if [ -n "$GLOBAL_CONFIG_FILE_PATH" ]; then
                    dingtalk_args+=("--config" "$GLOBAL_CONFIG_FILE_PATH")
                fi
                dingtalk_args+=("${push_args[@]}")
                
                python -m src.utils.dingtalk "${dingtalk_args[@]}"
                return $?
            else
                echo -e "${RED}✗ 周报生成失败 (退出码: $gen_exit_code)${NC}"
                return $gen_exit_code
            fi
            ;;
            
        recent-report)
            local days="${all_args[1]:-}"
            
            if [[ ! "$days" =~ ^[0-9]+$ ]]; then
                show_error "recent-report 需要一个数字类型的天数参数\n用法: $0 dingpush recent-report <天数> [选项]"
                return 1
            fi
            
            echo -e "${BLUE}正在生成最近 ${days} 天竞品分析报告...${NC}"
            
            local gen_args=("--mode" "recent" "--days" "$days")
            local push_args=()
            
            # 处理参数（跳过前两个：子命令和天数）
            for arg in "${all_args[@]:2}"; do
                case "$arg" in
                    --debug)
                        gen_args+=("--loglevel" "DEBUG")
                        ;;
                    --robot|--config)
                        push_args+=("$arg")
                        ;;
                    *)
                        push_args+=("$arg")
                        ;;
                esac
            done
            
            # 添加全局配置
            if [ -n "$GLOBAL_CONFIG_FILE_PATH" ]; then
                gen_args+=("--config" "$GLOBAL_CONFIG_FILE_PATH")
            fi
            
            # 生成报告并捕获输出路径
            local report_path=$(python -m src.utils.report_generator "${gen_args[@]}" 2>&1 | tail -n 1)
            local gen_exit_code=$?
            
            if [ $gen_exit_code -eq 0 ] && [ -f "$report_path" ]; then
                echo -e "${GREEN}✓ 最近 ${days} 天报告生成成功: $report_path${NC}"
                echo -e "${BLUE}现在推送到钉钉...${NC}"
                
                local dingtalk_args=("pushfile" "--filepath" "$report_path")
                if [ -n "$GLOBAL_CONFIG_FILE_PATH" ]; then
                    dingtalk_args+=("--config" "$GLOBAL_CONFIG_FILE_PATH")
                fi
                dingtalk_args+=("${push_args[@]}")
                
                python -m src.utils.dingtalk "${dingtalk_args[@]}"
                return $?
            else
                echo -e "${RED}✗ 最近 ${days} 天报告生成失败 (退出码: $gen_exit_code)${NC}"
                return $gen_exit_code
            fi
            ;;
            
        pushfile)
            # 直接传递给 dingtalk.py
            echo -e "${BLUE}推送指定的Markdown文件...${NC}"
            python -m src.utils.dingtalk "${all_args[@]}"
            return $?
            ;;
        
        monthly-domestic-report)
            echo -e "${BLUE}正在生成国内云厂商月度竞争动态报告...${NC}"
            
            local gen_args=("--mode" "monthly-domestic")
            local push_args=()
            local year_arg=""
            local month_arg=""
            local skip_next=false
            
            # 处理参数
            for i in "${!all_args[@]}"; do
                if [ $i -eq 0 ]; then
                    continue  # 跳过子命令
                fi
                
                if $skip_next; then
                    skip_next=false
                    continue
                fi
                
                local arg="${all_args[$i]}"
                case "$arg" in
                    --debug)
                        gen_args+=("--loglevel" "DEBUG")
                        ;;
                    --year)
                        year_arg="${all_args[$((i+1))]}"
                        gen_args+=("--year" "$year_arg")
                        skip_next=true
                        ;;
                    --month)
                        month_arg="${all_args[$((i+1))]}"
                        gen_args+=("--month" "$month_arg")
                        skip_next=true
                        ;;
                    --robot|--config)
                        push_args+=("$arg")
                        ;;
                    *)
                        push_args+=("$arg")
                        ;;
                esac
            done
            
            # 添加全局配置
            if [ -n "$GLOBAL_CONFIG_FILE_PATH" ]; then
                gen_args+=("--config" "$GLOBAL_CONFIG_FILE_PATH")
            fi
            
            # 生成报告并捕获输出路径
            local report_path=$(python -m src.utils.report_generator "${gen_args[@]}" 2>&1 | tail -n 1)
            local gen_exit_code=$?
            
            if [ $gen_exit_code -eq 0 ] && [ -f "$report_path" ]; then
                echo -e "${GREEN}✓ 国内月报生成成功: $report_path${NC}"
                echo -e "${BLUE}现在推送到钉钉...${NC}"
                
                local dingtalk_args=("pushfile" "--filepath" "$report_path")
                if [ -n "$GLOBAL_CONFIG_FILE_PATH" ]; then
                    dingtalk_args+=("--config" "$GLOBAL_CONFIG_FILE_PATH")
                fi
                dingtalk_args+=("${push_args[@]}")
                
                python -m src.utils.dingtalk "${dingtalk_args[@]}"
                return $?
            else
                echo -e "${RED}✗ 国内月报生成失败 (退出码: $gen_exit_code)${NC}"
                return $gen_exit_code
            fi
            ;;
            
        *)
            show_error "未知的 dingpush 子命令: $subcmd\n有效子命令: weekly-report, recent-report, monthly-domestic-report, pushfile"
            return 1
            ;;
    esac
}

# 主函数
main() {
    # 如果没有参数，显示帮助信息
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    # 全局DEBUG和CONFIG变量
    GLOBAL_DEBUG=""
    GLOBAL_CONFIG_FILE_PATH=""
    
    # 暂存所有原始参数
    ORIGINAL_ARGS=("$@")
    PROCESSED_ARGS=() # 参数处理后，用于确定COMMAND和后续ARGS

    # 第一轮处理：提取全局 --debug 和 --config 文件路径
    # 这种方式允许 --debug 和 --config 出现在命令之前或之后
    temp_args=()
    skip_next=false
    for arg in "${ORIGINAL_ARGS[@]}"; do
        if $skip_next; then
            skip_next=false
            continue
        fi
        case "$arg" in
            --debug)
                if [ -z "$GLOBAL_DEBUG" ]; then # 只设置一次
                    GLOBAL_DEBUG="--debug"
                    show_info "已启用全局调试模式"
                else
                    show_warning "检测到重复的 --debug 参数，已忽略后续的。"
                fi
                ;;
            --config)
                # 下一个参数应该是路径
                next_arg_idx=$(echo "${ORIGINAL_ARGS[@]}" | tr -s ' ' '\\n' | grep -nx -- "$arg" | cut -d: -f1)
                next_arg_val=""
                # A bit complex to get next arg correctly if there are multiple --config. Assume first one wins for global.
                # This simplified loop assumes a structure where we find the *first* --config for global.
                # A more robust way is to iterate with index.
                
                # Let's refine the loop for robust --config and --debug parsing ANYWHERE
                # This part is tricky with current single-pass.
                # Fallback to simpler: --debug first, then COMMAND, then parse ARGS for --config
                PROCESSED_ARGS+=("$arg") # For now, keep them all
                ;;
            *)
                PROCESSED_ARGS+=("$arg")
                ;;
        esac
    done

    # 重新实现参数解析，更健壮地处理全局参数
    # Pass 1: Extract global --debug
    if [[ "${PROCESSED_ARGS[0]}" == "--debug" ]]; then
        GLOBAL_DEBUG="--debug"
        show_info "已启用全局调试模式 (首参数)"
        PROCESSED_ARGS=("${PROCESSED_ARGS[@]:1}") # Remove --debug from head
        if [ ${#PROCESSED_ARGS[@]} -eq 0 ]; then
            show_error "启用调试模式后，需要指定要执行的命令"
            exit 1
        fi
    fi

    COMMAND="${PROCESSED_ARGS[0]}"
    ARGS=("${PROCESSED_ARGS[@]:1}") # Arguments after the command

    # Pass 2: Extract --config and potentially another --debug from ARGS
    FILTERED_ARGS=()
    i=0
    while [ $i -lt ${#ARGS[@]} ]; do
        arg="${ARGS[$i]}"
        case "$arg" in
            --debug)
                if [ -z "$GLOBAL_DEBUG" ]; then
                    GLOBAL_DEBUG="--debug"
                    show_info "已启用全局调试模式 (参数在命令后)"
                else
                    show_warning "检测到重复的 --debug 参数，将被忽略。"
                fi
                i=$((i+1))
                ;;
            --config)
                if [ $i -lt $((${#ARGS[@]}-1)) ] && [[ "${ARGS[$((i+1))]}" != --* ]]; then
                    if [ -z "$GLOBAL_CONFIG_FILE_PATH" ]; then # First --config encountered becomes global
                        GLOBAL_CONFIG_FILE_PATH="${ARGS[$((i+1))]}"
                        check_config_exists "$GLOBAL_CONFIG_FILE_PATH" # Validate file
                        show_info "全局配置文件已指定: $GLOBAL_CONFIG_FILE_PATH"
                    else
                        show_warning "检测到重复的 --config 参数。全局配置已设为 '$GLOBAL_CONFIG_FILE_PATH'。后续 '--config $arg_val' 将作为命令特定参数传递（如果命令支持）。"
                        FILTERED_ARGS+=("$arg") # Pass this specific --config to command
                        FILTERED_ARGS+=("${ARGS[$((i+1))]}")
                    fi
                    i=$((i+2)) # Skip --config and its value
                else
                    # Malformed --config (e.g., at the end or followed by another option)
                    # Add it to FILTERED_ARGS so validate_args for the command can complain
                    show_warning "参数 --config 格式不正确或缺少路径，将传递给命令自行处理。"
                    FILTERED_ARGS+=("$arg")
                    i=$((i+1))
                fi
                ;;
            *)
                FILTERED_ARGS+=("$arg")
                i=$((i+1))
                ;;
        esac
    done
    
    # 验证命令是否有效
    case "$COMMAND" in
        crawl|analyze|server|setup|driver|stats|check-tasks|clean|daily|rebuild-md|help|dingpush)
            # 有效命令
            ;;
        dingtalk)
            # 向后兼容：将dingtalk命令重定向到dingpush weekly
            show_warning "dingtalk命令已弃用，将自动转换为dingpush weekly命令"
            COMMAND="dingpush"
            set -- "weekly" "${FILTERED_ARGS[@]}"
            FILTERED_ARGS=("weekly" "${FILTERED_ARGS[@]}")
            ;;
        *)
            show_error "未知命令: $COMMAND"
            ;;
    esac
    
    # 执行命令
    case "$COMMAND" in
        crawl)
            # 如果第一个参数是 -h 或 --help，则显示 crawl 模式的帮助信息
            if [[ "${FILTERED_ARGS[0]}" == "-h" ]] || [[ "${FILTERED_ARGS[0]}" == "--help" ]]; then
                echo -e "${BLUE}显示 crawl 命令 (src.main --mode crawl) 的帮助信息...${NC}"
                activate_venv # 确保环境已激活
                python -m src.main --mode crawl --help
                exit $?
            fi

            if [ -n "$GLOBAL_DEBUG" ]; then
                crawl_data "${FILTERED_ARGS[@]}" --debug
            else
                crawl_data "${FILTERED_ARGS[@]}"
            fi
            
            RESULT=$?
            if [ $RESULT -eq 0 ]; then
                echo -e "${BLUE}==================================================${NC}"
                echo -e "${BLUE}爬取完成，正在重建元数据...${NC}"
                echo -e "${YELLOW}注意: 使用深度检查模式，但不会删除任何文件${NC}"
                echo -e "${BLUE}==================================================${NC}"
                
                if [ -n "$GLOBAL_DEBUG" ]; then
                    run_rebuild_metadata --type crawler --deep-check --debug
                else
                    run_rebuild_metadata --type crawler --deep-check
                fi
                
                echo -e "${BLUE}==================================================${NC}"
                echo -e "${GREEN}爬取及元数据更新流程已完成!${NC}"
            fi
            ;;
        analyze)
            # 如果第一个参数是 -h 或 --help，则显示 analyze 模式的帮助信息
            if [[ "${FILTERED_ARGS[0]}" == "-h" ]] || [[ "${FILTERED_ARGS[0]}" == "--help" ]]; then
                echo -e "${BLUE}显示 analyze 命令 (src.main --mode analyze) 的帮助信息...${NC}"
                activate_venv # 确保环境已激活
                python -m src.main --mode analyze --help
                exit $?
            fi

            if [ -n "$GLOBAL_DEBUG" ]; then
                analyze_data "${FILTERED_ARGS[@]}" --debug
            else
                analyze_data "${FILTERED_ARGS[@]}"
            fi
            
            RESULT=$?
            if [ $RESULT -eq 0 ]; then
                echo -e "${BLUE}==================================================${NC}"
                echo -e "${BLUE}分析完成，正在重建元数据...${NC}"
                echo -e "${YELLOW}注意: 使用深度检查模式，但不会删除任何文件${NC}"
                echo -e "${BLUE}==================================================${NC}"
                
                if [ -n "$GLOBAL_DEBUG" ]; then
                    run_rebuild_metadata --type analysis --deep-check --debug
                else
                    run_rebuild_metadata --type analysis --deep-check
                fi
                
                echo -e "${BLUE}==================================================${NC}"
                echo -e "${GREEN}分析及元数据更新流程已完成!${NC}"
            fi
            ;;
        server)
            # 如果第一个参数是 -h 或 --help，则显示 web_server 的帮助信息
            if [[ "${FILTERED_ARGS[0]}" == "-h" ]] || [[ "${FILTERED_ARGS[0]}" == "--help" ]]; then
                echo -e "${BLUE}显示 server 命令 (src.web_server.run) 的帮助信息...${NC}"
                activate_venv # 确保环境已激活
                python -m src.web_server.run --help
                exit $?
            fi

            if [ -n "$GLOBAL_DEBUG" ]; then
                run_server "${FILTERED_ARGS[@]}" --debug
            else
                run_server "${FILTERED_ARGS[@]}"
            fi
            ;;
        setup)
            # 验证参数
            validate_args "setup" "${FILTERED_ARGS[@]}" || exit 1
            setup_environment
            ;;
        driver)
            # 验证参数
            validate_args "driver" "${FILTERED_ARGS[@]}" || exit 1
            download_driver
            ;;
        stats)
            # 如果第一个参数是 -h 或 --help，则显示 compare_stats 的帮助信息
            if [[ "${FILTERED_ARGS[0]}" == "-h" ]] || [[ "${FILTERED_ARGS[0]}" == "--help" ]]; then
                echo -e "${BLUE}显示 stats 命令 (src.utils.compare_stats) 的帮助信息...${NC}"
                activate_venv # 确保环境已激活
                python -m src.utils.compare_stats --help
                exit $?
            fi

            if [ -n "$GLOBAL_DEBUG" ]; then
                compare_stats "${FILTERED_ARGS[@]}" --debug
            else
                compare_stats "${FILTERED_ARGS[@]}"
            fi
            ;;
        check-tasks)
            # 如果第一个参数是 -h 或 --help，则显示 compare_stats 的帮助信息
            # (check-tasks 是 compare_stats 的一个特定调用封装)
            if [[ "${FILTERED_ARGS[0]}" == "-h" ]] || [[ "${FILTERED_ARGS[0]}" == "--help" ]]; then
                echo -e "${BLUE}显示 check-tasks 相关模块 (src.utils.compare_stats) 的帮助信息...${NC}"
                activate_venv # 确保环境已激活
                python -m src.utils.compare_stats --help
                exit $?
            fi

            if [ -n "$GLOBAL_DEBUG" ]; then
                check_tasks "${FILTERED_ARGS[@]}" --debug
            else
                check_tasks "${FILTERED_ARGS[@]}"
            fi
            ;;
        clean)
            if [ -n "$GLOBAL_DEBUG" ]; then
                clean_files "${FILTERED_ARGS[@]}" --debug
            else
                clean_files "${FILTERED_ARGS[@]}"
            fi
            ;;
        daily)
            if [ -n "$GLOBAL_DEBUG" ]; then
                run_daily "${FILTERED_ARGS[@]}" --debug
            else
                run_daily "${FILTERED_ARGS[@]}"
            fi
            ;;
        rebuild-md)
            # 如果第一个参数是 -h 或 --help，则显示 rebuild_metadata 的帮助信息
            if [[ "${FILTERED_ARGS[0]}" == "-h" ]] || [[ "${FILTERED_ARGS[0]}" == "--help" ]]; then
                echo -e "${BLUE}显示 rebuild-md 命令 (src.utils.rebuild_metadata) 的帮助信息...${NC}"
                activate_venv # 确保环境已激活
                python -m src.utils.rebuild_metadata --help
                exit $?
            fi

            if [ -n "$GLOBAL_DEBUG" ]; then
                run_rebuild_metadata "${FILTERED_ARGS[@]}" --debug
            else
                run_rebuild_metadata "${FILTERED_ARGS[@]}"
            fi
            ;;
        dingpush)
            # 检查是否请求帮助或无参数
            if [[ -z "${FILTERED_ARGS[0]}" ]] || [[ "${FILTERED_ARGS[0]}" == "-h" ]] || [[ "${FILTERED_ARGS[0]}" == "--help" ]]; then
                echo -e "${BLUE}钉钉推送命令帮助${NC}"
                echo ""
                echo -e "${YELLOW}可用子命令:${NC}"
                echo -e "  ${GREEN}weekly-report${NC}                - 生成并推送每周竞品分析报告"
                echo -e "  ${GREEN}recent-report${NC} [天数]         - 生成并推送最近N天竞品分析报告"
                echo -e "  ${GREEN}monthly-domestic-report${NC}      - 生成并推送国内云厂商月报（华为/腾讯/火山）"
                echo -e "  ${GREEN}pushfile${NC} --filepath [路径]   - 推送指定的Markdown文件"
                echo ""
                echo -e "${YELLOW}选项:${NC}"
                echo -e "  ${GREEN}--robot${NC} [机器人名称]           - 使用指定的钉钉机器人推送（可指定多个）"
                echo -e "  ${GREEN}--config${NC} [配置文件]           - 指定配置文件路径"
                echo -e "  ${GREEN}--filepath${NC} [文件路径]         - 要推送的Markdown文件路径（pushfile命令必需）"
                echo -e "  ${GREEN}--year${NC} [年份]                 - 指定报告年份（monthly-domestic-report可用）"
                echo -e "  ${GREEN}--month${NC} [月份]                - 指定报告月份（monthly-domestic-report可用）"
                echo ""
                echo -e "${YELLOW}示例:${NC}"
                echo -e "  $0 dingpush weekly-report"
                echo -e "  $0 dingpush recent-report 7"
                echo -e "  $0 dingpush monthly-domestic-report"
                echo -e "  $0 dingpush monthly-domestic-report --year 2025 --month 11"
                echo -e "  $0 dingpush recent-report 7 --robot 机器人1"
                echo -e "  $0 dingpush pushfile --filepath data/reports/report.md"
                echo ""
                echo -e "${BLUE}提示: pushfile 子命令直接调用 dingtalk.py 模块${NC}"
                exit 0
            fi

            # 正常参数验证和执行
            validate_args "dingpush" "${FILTERED_ARGS[@]}" || exit 1 
            if [ -n "$GLOBAL_DEBUG" ]; then
                run_dingpush "${FILTERED_ARGS[@]}" --debug
            else
                run_dingpush "${FILTERED_ARGS[@]}"
            fi
            ;;
        help)
            # 验证参数
            validate_args "help" "${FILTERED_ARGS[@]}" || exit 1
            show_help
            ;;
        *)
            show_error "未知命令: $COMMAND"
            ;;
    esac
}

# 执行主函数
main "$@"
