#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import platform
import subprocess
import zipfile
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
import urllib.request

def detect_os():
    """检测操作系统和架构"""
    print("检测操作系统...")
    
    # 操作系统
    system = platform.system()
    if system == "Linux":
        os_name = "linux"
    elif system == "Darwin":
        os_name = "mac"
    elif system == "Windows":
        os_name = "win"
    else:
        os_name = "unknown"
    
    # 架构
    machine = platform.machine()
    if machine == "x86_64" or machine == "AMD64":
        arch = "x64"
    elif machine == "arm64" or machine == "aarch64":
        arch = "arm64"
    else:
        arch = machine
    
    # 平台名称映射
    if os_name == "mac" and arch == "arm64":
        platform_name = "mac-arm64"
    elif os_name == "mac" and arch == "x64":
        platform_name = "mac-x64"
    elif os_name == "linux" and arch == "x64":
        platform_name = "linux64"
    elif os_name == "win" and arch == "x64":
        platform_name = "win64"
    else:
        raise ValueError(f"不支持的操作系统/架构组合: {os_name}/{arch}")
    
    print(f"检测到系统: {os_name} ({arch})")
    
    return os_name, arch, platform_name

def get_latest_version():
    """获取最新Chrome版本"""
    print("获取最新Chrome版本信息...")
    
    version_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json"
    
    try:
        with urllib.request.urlopen(version_url) as response:
            version_json = json.loads(response.read().decode())
        
        chrome_version = version_json["channels"]["Stable"]["version"]
        
        if not chrome_version:
            raise ValueError("无法获取Chrome版本信息")
        
        print(f"找到最新稳定版本: {chrome_version}")
        return chrome_version
    except Exception as e:
        print(f"获取Chrome版本失败: {e}")
        raise

def download_file(url, dest_path, description):
    """下载文件"""
    print(f"下载{description}: {url}")
    
    try:
        with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        
        print("下载完成")
        return True
    except Exception as e:
        print(f"下载{description}失败: {e}")
        return False

