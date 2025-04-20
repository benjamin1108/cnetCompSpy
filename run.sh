#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # 无颜色

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 显示帮助信息
show_help() {
    echo -e "${BLUE}云计算网络竞争动态分析工具${NC}"
    echo -e "${YELLOW}用法:${NC}"
    echo -e "  $0 [命令] [选项]"
    echo ""
    echo -e "${YELLOW}命令:${NC}"
    echo -e "  ${GREEN}crawl${NC}    - 爬取数据"
    echo -e "  ${GREEN}analyze${NC}  - 分析数据"
    echo -e "  ${GREEN}server${NC}   - 启动Web服务器"
    echo -e "  ${GREEN}setup${NC}    - 设置环境（创建虚拟环境并安装依赖）"
    echo -e "  ${GREEN}driver${NC}   - 下载最新的WebDriver"
    echo -e "  ${GREEN}stats${NC}    - 比较元数据和实际文件统计"
    echo -e "  ${GREEN}check-tasks${NC} - 检查任务完成状态，显示未完成任务的文件"
    echo -e "  ${GREEN}clean${NC}    - 清理中间文件和临时文件"
    echo -e "  ${GREEN}daily${NC}    - 执行每日爬取与分析任务"
    echo -e "  ${GREEN}help${NC}     - 显示此帮助信息"
    echo ""
    echo -e "${YELLOW}选项:${NC}"
    echo -e "  ${GREEN}--vendor${NC} [aws|azure|gcp]  - 指定厂商（仅用于crawl命令）"
    echo -e "  ${GREEN}--limit${NC} [数字]            - 限制爬取的文章数量（仅用于crawl命令）"
    echo -e "  ${GREEN}--host${NC} [主机地址]         - 指定服务器主机地址（仅用于server命令）"
    echo -e "  ${GREEN}--port${NC} [端口号]           - 指定服务器端口（仅用于server命令）"
    echo -e "  ${GREEN}--debug${NC}                  - 启用调试模式"
    echo -e "  ${GREEN}--clean${NC}                  - 清理数据目录（仅用于crawl和analyze命令）"
    echo -e "  ${GREEN}--force${NC}                  - 强制执行，忽略本地metadata或文件是否已存在"
    echo -e "  ${GREEN}--all${NC}                    - 清理所有中间文件（仅用于clean命令）"
    echo -e "  ${GREEN}--pyc${NC}                    - 清理Python字节码文件（仅用于clean命令）"
    echo -e "  ${GREEN}--logs${NC}                   - 清理日志文件（仅用于clean命令）"
    echo -e "  ${GREEN}--temp${NC}                   - 清理临时文件（仅用于clean命令）"
    echo -e "  ${GREEN}--data${NC}                   - 清理data目录（仅用于clean命令）"
    echo -e "  ${GREEN}--detailed${NC}               - 显示详细信息（仅用于stats命令）"
    echo -e "  ${GREEN}--tasks-only${NC}             - 只显示任务信息（仅用于check-tasks命令）"
    echo ""
    echo -e "${YELLOW}示例:${NC}"
    echo -e "  $0 crawl                     # 爬取所有厂商的数据"
    echo -e "  $0 crawl --vendor aws        # 仅爬取AWS的数据"
    echo -e "  $0 crawl --limit 10          # 每个来源最多爬取10篇文章"
    echo -e "  $0 crawl --force             # 强制爬取所有数据，忽略本地metadata"
    echo -e "  $0 analyze                   # 分析所有爬取的数据"
    echo -e "  $0 analyze --force           # 强制分析所有数据，忽略文件是否已存在"
    echo -e "  $0 server                    # 启动Web服务器（默认127.0.0.1:5000）"
    echo -e "  $0 server --host 0.0.0.0 --port 8080  # 指定主机和端口启动服务器"
    echo -e "  $0 setup                     # 设置环境"
    echo -e "  $0 driver                    # 下载最新的WebDriver"
    echo -e "  $0 stats                     # 比较元数据和实际文件统计"
    echo -e "  $0 stats --detailed          # 显示详细的文件对比信息"
    echo -e "  $0 clean                     # 清理所有中间文件和临时文件"
    echo -e "  $0 clean --pyc               # 只清理Python字节码文件"
    echo -e "  $0 clean --logs              # 只清理日志文件"
    echo -e "  $0 clean --data              # 只清理data目录"
    echo -e "  $0 daily                     # 执行每日爬取与分析任务"
}

# 显示错误信息
show_error() {
    echo -e "${RED}错误: $1${NC}"
    echo -e "${BLUE}使用 '$0 help' 查看完整帮助${NC}"
    exit 1
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
            local valid_opts=("--vendor" "--source" "--limit" "--debug" "--clean" "--force")
            local requires_value=("--vendor" "--source" "--limit")
            
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
                                show_error "无效的厂商: $2，有效值为: aws, azure, gcp"
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
            
        analyze)
            # analyze命令有效参数
            local valid_opts=("--debug" "--clean" "--force")
            
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
            # daily命令没有特定参数，所有参数都传递给内部脚本
            return 0
            ;;
            
        setup|driver|help)
            # 这些命令不接受任何参数
            if [[ $# -gt 0 ]]; then
                invalid_args=("$@")
            fi
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
                echo -e "${GREEN}--vendor [aws|azure|gcp], --limit [数字], --debug, --clean, --force${NC}"
                ;;
            analyze)
                echo -e "${GREEN}--debug, --clean, --force${NC}"
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
        esac
        
        echo -e "${BLUE}例如: $0 $cmd ${NC}"
        echo -e "${BLUE}使用 '$0 help' 查看完整帮助${NC}"
        return 1
    fi
    
    return 0
}

