from typing import Dict

from app.tools.base import BaseTool


class ToolRegistry:
    """
    Tool Registry

    负责把：

        data_requirement

    映射到：

        Tool
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(
        self,
        requirement: str,
        tool: BaseTool
    ):
        """
        注册 Tool。
        """

        if requirement in self._tools:
            raise ValueError(
                f"Tool 已经注册: {requirement}"
            )

        self._tools[requirement] = tool

    def get(
        self,
        requirement: str
    ) -> BaseTool:
        """
        根据 data_requirement 获取 Tool。
        """

        tool = self._tools.get(requirement)

        if tool is None:
            raise ValueError(
                f"没有找到对应 Tool: {requirement}"
            )

        return tool

    def has(
        self,
        requirement: str
    ) -> bool:
        return requirement in self._tools

    def list_tools(self):
        return list(self._tools.keys())