def check_dependencies(os_name):
    """检查系统依赖"""
    print("检查系统依赖...")
    
    if os_name == "linux":
        # 提供Chrome运行所需的完整依赖库列表
        print("Chrome headless shell 在Linux系统上需要以下依赖库:")
        print("=======================================")
        dependencies = [
            "libatk-1.0-0           # ATK库",
            "libatk-bridge-2.0-0    # ATK桥接库",
            "libasound2             # ALSA音频库",
            "libcups2               # CUPS打印系统",
            "libdrm2                # Direct Rendering Manager",
            "libgtk-3-0             # GTK+3",
            "libgbm1                # Mesa GBM库",
            "libnss3                # NSS安全库",
            "libxcomposite1         # X Composite扩展",
            "libxdamage1            # X Damage扩展",
            "libxfixes3             # X Fixes扩展",
            "libxrandr2             # X Resize, Rotate and Reflection扩展",
            "libxshmfence1          # X shared memory fences",
            "libpango-1.0-0         # Pango文本布局库",
            "libpangocairo-1.0-0    # Pango Cairo渲染",
            "libcairo2              # Cairo绘图库",
            "libatspi2.0-0          # AT-SPI库",
            "libxkbcommon0          # XKB库",
            "libxss1                # XScreenSaver扩展库",
            "libxtst6               # X Test扩展库",
            "libexpat1              # Expat XML解析库",
            "libfontconfig1         # 字体配置库",
            "libxi6                 # X11 Input扩展库",
            "libx11-6               # X11客户端库",
            "libxcursor1            # X光标管理库",
            "libxext6               # X11扩展库",
            "libxrender1            # X Rendering扩展",
            "libglib2.0-0           # GLib库",
            "libnspr4               # Netscape可移植运行时",
            "libu2f-udev            # U2F设备支持",
            "libvulkan1             # Vulkan加载器",
            "libdbus-1-3            # D-Bus IPC系统",
            "libwayland-client0     # Wayland客户端库",
            "libwayland-egl1        # Wayland EGL库",
            "libwayland-cursor0     # Wayland光标库"
        ]
        
        for dep in dependencies:
            print(f"- {dep}")
        
        print("=======================================")
        
        # 根据不同发行版提供安装命令
        if os.path.exists("/etc/debian_version"):
            # Debian/Ubuntu系
            print("在Debian/Ubuntu系统上，请尝试运行以下命令安装依赖:")
            print("sudo apt-get update")
            print("sudo apt-get install -y libatk1.0-0 libatk-bridge2.0-0 libasound2 libcups2 libdrm2 libgtk-3-0 libgbm1 libnss3 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libxshmfence1 libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libatspi2.0-0 libxkbcommon0 libxss1 libxtst6 libexpat1 libfontconfig1 libxi6 libx11-6 libxcursor1 libxext6 libxrender1 libglib2.0-0 libnspr4 libu2f-udev libvulkan1 libdbus-1-3 libwayland-client0 libwayland-egl1 libwayland-cursor0")
        elif os.path.exists("/etc/redhat-release"):
            # RHEL/CentOS/Fedora系
            print("在RHEL/CentOS/Fedora系统上，请尝试运行以下命令安装依赖:")
            print("sudo yum install -y atk at-spi2-atk alsa-lib cups-libs libdrm gtk3 mesa-libgbm nss libXcomposite libXdamage libXfixes libXrandr libxshmfence pango pango-cairo cairo at-spi2-core libxkbcommon libXScrnSaver libXtst expat fontconfig libXi libX11 libXcursor libXext libXrender glib2 nspr libu2f-host vulkan-loader dbus-libs wayland-libs")
        elif os.path.exists("/etc/arch-release"):
            # Arch系
            print("在Arch系统上，请尝试运行以下命令安装依赖:")
            print("sudo pacman -S --needed atk at-spi2-atk alsa-lib cups libdrm gtk3 libgbm nss libxcomposite libxdamage libxfixes libxrandr libxshmfence pango cairo at-spi2-core libxkbcommon libxss libxtst expat fontconfig libxi libx11 libxcursor libxext libxrender glib2 nspr libu2f-host vulkan-icd-loader dbus wayland")
        else:
            print("请使用系统的包管理器安装上述列出的库")
        
        # 试运行--no-sandbox模式作为备选方案
        print("作为临时解决方案，您也可以尝试使用--no-sandbox模式:")
        print("在src/crawlers/common/base_crawler.py文件中找到_init_driver函数，确保chrome_options中包含'--no-sandbox'参数")
    elif os_name == "mac":
        print("在macOS上，大多数依赖由操作系统提供，但您可能需要确保XQuartz已安装（用于X11支持）")
        print("您可以通过Homebrew安装XQuartz:")
        print("brew install --cask xquartz")
    elif os_name == "win":
        print("在Windows上，大多数依赖已包含在安装包中")
        print("请确保已安装Visual C++ Redistributable包")

def download_chrome_headless_shell(chrome_version, platform_name, drivers_dir):
    """下载chrome-headless-shell"""
    print("下载chrome-headless-shell...")
    
    download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/{platform_name}/chrome-headless-shell-{platform_name}.zip"
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_file = os.path.join(temp_dir, "chrome-headless-shell.zip")
        
        # 下载文件
        if not download_file(download_url, zip_file, "chrome-headless-shell"):
            return None
        
        # 解压文件
        print("解压chrome-headless-shell...")
        chrome_headless_dir = os.path.join(drivers_dir, f"chrome-headless-shell-{platform_name}")
        
        # 如果目录已存在，先删除
        if os.path.exists(chrome_headless_dir):
            shutil.rmtree(chrome_headless_dir)
        
        # 解压
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(drivers_dir)
            
            # 如果需要重命名目录
            for dir_name in os.listdir(drivers_dir):
                dir_path = os.path.join(drivers_dir, dir_name)
                if os.path.isdir(dir_path) and dir_name.startswith("chrome-headless-shell-") and dir_path != chrome_headless_dir:
                    shutil.move(dir_path, chrome_headless_dir)
            
            print(f"chrome-headless-shell已解压到: {chrome_headless_dir}")
            
            # 设置可执行权限
            chrome_bin = os.path.join(chrome_headless_dir, "chrome-headless-shell")
            if platform_name.startswith("win"):
                chrome_bin += ".exe"
            
            if os.path.exists(chrome_bin) and not platform_name.startswith("win"):
                os.chmod(chrome_bin, 0o755)
                print("已设置执行权限")
            
            return chrome_bin
        except Exception as e:
            print(f"解压chrome-headless-shell失败: {e}")
            return None

