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
    echo -e "  ${GREEN}help${NC}     - 显示此帮助信息"
    echo ""
    echo -e "${YELLOW}选项:${NC}"
    echo -e "  ${GREEN}--vendor${NC} [aws|azure|gcp]  - 指定厂商（仅用于crawl命令）"
    echo -e "  ${GREEN}--limit${NC} [数字]            - 限制爬取的文章数量（仅用于crawl命令）"
    echo -e "  ${GREEN}--host${NC} [主机地址]         - 指定服务器主机地址（仅用于server命令）"
    echo -e "  ${GREEN}--port${NC} [端口号]           - 指定服务器端口（仅用于server命令）"
    echo -e "  ${GREEN}--debug${NC}                  - 启用调试模式"
    echo -e "  ${GREEN}--clean${NC}                  - 清理数据目录（仅用于crawl和analyze命令）"
    echo ""
    echo -e "${YELLOW}示例:${NC}"
    echo -e "  $0 crawl                     # 爬取所有厂商的数据"
    echo -e "  $0 crawl --vendor aws        # 仅爬取AWS的数据"
    echo -e "  $0 crawl --limit 10          # 每个来源最多爬取10篇文章"
    echo -e "  $0 analyze                   # 分析所有爬取的数据"
    echo -e "  $0 server                    # 启动Web服务器（默认127.0.0.1:5000）"
    echo -e "  $0 server --host 0.0.0.0 --port 8080  # 指定主机和端口启动服务器"
    echo -e "  $0 setup                     # 设置环境"
    echo -e "  $0 driver                    # 下载最新的WebDriver"
}

# 激活虚拟环境
activate_venv() {
    # 检查当前目录是否存在venv目录
    if [ -d "venv" ]; then
        echo -e "${GREEN}找到venv目录，正在激活...${NC}"
        source venv/bin/activate
    else
        echo -e "${YELLOW}未找到venv目录，正在创建...${NC}"
        python3 -m venv venv
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}venv目录已创建，正在激活...${NC}"
            source venv/bin/activate
        else
            echo -e "${RED}创建venv失败，请检查python3和venv模块是否可用。${NC}"
            exit 1
        fi
    fi
    echo -e "${GREEN}Python虚拟环境已激活${NC}"
}

# 安装依赖
install_dependencies() {
    echo -e "${BLUE}正在安装项目依赖...${NC}"
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}依赖安装成功${NC}"
    else
        echo -e "${RED}依赖安装失败，请检查网络连接和requirements.txt文件${NC}"
        exit 1
    fi
}

# 设置环境
setup_environment() {
    activate_venv
    install_dependencies
    echo -e "${GREEN}环境设置完成${NC}"
}

# 下载WebDriver
download_driver() {
    echo -e "${BLUE}正在下载最新的WebDriver...${NC}"
    bash scripts/setup_latest_driver.sh
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}WebDriver下载成功${NC}"
    else
        echo -e "${RED}WebDriver下载失败${NC}"
        exit 1
    fi
}

# 爬取数据
crawl_data() {
    activate_venv
    echo -e "${BLUE}开始爬取数据...${NC}"
    python -m src.main --mode crawl $@
}

# 分析数据
analyze_data() {
    activate_venv
    echo -e "${BLUE}开始分析数据...${NC}"
    python -m src.main --mode analyze $@
}

# 启动Web服务器
run_server() {
    activate_venv
    echo -e "${BLUE}启动Web服务器...${NC}"
    
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
            crawl_data $@
            ;;
        analyze)
            analyze_data $@
            ;;
        server)
            run_server $@
            ;;
        setup)
            setup_environment
            ;;
        driver)
            download_driver
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
