# WebDriver 问题修复总结

## 修复日期
2025-10-27

## 问题描述

运行爬虫时遇到以下错误：

1. **WebDriver用户数据目录冲突**
   ```
   session not created: probably user data directory is already in use
   ```

2. **缺少系统依赖库**
   ```
   chrome-headless-shell缺少系统依赖库: libatk-bridge-2.0.so.0
   ```

3. **AWS URL格式错误**
   ```
   HTTPSConnectionPool(host='aws.amazon.comabout-aws', port=443)
   ```

## 已应用的修复

### 1. WebDriver用户数据目录冲突 ✅

**文件**: `src/crawlers/common/base_crawler.py`

**修改内容**:
- 为每个WebDriver实例创建唯一的临时用户数据目录
- 在`__init__`方法中添加`self.user_data_dir`属性
- 在`_init_driver`方法中使用`tempfile.mkdtemp()`创建临时目录
- 在`_close_driver`方法中自动清理临时目录

**效果**: 多个爬虫实例可以同时运行，不会再出现用户数据目录冲突

### 2. AWS URL格式错误 ✅

**文件**: `src/crawlers/vendors/aws/whatsnew_crawler.py`

**修改内容**:
- 在构建完整URL时，检查路径是否以`/`开头
- 如果不是，自动添加`/`前缀

**效果**: 修复了URL拼接错误，避免域名和路径连在一起

### 3. 系统依赖库安装脚本 ✅

**新增文件**: `scripts/setup_chrome_dependencies.sh`

**功能**:
- 自动检测操作系统类型（Ubuntu/Debian/CentOS/RHEL）
- 检查缺少的依赖库
- 自动安装所需的系统依赖
- 验证Chrome是否可以正常运行

**使用方法**:
```bash
bash scripts/setup_chrome_dependencies.sh
```

### 4. 问题排查文档 ✅

**新增文件**: `docs/webdriver_troubleshooting.md`

**内容**:
- 详细的问题诊断步骤
- 各操作系统的依赖安装命令
- 快速诊断命令
- 预防措施和最佳实践

## 下一步操作

### 立即执行

1. **安装系统依赖**（如果还没有安装）:
   ```bash
   bash scripts/setup_chrome_dependencies.sh
   ```

2. **验证修复**:
   ```bash
   # 重新运行爬虫程序
   bash run.sh
   ```

### 可选操作

1. **清理残留的临时目录**（如果之前有异常退出）:
   ```bash
   rm -rf /tmp/chrome_profile_*
   ```

2. **检查Chrome进程**:
   ```bash
   ps aux | grep chrome
   ```

3. **查看日志**:
   ```bash
   tail -f logs/app.log
   ```

## 预期结果

修复后，应该不再出现以下错误：
- ✅ WebDriver用户数据目录冲突
- ✅ AWS URL格式错误
- ⚠️ 系统依赖库缺失（需要运行安装脚本）

## 注意事项

1. **系统依赖**: 必须先安装系统依赖库，否则Chrome无法运行
2. **权限**: 安装脚本需要sudo权限
3. **并发**: 虽然修复了用户数据目录冲突，但仍需注意系统资源（内存、CPU）
4. **日志监控**: 建议定期检查日志，及时发现新问题

## 相关文件

- `src/crawlers/common/base_crawler.py` - WebDriver初始化逻辑
- `src/crawlers/vendors/aws/whatsnew_crawler.py` - AWS爬虫URL构建
- `scripts/setup_chrome_dependencies.sh` - 依赖安装脚本
- `docs/webdriver_troubleshooting.md` - 问题排查文档
