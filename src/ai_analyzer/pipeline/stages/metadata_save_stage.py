import logging
import os
import json
from typing import Dict, Any

from ..pipeline_stage import PipelineStage
from ..pipeline_context import AnalysisContext

logger = logging.getLogger(__name__)

class MetadataSaveStage(PipelineStage):
    def __init__(self):
        super().__init__(stage_name="MetadataSave")

    def execute(self, context: AnalysisContext) -> AnalysisContext:
        self.logger.info("开始执行元数据保存阶段...")

        if not context.lock_acquired and context.process_lock_manager:
            self.logger.warning("分析进程锁未获取，但仍尝试保存元数据。这可能不安全，如果其他进程可能已修改或正在修改元数据。")
            # Depending on strictness, could skip saving or raise an error.
            # For now, proceed with warning.

        metadata_file_path = context.metadata_file_path
        if not metadata_file_path:
            self.logger.error("元数据文件路径 (metadata_file_path) 未在 context 中配置。无法保存元数据。")
            return context # Cannot save if path is unknown

        if context.metadata is None: # Should be at least {} from AnalysisContext default_factory
            self.logger.warning("Context中的元数据为None，没有内容可保存。")
            return context
        
        if not isinstance(context.metadata, dict):
            self.logger.error(f"Context中的元数据不是一个字典 (类型: {type(context.metadata)})，无法保存为JSON。")
            return context

        # Ensure the directory for the metadata file exists
        try:
            metadata_dir = os.path.dirname(metadata_file_path)
            if metadata_dir: # Avoid trying to create a dir if metadata_file_path is just a filename
                os.makedirs(metadata_dir, exist_ok=True)
                self.logger.debug(f"已确保元数据目录存在: {metadata_dir}")
        except Exception as e:
            self.logger.error(f"创建元数据目录 '{metadata_dir}' 时失败: {e}。可能无法保存元数据。")
            # Depending on severity, could return context here.

        lock_to_use = context.metadata_lock if context.metadata_lock else context.process_lock_manager
        if lock_to_use is None:
            self.logger.warning("没有可用的锁 (metadata_lock 或 process_lock_manager)，元数据保存将不加锁执行。这非常不推荐！")
            try:
                self.logger.info(f"尝试向 '{metadata_file_path}' 保存元数据 (无锁)... 共 {len(context.metadata)} 条记录。")
                with open(metadata_file_path, 'w', encoding='utf-8') as f:
                    json.dump(context.metadata, f, ensure_ascii=False, indent=4)
                self.logger.info(f"元数据已成功保存到 '{metadata_file_path}' (无锁)。")
            except Exception as e:
                self.logger.error(f"保存元数据到 '{metadata_file_path}' (无锁) 时发生错误: {e}", exc_info=True)
        else:
            try:
                with lock_to_use:
                    self.logger.info(f"尝试向 '{metadata_file_path}' 保存元数据 (加锁)... 共 {len(context.metadata)} 条记录。")
                    with open(metadata_file_path, 'w', encoding='utf-8') as f:
                        json.dump(context.metadata, f, ensure_ascii=False, indent=4)
                    self.logger.info(f"元数据已成功保存到 '{metadata_file_path}' (加锁)。")
            except Exception as e:
                self.logger.error(f"保存元数据到 '{metadata_file_path}' (加锁) 时发生错误: {e}", exc_info=True)
                # Depending on policy, could re-raise the exception.

        self.logger.info("元数据保存阶段执行完毕。")
        return context 