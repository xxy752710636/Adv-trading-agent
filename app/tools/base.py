from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """
    所有研究工具的统一基础接口。

    Tool 只负责：
    1. 接收结构化参数
    2. 执行数据获取或计算
    3. 返回结构化结果

    Tool 不负责：
    - 理解用户问题
    - 制定研究计划
    - 生成最终回答
    """

    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行 Tool。

        params:
            工具需要的参数

        return:
            结构化结果
        """
        raise NotImplementedError