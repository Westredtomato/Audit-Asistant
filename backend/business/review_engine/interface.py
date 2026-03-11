"""
重大事项复核引擎模块接口模块
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import json


from langchain_openai import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 添加 review_engine 目录到 Python 路径
review_engine_path = project_root / "business"
sys.path.append(str(review_engine_path))

# 添加 review_engine 目录到 Python 路径
review_engine_path = project_root / "business" / "review_engine"
sys.path.append(str(review_engine_path))

# 添加 review_engine 目录到 Python 路径
review_engine_path = project_root / "business" / "review_engine" / "agent"
sys.path.append(str(review_engine_path))

from agent.review_agent import create_agent, llm_without_tools
from agent.config_manager import Controller
from schemas import (ReviewData,
                    UploadFileRequirement,
                    ResponseData,
                    HelpRequirement,
                    StatisticalSummary,
                    ReviewResult,
                    EngineResponseData,
                    ReplyInInteraction
                )
# 添加项目根目录（backend/）到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
from document_parser import DocumentParser




class MainReviewEngine:
    """
    重大事项复核引擎模块接口

    """
    def __init__(self, memory: str = "internal_storage"):
        """
        初始化重大事项复核引擎模块

        Args:
            memory (str): 存储复核结果。必选参数，可选策略为"internal_storage",

        """
        def init_engine(memory):
            # 初始化配置
            controller = {k: v for k, v in Controller().review_config.items() if k != "LLM_CONFIG"}

            # 初始化存储策略与智能体

            if memory == "internal_storage":
                memory = InMemorySaver()
                core_agent = create_agent().compile(checkpointer=memory)
            else:
                raise ValueError("Invalid memory type")
            return {
                    "controler": controller,
                    "memory": memory,
                    "core_agent": core_agent
                }
        engine_data = init_engine(memory)
        self.base_config = engine_data.get("controler")
        self.memory = engine_data.get("memory")
        self.core_agent = engine_data.get("core_agent")
        self.config = {"configurable": {"thread_id": "1"}}
        
        self.review_data = None
        self._last_missing_files = []
        self.files_to_parsed = []
    
    def _check_missing_files(self, review_data: ReviewData) -> List[str]:
        """
        检查ReviewData中的二级分类示例键名是否在指定目录中存在对应的文件
        
        Args:
            review_data (ReviewData): 审核数据
            
        Returns:
            List[str]: 不存在的文件名列表，如果都存在则返回空列表
        """
        # 提取所有二级分类示例键名
        secondary_categories = []
        audit_evidence_standard = review_data.审计证据标准
        
        # 遍历审计证据分类与要求列表
        for item in audit_evidence_standard.审计证据分类与要求:
            for primary_category, secondary_dict in item.items():
                # 获取二级分类示例键名
                secondary_categories.extend(secondary_dict.keys())
        
        # 获取HTML文件目录
        html_file_dir = self.base_config.get("HTML_FILE_DIR")
        if not html_file_dir:
            # 如果目录未配置，抛出异常
            raise FileNotFoundError("HTML文件目录未配置")

        if not os.path.exists(html_file_dir):
            # 如果目录不存在，抛出异常
            raise FileNotFoundError(f"HTML文件目录不存在: {html_file_dir}")
        
        # 获取目录中所有文件名
        existing_files = set(os.listdir(html_file_dir))
        
        # 找出不存在的文件
        missing_files = []
        for category in secondary_categories:
            # 假设文件名与分类名相同，扩展名可能是.html或其他
            if category not in existing_files and f"{category}.html" not in existing_files:
                missing_files.append(category)
        
        self._last_missing_files = missing_files
        
        return missing_files
    
    def parse_workpaper(self, work_paper_file):
            """
            接收一个或多个Excel file,写入系统EXCEL_FILE_DIR目录下
            
            Args:
                work_paper_file: 单个文件对象、文件对象列表，或WorkPaperFile对象列表
                
            Returns:
                list: 保存成功的文件名列表
            """
            import base64
            
            # 获取Excel文件目录
            excel_file_dir = self.base_config.get("EXCEL_FILE_DIR")
            if not excel_file_dir:
                raise FileNotFoundError("Excel文件目录未配置")
            
            # 确保目录存在
            if not os.path.exists(excel_file_dir):
                os.makedirs(excel_file_dir)
            
            # 标准化文件参数为列表
            files = work_paper_file if isinstance(work_paper_file, list) else [work_paper_file]
            
            saved_files = []
            for file in files:
                # 获取文件名 - 支持多种格式
                if isinstance(file, dict):
                    # 字典格式（来自前端的JSON）
                    filename = file.get('filename', 'unknown.xlsx')
                    content = file.get('content', '')
                    file_type = 'dict'
                elif hasattr(file, 'filename'):
                    # Pydantic模型或Werkzeug FileStorage对象
                    filename = file.filename
                    content = getattr(file, 'content', None)
                    file_type = 'object'
                else:
                    filename = getattr(file, 'name', 'unknown.xlsx')
                    content = None
                    file_type = 'file'
                
                # 检查是否为Excel文件
                if not filename.lower().endswith(('.xls', '.xlsx')):
                    continue
                
                # 获取不带扩展名的文件名
                filename_without_ext = os.path.splitext(filename)[0]
                
                # 检查文件名是否在缺失文件列表中
                if filename_without_ext in self._last_missing_files:
                    # 构造完整路径
                    file_path = os.path.join(excel_file_dir, filename)
                    
                    # 保存文件 - 根据不同类型处理
                    if file_type == 'dict' and content:
                        # Base64编码的内容（来自前端）
                        try:
                            file_bytes = base64.b64decode(content)
                            with open(file_path, 'wb') as f:
                                f.write(file_bytes)
                        except Exception as e:
                            raise ValueError(f"解码Base64文件内容失败: {str(e)}")
                    elif file_type == 'object' and content:
                        # Pydantic模型的content字段（Base64字符串）
                        try:
                            if isinstance(content, str):
                                file_bytes = base64.b64decode(content)
                            else:
                                file_bytes = content
                            with open(file_path, 'wb') as f:
                                f.write(file_bytes)
                        except Exception as e:
                            raise ValueError(f"处理文件内容失败: {str(e)}")
                    elif hasattr(file, 'save'):  # Werkzeug FileStorage对象
                        file.save(file_path)
                    elif hasattr(file, 'read'):  # 文件对象
                        with open(file_path, 'wb') as f:
                            f.write(file.read())
                    else:  # 假设是文件路径
                        with open(file, 'rb') as src, open(file_path, 'wb') as dst:
                            dst.write(src.read())
                    
                    saved_files.append(filename)
                    # 更新files_to_parsed
                    self.files_to_parsed.append(filename)
                    # 从_last_missing_files中移除已保存的文件
                    self._last_missing_files.remove(filename_without_ext)
            
            if self._last_missing_files:
                upload_file_req_dict = {
                    "filename_list": self._last_missing_files,
                    "review_config": {
                        "MAX_TRIES": self.base_config["MAX_TRIES"],
                        "WAIT_TIMES": self.base_config["WAIT_TIMES"]
                    }
                }
                upload_file_requirement = UploadFileRequirement(**upload_file_req_dict)
                return upload_file_requirement
            
            for filename in self.files_to_parsed:
                file_path = os.path.join(excel_file_dir, filename)
                html_filename = os.path.splitext(filename)[0] + ".html"
                html_dir = self.base_config.get("HTML_FILE_DIR")
                html_file_path = os.path.join(html_dir, html_filename)

                DocumentParser().convert_xlsx_to_html(file_path, html_file_path)

            return True        

    def execute_review(self,review_data : ReviewData,config = {"configurable": {"thread_id": "1"}}):
        self.review_data = review_data
        missing_files = self._check_missing_files(review_data)
        if missing_files:
            upload_file_req_dict = {
                "filename_list": missing_files,
                "review_config": {
                    "MAX_TRIES": self.base_config["MAX_TRIES"],
                    "WAIT_TIMES": self.base_config["WAIT_TIMES"]
                }
            }
            upload_file_requirement = UploadFileRequirement(**upload_file_req_dict)
            return_result = EngineResponseData(response_type="upload_file_requirement", 
                                        data=upload_file_requirement,
                                        review_config=self.base_config
                                        )
            return return_result
        
        self.continue_review(None,config)

    def continue_review(self,response_data: ResponseData | None,config = {"configurable": {"thread_id": "1"}}):
        if response_data and response_data.response_type == "help_response":
            help_response_data = response_data.data
            resume_command = Command(resume=help_response_data)
            result = self.core_agent.invoke(resume_command,
                                            config=config,
                                            stream_mode="values"
            )                    

        else:
            if response_data and response_data.response_type == "upload_file_response":
                work_paper_file = response_data.data
                self.parse_workpaper(work_paper_file)                
            init_state = {
                "task_data": self.review_data.model_dump(),
                "task_index": 0,
                "counter": 0,
                "WAIT_TIMES": self.base_config["WAIT_TIMES"],
                "MAX_TRIES": self.base_config["MAX_TRIES"]
            }
            result = self.core_agent.invoke(init_state,
                                            config=config,
                                            stream_mode="values"
            )

        interrupt_results = result.get("__interrupt__",None)
        if interrupt_results:
            help_requirement = HelpRequirement(**interrupt_results[0].value)
            return_result = EngineResponseData(response_type="help_requirement", 
                                        data=help_requirement,
                                        review_config=self.base_config
                                        )            
            return return_result
        review_result_detail = result["review_result"]
        review_result = self.finally_summarize(review_result_detail)
        
        # 检查finally_summarize是否返回了有效的结果
        if review_result is None:
            # 如果没有返回有效结果，创建一个基本的ReviewResult对象
            review_result_data = ReviewResult(
                重大事项概述=self.review_data.重大事项概述 if self.review_data else "未知事项",
                审计结论=self.review_data.审计证据标准.审计结论 if self.review_data and self.review_data.审计证据标准 else "无结论",
                复核结果明细=review_result_detail if review_result_detail else [],
                统计整理=StatisticalSummary(
                    证据总数=0,
                    充分性情况=StatisticalSummary.SufficiencyDetail(
                        缺失数量=0, 
                        缺失详情=[]
                    ),
                    适当性情况=StatisticalSummary.AppropriatenessDetail(
                        不适当证据数量=0, 
                        详情=[]
                    )
                ),
                结论与原因=ReviewResult.ConclusionAndReason(
                    复核结论="审核完成但未能生成完整结论",
                    业务原因="在处理审核结果时发生错误或结果不完整"
                )
            )
        else:
            # finally_summarize现在直接返回ReviewResult对象
            review_result_data = review_result
            
        return_result = EngineResponseData(response_type="review_result", 
                                    data=review_result_data,
                                    review_config=self.base_config
                                    )        
        return return_result                    

    def generate_statistical_summary(self,review_result_detail: List[Dict[str, Dict[str, List[Dict]]]]) -> StatisticalSummary:
        """
        根据复核结果明细生成统计摘要
        
        Args:
            review_result_detail: 复核结果明细列表
            
        Returns:
            StatisticalSummary: 统计摘要实例
        """
        total_evidence_count = 0
        missing_evidence_count = 0
        inappropriate_evidence_count = 0
        
        missing_details = []
        inappropriate_details = []
        
        # 遍历复核结果明细
        for level1_item in review_result_detail:
            for level1_key, level2_dict in level1_item.items():
                for level2_key, level3_list in level2_dict.items():
                    for level3_item in level3_list:
                        # 获取相关证据与质量评估列表
                        evidence_list = level3_item.get("相关证据与质量评估", [])
                        
                        # 统计证据总数（非空列表）
                        if evidence_list:
                            total_evidence_count += len(evidence_list)
                        else:
                            # 空列表计入缺失数量
                            missing_evidence_count += 1
                            missing_details.append({
                                "证据内容": level3_item.get("证据内容", ""),
                                "质量要求": level3_item.get("质量要求", ""),
                                "证据类别": [level1_key, level2_key]
                            })
                        
                        # 遍历证据列表，统计不适当证据
                        for evidence in evidence_list:
                            quality_assessment = evidence.get("质量评估", {})
                            if quality_assessment.get("结论") == "不达标":
                                inappropriate_evidence_count += 1
                                info_location = evidence.get("信息定位", "")
                                if isinstance(info_location, list):
                                    # 如果是列表，将其转换为字符串
                                    info_location = ', '.join(info_location) if info_location else ""                                
                                inappropriate_details.append({
                                    "证据": evidence.get("证据", ""),
                                    "信息定位": info_location,
                                    "质量评估": quality_assessment,
                                    "证据内容": level3_item.get("证据内容", ""),
                                    "质量要求": level3_item.get("质量要求", ""),
                                    "证据类别": [level1_key, level2_key]
                                })
        
        # 构建统计摘要对象
        statistical_summary = StatisticalSummary(
            证据总数=total_evidence_count,
            充分性情况=StatisticalSummary.SufficiencyDetail(
                缺失数量=missing_evidence_count,
                缺失详情=missing_details
            ),
            适当性情况=StatisticalSummary.AppropriatenessDetail(
                不适当证据数量=inappropriate_evidence_count,
                详情=inappropriate_details
            )
        )
        
        return statistical_summary    

    def finally_summarize(self,review_result_detail: List[Dict[str, Dict[str, List[Dict]]]]) -> ReviewResult:   
        statistical_summary = self.generate_statistical_summary(review_result_detail)
        pre_summary = {
            "重大事项概述": self.review_data.重大事项概述,
            "审计结论": self.review_data.审计证据标准.审计结论,
            "复核结果明细": review_result_detail,
            "统计整理": statistical_summary.model_dump(),
        }
        prompt = f"""
