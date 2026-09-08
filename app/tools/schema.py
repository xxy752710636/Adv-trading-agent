from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolField(BaseModel):
    """
    Tool 的单个输入/输出字段定义。
    """

    name: str
    type: str

    description: str = ""

    required: bool = False

    default: Any = None


class ToolInputSchema(BaseModel):
    """
    Tool 输入 Schema。
    """

    fields: List[ToolField] = Field(default_factory=list)


class ToolOutputSchema(BaseModel):
    """
    Tool 输出 Schema。
    """

    fields: List[ToolField] = Field(default_factory=list)


class ToolSchema(BaseModel):
    """
    Tool Schema 2.0。

    描述一个 Tool 完整的输入、输出以及依赖关系。
    """

    name: str

    description: str = ""

    inputs: ToolInputSchema = Field(
        default_factory=ToolInputSchema
    )

    outputs: ToolOutputSchema = Field(
        default_factory=ToolOutputSchema
    )

    dependencies: List[str] = Field(
        default_factory=list
    )

    category: str = "market"

    tags: List[str] = Field(
        default_factory=list
    )

    realtime: bool = False

    historical: bool = False

    enabled: bool = True