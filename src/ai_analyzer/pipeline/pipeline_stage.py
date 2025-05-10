from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .pipeline_context import AnalysisContext

import logging
logger = logging.getLogger(__name__)

class PipelineStage(ABC):
    """
    Pipeline中一个阶段的抽象基类。
    """
    stage_name: str = "UnnamedStage"

    def __init__(self, stage_name: Optional[str] = None):
        if stage_name:
            self.stage_name = stage_name
        else:
            self.stage_name = self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.stage_name}")


    @abstractmethod
    def execute(self, context: 'AnalysisContext') -> 'AnalysisContext':
        """
        执行该pipeline阶段的逻辑。

        Args:
            context: 当前的分析上下文，包含数据和共享服务。

        Returns:
            更新后的分析上下文。
            如果阶段执行失败且无法恢复，可以抛出异常。
        """
        pass

    def __repr__(self) -> str:
        return f"<PipelineStage: {self.stage_name}>" 