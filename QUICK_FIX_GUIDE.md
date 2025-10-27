# 快速修复指南

## 🚀 立即执行（3步解决问题）

### 步骤1: 安装系统依赖
```bash
bash scripts/setup_chrome_dependencies.sh
```

### 步骤2: 清理可能的残留（可选）
```bash
# 清理临时Chrome配置文件
rm -rf /tmp/chrome_profile_*

# 杀死可能卡住的Chrome进程
pkill -f chrome
```

### 步骤3: 重新运行程序
```bash
bash run.sh
```

---

## ✅ 已修复的问题

1. **WebDriver用户数据目录冲突** - 每个实例现在使用独立的临时目录
2. **AWS URL格式错误** - 自动添加缺失的斜杠
3. **提供依赖安装脚本** - 自动检测并安装缺失的系统库

---

## 🔍 验证修复是否成功

运行后检查日志，应该看到：
```
✓ 没有 "user data directory is already in use" 错误
✓ 没有 "aws.amazon.comabout-aws" 这样的URL错误
✓ WebDriver成功初始化
```

---

## ⚠️ 如果仍有问题

### 问题: 仍然提示缺少依赖库

**解决**:
```bash
# 手动检查缺少的库
ldd drivers/chrome-headless-shell-linux64/chrome-headless-shell | grep "not found"

# Ubuntu/Debian系统
sudo apt-get install -y libatk-bridge2.0-0 libgtk-3-0 libnss3

# CentOS/RHEL系统
sudo yum install -y at-spi2-atk gtk3 nss
```

### 问题: Chrome进程卡住

**解决**:
```bash
# 查看Chrome进程
ps aux | grep chrome

# 强制杀死所有Chrome进程
pkill -9 -f chrome

# 清理临时文件
rm -rf /tmp/chrome_profile_*
```

### 问题: 内存不足

**解决**: 在`config/crawler.yaml`中减少并发数量

---

## 📚 详细文档

- 完整修复说明: `FIXES_APPLIED.md`
- 问题排查指南: `docs/webdriver_troubleshooting.md`
