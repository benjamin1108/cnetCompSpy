# WebDriver 问题排查指南

## 问题1: 用户数据目录冲突

### 错误信息
```
session not created: probably user data directory is already in use, 
please specify a unique value for --user-data-dir argument, or don't use --user-data-dir
```

### 原因
多个Chrome实例同时运行时尝试使用相同的用户数据目录，导致冲突。

### 解决方案
已在 `src/crawlers/common/base_crawler.py` 中实现：
- 为每个WebDriver实例创建唯一的临时用户数据目录
- 在关闭WebDriver时自动清理临时目录

### 验证
重新运行爬虫程序，该错误应该不再出现。

---

## 问题2: 缺少系统依赖库

### 错误信息
```
chrome-headless-shell缺少系统依赖库: libatk-bridge-2.0.so.0
```

### 原因
系统缺少Chrome运行所需的依赖库。

### 解决方案

#### Ubuntu/Debian系统
```bash
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
    xdg-utils
```

#### CentOS/RHEL系统
```bash
sudo yum install -y \
    at-spi2-atk \
    atk \
    cups-libs \
    dbus-libs \
    libdrm \
    libgbm \
    gtk3 \
    nspr \
    nss \
    libwayland-client \
    libXcomposite \
    libXdamage \
    libXfixes \
    libxkbcommon \
    libXrandr \
    xdg-utils
```

#### 检查缺少的依赖
```bash
# 检查chrome-headless-shell的依赖
ldd drivers/chrome-headless-shell-linux64/chrome-headless-shell | grep "not found"
```

---

## 问题3: URL格式错误

### 错误信息
```
HTTPSConnectionPool(host='aws.amazon.comabout-aws', port=443): Max retries exceeded
```

### 原因
URL拼接错误，缺少斜杠分隔符，导致域名和路径连在一起。

### 检查位置
查看AWS爬虫的URL构建逻辑，确保正确使用 `urljoin()` 或手动添加斜杠。

---

## 快速诊断命令

### 1. 检查Chrome是否可以运行
```bash
drivers/chrome-headless-shell-linux64/chrome-headless-shell --version
```

### 2. 检查缺少的依赖
```bash
ldd drivers/chrome-headless-shell-linux64/chrome-headless-shell | grep "not found"
```

### 3. 清理可能的Chrome进程
```bash
# 查看Chrome进程
ps aux | grep chrome

# 如果需要，杀死所有Chrome进程
pkill -f chrome
```

### 4. 清理临时目录（如果需要）
```bash
# 清理可能残留的临时Chrome配置文件
rm -rf /tmp/chrome_profile_*
```

---

## 预防措施

1. **定期清理临时文件**: 虽然代码会自动清理，但异常退出可能导致残留
2. **监控系统资源**: 多个Chrome实例会消耗大量内存
3. **使用进程池限制**: 限制同时运行的爬虫数量
4. **日志监控**: 定期检查日志中的WebDriver错误

---

## 相关配置

### config/crawler.yaml
```yaml
crawler:
  headless: true  # 使用无头模式
  timeout: 30
  retry: 3
  interval: 2
  page_load_timeout: 45
  script_timeout: 30
  implicit_wait: 10
```

调整这些参数可以改善爬虫的稳定性和性能。