# 检查是否安装了miniforge
check_miniforge() {
    echo -e "${BLUE}检查Miniforge是否已安装...${NC}"
    
    # 检查是否可以执行conda命令
    if command -v conda >/dev/null 2>&1; then
        echo -e "${GREEN}Miniforge已安装${NC}"
        return 0
    else
        echo -e "${RED}未检测到Miniforge${NC}"
        echo -e "${YELLOW}请按照以下步骤安装Miniforge:${NC}"
        echo -e ""
        
        # 根据系统类型显示不同的安装说明
        case "$(uname -s)" in
            Darwin*)    # macOS
                echo -e "${BLUE}macOS安装步骤:${NC}"
                echo -e "1. 执行以下命令下载安装脚本:"
                echo -e "   ${GREEN}curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh${NC}"
                echo -e "   (对于M1/M2 Mac，请使用: ${GREEN}curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh${NC})"
                echo -e "2. 执行安装脚本:"
                echo -e "   ${GREEN}bash Miniforge3-MacOSX-x86_64.sh${NC}"
                echo -e "   (或者 ${GREEN}bash Miniforge3-MacOSX-arm64.sh${NC} 如果是M1/M2 Mac)"
                echo -e "3. 按照提示完成安装并初始化"
                echo -e "4. 关闭并重新打开终端，或者执行 ${GREEN}source ~/.bashrc${NC} 或 ${GREEN}source ~/.zshrc${NC}"
                ;;
            Linux*)     # Linux
                echo -e "${BLUE}Linux安装步骤:${NC}"
                echo -e "1. 执行以下命令下载安装脚本:"
                echo -e "   ${GREEN}wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh${NC}"
                echo -e "2. 执行安装脚本:"
                echo -e "   ${GREEN}bash Miniforge3-Linux-x86_64.sh${NC}"
                echo -e "3. 按照提示完成安装并初始化"
                echo -e "4. 关闭并重新打开终端，或者执行 ${GREEN}source ~/.bashrc${NC}"
                ;;
            CYGWIN*|MINGW*|MSYS*)  # Windows
                echo -e "${BLUE}Windows安装步骤:${NC}"
                echo -e "1. 下载安装程序: ${GREEN}https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe${NC}"
                echo -e "2. 运行下载的安装程序并按照提示完成安装"
                ;;
            *)
                echo -e "${BLUE}通用安装步骤:${NC}"
                echo -e "1. 访问 ${GREEN}https://github.com/conda-forge/miniforge${NC} 获取最新的安装指南"
                ;;
        esac
        
        echo -e ""
        echo -e "${BLUE}安装完成后，请再次运行本脚本${NC}"
        return 1
    fi
}

# 激活虚拟环境
activate_venv() {
    # 检查是否存在名为venv的conda环境
    if conda env list | grep -q "^venv "; then
        echo -e "${GREEN}找到venv环境，正在激活...${NC}"
        eval "$(conda shell.bash hook)"
        conda activate venv
    else
        echo -e "${YELLOW}未找到venv环境，正在创建...${NC}"
        eval "$(conda shell.bash hook)"
        conda create -y -n venv python=3.11
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}venv环境已创建，正在激活...${NC}"
            conda activate venv
        else
            echo -e "${RED}创建venv环境失败，请检查miniforge安装是否正确。${NC}"
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
    
    # 检查miniforge
    check_miniforge || exit 1
    
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
    
    # 验证参数
    validate_args "crawl" "$@" || return 1
    
    # 激活虚拟环境
    activate_venv
    
    # 调用Python模块
    python -m src.main --mode crawl "$@"
}

# 分析数据
analyze_data() {
    echo -e "${BLUE}开始分析数据...${NC}"
    
    # 验证参数
    validate_args "analyze" "$@" || return 1
    
    # 激活虚拟环境
    activate_venv
    
    # 调用Python模块
    python -m src.main --mode analyze "$@"
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

# 主函数
main() {
    # 如果没有参数，显示帮助信息
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    # 解析命令
    COMMAND="$1"
    shift
    
    # 验证命令是否有效
    case "$COMMAND" in
        crawl|analyze|server|setup|driver|stats|check-tasks|clean|daily|help)
            # 有效命令
            ;;
        *)
            show_error "未知命令: $COMMAND。有效命令: crawl, analyze, server, setup, driver, stats, check-tasks, clean, daily, help"
            ;;
    esac
    
    # 执行命令
    case "$COMMAND" in
        crawl)
            crawl_data "$@"
            ;;
        analyze)
            analyze_data "$@"
            ;;
        server)
            run_server "$@"
            ;;
        setup)
            # 验证参数
            validate_args "setup" "$@" || exit 1
            setup_environment
            ;;
        driver)
            # 验证参数
            validate_args "driver" "$@" || exit 1
            download_driver
            ;;
        stats)
            compare_stats "$@"
            ;;
        check-tasks)
            check_tasks "$@"
            ;;
        clean)
            clean_files "$@"
            ;;
        daily)
            # validate_args "daily" "$@" || exit 1  # daily命令允许任意参数传递给内部脚本
            run_daily "$@"
            ;;
        help)
            # 验证参数
            validate_args "help" "$@" || exit 1
            show_help
            ;;
        *)
            show_error "未知命令: $COMMAND"
            ;;
    esac
}

# 执行主函数
main "$@"
