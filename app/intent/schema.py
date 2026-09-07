from typing import List, Optional

from pydantic import BaseModel, Field


class Target(BaseModel):
    name: str
    type: str
    code: Optional[str] = None


class TechnicalContext(BaseModel):
    indicator: str = ""
    periods: List[int] = Field(default_factory=list)
    question: str = ""


class ResearchIntent(BaseModel):
    """
    用户投研任务的结构化表示。

    Intent Agent 负责生成。
    Planner 根据这个结构制定后续研究计划。
    """

    # 用户到底想做什么
    goal: str = ""

    # LLM 对本次意图识别的置信度
    confidence: float = 0

    # 研究对象
    targets: List[Target] = Field(default_factory=list)

    # 用户真正想解决的问题
    questions: List[str] = Field(default_factory=list)

    # 研究维度
    dimensions: List[str] = Field(default_factory=list)

    # 技术分析上下文
    technical_context: TechnicalContext = Field(
        default_factory=TechnicalContext
    )

    # 时间周期
    time_horizon: str = ""

    # 交易风格
    trading_style: str = ""

    # 需要的数据
    data_requirements: List[str] = Field(
        default_factory=list
    )

    # 用户特殊限制
    constraints: List[str] = Field(
        default_factory=list
    )