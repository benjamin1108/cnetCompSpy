#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报告生成器模块

为任何日期范围生成 AI 驱动的云厂商更新报告。
支持周报和最近 N 天报告两种模式。
"""

import datetime
import logging
import os
import sys
import argparse
import re
from typing import Dict, Optional, Any, List
from datetime import date, timedelta

# 动态将项目根目录添加到 sys.path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.dirname(_SCRIPT_DIR)
_PROJECT_ROOT = os.path.dirname(_SRC_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.utils.config_loader import get_config 
from src.utils.colored_logger import setup_colored_logging
from src.ai_analyzer.model_manager import ModelManager
from src.ai_analyzer.exceptions import AIAnalyzerError


class ReportGenerator:
    """为日期范围内的云厂商更新生成格式化报告"""
    
    def __init__(self, config: dict, start_date: date, end_date: date, report_type: str = "weekly"):
        """
        初始化报告生成器
        
        参数:
            config: 完整配置字典
            start_date: 日期范围开始（包含）
            end_date: 日期范围结束（包含）
            report_type: 报告类型 ("weekly" 或 "recent")
        """
        self.config = config
        self.start_date = start_date
        self.end_date = end_date
        self.report_type = report_type
        self.logger = logging.getLogger(f"{__name__}.ReportGenerator")
        
        # 从配置中获取路径和厂商信息
        raw_data_config = config.get("data_paths", {})
        self.base_path = raw_data_config.get("raw_articles_base", "data/raw")
        self.vendors = config.get("vendors_to_scan", ["aws", "azure", "gcp", "huawei"])
        
        # 从配置中获取报告相关设置
        self.reporting_config = config.get("reporting", {})
        self.beautification_config = self.reporting_config.get("beautification", {})
        
        # 优先使用 platform_url，如果没有则使用 site_base_url
        self.platform_url = self.beautification_config.get("platform_url") or \
                           self.reporting_config.get("site_base_url", "http://cnetspy.site")
        
    def collect_articles(self) -> List[Dict[str, str]]:
        """
        收集日期范围内的所有文章
        
        返回:
            文章数据字典列表
        """
        if not os.path.isdir(self.base_path):
            self.logger.error(f"原始数据基础路径未找到或不是一个目录: {self.base_path}")
            return []
        
        all_articles_data = []
        self.logger.info(
            f"正在扫描从 {self.start_date.isoformat()} 到 {self.end_date.isoformat()} "
            f"的原始文章，供应商: {self.vendors}"
        )
        
        for vendor in self.vendors:
            vendor_base_path = os.path.join(self.base_path, vendor)
            if not os.path.isdir(vendor_base_path):
                self.logger.debug(f"供应商基础路径未找到或不是目录，跳过: {vendor_base_path}")
                continue
            
            try:
                subcategories = [
                    d for d in os.listdir(vendor_base_path) 
                    if os.path.isdir(os.path.join(vendor_base_path, d))
                ]
                if not subcategories:
                    self.logger.debug(f"在 {vendor_base_path} 中未找到子类别，跳过此供应商。")
                    continue
            except OSError as e:
                self.logger.warning(f"无法列出 {vendor_base_path} 中的子类别: {e}")
                continue
            
            for subcategory in subcategories:
                subcategory_path = os.path.join(vendor_base_path, subcategory)
                self.logger.debug(f"正在扫描目录: {subcategory_path}")
                
                try:
                    for filename in os.listdir(subcategory_path):
                        if not filename.endswith(".md"):
                            continue
                        
                        # 解析文件日期
                        file_date_obj = self._parse_date_from_filename(filename)
                        if file_date_obj is None:
                            continue
                        
                        # 检查日期是否在范围内
                        if not (self.start_date <= file_date_obj <= self.end_date):
                            continue
                        
                        # 读取文章内容
                        file_path = os.path.join(subcategory_path, filename)
                        article_data = self._read_article_file(
                            file_path, filename, vendor, subcategory, file_date_obj
                        )
                        
                        if article_data:
                            all_articles_data.append(article_data)
                            
                except OSError as e:
                    self.logger.warning(f"无法列出 {subcategory_path} 中的文件: {e}")
        
        if not all_articles_data:
            self.logger.info(f"在指定日期范围内未找到原始文章。")
            return []
        
        self.logger.info(f"成功收集到 {len(all_articles_data)} 篇原始文章的数据。")
        return all_articles_data
    
    def _parse_date_from_filename(self, filename: str) -> Optional[date]:
        """从文件名解析日期"""
        file_date_obj = None
        
        # 尝试 AWS 格式: YYYY_MM_DD_*.md
        if '_' in filename:
            date_part_str = filename.split('_', 3)
            if len(date_part_str) >= 3:
                try:
                    file_date_str = f"{date_part_str[0]}-{date_part_str[1]}-{date_part_str[2]}"
                    file_date_obj = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
                    self.logger.debug(f"文件 {filename}: 使用AWS格式解析日期 {file_date_obj}")
                    return file_date_obj
                except ValueError:
                    pass
        
        # 尝试 Azure 格式: YYYY-MM-DD_*.md
        if '-' in filename:
            underscore_pos = filename.find('_')
            if underscore_pos > 0:
                date_part = filename[:underscore_pos]
                if len(date_part) == 10 and date_part.count('-') == 2:
                    try:
                        file_date_obj = datetime.datetime.strptime(date_part, "%Y-%m-%d").date()
                        self.logger.debug(f"文件 {filename}: 使用Azure格式解析日期 {file_date_obj}")
                        return file_date_obj
                    except ValueError:
                        pass
        
        self.logger.debug(
            f"文件 {filename} 不匹配任何已知的日期格式 "
            f"(AWS: YYYY_MM_DD_*, Azure: YYYY-MM-DD_*)"
        )
        return None
    
    def _read_article_file(
        self, file_path: str, filename: str, vendor: str, 
        subcategory: str, file_date: date
    ) -> Optional[Dict[str, str]]:
        """读取文章文件并提取内容和元数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            original_url = ""
            raw_content_lines = []
            in_metadata_section = True
            
            for line_content in lines:
                stripped_line = line_content.strip()
                
                # 提取原始链接
                if original_url == "" and stripped_line.startswith("**原始链接:**"):
                    match = re.search(r'\((https?://[^\)]+)\)', stripped_line)
                    if match:
                        original_url = match.group(1)
                        self.logger.debug(f"文件 {filename}: 找到URL: {original_url}")
                    else:
                        potential_url = stripped_line.replace("**原始链接:**", "").strip()
                        if potential_url.startswith("http"):
                            original_url = potential_url
                
                # 检查元数据分隔符
                if stripped_line == "---" and in_metadata_section:
                    in_metadata_section = False
                    continue
                
                if not in_metadata_section:
                    raw_content_lines.append(line_content)
            
            raw_content = "".join(raw_content_lines)
            
            # 后备逻辑
            if not original_url and lines:
                first_line = lines[0].strip()
                if first_line.startswith("http"):
                    original_url = first_line
                    if not raw_content.strip():
                        raw_content = "".join(lines[1:])
                elif not raw_content.strip():
                    raw_content = "".join(lines)
            
            # 生成占位符 URL（如果需要）
            if not original_url:
                original_url = f"PLACEHOLDER_{vendor}_{subcategory}_{filename}"
                self.logger.debug(f"文件 {filename}: 生成占位符URL: {original_url}")
            
            if not raw_content.strip():
                self.logger.warning(f"文件 {filename} 的有效原始内容为空，跳过。")
                return None
            
            source_info = f"来源: {vendor}/{subcategory}/{file_date.isoformat()}/{filename}"
            
            return {
                "raw_content": raw_content,
                "vendor": vendor,
                "subcategory": subcategory,
                "original_filename": filename,
                "source_info_for_llm": source_info,
                "original_url": original_url,
                "date_published": file_date.isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"无法读取或处理文件 {file_path}: {e}")
            return None
    
    def generate_report(self, model_client: Any) -> Optional[str]:
        """
        生成完整的 markdown 报告
        
        参数:
            model_client: LLM 客户端实例
            
        返回:
            Markdown 报告内容，如果生成失败则返回 None
        """
        # 收集文章
        articles_data = self.collect_articles()
        
        if not articles_data:
            self.logger.info("没有文章数据，生成空报告框架。")
            # 仍然生成一个报告，但标记为无更新
            return self._generate_empty_report()
        
        # 准备 LLM 输入
        llm_input = self._prepare_llm_input(articles_data)
        if not llm_input:
            self.logger.warning("准备的LLM输入内容为空，无法生成报告。")
            return None
        
        self.logger.info(
            f"已为 {len(articles_data)} 篇文章准备好合并的LLM输入，"
            f"总长度约: {len(llm_input)} chars"
        )
        
        # 调用 LLM 生成报告内容
        generated_content = self._call_llm(model_client, llm_input)
        if not generated_content:
            self.logger.error("LLM未能生成有效内容。")
            return self._generate_empty_report()
        
        # 替换 URL
        processed_content = self._replace_urls(generated_content, articles_data)
        
        # 组合最终报告
        final_report = self._assemble_final_report(processed_content, len(articles_data))
        
        return final_report
    
    def _prepare_llm_input(self, articles_data: List[Dict[str, str]]) -> str:
        """准备发送给 LLM 的输入"""
        llm_input_parts = []
        for article in articles_data:
            llm_input_parts.append(
                f"--- 文章开始 ---\n"
                f"来源信息: {article['source_info_for_llm']}\n"
                f"原文URL: {article['original_url']}\n"
                f"文章原始内容:\n{article['raw_content']}\n"
                f"--- 文章结束 ---\n\n"
            )
        return "\n".join(llm_input_parts)
    
    def _call_llm(self, model_client: Any, prompt: str) -> Optional[str]:
        """调用 LLM 生成报告内容"""
        try:
            generated_content = model_client.predict(prompt=prompt)
            if isinstance(generated_content, str) and generated_content.strip():
                self.logger.info("LLM成功返回报告内容。")
                return generated_content
            else:
                self.logger.error("LLM返回的报告内容为空或无效。")
                return None
        except Exception as e:
            self.logger.error(f"调用LLM生成整体报告时出错: {e}", exc_info=True)
            return None
    
    def _replace_urls(self, content: str, articles_data: List[Dict[str, str]]) -> str:
        """将原始 URL 替换为内部链接"""
        processed_content = content
        replacement_attempts = 0
        successful_replacements = 0
        
        self.logger.info("开始在LLM生成的报告内容中替换原文URL为内部链接...")
        
        for article_info in articles_data:
            original_url = article_info.get("original_url")
            source_info = article_info.get('source_info_for_llm', '未知文章')
            
            if not original_url or not isinstance(original_url, str) or not original_url.strip():
                self.logger.warning(f"跳过文章 '{source_info}' 的URL替换: URL无效")
                continue
            
            # 检查是否是有效的 URL 或占位符 URL
            is_placeholder = original_url.startswith("PLACEHOLDER_")
            is_valid_http = original_url.strip().startswith("http")
            
            if not is_placeholder and not is_valid_http:
                self.logger.warning(f"跳过文章 '{source_info}' 的URL替换: URL格式无效")
                continue
            
            replacement_attempts += 1
            
            # 构建内部链接
            vendor = article_info.get("vendor", "unknown_vendor")
            subcategory = article_info.get("subcategory", "unknown_subcategory")
            filename = article_info.get("original_filename")
            
            if not filename:
                self.logger.warning(f"文章 '{source_info}' 缺少文件名，无法构建内部URL")
                continue
            
            internal_link_path = f"analysis/document/{vendor}/{subcategory}/{filename}"
            internal_link_full = f"{self.platform_url}/{internal_link_path}"
            
            pattern_to_find = f"]({original_url})"
            replacement_pattern = f"]({internal_link_full})"
            
            if pattern_to_find in processed_content:
                processed_content = processed_content.replace(pattern_to_find, replacement_pattern)
                successful_replacements += 1
                self.logger.debug(f"成功替换URL: '{original_url}' -> '{internal_link_full}'")
            else:
                self.logger.warning(f"未找到URL模式 '{pattern_to_find}' 在报告中")
        
        self.logger.info(
            f"URL替换完成。尝试次数: {replacement_attempts}, "
            f"成功次数: {successful_replacements}"
        )
        
        return processed_content
    
    def _generate_empty_report(self) -> str:
        """生成空报告（无更新时）"""
        no_updates_text = self.beautification_config.get(
            "no_updates_text", 
            "本周暂无重要更新内容。"
        )
        return self._assemble_final_report(no_updates_text, 0)
    
    def _assemble_final_report(self, content: str, article_count: int) -> str:
        """组合最终的 Markdown 报告"""
        final_parts = []
        
        # Banner
        banner_url = self.beautification_config.get("banner_url", "")
        if banner_url:
            final_parts.append(f"![]({banner_url})\n")
        
        # 标题和日期范围
        if self.report_type == "weekly":
            title_prefix = self.beautification_config.get("report_title_prefix", "【云技术周报】")
            intro = self.beautification_config.get(
                "intro_text", 
                "汇集本周主要云厂商的技术产品动态，助您快速掌握核心变化。"
            )
            date_range_str = (
                f"{self.start_date.strftime('%Y年%m月%d日')} - "
                f"{self.end_date.strftime('%Y年%m月%d日')}"
            )
            title = f"{title_prefix} {date_range_str} 竞争动态速览"
        else:  # recent
            title_prefix = self.beautification_config.get("recent_title_prefix", "【云技术动态】")
            intro = self.beautification_config.get(
                "recent_intro_text",
                "汇集近期主要云厂商的技术产品动态，助您快速掌握核心变化。"
            )
            days_diff = (self.end_date - self.start_date).days + 1
            date_range_str = (
                f"{self.start_date.strftime('%Y年%m月%d日')} - "
                f"{self.end_date.strftime('%Y年%m月%d日')}"
            )
            title = f"{title_prefix} 近{days_diff}天 {date_range_str} 竞争动态速览"
        
        final_parts.append(f"# {title}\n")
        final_parts.append(f"{intro}\n")
        
        # 内容
        final_parts.append(content)
        if not content.endswith('\n'):
            final_parts.append("\n")
        
        # 页脚
        footer_text = self.beautification_config.get("footer_text", "由云竞争情报分析平台自动汇总。")
        platform_link_text = self.beautification_config.get("platform_link_text", "前往平台查看更多详情")
        
        if self.platform_url and platform_link_text:
            final_parts.append(f"{footer_text} [{platform_link_text}]({self.platform_url})")
        else:
            final_parts.append(footer_text)
        
        self.logger.info(f"报告Markdown内容已生成 (处理了 {article_count} 篇文章)。")
        return "\n".join(final_parts)
    
    def save_report(self, content: str) -> str:
        """
        保存报告到文件
        
        参数:
            content: Markdown 报告内容
            
        返回:
            保存的报告文件路径
        """
        output_dir_config = self.config.get("output_paths", {})
        output_dir = output_dir_config.get("reports_dir", "data/reports")
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            self.logger.info(f"已确保输出目录存在: {output_dir}")
        except OSError as e:
            self.logger.error(f"无法创建输出目录 {output_dir}: {e}")
            raise
        
        # 生成文件名
        if self.report_type == "weekly":
            filename_pattern = output_dir_config.get(
                "weekly_filename_pattern",
                "weekly_report_{start_date}_to_{end_date}.md"
            )
            filename = filename_pattern.format(
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
        else:  # recent
            days_diff = (self.end_date - self.start_date).days + 1
            filename_pattern = output_dir_config.get(
                "recent_filename_pattern",
                "recent_{days}_days_report_{end_date}.md"
            )
            filename = filename_pattern.format(
                days=days_diff,
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
        
        output_filepath = os.path.join(output_dir, filename)
        
        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"成功将报告写入: {output_filepath}")
            return output_filepath
        except IOError as e:
            self.logger.error(f"写入报告文件 {output_filepath} 时出错: {e}")
            raise


# 便捷函数

def generate_weekly_report(config: dict) -> Optional[str]:
    """
    生成当前周（周一到今天）的报告
    
    参数:
        config: 配置字典
        
    返回:
        生成的报告文件路径，如果失败则返回 None
    """
    logger = logging.getLogger(__name__)
    
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    
    logger.info(f"生成周报: {start_of_week} 到 {today}")
    
    try:
        # 初始化 ModelManager 和获取 LLM 客户端
        ai_config = config.get("ai_analyzer")
        if not ai_config:
            logger.error("配置中未找到 'ai_analyzer' 部分")
            return None
        
        model_manager = ModelManager(ai_config=ai_config)
        
        # 加载提示模板
        prompt_file_path_config = config.get("prompt_paths", {})
        reporting_config = config.get("reporting", {})
        prompt_key = reporting_config.get("weekly_update_prompt_key", "weekly_updates")
        prompt_file_path = prompt_file_path_config.get(prompt_key, f"prompt/{prompt_key}.txt")
        
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        
        # 获取模型配置
        model_profile = reporting_config.get(
            "weekly_summary_model_profile",
            model_manager.active_model_profile_name
        )
        
        llm_client = model_manager.get_model_client(
            system_prompt_text=system_prompt,
            model_profile_name=model_profile
        )
        
        # 生成报告
        generator = ReportGenerator(config, start_of_week, today, "weekly")
        report_content = generator.generate_report(llm_client)
        
        if not report_content:
            logger.error("报告生成失败")
            return None
        
        # 保存报告
        output_path = generator.save_report(report_content)
        return output_path
        
    except Exception as e:
        logger.error(f"生成周报时出错: {e}", exc_info=True)
        return None



def generate_recent_report(config: dict, days: int) -> Optional[str]:
    """
    生成最近 N 天的报告
    
    参数:
        config: 配置字典
        days: 回溯的天数
        
    返回:
        生成的报告文件路径，如果失败则返回 None
    """
    logger = logging.getLogger(__name__)
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    
    logger.info(f"生成最近 {days} 天报告: {start_date} 到 {end_date}")
    
    try:
        # 初始化 ModelManager 和获取 LLM 客户端
        ai_config = config.get("ai_analyzer")
        if not ai_config:
            logger.error("配置中未找到 'ai_analyzer' 部分")
            return None
        
        model_manager = ModelManager(ai_config=ai_config)
        
        # 加载提示模板（使用与周报相同的提示）
        prompt_file_path_config = config.get("prompt_paths", {})
        reporting_config = config.get("reporting", {})
        prompt_key = reporting_config.get("recent_prompt_key", "weekly_updates")
        prompt_file_path = prompt_file_path_config.get(prompt_key, f"prompt/{prompt_key}.txt")
        
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        
        # 获取模型配置
        model_profile = reporting_config.get(
            "weekly_summary_model_profile",
            model_manager.active_model_profile_name
        )
        
        llm_client = model_manager.get_model_client(
            system_prompt_text=system_prompt,
            model_profile_name=model_profile
        )
        
        # 生成报告
        generator = ReportGenerator(config, start_date, end_date, "recent")
        report_content = generator.generate_report(llm_client)
        
        if not report_content:
            logger.error("报告生成失败")
            return None
        
        # 保存报告
        output_path = generator.save_report(report_content)
        return output_path
        
    except Exception as e:
        logger.error(f"生成最近 {days} 天报告时出错: {e}", exc_info=True)
        return None


# CLI 主函数

def main():
    """CLI 入口点"""
    parser = argparse.ArgumentParser(description="生成云厂商更新报告")
    parser.add_argument(
        '--mode',
        required=True,
        choices=['weekly', 'recent'],
        help='报告模式: weekly (本周) 或 recent (最近N天)'
    )
    parser.add_argument(
        '--days',
        type=int,
        help='最近N天（仅在 mode=recent 时需要）'
    )
    parser.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='设置日志级别 (默认: INFO)'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='自定义配置文件路径'
    )
    
    args = parser.parse_args()
    
    # 验证参数
    if args.mode == 'recent' and not args.days:
        parser.error("--mode recent 需要 --days 参数")
    
    if args.days and args.days <= 0:
        parser.error("--days 必须是正整数")
    
    # 设置日志
    numeric_log_level = getattr(logging, args.loglevel.upper())
    setup_colored_logging()
    logging.getLogger().setLevel(numeric_log_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"日志级别已设置为: {args.loglevel}")
    logger.info(f"开始生成报告，模式: {args.mode}")
    
    # 加载配置
    try:
        config = get_config(config_path=args.config)
        if not config:
            logger.error("配置加载失败")
            return 1
        logger.info("配置加载成功")
    except Exception as e:
        logger.error(f"加载配置时出错: {e}", exc_info=True)
        return 1
    
    # 生成报告
    try:
        if args.mode == 'weekly':
            output_path = generate_weekly_report(config)
        else:  # recent
            output_path = generate_recent_report(config, args.days)
        
        if output_path:
            logger.info(f"报告生成成功: {output_path}")
            print(output_path)  # 输出路径供 shell 脚本使用
            return 0
        else:
            logger.error("报告生成失败")
            return 1
            
    except Exception as e:
        logger.error(f"生成报告时发生错误: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
