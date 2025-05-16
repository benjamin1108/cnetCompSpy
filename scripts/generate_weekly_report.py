import datetime
import logging
import os
import sys
import argparse # 导入argparse用于处理命令行参数
from typing import Dict, Optional, Any 

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

def get_all_raw_content_for_week(config: dict) -> str:
    """
    获取并拼接当前周（周一至周日）所有原始文章 (.md) 的内容。
    日期从文件名中解析 (例如 YYYY_MM_DD_*.md)。
    """
    logger = logging.getLogger(__name__)
    raw_data_config = config.get("data_paths", {})
    base_path = raw_data_config.get("raw_articles_base", "data/raw")
    vendors = config.get("vendors_to_scan", ["aws", "azure", "gcp"]) # 默认扫描的供应商

    if not os.path.isdir(base_path):
        logger.error(f"原始数据基础路径未找到或不是一个目录: {base_path}")
        return ""

    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday()) # 本周一
    
    all_contents = []
    logger.info(f"正在扫描从 {start_of_week.isoformat()} 到 {today.isoformat()} 的原始文章，供应商: {vendors}")

    for vendor in vendors:
        vendor_base_path = os.path.join(base_path, vendor) # 路径到 data/raw/<vendor>/
        if not os.path.isdir(vendor_base_path):
            logger.debug(f"供应商基础路径未找到或不是目录，跳过: {vendor_base_path}")
            continue

        try:
            # 动态获取供应商目录下的子类别 (例如 'blog', 'whatsnew')
            subcategories = [d for d in os.listdir(vendor_base_path) if os.path.isdir(os.path.join(vendor_base_path, d))]
            if not subcategories:
                logger.debug(f"在 {vendor_base_path} 中未找到子类别，跳过此供应商。")
                continue
        except OSError as e_list_sub:
            logger.warning(f"无法列出 {vendor_base_path} 中的子类别: {e_list_sub}")
            continue
        
        for subcategory in subcategories:
            subcategory_path = os.path.join(vendor_base_path, subcategory) # 路径类似 data/raw/<vendor>/<subcategory>/
            logger.info(f"正在扫描目录: {subcategory_path}") 

            try:
                for filename in os.listdir(subcategory_path):
                    if filename.endswith(".md"): # 查找 .md 文件
                        # 尝试从文件名中解析日期，格式如 YYYY_MM_DD_*.md
                        try:
                            date_part_str = filename.split('_', 3) # 分割成 [YYYY, MM, DD, rest]
                            if len(date_part_str) >= 3:
                                file_date_str = f"{date_part_str[0]}-{date_part_str[1]}-{date_part_str[2]}"
                                file_date_obj = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
                                
                                # 检查文件日期是否在当前处理周的范围内
                                if start_of_week <= file_date_obj <= today:
                                    # 确保文件日期精确匹配本周从周一到今天的某一天
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
                                                content = f_article.read()
                                            
                                            # 提取标题用于日志记录
                                            title_for_log = "未找到标题"
                                            try:
                                                content_lines = content.splitlines()
                                                if content_lines:
                                                    first_line_stripped = content_lines[0].strip()
                                                    if first_line_stripped.startswith("# "):
                                                        title_for_log = first_line_stripped[2:].strip()
                                            except Exception: # 捕获广泛异常以避免日志记录中断收集流程
                                                logger.debug(f"无法从 {filename} 中提取标题用于日志记录")

                                            logger.info(f"已收集用于摘要: 标题='{title_for_log}', 文件='{filename}'")

                                            # 源信息使用实际文件日期，而非迭代日期
                                            source_info = f"来源: {vendor}/{subcategory}/{file_date_obj.isoformat()}/{filename}"
                                            all_contents.append(f"--- {source_info} ---\n{content}")
                                            logger.debug(f"已读取内容: {file_path} (日期: {file_date_obj.isoformat()})")
                                        except Exception as e_read:
                                            logger.warning(f"无法读取文件 {file_path}: {e_read}")
                            else:
                                logger.debug(f"文件 {filename} (在 {subcategory_path} 中) 与 YYYY_MM_DD_* 格式不匹配。")
                        except ValueError:
                            logger.debug(f"无法从文件 {filename} (在 {subcategory_path} 中) 解析日期。期望格式 YYYY_MM_DD_*.md。")
                        except Exception as e_parse: # 捕获其他解析错误
                            logger.warning(f"解析文件名 {filename} (在 {subcategory_path} 中) 时出错: {e_parse}")
                            
            except OSError as e_list_files:
                logger.warning(f"无法列出 {subcategory_path} 中的文件: {e_list_files}")
    
    if not all_contents:
        logger.info("当前周未找到原始文章。")
        return ""
    
    logger.info(f"本周成功收集到来自 {len(all_contents)} 个原始文件的内容。")
    return "\n\n\n".join(all_contents) # 使用更明显的分割符连接内容


