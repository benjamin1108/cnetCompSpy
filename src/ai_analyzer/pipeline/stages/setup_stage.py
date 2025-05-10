import logging
import os # Added import
from ..pipeline_stage import PipelineStage
from ..pipeline_context import AnalysisContext
# Assuming ProcessLockManager might raise a specific error if lock acquisition fails
# from src.utils.process_lock_manager import LockAcquisitionError 

logger = logging.getLogger(__name__)

class GlobalSetupStage(PipelineStage):
    def __init__(self):
        super().__init__(stage_name="GlobalSetup")

    def execute(self, context: AnalysisContext) -> AnalysisContext:
        self.logger.info("开始执行全局设置阶段...")

        if not context.process_lock_manager:
            self.logger.error("ProcessLockManager 未在 AnalysisContext 中初始化。")
            raise ValueError("ProcessLockManager not available in context for GlobalSetupStage.")

        self.logger.info("尝试获取分析进程锁...")
        try:
            if context.process_lock_manager.acquire_lock():
                context.lock_acquired = True
                self.logger.info("分析进程锁已成功获取。")
            else:
                context.lock_acquired = False
                self.logger.error("无法获取分析进程锁，可能有其他分析进程正在运行或互斥进程正在运行。")
                # For setup stage, if lock acquisition fails, it usually means pipeline should not proceed.
                # Raising an error is a common pattern here, or setting a flag that subsequent stages check.
                # For now, we set context.lock_acquired = False, critical stages later MUST check this.
        except Exception as e:
            context.lock_acquired = False
            self.logger.error(f"获取分析进程锁时发生未知错误: {e}")
            # Depending on severity, could re-raise or just log and continue (with lock_acquired=False)
        
        # Ensure analysis output directory exists
        if context.analysis_output_dir:
            try:
                os.makedirs(context.analysis_output_dir, exist_ok=True)
                self.logger.info(f"已确保分析输出目录存在: {context.analysis_output_dir}")
            except Exception as e:
                self.logger.error(f"创建或验证分析输出目录 '{context.analysis_output_dir}' 时失败: {e}")
                # This could be a critical failure depending on requirements.
        else:
            self.logger.warning("Analysis output directory (analysis_output_dir) 未在 context 中配置。")

        self.logger.info("全局设置阶段执行完毕。")
        return context 