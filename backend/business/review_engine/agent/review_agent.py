"""
复核智能体模块
"""

import sys
import os
from pathlib import Path
import re
import json
from typing import Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from lxml import etree
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages,RemoveMessage
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage
from langchain_core.prompts import PromptTemplate
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt

from config_manager import Controller


reviw_config = Controller().review_config
API_KEY = reviw_config.get("LLM_CONFIG").get("API_KEY")
LLM_MODAL = reviw_config.get("LLM_CONFIG").get("LLM_MODAL")
MAX_TRIES = reviw_config.get("MAX_TRIES")
HTML_FILE_DIR = reviw_config.get("HTML_FILE_DIR")

 
class State(TypedDict):
    messages: Annotated[list, add_messages]
    task_data: dict
    task_list: list
    task_index: int
    doc_info: dict
    audit_data_query: list
    audit_data_q_result: dict
    max_tries: int
    wait_time: dict
    counter: int
    evaluation: str = Field(description="评估结果：yes or no")
    review_result: list

class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        messages = inputs.get("messages", [])
        if messages:
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

class LlmNode:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def pre_review_agent(self, state: State) -> State:
        if state["review_result"][state["task_index"]]:
            review_result = state["review_result"][state["task_index"]]
            template = PromptTemplate(
                input_variables=["review_result"],
                template="""
# 已有复核结果与评估情况
{review_result}                
# 任务
请继续严格依据**审计证据分类与质量要求**，基于最新**已有复核结果**的未在审计记录中找到审计证据或不能完成质量评估的部分，继续搜索信息或分析，给出符合要求的复核结果。
"""              )
            prompt = template.format(review_result=review_result)
            messages_list = state["messages"].copy()
            messages_list.append({"role":"user","content":prompt})
            result = self.llm.invoke(messages_list)
            # 更新列表，只保留最后一轮对话，添加到"messages"列表中
            messages_list = [{"role":"user","content":prompt}] + [result]
            return {"messages": messages_list}
        else:
            task_index = state["task_index"]
            task_info = state["task_list"][task_index]
            query_and_result = state["audit_data_q_result"]
            review_req_method = task_info
            system_mess_template = PromptTemplate(
                input_variables=["review_req_method"],
                template="""
# 你的角色
- 你是一名资深审计项目负责人，负责复核审计人员的审计工作中形成的审计记录，以保障审计工作质量。你有多项工具，可以在需要时使用。
- 你需要根据**审计证据分类与要求**，完成对审计记录中的审计证据的分类与质量评估。
- 如果用户对你的输出内容有格式要求，**请一定严格按照要求的数据模式输出！！**
# 审计证据分类与质量要求
{review_req_method}
"""              )
            system_message = system_mess_template.format(review_req_method=review_req_method)

            template = PromptTemplate(
                input_variables=["query_and_result","open_brace","close_brace"],
                template="""
# 已获取审计证据
- 你已经收集了审计记录中的审计证据如下：
{query_and_result}
- 注意：信息不一定完全全面地搜索了实际审计记录中的**审计证据分类与质量要求**证据信息，如有信息不足的情况，需要搜索或请求补充
# 任务
请严格依据你掌握的**审计证据分类与要求**，分情况完成任务：
1. 对于可以确定信息搜索完全的审计证据，请逐一匹配对应的**审计证据分类与质量要求**信息，按如下格式对**已获取审计证据**的整理与质量评估
{open_brace}"证据内容":"example_evidence_content","文件名称":"example_filename.html","证据整理与质量评估":[{open_brace}"证据":"example_evidence_1","信息定位":["example_Xpath_1","example_Xpath_2"],"质量评估":{open_brace}"结论":"达标 or 不达标","理由","example_reason"{close_brace}{close_brace}]{close_brace}
- 注意："证据整理与质量评估"的结果可能有多个，所以需要用列表保存；"质量评估"-"结论"只能是"达标"或"不达标"
2. 对于可以确定信息不存在审计记录中的审计证据，请逐一匹配对应的**审计证据分类与要求**信息，按如下格式对**已获取审计证据**的整理与质量评估
{open_brace}"证据内容":"example_evidence_content","文件名称":"example_filename.html","证据整理与质量评估":[{close_brace}
- 注意："证据整理与质量评估"列表为空
3. 对于无法确定信息是否存在审计记录中的审计证据，或无法完成质量评估的的审计证据，可以采用工具
"""              )
            user_message = template.format(query_and_result=query_and_result, open_brace="{", close_brace="}")
            messages_list = [{"role":"system","content":system_message},{"role":"user","content": user_message}]
            result = self.llm.invoke(messages_list)
            messages_list.append(result)
            return {"messages": messages_list}
    
    def review_conclusion_agent(self, state: State) -> dict:
        review_result = state["review_result"][state["task_index"]]
        template = PromptTemplate(
            input_variables=["review_result", "open_brace", "close_brace"],
            template="""
# 已有复核结果
- 你先前已经完成的复审结果整理如下，它没有整理你最近一轮的复核结果。
{review_result}
# 任务
现在
1. 请你总结最近一轮的复核结果获取的信息或结论，基于**审计证据分类与质量要求**顺序，用于补充、修改**已有复核结果*，如果确定**已有复核结果**某些信息错误，则需修改对应部分。
2. 判断检查**已有复核结果**，判断是否已经确定**审计证据分类与质量要求**中的证据已经完成整理与质量评估，或确定证据不存在与审计记录中。
- 若是，回复yes
- 若否，则回答no
# 输出格式
请严格按照以下的数据模式输出！！
注意"信息定位"的值类型是字符串
``` json
{open_brace}"检查结果":"yes or no","最新复核结果":[{open_brace}"文件名称":{open_brace}"证据内容":"example","质量要求":"example","相关证据与质量评估":[{open_brace}"证据":"example","信息定位":'["example_Xpath_1","example_Xpath_2"]',"质量评估":{open_brace}"结论":"达标 or 不达标","理由":"example"{close_brace}{close_brace}]{close_brace}{close_brace}]{close_brace}
```
"""         )
        prompt = template.format(review_result=review_result, open_brace="{", close_brace="}")
        messages_list = state["messages"].copy()
        messages_list.append({"role":"user","content":prompt})
        result = self.llm.invoke(messages_list)
        result_content = result.content if hasattr(result, 'content') else str(result)
        
        # 使用新的验证方法
        is_valid, extracted_content, error_msg = self._extract_llm_result(result_content, "json")
        # 更新列表，只保留最后一轮对话，添加到"messages"列表中
        messages_list = [{"role":"user","content":prompt}] + [result]
        if is_valid:
            result_data = json.loads(extracted_content)
            if result_data["最新复核结果"]:
                review_result = result_data["最新复核结果"]
            else:
                review_result = state["review_result"][state["task_index"]]
            evaluation = result_data["检查结果"]
            state["review_result"][state["task_index"]] = review_result
            return {
                    "review_result": state["review_result"],
                    "evaluation": evaluation,
                    "messages": messages_list
                        }
        else:
            # 处理验证失败的情况
            return {
                "review_result": state["review_result"],
                "evaluation": "no",
                "messages": messages_list
            }
    
    def finally_conclude(self, state: State) -> dict:
        # state["review_result"]的索引表示任务序号，state["task_index"]获取当前任务序号，以正确的将复核结果写入当前任务中。
        review_result = state["review_result"][state["task_index"]]
        task_info = state["task_list"][state["task_index"]]
        review_req_method = task_info        
        if state["counter"] > MAX_TRIES:
            template = PromptTemplate(
                input_variables=["review_req_method", "review_result", "open_brace", "close_brace"],
                template="""
# 审计证据分类与质量要求
{review_req_method}          
# 已有复核结果与评估情况
- 最新的复核结果整理如下，它不能完全复核既定的复核要求。
{review_result}
# 任务
为了让相关工作人员后续能够基于你的工作继续完善复核结果，让他们明确你的哪些复核结果是确定的，哪些复核结果或信息是你不确定的。你需要完成最后的整理与备注。
- 请逐一检查**审计证据分类与质量要求**的每一项"证据内容"
  - 若"证据内容"存在于"已有复核结果与评估情况"中，基于在**审计证据分类与质量要求**组织架构与内容，添加一个与"证据内容"同级别的键"相关证据与质量评估"，并将匹配的"已有复核结果与评估情况"的"相关证据与质量评估"值写入
  - 若"证据内容"不存在于"已有复核结果与评估情况"中，基于在**审计证据分类与质量要求**组织架构与内容，请添加一个与"审计证据分类与质量要求"同级别的键"警告"，写入"结果无法确定"
- 输出格式示例
{open_brace}
          "example_category": {open_brace}
            "example_sub_category": [
              {open_brace}
                "证据内容": "example_1",
                "质量要求":"example_1",
                "相关证据与质量评估": [empty or "example_1","example_2"]
              {close_brace},
              {open_brace}
                "证据内容": "example_2",
                "质量要求":"example_2",
                "警告":"结果无法确定"
              {close_brace}]              
            {close_brace}
            {close_brace}             
""
"""              )
        else:
            template = PromptTemplate(
                input_variables=["review_req_method", "review_result", "open_brace", "close_brace"],
                template="""
# 审计证据分类与质量要求
{review_req_method}          
# 已有复核结果与评估情况
{review_result}
# 任务
- 请逐一检查**审计证据分类与质量要求**的每一项"证据内容"
  - 若"证据内容"存在于"已有复核结果与评估情况"中，基于在**审计证据分类与质量要求**组织架构与内容，添加一个与"证据内容"同级别的键"相关证据与质量评估"，并将匹配的"已有复核结果与评估情况"的"相关证据与质量评估"值写入
- 输出格式示例
{open_brace}
          "example_category": {open_brace}
            "example_sub_category": [
              {open_brace}
                "证据内容": "example_1",
                "质量要求":"example_1",
                "相关证据与质量评估": [empty or "example_1","example_2"]
              {close_brace}]
{close_brace}
{close_brace}           
"""         )
        prompt = template.format(review_req_method=review_req_method,review_result=review_result, open_brace="{", close_brace="}")
        user_message = {"role":"user","content":prompt}
        messages_list = state["messages"].copy()
        messages_list.append(user_message)
        result = self.llm.invoke(messages_list)
        
        # 使用新的验证方法
        is_valid, extracted_content, error_msg = self._extract_llm_result(result.content, "json")
        
        if is_valid:
            result_data = json.loads(extracted_content)
            result_content = result_data
            state["review_result"][state["task_index"]] = result_content
            # 更新列表，只保留最后一轮对话，添加到"messages"列表中
            messages_list = [user_message] + [result]
            return {
                "review_result": state["review_result"],
                "messages": messages_list
            }
        else:
            # 错误处理
            # 更新列表，只保留最后一轮对话，添加到"messages"列表中
            messages_list = [user_message] + [result]
            return {
                "review_result": state["review_result"],
                "messages": messages_list
            }


    def invoke_with_validation(self, prompt: str, validation_type: str = "json") -> tuple[bool, str, str]:
        """
        调用LLM并验证结果格式
        
        Args:
            prompt: 发送给LLM的提示词
            validation_type: 验证类型 ("json", "html_section")
            
        Returns:
            tuple: (是否符合格式, 提取的结果, 错误信息)
        """
        try:
            result = self.llm.invoke([{"role":"user","content":prompt}])
            content = result.content if hasattr(result, 'content') else str(result)
            
            # 验证格式
            is_valid, error_msg = self._validate_format(content, validation_type)
            
            if is_valid:
                return True, content, ""
            
            # 如果格式不正确，尝试用正则表达式提取
            extracted_content = self._extract_with_regex(content, validation_type)
            
            if extracted_content:
                # 验证提取的内容是否符合格式要求
                is_valid_extracted, error_msg_extracted = self._validate_format(extracted_content, validation_type)                
                if is_valid_extracted:
                    return True, extracted_content, f"从原始输出中提取: {error_msg}"
                else:
                    # 即使提取了内容，但格式仍然不正确
                    return False, content, error_msg_extracted
            else:  # 没有提取到内容或提取内容无效
                return False, content, error_msg
            
        except Exception as e:
            return False, "", f"调用LLM时出错: {str(e)}"
    
    def _extract_llm_result(self, content: str, validation_type: str) -> str:
        """
        从LLM的输出中提取内容
        
        Args:
            content: 待提取的内容
            validation_type: 验证类型 ("json", "html_section")
            
        Returns:
            str: 提取的内容
        """    
        # 验证格式
        is_valid, error_msg = self._validate_format(content, validation_type)
        
        if is_valid:
            return True, content, ""
        
        # 如果格式不正确，尝试用正则表达式提取
        extracted_content = self._extract_with_regex(content, validation_type)
        
        if extracted_content:
            # 验证提取的内容是否符合格式要求
            is_valid_extracted, error_msg_extracted = self._validate_format(extracted_content, validation_type)                
            if is_valid_extracted:
                return True, extracted_content, f"从原始输出中提取: {error_msg}"
            else:
                # 即使提取了内容，但格式仍然不正确
                return False, content, error_msg_extracted
        else:  # 没有提取到内容或提取内容无效
            return False, content, error_msg        


    def _validate_format(self, content: str, validation_type: str) -> tuple[bool, str]:
        """
        验证内容是否符合预期格式
        
        Args:
            content: 待验证的内容
            validation_type: 验证类型 ("json", "html_section")
            
        Returns:
            tuple: (是否符合格式, 错误信息)
        """
        try:
            if validation_type == "json":
                # 尝试解析JSON
                parsed = json.loads(content)
                # 移除额外验证，只验证是否为有效的JSON
                return True, ""
            elif validation_type == "html_section":
                # 检查是否包含<section>标签
                if "<section" in content and "</section>" in content:
                    return True, ""
                else:
                    return False, "缺少<section>标签"
            else:
                return False, f"不支持的验证类型: {validation_type}"
        except json.JSONDecodeError as e:
            return False, f"JSON格式错误: {str(e)}"
        except Exception as e:
            return False, f"格式验证时出错: {str(e)}"
    
    def _extract_with_regex(self, content: str, validation_type: str) -> str:
        """
        使用正则表达式从内容中提取符合格式的信息
        
        Args:
            content: 原始内容
            validation_type: 提取类型 ("json", "html_section")
            
        Returns:
            str: 提取的内容，如果无法提取则返回空字符串
        """
        try:
            if validation_type == "json":
                # 处理特殊情况：嵌套的代码块标记
                # 比如: ``` ``` json [...] ``` ```
                nested_code_block_pattern = r'```(?:\s*```(?:\s*json)?\s*([\s\S]*?)\s*```\s*)```'
                nested_matches = re.findall(nested_code_block_pattern, content, re.DOTALL)
                for match in nested_matches:
                    if match.strip():
                        try:
                            json.loads(match)
                            return match
                        except json.JSONDecodeError:
                            continue
                
                # 首先尝试提取代码块中的JSON
                code_block_patterns = [
                    r'```(?:json)?\s*([\s\S]*?)\s*```',  # 匹配```json或```代码块
                ]
                
                # 收集所有可能的匹配项
                all_json_candidates = []
                
                for pattern in code_block_patterns:
                    matches = re.findall(pattern, content, re.DOTALL)
                    for match in matches:
                        # 过滤掉空的或只包含空白字符的匹配项
                        if match.strip():
                            try:
                                # 验证提取的内容是否为有效JSON
                                parsed = json.loads(match)
                                # 如果是有效的JSON，添加到候选列表
                                all_json_candidates.append((match, len(match)))  # (内容, 长度)
                            except json.JSONDecodeError:
                                # 如果提取的JSON无效，则继续尝试其他模式
                                continue
                
                # 如果没有找到有效的代码块JSON，尝试更宽松的匹配模式
                if not all_json_candidates:
                    # 尝试匹配可能被错误分割的代码块
                    # 使用更宽松的正则表达式来匹配代码块内容
                    loose_patterns = [
                        r'```\s*json\s*([\s\S]*?)\s*```',
                        r'```\s*([\s\S]*?)\s*```',
                    ]
                    
                    for pattern in loose_patterns:
                        matches = re.findall(pattern, content, re.DOTALL)
                        for match in matches:
                            if match.strip():
                                try:
                                    parsed = json.loads(match)
                                    all_json_candidates.append((match, len(match)))
                                except json.JSONDecodeError:
                                    continue
                
                # 按长度排序，优先返回更长的匹配项（更完整）
                all_json_candidates.sort(key=lambda x: x[1], reverse=True)
                if all_json_candidates:
                    return all_json_candidates[0][0]
                
                # 如果代码块中没有找到有效的JSON，尝试直接匹配最外层的JSON对象或数组
                # 优先匹配对象，然后是数组
                object_matches = self._match_outermost_braces(content, '{', '}')
                # 按长度降序排列，优先处理更大的匹配项（更可能是完整的JSON对象）
                object_matches.sort(key=len, reverse=True)
                for match in object_matches:
                    try:
                        json.loads(match)
                        return match
                    except json.JSONDecodeError:
                        continue
                        
                # 再尝试匹配数组
                array_matches = self._match_outermost_brackets(content, '[', ']')
                # 按长度降序排列，优先处理更大的匹配项（更可能是完整的JSON数组）
                array_matches.sort(key=len, reverse=True)
                for match in array_matches:
                    try:
                        json.loads(match)
                        return match
                    except json.JSONDecodeError:
                        continue
                
                return ""
                
            elif validation_type == "html_section":
                # 匹配<section>标签及其内容
                section_pattern = r'<section[^>]*>[\s\S]*?</section>'
                matches = re.findall(section_pattern, content)
                if matches:
                    return '\n'.join(matches)
                return ""
                
            return ""
        except Exception:
            return ""

    def _match_outermost_braces(self, text: str, open_char: str, close_char: str) -> list:
        """
        匹配最外层的括号结构
        
        Args:
            text: 要匹配的文本
            open_char: 开括号字符
            close_char: 闭括号字符
            
        Returns:
            list: 匹配到的最外层括号内容列表
        """
        matches = []
        stack = []
        start = -1
        
        for i, char in enumerate(text):
            if char == open_char:
                if len(stack) == 0:
                    start = i
                stack.append(char)
            elif char == close_char:
                if len(stack) > 0:
                    stack.pop()
                    if len(stack) == 0 and start != -1:
                        matches.append(text[start:i+1])
                        start = -1
                        
        return matches

    def _match_outermost_brackets(self, text: str, open_char: str, close_char: str) -> list:
        """
        匹配最外层的方括号结构
        
        Args:
            text: 要匹配的文本
            open_char: 开括号字符
            close_char: 闭括号字符
            
        Returns:
            list: 匹配到的最外层括号内容列表
        """
        return self._match_outermost_braces(text, open_char, close_char)
    
    def gen_audit_data_query(self, state: State) -> dict:
        task_index = state["task_index"]
        task_info = state["task_list"][task_index]

        template = PromptTemplate(
            input_variables=["audit_data_query"],
            template="""
# 你的角色
你是一名资深审计人员，深刻了解审计工作对应的审计记录。同时，你精通Xpath语句，擅长爬取html文档信息。
# 证据内容
**证据内容**指审计工作底稿中记录的审计证据对应的内容。
# html schema
所有审计记录信息都存储在html文件中，同类行审计工作记录信息存储于同一个html文件，同时所有html文件都满足以下schema.
``` html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>[文档标题]</title>
    <!-- 可选：基础 viewport meta 标签 -->
    <!-- <meta name="viewport" content="width=device-width, initial-scale=1.0"> -->
</head>
<body>
    <!-- 主容器 -->
    <main class="document">

        <!-- 文档头部信息 -->
        <header class="document__header">
            <h1 class="document__title">[主标题]</h1>
            <p class="document__info-item">[信息项 1: 例如 被审计单位：ABC公司]</p>
            <p class="document__info-item">[信息项 2: 例如 会计期间：2023-01-01至2023-12-31]</p>
            <!-- ... 更多信息项 ... -->
</header>

        <!-- 工作表 1 (例如 目录 Index) -->
        <section class="worksheet worksheet_type_index">
            <h2 class="worksheet__title">[工作表标题 1: 例如 目录 (索引号: 1370)]</h2>
            <!-- 工作表内的签名/日期信息 -->
            <p class="paragraph paragraph_type_signature">[签名信息: 例如 被审计单位：... 截止日期：... 编制人：张三 2024-1-1  复核人：李四 2024-1-2]</p>

            <!-- 数据表格 -->
            <table class="data-table data-table_type_index">
                <thead class="data-table__header">
                    <tr class="data-table__row">
                        <th class="data-table__header-cell">[表头 1]</th>
                        <th class="data-table__header-cell">[表头 2]</th>
                        <!-- ... 更多表头 ... -->
                    </tr>
                </thead>
                <tbody class="data-table__body">
                    <tr class="data-table__row">
                        <td class="data-table__cell data-table__cell_type_text">[数据 1,1]</td>
                        <td class="data-table__cell data-table__cell_type_text">[数据 1,2]</td>
                        <!-- ... 更多数据 ... -->
                    </tr>
                    <!-- ... 更多数据行 ... -->
                </tbody>
                <!-- 如果有表尾汇总 -->
                <!--
                <tfoot class="data-table__footer">
                    <tr class="data-table__row">
                        <td class="data-table__cell">[表尾数据]</td>
                        ...
                    </tr>
                </tfoot>
                -->
            </table>
        </section>

        <!-- 工作表 2 (例如 明细表 Details) -->
        <section class="worksheet worksheet_type_details">
            <h2 class="worksheet__title">[工作表标题 2: 例如 无形资产明细表 (索引号: 1370-3)]</h2>
            <p class="paragraph paragraph_type_signature">[签名信息]</p>

            <!-- 数据表格 -->
            <table class="data-table data-table_type_main">
                <thead class="data-table__header">
                    <tr class="data-table__row">
                        <th class="data-table__header-cell">[表头 A]</th>
                        <th class="data-table__header-cell">[表头 B]</th>
                        <!-- ... 更多表头 ... -->
                    </tr>
                </thead>
                <tbody class="data-table__body">
                    <tr class="data-table__row">
                        <td class="data-table__cell data-table__cell_type_text">[明细数据 1,A]</td>
                        <td class="data-table__cell data-table__cell_type_number">[明细数据 1,B]</td>
                        <!-- ... 更多明细数据 ... -->
                    </tr>
                    <tr class="data-table__row">
                        <td class="data-table__cell data-table__cell_type_text">[明细数据 2,A]</td>
                        <td class="data-table__cell data-table__cell_type_number">[明细数据 2,B]</td>
                        <!-- ... 更多明细数据 ... -->
                    </tr>
                    <!-- ... 更多明细数据行 ... -->
                </tbody>
            </table>

            <!-- 审计说明段落 -->
            <p class="paragraph paragraph_type_note">审计说明：</p>
            <p class="paragraph">[具体的审计说明内容...]</p>
        </section>

        <!-- 工作表 3 (例如 审定表 Finalization) -->
        <section class="worksheet worksheet_type_finalization">
            <h2 class="worksheet__title">[工作表标题 3: 例如 无形资产审定表 (索引号: 1370-2)]</h2>
            <p class="paragraph paragraph_type_signature">[签名信息]</p>

            <table class="data-table data-table_type_summary">
                <thead class="data-table__header">
                    <tr class="data-table__row">
                        <th class="data-table__header-cell">[表头 X]</th>
                        <th class="data-table__header-cell">[表头 Y]</th>
                        <!-- ... 更多表头 ... -->
                    </tr>
                </thead>
                <tbody class="data-table__body">
                    <tr class="data-table__row">
                        <td class="data-table__cell data-table__cell_type_text">[审定数据 1,X]</td>
                        <td class="data-table__cell data-table__cell_type_number">[审定数据 1,Y]</td>
                        <!-- ... 更多审定数据 ... -->
                    </tr>
                     <!-- ... 更多审定数据行 ... -->
                </tbody>
            </table>
        </section>

        <!-- 工作表 4 (例如 调整分录 Adjustment Entries) -->
        <section class="worksheet worksheet_type_adjustments">
            <h2 class="worksheet__title">[工作表标题 4: 例如 无形资产科目审计调整分录 (索引号: 1370-1)]</h2>
            <p class="paragraph paragraph_type_signature">[签名信息]</p>

            <table class="data-table data-table_type_entries">
                <thead class="data-table__header">
                    <tr class="data-table__row">
                        <th class="data-table__header-cell">[表头 M]</th>
                        <th class="data-table__header-cell">[表头 N]</th>
                        <!-- ... 更多表头 ... -->
                    </tr>
                </thead>
                <tbody class="data-table__body">
                    <tr class="data-table__row">
                        <td class="data-table__cell data-table__cell_type_text">[分录数据 1,M]</td>
                        <td class="data-table__cell data-table__cell_type_text">[分录数据 1,N]</td>
                         <td class="data-table__cell data-table__cell_type_number">[分录数据 1,O]</td>
                        <!-- ... 更多分录数据 ... -->
                    </tr>
                     <!-- ... 更多分录数据行 ... -->
                </tbody>
            </table>
        </section>

        <!-- 更多工作表 ... -->
        <!--
        <section class="worksheet worksheet_type_[specific_type]">
            <h2 class="worksheet__title">[工作表标题 N]</h2>
            <p class="paragraph paragraph_type_signature">[签名信息]</p>
            <table class="data-table data-table_type_[specific_type]">
                 ...
            </table>
            <p class="paragraph paragraph_type_note">审计说明：</p>
            <p class="paragraph">[说明内容...]</p>
        </section>
        -->

    </main>
</body>
</html>
```
# 任务
为了找到**证据内容**，请严格依照**html schema**，在以下搜索列表中，补充Xpath语句，来全面搜索出**"证据内容"**内的信息。请严格按**输出格式**输出，此外不要有任何说明。
# 输出格式
``` json
{audit_data_query}
```
# **现在，请你完成任务**
"""
        )
        
        audit_data_query = []
        for value in task_info.values():
            filename = [key for key in value.keys()][0]
            for evidence_contet in value[filename]:
                evidece_content = evidence_contet.get("证据内容","")
                audit_data_query.append({"证据内容":evidece_content,"文件名称":f"{filename}.html","Xpath":""})


        prompt = template.format(audit_data_query=audit_data_query)
        # 验证方法
        is_valid, result_content, error_msg = self.invoke_with_validation(prompt, "json")
        
        if is_valid:
            parsed = json.loads(result_content)

            # 标准化文件名，确保以.html结尾
            # 添加类型检查，防止 parsed 不是列表
            if not isinstance(parsed, list):
                parsed = [parsed] if parsed else []
            
            for item in parsed:
                # 确保 item 是字典
                if not isinstance(item, dict):
                    continue
                    
                if "文件名称" in item and item["文件名称"]:
                    item["文件名称"] = self.standardize_filename(item["文件名称"])
            
            return {"audit_data_query": parsed}
        else:
            # 处理错误情况
            return {"audit_data_query": []}
    
    def standardize_filename(self, filename: str) -> str:
        """
        将文件名统一修改为.html结尾
        """

        if not filename:
            return filename
            
        # 如果已经以.html结尾，则直接返回
        if filename.endswith('.html'):
            return filename
            
        # 如果包含其他扩展名，则替换为.html
        if '.' in filename:
            base_name = filename.split('.')[0]
            return f"{base_name}.html"
            
        # 如果没有扩展名，则添加.html
        return f"{filename}.html"
    
    def evaluate_query_result(self, state: State) -> dict:
        task_index = state["task_index"]
        query_and_result = state["audit_data_q_result"]
        template = PromptTemplate(
            input_variables=["query_and_result", "open_brace", "close_brace"],
            template="""
# 你的角色
你是一名资深审计人员，深刻了解审计工作对应的审计记录。同时，你精通Xpath语句，擅长爬取html文档信息。
# html schema
所有审计记录信息都存储在html文件中，同类行审计工作记录信息存储于同一个html文件，同时所有html文件都满足以下schema.
``` html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>[文档标题]</title>
    <!-- 可选：基础 viewport meta 标签 -->
    <!-- <meta name="viewport" content="width=device-width, initial-scale=1.0"> -->
</head>
<body>
    <!-- 主容器 -->
    <main class="document">

        <!-- 文档头部信息 -->
        <header class="document__header">
            <h1 class="document__title">[主标题]</h1>
            <p class="document__info-item">[信息项 1: 例如 被审计单位：ABC公司]</p>
            <p class="document__info-item">[信息项 2: 例如 会计期间：2023-01-01至2023-12-31]</p>
            <!-- ... 更多信息项 ... -->
</header>

        <!-- 工作表 1 (例如 目录 Index) -->
        <section class="worksheet worksheet_type_index">
            <h2 class="worksheet__title">[工作表标题 1: 例如 目录 (索引号: 1370)]</h2>
            <!-- 工作表内的签名/日期信息 -->
            <p class="paragraph paragraph_type_signature">[签名信息: 例如 被审计单位：... 截止日期：... 编制人：张三 2024-1-1  复核人：李四 2024-1-2]</p>

            <!-- 数据表格 -->
            <table class="data-table data-table_type_index">
                <thead class="data-table__header">
                    <tr class="data-table__row">
                        <th class="data-table__header-cell">[表头 1]</th>
                        <th class="data-table__header-cell">[表头 2]</th>
                        <!-- ... 更多表头 ... -->
                    </tr>
                </thead>
                <tbody class="data-table__body">
                    <tr class="data-table__row">
                        <td class="data-table__cell data-table__cell_type_text">[数据 1,1]</td>
                        <td class="data-table__cell data-table__cell_type_text">[数据 1,2]</td>
                        <!-- ... 更多数据 ... -->
                    </tr>
                    <!-- ... 更多数据行 ... -->
                </tbody>
                <!-- 如果有表尾汇总 -->
                <!--
                <tfoot class="data-table__footer">
                    <tr class="data-table__row">
                        <td class="data-table__cell">[表尾数据]</td>
                        ...
                    </tr>
                </tfoot>
                -->
            </table>
        </section>

        <!-- 工作表 2 (例如 明细表 Details) -->
        <section class="worksheet worksheet_type_details">
            <h2 class="worksheet__title">[工作表标题 2: 例如 无形资产明细表 (索引号: 1370-3)]</h2>
            <p class="paragraph paragraph_type_signature">[签名信息]</p>

            <!-- 数据表格 -->
            <table class="data-table data-table_type_main">
                <thead class="data-table__header">
                    <tr class="data-table__row">
                        <th class="data-table__header-cell">[表头 A]</th>
                        <th class="data-table__header-cell">[表头 B]</th>
                        <!-- ... 更多表头 ... -->
                    </tr>
                </thead>
                <tbody class="data-table__body">
                    <tr class="data-table__row">
                        <td class="data-table__cell data-table__cell_type_text">[明细数据 1,A]</td>
                        <td class="data-table__cell data-table__cell_type_number">[明细数据 1,B]</td>
                        <!-- ... 更多明细数据 ... -->
                    </tr>
                    <tr class="data-table__row">
                        <td class="data-table__cell data-table__cell_type_text">[明细数据 2,A]</td>
                        <td class="data-table__cell data-table__cell_type_number">[明细数据 2,B]</td>
                        <!-- ... 更多明细数据 ... -->
                    </tr>
                    <!-- ... 更多明细数据行 ... -->
                </tbody>
            </table>

            <!-- 审计说明段落 -->
            <p class="paragraph paragraph_type_note">审计说明：</p>
            <p class="paragraph">[具体的审计说明内容...]</p>
        </section>

        <!-- 工作表 3 (例如 审定表 Finalization) -->
        <section class="worksheet worksheet_type_finalization">
            <h2 class="worksheet__title">[工作表标题 3: 例如 无形资产审定表 (索引号: 1370-2)]</h2>
            <p class="paragraph paragraph_type_signature">[签名信息]</p>

            <table class="data-table data-table_type_summary">
                <thead class="data-table__header">
                    <tr class="data-table__row">
                        <th class="data-table__header-cell">[表头 X]</th>
                        <th class="data-table__header-cell">[表头 Y]</th>
                        <!-- ... 更多表头 ... -->
                    </tr>
                </thead>
                <tbody class="data-table__body">
                    <tr class="data-table__row">
                        <td class="data-table__cell data-table__cell_type_text">[审定数据 1,X]</td>
                        <td class="data-table__cell data-table__cell_type_number">[审定数据 1,Y]</td>
                        <!-- ... 更多审定数据 ... -->
                    </tr>
                     <!-- ... 更多审定数据行 ... -->
                </tbody>
            </table>
        </section>

        <!-- 工作表 4 (例如 调整分录 Adjustment Entries) -->
        <section class="worksheet worksheet_type_adjustments">
            <h2 class="worksheet__title">[工作表标题 4: 例如 无形资产科目审计调整分录 (索引号: 1370-1)]</h2>
            <p class="paragraph paragraph_type_signature">[签名信息]</p>

            <table class="data-table data-table_type_entries">
                <thead class="data-table__header">
                    <tr class="data-table__row">
                        <th class="data-table__header-cell">[表头 M]</th>
                        <th class="data-table__header-cell">[表头 N]</th>
                        <!-- ... 更多表头 ... -->
                    </tr>
                </thead>
                <tbody class="data-table__body">
                    <tr class="data-table__row">
                        <td class="data-table__cell data-table__cell_type_text">[分录数据 1,M]</td>
                        <td class="data-table__cell data-table__cell_type_text">[分录数据 1,N]</td>
                         <td class="data-table__cell data-table__cell_type_number">[分录数据 1,O]</td>
                        <!-- ... 更多分录数据 ... -->
                    </tr>
                     <!-- ... 更多分录数据行 ... -->
                </tbody>
            </table>
        </section>

        <!-- 更多工作表 ... -->
        <!--
        <section class="worksheet worksheet_type_[specific_type]">
            <h2 class="worksheet__title">[工作表标题 N]</h2>
            <p class="paragraph paragraph_type_signature">[签名信息]</p>
            <table class="data-table data-table_type_[specific_type]">
                 ...
            </table>
            <p class="paragraph paragraph_type_note">审计说明：</p>
            <p class="paragraph">[说明内容...]</p>
        </section>
        -->

    </main>
</body>
</html>
```
# 已有搜索与结果
为了找到在审计记录中找到**证据内容**，已有的搜索与执行结果如下：
{query_and_result}
# 任务
现在，你需要检查**已有搜索与结果**，判断是否所有的Xpath语句都正确搜索到了"证据内容"。
- 若是，回复yes
- 若否，即搜索错误或者搜索信息不足以满足"证据内容"需要，则回答no。并基于搜索的不足，继续生成查询语句。
# 输出格式
```
{open_brace}"检查结果":"yes","查询语句":[]{close_brace}
```
或者
```
{open_brace}"检查结果":"no","查询语句":[
{open_brace}"证据内容":"","文件名称":"","Xpath":"",{close_brace},
{open_brace}"证据内容":"","文件名称":"","Xpath":"",{close_brace}]
{close_brace}
```
# **现在，请你完成任务**
"""
        )
        prompt = template.format(query_and_result=query_and_result, open_brace="{", close_brace="}")
        # 修改调用方式，使用新的验证方法
        is_valid, result_content, error_msg = self.invoke_with_validation(prompt, "json")
        
        if is_valid:
            parsed = json.loads(result_content)
            if parsed.get("检查结果",""):
                if parsed["检查结果"].lower() == "yes":
                    return {"evaluation":"yes"}
                else:
                    return {"evaluation":"no","audit_data_query":parsed["查询语句"]}
        else:
            # 处理错误情况
            return {"audit_data_query": []}

