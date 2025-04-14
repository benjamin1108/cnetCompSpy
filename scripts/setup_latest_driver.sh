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
# 获取项目根目录（假设脚本在scripts子目录下）
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 驱动目录（相对于项目根目录）
DRIVERS_DIR="$PROJECT_ROOT/drivers"

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

# 检查系统依赖
check_dependencies() {
    echo -e "${BLUE}检查系统依赖...${NC}"
    
    if [[ "$OS" == "linux" ]]; then
        # 提供Chrome运行所需的完整依赖库列表
        echo -e "${YELLOW}Chrome headless shell 在Linux系统上需要以下依赖库:${NC}"
        echo -e "${YELLOW}=======================================${NC}"
        echo -e "${YELLOW}- libatk-1.0-0           # ATK库${NC}"
        echo -e "${YELLOW}- libatk-bridge-2.0-0    # ATK桥接库${NC}"
        echo -e "${YELLOW}- libasound2             # ALSA音频库${NC}"
        echo -e "${YELLOW}- libcups2               # CUPS打印系统${NC}"
        echo -e "${YELLOW}- libdrm2                # Direct Rendering Manager${NC}"
        echo -e "${YELLOW}- libgtk-3-0             # GTK+3${NC}"
        echo -e "${YELLOW}- libgbm1                # Mesa GBM库${NC}"
        echo -e "${YELLOW}- libnss3                # NSS安全库${NC}"
        echo -e "${YELLOW}- libxcomposite1         # X Composite扩展${NC}"
        echo -e "${YELLOW}- libxdamage1            # X Damage扩展${NC}"
        echo -e "${YELLOW}- libxfixes3             # X Fixes扩展${NC}"
        echo -e "${YELLOW}- libxrandr2             # X Resize, Rotate and Reflection扩展${NC}"
        echo -e "${YELLOW}- libxshmfence1          # X shared memory fences${NC}"
        echo -e "${YELLOW}- libpango-1.0-0         # Pango文本布局库${NC}"
        echo -e "${YELLOW}- libpangocairo-1.0-0    # Pango Cairo渲染${NC}"
        echo -e "${YELLOW}- libcairo2              # Cairo绘图库${NC}"
        echo -e "${YELLOW}- libatspi2.0-0          # AT-SPI库${NC}"
        echo -e "${YELLOW}- libxkbcommon0          # XKB库${NC}"
        echo -e "${YELLOW}- libxss1                # XScreenSaver扩展库${NC}"
        echo -e "${YELLOW}- libxtst6               # X Test扩展库${NC}"
        echo -e "${YELLOW}- libexpat1              # Expat XML解析库${NC}"
        echo -e "${YELLOW}- libfontconfig1         # 字体配置库${NC}"
        echo -e "${YELLOW}- libxi6                 # X11 Input扩展库${NC}"
        echo -e "${YELLOW}- libx11-6               # X11客户端库${NC}"
        echo -e "${YELLOW}- libxcursor1            # X光标管理库${NC}"
        echo -e "${YELLOW}- libxext6               # X11扩展库${NC}"
        echo -e "${YELLOW}- libxrender1            # X Rendering扩展${NC}"
        echo -e "${YELLOW}- libglib2.0-0           # GLib库${NC}"
        echo -e "${YELLOW}- libnspr4               # Netscape可移植运行时${NC}"
        echo -e "${YELLOW}- libu2f-udev            # U2F设备支持${NC}"
        echo -e "${YELLOW}- libvulkan1             # Vulkan加载器${NC}"
        echo -e "${YELLOW}- libdbus-1-3            # D-Bus IPC系统${NC}"
        echo -e "${YELLOW}- libwayland-client0     # Wayland客户端库${NC}"
        echo -e "${YELLOW}- libwayland-egl1        # Wayland EGL库${NC}"
        echo -e "${YELLOW}- libwayland-cursor0     # Wayland光标库${NC}"
        echo -e "${YELLOW}=======================================${NC}"
        
        # 根据不同发行版提供安装命令
        if [[ -f /etc/debian_version ]]; then
            # Debian/Ubuntu系
            echo -e "${GREEN}在Debian/Ubuntu系统上，请尝试运行以下命令安装依赖:${NC}"
            echo -e "sudo apt-get update"
            echo -e "sudo apt-get install -y libatk1.0-0 libatk-bridge2.0-0 libasound2 libcups2 libdrm2 libgtk-3-0 libgbm1 libnss3 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libxshmfence1 libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libatspi2.0-0 libxkbcommon0 libxss1 libxtst6 libexpat1 libfontconfig1 libxi6 libx11-6 libxcursor1 libxext6 libxrender1 libglib2.0-0 libnspr4 libu2f-udev libvulkan1 libdbus-1-3 libwayland-client0 libwayland-egl1 libwayland-cursor0"
        elif [[ -f /etc/redhat-release ]]; then
            # RHEL/CentOS/Fedora系
            echo -e "${GREEN}在RHEL/CentOS/Fedora系统上，请尝试运行以下命令安装依赖:${NC}"
            echo -e "sudo yum install -y atk at-spi2-atk alsa-lib cups-libs libdrm gtk3 mesa-libgbm nss libXcomposite libXdamage libXfixes libXrandr libxshmfence pango pango-cairo cairo at-spi2-core libxkbcommon libXScrnSaver libXtst expat fontconfig libXi libX11 libXcursor libXext libXrender glib2 nspr libu2f-host vulkan-loader dbus-libs wayland-libs"
        elif [[ -f /etc/arch-release ]]; then
            # Arch系
            echo -e "${GREEN}在Arch系统上，请尝试运行以下命令安装依赖:${NC}"
            echo -e "sudo pacman -S --needed atk at-spi2-atk alsa-lib cups libdrm gtk3 libgbm nss libxcomposite libxdamage libxfixes libxrandr libxshmfence pango cairo at-spi2-core libxkbcommon libxss libxtst expat fontconfig libxi libx11 libxcursor libxext libxrender glib2 nspr libu2f-host vulkan-icd-loader dbus wayland"
        else
            echo -e "${GREEN}请使用系统的包管理器安装上述列出的库${NC}"
        fi
        
        # 试运行--no-sandbox模式作为备选方案
        echo -e "${YELLOW}作为临时解决方案，您也可以尝试使用--no-sandbox模式:${NC}"
        echo -e "在src/crawlers/common/base_crawler.py文件中找到_init_driver函数，确保chrome_options中包含'--no-sandbox'参数"
    elif [[ "$OS" == "mac" ]]; then
        echo -e "${YELLOW}在macOS上，大多数依赖由操作系统提供，但您可能需要确保XQuartz已安装（用于X11支持）${NC}"
        echo -e "${GREEN}您可以通过Homebrew安装XQuartz:${NC}"
        echo -e "brew install --cask xquartz"
    elif [[ "$OS" == "win" ]]; then
        echo -e "${YELLOW}在Windows上，大多数依赖已包含在安装包中${NC}"
        echo -e "${YELLOW}请确保已安装Visual C++ Redistributable包${NC}"
    fi
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
    
    # 检查系统依赖
    check_dependencies
    
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