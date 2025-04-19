#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 获取脚本所在目录和项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 切换到项目根目录
cd "$PROJECT_ROOT"

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

# 检查miniforge
check_miniforge || exit 1

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
