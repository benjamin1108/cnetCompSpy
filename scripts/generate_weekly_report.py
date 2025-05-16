import datetime
import logging
import os
import sys
import argparse # 导入argparse用于处理命令行参数
import re # <--- Added import re
from typing import Dict, Optional, Any, List, Tuple # Added List and Tuple

# --- 动态将项目根目录添加到sys.path ---
# 确保当脚本从'scripts'目录或其他位置运行时，能够找到'src'模块。
# 获取当前脚本所在目录的绝对路径。
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 假设项目根目录是'scripts'目录的父目录。
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
# 如果项目根目录不在Python路径中，则添加到路径列表的开头。
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT) # 插入到开头以优先加载项目模块
# --- sys.path 修改结束 ---

from src.utils.config_loader import get_config 
from src.utils.colored_logger import setup_colored_logging

from src.ai_analyzer.model_manager import ModelManager
from src.ai_analyzer.exceptions import AIAnalyzerError, APIError 

def load_prompt_template(prompt_file_path: str) -> str:
    """从给定文件加载提示模板。"""
    logger = logging.getLogger(__name__)
    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"提示模板文件未找到: {prompt_file_path}")
        raise
    except Exception as e:
        logger.error(f"读取提示模板文件 {prompt_file_path} 时出错: {e}")
        raise