def generate_consolidated_weekly_summary(
    model_client: Any, 
    all_articles_raw_content: str,
) -> Optional[str]:
    """
    使用提供的模型客户端为当前周的所有文章生成单个整合的 Markdown 摘要。
    """
    logger = logging.getLogger(__name__)
    
    if not all_articles_raw_content: 
        logger.info("未提供原始文章内容给 generate_consolidated_weekly_summary 函数，跳过摘要生成。")
        return None
    
    logger.info(f"用于摘要的原始内容总长度: {len(all_articles_raw_content)} 字符。")
    
    try:
        logger.info("正在使用配置好的LLM客户端生成整合周报...")
        
        # model_client 是 OpenAICompatibleAI 的一个实例。
        # 其 'predict' 方法接收用户的文本提示。
        # 系统提示 (来自 weekly_updates.txt) 已在客户端实例中配置好，
        # 'predict' 方法会在内部使用它。
        summary_text = model_client.predict(prompt=all_articles_raw_content)
        
        # OpenAICompatibleAI 中的 predict 方法设计为直接返回解析后的文本字符串。
        # 因此，如果 OpenAICompatibleAI._parse_response 对所有提供商都能按预期工作，
        # 此处理想情况下不需要复杂的解析逻辑 (如检查 .text, .content 或 .choices[0].message.content)。
        # 但保留一个基本检查以防 predict() 意外返回非字符串对象。
        if not isinstance(summary_text, str):
            logger.warning(f"LLM客户端的predict方法返回了非字符串类型: {type(summary_text)}。尝试转换为字符串。")
            # 此路径理想情况下不应被命中，如果 _parse_response 足够健壮。
            # 如果它是一个可以转换为所需文本的对象，这可能会起作用。
            # 否则，如果发生这种情况，可能需要根据实际对象类型进行更具体的处理。
            summary_text = str(summary_text) # 后备转换，可能不是正确的内容。

        if not summary_text or not summary_text.strip():
            logger.warning("LLM返回的摘要为空或仅包含空白字符。")
            return None
            
        logger.info("成功生成整合周报。")
        return summary_text
    except APIError as e: # 捕获来自AI客户端的特定API错误
        logger.error(f"本周LLM摘要过程中发生API错误: {e}", exc_info=True)
        return f"生成周报时发生API错误: {e}"
    except AIAnalyzerError as e: # 捕获来自ModelManager/AI客户端的其他错误
        logger.error(f"本周LLM摘要过程中发生AI分析器错误: {e}", exc_info=True)
        return f"生成周报时发生AI分析器错误: {e}"
    except Exception as e:
        logger.error(f"本周LLM摘要过程中发生意外错误: {e}", exc_info=True)
        return f"生成周报时发生错误: {e}"


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
    logger.info("开始生成每周竞品动态摘要脚本。")

    try:
        config = get_config() 
        if not config:
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
    ai_config_params = config.get("ai_analyzer")
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
    prompt_file_path_config = config.get("prompt_paths", {})
    weekly_update_prompt_key = "weekly_updates" # 配置中的默认键
    
    # 允许从 reporting 配置中覆盖提示键以获得更大灵活性
    reporting_config = config.get("reporting", {})
    weekly_update_prompt_key = reporting_config.get("weekly_update_prompt_key", weekly_update_prompt_key)
    
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
    report_model_profile_name = reporting_config.get("weekly_summary_model_profile", default_profile_name)

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
    logger.info("正在尝试获取本周所有原始内容...")
    all_articles_raw_content = get_all_raw_content_for_week(config)

    if not all_articles_raw_content:
        logger.info("未找到本周原始文章内容。跳过摘要生成。")
        return # 如果没有内容，则不创建输出文件

    # --- 使用新的客户端生成整合周报 ---
    weekly_summary_md = generate_consolidated_weekly_summary(
        model_client=llm_client_for_report,
        all_articles_raw_content=all_articles_raw_content
    )
    
    if not weekly_summary_md:
        logger.info("未生成周报。将不创建输出文件。")
        return

    # --- 输出 Markdown ---
    final_markdown_content = weekly_summary_md # 这现在是来自LLM的单个摘要字符串

    output_dir_config = config.get("output_paths", {})
    output_dir = output_dir_config.get("reports_dir", "data/reports")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"已确保输出目录存在: {output_dir}")
    except OSError as e:
        logger.error(f"无法创建输出目录 {output_dir}: {e}")
        return 

    today_date_obj = datetime.date.today()
    report_title_date = today_date_obj.strftime("%Y-%m-%d")
    output_filename = f"weekly_competitor_summary_{report_title_date}.md"
    output_filepath = os.path.join(output_dir, output_filename)

    # 报告标题和引言已经是中文，无需修改
    report_main_title = f"# 每周竞品动态摘要 - {report_title_date}\n\n"
    report_intro = ("本报告根据近期的公开技术文章，使用AI进行摘要总结，"
                    "旨在帮助快速了解技术核心和潜在影响。\n\n---\n\n")

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(report_main_title)
            f.write(report_intro)
            f.write(final_markdown_content)
        logger.info(f"成功将周报写入: {output_filepath}")
    except IOError as e:
        logger.error(f"写入摘要文件 {output_filepath} 时出错: {e}")

if __name__ == "__main__":
    main() 