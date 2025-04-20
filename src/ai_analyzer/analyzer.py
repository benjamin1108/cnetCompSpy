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

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

logger = logging.getLogger(__name__)

class RateLimiter:
    """API 请求频率限制器"""
    
    def __init__(self, requests_per_minute: int = 10):
        """
        初始化频率限制器
        
        Args:
            requests_per_minute: 每分钟允许的最大请求数
        """
        self.requests_per_minute = requests_per_minute
        self.interval = 60.0 / requests_per_minute  # 请求间隔（秒）
        self.last_request_time = 0.0
        self.lock = threading.Lock()  # 添加线程锁，确保线程安全
        logger.info(f"初始化 API 频率限制器: {requests_per_minute} 请求/分钟, 间隔 {self.interval:.2f} 秒")
    
    def wait(self):
        """
        等待直到可以发送下一个请求
        """
        with self.lock:
            # 计算需要等待的时间
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            wait_time = max(0, self.interval - elapsed)
            
            if wait_time > 0:
                logger.info(f"API 频率限制: 等待 {wait_time:.2f} 秒后发送请求")
                time.sleep(wait_time)
            
            # 更新最后请求时间
            self.last_request_time = time.time()

class RetryWithExponentialBackoff:
    """实现指数退避的API请求重试策略"""
    
    def __init__(self, initial_delay: float = 1.0, max_delay: float = 60.0, max_retries: int = 5):
        """
        初始化重试策略
        
        Args:
            initial_delay: 初始重试延迟时间（秒）
            max_delay: 最大重试延迟时间（秒）
            max_retries: 最大重试次数
        """
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        logger.info(f"初始化指数退避重试策略: 初始延迟={initial_delay}秒, 最大延迟={max_delay}秒, 最大重试次数={max_retries}")
    
    def execute(self, func, *args, **kwargs):
        """
        执行函数，失败时使用指数退避策略重试
        
        Args:
            func: 要执行的函数
            *args, **kwargs: 传递给函数的参数
            
        Returns:
            函数返回结果
            
        Raises:
            最后一次失败时抛出的异常
        """
        delay = self.initial_delay
        last_exception = None
        
        for retry_count in range(self.max_retries + 1):
            try:
                if retry_count > 0:
                    logger.warning(f"第 {retry_count}/{self.max_retries} 次重试API调用...")
                return func(*args, **kwargs)
            except (requests.exceptions.RequestException, requests.exceptions.HTTPError, 
                    requests.exceptions.ConnectionError, requests.exceptions.Timeout,
                    requests.exceptions.TooManyRedirects) as e:
                last_exception = e
                
                if retry_count == self.max_retries:
                    logger.error(f"达到最大重试次数 {self.max_retries}，放弃重试")
                    raise
                
                # 记录错误和重试信息
                error_code = e.response.status_code if hasattr(e, 'response') and hasattr(e.response, 'status_code') else "未知"
                error_msg = str(e)
                logger.warning(f"API请求失败 (错误码: {error_code}): {error_msg}")
                logger.warning(f"等待 {delay:.2f} 秒后重试...")
                
                # 等待一段时间后重试
                time.sleep(delay)
                
                # 增加延迟时间（指数增长），但不超过最大延迟
                delay = min(delay * 2, self.max_delay)
                
                # 添加一些随机性以避免同时重试
                jitter = delay * 0.1
                delay += random.uniform(-jitter, jitter)
        
        # 这里不应该有返回值，因为如果达到这里，应该已经在上面的if语句中抛出异常
        # 但为了代码安全，如果代码到达这里，抛出最后一个异常
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("所有重试都失败了，但没有捕获到异常信息")