class GraphProcessor:
    """封装处理状态图输入、输出的类

    
    """
    def __init__(self):
        pass

    def make_serializable(self, obj):
        # 将生成器转换为列表
        obj = list(obj)
        # 如果列表中有元素且第一个元素是字典
        if obj and isinstance(obj, list) and len(obj) > 0 and isinstance(obj[0], dict):
            # 返回第一个字典
            return obj[0]
        # 如果是其他情况，返回原对象
        return obj

# 节点功能函数
def manage_task(state: State) -> dict:
    task_list = state["task_data"]["审计证据标准"]["审计证据分类与要求"]
    review_result = [None] * len(task_list)
    return {"task_list": task_list,
            "review_result": review_result
            }

def execute_html_query(state: State) -> dict:
    """
    执行HTML查询并返回结果
    
    Args:
        state: 包含audit_data_query的State对象
        
    Returns:
        dict: 包含查询结果的字典
    """
    
    # 获取查询信息
    queries = state["audit_data_query"]
    
    # 按目标信息和文件名称分组
    grouped_queries = {}
    for query in queries:
        target_info = query.get("证据内容", "")
        filename = query.get("文件名称", "")
        xpath = query.get("Xpath", "") 
        
        if not filename or not xpath:
            continue
            
        key = (target_info, filename)
        if key not in grouped_queries:
            grouped_queries[key] = []
        grouped_queries[key].append(xpath)
    
    # 执行查询并收集结果
    query_results = []
    
    for (target_info, filename), xpaths in grouped_queries.items():
        file_results = []
        file_path = os.path.join(HTML_FILE_DIR, filename)
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            try:
                # 解析HTML文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = etree.HTML(content)
                
                # 执行每个XPath查询
                for xpath in xpaths:
                    try:
                        result_elements = tree.xpath(xpath)
                        # 将结果转换为字符串
                        if isinstance(result_elements, list):
                            result_text = ' '.join([etree.tostring(el, encoding='unicode', method='text') 
                                                  if not isinstance(el, str) else el 
                                                  for el in result_elements])
                        else:
                            result_text = str(result_elements)
                            
                        file_results.append({
                            "Xpath": xpath,
                            "Result": result_text
                        })
                    except Exception as e:
                        file_results.append({
                            "Xpath": xpath,
                            "Result": f"查询错误: {str(e)}"
                        })
            except Exception as e:
                file_results.append({
                    "Xpath": "N/A",
                    "Result": f"文件读取错误: {str(e)}"
                })
        else:
            file_results.append({
                "Xpath": "N/A",
                "Result": f"文件不存在: {file_path}"
            })
        
        query_results.append({
            "证据内容": target_info,
            "文件名称": filename,
            "查询结果": file_results
        })
    
    return {"audit_data_q_result": query_results}

