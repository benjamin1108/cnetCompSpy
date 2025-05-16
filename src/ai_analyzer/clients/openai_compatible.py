import logging
import requests
import time
import copy
import random
import os

# 从父目录的 exceptions 模块导入
from ..exceptions import APIError, ParseError, AIAnalyzerError # AIAnalyzerError 也可能需要，以防某些地方仍然引用它

logger = logging.getLogger(__name__)

class OpenAICompatibleAI:
    def __init__(self, config):
        self.model_name = config.get('model')
        self.temperature = config.get('temperature')
        self.max_tokens = config.get('max_tokens')
        self.api_key = config.get('api_key')
        self.api_base = config.get('api_base')
        
        self.system_prompt = config.get('system_prompt', '') 
        if not self.system_prompt:
            logger.warning("OpenAICompatibleAI 初始化时未收到有效的系统提示文本，系统提示将为空。")
        else:
            logger.debug(f"OpenAICompatibleAI 使用的系统提示长度: {len(self.system_prompt)} 字符")

        # Debug mode for logging full prompt
        self.log_full_prompt_enabled = config.get('log_full_prompt', False)
        if self.log_full_prompt_enabled:
            logger.info(f"OpenAICompatibleAI: 完整提示日志功能已为模型 '{self.model_name}' 开启。实际提示将在请求构建时记录。")

        model_params = config.get('model_params', {})
        self.enable_search = model_params.get('enable_search', True) 
        logger.info(f"OpenAICompatibleAI 模型参数 enable_search 设置为: {self.enable_search}")
        
        if not self.api_key or not self.api_base:
            error_msg = "未提供API密钥或API基础URL，无法初始化AI模型"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.provider = self._identify_provider()
        logger.info(f"已识别API提供商: {self.provider}")
    
    def _identify_provider(self):
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
        logger.debug(f"准备向模型 {self.model_name} (provider: {self.provider}) 发送请求")
        logger.debug(f"提示词长度: {len(prompt)} 字符")
        
        try:
            request_data = self._build_request_data(prompt)
        except Exception as e:
            logger.error(f"构建API请求数据时失败: {e}")
            raise APIError(f"构建API请求数据失败: {e}") from e

        logger.debug(f"请求URL: {request_data['url']}")
        logger.debug(f"请求头: {','.join(request_data['headers'].keys())}")
        logger.debug(f"请求参数: temperature={self.temperature}, max_tokens={self.max_tokens}")
        
        log_payload = copy.deepcopy(request_data["payload"])
        if "messages" in log_payload and isinstance(log_payload["messages"], list):
            for i, msg in enumerate(log_payload["messages"]):
                if "content" in msg and len(msg["content"]) > 100:
                    msg["content"] = msg["content"][:100] + "... [内容已省略]"
        
        logger.info(f"完整请求URL: {request_data['url']}")
        logger.info(f"使用普通请求调用 {self.provider} API")
        
        start_time = time.time()
        session = requests.Session()

        try:
            logger.info(f"开始发送请求: POST {request_data['url']}")
            response = session.post(
                request_data["url"],
                headers=request_data["headers"],
                json=request_data["payload"],
                timeout=300
            )
            request_time = time.time() - start_time
            logger.info(f"API调用完成，耗时: {request_time:.2f}秒")
            logger.info(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                error_message_base = f"API调用失败: HTTP状态码 {response.status_code}"
                if response.status_code in [429, 500, 502, 503, 504]: 
                    logger.warning(f"{error_message_base}. 响应 (前500字符): {response.text[:500]}. 将尝试重试。")
                    try:
                        response.raise_for_status()
                    except requests.exceptions.HTTPError as http_err:
                        logger.error(f"可重试的HTTP错误被封装: {http_err}")
                        raise 
                else: 
                    logger.error(f"{error_message_base}. 响应 (前500字符): {response.text[:500]}. 不可重试。")
                    raise APIError(error_message_base, status_code=response.status_code, response_text=response.text)

        except requests.exceptions.RequestException as e: 
            request_time = time.time() - start_time
            logger.error(f"API请求失败 (耗时 {request_time:.2f}秒): {e}")
            if isinstance(e, (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.TooManyRedirects)) or \
               (isinstance(e, requests.exceptions.HTTPError) and e.response is not None and e.response.status_code in [429, 500, 502, 503, 504]):
                raise 
            else:
                raise APIError(f"API网络请求或非重试HTTP错误: {e}") from e
        
        logger.info(f"API调用成功: 状态码 {response.status_code}")
        
        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"API响应内容不是有效的JSON: {e}. 响应文本 (前500字符): {response.text[:500]}")
            raise APIError(f"API响应内容不是有效的JSON: {e}. 响应: {response.text[:500]}") from e
        
        try:
            result = self._parse_response(response_json)
            logger.info(f"解析后的响应长度: {len(result)} 字符")
            response_preview = result[:50] + "..." if len(result) > 50 else result
            logger.info(f"解析后的响应内容预览: {response_preview}")
            return result
        except ParseError as e: 
            logger.error(f"解析API响应失败: {e}")
            raise APIError(f"解析API响应失败: {e}") from e
        except Exception as e: 
            logger.error(f"调用_parse_response时发生意外错误: {e}")
            raise APIError(f"解析API响应时发生意外内部错误: {e}") from e
    
    def _build_request_data(self, prompt):
        headers = {
            "Content-Type": "application/json"
        }
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        if self.log_full_prompt_enabled:
            logger.info("--- 开始记录完整提示信息 (调试模式) ---")
            for message_item in messages: 
                role = message_item.get("role")
                content = message_item.get("content", "")
                if role == "system":
                    logger.info(f"系统提示 (完整): {content}")
                elif role == "user":
                    logger.info(f"用户提示 (完整): {content}")
                else: # 其他角色 (如果有)
                    logger.info(f"消息 (角色: {role}, 内容完整): {content}")
            logger.info("--- 结束记录完整提示信息 (调试模式) ---")

        if "compatible-mode" in self.api_base.lower() and self.api_base.endswith("chat/completions"):
            url = self.api_base
        elif "compatible-mode" in self.api_base.lower():
            url = f"{self.api_base}/chat/completions"
        else:
            url = f"{self.api_base}/chat/completions"
        
        headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "enable_search": self.enable_search 
        }
        
        return {
            "url": url,
            "headers": headers,
            "payload": payload
        }
    
    def _parse_response(self, response_json):
        try:
            if response_json is None: 
                logger.error("API响应JSON对象为None")
                raise ParseError("API响应JSON对象为None")
            if not response_json: 
                logger.error("API响应为空Json对象 (e.g. {})")
                raise ParseError("API响应为空Json对象")

            logger.debug(f"原始响应 (前200字符): {str(response_json)[:200]}...")

            if self.provider == "aliyun_compatible_full" or self.provider == "aliyun_compatible":
                try:
                    choices = response_json.get('choices')
                    if choices is None:
                        raise ParseError(f"解析 {self.provider} 响应格式错误: 缺少 'choices' 字段")
                    if not isinstance(choices, list) or not choices:
                        raise ParseError(f"解析 {self.provider} 响应格式错误: 'choices' 字段为空列表或非列表")
                    
                    message = choices[0].get('message')
                    if message is None:
                        raise ParseError(f"解析 {self.provider} 响应格式错误: 'choices[0]' 中缺少 'message' 字段")
                    if not isinstance(message, dict):
                        raise ParseError(f"解析 {self.provider} 响应格式错误: 'message' 字段非字典类型")

                    if 'content' not in message:
                        raise ParseError(f"解析 {self.provider} 响应格式错误: 'message' 对象中缺少 'content' 字段")
                    content = message['content']
                    return content 
                except (KeyError, IndexError, AttributeError, TypeError) as e:
                    logger.error(f"解析阿里云兼容模式响应时出现意外错误: {str(e)}")
                    raise ParseError(f"解析阿里云兼容模式响应失败: {str(e)}") from e
            
            elif self.provider == "aliyun":
                try:
                    output = response_json.get('output')
                    if output is None:
                        raise ParseError("解析阿里云原生响应格式错误: 缺少 'output' 字段")
                    if not isinstance(output, dict):
                        raise ParseError("解析阿里云原生响应格式错误: 'output' 字段非字典类型")

                    choices = output.get('choices')
                    if choices is None:
                        raise ParseError("解析阿里云原生响应格式错误: 'output' 对象中缺少 'choices' 字段")
                    if not isinstance(choices, list) or not choices:
                        raise ParseError("解析阿里云原生响应格式错误: 'choices' 字段为空列表或非列表")
                        
                    message = choices[0].get('message')
                    if message is None:
                        raise ParseError("解析阿里云原生响应格式错误: 'choices[0]' 中缺少 'message' 字段")
                    if not isinstance(message, dict):
                        raise ParseError("解析阿里云原生响应格式错误: 'message' 字段非字典类型")

                    if 'content' not in message:
                        raise ParseError("解析阿里云原生响应格式错误: 'message' 对象中缺少 'content' 字段")
                    content = message['content']
                    return content 
                except (KeyError, IndexError, AttributeError, TypeError) as e:
                    logger.error(f"解析阿里云原生响应时出现意外错误: {str(e)}")
                    raise ParseError(f"解析阿里云原生响应失败: {str(e)}") from e
            
            elif self.provider == "baidu":
                try:
                    if 'result' not in response_json:
                        raise ParseError("解析百度响应格式错误: 缺少 'result' 字段")
                    result_text = response_json['result']
                    return result_text 
                except (KeyError, AttributeError, TypeError) as e: 
                    logger.error(f"解析百度响应时出现意外错误: {str(e)}")
                    raise ParseError(f"解析百度响应失败: {str(e)}") from e
            
            elif self.provider == "xfyun":
                try:
                    payload = response_json.get('payload')
                    if payload is None:
                        raise ParseError("解析讯飞响应格式错误: 缺少 'payload' 字段")
                    if not isinstance(payload, dict):
                        raise ParseError("解析讯飞响应格式错误: 'payload' 字段非字典类型")

                    choices = payload.get('choices')
                    if choices is None:
                        raise ParseError("解析讯飞响应格式错误: 'payload' 对象中缺少 'choices' 字段")
                    if not isinstance(choices, list) or not choices:
                        raise ParseError("解析讯飞响应格式错误: 'choices' 字段为空列表或非列表")
                    
                    text_list = choices[0].get('text')
                    if text_list is None:
                        raise ParseError("解析讯飞响应格式错误: 'choices[0]' 中缺少 'text' 字段")
                    if not isinstance(text_list, list): 
                        raise ParseError("解析讯飞响应格式错误: 'text' 字段非列表类型")

                    full_text_content = "".join([item.get('content', '') for item in text_list if isinstance(item, dict)])
                    return full_text_content 

                except (KeyError, IndexError, AttributeError, TypeError) as e:
                    logger.error(f"解析讯飞响应时出现意外错误: {str(e)}")
                    raise ParseError(f"解析讯飞响应失败: {str(e)}") from e
            
            elif self.provider == "xai_grok":
                try:
                    choices = response_json.get('choices')
                    if choices is None:
                        raise ParseError(f"解析 {self.provider} 响应格式错误: 缺少 'choices' 字段")
                    if not isinstance(choices, list) or not choices:
                        raise ParseError(f"解析 {self.provider} 响应格式错误: 'choices' 字段为空列表或非列表")

                    message = choices[0].get('message')
                    if message is None:
                        raise ParseError(f"解析 {self.provider} 响应格式错误: 'choices[0]' 中缺少 'message' 字段")
                    if not isinstance(message, dict):
                        raise ParseError(f"解析 {self.provider} 响应格式错误: 'message' 字段非字典类型")

                    if 'content' not in message:
                        raise ParseError(f"解析 {self.provider} 响应格式错误: 'message' 对象中缺少 'content' 字段")
                    content = message['content']
                    return content 
                except (KeyError, IndexError, AttributeError, TypeError) as e:
                    logger.error(f"解析Grok响应时出现意外错误: {str(e)}")
                    raise ParseError(f"解析Grok响应失败: {str(e)}") from e
            
            else: 
                provider_name_for_log = self.provider if self.provider else "未知 (按OpenAI兼容格式处理)"
                try:
                    choices = response_json.get('choices')
                    if choices is None:
                        raise ParseError(f"解析 {provider_name_for_log} 响应格式错误: 缺少 'choices' 字段")
                    if not isinstance(choices, list) or not choices:
                        raise ParseError(f"解析 {provider_name_for_log} 响应格式错误: 'choices' 字段为空列表或非列表")

                    message = choices[0].get('message')
                    if message is None:
                        raise ParseError(f"解析 {provider_name_for_log} 响应格式错误: 'choices[0]' 中缺少 'message' 字段")
                    if not isinstance(message, dict):
                        raise ParseError(f"解析 {provider_name_for_log} 响应格式错误: 'message' 字段非字典类型")
                        
                    if 'content' not in message: 
                        raise ParseError(f"解析 {provider_name_for_log} 响应格式错误: 'message' 对象中缺少 'content' 字段")
                    content = message['content'] 
                    return content
                except (KeyError, IndexError, AttributeError, TypeError) as e:
                    logger.error(f"解析OpenAI兼容格式响应时 ({provider_name_for_log}) 出现意外错误: {str(e)}")
                    raise ParseError(f"解析OpenAI兼容格式响应失败 ({provider_name_for_log}): {str(e)}") from e
        
        except ParseError: 
            raise
        except Exception as e: 
            logger.error(f"解析响应时发生未预料的顶层异常: {str(e)}")
            logger.debug(f"导致顶层解析异常的原始响应 (前200字符): {str(response_json)[:200]}...")
            raise ParseError(f"解析模型响应过程中发生未知错误: {str(e)}") from e 