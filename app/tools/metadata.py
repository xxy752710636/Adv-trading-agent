from typing import List
from pydantic import BaseModel, Field

from app.tools.schema import (
    ToolInputSchema,
    ToolOutputSchema,
)


class ToolMetadata(BaseModel):
    name: str

    description: str

    category: str = "market"

    # ======================================================
    # Tool Schema 1.0 兼容字段
    # ======================================================

    input_fields: List[str] = Field(
        default_factory=list
    )

    output_fields: List[str] = Field(
        default_factory=list
    )

    # ======================================================
    # Tool Schema 2.0
    # ======================================================

    inputs: ToolInputSchema = Field(
        default_factory=ToolInputSchema
    )

    outputs: ToolOutputSchema = Field(
        default_factory=ToolOutputSchema
    )

    # ======================================================
    # Tool 能力描述
    # ======================================================

    data_type: List[str] = Field(
        default_factory=list
    )

    requires_entity: bool = True

    dependencies: List[str] = Field(
        default_factory=list
    )

    realtime: bool = False

    historical: bool = False

    source_independent: bool = True

    enabled: bool = True

    tags: List[str] = Field(
        default_factory=list
    )