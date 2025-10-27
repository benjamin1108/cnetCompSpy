#!/bin/bash

# Chrome依赖安装脚本
# 用于安装chrome-headless-shell所需的系统依赖库

set -e

echo "=========================================="
echo "Chrome依赖检查和安装脚本"
echo "=========================================="
echo ""

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Chrome可执行文件路径
CHROME_PATH="$PROJECT_ROOT/drivers/chrome-headless-shell-linux64/chrome-headless-shell"

# 检查Chrome是否存在
if [ ! -f "$CHROME_PATH" ]; then
    echo "错误: 找不到chrome-headless-shell"
    echo "路径: $CHROME_PATH"
    echo "请先下载并安装chrome-headless-shell"
    exit 1
fi

echo "找到chrome-headless-shell: $CHROME_PATH"
echo ""

# 检查缺少的依赖
echo "检查缺少的依赖库..."
MISSING_LIBS=$(ldd "$CHROME_PATH" 2>&1 | grep "not found" | awk '{print $1}' || true)

if [ -z "$MISSING_LIBS" ]; then
    echo "✓ 所有依赖库都已安装"
    echo ""
    echo "测试Chrome运行..."
    if "$CHROME_PATH" --version; then
        echo "✓ Chrome运行正常"
        exit 0
    else
        echo "✗ Chrome运行失败"
        exit 1
    fi
fi

echo "缺少以下依赖库:"
echo "$MISSING_LIBS"
echo ""

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "无法检测操作系统类型"
    exit 1
fi

echo "检测到操作系统: $OS"
echo ""

# 根据操作系统安装依赖
case $OS in
    ubuntu|debian)
        echo "使用apt-get安装依赖..."
        echo "需要sudo权限，可能会提示输入密码"
        echo ""
        
        sudo apt-get update
        sudo apt-get install -y \
            libatk-bridge2.0-0 \
            libatk1.0-0 \
            libatspi2.0-0 \
            libcups2 \
            libdbus-1-3 \
            libdrm2 \
            libgbm1 \
            libgtk-3-0 \
            libnspr4 \
            libnss3 \
            libwayland-client0 \
            libxcomposite1 \
            libxdamage1 \
            libxfixes3 \
            libxkbcommon0 \
            libxrandr2 \
            xdg-utils \
            fonts-liberation \
            libasound2 \
            libcairo2 \
            libgdk-pixbuf2.0-0 \
            libpango-1.0-0 \
            libx11-6 \
            libxcb1 \
            libxext6
        ;;
    
    centos|rhel|fedora)
        echo "使用yum/dnf安装依赖..."
        echo "需要sudo权限，可能会提示输入密码"
        echo ""
        
        if command -v dnf &> /dev/null; then
            PKG_MGR="dnf"
        else
            PKG_MGR="yum"
        fi
        
        sudo $PKG_MGR install -y \
            at-spi2-atk \
            atk \
            cups-libs \
            dbus-libs \
            libdrm \
            mesa-libgbm \
            gtk3 \
            nspr \
            nss \
            libwayland-client \
            libXcomposite \
            libXdamage \
            libXfixes \
            libxkbcommon \
            libXrandr \
            xdg-utils \
            liberation-fonts \
            alsa-lib \
            cairo \
            gdk-pixbuf2 \
            pango \
            libX11 \
            libxcb \
            libXext
        ;;
    
    *)
        echo "不支持的操作系统: $OS"
        echo "请手动安装以下依赖库:"
        echo "$MISSING_LIBS"
        echo ""
        echo "参考文档: docs/webdriver_troubleshooting.md"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "依赖安装完成，重新检查..."
echo "=========================================="
echo ""

# 重新检查依赖
MISSING_LIBS=$(ldd "$CHROME_PATH" 2>&1 | grep "not found" | awk '{print $1}' || true)

if [ -z "$MISSING_LIBS" ]; then
    echo "✓ 所有依赖库都已安装"
    echo ""
    echo "测试Chrome运行..."
    if "$CHROME_PATH" --version; then
        echo "✓ Chrome运行正常"
        echo ""
        echo "=========================================="
        echo "安装成功！现在可以运行爬虫程序了"
        echo "=========================================="
        exit 0
    else
        echo "✗ Chrome运行失败"
        exit 1
    fi
else
    echo "✗ 仍然缺少以下依赖库:"
    echo "$MISSING_LIBS"
    echo ""
    echo "请手动安装这些依赖库"
    exit 1
fi
