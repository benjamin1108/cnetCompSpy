import logging
import time
import threading

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
            return wait_time 