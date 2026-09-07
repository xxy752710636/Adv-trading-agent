from app.tools.base import BaseTool
from app.data.stock_market import (TencentRealtimeAdapter)


class StockMarketTool(BaseTool):

    name = "stock_market"

    description = (
        "获取股票真实实时市场行情"
    )

    def __init__(self):

        self.adapter = (
            TencentRealtimeAdapter()
        )

    def execute(self, params):

        code = params.get("code")
        market = params.get("market")

        if not code:

            raise ValueError(
                "缺少股票代码 code"
            )

        if not market:

            raise ValueError(
                "缺少股票市场 market"
            )

        data = (
            self.adapter.get_stock_market(
                code=code,
                market=market,
            )
        )

        return {
            "status": "success",
            "data": data.model_dump(),
        }