#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import glob
import json
import requests
import sys
from typing import Dict, Any, List, Optional
import time
import yaml
from copy import deepcopy
import re
import copy
import threading  # 保留线程安全支持（用于RateLimiter）
import random

from src.utils.process_lock_manager import ProcessLockManager, ProcessType
from src.utils.config_loader import merge_configs
# 从新的 model_manager 模块导入
from .model_manager import ModelManager
# OpenAICompatibleAI 不再需要直接由 AIAnalyzer 导入
# from .model_manager import OpenAICompatibleAI # 已移除
# 从新的 exceptions 模块导入异常类
from .exceptions import AIAnalyzerError, ParseError, APIError # APIError 可能在 analyze_file 中被捕获或抛出
# 从新的 rate_limiter.py 导入 RateLimiter
from .rate_limiter import RateLimiter
# 从新的 retry_strategy.py 导入 RetryWithExponentialBackoff
from .retry_strategy import RetryWithExponentialBackoff

# Pipeline components
from .pipeline.orchestrator import PipelineOrchestrator
from .pipeline.stages import (
    GlobalSetupStage,
    MetadataLoadStage,
    FileDiscoveryStage,
    AnalysisExecutionStage,
    MetadataSaveStage,
    GlobalTeardownStage
)

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

logger = logging.getLogger(__name__)



