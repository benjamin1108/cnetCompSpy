#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # 无颜色

# 驱动目录
DRIVERS_DIR="drivers"

# 确保驱动目录存在
mkdir -p "$DRIVERS_DIR"
mkdir -p "$DRIVERS_DIR/download"

# 检测操作系统
detect_os() {
    echo -e "${BLUE}检测操作系统...${NC}"
    
    # 操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="mac"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="win"
    else
        OS="unknown"
    fi
    
    # 架构
    MACHINE=$(uname -m)
    if [[ "$MACHINE" == "x86_64" ]]; then
        ARCH="x64"
    elif [[ "$MACHINE" == "arm64" ]] || [[ "$MACHINE" == "aarch64" ]]; then
        ARCH="arm64"
    else
        ARCH="$MACHINE"
    fi

    # 平台名称映射
    if [[ "$OS" == "mac" && "$ARCH" == "arm64" ]]; then
        PLATFORM="mac-arm64"
    elif [[ "$OS" == "mac" && "$ARCH" == "x64" ]]; then
        PLATFORM="mac-x64"
    elif [[ "$OS" == "linux" && "$ARCH" == "x64" ]]; then
        PLATFORM="linux64"
    elif [[ "$OS" == "win" && "$ARCH" == "x64" ]]; then
        PLATFORM="win64"
    else
        echo -e "${RED}不支持的操作系统/架构组合: $OS/$ARCH${NC}"
        exit 1
    fi

    echo -e "${GREEN}检测到系统: $OS ($ARCH)${NC}"
}

# 获取最新Chrome版本
get_latest_version() {
    echo -e "${BLUE}获取最新Chrome版本信息...${NC}"
    
    VERSION_URL="https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json"
    if command -v curl &> /dev/null; then
        VERSION_JSON=$(curl -s "$VERSION_URL")
    elif command -v wget &> /dev/null; then
        VERSION_JSON=$(wget -q -O - "$VERSION_URL")
    else
        echo -e "${RED}错误: 需要安装curl或wget来下载版本信息${NC}"
        exit 1
    fi
    
    # 解析JSON获取稳定版本
    if command -v jq &> /dev/null; then
        CHROME_VERSION=$(echo "$VERSION_JSON" | jq -r '.channels.Stable.version')
    else
        # 使用grep和sed作为jq的替代方案（不太可靠但可作为备选）
        CHROME_VERSION=$(echo "$VERSION_JSON" | grep -o '"Stable":{[^}]*"version":"[^"]*"' | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    fi
    
    if [[ -z "$CHROME_VERSION" ]]; then
        echo -e "${RED}无法获取Chrome版本信息${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}找到最新稳定版本: $CHROME_VERSION${NC}"
}

# 下载文件通用函数
download_file() {
    local url=$1
    local dest_path=$2
    local description=$3
    
    echo -e "${BLUE}下载$description: $url${NC}"
    
    if command -v curl &> /dev/null; then
        curl -# -L -o "$dest_path" "$url"
    elif command -v wget &> /dev/null; then
        wget --show-progress -q -O "$dest_path" "$url"
    else
        echo -e "${RED}错误: 需要安装curl或wget来下载文件${NC}"
        return 1
    fi
    
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}下载$description失败${NC}"
        return 1
    fi
    
    echo -e "${GREEN}下载完成${NC}"
    return 0
}

# 下载chrome-headless-shell
download_chrome_headless_shell() {
    echo -e "${BLUE}下载chrome-headless-shell...${NC}"
    
    DOWNLOAD_URL="https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/$PLATFORM/chrome-headless-shell-$PLATFORM.zip"
    ZIP_FILE="$DRIVERS_DIR/download/chrome-headless-shell.zip"
    
    download_file "$DOWNLOAD_URL" "$ZIP_FILE" "chrome-headless-shell"
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    
    # 解压文件
    echo -e "${BLUE}解压chrome-headless-shell...${NC}"
    
    CHROME_HEADLESS_DIR="$DRIVERS_DIR/chrome-headless-shell-$PLATFORM"
    
    # 如果目录已存在，先删除
    if [[ -d "$CHROME_HEADLESS_DIR" ]]; then
        rm -rf "$CHROME_HEADLESS_DIR"
    fi
    
    # 解压
    if command -v unzip &> /dev/null; then
        unzip -q "$ZIP_FILE" -d "$DRIVERS_DIR"
    else
        echo -e "${RED}错误: 需要安装unzip来解压文件${NC}"
        return 1
    fi
    
    # 如果需要重命名目录
    for dir in "$DRIVERS_DIR"/chrome-headless-shell-*; do
        if [[ -d "$dir" && "$dir" != "$CHROME_HEADLESS_DIR" ]]; then
            mv "$dir" "$CHROME_HEADLESS_DIR"
        fi
    done
    
    echo -e "${GREEN}chrome-headless-shell已解压到: $CHROME_HEADLESS_DIR${NC}"
    
    # 设置可执行权限
    CHROME_BIN="$CHROME_HEADLESS_DIR/chrome-headless-shell"
    if [[ "$OS" == "win" ]]; then
        CHROME_BIN="$CHROME_BIN.exe"
    fi
    
    if [[ -f "$CHROME_BIN" && ("$OS" == "mac" || "$OS" == "linux") ]]; then
        chmod +x "$CHROME_BIN"
        echo -e "${GREEN}已设置执行权限${NC}"
    fi
    
    # 清理下载文件
    rm "$ZIP_FILE"
    
    return 0
}

