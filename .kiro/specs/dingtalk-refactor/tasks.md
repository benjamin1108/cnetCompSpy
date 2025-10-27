# 实施计划

- [x] 1. 重构 report_generator 模块
  - 将 scripts/generate_weekly_report.py 移动并重命名为 src/utils/report_generator.py
  - 创建 ReportGenerator 类以封装报告生成逻辑
  - 实现 generate_weekly_report() 函数用于周报生成
  - 实现 generate_recent_report() 函数用于最近 N 天报告生成
  - 更新 CLI 参数解析以支持 --mode weekly 和 --mode recent --days N
  - _需求: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1_

- [x] 2. 重构 dingtalk.py 模块
- [x] 2.1 移除过时的推送方法
  - 删除 send_weekly_updates() 方法及其所有代码
  - 删除 send_daily_updates() 方法及其所有代码
  - 删除 send_recently_updates() 方法及其所有代码
  - 删除 _format_update_item() 辅助方法（如果仅被已删除方法使用）
  - _需求: 1.1, 1.2, 1.3_

- [x] 2.2 重命名和简化保留的方法
  - 将 send_markdown_file() 方法重命名为 send_report_file()
  - 更新方法文档字符串以反映其用于发送报告文件
  - 确保方法保持对 --robot 和 --config 选项的支持
  - _需求: 4.2, 6.1, 6.2, 6.3, 6.4_

- [x] 2.3 更新 CLI 参数解析
  - 从 argparse 中移除 'weekly' 子命令
  - 从 argparse 中移除 'daily' 子命令
  - 从 argparse 中移除 'recent' 子命令
  - 保留 'pushfile' 子命令
  - 更新帮助文本以仅显示 pushfile 子命令
  - _需求: 1.4, 5.2_

- [x] 3. 更新 run.sh 脚本
- [x] 3.1 重构 run_dingpush 函数
  - 移除对 'weekly' 子命令的处理
  - 移除对 'daily' 子命令的处理
  - 将 'recent' 子命令重命名为 'recent-report'
  - 将 'weekly_report' 子命令重命名为 'weekly-report'（使用连字符）
  - 实现 'recent-report' 子命令：调用 report_generator 然后 pushfile
  - 实现 'weekly-report' 子命令：调用 report_generator 然后 pushfile
  - 保留 'pushfile' 子命令的直接传递
  - 添加参数验证以确保 recent-report 需要 days 参数
  - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 4.3_

- [x] 3.2 更新 validate_args 函数中的 dingpush 验证
  - 更新有效子命令列表为: weekly-report, recent-report, pushfile
  - 为 recent-report 添加 days 参数验证
  - 移除对旧子命令（weekly, daily, recent）的验证逻辑
  - _需求: 1.4, 2.5_

- [x] 3.3 更新 show_help 函数
  - 更新 dingpush 命令的帮助文本
  - 列出新的子命令: weekly-report, recent-report, pushfile
  - 为 recent-report 添加清晰的 days 参数说明
  - 添加使用示例展示新命令
  - 移除所有对 weekly 和 daily 子命令的引用
  - _需求: 5.1, 5.3, 5.4, 5.5_

- [x] 3.4 更新 dingpush 命令的帮助显示逻辑
  - 修改当用户运行 "./run.sh dingpush --help" 时的输出
  - 确保显示 dingtalk.py 的帮助（仅 pushfile）
  - 添加额外提示说明 run.sh 封装的 weekly-report 和 recent-report 命令
  - _需求: 5.2_

- [x] 4. 更新配置文件和文档
- [x] 4.1 更新 config/reporting.yaml
  - 添加 report_generator 配置节
  - 添加 weekly_prompt_key 和 recent_prompt_key 配置
  - 添加 output_paths 配置（weekly_filename_pattern, recent_filename_pattern）
  - 添加 recent_title_prefix 和 recent_intro_text 到 beautification 配置
  - _需求: 4.4_

- [x] 4.2 更新 README 或相关文档
  - 记录新的 dingpush 命令用法
  - 提供 weekly-report 和 recent-report 的示例
  - 说明从旧命令的迁移路径
  - 标记旧命令为已弃用
  - _需求: 5.1, 5.3_

- [x] 5. 测试和验证
- [x] 5.1 测试 report_generator 模块
  - 测试 weekly 模式生成报告
  - 测试 recent 模式生成报告（不同天数）
  - 验证生成的报告格式正确
  - 验证 URL 替换功能正常
  - 验证日期范围计算正确
  - _需求: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5.2 测试 dingtalk.py 模块
  - 验证 send_report_file() 方法工作正常
  - 测试 pushfile 命令的 CLI 接口
  - 验证 --robot 和 --config 选项功能
  - 确认旧方法已完全移除
  - _需求: 1.1, 1.2, 1.3, 6.1, 6.2, 6.3, 6.4_

- [x] 5.3 测试 run.sh 脚本
  - 测试 "./run.sh dingpush weekly-report" 命令
  - 测试 "./run.sh dingpush recent-report 7" 命令
  - 测试 "./run.sh dingpush pushfile --filepath <path>" 命令
  - 验证错误处理（缺少参数、无效参数等）
  - 测试 "./run.sh dingpush --help" 显示正确帮助
  - 测试 "./run.sh help" 显示更新的 dingpush 文档
  - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 5.4 端到端集成测试
  - 生成周报并推送到测试钉钉机器人
  - 生成最近 7 天报告并推送到测试钉钉机器人
  - 验证钉钉中收到的消息格式正确
  - 验证内部链接可点击且正确
  - _需求: 2.1, 2.2, 2.3, 2.4_

- [x] 6. 清理和最终检查
- [x] 6.1 删除旧文件和代码
  - 删除 scripts/generate_weekly_report.py（已移动到 src/utils/report_generator.py）
  - 搜索并移除代码中对已删除方法的任何引用
  - 移除未使用的导入和辅助函数
  - _需求: 1.1, 1.2, 1.3, 4.1_

- [x] 6.2 代码审查和重构
  - 审查所有修改的文件确保代码质量
  - 确保命名一致性（方法名、变量名、配置键）
  - 添加或更新必要的代码注释
  - 确保错误消息清晰且有帮助
  - _需求: 4.2, 4.3, 4.4_

- [x] 6.3 最终验证
  - 运行所有测试确保无回归
  - 验证所有帮助文本准确且完整
  - 确认所有需求都已满足
  - 检查是否有遗漏的旧代码引用
  - _需求: 所有需求_
