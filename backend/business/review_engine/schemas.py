"""
数据模式定义
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class ReviewData(BaseModel):
    """
    审计复核任务数据模式，定义启动复核时传入业务层的数据模式
    
    JSON数据示例:
    {
      "重大事项概述": "example_major_event_description",
      "审计目标": "example_audit_objective",
      "审计证据标准": {
        "审计结论": "example_audit_conclusion",
        "审计证据分类与要求": [
          {
            "一级分类示例": {
              "二级分类示例": [
                {
                  "证据内容": "example_evidence_content",
                  "质量要求": "example_quality_requirements"
                }
              ]
            }
          }
        ],
        "充分、适当评判标准": "example_sufficiency_and_appropriateness_criteria"
      }
    }
    
    字段说明:
    - 重大事项概述: 描述被审计单位面临的重大事项或情况
    - 审计目标: 审计师需要达成的具体审计目标
    - 审计证据标准: 包含审计结论和证据要求的复合结构
      - 审计结论: 基于审计证据得出的结论
      - 审计证据分类与要求: 按类别组织的审计证据及其质量要求
        - 一级分类示例、二级分类示例:实际上需要赋予具体的键
          - to do
      - 充分、适当评判标准: 用于评估审计证据是否充分和适当的评判标准
    """
    重大事项概述: str = Field(..., description="重大事项概述")
    审计目标: str = Field(..., description="审计目标")
    
    class Config:
        # 允许使用任意类型，以支持复杂的嵌套结构
        arbitrary_types_allowed = True

    class AuditEvidenceStandard(BaseModel):
        """审计证据标准模型"""
        审计结论: str = Field(..., description="审计结论")
        审计证据分类与要求: List[Dict[str, Dict[str, List[Dict[str, str]]]]] = Field(..., description="审计证据分类与要求")
        充分_适当评判标准: str = Field(..., description="充分、适当评判标准")
    
    审计证据标准: AuditEvidenceStandard = Field(..., description="审计证据标准")


class ReviewConfig(BaseModel):
    """审计复核配置模型
    
    JSON数据示例:
    {
      "MAX_TRIES": 3,
      "WAIT_TIMES": {
        "file_loading": 10,
        "replying": 20
      }
    }
    
    字段说明:
    - MAX_TRIES: 最大尝试次数，用于重试机制
    - WAIT_TIMES: 等待时间配置，键为操作类型，值为等待秒数
      - file_loading: 文件加载等待时间
      - replying: 回复等待时间
    """
    MAX_TRIES: int = Field(..., description="最大尝试次数")

    class SPECIFIC_WAIT_TIMES(BaseModel):
        file_loading: int = Field(..., description="文件加载等待时间")
        replying: int = Field(..., description="回复等待时间")

    WAIT_TIMES: SPECIFIC_WAIT_TIMES

class UploadFileRequirement(BaseModel):
    """
    上传文件请求模型
    """
    filename_list: list = Field(..., description="需要补充的文件名列表")
    review_config: ReviewConfig = Field(..., description="默认复核设置信息")


class HelpRequirement(BaseModel):
    """
    调用帮助模型，定义智能体请求数据模式
    """
    stage: str = Field(..., description="当前复核阶段")
    request: str = Field(..., description="需要帮助的请求")
    reason: str = Field(..., description="基于当前工作，总结需求帮助的理由")


class WorkPaperFile(BaseModel):
    """
    工作底稿文件模型，定义工作底稿文件的数据模式
    
    JSON数据示例:
    {
      "filename": "example.xlsx",
      "content": "base64_encoded_string",
      "size": 1024
    }
    
    字段说明:
    - filename: 文件名
    - content: 文件内容（Base64编码的字符串）
    - size: 文件大小（字节）
    """
    filename: str = Field(..., description="文件名")
    content: str = Field(..., description="文件内容（Base64编码）")
    size: int = Field(..., description="文件大小（字节）")

class HelpResponseData(BaseModel):
    """
    帮助响应数据模型
    
    JSON数据示例:
    {
      "res_case": "y",
      "data": "帮助信息内容"
    }
    
    字段说明:
    - res_case: 是否提供帮助, 只能是"y"或"n"
    - data: 帮助信息
    """
    res_case: str = Field(..., description="是否提供帮助", pattern="^(y|n)$")
    data: str = Field(..., description="帮助信息")

class ReviewDetailItemLevel3(BaseModel):
    """
    复核结果明细第三级模型（证据相关模型）
    
    JSON数据示例:
    {
      "证据": "从工信部官网获取的《2024年光伏行业运行分析报告》PDF文件",
      "信息定位": "风险评估及计划工作底稿 > 了解被审计单位及其环境 > 影响被审计单位的行业/市场因素",
      "质量评估":
        {
          "结论": "达标",
          "理由": "来源为工信部，权威可靠；获取路径（URL、发布时间2024年7月15日）已完整记录；内容覆盖了产能、价格、政策等关键变量；发布时间在6个月内。该证据充分证明了行业整体处于供过于求的下行周期，对被审计单位构成重大外部压力，其适当性高。"
        }
    }
    
    字段说明:
    - 证据: 具体的审计证据描述
    - 信息定位: 证据在工作底稿中的位置
    - 质量评估: 对证据质量的评估列表
      - 结论: 评估结论（如"达标"）
      - 理由: 评估理由说明
    """
    证据: str = Field(..., description="具体的审计证据描述")
    信息定位: str = Field(..., description="证据在工作底稿中的位置")
    质量评估: Dict[str, str] = Field(description="对证据质量的评估结果")

class ReviewDetailItemLevel2(BaseModel):
    """
    复核结果明细第二级模型
    
    JSON数据示例:
    {
      "证据内容": "影响被审计单位的行业/市场因素",
      "质量要求": "",
      "相关证据与质量评估": [
        {
          "证据": "从工信部官网获取的《2024年光伏行业运行分析报告》PDF文件",
          "信息定位": "风险评估及计划工作底稿 > 了解被审计单位及其环境 > 影响被审计单位的行业/市场因素",
          "质量评估": 
            {
              "结论": "达标",
              "理由": "来源为工信部，权威可靠；获取路径（URL、发布时间2024年7月15日）已完整记录；内容覆盖了产能、价格、政策等关键变量；发布时间在6个月内。该证据充分证明了行业整体处于供过于求的下行周期，对被审计单位构成重大外部压力，其适当性高。"
            }        
        }
      ]
    }
    
    字段说明:
    - 证据内容: 证据内容描述
    - 质量要求: 对证据的质量要求
    - 相关证据与质量评估: 相关证据及其质量评估列表，可以为空列表
    """
    证据内容: str = Field(..., description="证据内容描述")
    质量要求: str = Field(..., description="对证据的质量要求")
    相关证据与质量评估: List[ReviewDetailItemLevel3] = Field(default_factory=list, description="相关证据及其质量评估列表，可以为空列表")

class StatisticalSummary(BaseModel):
    """
    统计整理模型
    
    JSON数据示例:
    {
      "证据总数": 10,
      "充分性情况": {
        "缺失数量": 2,
        "缺失详情": [
          {
            "证据内容": "行业分析报告（如有）",
            "质量要求": "应包含行业监管法规汇编",
            "证据类别": [
              "初步业务活动工作底稿",
              "行业分析报告"
            ]
          }
        ]
      },
      "适当性情况": {
        "不适当证据数量": 3,
        "详情": [
          {
            "证据": "某财经博客转载的行业评论文章",
            "信息定位": "初步业务活动工作底稿 > 行业分析报告 > 行业监管法规汇编（如有）",
            "质量评估":
              {
                "结论": "不达标",
                "理由": "来源为非权威的个人博客，缺乏独立性和公信力，属于被明确禁止的'非正式新闻稿'，无法为持续经营判断提供可靠依据，其适当性为零。"
              },
            "证据内容": "",
            "质量要求": "",
            "证据类别": [
              "初步业务活动工作底稿",
              "行业分析报告"
            ]
          }
        ]
      }
    }
    
    字段说明:
    - 证据总数: 审计证据总数
    - 充分性情况: 证据充分性情况
      - 缺失数量: 缺失证据数量
      - 缺失详情: 缺失证据详情列表
    - 适当性情况: 证据适当性情况
      - 不适当证据数量: 不适当证据数量
      - 详情: 不适当证据详情列表
    """
    
    class SufficiencyDetail(BaseModel):
        """
        充分性详情模型
        """
        缺失数量: int = Field(..., description="缺失证据数量")
        
        class MissingDetailItem(BaseModel):
            """
            缺失详情项模型
            """
            证据内容: str = Field(..., description="证据内容")
            质量要求: str = Field(..., description="质量要求")
            证据类别: List[str] = Field(..., description="证据类别列表")
        
        缺失详情: List[MissingDetailItem] = Field(..., description="缺失证据详情列表")
    
    class AppropriatenessDetail(BaseModel):
        """
        适当性详情模型
        """
        不适当证据数量: int = Field(..., description="不适当证据数量")
        
        class InappropriateDetailItem(BaseModel):
            """
            不适当详情项模型
            """
            证据: str = Field(..., description="证据")
            信息定位: str = Field(..., description="信息定位")
            质量评估: Dict[str, str] = Field(description="对证据质量的评估结果")
            证据内容: str = Field(..., description="证据内容")
            质量要求: str = Field(..., description="质量要求")
            证据类别: List[str] = Field(..., description="证据类别列表")
        
        详情: List[InappropriateDetailItem] = Field(..., description="不适当证据详情列表")
    
    证据总数: int = Field(..., description="审计证据总数")
    充分性情况: SufficiencyDetail = Field(..., description="证据充分性情况")
    适当性情况: AppropriatenessDetail = Field(..., description="证据适当性情况")


class ReviewResult(BaseModel):
    """
    审核结果完整模型
    
    JSON数据示例:
    {
      "重大事项概述": "被审计单位所属行业发生重大变化，导致对持续经营能力产生重大不确定性，可能导致收入舞弊风险等。",
      "审计结论": "根据获取的审计证据，认为\"被审计单位所属行业发生重大变化\"应作为\"可能导致对被审计单位持续经营能力产生重大疑虑的事项或情况\"。",
      "复核结果明细": [
        {
          "一级标题示例": {
            "二级标题示例": [
              {
                "证据内容": "影响被审计单位的行业/市场因素",
                "质量要求": "",
                "相关证据与质量评估": [
                  {
                    "证据": "从工信部官网获取的《2024年光伏行业运行分析报告》PDF文件",
                    "信息定位": "风险评估及计划工作底稿 > 了解被审计单位及其环境 > 影响被审计单位的行业/市场因素",
                    "质量评估": 
                      {
                        "结论": "达标",
                        "理由": "来源为工信部，权威可靠；获取路径（URL、发布时间2024年7月15日）已完整记录；内容覆盖了产能、价格、政策等关键变量；发布时间在6个月内。该证据充分证明了行业整体处于供过于求的下行周期，对被审计单位构成重大外部压力，其适当性高。"
                      }                    
                  }
                ]
              }
            ]
          }
        }
      ],
      "统计整理": {
        "证据总数": 10,
        "充分性情况": {
          "缺失数量": 2,
          "缺失详情": [
            {
              "证据内容": "行业分析报告（如有）",
              "质量要求": "应包含行业监管法规汇编",
              "证据类别": [
                "初步业务活动工作底稿",
                "行业分析报告"
              ]
            }
          ]
        },
        "适当性情况": {
          "不适当证据数量": 3,
          "详情": [
            {
              "证据": "某财经博客转载的行业评论文章",
              "信息定位": "初步业务活动工作底稿 > 行业分析报告 > 行业监管法规汇编（如有）",
              "质量评估": 
                {
                  "结论": "不达标",
                  "理由": "来源为非权威的个人博客，缺乏独立性和公信力，属于被明确禁止的'非正式新闻稿'，无法为持续经营判断提供可靠依据，其适当性为零。"
                },
              "证据内容": "",
              "质量要求": "",
              "证据类别": [
                "初步业务活动工作底稿",
                "行业分析报告"
              ]
            }
          ]
        }
      },
      "结论与原因": {
        "复核结论": "审计证据总体支持将行业重大变化作为持续经营重大疑虑事项，但初步业务活动阶段存在证据来源不可靠问题，影响证据适当性。",
        "业务原因": "在风险识别工作上，普遍存在证据来源不可靠的情况，部分依赖非权威渠道信息，未严格执行交叉验证与独立来源要求。"
      }
    }
    
    字段说明:
    - 重大事项概述: 重大事项概述
    - 审计结论: 审计结论
    - 复核结果明细: 复核结果明细列表，包含动态键名的一级分类
    - 统计整理: 统计整理信息
    - 结论与原因: 结论与原因
      - 复核结论: 复核结论
      - 业务原因: 业务原因
    """
    重大事项概述: str = Field(..., description="重大事项概述")
    审计结论: str = Field(..., description="审计结论")
    复核结果明细: List[Dict[str, Dict[str, List[ReviewDetailItemLevel2]]]] = Field(..., description="复核结果明细")
    统计整理: StatisticalSummary = Field(..., description="统计整理信息")
    
    class ConclusionAndReason(BaseModel):
        """
        结论与原因模型
        """
        复核结论: str = Field(..., description="复核结论")
        业务原因: str = Field(..., description="业务原因")
    
    结论与原因: ConclusionAndReason = Field(..., description="结论与原因")



# 集成数据模式

class EngineResponseData(BaseModel):
    """
    复核引擎响应数据模型

    字段说明:
    - response_type: 响应类型，只能是upload_file_requirement, help_requirement, review_result
      - upload_file_requirement, help_requirement, review_result
    """
    response_type: str = Field(..., description="响应类型", pattern="^(upload_file_requirement|help_requirement|review_result)$")
    data: UploadFileRequirement | HelpRequirement | ReviewResult = Field(..., description="响应数据")
    review_config: ReviewConfig = Field(..., description="默认复核配置")

class ResponseData(BaseModel):
    """
    用户响应数据模型

    字段说明:
    - response_type: 响应类型，只能是upload_file_response或help_response
      - upload_file_response, help_response
    """
    response_type: str = Field(..., description="响应类型", pattern="^(upload_file_response|help_response)$")
    data: List[WorkPaperFile] | HelpResponseData = Field(..., description="响应数据")



# InterfaceAgent相关数据模式
class ReplyInInteraction(BaseModel):
        """
        回复消息模型
        """
        用户意图: str = Field(..., description="识别用户发送消息的目的")
        是否完整: bool = Field(..., description="对实现用户目的，用户提供的信息是否完整")
        内容: str = Field(..., description="回复或引导")