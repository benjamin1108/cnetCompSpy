import logging
import os
import glob
from typing import List, Dict, Any, Optional, Callable # Added Optional and Callable

from ..pipeline_stage import PipelineStage
from ..pipeline_context import AnalysisContext

logger = logging.getLogger(__name__)

class FileDiscoveryStage(PipelineStage):
    def __init__(self):
        super().__init__(stage_name="FileDiscovery")

    def _normalize_path_for_metadata(self, file_path: str, context: AnalysisContext) -> str:
        """
        标准化文件路径，用于元数据存储和查找。
        目标是生成一个相对于项目根目录的、使用正斜杠的路径 (e.g., data/raw/vendor/file.md)。
        """
        if not context.project_root_dir:
            self.logger.error("Project root directory not set in context. Cannot normalize path correctly.")
            # Fallback or raise error. For now, return a cleaned absolute path.
            return os.path.normpath(file_path).replace('\\', '/')

        # Ensure file_path is absolute before calculating relative path
        abs_file_path = os.path.abspath(os.path.normpath(file_path))
        project_root_abs = os.path.abspath(os.path.normpath(context.project_root_dir))

        try:
            # Calculate path relative to project_root_dir
            relative_path = os.path.relpath(abs_file_path, project_root_abs)
            # Normalize to forward slashes
            normalized_relative_path = relative_path.replace('\\', '/')
            self.logger.debug(f"Normalized path for '{file_path}' (base: '{project_root_abs}') -> '{normalized_relative_path}'")
            return normalized_relative_path
        except ValueError as e:
            self.logger.error(f"Error normalizing path '{abs_file_path}' relative to '{project_root_abs}': {e}. Falling back to absolute path.")
            # Fallback to a cleaned absolute path if relpath fails (e.g., different drives on Windows)
            return abs_file_path.replace('\\', '/')

    def _is_file_analyzed(self, 
                            normalized_path_for_meta: str, # This is now relative to project_root
                            full_file_path: str, 
                            context: AnalysisContext) -> bool:
        """
        检查单个文件是否已经被完整分析。
        normalized_path_for_meta is the key for context.metadata.
        """
        # analysis_file_path_to_check needs to be an absolute path or correctly relative to CWD
        analysis_file_path_to_check = ""
        # context.analysis_output_dir is typically relative to project_root, e.g., "data/analysis"
        if context.analysis_output_dir and context.project_root_dir:
            # normalized_path_for_meta is like "data/raw/vendor/file.md"
            # We need to transform it to "data/analysis/vendor/file.md"
            if normalized_path_for_meta.startswith(context.raw_data_dir.replace('\\', '/')):
                path_part_after_raw_dir = normalized_path_for_meta[len(context.raw_data_dir.replace('\\', '/').rstrip('/')):].lstrip('/')
                analysis_file_relative_to_project = os.path.join(context.analysis_output_dir, path_part_after_raw_dir)
                analysis_file_path_to_check = os.path.join(context.project_root_dir, analysis_file_relative_to_project)
                analysis_file_path_to_check = os.path.normpath(analysis_file_path_to_check)
            else:
                self.logger.warning(f"Cannot reliably determine analysis file path from normalized meta key '{normalized_path_for_meta}' as it does not start with raw_data_dir '{context.raw_data_dir}'.")

        if analysis_file_path_to_check and not os.path.exists(analysis_file_path_to_check):
            self.logger.debug(f"分析结果文件不存在 '{analysis_file_path_to_check}' (derived from '{normalized_path_for_meta}')，需要分析。")
            return False
        elif not analysis_file_path_to_check:
             self.logger.debug(f"无法确定分析结果文件路径 для '{normalized_path_for_meta}'，假设需要分析。") # Assuming Russian for 'for' was a typo
             return False # If we can't check the analysis file, assume it needs analysis
        
        if normalized_path_for_meta not in context.metadata:
            self.logger.debug(f"元数据中不存在 '{normalized_path_for_meta}' 的记录，需要分析。")
            return False

        file_meta = context.metadata[normalized_path_for_meta]
        defined_tasks = context.ai_config.get('tasks', [])

        if not defined_tasks:
            self.logger.debug(f"没有定义分析任务，但文件 '{normalized_path_for_meta}' 在元数据中，认为已分析。")
            return True

        for task_config in defined_tasks:
            task_type = task_config.get('type')
            if not task_type:
                continue
            
            task_status = file_meta.get('tasks', {}).get(task_type, {})
            if not task_status.get('success', False):
                self.logger.debug(f"文件 '{normalized_path_for_meta}' 的任务 '{task_type}' 未成功完成或无记录，需要分析。")
                return False
        
        self.logger.debug(f"文件 '{normalized_path_for_meta}' 所有已定义任务均已成功完成。")
        return True

    def execute(self, context: AnalysisContext) -> AnalysisContext:
        self.logger.info("开始执行文件发现阶段...")
        context.files_to_analyze = [] # 重置以防重跑

        if not context.lock_acquired:
            self.logger.warning("分析进程锁未获取，跳过文件发现阶段。")
            return context

        force_mode = context.force_analyze_all 
        specific_file_input = context.specific_file_to_analyze
        file_limit = context.limit_per_vendor if context.limit_per_vendor is not None else 0
        vendor_to_process = context.vendor_to_process
        
        raw_data_dir = context.raw_data_dir # This is like "data/raw"
        # base_project_dir is needed if specific_file_input is relative to project root
        # Assuming context.config.get('base_dir') or a similar attribute holds the project root path.
        # For now, let's assume specific_file_input if relative, should be joined with a proper base if not already data/raw/...
        # Or, simpler: if it starts with raw_data_dir or is absolute, use as is. Otherwise, it's an error or needs base_dir. 

        supported_extensions = context.ai_config.get('supported_extensions', ['.md'])
        supported_extensions = [ext.lower() if ext.startswith('.') else '.' + ext.lower() for ext in supported_extensions]

        if not raw_data_dir or not os.path.isdir(raw_data_dir):
            self.logger.error(f"原始数据目录 (raw_data_dir) '{raw_data_dir}' 未配置或不是一个有效目录。无法发现文件。")
            return context
        
        if context.metadata is None:
            self.logger.warning("元数据未在context中初始化/加载，文件分析状态检查可能不准确。")

        discovered_files_full_paths: List[str] = []

        if specific_file_input:
            self.logger.info(f"处理 specific_file: {specific_file_input} (由 context.specific_file_to_analyze 提供)")
            
            current_file_full_path: str
            if os.path.isabs(specific_file_input):
                current_file_full_path = os.path.normpath(specific_file_input)
            else:
                # If specific_file_input is like "data/raw/aws/file.md", it's relative to project root.
                # os.path.abspath will resolve it correctly based on current working directory.
                # Ensure CWD is project root when script is run.
                current_file_full_path = os.path.abspath(os.path.normpath(specific_file_input))

            self.logger.debug(f"检查 specific_file 的规范化路径: {current_file_full_path}")

            if not os.path.exists(current_file_full_path):
                self.logger.error(f"指定的 specific_file 不存在: {current_file_full_path}")
                return context
            
            if not any(current_file_full_path.lower().endswith(ext) for ext in supported_extensions):
                self.logger.error(f"指定的 specific_file '{current_file_full_path}' 类型不受支持 (支持: {supported_extensions})。")
                return context

            normalized_path_for_meta = self._normalize_path_for_metadata(current_file_full_path, context)
            if force_mode or not self._is_file_analyzed(normalized_path_for_meta, current_file_full_path, context):
                discovered_files_full_paths.append(current_file_full_path)
            else:
                self.logger.info(f"Specific_file '{current_file_full_path}' 已分析完成且非强制模式，跳过。")
        
        else: # No specific_file, scan raw_data_dir
            self.logger.info(f"扫描目录 '{raw_data_dir}' 以查找支持的文件类型... (specific_file_input 为空)")
            # supported_extensions 已在前面获取

            # 用于按厂商筛选的计数器 (如果 limit_per_vendor > 0)
            vendor_counts: Dict[str, int] = {}

            for root, _, found_in_dir_files in os.walk(raw_data_dir):
                # 如果指定了 vendor_to_process，并且当前 root 不属于该 vendor，则跳过此目录
                if vendor_to_process:
                    # 尝试从 root 路径中提取当前厂商
                    # 假设路径结构类似 data/raw/VENDOR_NAME/...
                    try:
                        relative_to_raw = os.path.relpath(root, raw_data_dir)
                        current_vendor_in_path = relative_to_raw.split(os.sep)[0]
                        if current_vendor_in_path.lower() != vendor_to_process.lower():
                            continue # 跳过不匹配的厂商目录
                    except ValueError:
                        # 如果无法确定相对路径或厂商，保守起见继续处理
                        pass 
                
                for file_name in found_in_dir_files:
                    if any(file_name.lower().endswith(ext) for ext in supported_extensions):
                        current_file_full_path = os.path.join(root, file_name)
                        normalized_path_for_meta = self._normalize_path_for_metadata(current_file_full_path, context)
                        
                        # 应用 limit_per_vendor (如果开启且未达到限制)
                        can_add_file = True
                        if vendor_to_process and file_limit > 0:
                            vendor_key = vendor_to_process # 既然已经筛选了厂商，这里的key就是它
                            if vendor_counts.get(vendor_key, 0) >= file_limit:
                                can_add_file = False
                        
                        if can_add_file and (force_mode or not self._is_file_analyzed(normalized_path_for_meta, current_file_full_path, context)):
                            discovered_files_full_paths.append(current_file_full_path)
                            if vendor_to_process and file_limit > 0: # 更新计数器
                                vendor_counts[vendor_to_process] = vendor_counts.get(vendor_to_process, 0) + 1
            
            log_msg_parts = []
            if force_mode: log_msg_parts.append("强制模式")
            if vendor_to_process: log_msg_parts.append(f"厂商筛选: {vendor_to_process}")
            
            scan_type_msg = ", ".join(log_msg_parts) if log_msg_parts else "标准扫描"
            self.logger.info(f"{scan_type_msg}: 扫描找到 {len(discovered_files_full_paths)} {'个文件需要分析' if not force_mode else '个符合条件的文件'}")

        # 全局 file_limit 应用 (如果 specific_file_input 为空，且 limit_per_vendor 未生效或全局限制更严格)
        # 注意：如果 limit_per_vendor 已应用，这里的全局 file_limit 逻辑可能需要调整或明确其行为
        # 当前的 file_limit 是从 context.limit_per_vendor 来的，它应该是厂商级别的限制
        # 如果需要一个独立的全局限制，应该从 context.ai_config 读取一个不同的配置项
        # 为简化，我们假设这里的 file_limit 是指在所有发现的文件中的最终数量限制（如果未被厂商限制覆盖）
        # 现在的 file_limit 来自 context.limit_per_vendor，所以这个后续的全局截断逻辑可能不完全适用
        # 如果 limit_per_vendor 被使用，可能不需要这里的额外截断

        # if file_limit > 0 and len(discovered_files_full_paths) > file_limit: 
        #     # This specific block might be redundant if limit_per_vendor is the primary limiting factor now
        #     self.logger.info(f"应用全局文件数量限制: 从 {len(discovered_files_full_paths)} 个文件截取前 {file_limit} 个。")
        #     context.files_to_analyze = discovered_files_full_paths[:file_limit]
        # else:
        context.files_to_analyze = discovered_files_full_paths
            
        self.logger.info(f"文件发现阶段完成，确定 {len(context.files_to_analyze)} 个文件待分析。")
        if context.files_to_analyze:
            for f_path_idx, f_path_val in enumerate(context.files_to_analyze):
                if f_path_idx < 5:
                    self.logger.debug(f"  - {f_path_val}")
                else:
                    self.logger.debug(f"  ... and {len(context.files_to_analyze) - 5} more.")
                    break
        return context 