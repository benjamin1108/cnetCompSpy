#!/bin/bash

# 该脚本用于自动下载和配置chrome-headless-shell
# 支持Linux、macOS和Windows系统

set -e

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 设置版本和文件名
CHROME_VERSION="122.0.6261.94"  # 更新到较新的版本
DRIVERS_DIR="drivers"
DOWNLOAD_DIR="$DRIVERS_DIR/download"

# 创建目录
mkdir -p $DRIVERS_DIR
mkdir -p $DOWNLOAD_DIR

# 检测操作系统类型
detect_os() {
  echo -e "${BLUE}检测操作系统...${NC}"
  case "$(uname -s)" in
    Linux*)     OS="linux";;
    Darwin*)    OS="mac";;
    CYGWIN*|MINGW*|MSYS*) OS="win";;
    *)          OS="unknown";;
  esac

  # 检测是否是ARM架构
  if [[ "$(uname -m)" == "arm"* ]] || [[ "$(uname -m)" == "aarch"* ]]; then
    ARCH="arm64"
  else
    ARCH="x64"
  fi

  echo -e "${GREEN}检测到系统: $OS ($ARCH)${NC}"
}

# 设置下载URL
set_download_url() {
  BASE_URL="https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing"
  
  case $OS in
    "linux")
      if [[ "$ARCH" == "arm64" ]]; then
        DOWNLOAD_URL="$BASE_URL/$CHROME_VERSION/linux-arm64/chrome-headless-shell-linux-arm64.zip"
      else
        DOWNLOAD_URL="$BASE_URL/$CHROME_VERSION/linux64/chrome-headless-shell-linux64.zip"
      fi
      ;;
    "mac")
      if [[ "$ARCH" == "arm64" ]]; then
        DOWNLOAD_URL="$BASE_URL/$CHROME_VERSION/mac-arm64/chrome-headless-shell-mac-arm64.zip"
      else
        DOWNLOAD_URL="$BASE_URL/$CHROME_VERSION/mac-x64/chrome-headless-shell-mac-x64.zip"
      fi
      ;;
    "win")
      DOWNLOAD_URL="$BASE_URL/$CHROME_VERSION/win64/chrome-headless-shell-win64.zip"
      ;;
    *)
      echo -e "${RED}不支持的操作系统: $OS${NC}"
      exit 1
      ;;
  esac
}

# 下载headless chrome
download_chrome() {
  echo -e "${BLUE}下载chrome-headless-shell...${NC}"
  echo -e "下载URL: $DOWNLOAD_URL"
  
  # 使用系统命令下载
  if command -v curl &> /dev/null; then
    curl -L "$DOWNLOAD_URL" -o "$DOWNLOAD_DIR/chrome-headless-shell.zip"
  elif command -v wget &> /dev/null; then
    wget -O "$DOWNLOAD_DIR/chrome-headless-shell.zip" "$DOWNLOAD_URL"
  else
    echo -e "${RED}错误: 需要curl或wget来下载文件${NC}"
    exit 1
  fi
  
  echo -e "${GREEN}下载完成${NC}"
}

# 解压文件
extract_chrome() {
  echo -e "${BLUE}解压chrome-headless-shell...${NC}"
  
  if command -v unzip &> /dev/null; then
    unzip -o "$DOWNLOAD_DIR/chrome-headless-shell.zip" -d "$DRIVERS_DIR"
  else
    echo -e "${RED}错误: 需要unzip来解压文件${NC}"
    exit 1
  fi
  
  echo -e "${GREEN}解压完成${NC}"
}

# 设置权限
set_permissions() {
  echo -e "${BLUE}设置执行权限...${NC}"
  
  if [[ "$OS" == "linux" ]] || [[ "$OS" == "mac" ]]; then
    chmod +x "$DRIVERS_DIR"/chrome-headless-shell*/chrome-headless-shell
    if [ -f "$DRIVERS_DIR"/chrome-headless-shell*/chrome ]; then
      chmod +x "$DRIVERS_DIR"/chrome-headless-shell*/chrome
    fi
  fi
  
  echo -e "${GREEN}权限设置完成${NC}"
}

# 清理下载文件
cleanup() {
  echo -e "${BLUE}清理临时文件...${NC}"
  rm -rf $DOWNLOAD_DIR
  echo -e "${GREEN}清理完成${NC}"
}

# 创建配置文件
create_config() {
  echo -e "${BLUE}创建WebDriver配置文件...${NC}"
  
  CONFIG_FILE="$DRIVERS_DIR/webdriver_config.json"
  
  # 获取Chrome路径
  CHROME_HEADLESS_DIR=$(find "$DRIVERS_DIR" -name "chrome-headless-shell*" -type d | head -n 1)
  
  if [[ "$OS" == "win" ]]; then
    CHROME_PATH="$CHROME_HEADLESS_DIR/chrome-headless-shell.exe"
    CHROME_PATH=${CHROME_PATH//\\/\\\\}  # 转义Windows路径
  else
    CHROME_PATH="$CHROME_HEADLESS_DIR/chrome-headless-shell"
  fi
  
  # 创建配置JSON
  cat > $CONFIG_FILE << EOL
{
  "version": "$CHROME_VERSION",
  "os": "$OS",
  "arch": "$ARCH",
  "chrome_path": "$CHROME_PATH",
  "installed_on": "$(date)"
}
EOL
  
  echo -e "${GREEN}配置文件已创建: $CONFIG_FILE${NC}"
}

# 主函数
main() {
  echo -e "${YELLOW}======= chrome-headless-shell 安装脚本 =======${NC}"
  
  detect_os
  set_download_url
  download_chrome
  extract_chrome
  set_permissions
  create_config
  cleanup
  
  echo -e "${GREEN}======= 安装完成! =======${NC}"
  echo -e "chrome-headless-shell 已安装到: $DRIVERS_DIR"
  echo -e "配置信息已保存到: $DRIVERS_DIR/webdriver_config.json"
  echo -e "${YELLOW}要在Python中使用，请确保WebDriver路径已正确配置${NC}"
}

# 运行主函数
main 