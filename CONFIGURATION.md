# 配置系统说明

## 概述

项目配置已经被拆分为多个文件，存放在 `config/` 目录下，以提高可维护性和可读性。这种方式允许不同模块的配置分离，使得管理更加简单。

## 配置文件结构

- `main.yaml` - 主配置文件，用于导入其他配置文件
- `notification.yaml` - 邮件和钉钉通知配置
- `crawler.yaml` - 爬虫基础配置
- `sources.yaml` - 数据源配置
- `ai_analyzer.yaml` - AI分析配置
- `scheduler.yaml` - 定时任务配置
- `webserver.yaml` - Web服务器配置
- `logging.yaml` - 日志配置

## 配置加载方式

系统支持两种配置方式：
1. 将所有配置放在一个 `config.yaml` 文件中（旧方式，仍然支持）
2. 将配置拆分为多个文件放在 `config/` 目录下（推荐方式）

配置加载优先级：
1. 命令行参数指定的配置文件或目录
2. 项目根目录下的 `config/` 目录
3. 项目根目录下的 `config.yaml` 文件
4. 默认配置

## 配置导入机制

当配置从 `config/` 目录加载时，系统会首先查找 `main.yaml` 文件。如果该文件存在，系统会按照其中 `imports` 字段指定的顺序导入其他配置文件。例如：

```yaml
# main.yaml
imports:
  - notification.yaml
  - crawler.yaml
  - sources.yaml
  - ai_analyzer.yaml
  - scheduler.yaml
  - webserver.yaml
  - logging.yaml
```

如果 `config/` 目录中不存在 `main.yaml` 文件，系统会按字母顺序加载目录中的所有 `.yaml` 和 `.yml` 文件。

## 敏感信息处理

敏感信息（如API密钥、密码等）应放在 `config.secret.yaml` 文件中，该文件不应提交到版本控制系统。系统会自动加载这个文件，并将其配置与其他配置合并。

## 配置加载接口

项目提供了一个统一的配置加载接口，位于 `src/utils/config_loader.py`。所有需要加载配置的代码都应该使用这个接口：

```python
from src.utils.config_loader import get_config

# 加载配置
config = get_config()

# 如果需要指定配置路径
config = get_config(config_path='/path/to/config')

# 如果需要指定默认配置
default_config = {'some_key': 'default_value'}
config = get_config(default_config=default_config)
```

## 配置合并逻辑

配置合并遵循以下规则：
1. 如果键在两个配置中都存在，且两个值都是字典，则递归合并这两个字典
2. 如果键在两个配置中都存在，但至少一个值不是字典，则后导入的配置会覆盖先导入的配置
3. 如果键只在一个配置中存在，则保留该键值对

## 命令行参数

用户可以通过命令行参数 `--config` 指定配置文件或目录路径：

```bash
# 指定单个配置文件
python -m src.main --config custom_config.yaml

# 指定配置目录
python -m src.main --config custom_config_dir/
```

## 切换到新配置系统

项目包含一个脚本 `scripts/config_backup.py`，用于创建当前配置的备份，并测试新配置系统是否正常工作。运行该脚本可以验证配置迁移是否成功：

```bash
python scripts/config_backup.py
``` 