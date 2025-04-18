# 每日爬取与分析自动化脚本

这个文档提供了关于`scripts/daily_crawl_and_analyze.sh`脚本的使用说明，该脚本用于自动化运行爬虫功能，并在爬虫完成后调用分析功能。

## 功能概述

`daily_crawl_and_analyze.sh`脚本提供以下功能：

1. 自动激活Python虚拟环境
2. 运行爬虫功能收集数据
3. 检查爬虫是否成功完成
4. 如果爬虫成功，则运行分析功能
5. 记录执行过程和结果到日志文件
6. 支持通知功能（需要自行配置）

## 使用方法

### 手动运行

您可以通过以下命令手动运行脚本：

```bash
./scripts/daily_crawl_and_analyze.sh
```

脚本支持传递参数，这些参数将被传递给爬虫和分析功能。例如：

```bash
# 限制每个来源最多爬取10篇文章
./scripts/daily_crawl_and_analyze.sh --limit 10

# 仅爬取AWS的数据
./scripts/daily_crawl_and_analyze.sh --vendor aws

# 强制执行，忽略本地metadata或文件是否已存在
./scripts/daily_crawl_and_analyze.sh --force

# 限制分析的文件数量为5个
./scripts/daily_crawl_and_analyze.sh --limit 5

# 组合使用多个参数
./scripts/daily_crawl_and_analyze.sh --vendor aws --limit 10 --force
```

注意：`--limit`参数同时适用于爬虫和分析功能。在爬虫阶段，它限制每个来源最多爬取的文章数量；在分析阶段，它限制要分析的文件总数。

### 日志文件

脚本会在`logs`目录下生成日志文件，文件名格式为`daily_crawl_analyze_YYYYMMDD_HHMMSS.log`。您可以通过查看这些日志文件来了解脚本的执行情况。

## 设置每日自动运行

要使脚本每日自动运行，您可以使用cron作业。以下是设置cron作业的步骤：

1. 打开终端，输入以下命令编辑cron作业：

```bash
crontab -e
```

2. 添加一行cron作业，指定脚本的运行时间。例如，要在每天凌晨2点运行脚本：

```
0 2 * * * /完整路径/scripts/daily_crawl_and_analyze.sh >> /完整路径/logs/cron.log 2>&1
```

请将`/完整路径/`替换为脚本的实际路径。

3. 保存并关闭编辑器。

### cron作业示例

以下是一些常用的cron作业示例：

- 每天凌晨2点运行：
```
0 2 * * * /完整路径/scripts/daily_crawl_and_analyze.sh
```

- 每周一凌晨3点运行：
```
0 3 * * 1 /完整路径/scripts/daily_crawl_and_analyze.sh
```

- 每小时运行一次：
```
0 * * * * /完整路径/scripts/daily_crawl_and_analyze.sh
```

## 通知功能

脚本现在集成了一个强大的邮件通知系统，可以在任务完成、失败或部分完成时发送详细的HTML格式邮件通知。

### 配置邮件通知

邮件通知配置分为两部分：基本配置和敏感配置。

#### 基本配置

在项目根目录下的`config.yaml`文件中，修改`email`部分：

```yaml
# 邮件通知配置
email:
  enabled: true  # 将此值改为true以启用邮件通知
  smtp_server: "smtp.example.com"  # 替换为您的SMTP服务器地址
  smtp_port: 587  # 替换为您的SMTP服务器端口
  use_tls: true  # 是否使用TLS加密
  # 用户名和密码在config.secret.yaml中配置
  sender: "your_email@example.com"  # 替换为发件人地址
  recipients: ["recipient@example.com"]  # 替换为收件人地址，可以是多个
  subject_prefix: "[云计算网络竞争动态分析]"  # 邮件主题前缀
```

#### 敏感配置（用户名和密码）

为了安全起见，邮箱用户名和密码应该存储在单独的敏感配置文件中。请按照以下步骤操作：

1. 复制项目根目录下的`config.secret.yaml.template`文件，并重命名为`config.secret.yaml`：

```bash
cp config.secret.yaml.template config.secret.yaml
```

2. 编辑`config.secret.yaml`文件，填入您的邮箱用户名和密码：

```yaml
# 邮件账户配置
email:
  username: "your_email@example.com"  # 替换为您的邮箱用户名
  password: "your_secure_password_here"  # 替换为您的邮箱密码
```

3. 确保`config.secret.yaml`文件不会被提交到版本控制系统中（该文件已在`.gitignore`中配置）。

### 邮件通知内容

发送的通知邮件包含以下信息：

1. 任务状态（成功、失败或部分成功）
2. 详细消息内容
3. 执行时间
4. 主机名和IP地址
5. 日志文件内容（最后100行）

### 常见邮件服务器配置示例

以下是一些常见邮件服务器的配置示例：

#### Gmail

在`config.yaml`中：
```yaml
email:
  enabled: true
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  use_tls: true
  sender: "your_gmail@gmail.com"
  recipients: ["recipient@example.com"]
```

在`config.secret.yaml`中：
```yaml
email:
  username: "your_gmail@gmail.com"
  password: "your_app_password"  # 需要使用应用专用密码
```

注意：Gmail需要使用应用专用密码，而不是您的Gmail账户密码。您可以在Google账户的安全设置中生成应用专用密码。

#### 腾讯企业邮箱

在`config.yaml`中：
```yaml
email:
  enabled: true
  smtp_server: "smtp.exmail.qq.com"
  smtp_port: 465
  use_tls: true
  sender: "your_name@your_company.com"
  recipients: ["recipient@example.com"]
```

在`config.secret.yaml`中：
```yaml
email:
  username: "your_name@your_company.com"
  password: "your_password"
```

#### 阿里云企业邮箱

在`config.yaml`中：
```yaml
email:
  enabled: true
  smtp_server: "smtp.qiye.aliyun.com"
  smtp_port: 465
  use_tls: true
  sender: "your_name@your_company.com"
  recipients: ["recipient@example.com"]
```

在`config.secret.yaml`中：
```yaml
email:
  username: "your_name@your_company.com"
  password: "your_password"
```

### 禁用邮件通知

如果您不需要邮件通知，只需将`config.yaml`文件中的`email.enabled`设置为`false`即可。

## 故障排除

如果脚本运行失败，请检查以下几点：

1. 确保脚本具有执行权限：
```bash
chmod +x scripts/daily_crawl_and_analyze.sh
```

2. 确保Python虚拟环境已正确设置：
```bash
./scripts/run.sh setup
```

3. 检查日志文件以获取详细的错误信息。

4. 如果使用cron作业，确保在cron环境中提供了所有必要的环境变量。

## 自定义

您可以根据需要自定义脚本：

1. 修改日志文件的位置和格式
2. 配置通知方式（电子邮件、短信等）
3. 添加更多的错误处理和重试逻辑
4. 调整爬虫和分析的参数

## 注意事项

- 脚本假设它与项目的其他文件位于正确的目录结构中
- 脚本依赖于项目的虚拟环境和其他脚本
- 如果您的系统使用不同的Python命令（例如`python3`而不是`python`），您可能需要相应地修改脚本