def download_chromedriver(chrome_version, platform_name, drivers_dir):
    """下载ChromeDriver"""
    print("下载ChromeDriver...")
    
    download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/{platform_name}/chromedriver-{platform_name}.zip"
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_file = os.path.join(temp_dir, "chromedriver.zip")
        
        # 下载文件
        if not download_file(download_url, zip_file, "ChromeDriver"):
            return None
        
        # 解压文件
        print("解压ChromeDriver...")
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 解压后的文件在子目录中
            chromedriver_subdir = f"chromedriver-{platform_name}"
            chromedriver_src = os.path.join(temp_dir, chromedriver_subdir, "chromedriver")
            if platform_name.startswith("win"):
                chromedriver_src += ".exe"
            
            # 将chromedriver复制到drivers目录
            chromedriver_dest = os.path.join(drivers_dir, "chromedriver")
            if platform_name.startswith("win"):
                chromedriver_dest += ".exe"
            
            # 如果目标文件已存在，先删除
            if os.path.exists(chromedriver_dest):
                os.remove(chromedriver_dest)
            
            shutil.copy2(chromedriver_src, chromedriver_dest)
            print(f"ChromeDriver已复制到: {chromedriver_dest}")
            
            # 设置可执行权限
            if os.path.exists(chromedriver_dest) and not platform_name.startswith("win"):
                os.chmod(chromedriver_dest, 0o755)
                print("已设置执行权限")
            
            return chromedriver_dest
        except Exception as e:
            print(f"解压ChromeDriver失败: {e}")
            return None

def create_config_file(chrome_version, os_name, arch, chrome_bin, chromedriver_path, drivers_dir):
    """创建配置文件"""
    print("创建配置文件...")
    
    config_file = os.path.join(drivers_dir, "webdriver_config.json")
    
    # 生成配置文件内容
    config_content = {
        "version": chrome_version,
        "os": os_name,
        "arch": arch,
        "chrome_path": chrome_bin,
        "chromedriver_path": chromedriver_path,
        "installed_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 写入配置文件
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_content, f, ensure_ascii=False, indent=2)
    
    print(f"配置文件已创建: {config_file}")
    return config_file

def setup_driver(args=None):
    """设置WebDriver"""
    print("======= 驱动程序设置脚本 =======")
    print("该脚本将下载最新版本的chrome-headless-shell和ChromeDriver")
    
    # 获取项目根目录
    project_root = Path(__file__).resolve().parent.parent.parent
    drivers_dir = project_root / "drivers"
    
    # 确保驱动目录存在
    os.makedirs(drivers_dir, exist_ok=True)
    
    try:
        # 检测操作系统
        os_name, arch, platform_name = detect_os()
        
        # 获取最新Chrome版本
        chrome_version = get_latest_version()
        
        # 下载chrome-headless-shell
        chrome_bin = download_chrome_headless_shell(chrome_version, platform_name, drivers_dir)
        if not chrome_bin:
            print("chrome-headless-shell下载失败")
            return 1
        
        # 下载ChromeDriver
        chromedriver_path = download_chromedriver(chrome_version, platform_name, drivers_dir)
        if not chromedriver_path:
            print("ChromeDriver下载失败")
            return 1
        
        # 创建配置文件
        config_file = create_config_file(chrome_version, os_name, arch, chrome_bin, chromedriver_path, drivers_dir)
        
        # 检查系统依赖
        check_dependencies(os_name)
        
        print("======= 安装完成! =======")
        print(f"chrome-headless-shell版本: {chrome_version}")
        print(f"ChromeDriver版本: {chrome_version}")
        print(f"chrome-headless-shell路径: {chrome_bin}")
        print(f"ChromeDriver路径: {chromedriver_path}")
        print(f"配置信息已保存到: {config_file}")
        
        return 0
    except Exception as e:
        print(f"设置WebDriver失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(setup_driver())
