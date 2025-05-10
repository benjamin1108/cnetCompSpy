import logging
import os
import json
from typing import Dict, Any

from ..pipeline_stage import PipelineStage
from ..pipeline_context import AnalysisContext

logger = logging.getLogger(__name__)

class MetadataLoadStage(PipelineStage):
    def __init__(self):
        super().__init__(stage_name="MetadataLoad")

    def execute(self, context: AnalysisContext) -> AnalysisContext:
        self.logger.info("开始执行元数据加载阶段...")

        # For loading, lock_acquired might not be strictly necessary for the read operation itself,
        # but operations on metadata (even reads that influence later writes) should be consistent.
        # If the pipeline is designed to stop if lock isn't acquired, this check is good.
        if not context.lock_acquired and context.process_lock_manager: # Check if plm exists
            self.logger.warning("分析进程锁未获取。元数据加载将继续（只读），但后续依赖此元数据的写操作可能不安全（如果锁意味着独占）。")
            # If pipeline should halt if lock isn't acquired by GlobalSetupStage, then GlobalSetupStage
            # should have already potentially halted the pipeline or thrown an error.
            # If we reach here, it implies GlobalSetupStage allowed continuation or didn't run/exist.

        metadata_file_path = context.metadata_file_path
        if not metadata_file_path:
            self.logger.error("元数据文件路径 (metadata_file_path) 未在 context 中配置。无法加载元数据。")
            context.metadata = {} # Ensure it's an empty dict if not loadable
            return context

        loaded_metadata: Dict[str, Dict[str, Any]] = {}
        
        if context.metadata_lock is None:
            self.logger.error("元数据锁 (metadata_lock) 未在 AnalysisContext 中初始化。元数据操作可能不安全。")
            # This is a critical setup failure by the orchestrator, should ideally not happen.
            # For safety, we could refuse to load, or proceed with a warning.
            # Let's proceed with a warning, but this indicates an orchestrator setup issue.
            # raise ValueError("Metadata lock not available in context for MetadataLoadStage.")

        lock_to_use = context.metadata_lock if context.metadata_lock else context.process_lock_manager # Fallback, not ideal
        if lock_to_use is None:
            self.logger.warning("没有可用的锁 (metadata_lock 或 process_lock_manager)，元数据加载将不加锁执行。")
            # Execute without lock if none is available
            if os.path.exists(metadata_file_path):
                self.logger.info(f"尝试从 '{metadata_file_path}' 加载元数据 (无锁)... ")
                try:
                    with open(metadata_file_path, 'r', encoding='utf-8') as f:
                        loaded_metadata = json.load(f)
                    if not isinstance(loaded_metadata, dict):
                        self.logger.warning(f"元数据文件 '{metadata_file_path}' 内容不是有效的JSON对象。视为空元数据。")
                        loaded_metadata = {}
                    else:
                        self.logger.info(f"成功加载元数据: {len(loaded_metadata)} 条记录 (无锁)。")
                except json.JSONDecodeError as e:
                    self.logger.error(f"解析元数据文件 '{metadata_file_path}' 时发生JSON解码错误 (无锁): {e}。视为空元数据。")
                    loaded_metadata = {}
                except Exception as e:
                    self.logger.error(f"加载元数据文件 '{metadata_file_path}' (无锁) 过程中发生未知错误: {e}")
                    loaded_metadata = {}
            else:
                self.logger.info(f"元数据文件 '{metadata_file_path}' 不存在。将使用空元数据 (无锁)。")
                loaded_metadata = {}
        else:
            # Execute with lock
            try:
                with lock_to_use: 
                    if os.path.exists(metadata_file_path):
                        self.logger.info(f"尝试从 '{metadata_file_path}' 加载元数据 (加锁)... ")
                        with open(metadata_file_path, 'r', encoding='utf-8') as f:
                            try:
                                loaded_metadata = json.load(f)
                                if not isinstance(loaded_metadata, dict):
                                    self.logger.warning(f"元数据文件 '{metadata_file_path}' 内容不是一个有效的JSON对象（字典）。将视为空元数据。")
                                    loaded_metadata = {}
                                else:
                                    self.logger.info(f"成功加载元数据: {len(loaded_metadata)} 条记录 (加锁)。")
                            except json.JSONDecodeError as e:
                                self.logger.error(f"解析元数据文件 '{metadata_file_path}' 时发生JSON解码错误 (加锁): {e}。将视为空元数据。")
                                loaded_metadata = {} 
                    else:
                        self.logger.info(f"元数据文件 '{metadata_file_path}' 不存在。将使用空元数据 (加锁)。")
                        loaded_metadata = {}
            except Exception as e:
                self.logger.error(f"加载元数据文件 '{metadata_file_path}' (加锁) 过程中发生未知错误: {e}")
                logger.exception("详细错误信息：")
                loaded_metadata = {} 

        context.metadata = loaded_metadata
        self.logger.info("元数据加载阶段执行完毕。")
        return context 