def search_again(state: State) -> dict:
    """
    Search again for the query.
    """
    if state["counter"] > MAX_TRIES:
        return execute_html_query(state)
    return {"audit_data_q_result":state["audit_data_q_result"],
            "counter":0}
# 流程控制函数
def ctrl_times(state: State) -> dict:
    return {"counter": state["counter"] + 1}

def ctrl_progress(state: State) -> dict:
    return {"task_index": state["task_index"] + 1}

def clear_counter(state: State) -> dict:
    return {"counter": 0}

def clear_messages(state: State) -> dict:
    messages = state["messages"]
    # remove all messages
    return {"messages": [RemoveMessage(id=m.id) for m in messages]}

# 创建工具

class CallHelpForData(BaseModel):
    request: str = Field(description="需要人员补充的信息")
    reason: str = Field(description="基于当前工作，总结为什么需要人员补充的这些信息")
@tool("call_help_for_data", args_schema=CallHelpForData)
def call_help_for_data(request: str, reason: str) -> int:
    """当已有审计记录信息不足时，可以调用此工具，请求帮助补充信息"""
    response = interrupt({"stage":"执行复核，进一步搜索底稿信息","request":request,"reason":reason})
    res_case = response.res_case
    if res_case == "y":
        return response.data
    return "请基于已有信息继续完成复核"

