import logging
import os
import time # Added import
from typing import List, Dict, Any, Optional
from threading import Lock

from .pipeline_context import AnalysisContext
from .pipeline_stage import PipelineStage
from ..model_manager import ModelManager
from ..prompt_manager import PromptManager
# Ensure this path is correct based on your project structure for utils
# Assuming src is in PYTHONPATH or utils is directly accessible
from src.utils.process_lock_manager import ProcessLockManager, ProcessType
from src.utils.config_loader import get_config, merge_configs # Changed load_config to get_config
from src.utils import colored_logger # Changed import for logger_config

# Initial basic logging configuration, will be overridden by setup_colored_logging if called.
# This helps catch issues even before colored_logger is fully setup or if it fails.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    def _determine_project_root(self) -> str:
        """
        确定项目的根目录。
        假设此文件位于 src/ai_analyzer/pipeline/ 目录下。
        项目根目录是 src/ 的父目录的父目录。
        """
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        # pipeline_dir = current_file_dir 
        ai_analyzer_dir = os.path.dirname(current_file_dir) # pipeline_dir is current_file_dir
        src_dir = os.path.dirname(ai_analyzer_dir)
        project_root = os.path.dirname(src_dir)
        logger.debug(f"Determined project root: {project_root}")
        return project_root

    def __init__(self, config_path: Optional[str] = None, initial_config: Optional[Dict[str, Any]] = None):
        # Attempt to setup colored logging ASAP.
        # If config loading fails later, at least we have some logging.
        try:
            # TODO: Parameterize these logging settings from main config if available later
            colored_logger.setup_colored_logging(level=logging.INFO) # Using INFO as a sensible default
            logger.info("Colored logging configured by PipelineOrchestrator.")
        except Exception as e:
            logger.error(f"Failed to setup colored logging: {e}", exc_info=True)
            # Basic logging should still work.

        self.stages: List[PipelineStage] = []
        self.context = AnalysisContext()
        self.project_root_dir = self._determine_project_root()
        self.context.project_root_dir = self.project_root_dir

        # 1. 加载配置
        # initial_config 作为 get_config 的 default_config，会被后续加载的文件配置覆盖。
        # config_path (如果提供) 会被 get_config 用来加载文件配置。
        # 如果 config_path 未提供，get_config 会尝试其内部定义的默认路径。
        try:
            logger.info(f"PipelineOrchestrator: 尝试加载配置。提供的 config_path: '{config_path}', initial_config provided: {initial_config is not None}")
            base_config_for_loading = initial_config if initial_config else {}
            loaded_config = get_config(config_path=config_path, default_config=base_config_for_loading, base_dir=self.project_root_dir)
            if not loaded_config and not base_config_for_loading: # 如果get_config返回空且没给initial_config
                 logger.warning("get_config 返回了空配置，并且没有提供 initial_config。上下文配置可能不完整。")

        except Exception as e:
            logger.error(f"加载主配置时发生严重错误: {e}", exc_info=True)
            # 根据策略，这里可以抛出异常或尝试使用空的loaded_config继续（可能导致后续错误）
            raise ValueError(f"Failed to load main configuration: {e}")


        # 2. 加载 Secret 配置并合并
        # get_config 应该已经能够处理项目根目录的确定，但为了明确，我们可以指定
        # secret_config_path = os.path.join(self.project_root_dir, 'config.secret.yaml')
        # 实际上，get_config 的设计可能已经在其内部处理了 secret 的合并，或者需要一个专门的函数。
        # 查阅 get_config 的实现，它在内部不会自动加载 config.secret.yaml。
        # 它加载的是指定的 config_path 或 config/ 目录下的。
        # 因此，我们需要手动加载 secret 配置。

        secret_config = {}
        secret_config_path = os.path.join(self.project_root_dir, 'config.secret.yaml')
        if os.path.exists(secret_config_path):
            logger.info(f"加载 secret 配置文件: {secret_config_path}")
            try:
                # 使用 get_config 来加载单个 secret 文件（利用其缓存和健壮性）
                # 或者，更简单地，直接用 load_yaml_file，因为它已经在 config_loader 中
                from src.utils.config_loader import load_yaml_file #局部导入
                secret_data = load_yaml_file(secret_config_path)
                if secret_data:
                    secret_config = secret_data
                else:
                    logger.warning(f"Secret 文件 {secret_config_path} 为空或加载失败。")
            except Exception as e:
                logger.error(f"加载 secret 配置文件 {secret_config_path} 时出错: {e}", exc_info=True)
        else:
            logger.info(f"Secret 配置文件 {secret_config_path} 不存在，跳过加载。")

        # 合并主配置和 Secret 配置
        if secret_config:
            final_config = merge_configs(loaded_config, secret_config)
            logger.info("已将 Secret 配置合并到主配置中。")
        else:
            final_config = loaded_config
        
        if not final_config:
            logger.error("最终配置为空！Pipeline 可能无法正确运行。")
            # Consider raising an error if config is essential and missing
            # raise ValueError("Final configuration is empty after loading attempts.")
            final_config = {} # Ensure it's a dict to avoid None issues

        self.context.config = final_config
        self.context.ai_config = final_config.get('ai_analyzer', {})

        # 从 ai_config (即 ai_analyzer 节) 中获取 directory_settings 和 prompt_settings
        if self.context.ai_config: # 确保 ai_config 不是空的
            self.context.directory_settings = self.context.ai_config.get('directory_settings', {})
            self.context.prompt_settings = self.context.ai_config.get('prompt_settings', {}) 
        else:
            # 如果 ai_config 本身就是空的，那么这些也应该是空的
            self.context.directory_settings = {}
            self.context.prompt_settings = {}
            logger.warning("'ai_analyzer' 配置部分为空，因此 directory_settings 和 prompt_settings 也将为空。")

        # 更新日志检查
        if not self.context.ai_config: # 这个检查可以保留
            logger.warning("'ai_analyzer' 配置部分未找到或为空，AI相关功能可能受限。")
        
        if not self.context.directory_settings: # 这个检查现在基于从 ai_config 获取的结果
            logger.warning("'directory_settings' 在 'ai_analyzer' 配置中未找到或为空，文件路径可能依赖默认值。")
        
        if not self.context.prompt_settings: # 新增对 prompt_settings 的检查和警告
            logger.warning("'prompt_settings' 在 'ai_analyzer' 配置中未找到或为空，PromptManager 可能无法正确加载 prompts。")


        # 2. 初始化共享服务并注入到 context
        self._initialize_shared_services()
        
        logger.info("PipelineOrchestrator 初始化完成。")

    def _initialize_shared_services(self):
        project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        
        self.context.model_manager = ModelManager(ai_config=self.context.ai_config)
        logger.info("ModelManager 注入到 AnalysisContext。")

        if not self.context.prompt_settings:
             logger.warning("Prompt settings 为空，PromptManager 可能无法正确加载 prompts。")

        self.context.prompt_manager = PromptManager(
            prompt_settings=self.context.prompt_settings, # Can be empty dict if not found
            project_root_dir=project_root_dir
        )
        logger.info("PromptManager 注入到 AnalysisContext。")
        
        defined_tasks = self.context.ai_config.get('tasks', [])
        if defined_tasks and self.context.prompt_manager:
             self.context.prompt_manager.preload_all_task_prompts(defined_tasks)

        self.context.process_lock_manager = ProcessLockManager.get_instance(ProcessType.ANALYZER)
        logger.info("ProcessLockManager 注入到 AnalysisContext。")

        self.context.metadata_lock = Lock() 
        logger.info("Metadata Lock (threading.Lock) 注入到 AnalysisContext。")
        
        self.context.raw_data_dir = self.context.directory_settings.get('raw_data_dir', 'data/raw')
        self.context.analysis_output_dir = self.context.directory_settings.get('analysis_output_dir', 'data/analysis')
        self.context.metadata_file_path = self.context.directory_settings.get('metadata_file_path', 'data/metadata/analysis_metadata.json')
        # self.context.prompt_root_dir is effectively managed by PromptManager
        logger.info(f"关键路径已设置: RawData='{self.context.raw_data_dir}', AnalysisOutput='{self.context.analysis_output_dir}', MetadataFile='{self.context.metadata_file_path}'")

    def add_stage(self, stage: PipelineStage) -> 'PipelineOrchestrator':
        self.stages.append(stage)
        logger.info(f"Stage '{stage.stage_name}' 已添加到 pipeline。")
        return self

    def run(self) -> AnalysisContext:
        if not self.stages:
            logger.warning("Pipeline 为空，没有 stages 可以执行。")
            return self.context

        logger.info(f"开始执行 Pipeline，共 {len(self.stages)} 个 stages。")
        current_context = self.context
        current_stage_name = "Unknown" # For logging in case of early error
        try:
            for stage in self.stages:
                current_stage_name = stage.stage_name
                logger.info(f"==> 开始执行 Stage: {current_stage_name} <==")
                stage_start_time = time.time()
                
                current_context = stage.execute(current_context)
                
                stage_duration = time.time() - stage_start_time
                logger.info(f"==> Stage: {current_stage_name} 执行完毕，耗时: {stage_duration:.2f} 秒 <==")
                
        except Exception as e:
            logger.error(f"Pipeline 执行过程中在 Stage '{current_stage_name}' 发生严重错误: {e}")
            logger.exception("详细错误追溯:")
            raise 
        
        logger.info("Pipeline 全部 stages 执行完毕。")
        return current_context 