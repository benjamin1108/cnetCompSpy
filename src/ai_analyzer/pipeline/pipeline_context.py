from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from threading import Lock

# Forward declarations for type hints if these classes are in other files
# and to avoid circular imports initially.
# Actual imports will be needed when these are fully fleshed out.
ProcessLockManager = Any # Placeholder
ModelManager = Any # Placeholder
RateLimiter = Any # Placeholder
RetryStrategy = Any # Placeholder
PromptManager = Any # Placeholder

@dataclass
class AnalysisContext:
    """
    上下文对象，用于在 Pipeline 的各个阶段之间传递数据和共享服务。
    """
    # 配置
    config: Dict[str, Any] = field(default_factory=dict)
    ai_config: Dict[str, Any] = field(default_factory=dict) # Specific AI config section
    directory_settings: Dict[str, Any] = field(default_factory=dict)
    prompt_settings: Dict[str, Any] = field(default_factory=dict)

    # 关键路径
    project_root_dir: Optional[str] = None # RENAMED from project_base_dir to match Orchestrator usage
    raw_data_dir: Optional[str] = None
    analysis_output_dir: Optional[str] = None
    metadata_file_path: Optional[str] = None
    prompt_root_dir: Optional[str] = None

    # 待处理数据
    files_to_analyze: List[str] = field(default_factory=list)
    
    # 元数据
    metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # 分析结果
    analysis_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # 共享服务/组件实例 (这些将由 Pipeline Orchestrator 初始化并注入)
    model_manager: Optional[ModelManager] = None
    # rate_limiter: Optional[RateLimiter] = None # RateLimiter may be managed by ModelManager or thread pool
    # retry_strategy: Optional[RetryStrategy] = None # RetryStrategy might be instantiated per call or per model
    prompt_manager: Optional[PromptManager] = None # Handles loading and providing prompts

    # 同步原语
    process_lock_manager: Optional[ProcessLockManager] = None
    metadata_lock: Optional[Lock] = None # For fine-grained metadata saving control
    
    # 状态标志
    lock_acquired: bool = False # For process lock
    force_analyze_all: bool = False # ADDED: Control flag for forcing analysis
    specific_file_to_analyze: Optional[str] = None # ADDED: Specific file to analyze
    vendor_to_process: Optional[str] = None # ADDED: Vendor to filter by
    limit_per_vendor: Optional[int] = None # ADDED: Limit files per vendor
    
    # 其他可能需要的共享状态
    # e.g., current_file_path during iteration, current_task_type, etc.
    # These can be added as needed by specific stages.

    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """
        Helper to get a value from the nested config dictionary.
        Example: key_path = "ai_analyzer.max_retries"
        """
        keys = key_path.split('.')
        current_level = self.config
        for key in keys:
            if isinstance(current_level, dict) and key in current_level:
                current_level = current_level[key]
            else:
                return default
        return current_level 