class CallHelpForInstruction(BaseModel):
    request: str = Field(description="具体指出需要什么指导")
    reason: str = Field(description="基于当前工作，总结遇到了什么困难，使得无法做出准确判断")
@tool("call_help_for_instruction", args_schema=CallHelpForInstruction)
def call_help_for_instruction(request: str, reason: str) -> int:
    """当基于已有方法要求，不能准确做出复核结论时，可以调用此工具，请求具体指导"""
    response = interrupt({"stage":"执行复核，复核分析","request":request,"reason":reason})
    res_case = response.res_case
    if res_case == "y":
        return response.data
    return "请基于已有方法继续完成复核"


# 建立工具列表

tools = [call_help_for_data, call_help_for_instruction]


llm = ChatOpenAI(
    api_key=API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model=LLM_MODAL,  # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    temperature=0,
    # other params...
)
llm_with_tools = llm.bind_tools(tools)

llm_with_tools = LlmNode(llm_with_tools)
llm_without_tools = LlmNode(llm)

gen_audit_data_query = llm_without_tools.gen_audit_data_query
evaluate_query_result = llm_without_tools.evaluate_query_result

pre_review_agent = llm_with_tools.pre_review_agent
review_conclusion_agent = llm_without_tools.review_conclusion_agent
finally_conclude = llm_without_tools.finally_conclude