# 你的角色
你是一名资深审计项目负责人，负责评价复核审计人员的审计工作中形成的审计记录工作质量，形成复核结论，并给出导致审计工作问题的主要原因。

# 复核内容与结果
## 内容
{pre_summary}
## 说明
- "重大事项概述"指出了审计工作的审计对象，"审计结论"是审计人员在给出的审计结论；
- "复核结果明细"与"统计整理"是对审计人员工作的详细复核结果

# 任务
1. 基于**复核内容与结果**,评价审计人员此次"重大事项"审计工作质量，并给出复核结论，给出导致审计工作问题的主要原因。
2. 输出格式为JSON，包含以下字段：
``` json
{"{"}"复核结论":"示例：评价审计人员此次重大事项审计工作质量","业务原因":"示例：说明导致审计工作问题的主要原因"{"}"}
```
# **现在，请你完成任务**
"""
        conclusion_reason = llm_without_tools.llm.invoke([{"role":"user","content":prompt}])
        conclusion_reason = conclusion_reason.content
        is_valid, extracted_content, error_msg = llm_without_tools._extract_llm_result(conclusion_reason, "json")
        if is_valid:
            conclusion_reason = json.loads(extracted_content)
            
            # 构建完整的ReviewResult对象
            review_result = ReviewResult(
                重大事项概述=self.review_data.重大事项概述,
                审计结论=self.review_data.审计证据标准.审计结论,
                复核结果明细=review_result_detail,
                统计整理=statistical_summary,
                结论与原因=ReviewResult.ConclusionAndReason(
                    复核结论=conclusion_reason["复核结论"],
                    业务原因=conclusion_reason["业务原因"]
                )
            )
            return review_result

class InterfaceAgent:
    def __init__(self, model = None):
        controller = Controller().review_config.get("LLM_CONFIG")
        if model is None:
            model = controller.get("LLM_MODAL")
        self.llm = ChatOpenAI(
            api_key=controller.get("API_KEY"),
            base_url=controller.get("BASE_URL"),
            model=model,  # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            temperature=0.01,
            )
    def chat_with_user(self, messages: list) -> ReplyInInteraction:
        """
        理解用户意图，并给出回复或引导
        """
        response_schemas = [
            ResponseSchema(name="用户意图", description="结合**对话历史**信息，识别用户最后一条消息的目的，只能回答: 执行复核|未明确|提供帮助 ", pattern="^(执行复核|未明确|介入)$"),
            ResponseSchema(name="是否完整", description="根据**对话历史**信息，判断用户提供的信息是否完整表述了他的目的，只能回答: true|false 。同时注意字母小写", pattern="^(true|false)$"),
            ResponseSchema(name="内容", description="根据判断的**用户意图**，以及用户意图**是否完整**，给出回复。")
        ]
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)       
        format_instructions = output_parser.get_format_instructions()
        prompt = PromptTemplate(
            template="""
# 你的角色
你的名字是**核瞳君**。你是一名审计复核助手，专门帮助用户进行审计复核，若用户提出无关要求，请用礼貌的语气回复，说明你的责任所在。

# 对话历史
你与用户对话的历史记录信息如下
```
{history}
```

# 任务
识别用户意图与用户表述是否完整描述他的意图，给出回复或引导
- 若用户意图为**执行复核**，且用户意图完整，则在保留原意的情况下总结用户的消息；若用户意图为**执行复核**，且用户意图不完整，则引导用户清晰表达他的意图。
  - 注意，用户意图完整指用户表达清楚他想要什么复核，而不需要表达复核需要的信息，这些信息会在后续补充。
- 若用户意图为**未明确**，则说明用户的要求你并不清晰。你的工作是帮助用户进行审计复核，欢迎用户提出审计复核的问题或任务。
\n{format_instructions}
""",
            input_variables=["history"],
            partial_variables={"format_instructions": format_instructions}
        )
        _input = prompt.format_prompt(history=messages)
        output = self.llm.invoke(_input.to_string())
        parsed_output = output_parser.parse(output.content)
        reply_in_interaction = ReplyInInteraction(**parsed_output)        
        return reply_in_interaction


        