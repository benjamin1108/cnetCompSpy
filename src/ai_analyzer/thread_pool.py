#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import threading
import time
import queue
import os
from typing import Callable, List, Dict, Any, Tuple, Optional
import datetime

# 创建日志器
logger = logging.getLogger(__name__)

# 颜色代码
class Colors:
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def log_yellow(message: str):
    """输出黄色日志"""
    logger.info(f"{Colors.YELLOW}[ThreadPool] {message}{Colors.RESET}")

def log_green(message: str):
    """输出绿色日志"""
    logger.info(f"{Colors.GREEN}[ThreadPool] {message}{Colors.RESET}")

def log_red(message: str):
    """输出红色日志"""
    logger.error(f"{Colors.RED}[ThreadPool] {message}{Colors.RESET}")

def log_blue(message: str):
    """输出蓝色日志"""
    logger.info(f"{Colors.BLUE}[ThreadPool] {message}{Colors.RESET}")

class PreciseRateLimiter:
    """精确的API请求频率限制器"""
    
    def __init__(self, requests_per_minute: int = 10, window_size: int = 60):
        """
        初始化精确频率限制器
        
        Args:
            requests_per_minute: 每分钟允许的最大请求数
            window_size: 滑动窗口大小（秒）
        """
        self.requests_per_minute = requests_per_minute
        self.window_size = window_size
        self.call_timestamps = []
        self.lock = threading.RLock()
        log_yellow(f"初始化精确API频率限制器: {requests_per_minute} 请求/分钟")
    
    def wait(self) -> float:
        """
        等待直到可以发送请求，返回等待时间
        
        Returns:
            实际等待的时间（秒）
        """
        wait_time = 0
        start_wait = time.time()
        
        with self.lock:
            current_time = time.time()
            
            # 清理超出窗口的时间戳
            self.call_timestamps = [t for t in self.call_timestamps 
                                  if t > current_time - self.window_size]
            
            # 当前窗口中的请求数
            current_count = len(self.call_timestamps)
            
            if current_count >= self.requests_per_minute:
                # 计算最早的调用何时离开窗口
                oldest_call = min(self.call_timestamps) if self.call_timestamps else current_time
                required_wait = oldest_call + self.window_size - current_time
                
                if required_wait > 0:
                    wait_time = required_wait
                    log_yellow(f"API频率限制: 需要等待 {wait_time:.2f} 秒")
            
            if wait_time <= 0:
                # 可以立即调用
                self.call_timestamps.append(current_time)
                return 0
        
        # 需要等待
        if wait_time > 0:
            log_yellow(f"线程等待中: 将等待 {wait_time:.2f} 秒以符合API限制")
            time.sleep(wait_time)
            
            # 递归调用确保可以调用
            with self.lock:
                current_time = time.time()
                self.call_timestamps.append(current_time)
                log_yellow(f"等待结束: 已添加API调用时间戳，当前API使用量: {len(self.call_timestamps)}/{self.requests_per_minute}")
        
        return time.time() - start_wait
    
    def get_current_usage(self) -> float:
        """
        获取当前API使用率
        
        Returns:
            当前窗口使用率 (0.0-1.0)
        """
        with self.lock:
            current_time = time.time()
            # 清理超出窗口的时间戳
            self.call_timestamps = [t for t in self.call_timestamps 
                                  if t > current_time - self.window_size]
            
            return len(self.call_timestamps) / self.requests_per_minute
    
    def get_available_slots(self) -> int:
        """
        获取当前可用的请求槽位数
        
        Returns:
            可用的请求槽位数
        """
        with self.lock:
            current_time = time.time()
            # 清理超出窗口的时间戳
            self.call_timestamps = [t for t in self.call_timestamps 
                                  if t > current_time - self.window_size]
            
            return max(0, self.requests_per_minute - len(self.call_timestamps))

    def record_api_call(self):
        """记录一次API调用"""
        with self.lock:
            self.call_timestamps.append(time.time())

