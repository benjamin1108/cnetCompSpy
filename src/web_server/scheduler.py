import threading
import time
import datetime
import subprocess
import os
import yaml
import logging
from src.utils.colored_logger import setup_colored_logging

setup_colored_logging(level=logging.INFO)
logger = logging.getLogger('Scheduler')

class Scheduler:
    def __init__(self, config_path='config.yaml'):
        self.config_path = config_path
        self.last_run_date = None
        self.running = False
        self.current_daily_task_time = None
        self.current_check_interval = None
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                new_daily_task_time = config.get('scheduler', {}).get('daily_task_time', '02:00')
                new_check_interval = config.get('scheduler', {}).get('check_interval', 10)
                
                # 只有在配置发生变化时才输出日志
                if new_daily_task_time != self.current_daily_task_time or new_check_interval != self.current_check_interval:
                    logger.info(f"定时任务配置已加载：每日任务时间={new_daily_task_time}, 检查间隔={new_check_interval}秒")
                    self.current_daily_task_time = new_daily_task_time
                    self.current_check_interval = new_check_interval
                
                self.daily_task_time = new_daily_task_time
                self.check_interval = new_check_interval
        except Exception as e:
            logger.error(f"加载配置文件出错：{e}")
            self.daily_task_time = '02:00'
            self.check_interval = 10

    def should_run_task(self):
        """检查是否应该运行每日任务"""
        current_time = datetime.datetime.now()
        current_date = current_time.date()
        task_hour, task_minute = map(int, self.daily_task_time.split(':'))
        task_time_today = current_time.replace(hour=task_hour, minute=task_minute, second=0, microsecond=0)
        
        # 检查是否已经运行过今日任务
        if self.last_run_date == current_date:
            return False
        
        # 检查当前时间是否在任务时间附近（例如5分钟内）
        time_difference = (current_time - task_time_today).total_seconds()
        if time_difference >= 0 and time_difference <= 300:  # 5分钟窗口
            self.last_run_date = current_date
            return True
        
        # 如果当前时间已经超过任务时间太久，则等待到下一天
        if time_difference > 1:
            #logger.info(f"当前时间已超过任务时间 {self.daily_task_time} 太久，将等待到下一天执行")
            return False
        
        return False

    def run_daily_task(self):
        """运行每日任务脚本"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scripts', 'daily_crawl_and_analyze.sh')
        logger.info(f"启动每日任务脚本：{script_path}")
        
        try:
            process = subprocess.Popen([script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                logger.info(f"每日任务脚本执行成功：\n{stdout}")
            else:
                logger.error(f"每日任务脚本执行失败：\n{stderr}")
        except Exception as e:
            logger.error(f"执行每日任务脚本出错：{e}")

    def check_and_run(self):
        """检查并运行定时任务"""
        while self.running:
            self.load_config()  # 每次循环重新加载配置，允许动态修改
            if self.should_run_task():
                logger.info(f"达到每日任务时间 {self.daily_task_time}，启动任务...")
                self.run_daily_task()
            time.sleep(self.check_interval)

    def start(self):
        """启动定时任务检查线程"""
        if not self.running:
            self.running = True
            logger.info("定时任务检查线程已启动")
            threading.Thread(target=self.check_and_run, daemon=True).start()

    def stop(self):
        """停止定时任务检查"""
        self.running = False
        logger.info("定时任务检查线程已停止")

if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
