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

# MODIFIED: Made log functions more generic for different levels if needed
def log_info_color(message: str, color_code: str):
    """输出带颜色的INFO日志"""
    logger.info(f"{color_code}[ThreadPool] {message}{Colors.RESET}")

def log_error_color(message: str, color_code: str):
    """输出带颜色的ERROR日志"""
    logger.error(f"{color_code}[ThreadPool] {message}{Colors.RESET}")

def log_debug_color(message: str, color_code: str):
    """输出带颜色的DEBUG日志 (using logger.debug)"""
    logger.debug(f"{color_code}[ThreadPool] {message}{Colors.RESET}")


# Existing specific color log functions (can be kept for convenience or refactored)
def log_yellow(message: str):
    log_info_color(message, Colors.YELLOW)

def log_green(message: str):
    log_info_color(message, Colors.GREEN)

def log_red(message: str): # This was logger.error, which is good
    logger.error(f"{Colors.RED}[ThreadPool] {message}{Colors.RESET}")

def log_blue(message: str):
    log_info_color(message, Colors.BLUE)


class PreciseRateLimiter:
    """精确的API请求频率限制器"""
    
    def __init__(self, max_calls: int, window_seconds: int):
        if max_calls <= 0:
            raise ValueError("max_calls must be positive.")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive.")
            
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.call_timestamps = []
        self.lock = threading.RLock()
        log_yellow(f"初始化精确API频率限制器: 每 {self.window_seconds} 秒最多 {self.max_calls} 次调用")
    
    def wait(self) -> float:
        wait_time = 0
        
        with self.lock:
            current_time = time.time()
            self.call_timestamps = [t for t in self.call_timestamps if t > current_time - self.window_seconds]
            current_count_in_window = len(self.call_timestamps)
            
            if current_count_in_window >= self.max_calls:
                oldest_call_in_window = min(self.call_timestamps) if self.call_timestamps else current_time
                required_wait = (oldest_call_in_window + self.window_seconds) - current_time
                
                if required_wait > 0:
                    wait_time = required_wait
            
            if wait_time <= 0:
                self.call_timestamps.append(time.time())
                return 0
        
        if wait_time > 0:
            log_yellow(f"API频率限制: 当前窗口 ({self.window_seconds}s) 已有 {current_count_in_window}/{self.max_calls} 次调用. 将等待 {wait_time:.2f} 秒.")
            time.sleep(wait_time)
            with self.lock:
                self.call_timestamps.append(time.time())
        
        return wait_time
    
    def get_current_usage_ratio(self) -> float:
        """Returns the ratio of used slots to max_calls in the current window (0.0 to 1.0)."""
        with self.lock:
            current_time = time.time()
            self.call_timestamps = [t for t in self.call_timestamps if t > current_time - self.window_seconds]
            return len(self.call_timestamps) / self.max_calls if self.max_calls > 0 else 0.0
    
    def get_available_slots(self) -> int:
        with self.lock:
            current_time = time.time()
            self.call_timestamps = [t for t in self.call_timestamps if t > current_time - self.window_seconds]
            return max(0, self.max_calls - len(self.call_timestamps))

    def record_api_call(self):
        with self.lock:
            self.call_timestamps.append(time.time())