# 下载ChromeDriver
download_chromedriver() {
    echo -e "${BLUE}下载ChromeDriver...${NC}"
    
    DOWNLOAD_URL="https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/$PLATFORM/chromedriver-$PLATFORM.zip"
    ZIP_FILE="$DRIVERS_DIR/download/chromedriver.zip"
    
    download_file "$DOWNLOAD_URL" "$ZIP_FILE" "ChromeDriver"
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    
    # 解压文件
    echo -e "${BLUE}解压ChromeDriver...${NC}"
    
    if command -v unzip &> /dev/null; then
        unzip -q "$ZIP_FILE" -d "$DRIVERS_DIR/download"
    else
        echo -e "${RED}错误: 需要安装unzip来解压文件${NC}"
        return 1
    fi
    
    # 解压后的文件在子目录中
    CHROMEDRIVER_SUBDIR="chromedriver-$PLATFORM"
    CHROMEDRIVER_SRC="$DRIVERS_DIR/download/$CHROMEDRIVER_SUBDIR/chromedriver"
    if [[ "$OS" == "win" ]]; then
        CHROMEDRIVER_SRC="$CHROMEDRIVER_SRC.exe"
    fi
    
    # 将chromedriver复制到drivers目录
    CHROMEDRIVER_DEST="$DRIVERS_DIR/chromedriver"
    if [[ "$OS" == "win" ]]; then
        CHROMEDRIVER_DEST="$CHROMEDRIVER_DEST.exe"
    fi
    
    # 如果目标文件已存在，先删除
    if [[ -f "$CHROMEDRIVER_DEST" ]]; then
        rm "$CHROMEDRIVER_DEST"
    fi
    
    cp "$CHROMEDRIVER_SRC" "$CHROMEDRIVER_DEST"
    echo -e "${GREEN}ChromeDriver已复制到: $CHROMEDRIVER_DEST${NC}"
    
    # 设置可执行权限
    if [[ -f "$CHROMEDRIVER_DEST" && ("$OS" == "mac" || "$OS" == "linux") ]]; then
        chmod +x "$CHROMEDRIVER_DEST"
        echo -e "${GREEN}已设置执行权限${NC}"
    fi
    
    # 清理下载文件
    rm "$ZIP_FILE"
    rm -rf "$DRIVERS_DIR/download/$CHROMEDRIVER_SUBDIR"
    
    return 0
}

# 创建配置文件
create_config_file() {
    echo -e "${BLUE}创建配置文件...${NC}"
    
    CONFIG_FILE="$DRIVERS_DIR/webdriver_config.json"
    
    CHROME_BIN="$DRIVERS_DIR/chrome-headless-shell-$PLATFORM/chrome-headless-shell"
    if [[ "$OS" == "win" ]]; then
        CHROME_BIN="$CHROME_BIN.exe"
    fi
    
    CHROMEDRIVER_PATH="$DRIVERS_DIR/chromedriver"
    if [[ "$OS" == "win" ]]; then
        CHROMEDRIVER_PATH="$CHROMEDRIVER_PATH.exe"
    fi
    
    # 生成配置文件内容
    CONFIG_CONTENT="{
  \"version\": \"$CHROME_VERSION\",
  \"os\": \"$OS\",
  \"arch\": \"$ARCH\",
  \"chrome_path\": \"$CHROME_BIN\",
  \"chromedriver_path\": \"$CHROMEDRIVER_PATH\",
  \"installed_on\": \"$(date)\"
}"
    
    # 写入配置文件
    echo "$CONFIG_CONTENT" > "$CONFIG_FILE"
    
    echo -e "${GREEN}配置文件已创建: $CONFIG_FILE${NC}"
}

# 主函数
main() {
    echo -e "${PURPLE}======= 驱动程序设置脚本 =======${NC}"
    echo -e "${YELLOW}该脚本将下载最新版本的chrome-headless-shell和ChromeDriver${NC}"
    
    detect_os
    get_latest_version
    
    # 下载chrome-headless-shell
    download_chrome_headless_shell
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}chrome-headless-shell下载失败${NC}"
        exit 1
    fi
    
    # 下载ChromeDriver
    download_chromedriver
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}ChromeDriver下载失败${NC}"
        exit 1
    fi
    
    # 创建配置文件
    create_config_file
    
    # 清理下载目录
    rm -rf "$DRIVERS_DIR/download"
    
    echo -e "${PURPLE}======= 安装完成! =======${NC}"
    echo -e "${GREEN}chrome-headless-shell版本: $CHROME_VERSION${NC}"
    echo -e "${GREEN}ChromeDriver版本: $CHROME_VERSION${NC}"
    echo -e "${GREEN}chrome-headless-shell路径: $CHROME_BIN${NC}"
    echo -e "${GREEN}ChromeDriver路径: $CHROMEDRIVER_DEST${NC}"
    echo -e "${GREEN}配置信息已保存到: $CONFIG_FILE${NC}"
}

# 执行主函数
main 