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
    echo -e "  ${GREEN}stats --detailed${NC} - 详细对比元数据和实际文件，显示时间和文件名"
    echo -e "  ${GREEN}check-tasks${NC} - 检查任务完成状态，显示未完成任务的文件"
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
    echo -e "  $0 daily                     # 执行每日爬取与分析任务"
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
    
    # 检查是否安装了tabulate库
    if ! pip list | grep -q "tabulate"; then
        echo -e "${YELLOW}未安装tabulate库，正在安装...${NC}"
        pip install tabulate
    fi
    
    pip install -r "$SCRIPT_DIR/requirements.txt"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}依赖安装成功${NC}"
    else
        echo -e "${RED}依赖安装失败，请检查网络连接和requirements.txt文件${NC}"
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
    
    # 激活虚拟环境
    activate_venv
    
    # 调用Python模块
    python -m src.main --mode crawl "$@"
}

# 分析数据
analyze_data() {
    echo -e "${BLUE}开始分析数据...${NC}"
    
    # 激活虚拟环境
    activate_venv
    
    # 调用Python模块
    python -m src.main --mode analyze "$@"
}

# 比较元数据和实际文件统计
compare_stats() {
    echo -e "${BLUE}开始比较元数据和实际文件统计...${NC}"
    
    # 激活虚拟环境
    activate_venv
    
    # 调用Python模块
    python -m src.utils.compare_stats "$@"
}

# 检查任务完成状态
check_tasks() {
    echo -e "${BLUE}检查任务完成状态...${NC}"
    
    # 激活虚拟环境
    activate_venv
    
    # 调用Python模块，只显示未完成任务的文件
    python -m src.utils.compare_stats --detailed --tasks-only "$@"
}

# 启动Web服务器
run_server() {
    echo -e "${BLUE}启动Web服务器...${NC}"
    
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
            setup_environment
            ;;
        driver)
            download_driver
            ;;
        stats)
            compare_stats "$@"
            ;;
        check-tasks)
            check_tasks "$@"
            ;;
        daily)
            run_daily "$@"
            ;;
        help)
            show_help
            ;;
        *)
            echo -e "${RED}未知命令: $COMMAND${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
