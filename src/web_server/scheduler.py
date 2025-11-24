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
    def __init__(self, config_path=None):
        # 记录配置路径
        self.config_path = config_path
        # 初始化状态变量
        self.last_run_date = None
        self.last_dingtalk_push_date = None
        self.running = False
        self.current_daily_task_time = None
        self.current_dingtalk_push_time = None
        self.current_dingtalk_push_day = None
        self.current_check_interval = None
        self.debug_mode = False
        self.vendor = None  # 厂商设置
        self.limit = None   # 文章数量限制
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            # 使用通用配置加载器
            from src.utils.config_loader import get_config
            
            # 加载配置
            config = get_config(config_path=self.config_path)
            
            new_daily_task_time = config.get('scheduler', {}).get('daily_task_time', '02:00')
            new_check_interval = config.get('scheduler', {}).get('check_interval', 10)
            new_dingtalk_push_time = config.get('dingtalk', {}).get('weekly_push_time', '12:00')
            new_dingtalk_push_day = config.get('dingtalk', {}).get('weekly_push_day', 5)  # 默认周五
            new_debug_mode = config.get('scheduler', {}).get('debug_mode', False)
            new_vendor = config.get('scheduler', {}).get('vendor', None)  # 厂商设置，默认为None（全部厂商）
            new_limit = config.get('scheduler', {}).get('limit', None)    # 文章数量限制，默认为None（无限制）
            
            # 确保星期几的值在1-7之间
            if not (1 <= new_dingtalk_push_day <= 7):
                logger.warning(f"钉钉推送星期几配置无效: {new_dingtalk_push_day}，应为1-7，已设为默认值5(周五)")
                new_dingtalk_push_day = 5
            
            # 只有在配置发生变化时才输出日志
            config_changed = False
            
            if new_daily_task_time != self.current_daily_task_time:
                self.current_daily_task_time = new_daily_task_time
                config_changed = True
                
            if new_check_interval != self.current_check_interval:
                self.current_check_interval = new_check_interval
                config_changed = True
                
            if new_dingtalk_push_time != self.current_dingtalk_push_time:
                self.current_dingtalk_push_time = new_dingtalk_push_time
                config_changed = True
            
            if new_dingtalk_push_day != self.current_dingtalk_push_day:
                self.current_dingtalk_push_day = new_dingtalk_push_day
                config_changed = True
            
            if new_debug_mode != self.debug_mode:
                self.debug_mode = new_debug_mode
                config_changed = True
            
            if new_vendor != self.vendor:
                self.vendor = new_vendor
                config_changed = True
                
            if new_limit != self.limit:
                self.limit = new_limit
                config_changed = True
            
            if config_changed:
                weekday_names = {1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五", 6: "周六", 7: "周日"}
                weekday_name = weekday_names.get(new_dingtalk_push_day, "未知")
                vendor_info = f"厂商={new_vendor}" if new_vendor else "厂商=全部"
                limit_info = f"限制={new_limit}篇" if new_limit else "限制=无"
                
                logger.info(f"定时任务配置已加载：每日任务时间={new_daily_task_time}, 钉钉推送时间={weekday_name} {new_dingtalk_push_time}, " + 
                          f"检查间隔={new_check_interval}秒, 调试模式={'开启' if new_debug_mode else '关闭'}, {vendor_info}, {limit_info}")
            
            self.daily_task_time = new_daily_task_time
            self.check_interval = new_check_interval
            self.dingtalk_push_time = new_dingtalk_push_time
            self.dingtalk_push_day = new_dingtalk_push_day
            self.debug_mode = new_debug_mode
            self.vendor = new_vendor
            self.limit = new_limit
        except Exception as e:
            logger.error(f"加载配置文件出错：{e}")
            self.daily_task_time = '02:00'
            self.check_interval = 10
            self.dingtalk_push_time = '12:00'
            self.dingtalk_push_day = 5  # 默认周五
            self.debug_mode = False
            self.vendor = None
            self.limit = None

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

    def should_push_dingtalk(self):
        """检查是否应该执行钉钉推送任务"""
        current_time = datetime.datetime.now()
        current_date = current_time.date()
        
        # 检查是否是配置的星期几
        # isoweekday()返回1-7表示周一到周日
        if current_time.isoweekday() != self.dingtalk_push_day:
            return False
        
        push_hour, push_minute = map(int, self.dingtalk_push_time.split(':'))
        push_time_today = current_time.replace(hour=push_hour, minute=push_minute, second=0, microsecond=0)
        
        # 检查是否已经推送过本周钉钉
        # 本周的判断逻辑：上次推送日期是本周的同一天
        if self.last_dingtalk_push_date == current_date:
            return False
        
        # 检查当前时间是否在推送时间附近（例如5分钟内）
        time_difference = (current_time - push_time_today).total_seconds()
        if time_difference >= 0 and time_difference <= 300:  # 5分钟窗口
            self.last_dingtalk_push_date = current_date
            weekday_names = {1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五", 6: "周六", 7: "周日"}
            weekday_name = weekday_names.get(self.dingtalk_push_day, "未知")
            logger.info(f"今天是{weekday_name}，符合钉钉推送条件")
            return True
        
        return False

    def run_daily_task(self):
        """运行每日任务脚本"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scripts', 'daily_crawl_and_analyze.sh')
        logger.info(f"启动每日任务脚本：{script_path}")
        
        try:
            cmd = [script_path]
            
            # 添加调试模式参数
            if self.debug_mode:
                cmd.append('--debug')
                logger.info("以调试模式运行每日任务")
            
            # 添加厂商参数
            if self.vendor:
                cmd.extend(['--vendor', self.vendor])
                logger.info(f"仅处理厂商: {self.vendor}")
                
            # 添加文章数量限制参数
            if self.limit:
                cmd.extend(['--limit', str(self.limit)])
                logger.info(f"文章数量限制: {self.limit}篇")
                
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                logger.info(f"每日任务脚本执行成功：\n{stdout}")
            else:
                logger.error(f"每日任务脚本执行失败：\n{stderr}")
        except Exception as e:
            logger.error(f"执行每日任务脚本出错：{e}")

    def run_dingtalk_push(self):
        """运行钉钉推送任务"""
        weekday_names = {1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五", 6: "周六", 7: "周日"}
        weekday_name = weekday_names.get(self.dingtalk_push_day, "未知")
        logger.info(f"启动钉钉推送任务({weekday_name} {self.dingtalk_push_time})...")
        
        try:
            # 获取项目根目录
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            run_script = os.path.join(root_dir, 'run.sh')
            
            # 执行钉钉最近7天报告生成和推送命令（确保包含周末数据）
            cmd = [run_script, 'dingpush', 'recent-report', '7']
            
            # 如果 scheduler 配置了 debug_mode，则给 run.sh 传递 --debug 参数
            if self.debug_mode:
                cmd.append('--debug') # run.sh 的全局 --debug
                logger.info("以调试模式运行钉钉周报任务 (通过 run.sh --debug)")
                
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info(f"钉钉推送任务执行成功：\n{stdout}")
            else:
                logger.error(f"钉钉推送任务执行失败：\n{stderr}")
        except Exception as e:
            logger.error(f"执行钉钉推送任务出错：{e}")

    def check_and_run(self):
        """检查并运行定时任务"""
        while self.running:
            self.load_config()  # 每次循环重新加载配置，允许动态修改
            
            # 检查每日任务
            if self.should_run_task():
                logger.info(f"达到每日任务时间 {self.daily_task_time}，启动任务...")
                self.run_daily_task()
            
            # 检查钉钉推送任务
            if self.should_push_dingtalk():
                logger.info(f"达到钉钉推送时间 {self.dingtalk_push_time}，启动钉钉推送...")
                self.run_dingtalk_push()
            
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
