from typing import TypedDict, Any

from app.intent.schema import ResearchIntent
from app.entity.schema import ResolvedEntity


class AgentState(TypedDict, total=False):
    # 用户原始输入
    user_input: str

    # Intent Agent 输出
    intent: ResearchIntent

    # LLM Entity Extraction 输出
    extracted_entities: list

    # Entity Resolver 输出
    # 后续所有研究流程只信这个字段
    resolved_entities: list[ResolvedEntity]

    # Research Planner 输出
    plan: Any

    # Research Executor 输出
    tool_results: dict

    # 分析结果
    analysis: dict

    # 最终回答
    response: str

    # 流程错误
    errors: list