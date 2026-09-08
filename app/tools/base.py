from abc import ABC, abstractmethod
from typing import Any, Dict

from app.tools.metadata import ToolMetadata
from app.tools.schema import ToolSchema


class BaseTool(ABC):

    name: str = ""

    description: str = ""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name=self.name,
            description=self.description,
        )

    @property
    def schema(self) -> ToolSchema:
        metadata = self.metadata

        return ToolSchema(
            name=metadata.name,
            description=metadata.description,
            inputs=metadata.inputs,
            outputs=metadata.outputs,
            dependencies=metadata.dependencies,
            category=metadata.category,
            tags=metadata.tags,
            realtime=metadata.realtime,
            historical=metadata.historical,
            enabled=metadata.enabled,
        )

    @abstractmethod
    def execute(
        self,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:

        raise NotImplementedError