tool_node = BasicToolNode(tools)

# 构建langgraph图
graph_builder = StateGraph(State)

## 创建节点
graph_builder.add_node("manage_task", manage_task)
graph_builder.add_node("gen_audit_data_query", gen_audit_data_query)
graph_builder.add_node("execute_html_query", execute_html_query)
graph_builder.add_node("evaluate_query_result", evaluate_query_result)
graph_builder.add_node("ctrl_query_times", ctrl_times)
graph_builder.add_node("clear_query_times_counter",clear_counter)
graph_builder.add_node("execute_html_query_again", search_again)
graph_builder.add_node("pre_review_agent",pre_review_agent )
graph_builder.add_node("tools",tool_node )
graph_builder.add_node("review_conclusion_agent", review_conclusion_agent)
graph_builder.add_node("ctrl_review_times", ctrl_times)
graph_builder.add_node("clear_review_times_counter", clear_counter)
graph_builder.add_node("finally_conclude", finally_conclude)
graph_builder.add_node("ctrl_progress", ctrl_progress)
graph_builder.add_node("clear_messages", clear_messages)


## 路由函数，用于构建条件边
def decide_route(state: State) -> str:
    """
    Decide which route to take based on the state.
    """
    evaluation = state.get("evaluation")
    
    if evaluation is None:
        # 如果 evaluation 不存在，返回默认路由
        return "clear_query_times_counter"
    
    if evaluation:
        if evaluation == "no" and state["counter"] <= MAX_TRIES:
            return "execute_html_query"
        return "clear_query_times_counter"
    else:
        raise ValueError(f"Evaluating Error: {state}")
    
