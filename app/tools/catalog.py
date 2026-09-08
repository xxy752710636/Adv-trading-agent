from typing import List

from app.tools.metadata import ToolMetadata


class ToolCatalog:
    """
    Tool 能力目录。

    Registry 负责：
        Tool 是否存在、Tool 实例是什么

    Catalog 负责：
        Tool 能做什么
    """

    def __init__(self):
        self._metadata: dict[str, ToolMetadata] = {}

    def register(self, metadata: ToolMetadata):
        if metadata.name in self._metadata:
            raise ValueError(
                f"Tool Metadata 已经注册: {metadata.name}"
            )

        self._metadata[metadata.name] = metadata

    def get(self, name: str) -> ToolMetadata:
        metadata = self._metadata.get(name)

        if metadata is None:
            raise ValueError(
                f"没有找到 Tool Metadata: {name}"
            )

        return metadata

    def has(self, name: str) -> bool:
        return name in self._metadata

    def list_all(self) -> List[ToolMetadata]:
        return list(self._metadata.values())

    def list_enabled(self) -> List[ToolMetadata]:
        return [
            metadata
            for metadata in self._metadata.values()
            if metadata.enabled
        ]

    def describe(self) -> List[dict]:
        return [
            metadata.model_dump()
            for metadata in self.list_enabled()
        ]