def get_all_raw_content_for_week(config: dict) -> List[Dict[str, str]]:
    """
    获取当前周（周一至周日）所有原始文章 (.md) 的内容及元数据。
    日期从文件名中解析 (例如 YYYY_MM_DD_*.md)。
    每篇文章信息以字典形式返回，包含原始内容、厂商、子类别、原始文件名等。
    假设原文URL在.md文件的第一行。
    """
    logger = logging.getLogger(__name__)
    raw_data_config = config.get("data_paths", {})
    base_path = raw_data_config.get("raw_articles_base", "data/raw")
    vendors = config.get("vendors_to_scan", ["aws", "azure", "gcp"])

    if not os.path.isdir(base_path):
        logger.error(f"原始数据基础路径未找到或不是一个目录: {base_path}")
        return []

    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    
    all_articles_data = [] # Changed variable name
    logger.info(f"正在扫描从 {start_of_week.isoformat()} 到 {today.isoformat()} 的原始文章，供应商: {vendors}")

    for vendor in vendors:
        vendor_base_path = os.path.join(base_path, vendor)
        if not os.path.isdir(vendor_base_path):
            logger.debug(f"供应商基础路径未找到或不是目录，跳过: {vendor_base_path}")
            continue

        try:
            subcategories = [d for d in os.listdir(vendor_base_path) if os.path.isdir(os.path.join(vendor_base_path, d))]
            if not subcategories:
                logger.debug(f"在 {vendor_base_path} 中未找到子类别，跳过此供应商。")
                continue
        except OSError as e_list_sub:
            logger.warning(f"无法列出 {vendor_base_path} 中的子类别: {e_list_sub}")
            continue
        
        for subcategory in subcategories:
            subcategory_path = os.path.join(vendor_base_path, subcategory)
            logger.info(f"正在扫描目录: {subcategory_path}") 

            try:
                for filename in os.listdir(subcategory_path):
                    if filename.endswith(".md"):
                        try:
                            date_part_str = filename.split('_', 3)
                            if len(date_part_str) >= 3:
                                file_date_str = f"{date_part_str[0]}-{date_part_str[1]}-{date_part_str[2]}"
                                file_date_obj = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
                                
                                if start_of_week <= file_date_obj <= today:
                                    is_target_day_for_week = False
                                    for i in range(today.weekday() + 1):
                                        current_iter_day = start_of_week + datetime.timedelta(days=i)
                                        if file_date_obj == current_iter_day:
                                            is_target_day_for_week = True
                                            break
                                    
                                    if is_target_day_for_week:
                                        file_path = os.path.join(subcategory_path, filename)
                                        try:
                                            with open(file_path, 'r', encoding='utf-8') as f_article:
                                                lines = f_article.readlines()
                                            
                                            original_url = ""
                                            raw_content_for_llm_lines = []
                                            # metadata_header_ended = False # Not strictly needed with new logic

                                            in_metadata_section = True 
                                            
                                            for line_idx, line_content in enumerate(lines):
                                                stripped_line = line_content.strip()
                                                
                                                if original_url == "" and stripped_line.startswith("**原始链接:**"):
                                                    match = re.search(r'\((https?://[^\)]+)\)', stripped_line) # Corrected regex escaping for ( and )
                                                    if match:
                                                        original_url = match.group(1)
                                                        logger.debug(f"文件 {filename}: 从'**原始链接:**'行通过正则找到URL: {original_url}")
                                                    else:
                                                        potential_url = stripped_line.replace("**原始链接:**", "").strip()
                                                        if potential_url.startswith("http://") or potential_url.startswith("https://"):
                                                            original_url = potential_url # This case is less likely if markdown link is used
                                                            logger.debug(f"文件 {filename}: 从'**原始链接:**'行直接提取URL (非正则匹配): {original_url}")
                                                
                                                if stripped_line == "---" and in_metadata_section:
                                                    in_metadata_section = False
                                                    continue 
                                                
                                                if not in_metadata_section:
                                                    raw_content_for_llm_lines.append(line_content)

                                            raw_content_for_llm = "".join(raw_content_for_llm_lines)

                                            # Fallback logic if new parsing fails or "---" delimiter is missing
                                            if not original_url and lines: 
                                                first_line_stripped = lines[0].strip()
                                                if first_line_stripped.startswith("http://") or first_line_stripped.startswith("https://"):
                                                    original_url = first_line_stripped
                                                    logger.debug(f"文件 {filename}: 后备逻辑 - 从第一行提取到URL: {original_url}")
                                                    if not raw_content_for_llm.strip(): 
                                                       raw_content_for_llm = "".join(lines[1:])
                                                # If raw_content_for_llm is still empty (meaning "---" was not found and first line wasn't URL)
                                                # then the whole file is content, and URL remains empty (or as found by first line check)
                                                elif not raw_content_for_llm.strip(): 
                                                    logger.debug(f"文件 {filename}: 后备逻辑 - 第一行不是URL，且未找到'---'分隔符。将整个文件视为原始内容。URL保持为: '{original_url if original_url else '未找到'}'")
                                                    raw_content_for_llm = "".join(lines)


                                            if not raw_content_for_llm.strip():
                                                logger.warning(f"文件 {filename} 的有效原始内容为空（可能在元数据提取后），跳过。URL找到情况: '{original_url if original_url else '未找到'}'")
                                                continue

                                            source_info = f"来源: {vendor}/{subcategory}/{file_date_obj.isoformat()}/{filename}"
                                            
                                            article_data = {
                                                "raw_content": raw_content_for_llm,
                                                "vendor": vendor,
                                                "subcategory": subcategory,
                                                "original_filename": filename,
                                                "source_info_for_llm": source_info,
                                                "original_url": original_url, # 可能为空
                                                "date_published": file_date_obj.isoformat() # 添加发布日期
                                            }
                                            all_articles_data.append(article_data)
                                            logger.debug(f"已收集文章数据: {filename} (URL: {original_url if original_url else '未找到'})")
                                        except Exception as e_read:
                                            logger.warning(f"无法读取或处理文件 {file_path}: {e_read}")
                            else:
                                logger.debug(f"文件 {filename} (在 {subcategory_path} 中) 与 YYYY_MM_DD_* 格式不匹配。")
                        except ValueError:
                            logger.debug(f"无法从文件 {filename} (在 {subcategory_path} 中) 解析日期。期望格式 YYYY_MM_DD_*.md。")
                        except Exception as e_parse:
                            logger.warning(f"解析文件名 {filename} (在 {subcategory_path} 中) 时出错: {e_parse}")
            except OSError as e_list_files:
                logger.warning(f"无法列出 {subcategory_path} 中的文件: {e_list_files}")
    
    if not all_articles_data:
        logger.info("当前周未找到原始文章。")
        return [] # 返回空列表
    
    logger.info(f"本周成功收集到 {len(all_articles_data)} 篇原始文章的数据。")
    return all_articles_data # 返回文章数据列表