def route_tools(
    state: State,
):
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "review_conclusion_agent"

def decide_review_route(state: State) -> str:
    """
    Decide which route to take based on the state.
    """
    evaluation = state.get("evaluation")
    
    if evaluation is None:
        # 如果 evaluation 不存在，返回默认路由
        return "clear_review_times_counter"
    
    if evaluation:
        if evaluation == "no" and state["counter"] <= MAX_TRIES:
            return "pre_review_agent"
        return "clear_review_times_counter"
    else:
        raise ValueError(f"Evaluating Error: {state}")
  
def task_route(state: State) -> str:
    if state["task_index"] < len(state["task_list"]):
        return "gen_audit_data_query"
    return END

## 创建边
graph_builder.add_edge(START, "manage_task")
graph_builder.add_edge("manage_task", "gen_audit_data_query")
graph_builder.add_edge("gen_audit_data_query", "execute_html_query")
graph_builder.add_edge("execute_html_query", "evaluate_query_result")
graph_builder.add_edge("evaluate_query_result", "ctrl_query_times")
graph_builder.add_conditional_edges(
    "ctrl_query_times",
    decide_route,
    {"clear_query_times_counter": "clear_query_times_counter", "execute_html_query": "execute_html_query"},
)

graph_builder.add_edge("clear_query_times_counter", "execute_html_query_again")
graph_builder.add_edge("execute_html_query_again", "pre_review_agent")
graph_builder.add_conditional_edges(
    "pre_review_agent",
    route_tools,
    {"tools": "tools", "review_conclusion_agent": "review_conclusion_agent"},
)

graph_builder.add_edge("tools", "review_conclusion_agent")
graph_builder.add_edge("review_conclusion_agent", "ctrl_review_times")
graph_builder.add_conditional_edges(
    "ctrl_review_times",
    decide_review_route,
    {"clear_review_times_counter":"clear_review_times_counter", "pre_review_agent": "pre_review_agent"},
)

graph_builder.add_edge("clear_review_times_counter", "finally_conclude")
graph_builder.add_edge("finally_conclude", "clear_messages")
graph_builder.add_edge("clear_messages", "ctrl_progress")
graph_builder.add_conditional_edges(
    "ctrl_progress",
    task_route,
    {END: END, "gen_audit_data_query": "gen_audit_data_query"},
)
## graph_builder.add_edge("chatbot", END)在条件边下，执行条件边逻辑，此时无意义

def create_agent() -> StateGraph:
    return graph_builder






    
    





