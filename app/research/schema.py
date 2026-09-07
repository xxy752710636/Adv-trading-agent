from typing import Any, Dict, List

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """
    研究报告中的证据。

    source_step:
        证据来自哪个 Research Step

    statement:
        对这条证据的自然语言描述

    data:
        原始结构化数据
    """

    source_step: str

    statement: str

    data: Dict[str, Any] = Field(
        default_factory=dict
    )


class ResearchReport(BaseModel):
    """
    Research Agent 最终研究报告。

    LLM 只能基于 ResearchContext 中已经存在的数据
    生成该结构。
    """

    question: str = ""

    conclusion: str = ""

    evidence: List[Evidence] = Field(
        default_factory=list
    )

    risks: List[str] = Field(
        default_factory=list
    )

    uncertainties: List[str] = Field(
        default_factory=list
    )

    data_timestamp: str = ""

    confidence: float = 0.0
