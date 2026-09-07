from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.intent.schema import ResearchIntent
from app.entity.schema import ResolvedEntity
from app.planner.schema import ResearchPlan
from app.research.schema import ResearchReport


class ResearchContext(BaseModel):

    # 用户原始问题
    user_input: str = ""

    # Intent Agent 输出
    intent: Optional[ResearchIntent] = None

    # Entity Resolver 输出
    entities: List[ResolvedEntity] = Field(
        default_factory=list
    )

    # Research Planner 输出
    plan: Optional[ResearchPlan] = None

    # 各个 Research Step 的原始结果
    tool_results: Dict[str, Any] = Field(
        default_factory=dict
    )

    # 最终研究报告
    report: Optional[ResearchReport] = None

    # Pipeline / Executor 错误
    errors: List[str] = Field(
        default_factory=list
    )