class AIAnalyzer:
    """AI分析器，使用大模型分析爬取的内容"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化AI分析器
        
        Args:
            config: 配置信息，如果为None，则自动加载配置文件
        """
        # 如果未提供配置，尝试加载配置文件
        if config is None:
            logger.info("未提供配置，尝试加载配置文件")
            config = self._load_config()
        
        self.config = config
        self.ai_config = config.get('ai_analyzer', {})
        self.model_name = self.ai_config.get('model', 'gpt-4')
        self.max_tokens = self.ai_config.get('max_tokens', 4000)
        self.temperature = self.ai_config.get('temperature', 0.3)
        
        # 尝试从两个可能的位置获取API密钥
        self.api_key = self.ai_config.get('api_key', '')
        # 如果ai_config中没有api_key，尝试从config.ai_analyzer.api_key获取
        if not self.api_key and 'ai_analyzer' in config and 'api_key' in config['ai_analyzer']:
            self.api_key = config['ai_analyzer']['api_key']
            
        self.api_base = self.ai_config.get('api_base', '')
        self.system_prompt = self.ai_config.get('system_prompt', "你是一个专业的云计算技术分析师，擅长分析和解读各类云计算技术文档。")
        self.tasks = self.ai_config.get('tasks', [])
        self.raw_dir = 'data/raw'
        self.analysis_dir = 'data/analysis'
        self.metadata_file = 'data/metadata/analysis_metadata.json'
        self.vendor_filter = self.ai_config.get('vendor_filter', None)
        
        # 添加元数据锁，确保线程安全
        self.metadata_lock = threading.RLock()
        
        # 初始化进程锁管理器
        self.process_lock_manager = ProcessLockManager.get_instance(ProcessType.ANALYZER)
        self.lock_acquired = False
        
        # 初始化频率限制器
        requests_per_minute = self.ai_config.get('api_rate_limit', 10)  # 默认每分钟10个请求
        self.rate_limiter = RateLimiter(requests_per_minute)
        logger.info(f"API 请求频率限制: {requests_per_minute} 请求/分钟")
        
        # 检查API密钥和基础URL是否存在
        if not self.api_key or not self.api_base:
            error_msg = "未提供API密钥或API基础URL，无法初始化AI分析器"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # 确保目录存在并设置正确的权限
        self._ensure_dir_with_permissions(self.analysis_dir)
        
        # 初始化AI模型
        self.model = self._init_model()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config = {}
        
        # 获取项目根目录路径
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # 加载主配置文件
        config_path = os.path.join(base_dir, 'config.yaml')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                logger.info(f"已加载主配置文件: {config_path}")
            except Exception as e:
                logger.error(f"加载主配置文件失败: {e}")
        else:
            logger.warning(f"主配置文件不存在: {config_path}")
        
        # 加载敏感配置文件
        secret_config_path = os.path.join(base_dir, 'config.secret.yaml')
        if os.path.exists(secret_config_path):
            try:
                with open(secret_config_path, 'r', encoding='utf-8') as f:
                    secret_config = yaml.safe_load(f) or {}
                
                # 合并配置
                config = self._merge_configs(config, secret_config)
                logger.info(f"已加载敏感配置文件: {secret_config_path}")
            except Exception as e:
                logger.error(f"加载敏感配置文件失败: {e}")
        else:
            logger.warning(f"敏感配置文件不存在: {secret_config_path}")
        
        return config
    
    def _merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并配置字典"""
        result = deepcopy(base_config)
        
        for key, value in override_config.items():
            # 如果键存在且两个值都是字典，则递归合并
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                # 否则直接覆盖或添加
                result[key] = value
                
        return result
    
    def _ensure_dir_with_permissions(self, dir_path):
        """确保目录存在并设置合适的权限"""
        # 创建目录
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"创建目录: {dir_path}")
        
        # 设置目录权限 - 确保WSL和Windows都可访问
        try:
            # 设置777权限，确保完全访问权限
            os.chmod(dir_path, 0o777)
            logger.debug(f"设置目录权限: {dir_path}")
            
            # 如果是data目录，也设置其父目录权限
            parent_dir = os.path.dirname(dir_path)
            if parent_dir and parent_dir != "." and os.path.exists(parent_dir):
                os.chmod(parent_dir, 0o777)
                logger.debug(f"设置父目录权限: {parent_dir}")
        except Exception as e:
            logger.warning(f"设置目录权限失败 ({dir_path}): {e}")
    
    def _init_model(self):
        """
        初始化AI模型
        
        Returns:
            AI模型实例
        """
        logger.info(f"初始化AI模型: {self.model_name}")
        
        # 检查API密钥和基础URL是否存在
        if not self.api_key or not self.api_base:
            error_msg = "未提供API密钥或API基础URL，无法初始化AI模型"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # 返回使用OpenAI API调用的AI接口
        return self._get_openai_compatible_ai()
    
    def _get_openai_compatible_ai(self):
        """返回OpenAI兼容的API调用实现"""
        class OpenAICompatibleAI:
            def __init__(self, config):
                self.model_name = config.get('model', 'qwen-max')
                self.temperature = config.get('temperature', 0.3)
                self.max_tokens = config.get('max_tokens', 4000)
                self.api_key = config.get('api_key', '')
                self.api_base = config.get('api_base', '')
                self.system_prompt = config.get('system_prompt', "你是一个专业的云计算技术分析师，擅长分析和解读各类云计算技术文档。")
                
                # 检查API密钥和基础URL是否存在
                if not self.api_key or not self.api_base:
                    error_msg = "未提供API密钥或API基础URL，无法初始化AI模型"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # 提供商识别（基于API基础URL进行简单识别）
                self.provider = self._identify_provider()
                logger.info(f"已识别API提供商: {self.provider}")
            
            def _identify_provider(self):
                """识别API提供商"""
                if not self.api_base:
                    return "unknown"
                
                api_base_lower = self.api_base.lower()
                if "dashscope" in api_base_lower:
                    if "compatible-mode" in api_base_lower:
                        return "aliyun_compatible_full"
                    else:
                        return "aliyun"
                elif "openai.azure" in api_base_lower:
                    return "azure"
                elif "openai" in api_base_lower:
                    return "openai"
                elif "baidubce" in api_base_lower or "wenxin" in api_base_lower:
                    return "baidu"
                elif "xf-yun" in api_base_lower or "spark" in api_base_lower:
                    return "xfyun"
                elif "api.x.ai" in api_base_lower:
                    return "xai_grok"
                else:
                    return "custom"
            
            def predict(self, prompt):
                """
                调用模型进行预测
                
                Args:
                    prompt: 提示文本
                
                Returns:
                    模型响应文本
                """
                try:
                    # 检查API密钥和基础URL是否存在
                    if not self.api_key or not self.api_base:
                        error_msg = "未提供API密钥或API基础URL，无法进行API调用"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    
                    # 记录请求详情的日志
                    logger.debug(f"准备向模型 {self.model_name} 发送请求")
                    logger.debug(f"提示词长度: {len(prompt)} 字符")
                    
                    # 根据提供商构建请求
                    request_data = self._build_request_data(prompt)
                    logger.debug(f"请求URL: {request_data['url']}")
                    logger.debug(f"请求头: {','.join(request_data['headers'].keys())}")
                    logger.debug(f"请求参数: temperature={self.temperature}, max_tokens={self.max_tokens}")
                    
                    # 获取请求负载的副本，用于日志输出
                    log_payload = copy.deepcopy(request_data["payload"])
                    
                    # 如果存在messages字段并且有内容，简化提示词内容
                    if "messages" in log_payload and isinstance(log_payload["messages"], list):
                        for i, msg in enumerate(log_payload["messages"]):
                            if "content" in msg and len(msg["content"]) > 100:
                                # 保留提示词的前100个字符，其余用省略号替代
                                msg["content"] = msg["content"][:100] + "... [内容已省略]"
                    
                    # 增加请求详细日志记录
                    logger.info(f"完整请求URL: {request_data['url']}")
                    
                    # 取消流式输出，对所有提供商统一使用普通请求
                    logger.info(f"使用普通请求调用 {self.provider} API")
                    start_time = time.time()
                    
                    # 启用HTTP请求详细日志
                    requests_log = logging.getLogger("requests.packages.urllib3")
                    requests_log.setLevel(logging.DEBUG)
                    requests_log.propagate = True
                    
                    # 使用会话对象进行更详细的日志记录
                    session = requests.Session()
                    
                    logger.info(f"开始发送请求: POST {request_data['url']}")
                    
                    # 发送请求
                    response = session.post(
                        request_data["url"],
                        headers=request_data["headers"],
                        json=request_data["payload"],
                        timeout=300  # 增加超时时间到5分钟
                    )
                    
                    request_time = time.time() - start_time
                    logger.info(f"API调用完成，耗时: {request_time:.2f}秒")
                    logger.info(f"响应状态码: {response.status_code}")
                    
                    # 处理响应
                    if response.status_code == 200:
                        # 在INFO级别输出响应信息
                        logger.info(f"API调用成功: 状态码 {response.status_code}")
                        
                        # 解析响应
                        result = self._parse_response(response.json())
                        
                        # 在INFO级别输出解析后的结果
                        logger.info(f"解析后的响应长度: {len(result)} 字符")
                        # 仅记录响应内容的前50个字符作为预览，减少输出量
                        response_preview = result[:50] + "..." if len(result) > 50 else result
                        logger.info(f"解析后的响应内容预览: {response_preview}")
                        
                        return result
                    else:
                        logger.error(f"API调用失败: {response.status_code} - {response.text}")
                        return f"API调用失败: {response.status_code}"
                    
                except Exception as e:
                    logger.error(f"API调用异常: {str(e)}")
                    logger.exception("详细错误信息:")
                    return f"API调用异常: {str(e)}"
            
            def _build_request_data(self, prompt):
                """根据提供商构建请求数据"""
                headers = {
                    "Content-Type": "application/json"
                }
                
                # 基础消息格式
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ]
                
                # Grok-3 API的特殊处理
                if self.provider == "xai_grok":
                    url = "https://api.x.ai/v1/chat/completions"
                    headers["Authorization"] = f"Bearer {self.api_key}"
                    
                    payload = {
                        "model": "grok-3-latest",  # 固定使用grok-3-latest
                        "messages": messages,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                        "stream": False
                    }
                    
                    return {
                        "url": url,
                        "headers": headers,
                        "payload": payload
                    }
                
                # 直接使用用户配置的URL
                if "compatible-mode" in self.api_base.lower() and self.api_base.endswith("chat/completions"):
                    # 已经是完整URL，直接使用
                    url = self.api_base
                elif "compatible-mode" in self.api_base.lower():
                    # 如果是兼容模式但没有完整路径，添加路径
                    url = f"{self.api_base}/chat/completions"
                else:
                    # 其他情况，拼接标准路径
                    url = f"{self.api_base}/chat/completions"
                
                # 添加API密钥到请求头
                headers["Authorization"] = f"Bearer {self.api_key}"
                
                # 构建请求体
                payload = {
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "enable_search": True
                }
                
                return {
                    "url": url,
                    "headers": headers,
                    "payload": payload
                }
            
            def _parse_response(self, response_json):
                """解析不同提供商的响应格式"""
                try:
                    if self.provider == "aliyun_compatible_full" or self.provider == "aliyun_compatible":
                        # 阿里云通义千问兼容模式（OpenAI兼容格式）
                        return response_json.get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    elif self.provider == "aliyun":
                        # 阿里云通义千问
                        return response_json.get('output', {}).get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    elif self.provider == "baidu":
                        # 百度文心一言
                        return response_json.get('result', '')
                    
                    elif self.provider == "xfyun":
                        # 讯飞星火
                        return response_json.get('payload', {}).get('choices', [{}])[0].get('text', '')
                    
                    elif self.provider == "xai_grok":
                        # Grok-3 API (X.AI)
                        return response_json.get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    else:
                        # OpenAI兼容格式
                        return response_json.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                except Exception as e:
                    logger.error(f"解析响应失败: {str(e)}")
                    # 将原始响应日志从INFO级别降为DEBUG级别，仅在调试时可见
                    logger.debug(f"原始响应: {response_json}")
                    return "解析模型响应失败"
        
        return OpenAICompatibleAI(self.ai_config)
    
    def _normalize_file_path(self, file_path: str) -> str:
        """
        标准化文件路径，确保使用相对路径
        
        Args:
            file_path: 文件路径（可能是相对路径或绝对路径）
            
        Returns:
            标准化后的文件路径（相对于项目根目录）
        """
        # 获取项目根目录的绝对路径
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # 如果是绝对路径，转换为相对于项目根目录的路径
        if os.path.isabs(file_path):
            try:
                # 尝试将绝对路径转换为相对于项目根目录的路径
                rel_path = os.path.relpath(file_path, base_dir)
                logger.debug(f"将绝对路径 {file_path} 转换为相对路径 {rel_path}")
                return rel_path
            except ValueError:
                # 如果路径在不同的驱动器上（Windows），则保留原始路径
                logger.warning(f"无法将路径 {file_path} 转换为相对路径，保留原始路径")
                return file_path
        
        return file_path
    
    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        加载分析元数据
        
        Returns:
            Dict: 分析元数据字典，键为文件路径，值为元数据
        """
        from src.utils.metadata_utils import load_metadata
        
        # 使用通用的元数据加载函数
        metadata = load_metadata(
            file_path=self.metadata_file,
            lock=self.metadata_lock,
            normalize_path_func=self._normalize_file_path
        )
        
        logger.info(f"已加载分析元数据: {len(metadata)} 条记录")
        return metadata
    
    def _save_metadata(self, metadata: Dict[str, Dict[str, Any]]) -> None:
        """
        保存分析元数据
        
        Args:
            metadata: 分析元数据字典
        """
        from src.utils.metadata_utils import save_metadata
        
        # 使用通用的元数据保存函数
        save_metadata(
            file_path=self.metadata_file,
            metadata=metadata,
            lock=self.metadata_lock,
            normalize_path_func=self._normalize_file_path
        )
        
        logger.info(f"已保存分析元数据: {len(metadata)} 条记录")
    
    def _get_files_to_analyze(self) -> List[str]:
        """
        获取需要分析的文件列表
        
        Returns:
            文件路径列表
        """
        files = []
        force_mode = self.ai_config.get('force', False)
        metadata = self._load_metadata()
        specific_file = self.ai_config.get('specific_file', None)
        file_limit = self.ai_config.get('file_limit', 0)  # 获取文件数量限制
        
        # 如果指定了特定文件，只分析该文件
        if specific_file:
            # 标准化文件路径
            normalized_specific_file = self._normalize_file_path(specific_file)
            logger.info(f"仅分析指定文件: {normalized_specific_file}")
            
            # 检查文件是否存在
            if not os.path.exists(specific_file):
                logger.error(f"指定的文件不存在: {specific_file}")
                return []
            
            # 检查文件是否为markdown文件
            if not specific_file.endswith('.md'):
                logger.error(f"指定的文件不是markdown文件: {specific_file}")
                return []
            
            # 强制模式下，直接返回该文件
            if force_mode:
                logger.info(f"强制模式已启用，将分析指定文件: {normalized_specific_file}")
                return [specific_file]
            
            # 非强制模式下，检查该文件是否需要分析
            file_needs_analysis = False
            
            # 检查分析结果文件是否存在
            relative_path = os.path.relpath(specific_file, self.raw_dir)
            analysis_file_path = os.path.join(self.analysis_dir, relative_path)
            if not os.path.exists(analysis_file_path):
                file_needs_analysis = True
                logger.info(f"分析结果文件不存在: {analysis_file_path}")
            elif normalized_specific_file not in metadata:
                # 元数据中不存在该文件的记录，需要分析
                file_needs_analysis = True
                logger.info(f"元数据中不存在该文件的记录: {normalized_specific_file}")
            else:
                # 检查元数据中的分析状态
                file_metadata = metadata[normalized_specific_file]
                
                # 检查是否所有任务都成功完成
                all_tasks_completed = True
                for task in self.tasks:
                    task_type = task.get('type')
                    if not task_type:
                        continue
                        
                    # 检查任务是否成功完成
                    task_status = file_metadata.get('tasks', {}).get(task_type, {})
                    if not task_status.get('success', False):
                        all_tasks_completed = False
                        logger.info(f"任务 {task_type} 未成功完成")
                        break
                
                # 如果不是所有任务都成功完成，则需要分析
                if not all_tasks_completed:
                    file_needs_analysis = True
            
            if file_needs_analysis:
                logger.info(f"指定文件需要分析: {normalized_specific_file}")
                return [specific_file]
            else:
                logger.info(f"指定文件已经分析过，不需要重新分析: {normalized_specific_file}")
                return []
        
        # 如果没有指定特定文件，遍历raw目录下的所有md文件
        for md_file in glob.glob(f"{self.raw_dir}/**/*.md", recursive=True):
            # 标准化文件路径
            normalized_md_file = self._normalize_file_path(md_file)
            
            # 如果设置了vendor_filter，则根据过滤函数筛选文件
            if self.vendor_filter and not self.vendor_filter(normalized_md_file):
                continue
                
            # 检查是否已经成功分析过
            file_needs_analysis = False
            
            if force_mode:
                # 强制模式下，所有文件都需要分析
                file_needs_analysis = True
            else:
                # 检查分析结果文件是否存在
                relative_path = os.path.relpath(md_file, self.raw_dir)
                analysis_file_path = os.path.join(self.analysis_dir, relative_path)
                if not os.path.exists(analysis_file_path):
                    file_needs_analysis = True
                    logger.debug(f"分析结果文件不存在: {analysis_file_path}")
                elif normalized_md_file not in metadata:
                    # 元数据中不存在该文件的记录，需要分析
                    file_needs_analysis = True
                else:
                    # 检查元数据中的分析状态
                    file_metadata = metadata[normalized_md_file]
                    
                    # 检查是否所有任务都成功完成
                    all_tasks_completed = True
                    for task in self.tasks:
                        task_type = task.get('type')
                        if not task_type:
                            continue
                            
                        # 检查任务是否成功完成
                        task_status = file_metadata.get('tasks', {}).get(task_type, {})
                        if not task_status.get('success', False):
                            all_tasks_completed = False
                            break
                    
                    # 如果不是所有任务都成功完成，则需要分析
                    if not all_tasks_completed:
                        file_needs_analysis = True
            
            if file_needs_analysis:
                files.append(md_file)
        
        # 如果设置了文件数量限制，则只返回指定数量的文件
        if file_limit > 0 and len(files) > file_limit:
            logger.info(f"应用文件数量限制: {file_limit}/{len(files)}")
            files = files[:file_limit]
        
        if force_mode:
            logger.info(f"强制模式已启用，将分析 {len(files)} 个文件")
        else:
            logger.info(f"找到 {len(files)} 个文件需要分析")
        
        return files
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        分析单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            分析结果
        """
        # 标准化文件路径
        normalized_file_path = self._normalize_file_path(file_path)
        logger.info(f"开始分析文件: {normalized_file_path}")
        
        # 加载元数据 - 使用锁确保线程安全
        with self.metadata_lock:
            metadata = self._load_metadata()
            file_metadata = metadata.get(normalized_file_path, {
                'file': normalized_file_path,
                'last_analyzed': None,
                'tasks': {}
            })
        
        try:
            # 读取文件内容
            logger.debug(f"读取文件内容: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"文件内容长度: {len(content)} 字符")
            
            # 获取元数据
            logger.debug(f"提取文件元数据")
            file_info = self._extract_metadata(content)
            file_metadata['info'] = file_info
            logger.debug(f"提取的元数据: {file_info}")
            
            # 准备输出文件
            relative_path = os.path.relpath(file_path, self.raw_dir)
            target_dir = os.path.dirname(os.path.join(self.analysis_dir, relative_path))
            
            # 创建目录并确保权限正确
            self._ensure_dir_with_permissions(target_dir)
            
            md_path = os.path.join(self.analysis_dir, relative_path)
            
            analysis_results = {}
            logger.info(f"将执行 {len(self.tasks)} 个分析任务")
            
            # 记录任务执行状态
            tasks_status = {}
            
            # 打开文件，使用'w'模式覆盖任何现有内容
            with open(md_path, 'w', encoding='utf-8') as f:
                # 依次执行所有分析任务，并立即写入文件
                for i, task in enumerate(self.tasks):
                    task_type = task.get('type')
                    prompt = task.get('prompt')
                    output = task.get('output', True)  # 默认显示
                    
                    if not task_type or not prompt:
                        logger.warning(f"跳过无效任务: {task}")
                        continue
                    
                    logger.info(f"执行任务 [{i+1}/{len(self.tasks)}]: {task_type}")
                    
                    # 初始化任务状态
                    task_status = {
                        'success': False,
                        'error': None,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    try:
                        # 构建完整提示
                        full_prompt = f"{prompt}\n\n{content}"
                        logger.debug(f"完整提示词长度: {len(full_prompt)} 字符")
                        
                        # 调用AI模型获取结果
                        logger.info(f"开始调用AI模型进行 {task_type} 分析...")
                        logger.info(f"[{time.strftime('%H:%M:%S')}] 正在发送请求至API服务器...")
                        start_time = time.time()
                        result = self._analyze_content(full_prompt, task_type)
                        end_time = time.time()
                        logger.info(f"AI模型调用完成，耗时: {end_time - start_time:.2f} 秒")
                        logger.info(f"[{time.strftime('%H:%M:%S')}] 已接收{len(result)}字符的响应")
                        
                        # 检查结果是否包含错误信息
                        if result.startswith("API调用失败") or result.startswith("API调用异常") or len(result.strip()) < 10:
                            raise ValueError(f"API调用结果无效: {result}")
                        
                        # 清理AI模型输出中的额外文本
                        cleaned_result = self._clean_ai_output(result, task_type)
                        
                        # 保存分析结果到内存
                        analysis_results[task_type] = cleaned_result
                        
                        # 特殊处理：标题翻译总是需要保存，因为它用于网页标题显示
                        if task_type == "AI标题翻译" or output:
                            # 添加任务开始标记 - 使用特殊的HTML注释作为分隔符
                            task_start = f"\n<!-- AI_TASK_START: {task_type} -->\n"
                            f.write(task_start)
                            f.flush()
                            
                            # 立即写入结果到文件
                            f.write(f"{cleaned_result}\n")
                            f.flush()
                            os.fsync(f.fileno())  # 确保数据完全写入磁盘
                            
                            # 添加任务结束标记
                            task_end = f"\n<!-- AI_TASK_END: {task_type} -->\n\n"
                            f.write(task_end)
                            f.flush()
                            os.fsync(f.fileno())  # 确保数据完全写入磁盘
                            
                            logger.info(f"已将任务 {task_type} 的分析结果写入文件，并进行了同步")
                        else:
                            logger.info(f"任务 {task_type} 设置为不输出到文件，结果仅保存在内存中")
                        
                        # 标记任务成功
                        task_status['success'] = True
                    except Exception as e:
                        # 记录任务失败
                        error_msg = str(e)
                        logger.error(f"任务 {task_type} 执行失败: {error_msg}")
                        task_status['error'] = error_msg
                    
                    # 保存任务状态
                    tasks_status[task_type] = task_status
            
            # 设置文件权限 - 使用完全开放的权限以确保Windows可访问
            try:
                # 等待文件系统同步
                time.sleep(0.5)
                os.chmod(md_path, 0o777)  # 所有人可读写执行
                logger.debug(f"设置文件权限: {md_path}")
            except Exception as e:
                logger.warning(f"设置文件权限失败: {e}")
            
            # 更新元数据 - 使用锁确保线程安全
            with self.metadata_lock:
                # 重新加载元数据，避免覆盖其他线程的更改
                current_metadata = self._load_metadata()
                file_metadata['last_analyzed'] = time.strftime('%Y-%m-%d %H:%M:%S')
                file_metadata['tasks'] = tasks_status
                current_metadata[normalized_file_path] = file_metadata
                
                # 保存元数据
                self._save_metadata(current_metadata)
            
            logger.info(f"文件分析完成: {file_path}")
            
            return {
                'file': file_path,
                'metadata': file_info,
                'analysis': analysis_results,
                'tasks_status': tasks_status
            }
            
        except Exception as e:
            logger.error(f"分析文件失败: {file_path} - {e}")
            logger.exception("详细错误信息:")
            
            # 更新元数据，记录错误 - 使用锁确保线程安全
            with self.metadata_lock:
                # 重新加载元数据，避免覆盖其他线程的更改
                current_metadata = self._load_metadata()
                file_metadata['last_error'] = str(e)
                file_metadata['last_error_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                current_metadata[normalized_file_path] = file_metadata
                
                # 保存元数据
                self._save_metadata(current_metadata)
            
            return {
                'file': file_path,
                'error': str(e)
            }
    
    def _clean_ai_output(self, result: str, task_type: str) -> str:
        """
        清理AI模型输出中的额外文本
        
        Args:
            result: AI模型的原始输出
            task_type: 任务类型
            
        Returns:
            清理后的输出
        """
        # 如果是AI标题翻译，使用更精确的方法提取标题
        if task_type == "AI标题翻译":
            # 首先尝试查找常见的解释性文本后面的标题
            explanation_patterns = [
                "Here is the result:", "Here's the result:", 
                "Here is the translated title:", "Here's the translated title:",
                "The translated title is:", "Translated title:",
                "Here is my translation:", "Here's my translation:"
            ]
            
            for pattern in explanation_patterns:
                if pattern in result:
                    # 找到解释文本后的内容
                    title_part = result.split(pattern, 1)[1].strip()
                    if title_part:
                        return title_part
            
            # 如果没有找到解释性文本，尝试直接提取带标签的标题
            # 查找形如"[标签] 标题内容"的模式
            import re
            title_match = re.search(r'\[(解决方案|新功能|新产品|产品更新|技术更新|案例分析)\](.*?)($|\n)', result)
            if title_match:
                tag = title_match.group(1)
                title_content = title_match.group(2).strip()
                return f"[{tag}] {title_content}"
            
            # 如果没有找到标签，但结果很短且没有多行，可能就是标题本身
            if len(result.strip().split('\n')) == 1 and len(result.strip()) < 100:
                return result.strip()
            
            # 最后一种情况：尝试找到最后一个包含标签的行
            lines = result.strip().split('\n')
            for line in reversed(lines):
                if '[' in line and ']' in line:
                    tag_match = re.search(r'\[(.*?)\](.*?)$', line)
                    if tag_match:
                        tag = tag_match.group(1)
                        content = tag_match.group(2).strip()
                        if any(keyword in tag for keyword in ["解决方案", "新功能", "新产品", "产品更新", "技术更新", "案例分析"]):
                            return f"[{tag}] {content}"
        
        # 对于其他任务类型，使用更强大的方法去除解释性前缀
        # 首先尝试识别常见的解释性段落模式
        explanation_patterns = [
            r"^I understand.*?Here is.*?\n\n",
            r"^Based on.*?Here is.*?\n\n",
            r"^As requested.*?Here is.*?\n\n",
            r"^I've analyzed.*?Here's my.*?\n\n",
            r"^Here is.*?analysis.*?\n\n"
        ]
        
        import re
        cleaned_result = result
        for pattern in explanation_patterns:
            cleaned_result = re.sub(pattern, "", cleaned_result, flags=re.DOTALL | re.IGNORECASE)
        
        # 如果清理后的结果为空或者与原始结果相同，尝试行级别的清理
        if not cleaned_result.strip() or cleaned_result == result:
            lines = result.split('\n')
            cleaned_lines = []
            skip_block = False
            
            for i, line in enumerate(lines):
                # 检测解释性开头行
                if i == 0 and any(explanation in line.lower() for explanation in [
                    "i understand", "here is", "based on", "as requested", "i've analyzed", "here's my"
                ]):
                    skip_block = True
                    continue
                
                # 如果遇到空行，可能是解释段落的结束
                if not line.strip() and skip_block:
                    skip_block = False
                    continue
                
                # 如果不在跳过模式，添加该行
                if not skip_block:
                    cleaned_lines.append(line)
            
            # 重新组合清理后的行
            cleaned_result = '\n'.join(cleaned_lines).strip()
        
        # 如果清理后的结果为空，则返回原始结果
        if not cleaned_result.strip():
            return result.strip()
        
        return cleaned_result.strip()
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        从文件内容中提取元数据
        
        Args:
            content: 文件内容
            
        Returns:
            元数据字典
        """
        metadata = {
            'title': '',
            'original_url': '',
            'crawl_time': '',
            'vendor': '',
            'type': ''
        }
        
        # 扩展元数据提取逻辑，支持多种格式
        lines = content.split('\n')
        for line in lines[:20]:  # 只检查前20行
            line = line.strip()
            # 提取标题
            if line.startswith('# '):
                metadata['title'] = line[2:].strip()
            
            # 提取原始链接 - 支持多种格式
            elif line.startswith('原始链接:') or line.startswith('**原始链接:**'):
                url_part = line.split(':', 1)[1].strip()
                # 处理可能的Markdown链接格式 [url](url)
                if '[' in url_part and '](' in url_part:
                    url_match = re.search(r'\[(.*?)\]\((.*?)\)', url_part)
                    if url_match:
                        metadata['original_url'] = url_match.group(2)
                else:
                    metadata['original_url'] = url_part
            
            # 提取爬取时间 - 支持多种格式
            elif line.startswith('爬取时间:') or line.startswith('**爬取时间:**'):
                metadata['crawl_time'] = line.split(':', 1)[1].strip()
            elif line.startswith('发布时间:') or line.startswith('**发布时间:**'):
                metadata['crawl_time'] = line.split(':', 1)[1].strip()
            
            # 提取厂商信息 - 支持多种格式
            elif line.startswith('厂商:') or line.startswith('**厂商:**'):
                vendor_part = line.split(':', 1)[1].strip()
                metadata['vendor'] = vendor_part
            
            # 提取类型信息 - 支持多种格式
            elif line.startswith('类型:') or line.startswith('**类型:**'):
                type_part = line.split(':', 1)[1].strip()
                metadata['type'] = type_part
        
        # 清理元数据值（移除可能的粗体标记等）
        for key in metadata:
            if metadata[key]:
                # 移除粗体标记
                metadata[key] = metadata[key].replace('**', '')
                # 移除首尾空白
                metadata[key] = metadata[key].strip()
        
        return metadata
    
    def _analyze_content(self, prompt: str, task_type: str) -> str:
        """
        分析内容并返回结果(不写入文件)
        
        Args:
            prompt: 提示词
            task_type: 任务类型
            
        Returns:
            分析结果文本
        """
        # 检查是否启用mock模式
        mock_mode = self.ai_config.get('mock', False)
        if mock_mode:
            logger.info(f"[{time.strftime('%H:%M:%S')}] Mock模式已启用，将返回mock数据而非真实API调用")
            return self._get_mock_result(task_type, prompt)
        
        try:
            # 如果API密钥为空，抛出异常
            if not self.api_key or not self.api_base:
                error_msg = "未提供API密钥或API基础URL，无法进行内容分析"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # 构建AI请求
            api = self._get_openai_compatible_ai()
            
            # 记录请求信息
            logger.debug(f"准备向模型 {self.model_name} 发送 {task_type} 请求")
            
            # 准备请求数据
            logger.debug(f"[{time.strftime('%H:%M:%S')}] 正在构建请求数据...")
            request_data = api._build_request_data(prompt)
            
            # 获取请求负载的副本，用于日志输出
            log_payload = copy.deepcopy(request_data["payload"])
            
            # 如果存在messages字段并且有内容，简化提示词内容
            if "messages" in log_payload and isinstance(log_payload["messages"], list):
                for i, msg in enumerate(log_payload["messages"]):
                    if "content" in msg and len(msg["content"]) > 100:
                        # 保留提示词的前100个字符，其余用省略号替代
                        msg["content"] = msg["content"][:100] + "... [内容已省略]"
            
            # 增加请求详细日志记录
            logger.info(f"[{time.strftime('%H:%M:%S')}] 完整请求URL: {request_data['url']}")
            
            # 检查是否使用动态线程池
            use_dynamic = self.ai_config.get('use_dynamic_pool', True)
            
            # 使用频率限制器等待合适的请求间隔
            if use_dynamic:
                try:
                    # 尝试导入动态线程池的RateLimiter
                    from src.ai_analyzer.thread_pool import log_yellow, log_green
                    # 获取线程池实例，使用线程池的频率限制器
                    from src.ai_analyzer.thread_pool import get_thread_pool
                    thread_pool = get_thread_pool()
                    log_yellow(f"执行AI分析任务: {task_type}，使用动态线程池频率限制器")
                    # 线程池限制器会自动控制API调用频率
                    wait_time = thread_pool.rate_limiter.wait()
                    if wait_time > 0:
                        log_yellow(f"线程等待了 {wait_time:.2f}秒 以符合API频率限制")
                except ImportError:
                    logger.info(f"[{time.strftime('%H:%M:%S')}] 应用内置API频率限制...")
                    self.rate_limiter.wait()
            else:
                logger.info(f"[{time.strftime('%H:%M:%S')}] 应用内置API频率限制...")
                self.rate_limiter.wait()
                
            logger.info(f"[{time.strftime('%H:%M:%S')}] 频率限制检查通过，开始发送API请求")
            
            # 启用HTTP请求详细日志
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True
            
            # 使用会话对象进行更详细的日志记录
            session = requests.Session()
            
            # 创建一个重试器
            retries = self.ai_config.get('max_retries', 3)
            initial_delay = self.ai_config.get('initial_retry_delay', 2.0)
            max_delay = self.ai_config.get('max_retry_delay', 30.0)
            retry_strategy = RetryWithExponentialBackoff(
                initial_delay=initial_delay,
                max_delay=max_delay,
                max_retries=retries
            )
            
            # 定义发送请求的函数，用于重试机制
            def send_api_request():
                response = session.post(
                    request_data["url"],
                    headers=request_data["headers"],
                    json=request_data["payload"],
                    timeout=180  # 增加超时时间
                )
                
                # 如果使用动态线程池，记录API调用
                if use_dynamic:
                    try:
                        from src.ai_analyzer.thread_pool import get_thread_pool, log_green
                        thread_pool = get_thread_pool()
                        thread_pool.rate_limiter.record_api_call()
                        log_green(f"已记录API调用: {task_type}")
                    except (ImportError, AttributeError):
                        pass
                
                # 检查响应状态
                if response.status_code != 200:
                    # 对于可以重试的状态码，抛出异常以触发重试
                    if response.status_code in [429, 500, 502, 503, 504]:  # 添加其他可重试的状态码
                        error_msg = f"可重试的API错误: {response.status_code} - {response.text}"
                        logger.warning(error_msg)
                        response.reason = error_msg
                        response.raise_for_status()  # 抛出异常以触发重试
                    elif response.status_code == 429:  # 特别处理速率限制错误
                        error_msg = f"API调用频率受限: {response.status_code} - {response.text}"
                        logger.warning(error_msg)
                        response.reason = error_msg
                        response.raise_for_status()
                
                return response
                
            # 使用重试策略执行API请求
            logger.info(f"[{time.strftime('%H:%M:%S')}] 准备发送API请求，已配置自动重试机制...")
            
            # 发送请求并计时
            request_start = time.time()
            try:
                response = retry_strategy.execute(send_api_request)
                request_time = time.time() - request_start
                
                # 记录响应信息
                logger.info(f"[{time.strftime('%H:%M:%S')}] 收到API响应，耗时: {request_time:.2f}秒")
                logger.info(f"[{time.strftime('%H:%M:%S')}] 响应状态码: {response.status_code}")
                
                # 如果到这里，说明请求成功
                logger.info(f"[{time.strftime('%H:%M:%S')}] API调用成功: 状态码 {response.status_code}")
                logger.info(f"[{time.strftime('%H:%M:%S')}] 响应大小: {len(response.text)} 字节")
                
                # 仅记录响应内容的前50个字符作为预览，减少输出量
                response_preview = response.text[:50] + "..." if len(response.text) > 50 else response.text
                logger.info(f"[{time.strftime('%H:%M:%S')}] 响应预览: {response_preview}")
                
                logger.debug(f"[{time.strftime('%H:%M:%S')}] 开始解析响应...")
                
                # 解析响应
                parse_start = time.time()
                result = api._parse_response(response.json())
                parse_time = time.time() - parse_start
                
                # 记录解析结果信息
                logger.info(f"[{time.strftime('%H:%M:%S')}] 响应解析完成，耗时: {parse_time:.2f}秒")
                logger.info(f"解析后的响应长度: {len(result)} 字符")
                
                # 记录解析结果的前50个字符作为预览，减少输出量
                result_log_preview = result[:50] + "..." if len(result) > 50 else result
                logger.info(f"解析结果预览: {result_log_preview}")
                
                if use_dynamic:
                    try:
                        from src.ai_analyzer.thread_pool import log_green
                        log_green(f"AI分析任务完成: {task_type}")
                    except ImportError:
                        pass
                
                # 返回原始结果，不进行任何格式化
                logger.info(f"[{time.strftime('%H:%M:%S')}] {task_type} 响应接收完成，总长度: {len(result)} 字符")
                return result
            except Exception as e:
                error_msg = f"API调用失败: {str(e)}"
                logger.error(f"[{time.strftime('%H:%M:%S')}] {error_msg}")
                logger.exception("详细错误信息:")
                return f"API调用失败: {str(e)}"
            
        except Exception as e:
            error_msg = f"API调用异常: {str(e)}"
            logger.error(f"[{time.strftime('%H:%M:%S')}] {error_msg}")
            logger.exception("详细错误信息:")
            return error_msg
            
    def _get_mock_result(self, task_type: str, prompt: str) -> str:
        """
        根据任务类型生成mock结果
        
        Args:
            task_type: 任务类型
            prompt: 提示词
            
        Returns:
            mock结果文本
        """
        # 获取mock延迟时间，默认为2秒
        mock_delay = self.ai_config.get('mock_delay', 2)
        logger.info(f"[{time.strftime('%H:%M:%S')}] 生成{task_type}的mock数据，模拟延迟{mock_delay}秒")
        
        # 模拟AI分析的响应时间
        time.sleep(mock_delay)
        
        # 从提示词中提取文章标题（如果存在）
        title = ""
        content_lines = prompt.split('\n')
        for line in content_lines[:20]:  # 只检查前20行
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        if not title:
            title = "云计算网络技术文章"
        
        # 根据任务类型返回不同的mock数据
        if task_type == "AI标题翻译":
            # 判断标题是否包含特定关键词，以决定使用哪种前缀
            if any(keyword in title.lower() for keyword in ["how to", "guide", "best practices", "tutorial", "implement"]):
                return "[解决方案] " + title + "（中文翻译）"
            else:
                return "[新功能] " + title + "（中文翻译）"
        
        elif task_type == "AI竞争分析":
            # 判断是解决方案还是产品功能
            if any(keyword in title.lower() for keyword in ["how to", "guide", "best practices", "tutorial", "implement"]):
                return """# 解决方案分析

## 解决方案概述
这是一个关于**云网络**技术的解决方案，旨在帮助用户解决网络连接、安全和性能问题。该方案利用了**软件定义网络(SDN)**和**网络功能虚拟化(NFV)**技术，为企业提供灵活、可扩展的网络架构。

## 实施步骤
1. 评估现有网络架构和需求，确定迁移策略
2. 部署核心网络组件，包括虚拟路由器和负载均衡器
3. 配置安全策略和访问控制列表
4. 实施监控和日志系统，确保网络可见性
5. 进行性能测试和优化

## 方案客户价值
- 提高网络灵活性，支持快速业务变化和扩展
- 降低运维复杂度，实现 _管理效率提升40%_
- 增强安全性，通过微分段和深度包检测防御威胁
- 优化成本结构，相比传统网络解决方案 _节省约25%的总拥有成本_

## 涉及的相关产品
- 虚拟私有云(VPC)：提供隔离的网络环境
- 负载均衡服务：确保应用高可用性和性能
- 网络安全组：实现细粒度的访问控制
- 流日志：提供网络流量分析能力

## 技术评估
该解决方案采用了业界领先的云原生网络技术，具有较高的技术成熟度和可靠性。方案的优势在于灵活性和自动化程度高，但对于特定的传统网络协议支持可能存在一定限制。实施过程中需要考虑与现有系统的兼容性和迁移策略。

## 其他信息
部署该解决方案需要具备基本的云计算和网络知识，建议由有经验的网络工程师主导实施。方案支持主流操作系统和应用环境，可与大多数企业IT系统无缝集成。"""
            else:
                return """# 产品功能分析

## 新功能/新产品概述
这是一项关于**云网络连接**的新功能，提供了增强的网络连接能力和性能优化。该功能基于**高级路由算法**和**智能流量管理**技术，旨在解决企业在多云环境下面临的网络连接挑战。产品定位于需要高性能、安全可靠网络连接的企业客户。

## 关键客户价值
- 提供统一的网络管理界面，简化多云环境下的网络配置和监控
- 实现智能路由优化，相比传统方案 _降低网络延迟达30%_
- 支持自动扩展和故障转移，确保业务连续性
- 提供详细的网络分析和可视化，帮助客户优化网络架构

## 关键技术洞察
- 采用 _基于AI的流量预测_ 技术，动态调整网络资源分配
- 实现了跨区域的低延迟连接，通过优化路由和缓存机制
- 集成了高级安全功能，包括DDoS防护和加密传输
- 支持多种网络协议和标准，确保与现有系统的兼容性

## 市场影响评估
该产品功能的推出将显著增强云服务提供商在网络连接领域的竞争力。目标客户主要是大中型企业和对网络性能有高要求的行业（如金融、医疗、在线游戏等）。该功能填补了市场上在多云网络管理方面的空白，预计将吸引更多企业客户迁移到云环境。

## 其他信息
该功能目前处于公开预览阶段，预计在下一季度正式发布。使用该功能需要企业账户权限，并且某些高级特性可能需要额外付费。"""
        
        elif task_type == "AI全文翻译":
            # 生成一个简单的中文翻译mock
            return f"""# {title}（中文翻译）

这是一篇关于云计算网络技术的文章的中文翻译。原文讨论了云计算网络的最新发展和技术趋势。

## 主要内容

云计算网络技术正在快速发展，主要表现在以下几个方面：

1. 软件定义网络(SDN)的广泛应用
2. 网络功能虚拟化(NFV)技术的成熟
3. 多云网络连接解决方案的创新
4. 网络安全技术的增强

## 技术详情

云服务提供商不断推出新的网络产品和功能，以满足企业客户的需求。这些创新包括：

- 高性能的虚拟私有网络
- 智能负载均衡技术
- 全球分布式内容分发
- 自动化网络配置和管理工具

## 结论

随着云计算的普及，网络技术将继续演进，为企业提供更加灵活、安全、高效的连接方案。"""
        
        else:
            # 对于未知的任务类型，返回通用mock数据
            return f"""# Mock数据：{task_type}

这是为任务类型 "{task_type}" 生成的mock数据。

在实际的AI分析中，这里会包含针对原始内容的详细分析结果。

当前处于mock模式，用于调试整体项目流程，无需进行真正的AI API调用。"""
    
    def run(self) -> List[Dict[str, Any]]:
        """
        运行分析（单线程顺序执行）
        
        Returns:
            分析结果列表
        """
        # 获取进程锁，确保同一时间只有一个分析进程在运行
        if not self.process_lock_manager.acquire_lock():
            logger.error("无法获取分析进程锁，可能有其他分析进程正在运行或互斥进程正在运行")
            return []
        
        self.lock_acquired = True
        logger.info("已获取分析进程锁，开始执行分析任务")
        
        try:
            # 获取需要分析的文件
            files = self._get_files_to_analyze()
            if not files:
                logger.info("没有需要分析的新文件")
                return []
            
            results = []
            logger.info(f"使用单线程顺序分析 {len(files)} 个文件")
            
            # 顺序处理每个文件
            for file in files:
                logger.info(f"开始分析文件: {file}")
                try:
                    result = self.analyze_file(file)
                    results.append(result)
                    logger.info(f"文件分析完成: {file}")
                except Exception as e:
                    logger.error(f"处理文件时发生异常: {file} - {e}")
                    results.append({
                        'file': file,
                        'error': str(e)
                    })
            
            # 分析完成后，对整个分析目录应用权限，确保Windows用户可以访问
            try:
                logger.info("对分析结果目录应用权限...")
                
                # 确保data目录可访问
                os.system("chmod -R 777 data")  # 递归设置data及所有子目录权限
                
                # 强制写入更改到磁盘
                os.system("sync")
                
                logger.info("分析结果目录权限设置完成")
                
                # 等待文件系统同步
                time.sleep(1)
            except Exception as e:
                logger.warning(f"设置分析结果目录权限失败: {e}")
            
            return results
        finally:
            # 释放进程锁
            if self.lock_acquired:
                self.process_lock_manager.release_lock()
                logger.info("已释放分析进程锁")
    
    def run_dynamic(self) -> List[Dict[str, Any]]:
        """
        运行分析（使用动态线程池）
        
        Returns:
            分析结果列表
        """
        # 获取进程锁，确保同一时间只有一个分析进程在运行
        if not self.process_lock_manager.acquire_lock():
            logger.error("无法获取分析进程锁，可能有其他分析进程正在运行或互斥进程正在运行")
            return []
        
        self.lock_acquired = True
        logger.info("已获取分析进程锁，开始执行分析任务")
        
        try:
            # 导入动态线程池
            try:
                from src.ai_analyzer.thread_pool import get_thread_pool, log_yellow, log_green, log_red
            except ImportError:
                logger.error("无法导入动态线程池模块，将回退到单线程模式")
                return self.run()
            
            # 获取需要分析的文件
            files = self._get_files_to_analyze()
            if not files:
                logger.info("没有需要分析的新文件")
                return []
            
            # 获取API调用频率限制和最大线程数
            api_rate_limit = self.ai_config.get('api_rate_limit', 10)
            max_threads = self.ai_config.get('max_workers', 10)
            
            logger.info(f"使用动态线程池分析 {len(files)} 个文件，API频率限制: {api_rate_limit}/分钟，最大线程数: {max_threads}")
            
            # 获取线程池实例
            thread_pool = get_thread_pool(
                api_rate_limit=api_rate_limit,
                max_threads=max_threads
            )
            
            # 启动线程池
            thread_pool.start()
            
            # 定义文件处理函数
            def process_file(file_path):
                log_yellow(f"开始处理文件: {os.path.basename(file_path)}")
                try:
                    # 分析单个文件
                    result = self.analyze_file(file_path)
                    log_green(f"完成分析文件: {os.path.basename(file_path)}")
                    return result
                except Exception as e:
                    error_msg = str(e)
                    log_red(f"处理文件时发生异常: {os.path.basename(file_path)} - {error_msg}")
                    return {
                        'file': file_path,
                        'success': False,
                        'error': error_msg
                    }
            
            try:
                # 添加所有任务到线程池
                for file in files:
                    thread_pool.add_task(process_file, file)
                
                # 等待所有任务完成
                while thread_pool.task_queue.unfinished_tasks > 0:
                    # 每1秒检查一次任务完成情况
                    time.sleep(1)
                
                # 获取结果
                results = thread_pool.get_results()
                
                # 分析完成后，对整个分析目录应用权限
                try:
                    logger.info("对分析结果目录应用权限...")
                    os.system("chmod -R 777 data")
                    os.system("sync")
                    logger.info("分析结果目录权限设置完成")
                    time.sleep(1)
                except Exception as e:
                    logger.warning(f"设置分析结果目录权限失败: {e}")
                
                # 确认所有元数据都已正确保存
                logger.info("正在确认元数据完整性...")
                try:
                    # 最终确认一次元数据更新，确保所有线程的更改都被保存
                    with self.metadata_lock:
                        metadata = self._load_metadata()
                        
                        # 验证所有分析的文件是否都有元数据记录
                        processed_files = [result.get('file') for result in results if 'file' in result]
                        logger.info(f"已处理文件数: {len(processed_files)}")
                        logger.info(f"元数据记录数: {len(metadata)}")
                        
                        missing_records = []
                        for file_path in processed_files:
                            normalized_path = self._normalize_file_path(file_path)
                            if normalized_path not in metadata:
                                missing_records.append(normalized_path)
                                logger.warning(f"缺失元数据记录: {normalized_path}")
                        
                        if missing_records:
                            logger.warning(f"发现 {len(missing_records)} 个文件缺失元数据记录")
                        else:
                            logger.info("所有文件的元数据记录完整")
                        
                        # 重新保存元数据文件确保完整性
                        self._save_metadata(metadata)
                        logger.info(f"元数据最终确认完成，共 {len(metadata)} 条记录")
                except Exception as e:
                    logger.error(f"元数据完整性确认失败: {e}")
                    logger.exception("详细错误信息:")
                
                # 关闭线程池 - 确保在正常流程结束时也关闭线程池
                logger.info("任务完成，正在关闭线程池...")
                thread_pool.shutdown(wait=True)
                
                return results
                
            except KeyboardInterrupt:
                logger.warning("用户中断操作，正在优雅地关闭线程池...")
                # 关闭线程池
                thread_pool.shutdown(wait=True)
                raise
                
            except Exception as e:
                logger.error(f"动态线程池执行过程中发生异常: {e}")
                # 关闭线程池
                thread_pool.shutdown(wait=True)
                # 回退到单线程模式
                logger.info("回退到单线程模式继续执行...")
                return self.run()
        finally:
            # 释放进程锁
            if self.lock_acquired:
                self.process_lock_manager.release_lock()
                logger.info("已释放分析进程锁")
    
    def analyze_all(self) -> bool:
        """
        分析所有原始数据的别名方法
        
        Returns:
            bool: 分析是否成功完成
        """
        # 检查是否使用动态线程池
        use_dynamic = self.ai_config.get('use_dynamic_pool', True)
        
        try:
            if use_dynamic:
                logger.info("使用动态线程池进行分析")
                results = self.run_dynamic()
            else:
                logger.info("使用单线程模式进行分析")
                results = self.run()
            
            # 如果结果为空列表且不是因为没有文件需要分析，则可能是因为无法获取进程锁
            if not results and self._get_files_to_analyze():
                logger.error("分析任务失败，可能是因为无法获取进程锁")
                return False
            
            # 分析成功完成
            return True
        except Exception as e:
            logger.error(f"分析任务异常: {e}")
            logger.exception("详细错误信息:")
            return False
