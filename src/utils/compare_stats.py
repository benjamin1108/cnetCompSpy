#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import argparse
from tabulate import tabulate

# 定义颜色代码
GREEN = '\033[92m'  # 绿色
RED = '\033[91m'    # 红色
NC = '\033[0m'      # 无颜色

# 带颜色的对号和叉号
GREEN_CHECK = f"{GREEN}✓{NC}"
RED_CROSS = f"{RED}✗{NC}"

# 添加项目根目录到路径
base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, base_dir)

# 导入共享库
from src.utils.stats_analyzer import StatsAnalyzer

def main():
    parser = argparse.ArgumentParser(description='比较元数据和实际文件统计')
    parser.add_argument('--detailed', action='store_true', help='显示详细文件信息')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--tasks-only', action='store_true', help='只显示未完成任务的文件')
    args = parser.parse_args()
    
    # 创建统计分析器
    analyzer = StatsAnalyzer()
    
    if args.json:
        # 生成JSON格式的数据
        json_data = analyzer.generate_json_data(args.detailed)
        
        # 如果指定了输出文件，写入文件
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"JSON数据已写入: {args.output}")
        else:
            # 否则打印到标准输出
            # 确保JSON格式正确
            print(json.dumps(json_data, ensure_ascii=False, indent=2, separators=(',', ': ')))
        
        # 在JSON模式下不打印表格
        return
    else:
        # 原始的表格输出
        analyzer.load_metadata_files()
        analyzer.get_raw_files()
        analyzer.get_analysis_files()
        
        stats = analyzer.compare_metadata_with_files(args.detailed)
        summary_table, details = analyzer.format_stats(stats, args.detailed)
        
        # 将布尔值转换为带颜色的对号和叉号
        for i, detail in enumerate(details):
            for j, file_detail in enumerate(detail['files']):
                for k in range(1, len(file_detail)):
                    details[i]['files'][j][k] = GREEN_CHECK if file_detail[k] else RED_CROSS
        
        # 打印摘要表格
        print("\n=== 文件统计摘要 ===")
        print(tabulate(
            summary_table,
            headers=['Vendor', 'Type', 'Files', 'Meta-C', 'Meta-A', 'AIFileExist', 'AITaskDone'],
            tablefmt='pretty',
            stralign='center',
            numalign='center'
        ))
        
        # 如果需要详细信息，打印文件详情
        if args.detailed and details:
            # 如果只显示未完成任务的文件
            if args.tasks_only:
                print("\n=== 未完成任务的文件 ===")
                incomplete_files_found = False
                
                for vendor_detail in details:
                    # 过滤出未完成任务的文件（不在分析元数据中或任务未完成）
                    incomplete_files = [file for file in vendor_detail['files'] if RED_CROSS in file[2] or RED_CROSS in file[4]]
                    
                    if incomplete_files:
                        incomplete_files_found = True
                        print(f"\n{vendor_detail['vendor']} - {vendor_detail['source_type']}:")
                        print(tabulate(
                            incomplete_files,
                            headers=['File', 'Meta-C', 'Meta-A', 'AIFileExist', 'AITaskDone'],
                            tablefmt='pretty',
                            stralign='left',
                            numalign='center',
                            maxcolwidths=[30, 10, 10, 10, 10]
                        ))
                
                if not incomplete_files_found:
                    print("\n所有任务都已完成！")
            else:
                # 显示所有文件的详细信息
                print("\n=== 文件详细信息 ===")
                for vendor_detail in details:
                    print(f"\n{vendor_detail['vendor']} - {vendor_detail['source_type']}:")
                    print(tabulate(
                        vendor_detail['files'],
                        headers=['File', 'Meta-C', 'Meta-A', 'AIFileExist', 'AITaskDone'],
                        tablefmt='pretty',
                        stralign='left',
                        numalign='center',
                        maxcolwidths=[30, 10, 10, 10, 10]
                    ))

if __name__ == "__main__":
    main()
