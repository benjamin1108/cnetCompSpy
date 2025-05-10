import logging
import requests
import time
import copy
import random
import os # OpenAICompatibleAI._identify_provider 可能用到
# sys # OpenAICompatibleAI 本身不直接用sys.path
from typing import Dict, Any, Optional # ModelManager会用到

# 从新的 exceptions.py 导入异常类
from .exceptions import AIAnalyzerError, ParseError, APIError

# 从新的 clients 子包导入 OpenAICompatibleAI
from .clients.openai_compatible import OpenAICompatibleAI

logger = logging.getLogger(__name__)

class ModelManager:
    """
    模型管理器，负责根据配置实例化和提供模型客户端。
    """
    def __init__(self, ai_config: Dict[str, Any]):
        """
        初始化模型管理器。

        Args:
            ai_config: AI分析器的配置部分 (ai_analyzer.yaml 的内容)。
        """
        self.ai_config = ai_config
        self.model_profiles = ai_config.get('model_profiles', {})
        self.active_model_profile_name = ai_config.get('active_model_profile')

        if not self.model_profiles:
            logger.warning("配置中未找到 \'model_profiles\'。模型管理器可能无法正确实例化模型。")
        if not self.active_model_profile_name:
            logger.warning("配置中未指定 \'active_model_profile\'。将尝试使用第一个可用的模型配置 (如果存在)。")
            if self.model_profiles:
                self.active_model_profile_name = next(iter(self.model_profiles)) # 使用第一个profile的名称
                logger.info(f"自动选择模型配置: \'{self.active_model_profile_name}\'")


    def get_model_client(self, system_prompt_text: str, model_profile_name: Optional[str] = None) -> Any:
        """
        获取（实例化）一个配置好的模型客户端。

        Args:
            system_prompt_text: 要传递给模型客户端的系统提示文本。
            model_profile_name: 要使用的模型配置的名称。如果为None，则使用配置中的 active_model_profile。

        Returns:
            一个实例化的模型客户端 (例如 OpenAICompatibleAI 实例)。

        Raises:
            ValueError: 如果找不到指定的模型配置或配置无效。
            NotImplementedError: 如果模型配置中指定的类型当前不被支持。
        """
        profile_name_to_use = model_profile_name if model_profile_name is not None else self.active_model_profile_name

        if not profile_name_to_use:
            raise ValueError("无法确定要使用的模型配置名称 (未提供且配置中也无默认值)。")

        logger.info(f"尝试获取模型客户端，配置名称: \'{profile_name_to_use}\'")
        
        profile_config = self.model_profiles.get(profile_name_to_use)

        if not profile_config:
            raise ValueError(f"在 \'model_profiles\' 中未找到名为 \'{profile_name_to_use}\' 的模型配置。")

        model_type = profile_config.get('type')
        specific_model_config = profile_config.get('config', {})

        if not model_type:
            raise ValueError(f"模型配置 \'{profile_name_to_use}\' 中缺少 \'type\' 字段。")

        # 将 system_prompt_text 注入到将传递给模型客户端的配置中
        # 创建副本以避免修改原始 self.ai_config 或 self.model_profiles
        client_init_config = specific_model_config.copy() 
        client_init_config['system_prompt'] = system_prompt_text

        # API Key Handling: Prioritize profile.config.api_key, then profile_api_keys from secret.
        if 'api_key' not in client_init_config: # If not in ai_analyzer.yaml's profile.config.api_key
            profile_specific_keys_map = self.ai_config.get('profile_api_keys', {}) 
            api_key_from_secret_map = profile_specific_keys_map.get(profile_name_to_use)
            if api_key_from_secret_map:
                client_init_config['api_key'] = api_key_from_secret_map
                logger.info(f"API key for profile '{profile_name_to_use}' loaded from 'profile_api_keys' (secret config).")
            else:
                # If still not found, we don't set it. OpenAICompatibleAI.__init__ will later check 
                # if it's required and missing, and raise a ValueError there.
                logger.warning(f"API key for profile '{profile_name_to_use}' not found directly in profile config or in 'profile_api_keys'. Model client will proceed without it if optional, or fail if required.")
        else:
            logger.info(f"API key for profile '{profile_name_to_use}' loaded directly from profile config in ai_analyzer.yaml.")

        # Fallback for other essential keys: model, temperature, max_tokens, api_base, model_params.
        # Prioritize profile.config. If not there, fallback to self.ai_config (top-level) for backward compatibility.
        # Note: 'api_key' is handled above and should not be overridden by this general fallback if already set.
        keys_for_top_level_fallback = ['model', 'temperature', 'max_tokens', 'api_base', 'model_params']
        for key in keys_for_top_level_fallback:
            if key not in client_init_config: # If not in profile.config for this key
                value_from_top_level = self.ai_config.get(key) # Check top-level of merged ai_config
                if value_from_top_level is not None:
                    client_init_config[key] = value_from_top_level
                    logger.info(f"Parameter '{key}' for profile '{profile_name_to_use}' set from top-level ai_config (fallback).")

        logger.debug(f"为模型类型 '{model_type}' 准备的配置: {client_init_config}")

        if model_type == "openai_compatible":
            logger.info(f"实例化 OpenAICompatibleAI 模型客户端，使用配置 '{profile_name_to_use}\'。")
            # OpenAICompatibleAI 现在从 .clients.openai_compatible 导入
            return OpenAICompatibleAI(config=client_init_config)
        # elif model_type == "another_model_type":
        #     # return AnotherModelClient(config=client_init_config)
        #     pass
        else:
            logger.error(f"不支持的模型类型: {model_type}")
            raise NotImplementedError(f"模型类型 \'{model_type}\' 当前不被支持。") 