class AIAnalyzer:
    """
    AI分析器，使用流水线模式处理内容的分析。
    负责初始化和运行分析流水线。
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None, 
                 config_path: Optional[str] = None):
        """
        初始化AI分析器 Pipeline。

        Args:
            config: 可选的配置字典。如果提供，将优先于config_path。
            config_path: 可选的配置文件路径。如果config未提供，则从此路径加载。
                       如果两者都未提供，Orchestrator将尝试从默认路径加载。
        """
        logger.info("初始化 AIAnalyzer...")
        
        try:
            # PipelineOrchestrator 不直接接受 debug_mode 参数
            # debug 状态由全局日志配置或 initial_config 内部的设置驱动
            self.orchestrator = PipelineOrchestrator(
                initial_config=config, 
                config_path=config_path
            )
        except ValueError as e:
            logger.error(f"AIAnalyzer 初始化失败，PipelineOrchestrator 创建错误: {e}")
            self.orchestrator = None 
            raise AIAnalyzerError(f"PipelineOrchestrator initialization failed: {e}") from e

        if self.orchestrator:
            self._setup_pipeline_stages()
            logger.info("AIAnalyzer Pipeline Stages 配置完成。")
        else:
            logger.error("PipelineOrchestrator未能初始化，AIAnalyzer将无法运行。")

    def _setup_pipeline_stages(self):
        """Helper method to add stages to the orchestrator."""
        if not self.orchestrator:
            # Should not happen if __init__ raises an error on orchestrator failure
            logger.error("Cannot setup pipeline stages: Orchestrator is not initialized.")
            return

        self.orchestrator.add_stage(GlobalSetupStage())
        self.orchestrator.add_stage(MetadataLoadStage())
        self.orchestrator.add_stage(FileDiscoveryStage())
        self.orchestrator.add_stage(AnalysisExecutionStage()) 
        self.orchestrator.add_stage(MetadataSaveStage())
        # Note on GlobalTeardownStage:
        # A more robust PipelineOrchestrator.run() would use a try/finally 
        # to ensure cleanup stages like GlobalTeardownStage are always executed.
        # For now, adding it as the last stage in the main sequence.
        self.orchestrator.add_stage(GlobalTeardownStage())

    def run_analysis_pipeline(self, force_analyze_all: bool = False) -> List[Dict[str, Any]]:
        """
        运行完整的分析流水线。

        Args:
            force_analyze_all: 如果为 True，则强制分析所有文件，忽略元数据中的完成状态。

        Returns:
            分析结果列表，每个元素是一个包含单个文件分析详情的字典。
            如果Orchestrator未初始化或执行失败，则返回空列表。
        """
        if not self.orchestrator or not self.orchestrator.context:
            logger.error("PipelineOrchestrator 或其 context 未初始化，无法运行分析。")
            return []

        # Store original 'force_analyze_all' and 'specific_file' from context to restore later
        # This direct context manipulation is okay if AIAnalyzer is the primary user of Orchestrator for a run.
        original_force_flag = self.orchestrator.context.ai_config.get('force_analyze_all', False)
        # 'specific_file' might also be affected by force_analyze_all logic in FileDiscoveryStage
        original_specific_file = self.orchestrator.context.ai_config.get('specific_file')

        try:
            if force_analyze_all:
                self.orchestrator.context.ai_config['force_analyze_all'] = True
                # When forcing all, usually we don't want to be constrained by a specific_file setting from config.
                # FileDiscoveryStage will prioritize specific_file if set.
                # If force_analyze_all is true, it might be desired to clear specific_file.
                self.orchestrator.context.ai_config['specific_file'] = None 
                logger.info("'force_analyze_all' 为 True，将强制重新分析所有文件，并忽略 'specific_file' 配置。")
            
            logger.info("开始运行 AI 分析流水线...")
            final_context = self.orchestrator.run()
            logger.info("AI 分析流水线执行完毕。")
            return final_context.analysis_results
        except Exception as e:
            logger.error(f"AI 分析流水线执行过程中发生顶层错误: {e}", exc_info=True)
            return [] 
        finally:
            # Restore original config values in the context
            if self.orchestrator and self.orchestrator.context: # Check again in case of early init failure
                self.orchestrator.context.ai_config['force_analyze_all'] = original_force_flag
                self.orchestrator.context.ai_config['specific_file'] = original_specific_file
                if force_analyze_all: # Log only if we actually changed it
                    logger.debug("'force_analyze_all' 和 'specific_file' 相关配置已恢复。")

    def analyze_all(self, 
                    specific_file: Optional[str] = None, 
                    vendor_to_process: Optional[str] = None, 
                    limit_per_vendor: Optional[int] = None,
                    force_analyze_all: bool = False):
        """
        Orchestrates the AI analysis pipeline.
        The specific_file and force_analyze_all parameters are now determined with final priority by the caller (e.g., main.py).
        """
        logger.info("AIAnalyzer 开始执行 analyze_all...")

        if not self.orchestrator or not self.orchestrator.context:
            logger.error("PipelineOrchestrator 或其 context 未初始化，无法执行 analyze_all。")
            # Consider returning a specific error indicator or raising an exception
            return False # Or appropriate error value/exception

        self.orchestrator.context.force_analyze_all = force_analyze_all
        self.orchestrator.context.specific_file_to_analyze = specific_file
        self.orchestrator.context.vendor_to_process = vendor_to_process
        self.orchestrator.context.limit_per_vendor = limit_per_vendor

        if specific_file:
            logger.info(f"AIAnalyzer 将分析特定文件: {specific_file}. 'force_analyze_all' 已被设置为 {force_analyze_all}. 其他筛选 (vendor, limit) 已被忽略。")
        elif force_analyze_all:
            logger.info("AIAnalyzer 将强制重新分析所有符合条件的文件.")
            if vendor_to_process:
                logger.info(f"(筛选厂商: {vendor_to_process}，如适用)")
            if limit_per_vendor:
                logger.info(f"(每个厂商限制文件数: {limit_per_vendor}，如适用)")
        else:
            logger.info("AIAnalyzer 将根据元数据和筛选条件分析文件.")
            if vendor_to_process:
                logger.info(f"筛选厂商: {vendor_to_process}")
            if limit_per_vendor:
                logger.info(f"每个厂商限制文件数: {limit_per_vendor}")
        
        # REMOVED: self._setup_pipeline_stages() - Stages should be set up only once during __init__.
        
        logger.info("开始运行 AI 分析流水线...")
        success = self.orchestrator.run()
        logger.info("AI 分析流水线执行完毕。")
        return success

    def run(self) -> List[Dict[str, Any]]:
        """
        运行分析，具体并发行为取决于 'use_dynamic_pool' 配置。
        """
        logger.info("AIAnalyzer.run() 被调用，将执行标准分析流水线。")
        return self.run_analysis_pipeline(force_analyze_all=False)

    def run_dynamic(self) -> List[Dict[str, Any]]:
        """
        运行分析，此方法为兼容旧API而保留。
        实际并发行为取决于 'use_dynamic_pool' 配置，由 AnalysisExecutionStage 处理。
        """
        logger.info("AIAnalyzer.run_dynamic() 被调用，将执行标准分析流水线。")
        return self.run_analysis_pipeline(force_analyze_all=False)

# Example basic usage (for testing, assuming config files are in default locations)
# if __name__ == '__main__':
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     
#     # Option 1: Load from default config path defined in Orchestrator
#     # analyzer = AIAnalyzer()
#
#     # Option 2: Specify config path
#     # analyzer = AIAnalyzer(config_path="config/config.yaml") # Ensure your Orchestrator handles this path
#
#     # Option 3: Provide config dictionary directly
#     # test_config = {
#     #     'ai_analyzer': {
#     #         'prompt_settings': {
#     #             'prompt_root_dir': 'prompts_test', 
#     #             # ... other prompt settings
#     #         },
#     #         'tasks': [{'type': 'AI标题翻译'}],
#     #         'use_dynamic_pool': False, # Force serial for this test
#     #         'force_analyze_all': True,
#     #         # ... other ai_analyzer settings
#     #     },
#     #     'directory_settings': {
#     #         'raw_data_dir': 'test_data/raw',
#     #         'analysis_output_dir': 'test_data/analysis',
#     #         'metadata_file_path': 'test_data/metadata/analysis_metadata.json'
#     #         # ... other directory settings
#     #     },
#     #     # ... other top-level config sections
#     # }
#     # logger.info("Initializing AIAnalyzer with direct config dictionary for testing.")
#     # analyzer = AIAnalyzer(config=test_config)
#
#     # ---- Choose one initialization method above ----
#     try:
#         analyzer = AIAnalyzer() # Using default path load
#         logger.info("AIAnalyzer initialized. Starting analysis run...")
#         # results = analyzer.run()
#         # logger.info(f"Run completed. Number of results: {len(results)}")
#         # for res in results:
#         #     logger.info(f"File: {res.get('file_path')}, Status: {res.get('status')}, Error: {res.get('error')}")
#
#         success = analyzer.analyze_all()
#         logger.info(f"analyze_all completed with status: {success}")
#         if analyzer.orchestrator and analyzer.orchestrator.context:
#              logger.info(f"Final analysis results from context: {len(analyzer.orchestrator.context.analysis_results)}")
#
#     except AIAnalyzerError as e:
#         logger.error(f"AIAnalyzer operation failed: {e}")
#     except Exception as e:
#         logger.error(f"An unexpected error occurred during AIAnalyzer test run: {e}", exc_info=True)

