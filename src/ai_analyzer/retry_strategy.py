import logging
import time
import requests # For requests.exceptions
import random

# 导入 APIError 以便在 except 子句中使用
from .exceptions import APIError

logger = logging.getLogger(__name__)

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
        retryable_status_codes = [429, 500, 502, 503, 504] # 定义可重试的HTTP状态码

        for retry_count in range(self.max_retries + 1):
            try:
                if retry_count > 0:
                    logger.warning(f"第 {retry_count}/{self.max_retries} 次重试API调用...")
                return func(*args, **kwargs)
            # 将 APIError 添加到捕获列表，并优先于更通用的 RequestException 进行检查
            except APIError as e:
                last_exception = e
                is_retryable = False
                if hasattr(e, 'status_code') and e.status_code in retryable_status_codes:
                    is_retryable = True
                    logger.warning(f"捕获到可重试的 APIError (状态码: {e.status_code}): {e}")
                else:
                    status_code_info = f"状态码: {e.status_code}" if hasattr(e, 'status_code') else "无状态码"
                    logger.error(f"捕获到不可重试的 APIError ({status_code_info}): {e}. 将不会重试。")
                    raise # 直接重新抛出不可重试的 APIError

                # 如果到这里，说明是可重试的 APIError
                if retry_count == self.max_retries:
                    logger.error(f"APIError: 达到最大重试次数 {self.max_retries} (状态码: {e.status_code if hasattr(e, 'status_code') else 'N/A'})，放弃重试")
                    raise
                
                # 记录错误和重试信息 (通用部分)
                error_code_str = str(e.status_code) if hasattr(e, 'status_code') and e.status_code is not None else "APIError (无状态码)"

            except (requests.exceptions.RequestException, requests.exceptions.HTTPError, \
                    requests.exceptions.ConnectionError, requests.exceptions.Timeout,\
                    requests.exceptions.TooManyRedirects) as e:
                last_exception = e
                # 对于 requests.exceptions，我们假设它们本质上是可重试的网络相关问题
                # 或者 HTTPError (如果 predict 抛出) 已经是可重试类型
                logger.warning(f"捕获到可重试的 RequestException: {e}")
                if retry_count == self.max_retries:
                    logger.error(f"RequestException: 达到最大重试次数 {self.max_retries}，放弃重试")
                    raise
                
                error_code_str = "未知网络或HTTP错误"
                if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'status_code'):
                    error_code_str = str(e.response.status_code)
                elif hasattr(e, 'status_code') and e.status_code is not None: 
                    error_code_str = str(e.status_code)
            
            # 如果代码执行到这里，说明发生了可重试的异常 (APIError 或 RequestException)
            # 并且尚未达到最大重试次数。执行通用重试逻辑。
            if last_exception: # 确保 last_exception 已被设置
                error_msg_for_log = str(last_exception)
                logger.warning(f"API请求失败 (错误码: {error_code_str}): {error_msg_for_log}")
                logger.warning(f"等待 {delay:.2f} 秒后重试...")
                
                time.sleep(delay)
                
                delay = min(delay * 2, self.max_delay)
                
                jitter = delay * 0.1 # Apply jitter after doubling and capping
                delay = max(self.initial_delay / 2, delay + random.uniform(-jitter, jitter)) # Ensure delay doesn't become too small
            else:
                # 理论上不应到达这里，因为如果 try 成功，会直接 return
                # 如果 except 块被执行，last_exception 会被设置
                # 但为保险起见：
                logger.error("重试逻辑中出现意外情况，last_exception 未设置但仍在循环中。")
                break # 退出重试循环


        if last_exception:
            raise last_exception
        else:
            # This path should ideally not be reached if max_retries >= 0 and func always raises on error or returns.
            raise RuntimeError("所有重试都失败了，但没有捕获到异常信息或函数意外正常返回 (RetryWithExponentialBackoff)") 