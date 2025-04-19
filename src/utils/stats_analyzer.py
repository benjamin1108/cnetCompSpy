#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import glob
from datetime import datetime
from collections import defaultdict
from src.utils.metadata_manager import MetadataManager

class StatsAnalyzer:
    """统计分析器，用于分析元数据和文件统计信息"""
    
    def __init__(self, base_dir=None):
        """初始化统计分析器"""
        if base_dir is None:
            # 默认使用项目根目录
            self.base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        else:
            self.base_dir = base_dir
        
        # 初始化数据
        self.metadata_manager = MetadataManager(base_dir)
        self.all_metadata = {}
        self.crawler_metadata = {}
        self.analysis_metadata = self.metadata_manager.get_all_analysis_metadata()
        self.raw_files = defaultdict(lambda: defaultdict(list))
        self.analysis_files = defaultdict(lambda: defaultdict(list))
        self.tasks = []
        
        # 加载配置文件中的任务列表
        self._load_tasks()
    
    def _load_tasks(self):
        """加载配置文件中的任务列表"""
        config_path = os.path.join(self.base_dir, 'config.yaml')
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f) if config_path.endswith('.json') else yaml.safe_load(f)
                    self.tasks = [task.get('type') for task in config.get('ai_analyzer', {}).get('tasks', []) if task.get('type')]
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def load_metadata_files(self, verbose=True):
        """加载所有metadata文件"""
        if verbose:
            print("开始加载元数据文件...")
        
        # 使用MetadataManager加载元数据
        self.analysis_metadata = self.metadata_manager.get_all_analysis_metadata()
        
        # 获取所有爬虫元数据
        crawler_metadata = self.metadata_manager.get_all_crawler_metadata()
        
        # 处理爬虫元数据
        for vendor, vendor_data in crawler_metadata.items():
            for source_type, source_data in vendor_data.items():
                for url, file_data in source_data.items():
                    filepath = file_data.get('filepath', '')
                    if filepath:
                        self.crawler_metadata[filepath] = {
                            'url': url,
                            'title': file_data.get('title', ''),
                            'crawl_time': file_data.get('crawl_time', '')
                        }
        
        # 打印加载信息
        if verbose:
            # 打印分析元数据信息
            print(f"已加载元数据文件: analysis_metadata.json 包含 {len(self.analysis_metadata)} 条记录")
            
            # 打印爬虫元数据信息
            total_crawler_records = 0
            for vendor, vendor_data in crawler_metadata.items():
                for source_type, source_data in vendor_data.items():
                    total_crawler_records += len(source_data)
                    print(f"已加载元数据文件: {vendor}/{source_type} 包含 {len(source_data)} 条记录")
            
            print(f"已加载爬虫元数据文件: crawler_metadata.json 包含 {total_crawler_records} 条记录")
        
        return self.all_metadata
    
    def get_raw_files(self, verbose=True):
        """获取所有原始文件"""
        if verbose:
            print("\n获取原始文件信息...")
        
        raw_dir = os.path.join(self.base_dir, 'data', 'raw')
        raw_files = glob.glob(os.path.join(raw_dir, '**', '*.md'), recursive=True)
        
        # 按厂商和类型分组
        for file_path in raw_files:
            # 从路径中提取厂商和类型
            # 路径格式: data/raw/vendor/type/file.md
            parts = file_path.split(os.sep)
            if len(parts) >= 4:
                vendor = parts[-3]  # 倒数第三个部分是厂商
                source_type = parts[-2]  # 倒数第二个部分是类型
                self.raw_files[vendor][source_type].append(file_path)
        
        return self.raw_files
    
    def get_analysis_files(self, verbose=True):
        """获取所有分析文件"""
        if verbose:
            print("\n获取分析文件信息...")
        
        analysis_dir = os.path.join(self.base_dir, 'data', 'analysis')
        analysis_files = glob.glob(os.path.join(analysis_dir, '**', '*.md'), recursive=True)
        
        # 按厂商和类型分组
        for file_path in analysis_files:
            # 从路径中提取厂商和类型
            # 路径格式: data/analysis/vendor/type/file.md
            parts = file_path.split(os.sep)
            if len(parts) >= 4:
                vendor = parts[-3]  # 倒数第三个部分是厂商
                source_type = parts[-2]  # 倒数第二个部分是类型
                self.analysis_files[vendor][source_type].append(file_path)
        
        return self.analysis_files
    
    def extract_file_info(self, file_path):
        """从文件路径和内容中提取文件信息"""
        file_info = {
            'path': file_path,
            'filename': os.path.basename(file_path),
            'size': os.path.getsize(file_path),
            'mtime': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
            'title': '',
            'url': '',
            'crawl_time': ''
        }
        
        # 尝试从文件内容中提取标题和URL
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                for line in lines[:20]:  # 只检查前20行
                    if line.startswith('# '):
                        file_info['title'] = line[2:].strip()
                    elif '**原始链接:**' in line:
                        url_part = line.split('**原始链接:**')[1].strip()
                        # 提取URL，去除可能的Markdown链接格式
                        if '[' in url_part and '](' in url_part and ')' in url_part:
                            url_part = url_part.split('](')[1].split(')')[0]
                        file_info['url'] = url_part
                    elif '**发布时间:**' in line:
                        file_info['crawl_time'] = line.split('**发布时间:**')[1].strip()
        except Exception as e:
            print(f"提取文件信息失败: {file_path} - {e}")
        
        return file_info
    
    def check_analysis_tasks(self, file_path):
        """检查文件的分析任务是否全部完成"""
        # 使用MetadataManager检查分析任务是否完成
        return self.metadata_manager.check_analysis_tasks(file_path, self.tasks)
    
    def compare_metadata_with_files(self, detailed=False, verbose=True):
        """比较元数据和实际文件"""
        if verbose:
            print("\n比较元数据和实际文件...")
        
        # 确保数据已加载
        if not self.all_metadata:
            self.load_metadata_files(verbose)
        
        if not self.raw_files:
            self.get_raw_files(verbose)
        
        if not self.analysis_files:
            self.get_analysis_files(verbose)
        
        # 统计每个厂商和类型的文件数量
        stats = {}
        
        # 遍历所有原始文件
        for vendor, vendor_data in self.raw_files.items():
            if vendor not in stats:
                stats[vendor] = {}
            
            for source_type, files in vendor_data.items():
                if source_type not in stats[vendor]:
                    stats[vendor][source_type] = {
                        'metadata_count': 0,
                        'raw_count': len(files),
                        'analysis_count': 0,
                        'files': []
                    }
                else:
                    stats[vendor][source_type]['raw_count'] = len(files)
                
                # 收集文件详情，用于计算统计信息
                # 如果detailed=False，只收集基本信息用于统计
                # 如果detailed=True，收集完整信息用于显示详细表格
                for file_path in files:
                    # 查找对应的元数据
                    metadata_info = self.crawler_metadata.get(file_path, {})
                    
                    # 查找对应的分析文件
                    analysis_path = file_path.replace('/raw/', '/analysis/')
                    analysis_exists = os.path.exists(analysis_path)
                    
                    # 标准化文件路径
                    normalized_path = os.path.relpath(file_path, self.base_dir)
                    
                    # 检查分析任务是否全部完成
                    tasks_completed = self.check_analysis_tasks(file_path)
                    
                    file_data = {
                        'filename': os.path.basename(file_path),
                        'in_crawler_metadata': bool(metadata_info),
                        'has_analysis': analysis_exists,
                        'in_analysis_metadata': normalized_path in self.analysis_metadata,
                        'tasks_completed': tasks_completed
                    }
                    
                    # 如果需要详细信息，添加更多字段
                    if detailed:
                        file_info = self.extract_file_info(file_path)
                        file_data.update({
                            'path': file_path,
                            'title': file_info['title'] or metadata_info.get('title', ''),
                            'url': file_info['url'] or metadata_info.get('url', ''),
                            'crawl_time': file_info['crawl_time'] or metadata_info.get('crawl_time', ''),
                            'file_mtime': file_info['mtime']
                        })
                    
                    stats[vendor][source_type]['files'].append(file_data)
        
        # 遍历所有分析文件
        for vendor, vendor_data in self.analysis_files.items():
            if vendor not in stats:
                stats[vendor] = {}
            
            for source_type, files in vendor_data.items():
                if source_type not in stats[vendor]:
                    stats[vendor][source_type] = {
                        'metadata_count': 0,
                        'raw_count': 0,
                        'analysis_count': len(files),
                        'files': []
                    }
                else:
                    stats[vendor][source_type]['analysis_count'] = len(files)
        
        # 统计元数据中的文件数量
        for filepath, metadata_info in self.crawler_metadata.items():
            # 从路径中提取厂商和类型
            # 路径格式: data/raw/vendor/type/file.md
            parts = filepath.split(os.sep)
            if len(parts) >= 4:
                vendor = parts[-3]  # 倒数第三个部分是厂商
                source_type = parts[-2]  # 倒数第二个部分是类型
                
                if vendor not in stats:
                    stats[vendor] = {}
                
                if source_type not in stats[vendor]:
                    stats[vendor][source_type] = {
                        'metadata_count': 1,
                        'raw_count': 0,
                        'analysis_count': 0,
                        'files': []
                    }
                else:
                    stats[vendor][source_type]['metadata_count'] += 1
        
        return stats
    
    def format_stats(self, stats, detailed=False, verbose=True):
        """格式化统计结果"""
        if verbose:
            print("\n格式化统计结果...")
        
        summary_table = []
        details = []
        
        for vendor, vendor_data in stats.items():
            for source_type, source_stats in vendor_data.items():
                # 计算各种状态的文件数量
                in_crawler_count = 0
                in_analysis_count = 0
                has_file_count = 0
                tasks_done_count = 0
                
                if 'files' in source_stats:
                    for file_info in source_stats['files']:
                        if file_info['in_crawler_metadata']:
                            in_crawler_count += 1
                        if file_info['in_analysis_metadata']:
                            in_analysis_count += 1
                        if file_info['has_analysis']:
                            has_file_count += 1
                        if file_info.get('tasks_completed', False):
                            tasks_done_count += 1
                
                # 添加摘要行
                summary_table.append([
                    vendor,
                    source_type,
                    source_stats['raw_count'],
                    in_crawler_count,
                    in_analysis_count,
                    has_file_count,
                    tasks_done_count
                ])
                
                # 如果需要详细信息，添加文件详情
                if detailed and 'files' in source_stats:
                    vendor_details = []
                    for file_info in source_stats['files']:
                        vendor_details.append([
                            file_info['filename'],
                            file_info['in_crawler_metadata'],
                            file_info['in_analysis_metadata'],
                            file_info['has_analysis'],
                            file_info.get('tasks_completed', False)
                        ])
                    
                    if vendor_details:
                        details.append({
                            'vendor': vendor,
                            'source_type': source_type,
                            'files': vendor_details
                        })
        
        return summary_table, details
    
    def generate_json_data(self, detailed=False):
        """生成JSON格式的统计数据，用于Web服务器"""
        stats = self.compare_metadata_with_files(detailed, verbose=False)
        
        # 转换为JSON友好的格式
        json_data = {
            'summary': [],
            'details': {}
        }
        
        # 添加摘要数据
        for vendor, vendor_data in stats.items():
            for source_type, source_stats in vendor_data.items():
                # 计算各种状态的文件数量
                in_crawler_count = 0
                in_analysis_count = 0
                has_file_count = 0
                tasks_done_count = 0
                
                if 'files' in source_stats:
                    for file_info in source_stats['files']:
                        if file_info['in_crawler_metadata']:
                            in_crawler_count += 1
                        if file_info['in_analysis_metadata']:
                            in_analysis_count += 1
                        if file_info['has_analysis']:
                            has_file_count += 1
                        if file_info.get('tasks_completed', False):
                            tasks_done_count += 1
                
                json_data['summary'].append({
                    'vendor': vendor,
                    'source_type': source_type,
                    'metadata_count': source_stats['metadata_count'],
                    'raw_count': source_stats['raw_count'],
                    'analysis_count': source_stats['analysis_count'],
                    'metadata_match': source_stats['metadata_count'] == source_stats['raw_count'],
                    'analysis_match': source_stats['raw_count'] == source_stats['analysis_count'],
                    'in_crawler_count': in_crawler_count,
                    'in_analysis_count': in_analysis_count,
                    'has_file_count': has_file_count,
                    'tasks_done_count': tasks_done_count
                })
        
        # 如果需要详细信息，添加文件详情
        if detailed:
            for vendor, vendor_data in stats.items():
                if vendor not in json_data['details']:
                    json_data['details'][vendor] = {}
                
                for source_type, source_stats in vendor_data.items():
                    if 'files' in source_stats:
                        json_data['details'][vendor][source_type] = []
                        
                        for file_info in source_stats['files']:
                            json_data['details'][vendor][source_type].append({
                                'filename': file_info['filename'],
                                'title': file_info['title'],
                                'url': file_info['url'],
                                'crawl_time': file_info['crawl_time'],
                                'file_mtime': file_info['file_mtime'],
                                'in_crawler_metadata': file_info['in_crawler_metadata'],
                                'in_analysis_metadata': file_info['in_analysis_metadata'],
                                'has_analysis': file_info['has_analysis'],
                                'tasks_completed': file_info.get('tasks_completed', False)
                            })
        
        return json_data