class AdaptiveThreadPool:
    """自适应线程池，根据API调用频率动态调整线程数"""
    
    def __init__(self, api_rate_limit, initial_threads=2, max_threads=20, monitor_interval=30, shutdown_join_timeout=65):
        self.api_rate_limit = api_rate_limit
        self.max_threads = max(1, max_threads)
        self.current_threads_target = initial_threads
        
        self.task_queue = queue.Queue()
        self.rate_limiter = PreciseRateLimiter(api_rate_limit if api_rate_limit > 0 else 600, 60)
        
        self.active = False
        self.active_threads_count = 0
        self.active_threads_lock = threading.RLock()
        
        self.state_lock = threading.RLock()
        
        self.worker_threads = []
        self.thread_ids = {} 
        self.next_thread_id = 1
        self.thread_id_lock = threading.RLock()
        
        self.results = []
        self.results_lock = threading.RLock()

        self.thread_task_info: Dict[int, str] = {} 
        self.thread_task_info_lock = threading.RLock()
        
        self.performance_metrics = {
            'api_utilization': 0.0,
            'queue_size': 0,
            'avg_processing_time_ms': 0.0,
            'completed_tasks': 0,
            'total_processing_time_ms': 0.0,
        }
        self.metrics_lock = threading.RLock()
        self.monitor_interval = monitor_interval
        self.shutdown_join_timeout = shutdown_join_timeout
        self.tasks_submitted_this_activation = 0
        
        log_yellow(f"线程池定义: 初始目标={initial_threads}, 最大={self.max_threads}, API限制={api_rate_limit}/分钟, "
                   f"监控间隔={monitor_interval}s, 关闭等待超时={self.shutdown_join_timeout}s")
    
    def add_task(self, task_func: Callable, *args: Any, **kwargs: Any) -> bool:
        if not self.active:
            log_red("线程池未激活或已关闭，无法添加新任务")
            return False
        
        task_meta = kwargs.pop('task_meta', {})
        task_identifier = task_meta.get('identifier', f'未命名任务@{time.strftime("%H:%M:%S")}')

        if 'task_identifier' in kwargs and not task_meta:
            task_identifier = kwargs.pop('task_identifier')

        self.task_queue.put((task_func, args, kwargs, task_identifier))
        
        with self.metrics_lock:
            self.performance_metrics['queue_size'] = self.task_queue.qsize()
            self.tasks_submitted_this_activation += 1
        
        log_blue(f"新任务 '{task_identifier}' 已添加到队列 (ID: {id(task_func)}), 当前队列大小: {self.task_queue.qsize()}")
        
        self._adjust_thread_count()
        return True
    
    def start(self):
        with self.state_lock:
            if self.active:
                log_yellow("线程池已在运行中.")
                return

            self.active = True
            log_green("线程池已激活")
            
            self.results = []
            with self.metrics_lock:
                self.performance_metrics['completed_tasks'] = 0
                self.performance_metrics['total_processing_time_ms'] = 0.0
                self.tasks_submitted_this_activation = 0
            
            for _ in range(self.current_threads_target):
                if self.active_threads_count < self.max_threads:
                    self._start_worker_thread()
            
            if self.monitor_interval > 0:
                monitor_thread = threading.Thread(target=self._monitor_performance, daemon=True, 
                                                 name="ThreadPoolMonitor")
                monitor_thread.start()
                log_green(f"性能监控线程已启动 (每 {self.monitor_interval} 秒)")
            
            log_green(f"线程池已启动，初始工作线程数: {self.active_threads_count} (目标: {self.current_threads_target})")
    
    def shutdown(self, wait=True):
        with self.state_lock:
            if not self.active and not self.worker_threads:
                log_yellow("线程池已关闭或从未启动或已完全清理.")
                return

            log_yellow("线程池开始关闭流程...")
            self.active = False
            
            current_worker_list = []
            with self.active_threads_lock:
                current_worker_list = list(self.worker_threads)
            
            num_potential_workers_to_signal = len(current_worker_list)

            if num_potential_workers_to_signal > 0:
                log_yellow(f"准备发送 {num_potential_workers_to_signal} 个关闭信号到任务队列 (一个给每个当前工作线程)...")
                for _ in range(num_potential_workers_to_signal):
                    self.task_queue.put((None, (), {}, None))
            else:
                log_yellow("没有活动的工作线程需要发送关闭信号。队列中的任务可能不会被处理。")

            if not wait:
                cleared_tasks = 0
                temp_sentinels_holder = []
                while not self.task_queue.empty():
                    try:
                        task_tuple = self.task_queue.get_nowait()
                        if task_tuple[0] is not None:
                            cleared_tasks +=1
                            log_debug_color(f"任务 '{task_tuple[3] if len(task_tuple) > 3 else '未知'}' 在非等待关闭时被移除。", Colors.RED)
                        else:
                            temp_sentinels_holder.append(task_tuple)
                    except queue.Empty:
                        break
                for item in temp_sentinels_holder: 
                    self.task_queue.put(item)
                if cleared_tasks > 0:
                    log_yellow(f"关闭时清理了 {cleared_tasks} 个未处理的任务 (wait=False).")

        if current_worker_list: 
            log_yellow(f"等待所有 {len(current_worker_list)} 个工作线程完成队列中的剩余任务并退出...")
            for thread_obj in current_worker_list: 
                thread_custom_id_str = "未知"
                with self.thread_id_lock:
                    for tid, t_obj_stored in self.thread_ids.items():
                         if t_obj_stored == thread_obj:
                             thread_custom_id_str = str(tid)
                             break
                
                if thread_obj.is_alive():
                    log_yellow(f"等待线程 #{thread_custom_id_str} ({thread_obj.name}) 退出 (超时: {self.shutdown_join_timeout}s)...")
                    thread_obj.join(timeout=self.shutdown_join_timeout)
                    if thread_obj.is_alive():
                        log_red(f"线程 #{thread_custom_id_str} ({thread_obj.name}) 在{self.shutdown_join_timeout}秒后未能退出!")
                    else:
                        log_green(f"线程 #{thread_custom_id_str} ({thread_obj.name}) 已成功退出.")
                else:
                    log_green(f"线程 #{thread_custom_id_str} ({thread_obj.name}) 在等待前已退出/未激活.")
        
        with self.active_threads_lock:
            if not self.worker_threads:
                log_green("线程池已成功关闭. 所有工作线程记录已移除.")
            else:
                log_red(f"线程池关闭后，内部记录中仍有 {len(self.worker_threads)} 个工作线程对象: {[t.name for t in self.worker_threads]}. 这可能是一个清理小问题。")
                self.worker_threads.clear()
                self.active_threads_count = 0

        final_unprocessed_tasks = []
        try:
            while True:
                task_tuple = self.task_queue.get_nowait()
                if task_tuple[0] is not None:
                    task_identifier = task_tuple[3] if len(task_tuple) > 3 and task_tuple[3] else "未知任务"
                    final_unprocessed_tasks.append(task_identifier)
                self.task_queue.task_done()
        except queue.Empty:
            pass

        if final_unprocessed_tasks:
            log_red(f"线程池关闭后，队列中仍发现 {len(final_unprocessed_tasks)} 个未处理的任务: {', '.join(final_unprocessed_tasks)}")
        elif self.task_queue.qsize() > 0:
             log_yellow(f"线程池关闭后，队列中仍有 {self.task_queue.qsize()} 个项目(异常情况).")
        else:
            log_green("线程池关闭后，任务队列已清空.")
    
    def get_results(self) -> List[Any]:
        with self.results_lock:
            return list(self.results)
    
    def _get_next_thread_id(self) -> int:
        with self.thread_id_lock:
            tid = self.next_thread_id
            self.next_thread_id += 1
            return tid

    def _start_worker_thread(self):
        with self.active_threads_lock:
            if not self.active:
                log_yellow("线程池已关闭，取消创建新工作线程")
                return

            if self.active_threads_count >= self.max_threads:
                return

            thread_custom_id = self._get_next_thread_id()
            
            worker = threading.Thread(target=self._worker_loop, args=(thread_custom_id,), 
                                      name=f"WorkerThread-{thread_custom_id}")
            worker.daemon = True
            
            self.worker_threads.append(worker)
            self.thread_ids[worker] = thread_custom_id 
            self.active_threads_count += 1
            
            worker.start()
            log_green(f"线程 #{thread_custom_id} ({worker.name}) 已启动. 当前活动线程: {self.active_threads_count}")

    def _remove_worker_thread_record(self, thread_obj: threading.Thread, thread_custom_id: int):
        with self.active_threads_lock:
            if thread_obj in self.worker_threads:
                self.worker_threads.remove(thread_obj)
            if thread_obj in self.thread_ids: 
                del self.thread_ids[thread_obj]
        with self.thread_task_info_lock:
            self.thread_task_info.pop(thread_custom_id, None)


    def _worker_loop(self, thread_custom_id: int):
        log_blue(f"线程 #{thread_custom_id} ({threading.current_thread().name}) 进入工作循环.")
        
        try:
            while True:
                task_identifier_for_log = '无任务'
                with self.thread_task_info_lock:
                    self.thread_task_info.pop(thread_custom_id, None)

                task_data = None
                try:
                    task_data = self.task_queue.get(block=True, timeout=1.0) 
                except queue.Empty:
                    if not self.active and self.task_queue.empty():
                        log_yellow(f"线程 #{thread_custom_id} 等待任务超时，线程池已关闭且队列确认已空，准备退出.")
                        break
                    continue 
                
                if task_data is None:
                    log_red(f"线程 #{thread_custom_id} 从队列获取到裸 None (异常情况)，将视为关闭信号并退出.")
                    self.task_queue.task_done()
                    break

                task_func, task_args, task_kwargs, task_identifier = task_data
                task_identifier_for_log = task_identifier

                if task_func is None:
                    log_yellow(f"线程 #{thread_custom_id} 收到关闭信号 (sentinel)，完成任务队列处理，准备退出.")
                    self.task_queue.task_done()
                    break

                log_blue(f"线程 #{thread_custom_id} 获取到任务: '{task_identifier}'")
                with self.thread_task_info_lock:
                    self.thread_task_info[thread_custom_id] = task_identifier
                
                task_start_time = time.monotonic()
                try:
                    log_green(f"线程 #{thread_custom_id} 开始处理任务: '{task_identifier}'")
                    result = task_func(*task_args, **task_kwargs)
                    duration_ms = (time.monotonic() - task_start_time) * 1000
                    log_green(f"线程 #{thread_custom_id} 成功完成任务: '{task_identifier}', 耗时: {duration_ms:.2f}ms")
                    with self.results_lock:
                        self.results.append(result)
                    with self.metrics_lock:
                        self.performance_metrics['completed_tasks'] += 1
                        self.performance_metrics['total_processing_time_ms'] += duration_ms
                except Exception as e:
                    duration_ms = (time.monotonic() - task_start_time) * 1000
                    log_red(f"线程 #{thread_custom_id} 执行任务 '{task_identifier_for_log}' 失败: {e} (类型: {type(e).__name__}), 耗时: {duration_ms:.2f}ms")
                finally:
                    self.task_queue.task_done()
                    with self.thread_task_info_lock:
                        self.thread_task_info.pop(thread_custom_id, None)
        finally:
            log_yellow(f"线程 #{thread_custom_id} ({threading.current_thread().name}) 停止工作并退出循环.")
            with self.active_threads_lock:
                self.active_threads_count -= 1
                log_yellow(f"线程 #{thread_custom_id} 已停止. 当前活动线程: {self.active_threads_count}")
                
                current_thread_obj = threading.current_thread()
                if current_thread_obj in self.worker_threads:
                    self.worker_threads.remove(current_thread_obj)
                if current_thread_obj in self.thread_ids:
                    del self.thread_ids[current_thread_obj]
            with self.thread_task_info_lock:
                self.thread_task_info.pop(thread_custom_id, None)

    def _adjust_thread_count(self):
        with self.active_threads_lock:
            if not self.active:
                return

            q_size = self.task_queue.qsize()
            current_active = self.active_threads_count
            
            new_target_threads = self.current_threads_target

            if q_size > current_active and current_active < self.max_threads:
                new_target_threads = min(self.max_threads, current_active + 1)
            elif q_size == 0 and current_active > 1 :
                pass


            if new_target_threads != self.current_threads_target:
                log_yellow(f"线程池动态调整: 任务队列大小={q_size}, 当前活动线程={current_active}. 目标工作线程数从 {self.current_threads_target} 变更为 {new_target_threads}")
                self.current_threads_target = new_target_threads

            if self.current_threads_target > current_active:
                for _ in range(self.current_threads_target - current_active):
                    if self.active_threads_count < self.max_threads:
                         self._start_worker_thread()
                    else:
                        break 

    def _monitor_performance(self):
        log_debug_color("性能监控线程启动.", Colors.GREEN)
        while self.active: 
            time.sleep(self.monitor_interval)
            if not self.active : break

            with self.metrics_lock:
                q_size = self.performance_metrics['queue_size'] = self.task_queue.qsize()
                completed_this_activation = self.performance_metrics['completed_tasks']
                total_submitted_this_activation = self.tasks_submitted_this_activation
                total_processing_time_ms = self.performance_metrics['total_processing_time_ms']
                
                avg_time_ms = 0.0
                if completed_this_activation > 0:
                    avg_time_ms = total_processing_time_ms / completed_this_activation
                
                api_usage_percent = self.rate_limiter.get_current_usage_ratio() * 100
                self.performance_metrics['api_utilization'] = api_usage_percent

            with self.active_threads_lock:
                 active_threads = self.active_threads_count
                 target_threads = self.current_threads_target
            
            summary_lines = [
                f"{Colors.BOLD}---- 线程池周期性摘要 ({datetime.datetime.now().strftime('%H:%M:%S')}) ----{Colors.RESET}",
                f"  {Colors.BLUE}[状态]{Colors.RESET}",
                f"    - 活动/目标线程: {active_threads} / {target_threads}",
                f"    - 最大线程数: {self.max_threads}",
                f"    - API利用率: {api_usage_percent:.1f}%",
                f"  {Colors.BLUE}[任务队列]{Colors.RESET}",
                f"    - 当前大小: {q_size}",
                f"  {Colors.BLUE}[任务进度 (当前会话)]{Colors.RESET}"
            ]

            if total_submitted_this_activation > 0:
                progress_percent = (completed_this_activation / total_submitted_this_activation) * 100 if total_submitted_this_activation > 0 else 0
                summary_lines.append(f"    - 已完成: {completed_this_activation} / {total_submitted_this_activation} ({progress_percent:.1f}%)")
                
                bar_length = 20
                filled_length = int(bar_length * completed_this_activation // total_submitted_this_activation) if total_submitted_this_activation > 0 else 0
                bar = '#' * filled_length + '-' * (bar_length - filled_length)
                summary_lines.append(f"      [{Colors.GREEN}{bar}{Colors.RESET}]")
            else:
                summary_lines.append("    - 已完成: 0 / 0 (0.0%) (尚未提交任务)")
                summary_lines.append("      [--------------------]")

            summary_lines.extend([
                f"  {Colors.BLUE}[性能]{Colors.RESET}",
                f"    - 平均任务处理时间: {avg_time_ms:.2f}ms",
                f"    - 已完成任务总数 (当前会话): {completed_this_activation}"
            ])

            active_tasks_details = []
            with self.thread_task_info_lock:
                if self.thread_task_info:
                    for tid, task_id_str in self.thread_task_info.items():
                        active_tasks_details.append(f"    - 线程 #{tid} -> '{task_id_str}'")
            
            if active_tasks_details:
                summary_lines.append(f"  {Colors.BLUE}[活动任务详情 (最多显示几个)]{Colors.RESET}")
                summary_lines.extend(active_tasks_details)
            else:
                summary_lines.append(f"  {Colors.BLUE}[活动任务详情]{Colors.RESET}")
                summary_lines.append("    - 所有工作线程当前均空闲或无任务信息")
            
            summary_lines.append(f"{Colors.BOLD}------ 摘要结束 ------{Colors.RESET}")
            
            logger.debug("\n".join(summary_lines)) 

        log_debug_color("性能监控线程停止.", Colors.YELLOW)

# Global instance of the thread pool
_thread_pool_instance: Optional[AdaptiveThreadPool] = None
_thread_pool_lock = threading.Lock()

def get_thread_pool(api_rate_limit=60, initial_threads=2, max_threads=10, monitor_interval=30, shutdown_join_timeout=65, force_new=False) -> AdaptiveThreadPool:
    global _thread_pool_instance
    with _thread_pool_lock:
        if force_new and _thread_pool_instance is not None:
            log_yellow("强制创建新线程池实例，正在关闭旧实例 (如果存在且活动中)...")
            if _thread_pool_instance.active:
                 _thread_pool_instance.shutdown(wait=False)
            _thread_pool_instance = None

        if _thread_pool_instance is None:
            log_yellow(f"创建新的 AdaptiveThreadPool 实例: API每分钟{api_rate_limit}, 初始{initial_threads}, 最大{max_threads}, "
                       f"监控间隔{monitor_interval}s, 关闭等待超时={shutdown_join_timeout}s")
            _thread_pool_instance = AdaptiveThreadPool(
                api_rate_limit=api_rate_limit,
                initial_threads=initial_threads,
                max_threads=max_threads,
                monitor_interval=monitor_interval,
                shutdown_join_timeout=shutdown_join_timeout
            )
            _thread_pool_instance.start()
        
        if not _thread_pool_instance.active and not force_new :
            log_yellow("线程池实例已存在但已关闭，重新启动...")
            _thread_pool_instance.start()

    return _thread_pool_instance

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s')

    def sample_task(duration, task_id, api_limiter: PreciseRateLimiter):
        log_info_color(f"任务 {task_id} 开始，将休眠 {duration} 秒", Colors.GREEN)
        if api_limiter:
            wait_needed = api_limiter.wait()
            if wait_needed > 0:
                log_info_color(f"任务 {task_id} 等待API限速器 {wait_needed:.2f} 秒", Colors.YELLOW)
        
        time.sleep(duration)
        if task_id == 3:
            pass
        return f"任务 {task_id} 完成"

    pool = get_thread_pool(api_rate_limit=10, initial_threads=2, max_threads=5, monitor_interval=5, shutdown_join_timeout=7, force_new=True)
    
    for i in range(10):
        import random
        pool.add_task(sample_task, random.randint(1,2), i + 1, None, task_meta={'identifier': f'测试任务ID-{i+1}'})
        time.sleep(0.2)

    log_info_color("所有任务已提交. 等待线程池处理...", Colors.BOLD)
    
    time.sleep(10)

    log_info_color("准备关闭线程池...", Colors.BOLD)
    pool.shutdown(wait=True)

    results = pool.get_results()
    log_info_color(f"所有任务执行完毕. {len(results)} 个结果:", Colors.BOLD)
    for res_idx, r in enumerate(results):
        log_info_color(f"  结果 {res_idx+1}: {r}", Colors.GREEN)

    log_info_color("获取新线程池实例 (force_new=True)...", Colors.BOLD)
    pool2 = get_thread_pool(api_rate_limit=5, initial_threads=1, max_threads=3, monitor_interval=3, shutdown_join_timeout=5, force_new=True)
    pool2.add_task(sample_task, 1, 101, None, task_meta={'identifier': f'Pool2-任务1'})
    time.sleep(5)
    pool2.shutdown(wait=True)
    log_info_color("主程序结束.", Colors.BOLD)

