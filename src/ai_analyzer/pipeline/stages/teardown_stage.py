import logging
from ..pipeline_stage import PipelineStage
from ..pipeline_context import AnalysisContext

logger = logging.getLogger(__name__)

class GlobalTeardownStage(PipelineStage):
    def __init__(self):
        super().__init__(stage_name="GlobalTeardown")

    def execute(self, context: AnalysisContext) -> AnalysisContext:
        self.logger.info("开始执行全局清理阶段...")

        if context.process_lock_manager and context.lock_acquired:
            try:
                self.logger.info("尝试释放分析进程锁...")
                context.process_lock_manager.release_lock()
                context.lock_acquired = False # Update status
                self.logger.info("分析进程锁已成功释放。")
            except Exception as e:
                self.logger.error(f"释放分析进程锁时发生错误: {e}")
        elif context.process_lock_manager and not context.lock_acquired:
            self.logger.info("分析进程锁在 Teardown时尚未获取或已被释放，无需操作。")
        elif not context.process_lock_manager:
            self.logger.warning("ProcessLockManager 未在 AnalysisContext 中找到，无法尝试释放锁。")

        self.logger.info("全局清理阶段执行完毕。")
        return context 