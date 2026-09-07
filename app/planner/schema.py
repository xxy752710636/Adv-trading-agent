from typing import List, Optional

from pydantic import BaseModel, Field

from app.entity.schema import ResolvedEntity


class ResearchStep(BaseModel):
    id: str
    type: str
    data_requirement: str
    description: str
    dependencies: List[str] = Field(default_factory=list)


class ResearchPlan(BaseModel):
    goal: str = ""

    target_name: str = ""

    target_type: str = ""

    # ==========================================================
    # 真实解析后的研究实体
    #
    # 后续 ResearchExecutor 只能使用这里的实体。
    # ==========================================================

    resolved_entities: List[ResolvedEntity] = Field(
        default_factory=list
    )

    steps: List[ResearchStep] = Field(
        default_factory=list
    )

    reasoning: str = ""