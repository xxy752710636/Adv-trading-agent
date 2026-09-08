from typing import Dict, List

from app.tools.base import BaseTool
from app.tools.catalog import ToolCatalog


class ToolRegistry:
    """
    Tool 注册中心。

    Registry:
        管理 Tool 实例

    Catalog:
        管理 Tool 能力描述
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self.catalog = ToolCatalog()

    def register(
        self,
        requirement: str,
        tool: BaseTool,
    ):
        if requirement in self._tools:
            raise ValueError(
                f"Tool 已经注册: {requirement}"
            )

        self._tools[requirement] = tool

        metadata = tool.metadata

        # requirement 是 Planner 使用的抽象能力名称。
        # Tool.metadata.name 是真正的 Tool 名称。
        if metadata.name != requirement:
            metadata = metadata.model_copy(
                update={"name": requirement}
            )

        self.catalog.register(metadata)

    def get(self, requirement: str) -> BaseTool:
        tool = self._tools.get(requirement)

        if tool is None:
            raise ValueError(
                f"没有找到对应 Tool: {requirement}"
            )

        return tool

    def has(self, requirement: str) -> bool:
        return requirement in self._tools

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def list_metadata(self):
        return self.catalog.list_enabled()

    def describe_tools(self) -> List[dict]:
        return self.catalog.describe()