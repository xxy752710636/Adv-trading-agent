from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field


class ResolvedEntity(BaseModel):
    """
    标准化后的市场实体。
    """

    name: str
    type: str
    code: Optional[str] = None
    market: Optional[str] = None
    confidence: float = 0.0


class ResolveStatus(str, Enum):
    RESOLVED = "resolved"
    AMBIGUOUS = "ambiguous"
    NOT_FOUND = "not_found"
    ERROR = "error"


class EntityResolveResult(BaseModel):
    """
    EntityResolver 的统一输出。
    """

    status: ResolveStatus

    entity: Optional[ResolvedEntity] = None

    candidates: List[ResolvedEntity] = Field(
        default_factory=list
    )

    message: str = ""