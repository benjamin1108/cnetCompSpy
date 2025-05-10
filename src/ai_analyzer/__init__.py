#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI Analyzer Package

This package provides the core functionality for analyzing content using AI models,
now structured around a pipeline architecture.
"""

# 主要的分析器类 - Pipeline的入口和配置器
from .analyzer import AIAnalyzer

# 模型管理器，如果外部模块需要直接与它交互 (例如，独立于Pipeline获取模型实例)
from .model_manager import ModelManager

# Prompt管理器，如果外部需要自定义或检查prompt加载逻辑
from .prompt_manager import PromptManager 

# 核心异常类，方便外部捕获特定错误
from .exceptions import AIAnalyzerError, ParseError, APIError

# Pipeline 核心组件的基类和上下文，供可能的外部扩展使用
from .pipeline.pipeline_context import AnalysisContext
from .pipeline.pipeline_stage import PipelineStage

# RetryStrategy 和 RateLimiter 通常是内部组件，但如果需要外部微调或使用，可以导出
# from .retry_strategy import RetryWithExponentialBackoff
# from .rate_limiter import RateLimiter

__all__ = [
    'AIAnalyzer',
    'ModelManager',
    'PromptManager',
    'AIAnalyzerError',
    'ParseError',
    'APIError',
    'AnalysisContext',
    'PipelineStage',
]

"""AI分析模块""" 