class AdaptiveThreadPool:
    """自适应线程池，根据API调用频率动态调整线程数"""
    
    def __init__(self, api_rate_limit, initial_threads=2, max_threads=20):
        """
        初始化自适应线程池
        
        Args:
            api_rate_limit: 每分钟允许的API调用次数上限
            initial_threads: 初始线程数
            max_threads: 最大线程数上限
        """
        self.api_rate_limit = api_rate_limit
        self.max_threads = max_threads
        self.current_threads = initial_threads
        
        # 任务队列
        self.task_queue = queue.Queue()
        
        # 创建精确的频率限制器
        self.rate_limiter = PreciseRateLimiter(api_rate_limit)
        
        # 线程池状态
        self.active = True
        self.active_threads = 0
        self.active_threads_lock = threading.RLock()
        
        # 运行状态锁
        self.state_lock = threading.RLock()
        
        # 工作线程列表和线程ID映射
        self.worker_threads = []
        self.thread_ids = {}  # 映射线程对象到自定义ID
        self.next_thread_id = 1
        self.thread_id_lock = threading.RLock()
        
        # 结果追踪
        self.results = []
        self.results_lock = threading.RLock()
        
        # 性能统计
        self.performance_metrics = {
            'api_utilization': 0.0,  # API利用率百分比
            'queue_size': 0,         # 队列大小
            'avg_processing_time': 0.0, # 平均处理时间
            'completed_tasks': 0,    # 已完成任务数
            'waiting_time': 0.0,     # 平均等待时间
            'total_waiting_time': 0.0, # 总等待时间
        }
        self.metrics_lock = threading.RLock()
        
        log_yellow(f"初始化自适应线程池: 初始={initial_threads}, 最大={max_threads}, API限制={api_rate_limit}/分钟")
    
    def add_task(self, task_func, *args, **kwargs):
        """添加任务到队列"""
        if not self.active:
            log_red("线程池已关闭，无法添加新任务")
            return False
            
        self.task_queue.put((task_func, args, kwargs))
        
        with self.metrics_lock:
            self.performance_metrics['queue_size'] = self.task_queue.qsize()
        
        log_yellow(f"新任务已添加到队列, 当前队列大小: {self.task_queue.qsize()}")
        
        # 队列增长时考虑增加线程
        self._adjust_thread_count()
        return True
    
    def start(self):
        """启动线程池"""
        with self.state_lock:
            if not self.active:
                self.active = True
                log_green("线程池已激活")
            
            # 启动初始线程
            for _ in range(self.current_threads):
                self._start_worker_thread()
            
            # 启动监控线程
            monitor_thread = threading.Thread(target=self._monitor_performance, daemon=True, 
                                             name="ThreadPoolMonitor")
            monitor_thread.start()
            
            log_green(f"线程池已启动，当前工作线程: {self.current_threads}")
    
    def shutdown(self, wait=True):
        """关闭线程池"""
        with self.state_lock:
            log_yellow("线程池正在关闭...")
            self.active = False
            
            # 给每个线程放入一个None任务，让它们知道应该退出
            for _ in range(self.active_threads):
                self.task_queue.put((None, (), {}))
            
            # 等待所有线程完成
            if wait:
                for thread in self.worker_threads:
                    if thread.is_alive():
                        thread_id = self.thread_ids.get(thread, "未知")
                        log_yellow(f"等待线程 #{thread_id} 完成...")
                        thread.join()
            
            log_green("线程池已成功关闭")
    
    def get_results(self):
        """获取任务结果"""
        with self.results_lock:
            return list(self.results)
    
    def _get_next_thread_id(self):
        """获取下一个线程ID"""
        with self.thread_id_lock:
            thread_id = self.next_thread_id
            self.next_thread_id += 1
            return thread_id
    
    def _start_worker_thread(self):
        """启动新的工作线程"""
        thread_id = self._get_next_thread_id()
        thread_name = f"WorkerThread-{thread_id}"
        
        thread = threading.Thread(
            target=self._worker_loop, 
            daemon=True,
            name=thread_name,
            args=(thread_id,)
        )
        thread.start()
        
        with self.active_threads_lock:
            self.active_threads += 1
            self.worker_threads.append(thread)
            self.thread_ids[thread] = thread_id
            
        log_yellow(f"已创建新工作线程 #{thread_id}, 当前活动线程: {self.active_threads}")
    
    def _worker_loop(self, thread_id):
        """
        工作线程主循环
        
        Args:
            thread_id: 线程ID，用于日志输出
        """
        log_yellow(f"线程 #{thread_id} 已启动")
        should_exit = False
        
        while self.active and not should_exit:
            try:
                # 获取任务，但不会无限等待
                try:
                    task_func, args, kwargs = self.task_queue.get(timeout=5)
                    
                    # 检查是否是退出信号
                    if task_func is None:
                        log_yellow(f"线程 #{thread_id} 收到退出信号")
                        should_exit = True
                        self.task_queue.task_done()
                        continue
                        
                except queue.Empty:
                    # 检查是否应该减少线程数
                    with self.active_threads_lock:
                        if self.active_threads > self.current_threads:
                            log_yellow(f"线程 #{thread_id} 因为超出需要而自愿退出")
                            should_exit = True
                            self.active_threads -= 1
                            # 从worker_threads中移除
                            current_thread = threading.current_thread()
                            if current_thread in self.worker_threads:
                                self.worker_threads.remove(current_thread)
                                del self.thread_ids[current_thread]
                    continue
                
                # 执行任务前检查API调用频率
                log_yellow(f"线程 #{thread_id} 准备执行任务，检查API频率限制")
                wait_time = self.rate_limiter.wait()
                
                if wait_time > 0:
                    log_yellow(f"线程 #{thread_id} 已等待 {wait_time:.2f}s 以符合API限制")
                    # 更新性能指标
                    with self.metrics_lock:
                        self.performance_metrics['total_waiting_time'] += wait_time
                        self.performance_metrics['waiting_time'] = (
                            self.performance_metrics['total_waiting_time'] / 
                            max(1, self.performance_metrics['completed_tasks'])
                        )
                
                # 记录任务开始时间
                start_time = time.time()
                log_yellow(f"线程 #{thread_id} 开始执行任务")
                
                # 执行任务
                try:
                    result = task_func(*args, **kwargs)
                    
                    # 保存结果
                    with self.results_lock:
                        self.results.append(result)
                    
                    log_green(f"线程 #{thread_id} 成功完成任务")
                    
                except Exception as e:
                    log_red(f"线程 #{thread_id} 任务执行异常: {e}")
                
                # 更新性能统计
                processing_time = time.time() - start_time
                with self.metrics_lock:
                    # 更新平均处理时间（使用移动平均）
                    if self.performance_metrics['completed_tasks'] == 0:
                        self.performance_metrics['avg_processing_time'] = processing_time
                    else:
                        self.performance_metrics['avg_processing_time'] = (
                            self.performance_metrics['avg_processing_time'] * 0.8 + processing_time * 0.2
                        )
                    self.performance_metrics['completed_tasks'] += 1
                    self.performance_metrics['queue_size'] = self.task_queue.qsize()
                
                # 标记任务完成
                self.task_queue.task_done()
                log_yellow(f"线程 #{thread_id} 已标记任务完成，当前完成: {self.performance_metrics['completed_tasks']}")
                
            except Exception as e:
                log_red(f"线程 #{thread_id} 异常: {e}")
                time.sleep(1)  # 防止异常导致的CPU占用
        
        # 线程退出
        with self.active_threads_lock:
            # 确保线程计数正确
            if not should_exit:  # 如果不是已经处理过的自愿退出
                self.active_threads -= 1
                # 从worker_threads中移除
                current_thread = threading.current_thread()
                if current_thread in self.worker_threads:
                    self.worker_threads.remove(current_thread)
                    if current_thread in self.thread_ids:
                        del self.thread_ids[current_thread]
                
        log_yellow(f"线程 #{thread_id} 已退出，当前活动线程: {self.active_threads}")
    
    def _adjust_thread_count(self):
        """动态调整线程数量"""
        # 获取当前API利用率
        api_utilization = self.rate_limiter.get_current_usage()
        
        # 更新性能指标
        with self.metrics_lock:
            self.performance_metrics['api_utilization'] = api_utilization
        
        # 根据API利用率和队列大小调整线程数
        queue_size = self.task_queue.qsize()
        
        with self.state_lock:
            # 如果队列中有任务且API利用率低，增加线程
            if queue_size > 0 and api_utilization < 0.8 and self.current_threads < self.max_threads:
                # 计算可以增加的线程数
                available_api_capacity = max(1, self.api_rate_limit - int(api_utilization * self.api_rate_limit))
                avg_time = max(0.1, self.performance_metrics.get('avg_processing_time', 5))
                potential_new_threads = min(
                    max(1, int(available_api_capacity / (60 / avg_time))),  # 基于API容量
                    queue_size,  # 不超过队列大小
                    self.max_threads - self.current_threads  # 不超过最大线程数
                )
                
                # 保守增长，每次最多增加2个线程
                threads_to_add = max(1, min(2, potential_new_threads))
                old_thread_count = self.current_threads
                self.current_threads += threads_to_add
                
                log_yellow(f"增加线程: API使用率={api_utilization:.2f}, 队列大小={queue_size}, 增加={threads_to_add}个, {old_thread_count}->{self.current_threads}")
                
                # 启动新线程
                for _ in range(threads_to_add):
                    self._start_worker_thread()
            
            # 如果API利用率高或队列为空，减少线程
            elif (api_utilization > 0.9 or queue_size == 0) and self.current_threads > 1:
                # 计算要减少的线程数
                if api_utilization > 0.95:
                    # 接近限制，大幅减少
                    threads_to_remove = max(1, self.current_threads // 3)
                elif queue_size == 0:
                    # 队列为空，缓慢减少
                    threads_to_remove = 1
                else:
                    # 正常调整
                    threads_to_remove = 1
                
                old_thread_count = self.current_threads
                self.current_threads = max(1, self.current_threads - threads_to_remove)
                
                log_yellow(f"减少线程: API使用率={api_utilization:.2f}, 队列大小={queue_size}, 减少={threads_to_remove}个, {old_thread_count}->{self.current_threads}")
    
    def _monitor_performance(self):
        """性能监控线程"""
        log_blue("监控线程已启动")
        monitor_count = 0
        
        while self.active:
            try:
                # 每5秒检查一次性能
                time.sleep(5)
                monitor_count += 1
                
                # 记录当前性能指标
                with self.metrics_lock:
                    api_util = self.performance_metrics['api_utilization']
                    queue_size = self.performance_metrics['queue_size'] 
                    avg_time = self.performance_metrics['avg_processing_time']
                    completed = self.performance_metrics['completed_tasks']
                    waiting_time = self.performance_metrics['waiting_time']
                
                with self.active_threads_lock:
                    active_threads = self.active_threads
                
                # 每30秒输出详细信息，否则输出简略信息
                if monitor_count % 6 == 0:
                    log_blue(
                        f"性能报告: API使用率={api_util:.2f}, "
                        f"队列大小={queue_size}, "
                        f"平均处理时间={avg_time:.2f}秒, "
                        f"平均等待时间={waiting_time:.2f}秒, "
                        f"已完成任务={completed}, "
                        f"活动线程={active_threads}/{self.current_threads}"
                    )
                else:
                    log_blue(f"状态: API={api_util:.2f}, 队列={queue_size}, 线程={active_threads}/{self.current_threads}")
                
                # 动态调整线程数
                self._adjust_thread_count()
                
            except Exception as e:
                log_red(f"监控线程异常: {e}")
        
        log_blue("监控线程已退出")

# 单例模式，确保全局只有一个线程池实例
_thread_pool_instance = None
_instance_lock = threading.Lock()

def get_thread_pool(api_rate_limit=10, max_threads=20, force_new=False):
    """获取线程池实例（单例模式）"""
    global _thread_pool_instance
    
    with _instance_lock:
        if _thread_pool_instance is None or force_new:
            _thread_pool_instance = AdaptiveThreadPool(
                api_rate_limit=api_rate_limit,
                initial_threads=2,
                max_threads=max_threads
            )
            log_yellow("创建了新的线程池实例")
        
    return _thread_pool_instance 