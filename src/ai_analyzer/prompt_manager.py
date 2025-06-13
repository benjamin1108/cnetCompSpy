import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class PromptManager:
    """
    管理系统提示和任务特定提示的加载。
    """
    def __init__(self, prompt_settings: Dict[str, Any], project_root_dir: str):
        """
        初始化 PromptManager。

        Args:
            prompt_settings: 从配置中获取的 'prompt_settings' 部分。
            project_root_dir: 项目的根目录，用于解析相对路径的prompt文件。
        """
        self.prompt_settings = prompt_settings
        self.project_root_dir = project_root_dir

        self.prompt_root_dir_name: str = self.prompt_settings.get('prompt_root_dir', 'prompt')
        # 构建 prompt 根目录的绝对路径
        self.absolute_prompt_root_dir = os.path.join(self.project_root_dir, self.prompt_root_dir_name)
        
        self.system_prompt_filename: str = self.prompt_settings.get('system_prompt_filename', 'system_prompt.txt')
        self.default_system_prompt_text: str = self.prompt_settings.get(
            'default_system_prompt_text', 
            "你是专业的AI助手。" # 更通用的默认提示
        )
        
        self.task_prompt_map: Dict[str, str] = self.prompt_settings.get('task_prompt_map', {})
        
        self._prompts_cache: Dict[str, str] = {} # 用于缓存任务提示

        self.system_prompt: str = self._load_system_prompt()
        logger.info(f"PromptManager 初始化完成。Prompt根目录: '{self.absolute_prompt_root_dir}'")
        logger.info(f"系统提示已加载 (来自文件: '{self.system_prompt_filename}', 长度: {len(self.system_prompt)}).")

    def _load_file_content(self, filename: str) -> str:
        """
        从相对于 self.absolute_prompt_root_dir 的路径加载文件内容。

        Args:
            filename: 文件名 (例如 "system_prompt.txt" 或 "task_specific.txt")

        Returns:
            文件内容，如果文件不存在或加载失败则返回空字符串。
        """
        if not filename:
            logger.warning("尝试加载空的prompt文件名，跳过加载。")
            return ""

        prompt_path = os.path.join(self.absolute_prompt_root_dir, filename)
        
        if not os.path.exists(prompt_path):
            logger.warning(f"Prompt文件不存在: {prompt_path}")
            return ""
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip() # 通常 prompt 文件末尾的换行符不需要
                logger.debug(f"已加载prompt文件: {prompt_path}, 大小: {len(content)} 字符")
                return content
        except Exception as e:
            logger.error(f"加载prompt文件 '{prompt_path}' 时出错: {e}")
            return ""

    def _load_system_prompt(self) -> str:
        """加载系统提示词。"""
        content = self._load_file_content(self.system_prompt_filename)
        if not content:
            logger.warning(
                f"系统提示文件 '{self.system_prompt_filename}' 加载失败或为空，将使用默认系统提示。"
            )
            return self.default_system_prompt_text
        return content

    def get_system_prompt(self) -> str:
        """获取已加载的系统提示词。"""
        return self.system_prompt

    def _get_task_prompt_filename(self, task_type: str) -> str:
        """
        根据任务类型获取对应的prompt文件名。
        优先从配置的映射中查找，然后使用后备逻辑。
        """
        if task_type in self.task_prompt_map and self.task_prompt_map[task_type]:
            filename = self.task_prompt_map[task_type]
            logger.debug(f"任务 '{task_type}' 在配置的task_prompt_map中找到Prompt文件: '{filename}'")
            return filename
        
        fallback_filename = task_type.lower().replace(" ", "_") + ".txt"
        logger.debug(f"任务 '{task_type}' 在配置的task_prompt_map中未找到或为空，使用后备文件名逻辑: '{fallback_filename}'")
        return fallback_filename

    def get_task_prompt(self, task_type: str) -> str:
        """
        获取指定任务类型的prompt内容。
        会优先从缓存中读取，如果未缓存则加载并存入缓存。
        """
        if task_type in self._prompts_cache:
            logger.debug(f"从缓存中获取任务 '{task_type}' 的Prompt。")
            return self._prompts_cache[task_type]

        filename = self._get_task_prompt_filename(task_type)
        prompt_content = self._load_file_content(filename)
        
        if not prompt_content:
            logger.warning(f"任务 '{task_type}' (文件: '{filename}') 的Prompt加载失败或为空。")
            # 根据需求，这里可以返回一个默认的任务提示，或就是空字符串
        
        self._prompts_cache[task_type] = prompt_content # 即使为空也缓存，避免重复加载尝试
        logger.debug(f"任务 '{task_type}' (文件: '{filename}') 的Prompt已加载并缓存，长度: {len(prompt_content)}.")
        return prompt_content

    def validate_task_prompts(self, defined_tasks: List[Dict[str, Any]]):
        """
        验证在配置中定义的任务是否有对应的、可加载的prompt。
        主要用于启动时检查和日志记录。

        Args:
            defined_tasks: 从主配置中获取的任务列表 (例如 analyzer.tasks)
        """
        if not defined_tasks:
            logger.info("没有定义具体的分析任务 (defined_tasks 为空)，跳过Prompt校验。")
            return

        logger.info(f"开始校验 {len(defined_tasks)} 个已定义任务的Prompt文件...")
        all_valid = True
        for task_config in defined_tasks:
            task_type = task_config.get('type')
            if not task_type:
                logger.warning(f"在 defined_tasks 中发现一个没有'type'的任务配置: {task_config}")
                continue
            
            # 这里调用 get_task_prompt 会触发加载和缓存机制
            prompt_content = self.get_task_prompt(task_type)
            filename = self._get_task_prompt_filename(task_type) # 获取用于日志的文件名

            if not prompt_content:
                logger.warning(f"[校验失败] 任务 '{task_type}' 对应的Prompt文件 '{filename}' (路径: {os.path.join(self.absolute_prompt_root_dir, filename)}) 未能成功加载或内容为空。")
                all_valid = False
            else:
                logger.info(f"[校验成功] 任务 '{task_type}' (文件: '{filename}') Prompt已成功加载。")
        
        if all_valid:
            logger.info("所有已定义任务的Prompt文件均已校验通过。")
        else:
            logger.warning("部分任务的Prompt文件校验失败或内容为空，请检查日志和相关prompt文件。")

    def get_competitive_analysis_prompt(self, title_with_prefix: str) -> str:
        """
        根据标题前缀选择合适的竞争分析提示词。
        
        Args:
            title_with_prefix: 带前缀的标题，如 "[解决方案] 标题内容" 或 "[新产品/新功能] 标题内容"
            
        Returns:
            对应的竞争分析提示词内容
        """
        if not title_with_prefix:
            logger.warning("标题为空，使用默认竞争分析提示词")
            return self.get_task_prompt("AI竞争分析")
        
        # 检查标题前缀
        if title_with_prefix.startswith("[解决方案]"):
            prompt_filename = "solution_analysis.txt"
            logger.debug(f"检测到解决方案类标题，使用提示词文件: {prompt_filename}")
        elif title_with_prefix.startswith("[新产品/新功能]"):
            prompt_filename = "product_feature_analysis.txt"
            logger.debug(f"检测到新产品/新功能类标题，使用提示词文件: {prompt_filename}")
        else:
            logger.warning(f"未识别的标题前缀: {title_with_prefix[:50]}..., 使用默认竞争分析提示词")
            return self.get_task_prompt("AI竞争分析")
        
        # 直接加载对应的提示词文件
        prompt_content = self._load_file_content(prompt_filename)
        if not prompt_content:
            logger.warning(f"加载竞争分析提示词文件 '{prompt_filename}' 失败，使用默认竞争分析提示词")
            return self.get_task_prompt("AI竞争分析")
        
        return prompt_content

    def preload_all_task_prompts(self, defined_tasks: List[Dict[str, Any]]):
        """
        预加载所有已定义任务的prompts到缓存。
        """
        logger.info("开始预加载所有已定义任务的Prompts...")
        self.validate_task_prompts(defined_tasks) # validate 会顺便加载
        logger.info("所有已定义任务的Prompts预加载完成。") 