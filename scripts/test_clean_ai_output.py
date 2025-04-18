#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.ai_analyzer.analyzer import AIAnalyzer

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_clean_ai_output():
    """测试_clean_ai_output方法对中英文混合标题的处理能力"""
    
    # 创建一个简单的配置
    config = {
        'ai_analyzer': {
            'api_key': 'dummy_key',
            'api_base': 'https://api.example.com',
            'model': 'test-model'
        }
    }
    
    # 创建AIAnalyzer实例
    analyzer = AIAnalyzer(config)
    
    # 测试用例：中英文混合的标题
    test_cases = [
        # 正常情况：AI模型直接返回标题
        {
            "input": "[解决方案] 使用AWS CloudFront和Lambda@Edge优化网站性能",
            "expected": "[解决方案] 使用AWS CloudFront和Lambda@Edge优化网站性能",
            "task_type": "AI标题翻译"
        },
        # 带有解释性前缀的情况
        {
            "input": "I understand that you want me to analyze the article and provide a translated title with the appropriate prefix based on the content type. Here is the result:\n\n[解决方案] 使用AWS CloudFront和Lambda@Edge优化网站性能",
            "expected": "[解决方案] 使用AWS CloudFront和Lambda@Edge优化网站性能",
            "task_type": "AI标题翻译"
        },
        # 多行解释的情况
        {
            "input": "Based on the article content, I've analyzed that this is a solution-oriented post.\n\nHere is the translated title:\n\n[解决方案] 使用AWS CloudFront和Lambda@Edge优化网站性能",
            "expected": "[解决方案] 使用AWS CloudFront和Lambda@Edge优化网站性能",
            "task_type": "AI标题翻译"
        },
        # 中英文混合且带有特殊字符的情况
        {
            "input": "I understand your request. Here's the translated title:\n\n[新功能] AWS EC2实例新增G5g类型，支持ARM架构和NVIDIA T4G GPU加速",
            "expected": "[新功能] AWS EC2实例新增G5g类型，支持ARM架构和NVIDIA T4G GPU加速",
            "task_type": "AI标题翻译"
        },
        # 没有标签前缀的情况
        {
            "input": "Here is the translated title:\n\nAWS Lambda函数现已支持Node.js 18.x运行时环境",
            "expected": "AWS Lambda函数现已支持Node.js 18.x运行时环境",
            "task_type": "AI标题翻译"
        },
        # 非标题翻译任务的情况
        {
            "input": "I've analyzed the article as requested. Here's my competitive analysis:\n\n# 竞争分析\n\n## 产品概述\nAWS Lambda函数现已支持Node.js 18.x运行时环境，这是一项重要更新...",
            "expected": "# 竞争分析\n\n## 产品概述\nAWS Lambda函数现已支持Node.js 18.x运行时环境，这是一项重要更新...",
            "task_type": "AI竞争分析"
        }
    ]
    
    # 运行测试
    for i, case in enumerate(test_cases):
        input_text = case["input"]
        expected_output = case["expected"]
        task_type = case["task_type"]
        
        # 调用_clean_ai_output方法
        actual_output = analyzer._clean_ai_output(input_text, task_type)
        
        # 检查结果
        if actual_output == expected_output:
            logger.info(f"测试用例 {i+1} 通过!")
        else:
            logger.error(f"测试用例 {i+1} 失败!")
            logger.error(f"预期输出: {expected_output}")
            logger.error(f"实际输出: {actual_output}")
            logger.error(f"差异: {set(expected_output) - set(actual_output)}")
    
    logger.info("所有测试完成!")

if __name__ == "__main__":
    test_clean_ai_output()
