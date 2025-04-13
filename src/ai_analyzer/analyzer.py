#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import glob
import json
import requests
import sys
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import yaml
from copy import deepcopy
import re
import copy

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

logger = logging.getLogger(__name__)

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
        self.api_key = self.ai_config.get('api_key', '')
        self.api_base = self.ai_config.get('api_base', '')
        self.system_prompt = self.ai_config.get('system_prompt', "你是一个专业的云计算技术分析师，擅长分析和解读各类云计算技术文档。")
        self.tasks = self.ai_config.get('tasks', [])
        self.raw_dir = 'data/raw'
        self.analysis_dir = 'data/analysis'
        
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
                    logger.info(f"请求头详情: {json.dumps(request_data['headers'], indent=2)}")
                    logger.info(f"请求体详情(已简化): {json.dumps(log_payload, indent=2)}")
                    
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
                    logger.info(f"响应头: {json.dumps(dict(response.headers), indent=2)}")
                    
                    # 处理响应
                    if response.status_code == 200:
                        # 在INFO级别输出原始响应
                        logger.info(f"API调用成功: 状态码 {response.status_code}")
                        logger.info(f"原始响应: {response.text}")
                        
                        # 解析响应
                        result = self._parse_response(response.json())
                        
                        # 直接打印结果
                        print(f"\n\n======= AI响应内容 =======\n{result}\n===========================\n\n")
                        
                        # 在INFO级别输出解析后的结果
                        logger.info(f"解析后的响应长度: {len(result)} 字符")
                        logger.info(f"解析后的响应内容: {result}")
                        
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
                    
                    else:
                        # OpenAI兼容格式
                        return response_json.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                except Exception as e:
                    logger.error(f"解析响应失败: {str(e)}")
                    logger.debug(f"原始响应: {response_json}")
                    return "解析模型响应失败"
        
        return OpenAICompatibleAI(self.ai_config)
    
    def _get_files_to_analyze(self) -> List[str]:
        """
        获取需要分析的文件列表
        
        Returns:
            文件路径列表
        """
        files = []
        # 遍历raw目录下的所有md文件
        for md_file in glob.glob(f"{self.raw_dir}/**/*.md", recursive=True):
            # 检查是否已经分析过
            relative_path = os.path.relpath(md_file, self.raw_dir)
            analysis_file = os.path.join(self.analysis_dir, relative_path)
            
            if not os.path.exists(analysis_file):
                files.append(md_file)
        
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
        logger.info(f"开始分析文件: {file_path}")
        
        try:
            # 读取文件内容
            logger.debug(f"读取文件内容: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"文件内容长度: {len(content)} 字符")
            
            # 获取元数据
            logger.debug(f"提取文件元数据")
            metadata = self._extract_metadata(content)
            logger.debug(f"提取的元数据: {metadata}")
            
            # 准备输出文件
            relative_path = os.path.relpath(file_path, self.raw_dir)
            target_dir = os.path.dirname(os.path.join(self.analysis_dir, relative_path))
            
            # 创建目录并确保权限正确
            self._ensure_dir_with_permissions(target_dir)
            
            md_path = os.path.join(self.analysis_dir, relative_path)
            
            analysis_results = {}
            logger.info(f"将执行 {len(self.tasks)} 个分析任务")
            
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
                    
                    # 保存分析结果到内存
                    analysis_results[task_type] = result
                    
                    # 特殊处理：标题翻译总是需要保存，因为它用于网页标题显示
                    if task_type == "AI标题翻译" or output:
                        # 添加任务开始标记 - 使用特殊的HTML注释作为分隔符
                        task_start = f"\n<!-- AI_TASK_START: {task_type} -->\n"
                        f.write(task_start)
                        f.flush()
                        
                        # 立即写入结果到文件
                        f.write(f"{result}\n")
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
            
            # 设置文件权限 - 使用完全开放的权限以确保Windows可访问
            try:
                # 等待文件系统同步
                time.sleep(0.5)
                os.chmod(md_path, 0o777)  # 所有人可读写执行
                logger.debug(f"设置文件权限: {md_path}")
            except Exception as e:
                logger.warning(f"设置文件权限失败: {e}")
            
            logger.info(f"文件分析完成: {file_path}")
            
            return {
                'file': file_path,
                'metadata': metadata,
                'analysis': analysis_results
            }
            
        except Exception as e:
            logger.error(f"分析文件失败: {file_path} - {e}")
            logger.exception("详细错误信息:")
            return {
                'file': file_path,
                'error': str(e)
            }
    
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
        
        # 简单的元数据提取逻辑
        lines = content.split('\n')
        for line in lines[:20]:  # 只检查前20行
            if line.startswith('# '):
                metadata['title'] = line[2:].strip()
            elif line.startswith('原始链接:'):
                metadata['original_url'] = line[5:].strip()
            elif line.startswith('爬取时间:'):
                metadata['crawl_time'] = line[5:].strip()
            elif line.startswith('厂商:'):
                metadata['vendor'] = line[3:].strip()
            elif line.startswith('类型:'):
                metadata['type'] = line[3:].strip()
        
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
            logger.info(f"[{time.strftime('%H:%M:%S')}] 请求头详情: {json.dumps(request_data['headers'], indent=2)}")
            logger.info(f"[{time.strftime('%H:%M:%S')}] 请求体详情(已简化): {json.dumps(log_payload, indent=2)}")
            
            # 使用普通请求
            logger.info(f"[{time.strftime('%H:%M:%S')}] 使用普通请求调用 {api.provider} API")
            logger.info(f"[{time.strftime('%H:%M:%S')}] 目标URL: {request_data['url']}")
            logger.info(f"[{time.strftime('%H:%M:%S')}] 开始发送请求，等待API响应...")
            
            # 启用HTTP请求详细日志
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True
            
            # 使用会话对象进行更详细的日志记录
            session = requests.Session()
            
            # 发送请求并计时
            request_start = time.time()
            response = session.post(
                request_data["url"],
                headers=request_data["headers"],
                json=request_data["payload"],
                timeout=180  # 增加超时时间
            )
            request_time = time.time() - request_start
            
            # 记录响应信息
            logger.info(f"[{time.strftime('%H:%M:%S')}] 收到API响应，耗时: {request_time:.2f}秒")
            logger.info(f"[{time.strftime('%H:%M:%S')}] 响应状态码: {response.status_code}")
            logger.info(f"[{time.strftime('%H:%M:%S')}] 响应头: {json.dumps(dict(response.headers), indent=2)}")
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"API调用失败: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return error_msg
            
            # 解析结果
            logger.info(f"[{time.strftime('%H:%M:%S')}] API调用成功: 状态码 {response.status_code}")
            logger.info(f"[{time.strftime('%H:%M:%S')}] 响应大小: {len(response.text)} 字节")
            
            # 仅记录响应内容的前100个字符作为预览
            response_preview = response.text[:100] + "..." if len(response.text) > 100 else response.text
            logger.info(f"[{time.strftime('%H:%M:%S')}] 原始响应内容预览: {response_preview}")
            
            # 直接打印原始响应的部分内容
            print(f"\n\n======= 原始API响应预览 =======\n{response.text[:300]}...\n===========================\n\n")
            
            logger.debug(f"[{time.strftime('%H:%M:%S')}] 开始解析响应...")
            
            # 解析响应
            parse_start = time.time()
            result = api._parse_response(response.json())
            parse_time = time.time() - parse_start
            
            # 直接打印解析后的结果前500个字符
            result_preview = result[:500] + "..." if len(result) > 500 else result
            print(f"\n\n======= 解析后的AI响应内容预览 =======\n{result_preview}\n==================================\n\n")
            
            # 记录解析结果信息
            logger.info(f"[{time.strftime('%H:%M:%S')}] 响应解析完成，耗时: {parse_time:.2f}秒")
            logger.info(f"解析后的响应长度: {len(result)} 字符")
            
            # 记录解析结果的前100个字符作为预览
            result_log_preview = result[:100] + "..." if len(result) > 100 else result
            logger.info(f"解析后的响应内容预览: {result_log_preview}")
            
            # 返回原始结果，不进行任何格式化
            logger.info(f"[{time.strftime('%H:%M:%S')}] {task_type} 响应接收完成，总长度: {len(result)} 字符")
            if len(result) > 50:
                logger.debug(f"响应前50个字符预览: {result[:50]}...")
            
            return result
            
        except Exception as e:
            error_msg = f"API调用异常: {str(e)}"
            logger.error(f"[{time.strftime('%H:%M:%S')}] {error_msg}")
            logger.exception("详细错误信息:")
            return error_msg
    
    def run(self) -> List[Dict[str, Any]]:
        """
        运行分析
        
        Returns:
            分析结果列表
        """
        # 获取需要分析的文件
        files = self._get_files_to_analyze()
        if not files:
            logger.info("没有需要分析的新文件")
            return []
        
        results = []
        max_workers = self.config.get('ai_analyzer', {}).get('max_workers', 2)
        
        # 使用线程池并行处理文件
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.analyze_file, file): file 
                for file in files
            }
            
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
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
    
    def analyze_all(self) -> List[Dict[str, Any]]:
        """
        分析所有原始数据的别名方法
        
        Returns:
            List[Dict[str, Any]]: 分析结果列表
        """
        return self.run() 