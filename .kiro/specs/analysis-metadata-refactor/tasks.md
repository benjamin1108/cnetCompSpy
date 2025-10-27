# 实施计划

- [x] 1. 修改AnalysisExecutionStage以支持新格式metadata写入
  - 在`src/ai_analyzer/pipeline/stages/analysis_execution_stage.py`中添加`_write_metadata_header`方法
  - 修改`_process_single_file`方法，在打开输出文件后首先调用`_write_metadata_header`写入metadata块
  - 确保metadata块包含：发布时间、厂商、类型、原始链接四个字段
  - 在metadata块后添加水平分隔线`---`
  - 保持AI_TASK标记的写入逻辑不变
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 2. 开发metadata迁移脚本
- [x] 2.1 创建migrate_analysis_metadata.py脚本文件
  - 在`scripts/`目录下创建新文件`migrate_analysis_metadata.py`
  - 实现`AnalysisMetadataMigrator`类，包含初始化、metadata提取、文件迁移等方法
  - 实现`extract_metadata_from_content`方法，从AI全文翻译块或文件头部提取metadata
  - 实现`check_if_needs_migration`方法，判断文件是否需要迁移
  - 实现`migrate_file`方法，执行单个文件的迁移操作
  - 实现`migrate_all`方法，批量迁移所有分析文件
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [x] 2.2 实现迁移脚本的备份和统计功能
  - 在迁移前创建.bak备份文件
  - 记录迁移统计信息（总数、成功、失败、跳过）
  - 实现dry-run模式，支持预览迁移操作
  - 添加详细的日志输出，记录每个文件的处理状态
  - _Requirements: 6.7, 6.8, 6.9_

- [x] 2.3 实现迁移脚本的错误处理
  - 捕获单个文件迁移失败的异常
  - 记录错误信息到日志
  - 确保单个文件失败不影响其他文件的迁移
  - 在迁移结束时输出失败文件列表
  - _Requirements: 6.10, 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 3. 执行迁移操作
- [x] 3.1 在测试环境验证迁移脚本
  - 准备测试用的旧格式分析文件
  - 运行迁移脚本的dry-run模式
  - 验证识别需要迁移的文件是否正确
  - 执行实际迁移并验证结果
  - _Requirements: 6.1, 6.9_

- [x] 3.2 备份生产环境数据
  - 创建data/analysis目录的完整备份
  - 验证备份文件的完整性
  - 记录备份位置和时间
  - _Requirements: 6.7_

- [x] 3.3 在生产环境执行迁移
  - 运行迁移脚本的dry-run模式预检
  - 执行实际迁移操作
  - 监控迁移过程，记录统计信息
  - 验证迁移后的文件格式正确性
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.8_

- [ ] 4. 简化DocumentManager的metadata提取逻辑
- [x] 4.1 重写_extract_document_meta方法
  - 修改`src/web_server/document_manager.py`中的`_extract_document_meta`方法
  - 只读取文件前20行而不是16KB
  - 使用简化的正则表达式从文件头部提取metadata
  - 支持提取：发布时间、厂商、类型、原始链接字段
  - 正确处理中英文冒号和星号格式
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 4.2 删除DocumentManager中的旧格式处理代码
  - 删除从AI_TASK标记中提取metadata的逻辑
  - 删除复杂的日期格式匹配代码（华为月度格式等）
  - 删除从文件名提取日期的回退逻辑
  - 删除`_extract_translated_title`方法中从AI_TASK提取metadata的部分
  - 简化错误处理，metadata提取失败时返回空值
  - _Requirements: 3.5, 4.3, 4.4_

- [ ] 5. 简化rebuild_metadata.py的metadata提取逻辑
- [x] 5.1 创建extract_metadata_from_analysis_file函数
  - 在`src/utils/rebuild_metadata.py`中添加新函数`extract_metadata_from_analysis_file`
  - 从分析文件头部（前20行）提取metadata
  - 使用简化的正则表达式匹配metadata字段
  - 返回包含publish_date、vendor、type、original_url的字典
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 5.2 删除rebuild_metadata.py中的旧格式处理代码
  - 删除从AI全文翻译块提取发布日期的代码（约30行）
  - 删除从原始文件提取发布日期的回退逻辑（约40行）
  - 简化metadata组装逻辑，直接使用新函数的返回值
  - 保留从AI标题翻译块提取中文标题的逻辑（这是必要的）
  - 更新相关的日志输出
  - _Requirements: 4.3, 4.4_

- [x] 6. 更新analysis_metadata.json的写入逻辑
  - 确保AnalysisExecutionStage在写入文件的同时更新analysis_metadata.json
  - 验证metadata字段与文件头部保持一致
  - 确保使用MetadataManager的线程安全机制
  - 验证中文标题和update_type字段正确保存
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 7. 验证和测试
- [x] 7.1 验证新生成的分析文件格式
  - 运行AI分析生成新的分析文件
  - 检查文件头部metadata格式是否正确
  - 验证metadata字段完整性
  - 验证AI_TASK标记位置正确
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4_

- [x] 7.2 验证Web界面展示
  - 通过Web界面访问迁移后的分析文件
  - 验证metadata正确展示
  - 验证中文标题正确显示
  - 验证日期格式正确
  - _Requirements: 4.1, 4.2_

- [x] 7.3 验证rebuild_metadata.py功能
  - 运行rebuild_metadata.py脚本
  - 验证能够正确提取metadata
  - 验证analysis_metadata.json更新正确
  - 验证统计信息准确
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 7.4 性能测试
  - 测试DocumentManager的metadata提取性能
  - 对比重构前后的提取时间
  - 验证性能提升达到预期（50%以上）
  - _Requirements: 3.1, 4.4_

- [x] 8. 文档更新和代码清理
  - 更新相关代码注释
  - 更新README或开发文档，说明新的metadata格式
  - 删除所有标记为"旧格式处理"的注释
  - 运行代码格式化工具
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
