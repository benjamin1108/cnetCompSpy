# SQLite备份功能使用说明

## 概述

SQLite备份功能为项目提供了一种数据备份机制，将文件系统中的数据（爬虫源文件、分析文件和元数据）备份到SQLite数据库中。这个功能**不改变**现有的从文件系统读写数据的逻辑，仅作为数据的存储备份。

## 功能特性

- 自动将爬虫元数据和分析元数据备份到SQLite数据库
- **完整备份爬虫源文件和分析文件内容**，支持内容恢复和搜索
- 提供查询工具，方便查询和导出备份数据
- 支持定时备份，可配置备份频率
- 记录备份历史，便于追踪备份状态

## 目录结构

```
scripts/
├── sqlite_backup.py     # SQLite备份脚本
├── sqlite_query.py      # SQLite查询工具
└── sqlite_backup.sh     # 定时备份Shell脚本
```

## 配置说明

在项目的配置文件`config.secret.yaml`中，添加以下配置：

```yaml
# SQLite数据库配置
sqlite:
  db_path: "data/sqlite/cnet_comp_spy.db"  # SQLite数据库文件路径
  backup_frequency: "daily"  # 备份频率: daily, weekly, monthly
  backup_retention_days: 30  # 备份保留天数
```

## 使用方法

### 手动备份

手动运行备份脚本：

```bash
python scripts/sqlite_backup.py
```

### 定时备份

设置定时任务，定期运行备份脚本：

```bash
# 使用crontab设置每天凌晨2点运行备份
$ crontab -e
0 2 * * * /bin/bash /path/to/your/project/scripts/sqlite_backup.sh
```

### 查询备份数据

SQLite查询工具提供了多种查询命令：

1. 查看备份历史：

```bash
python scripts/sqlite_query.py history
```

2. 查看原始数据统计：

```bash
python scripts/sqlite_query.py raw_stats
```

3. 查看分析数据统计：

```bash
python scripts/sqlite_query.py analysis_stats
```

4. 根据标题搜索：

```bash
python scripts/sqlite_query.py search "关键词"
```

5. 查看某个文件的任务情况：

```bash
python scripts/sqlite_query.py tasks "文件路径"
```

6. 查看分析文件内容：

```bash
python scripts/sqlite_query.py content "文件路径"
```

7. 导出分析文件内容到文件：

```bash
python scripts/sqlite_query.py content "文件路径" --output "输出文件路径"
```

8. 在分析文件内容中搜索关键词：

```bash
python scripts/sqlite_query.py search_content "关键词"
```

9. 自定义SQL查询：

```bash
python scripts/sqlite_query.py query "SELECT * FROM raw_data LIMIT 10"
```

10. 导出查询结果到CSV：

```bash
python scripts/sqlite_query.py query "SELECT * FROM raw_data" --output data/export.csv
```

## 数据库表结构

SQLite数据库包含以下表：

1. `raw_data` - 存储原始爬虫数据和内容
2. `analysis_data` - 存储分析数据和分析文件内容
3. `analysis_tasks` - 存储分析任务
4. `raw_info` - 存储原始数据信息
5. `backup_history` - 存储备份历史

### 更新：分析文件内容备份

从版本1.1开始，本工具支持完整备份分析文件内容。这意味着：

- `analysis_data`表新增了`content`字段，存储完整的分析文件内容
- 您可以通过`content`命令查看或导出分析文件内容
- 可以使用`search_content`命令在所有分析文件内容中搜索关键词
- 在数据库损坏或文件丢失的情况下，可以从备份中恢复完整的分析文件内容

这一功能使数据备份更加完整可靠，为灾难恢复提供了更全面的支持。

## 注意事项

- 备份过程不会更改现有的数据读写逻辑
- 备份脚本会自动创建所需的数据库和表结构
- 首次运行可能需要较长时间，因为需要备份所有历史数据
- 后续运行会自动跳过已备份的数据，只备份新增或更新的数据
- 备份日志存储在`logs/sqlite_backup_YYYYMMDD.log`文件中
- 完整备份分析文件内容可能会显著增加数据库大小，请确保有足够的磁盘空间

## 依赖项

SQLite备份功能依赖以下Python包：

- sqlite3 (Python标准库)
- pandas (用于导出CSV)
- tabulate (用于格式化表格输出)

可以通过以下命令安装所需依赖：

```bash
pip install pandas tabulate
``` 