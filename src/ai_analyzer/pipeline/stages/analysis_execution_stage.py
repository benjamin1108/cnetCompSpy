import logging
import os
import time
import re
import json # For potential use, though direct JSON operations might be minimal here
import math # ADDED for math.floor
from typing import Dict, Any, List, Optional
import threading # Added for threading.get_ident()
from tqdm import tqdm # Added for progress bar

from ..pipeline_stage import PipelineStage
from ..pipeline_context import AnalysisContext
from ...exceptions import AIAnalyzerError, APIError # Assuming ParseError might be internal to model client or AI call
from ...retry_strategy import RetryWithExponentialBackoff
from src.utils.thread_pool import get_thread_pool, PreciseRateLimiter
from src.utils.colored_logger import Colors # Keep Colors for other potential direct uses if any, or for context

logger = logging.getLogger(__name__)

# THREAD_DEBUG_COLOR = Colors.BRIGHT_CYAN # REMOVED

class AnalysisExecutionStage(PipelineStage):
    def __init__(self):
        super().__init__(stage_name="AnalysisExecution")

    def _normalize_path_for_metadata(self, file_path: str, context: AnalysisContext) -> str:
        if not context.project_root_dir:
            self.logger.error("Project root directory not set in context. Cannot normalize path correctly for metadata.")
            return os.path.normpath(file_path).replace('\\', '/')
        abs_file_path = os.path.abspath(os.path.normpath(file_path))
        project_root_abs = os.path.abspath(os.path.normpath(context.project_root_dir))
        try:
            relative_path = os.path.relpath(abs_file_path, project_root_abs)
            normalized_relative_path = relative_path.replace('\\', '/')
            self.logger.debug(f"Normalized path for metadata for '{file_path}' (base: '{project_root_abs}') -> '{normalized_relative_path}'")
            return normalized_relative_path
        except ValueError as e:
            self.logger.error(f"Error normalizing path '{abs_file_path}' for metadata relative to '{project_root_abs}': {e}. Falling back to absolute path.")
            return abs_file_path.replace('\\', '/')

    def _extract_embedded_metadata(self, file_content: str) -> Dict[str, Any]:
        metadata = {
            'title': '',
            'original_url': '',
            'crawl_time': '',
            'publish_date': '',  # 新增发布日期字段
            'vendor': '',
            'type': ''
        }
        lines = file_content.split('\n')
        # 增加检查行数到60行，以覆盖AI全文翻译部分
        for line in lines[:60]:
            line_stripped = line.strip()
            if line_stripped.startswith('# ') and not metadata.get('title'):
                metadata['title'] = line_stripped[2:].strip()
            elif line_stripped.startswith('原始链接:') or line_stripped.startswith('**原始链接:**'):
                url_part = line_stripped.split(':', 1)[1].strip()
                url_match = re.search(r'\[(.*?)\]\((.*?)\)', url_part)
                metadata['original_url'] = url_match.group(2) if url_match else url_part
            elif line_stripped.startswith('爬取时间:') or line_stripped.startswith('**爬取时间:**'):
                metadata['crawl_time'] = line_stripped.split(':', 1)[1].strip()
            elif line_stripped.startswith('发布时间:') or line_stripped.startswith('**发布时间:**'):
                metadata['publish_date'] = line_stripped.split(':', 1)[1].strip()
            # 支持"发布于"格式，常见于AI全文翻译部分
            elif line_stripped.startswith('发布于:') or '发布于:' in line_stripped:
                # 提取日期，支持多种格式：2025 年 9 月 17 日 或 2025-09-17
                date_match = re.search(r'发布于[：:]\s*(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日|\d{4}[-/]\d{1,2}[-/]\d{1,2})', line_stripped)
                if date_match:
                    date_str = date_match.group(1).strip()
                    # 转换中文日期格式为标准格式
                    if '年' in date_str:
                        date_str = re.sub(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', r'\1-\2-\3', date_str)
                    metadata['publish_date'] = date_str
            elif line_stripped.startswith('厂商:') or line_stripped.startswith('**厂商:**'):
                metadata['vendor'] = line_stripped.split(':', 1)[1].strip()
            elif line_stripped.startswith('类型:') or line_stripped.startswith('**类型:**'):
                metadata['type'] = line_stripped.split(':', 1)[1].strip()
        
        # 如果没有明确的发布时间，但有爬取时间，则使用爬取时间作为发布时间的后备
        if not metadata['publish_date'] and metadata['crawl_time']:
            metadata['publish_date'] = metadata['crawl_time']
        
        # 清理所有字段中的星号和多余空格
        for key in metadata:
            if isinstance(metadata[key], str):
                # 移除星号和多余空格
                metadata[key] = metadata[key].replace('**', '').replace('*', '').strip()
        
        return metadata

    def _write_metadata_header(self, outfile, embedded_meta: Dict[str, Any]) -> None:
        """
        写入metadata头部到分析文件
        
        Args:
            outfile: 文件对象
            embedded_meta: 从原始文件提取的metadata字典
        """
        if not embedded_meta:
            return
        
        # 按顺序写入metadata字段
        if embedded_meta.get('publish_date'):
            outfile.write(f"**发布时间:** {embedded_meta['publish_date']}\n\n")
        if embedded_meta.get('vendor'):
            outfile.write(f"**厂商:** {embedded_meta['vendor']}\n\n")
        if embedded_meta.get('type'):
            outfile.write(f"**类型:** {embedded_meta['type']}\n\n")
        if embedded_meta.get('original_url'):
            outfile.write(f"**原始链接:** {embedded_meta['original_url']}\n\n")
        
        # 写入分隔线
        outfile.write("---\n\n")
        outfile.flush()

    def _clean_ai_response(self, raw_result: str, task_type: str) -> str:
        cleaned_result = raw_result.strip()
        if task_type == "AI标题翻译":
            explanation_patterns = [
                "Here is the result:", "Here's the result:",
                "Here is the translated title:", "Here's the translated title:",
                "The translated title is:", "Translated title:",
                "Here is my translation:", "Here's my translation:"
            ]
            for pattern in explanation_patterns:
                if pattern in cleaned_result:
                    title_part = cleaned_result.split(pattern, 1)[1].strip()
                    if title_part: return title_part
            if len(cleaned_result.strip().split('\n')) == 1 and len(cleaned_result.strip()) < 100:
                return cleaned_result.strip()
            return cleaned_result
        common_prefixes = [
            "I understand the task. Here is the analysis:",
            "Based on the content, here's the summary:",
            "Here is the information you requested:"
        ]
        for prefix in common_prefixes:
            if cleaned_result.startswith(prefix):
                cleaned_result = cleaned_result[len(prefix):].strip()
                break
        return cleaned_result

    def _perform_ai_analysis_call(
        self, 
        context: AnalysisContext, 
        model_client: Any, 
        full_prompt: str, 
        task_type: str,
        precise_rate_limiter: Optional[PreciseRateLimiter] = None
    ) -> str:
        thread_id = threading.get_ident()
        self.logger.debug(
            f"线程 {thread_id} 开始执行AI调用: 任务='{task_type}', 使用精确限速器={precise_rate_limiter is not None}"
        ) # REMOVED color_override
        max_retries = context.ai_config.get('max_retries', 3)
        initial_delay = context.ai_config.get('initial_retry_delay', 1.0)
        max_delay = context.ai_config.get('max_retry_delay', 60.0)
        retry_strategy = RetryWithExponentialBackoff(
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay
        )
        def api_call():
            if precise_rate_limiter:
                self.logger.debug(f"线程 {thread_id} 等待精确限速器...") # REMOVED color_override
                wait_duration = precise_rate_limiter.wait()
                if wait_duration and wait_duration > 0:
                     self.logger.debug(f"线程 {thread_id} 已等待 {wait_duration:.2f} 秒 (精确限速)") # REMOVED color_override
            self.logger.debug(f"线程 {thread_id} 发送AI请求: 任务='{task_type}' (调用 predict)") # REMOVED color_override
            start_time = time.time()
            response = model_client.predict(full_prompt)
            end_time = time.time()
            self.logger.debug(
                f"线程 {thread_id} 收到AI响应: 任务='{task_type}', 耗时={end_time - start_time:.2f}s"
            ) # REMOVED color_override
            return response
        try:
            result = retry_strategy.execute(api_call)
            return self._clean_ai_response(result, task_type)
        except APIError as e:
            self.logger.error(f"线程 {thread_id} 在任务 '{task_type}' 中遭遇API错误 (已达最大重试次数): {e}") # REMOVED color_override (was on an error before, ensure it's not now)
            raise AIAnalyzerError(f"AI API call failed for task '{task_type}' after multiple retries: {e}") from e
        except Exception as e:
            self.logger.error(f"线程 {thread_id} 在任务 '{task_type}' 的AI调用中发生意外错误: {e}") # REMOVED color_override (was on an error before, ensure it's not now)
            raise AIAnalyzerError(f"Unexpected error during AI call for task '{task_type}': {e}") from e

    def _process_single_file(
        self, 
        file_path: str, 
        context: AnalysisContext,
        precise_rate_limiter: Optional[PreciseRateLimiter] = None
        # task_identifier is implicitly passed via *args to thread pool, but not used by this func signature directly from add_task
    ) -> Dict[str, Any]:
        thread_id = threading.get_ident()
        self.logger.debug(f"开始处理文件: {file_path} (线程ID: {thread_id})") # MODIFIED message, REMOVED color_override
        normalized_path_key = self._normalize_path_for_metadata(file_path, context)
        file_summary = {
            'file_path': file_path,
            'normalized_key': normalized_path_key,
            'status': 'pending',
            'embedded_metadata': {},
            'task_results': {},
            'error': None
        }
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.logger.debug(f"已读取 {len(content)} 字符从 {file_path}") # REMOVED color_override
            embedded_meta = self._extract_embedded_metadata(content)
            file_summary['embedded_metadata'] = embedded_meta
            if not context.analysis_output_dir or not context.raw_data_dir:
                raise AIAnalyzerError("Analysis output or raw data directory not configured in context.")
            relative_file_path = os.path.relpath(file_path, context.raw_data_dir)
            analysis_output_file_path = os.path.join(context.analysis_output_dir, relative_file_path)
            os.makedirs(os.path.dirname(analysis_output_file_path), exist_ok=True)
            self.logger.debug(f"分析输出将保存至: {analysis_output_file_path}") # REMOVED color_override
            current_file_tasks_status: Dict[str, Dict[str, Any]] = {}
            analysis_content_for_file: Dict[str,str] = {}
            defined_tasks = context.ai_config.get('tasks', [])
            system_prompt_text = context.prompt_manager.get_system_prompt()
            model_client = context.model_manager.get_model_client(system_prompt_text=system_prompt_text)
            if not model_client:
                 raise AIAnalyzerError(f"未能从ModelManager获取模型客户端 (线程ID: {thread_id})。")
            with open(analysis_output_file_path, 'w', encoding='utf-8') as outfile:
                # 写入metadata头部到分析文档顶部
                self._write_metadata_header(outfile, embedded_meta)
                
                for i, task_config in enumerate(defined_tasks):
                    task_type = task_config.get('type')
                    if not task_type:
                        self.logger.warning(f"跳过没有类型的任务: {task_config}") # REMOVED color_override (was warning color before)
                        continue
                    
                    # 特殊处理AI竞争分析任务：根据标题前缀选择提示词
                    if task_type == "AI竞争分析":
                        # 先检查是否已经有标题翻译结果
                        title_translation = analysis_content_for_file.get("AI标题翻译", "").strip()
                        if title_translation:
                            task_prompt_text = context.prompt_manager.get_competitive_analysis_prompt(title_translation)
                            self.logger.info(f"根据标题前缀选择竞争分析提示词: {title_translation[:50]}...")
                        else:
                            # 如果没有标题翻译结果，使用默认的竞争分析提示词
                            task_prompt_text = context.prompt_manager.get_task_prompt(task_type)
                            self.logger.warning(f"未找到标题翻译结果，使用默认竞争分析提示词")
                    else:
                        task_prompt_text = context.prompt_manager.get_task_prompt(task_type)
                    
                    if not task_prompt_text:
                        self.logger.warning(f"因prompt为空跳过任务 '{task_type}' 。") # REMOVED color_override (was warning color before)
                        current_file_tasks_status[task_type] = {'success': False, 'error': 'Empty prompt', 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}
                        continue
                    self.logger.info(f"执行任务 [{i+1}/{len(defined_tasks)}]: {task_type} for file {file_path}") # REMOVED color_override
                    full_ai_prompt = f"{task_prompt_text}\n\n--- FILE CONTENT BELOW ---\n{content}"
                    task_status_entry = {'success': False, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}
                    try:
                        raw_ai_result = self._perform_ai_analysis_call(
                            context, model_client, full_ai_prompt, task_type, precise_rate_limiter
                        )
                        error_prefixes = ["API调用失败:", "API调用或重试机制失败:", "分析内容时发生意外错误:"]
                        if any(raw_ai_result.startswith(prefix) for prefix in error_prefixes) or len(raw_ai_result.strip()) < 5:
                            raise AIAnalyzerError(f"AI analysis for task '{task_type}' returned error or invalid result: {raw_ai_result}")
                        cleaned_result = self._clean_ai_response(raw_ai_result, task_type)
                        analysis_content_for_file[task_type] = cleaned_result
                        task_status_entry['success'] = True
                        should_output_to_file = task_config.get('output', True)
                        if task_type == "AI标题翻译" or should_output_to_file:
                            outfile.write(f"\n<!-- AI_TASK_START: {task_type} -->\n")
                            outfile.write(f"{cleaned_result}\n")
                            outfile.write(f"<!-- AI_TASK_END: {task_type} -->\n\n")
                            outfile.flush()
                    except Exception as e:
                        self.logger.error(f"在任务 '{task_type}' (文件 '{file_path}') 中发生错误: {e}", exc_info=True)
                        task_status_entry['error'] = str(e)
                        should_output_to_file = task_config.get('output', True)
                        if task_type == "AI标题翻译" or should_output_to_file:
                            sanitized_error_message = str(e).replace('-->', '--&gt;').replace('<!--', '&lt;!--')
                            error_message_for_file = f"<!-- ERROR: {sanitized_error_message} -->"
                            outfile.write(f"\n<!-- AI_TASK_START: {task_type} -->\n")
                            outfile.write(f"{error_message_for_file}\n")
                            outfile.write(f"<!-- AI_TASK_END: {task_type} -->\n\n")
                            outfile.flush()
                    current_file_tasks_status[task_type] = task_status_entry
            with context.metadata_lock:
                if normalized_path_key not in context.metadata:
                    context.metadata[normalized_path_key] = {'file': normalized_path_key}
                context.metadata[normalized_path_key]['info'] = embedded_meta
                
                # 从分析内容中提取中文标题（如果有）
                if analysis_content_for_file.get("AI标题翻译"):
                    raw_chinese_title = analysis_content_for_file["AI标题翻译"].strip()
                    
                    # 提取方括号内的标签作为 update_type
                    update_type_match = re.match(r'^\[(.*?)\]', raw_chinese_title)
                    if update_type_match:
                        update_type = update_type_match.group(1).strip()
                        # 使用正则表达式移除标题头部的如 "[标签]" 部分作为 chinese_title
                        pure_chinese_title = re.sub(r'^\[.*?\]\s*', '', raw_chinese_title).strip()
                    else:
                        update_type = "" # 如果没有匹配到标签，则 update_type 为空
                        pure_chinese_title = raw_chinese_title # chinese_title 就是原始标题

                    # 将提取的 update_type 和处理后的中文标题添加到info字段
                    context.metadata[normalized_path_key]['info']['update_type'] = update_type
                    context.metadata[normalized_path_key]['info']['chinese_title'] = pure_chinese_title
                    
                    # 记录到日志
                    self.logger.debug(f"提取到 update_type: '{update_type}', chinese_title: '{pure_chinese_title}' (文件: {file_path})")
                
                if embedded_meta.get('publish_date'):
                    context.metadata[normalized_path_key]['publish_date'] = embedded_meta['publish_date']
                context.metadata[normalized_path_key]['tasks'] = current_file_tasks_status
                context.metadata[normalized_path_key]['last_analyzed'] = time.strftime('%Y-%m-%d %H:%M:%S')
                context.metadata[normalized_path_key].pop('last_error', None)
            file_summary['status'] = 'completed'
            file_summary['task_results'] = analysis_content_for_file
            self.logger.info(f"成功处理文件: {file_path}") # REMOVED color_override
        except Exception as e:
            self.logger.error(f"处理文件 '{file_path}' 失败: {e}", exc_info=True)
            file_summary['status'] = 'failed'
            file_summary['error'] = str(e)
            with context.metadata_lock:
                if normalized_path_key not in context.metadata:
                     context.metadata[normalized_path_key] = {'file': normalized_path_key}
                # 如果有提取到嵌入式元数据，即使出错也保存
                if file_summary.get('embedded_metadata') and file_summary['embedded_metadata'].get('publish_date'):
                    context.metadata[normalized_path_key]['info'] = file_summary['embedded_metadata']
                    context.metadata[normalized_path_key]['publish_date'] = file_summary['embedded_metadata']['publish_date']
                
                # 如果成功生成了中文标题，即使其他任务失败也保存
                if file_summary.get('task_results') and file_summary['task_results'].get('AI标题翻译'):
                    if 'info' not in context.metadata[normalized_path_key]:
                        context.metadata[normalized_path_key]['info'] = {}
                    context.metadata[normalized_path_key]['info']['chinese_title'] = file_summary['task_results']['AI标题翻译'].strip()
                    self.logger.debug(f"即使处理失败，也将中文标题保存到元数据 (文件: {file_path})")
                
                context.metadata[normalized_path_key]['last_error'] = str(e)
                context.metadata[normalized_path_key]['last_error_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        self.logger.debug(f"完成文件处理: {file_path}, 状态: {file_summary['status']}") # REMOVED color_override
        return file_summary

    def execute(self, context: AnalysisContext) -> AnalysisContext:
        self.logger.info(f"开始执行 {self.stage_name} 阶段...") # REMOVED color_override
        context.analysis_results = []
        if not context.lock_acquired:
            self.logger.warning("分析进程锁未获取，跳过分析执行阶段。")
            return context
        if not context.files_to_analyze:
            self.logger.info("没有文件需要分析。")
            return context
        self.logger.info(f"准备分析 {len(context.files_to_analyze)} 个文件...") # REMOVED color_override
        use_dynamic_pool = context.ai_config.get('use_dynamic_pool', True)
        if use_dynamic_pool:
            max_workers = context.ai_config.get('max_workers', 4)
            initial_workers = context.ai_config.get('initial_workers', min(2, max_workers))
            api_requests_per_minute = context.ai_config.get('api_rate_limit', 0) # This is the overall per-minute target
            self.logger.info(f"使用 AdaptiveThreadPool 执行，初始线程: {initial_workers}, 最大线程: {max_workers}, API每分钟限制配置: {api_requests_per_minute}/分钟")
            
            execution_settings = context.ai_config.get('execution_settings', {})
            shutdown_join_timeout_seconds = execution_settings.get('thread_pool_shutdown_join_timeout')
            
            # NEW: Configure PreciseRateLimiter with burst control window
            api_call_burst_window_seconds = execution_settings.get('api_call_burst_window_seconds', 5) # Default to 5s if not configured
            if not isinstance(api_call_burst_window_seconds, int) or api_call_burst_window_seconds <= 0:
                self.logger.warning(f"配置的 api_call_burst_window_seconds ('{api_call_burst_window_seconds}') 无效，将使用默认值 5 秒。")
                api_call_burst_window_seconds = 5

            shared_precise_rate_limiter: Optional[PreciseRateLimiter] = None
            if api_requests_per_minute > 0:
                # Calculate max_calls for the burst window based on the per-minute rate
                # Ensure at least 1 call is allowed in the window if rate is very low but positive.
                calls_per_second_float = api_requests_per_minute / 60.0
                max_calls_for_burst_window = math.floor(calls_per_second_float * api_call_burst_window_seconds)
                max_calls_for_burst_window = max(1, max_calls_for_burst_window) # Ensure at least 1
                
                shared_precise_rate_limiter = PreciseRateLimiter(
                    max_calls=max_calls_for_burst_window, 
                    window_seconds=api_call_burst_window_seconds
                )
                self.logger.info(f"为AI调用创建共享 PreciseRateLimiter: 每 {api_call_burst_window_seconds} 秒最多 {max_calls_for_burst_window} 次调用 (基于 {api_requests_per_minute}/分钟 总速率配置)。")
            else:
                self.logger.warning("API速率限制未配置或为0 (api_rate_limit), AI调用将不被外部精确限速器限制。")
            
            # AdaptiveThreadPool's own rate_limiter is for its internal metrics, not task throttling.
            # The api_rate_limit passed to get_thread_pool is for that internal limiter.
            thread_pool_api_rate_config = api_requests_per_minute if api_requests_per_minute > 0 else 60 # Default for pool's internal monitor

            thread_pool_kwargs = {
                'api_rate_limit': thread_pool_api_rate_config,
                'max_threads': max_workers,
                'force_new': True
            }
            if shutdown_join_timeout_seconds is not None:
                try:
                    timeout_val = int(shutdown_join_timeout_seconds)
                    if timeout_val > 0:
                        thread_pool_kwargs['shutdown_join_timeout'] = timeout_val
                        self.logger.info(f"线程池关闭超时将使用配置值: {timeout_val}s")
                    else:
                        self.logger.warning(f"配置的 thread_pool_shutdown_join_timeout ({shutdown_join_timeout_seconds}) 不是正数，将使用默认超时。")
                except ValueError:
                    self.logger.warning(f"配置的 thread_pool_shutdown_join_timeout ('{shutdown_join_timeout_seconds}') 不是有效的整数，将使用默认超时。")
            else:
                self.logger.info("未在配置中找到 thread_pool_shutdown_join_timeout，线程池将使用其默认关闭超时。")

            adaptive_thread_pool = get_thread_pool(**thread_pool_kwargs)
            self.logger.debug(f"AdaptiveThreadPool 实例已获取/创建: {adaptive_thread_pool}") # REMOVED color_override
            submitted_tasks_count = 0
            for file_idx, file_path in enumerate(context.files_to_analyze):
                # Create a task identifier that includes the file name for better logging in the thread pool
                task_identifier = f"AI Analysis for {os.path.basename(file_path)}"
                self.logger.debug(f"提交任务 {file_idx+1}/{len(context.files_to_analyze)} ({task_identifier}) 到 AdaptiveThreadPool") # REMOVED color_override
                # The add_task in provided AdaptiveThreadPool snippet doesn't take task_identifier yet.
                # Assuming it will be modified to accept it as a keyword argument.
                success = adaptive_thread_pool.add_task(
                    self._process_single_file,
                    file_path, 
                    context,
                    shared_precise_rate_limiter,
                    task_identifier=task_identifier # Pass the identifier
                )
                if success:
                    submitted_tasks_count +=1
            self.logger.info(f"已提交 {submitted_tasks_count} 个文件分析任务到 AdaptiveThreadPool。等待任务完成...") # REMOVED color_override
            if hasattr(adaptive_thread_pool, 'shutdown') and callable(getattr(adaptive_thread_pool, 'shutdown')):
                adaptive_thread_pool.shutdown(wait=True)
            self.logger.info("AdaptiveThreadPool 所有任务已处理完毕。获取结果...") # REMOVED color_override
            raw_results = []
            if hasattr(adaptive_thread_pool, 'get_results') and callable(getattr(adaptive_thread_pool, 'get_results')):
                raw_results = adaptive_thread_pool.get_results()
            completed_count = 0
            failed_count = 0
            for file_result_summary in raw_results:
                if isinstance(file_result_summary, dict):
                    context.analysis_results.append(file_result_summary)
                    if file_result_summary.get('status') == 'failed':
                        failed_count += 1
                    else:
                        completed_count += 1
                else:
                    self.logger.error(f"从线程池收到意外的结果类型: {type(file_result_summary)}, 内容: {str(file_result_summary)[:200]}") # REMOVED color_override
                    failed_count +=1
            self.logger.info(f"AdaptiveThreadPool 处理完成。理论提交: {submitted_tasks_count}. 收到结果: {len(raw_results)}. 成功处理（基于结果状态）: {completed_count}, 失败: {failed_count}") # REMOVED color_override
        else:
            self.logger.info("使用串行执行模式。") # REMOVED color_override
            if api_requests_per_minute > 0 :
                # Calculate max_calls for the burst window based on the per-minute rate for serial execution too
                execution_settings = context.ai_config.get('execution_settings', {})
                api_call_burst_window_seconds = execution_settings.get('api_call_burst_window_seconds', 5) # Default to 5s
                if not isinstance(api_call_burst_window_seconds, int) or api_call_burst_window_seconds <= 0:
                    api_call_burst_window_seconds = 5 # Fallback
                
                calls_per_second_float = api_requests_per_minute / 60.0
                max_calls_for_burst_window = math.floor(calls_per_second_float * api_call_burst_window_seconds)
                max_calls_for_burst_window = max(1, max_calls_for_burst_window)

                serial_precise_rate_limiter = PreciseRateLimiter(
                    max_calls=max_calls_for_burst_window,
                    window_seconds=api_call_burst_window_seconds
                )
                self.logger.info(f"为串行执行创建 PreciseRateLimiter: 每 {api_call_burst_window_seconds} 秒最多 {max_calls_for_burst_window} 次调用 (基于 {api_requests_per_minute}/分钟 总速率配置)。")
            current_thread_id = threading.get_ident()
            for file_path_idx, file_path in enumerate(tqdm(context.files_to_analyze, desc="串行分析文件", unit="file")):
                self.logger.info(f"线程 {current_thread_id} (主) 串行处理文件 {file_path_idx+1}/{len(context.files_to_analyze)}: {file_path}") # REMOVED color_override
                file_result_summary = self._process_single_file(file_path, context, serial_precise_rate_limiter)
                context.analysis_results.append(file_result_summary)
                if file_result_summary['status'] == 'failed':
                     self.logger.error(f"线程 {current_thread_id} (主) 文件 '{file_path}' (串行)分析失败: {file_result_summary.get('error')}") # REMOVED color_override
        self.logger.info(f"分析执行阶段完成。共获得 {len(context.analysis_results)} 个文件结果。") # REMOVED color_override
        return context 