def generate_report_markdown_from_articles(
    articles_data: List[Dict[str, str]], 
    model_client: Any, 
    config: dict # 用于获取内部链接域名等配置
) -> Optional[str]:
    """
    将所有文章内容合并后进行单次LLM调用生成完整摘要，然后替换链接并格式化为周报Markdown。
    """
    logger = logging.getLogger(__name__) # 主函数日志
    
    if not articles_data:
        logger.info("没有文章数据传递给 generate_report_markdown_from_articles，不生成报告。")
        return None

    # --- 从配置中获取报告相关设置 ---
    reporting_config = config.get("reporting", {})
    site_base_url = reporting_config.get("site_base_url", "http://cnetspy.site") 

    beautification_config = reporting_config.get("beautification", {})
    banner_url = beautification_config.get("banner_url", "")
    report_title_prefix = beautification_config.get("report_title_prefix", "【云技术周报】")
    intro_text = beautification_config.get("intro_text", "汇集本周主要云厂商的技术产品动态，助您快速掌握核心变化。")
    vendor_emojis = beautification_config.get("vendor_emojis", {"AWS": "🟠", "AZURE": "🔵", "GCP": "🔴", "DEFAULT": "☁️"})
    no_updates_text = beautification_config.get("no_updates_text", "本周暂无重要更新内容。")
    footer_text = beautification_config.get("footer_text", "由云竞争情报分析平台自动汇总。")
    platform_link_text = beautification_config.get("platform_link_text", "前往平台查看更多详情")
    platform_url = beautification_config.get("platform_url", site_base_url) 

    # --- 1. 准备LLM的输入：合并所有文章内容 --- 
    # 我们需要在提示中告知LLM，它将收到一个包含多篇文章的集合，
    # 并为每篇文章生成摘要，然后将所有摘要组合成一个连贯的Markdown报告片段。
    # 提示词也需要强调，LLM生成的链接应使用原文URL，我们后续会处理。

    llm_input_parts = []
    for article in articles_data:
        # 为了帮助后续URL替换和内容校验，可以在每篇文章前后加入特殊标记，或确保LLM输出包含足够信息
        # 例如，可以在source_info_for_llm中包含一个唯一ID或文件名
        # 提示词也应指导LLM在生成每个摘要时，能够清晰地指明来源文章
        llm_input_parts.append(f"--- 文章开始 ---\n来源信息: {article['source_info_for_llm']}\n原文URL: {article['original_url']}\n文章原始内容:\n{article['raw_content']}\n--- 文章结束 ---\n\n") # 文章间留空行
    
    full_llm_input_prompt = "\n".join(llm_input_parts)
    if not full_llm_input_prompt.strip():
        logger.warning("准备的LLM输入内容为空，无法生成报告。")
        return None
    
    logger.info(f"已为 {len(articles_data)} 篇文章准备好合并的LLM输入，总长度约: {len(full_llm_input_prompt)} chars")
    logger.debug(f"发送给LLM的合并内容 (前500字符预览):\n{full_llm_input_prompt[:500]}...")

    # --- 2. 单次LLM调用 --- 
    generated_report_content_raw = None
    try:
        generated_report_content_raw = model_client.predict(prompt=full_llm_input_prompt)
        if not isinstance(generated_report_content_raw, str) or not generated_report_content_raw.strip():
            logger.error("LLM返回的报告内容为空或无效。")
            # 即使LLM失败，也尝试生成包含模板信息的报告
            generated_report_content_raw = beautification_config.get("dingtalk_no_updates_text", "本周各家云厂商在所监控的技术领域内暂无重要更新内容公开发布。") 
        else:
            logger.info("LLM成功返回报告内容。")
            logger.debug(f"LLM返回的原始报告内容 (前500字符预览):\n{generated_report_content_raw[:500]}...")
    except Exception as e:
        logger.error(f"调用LLM生成整体报告时出错: {e}", exc_info=True)
        # 即使LLM失败，也尝试生成包含模板信息的报告
        generated_report_content_raw = beautification_config.get("dingtalk_no_updates_text", "本周各家云厂商在所监控的技术领域内暂无重要更新内容公开发布。") 

    # --- 3. URL替换和内容校验 (关键且复杂的部分) ---
    # 现在的 generated_report_content_raw 是一个大的Markdown字符串，包含所有文章的摘要
    # 我们需要遍历它，找到所有形如 ### [[厂商] 标题](原文URL) 的链接，
    # 并将 原文URL 替换为对应的 内部URL。
    # articles_data 列表在这里至关重要，我们需要用它来查找每篇文章的元数据以构建内部链接。
    
    processed_report_content = generated_report_content_raw # 初始化
    
    # TODO: 实现更健壮的URL替换逻辑。
    # 这是一个简化版的占位逻辑，需要用正则表达式和更精确的匹配来完善。
    # 理想情况下，LLM的输出应严格遵循格式，便于解析。
    # 我们需要遍历 articles_data，对每篇文章尝试在 processed_report_content 中找到其对应的摘要和链接。

    temp_summaries_by_vendor = {} # 临时按厂商存放处理后的摘要片段
    # 假设LLM为每篇文章都生成了 ### [[厂商] 标题](原文URL) 格式的摘要，并且按顺序排列
    # 这只是一个非常粗略的设想，实际LLM的输出可能需要更复杂的解析

    # 示例：如果LLM严格按顺序输出了摘要，并且每个摘要都有唯一可识别的标题或原文URL
    # 我们可以尝试迭代 articles_data，然后在 generated_report_content_raw 中寻找并替换
    # 这部分非常依赖LLM的输出格式，需要根据实际输出来调整
    
    # 遍历原始文章数据，尝试在LLM的输出中找到并替换链接
    # 这需要LLM输出的摘要标题或内容与原文有足够高的相似度，或者LLM能按我们提供的原文URL输出
    if generated_report_content_raw and generated_report_content_raw != no_updates_text: # 仅当LLM有有效输出时尝试替换
        processed_llm_output = generated_report_content_raw # 使用一个新变量进行操作，保留原始LLM输出以供调试
        
        logger.info("开始在LLM生成的报告内容中替换原文URL为内部链接...")
        replacement_attempts = 0
        successful_replacements = 0

        for article_info in articles_data:
            original_url = article_info.get("original_url")
            source_info_log = article_info.get('source_info_for_llm', article_info.get('original_filename', '未知文章'))

            logger.debug(
                f"URL_REPLACE: 正在处理文章 '{source_info_log}'. "
                f"从元数据获取的 Original URL: '{original_url}' (类型: {type(original_url)})"
            )

            if not original_url or not isinstance(original_url, str) or not original_url.strip().startswith("http"):
                logger.warning(
                    f"URL_REPLACE_SKIP: 跳过文章 '{source_info_log}' 的URL替换. "
                    f"原因: 元数据中的 Original URL 无效或缺失 (值: '{original_url}')."
                )
                continue

            replacement_attempts += 1
            
            # 构建内部链接
            vendor = article_info.get("vendor", "unknown_vendor")
            subcategory = article_info.get("subcategory", "unknown_subcategory")
            original_filename_from_data = article_info.get("original_filename")

            if not original_filename_from_data:
                logger.warning(f"URL_REPLACE_WARNING: Article for source '{source_info_log}' is missing 'original_filename' in its data. Cannot build internal URL.")
                continue
            
            # 直接使用 original_filename_from_data，因为它应该包含 .md 后缀
            internal_link_path = f"analysis/document/{vendor}/{subcategory}/{original_filename_from_data}"
            internal_link_full = f"{site_base_url}/{internal_link_path}" 
            
            pattern_to_find = f"]({original_url})"
            replacement_pattern = f"]({internal_link_full})"

            logger.debug(
                f"URL_REPLACE_ATTEMPT: 文章 '{source_info_log}'. "
                f"查找模式: '{pattern_to_find}'. "
                f"替换为: '{replacement_pattern}'."
            )
            
            if pattern_to_find in processed_llm_output:
                processed_llm_output = processed_llm_output.replace(pattern_to_find, replacement_pattern)
                successful_replacements += 1
                logger.info(
                    f"URL_REPLACE_SUCCESS: 成功替换文章 '{source_info_log}' 的URL. "
                    f"'{original_url}' -> '{internal_link_full}'."
                )
            else:
                logger.warning(
                    f"URL_REPLACE_FAILED: 未能替换文章 '{source_info_log}' 的URL. "
                    f"查找模式 '{pattern_to_find}' 未在LLM当前处理的输出中找到. "
                    f"Original URL from metadata: '{original_url}'."
                )
                if original_url in generated_report_content_raw:
                    logger.warning(
                        f"URL_REPLACE_HINT: 模式 '{pattern_to_find}' 未找到, "
                        f"但原始URL '{original_url}' 本身存在于LLM未经修改的输出中. "
                        f"这可能意味着LLM输出的链接格式与期望的 '](URL)' 不完全匹配."
                    )
                    try:
                        search_term_for_context = original_url.lower().rstrip('/')
                        
                        idx = -1
                        variations_to_try = [
                            original_url, 
                            original_url.rstrip('/'), 
                            original_url.lower(), 
                            search_term_for_context 
                        ]
                        found_variation_for_context = None
                        for variation in variations_to_try:
                            temp_idx = generated_report_content_raw.find(variation)
                            if temp_idx != -1:
                                idx = temp_idx
                                found_variation_for_context = variation
                                logger.info(f"URL_REPLACE_CONTEXT: Found variation '{variation}' of original URL in raw LLM output at char index {idx}.")
                                break
                        
                        if idx != -1:
                            context_start = max(0, idx - 70)
                            context_end = min(len(generated_report_content_raw), idx + len(found_variation_for_context) + 70)
                            context_snippet = generated_report_content_raw[context_start:context_end]
                            # Safely construct the log message
                            # Using repr() for context_snippet to avoid issues with special characters in it
                            log_message_part1 = f"URL_REPLACE_CONTEXT: LLM原始输出中与 '{original_url}' (找到的变体: '{found_variation_for_context}') 相关的上下文片段 "
                            log_message_part2 = f"(位于字符索引 {idx} 附近):"
                            log_message_part3 = f"---...{repr(context_snippet)}...---"
                            logger.warning(log_message_part1 + log_message_part2 + log_message_part3)
                        else:
                            logger.warning(
                                f"URL_REPLACE_CONTEXT: 即使是原始URL '{original_url}' (或其变体) "
                                f"也未能在未经修改的LLM输出中直接定位到. LLM可能完全改变了它或没有包含它."
                            )
                    except Exception as e_context:
                        logger.error(f"URL_REPLACE_CONTEXT: 提取上下文时发生错误: {e_context}", exc_info=True)
                else:
                     logger.warning(
                        f"URL_REPLACE_HINT: 原始URL '{original_url}' 本身也未在未经修改的LLM输出中找到. "
                        f"请检查LLM是否按预期包含了该URL."
                    )
        
        logger.info(f"URL替换完成。尝试次数: {replacement_attempts}, 成功次数: {successful_replacements}.")
        processed_report_content = processed_llm_output 
    else:
        logger.info("LLM未返回有效内容或无文章数据，跳过URL替换。")
        processed_report_content = generated_report_content_raw

    # --- 4. 组合最终的Markdown报告 --- 
    final_markdown_parts = []
    total_articles_processed_successfully = len(articles_data) if processed_report_content and processed_report_content != no_updates_text else 0
    
    if banner_url:
        final_markdown_parts.append(f"![]({banner_url})\n")

    today_date_obj = datetime.date.today()
    start_of_week = today_date_obj - datetime.timedelta(days=today_date_obj.weekday())
    report_date_range_str = f"{start_of_week.strftime('%Y年%m月%d日')} - {today_date_obj.strftime('%Y年%m月%d日')}"
    
    report_main_title = f"{report_title_prefix} {report_date_range_str} 竞争动态速览"
    final_markdown_parts.append(f"# {report_main_title}\n")
    
    final_markdown_parts.append(f"{intro_text}\n")

    # 直接添加LLM处理过的内容
    # 假设LLM的输出已经是按厂商分组的或者我们接受LLM的排序
    if processed_report_content and processed_report_content != no_updates_text:
        final_markdown_parts.append(processed_report_content)
        # 确保LLM输出后有一个换行，以便和页脚分隔
        if not processed_report_content.endswith('\n'):
            final_markdown_parts.append("\n")
    else: # LLM没有有效输出或者返回的是无更新文本
        final_markdown_parts.append(no_updates_text + "\n")
        total_articles_processed_successfully = 0 # 确认计数

    if platform_url and platform_link_text:
        final_markdown_parts.append(f"{footer_text} [{platform_link_text}]({platform_url})")
    else:
        final_markdown_parts.append(footer_text)
        
    logger.info(f"报告Markdown内容已生成 (处理了约 {total_articles_processed_successfully} 篇文章的摘要)。")
    return "\n".join(final_markdown_parts)

def main():
    # --- 参数解析 --- 
    parser = argparse.ArgumentParser(description="生成每周竞品动态摘要报告。")
    parser.add_argument(
        '--loglevel',
        default='INFO', # 如果未指定，默认为 INFO
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='设置日志级别 (默认: INFO)'
    )
    args = parser.parse_args()

    # 将字符串日志级别转换为 logging常量
    numeric_log_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_log_level, int):
        raise ValueError(f'无效的日志级别: {args.loglevel}')

    # 首先设置日志 - 这可能会从配置中设置一个默认级别
    setup_colored_logging() 
    
    # 获取根日志记录器并根据命令行参数设置其级别
    # 这将影响所有日志记录器，除非它们有自己设置的更低级别。
    # 注意: 如果 setup_colored_logging 配置了具有特定级别的处理器，
    # 这些处理器的级别可能也需要调整，或者此根级别设置可能已足够。
    logging.getLogger().setLevel(numeric_log_level)
    # 如果想更精确地设置，可以为特定的日志记录器设置级别:
    # logging.getLogger('__main__').setLevel(numeric_log_level)
    # logging.getLogger('src.utils').setLevel(numeric_log_level) # 其他模块示例

    logger = logging.getLogger(__name__) # 在级别设置后获取logger

    logger.info(f"日志级别已设置为: {args.loglevel}") 
    logger.info("开始生成每周竞品动态摘要脚本 (单次LLM调用模式)。")

    try:
        config_full = get_config() 
        if not config_full:
            logger.error("严重: 配置加载失败。`get_config()` 返回 None或为空。请确保 config.yaml (或等效文件) 有效且可访问。")
            return
        logger.info("配置加载成功。")
    except FileNotFoundError:
        logger.error("严重: 配置文件 (例如 config.yaml) 未找到。请确保它存在于项目根目录或 config_loader.py 的相关路径中。")
        return
    except Exception as e:
        logger.error(f"严重: 加载配置时出错: {e}", exc_info=True)
        return

    # --- AI分析器 (ModelManager) 初始化 ---
    ai_config_params = config_full.get("ai_analyzer")
    if not ai_config_params:
        logger.error("严重: 配置中未找到 'ai_analyzer' 部分。ModelManager 需要此部分配置。")
        return
    
    try:
        model_manager = ModelManager(ai_config=ai_config_params)
        logger.info("ModelManager 初始化成功。")
    except Exception as e:
        logger.error(f"严重: 初始化 ModelManager 失败: {e}", exc_info=True)
        return

    # --- 加载提示模板 (用作LLM客户端的系统提示) ---
    # 此提示定义了LLM客户端实例的任务/角色。
    prompt_file_path_config = config_full.get("prompt_paths", {})
    
    # 从 reporting 配置中获取提示键
    reporting_config_main = config_full.get("reporting", {}) # 在main函数作用域也获取reporting_config
    weekly_update_prompt_key = reporting_config_main.get("weekly_update_prompt_key", "weekly_updates")
    
    prompt_file_path = prompt_file_path_config.get(weekly_update_prompt_key, f"prompt/{weekly_update_prompt_key}.txt")

    try:
        system_prompt_for_weekly_report = load_prompt_template(prompt_file_path)
        logger.info(f"成功从 {prompt_file_path} 加载周报的系统提示模板。")
    except Exception: # load_prompt_template 已记录具体错误
        logger.error(f"严重: 加载系统提示模板失败。请确保 '{prompt_file_path}' 存在且可读。")
        return

    # --- 从 ModelManager 获取配置好的 LLM 客户端 ---
    # 确定此报告使用哪个模型配置
    # 如果 reporting 配置中未指定，则默认为 ai_analyzer 配置中的 active_model_profile
    default_profile_name = model_manager.active_model_profile_name 
    report_model_profile_name = reporting_config_main.get("weekly_summary_model_profile", default_profile_name)

    if not report_model_profile_name:
        logger.error("严重: 无法确定周报使用的模型配置。配置中 'reporting.weekly_summary_model_profile' 和 'ai_analyzer.active_model_profile' 均未设置。")
        return

    try:
        logger.info(f"尝试获取LLM客户端，配置名称: '{report_model_profile_name}'，使用已加载的系统提示。")
        # system_prompt_for_weekly_report (来自 weekly_updates.txt) 将配置LLM客户端的行为。
        llm_client_for_report = model_manager.get_model_client(
            system_prompt_text=system_prompt_for_weekly_report,
            model_profile_name=report_model_profile_name
        )
        logger.info(f"成功获取配置为 '{report_model_profile_name}' 的LLM客户端。")
    except AIAnalyzerError as e:
        logger.error(f"严重: 从 ModelManager 获取LLM客户端失败 (AIAnalyzerError): {e}", exc_info=True)
        return
    except ValueError as e: # 捕获 ModelManager 的 ValueError (例如，配置未找到)
        logger.error(f"严重: 从 ModelManager 获取LLM客户端失败 (ValueError): {e}", exc_info=True)
        return
    except Exception as e: # 捕获任何其他意外错误
        logger.error(f"严重: 从 ModelManager 获取LLM客户端时发生意外错误: {e}", exc_info=True)
        return
        
    # --- 获取原始内容 --- 
    logger.info("正在尝试获取本周所有文章的详细数据...")
    # all_articles_raw_content 原来是字符串，现在是 List[Dict[str,str]]
    articles_data_list = get_all_raw_content_for_week(config_full)

    if not articles_data_list: # 修改了变量名和判断
        logger.info("未找到本周原始文章数据。将生成一个空的报告框架。")
        # 即使没有文章，也尝试生成一个空的报告框架，或者只包含无更新提示的报告
        # generate_report_markdown_from_articles 内部会处理 articles_data_list 为空的情况

    weekly_summary_md = generate_report_markdown_from_articles(
        articles_data=articles_data_list, # 传递文章数据列表
        model_client=llm_client_for_report,
        config=config_full # 传递完整的配置对象
    )
    
    if not weekly_summary_md:
        logger.info("未生成周报Markdown内容。将不创建输出文件。")
        return

    # --- 输出 Markdown ---
    final_markdown_content = weekly_summary_md 

    output_dir_config = config_full.get("output_paths", {})
    output_dir = output_dir_config.get("reports_dir", "data/reports")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"已确保输出目录存在: {output_dir}")
    except OSError as e:
        logger.error(f"无法创建输出目录 {output_dir}: {e}")
        return 

    today_date_obj = datetime.date.today()
    start_of_week = today_date_obj - datetime.timedelta(days=today_date_obj.weekday()) # 本周一
    
    report_title_range = f"{start_of_week.strftime('%Y-%m-%d')} 到 {today_date_obj.strftime('%Y-%m-%d')}"
    output_filename_date_range = f"{start_of_week.strftime('%Y-%m-%d')}_to_{today_date_obj.strftime('%Y-%m-%d')}"
    output_filename = f"weekly_competitor_summary_{output_filename_date_range}.md"
    output_filepath = os.path.join(output_dir, output_filename)

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(final_markdown_content) # final_markdown_content 现在是完整的报告
        logger.info(f"成功将周报写入: {output_filepath}")
    except IOError as e:
        logger.error(f"写入摘要文件 {output_filepath} 时出错: {e}")

if __name__ == "__main__":
    main() 