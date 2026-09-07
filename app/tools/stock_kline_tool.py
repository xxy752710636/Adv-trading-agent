from app.tools.base import BaseTool
from app.data.akshare_tx import AkShareTencentDataAdapter


class StockKlineTool(BaseTool):
    name = "stock_kline"
    description = "获取股票真实历史K线数据"

    def __init__(self):
        self.adapter = AkShareTencentDataAdapter()

    def execute(self, params):
        code = params.get("code")
        market = params.get("market")
        days = params.get("days", 60)
        adjustment = params.get("adjustment", "qfq")

        if not code:
            raise ValueError("缺少股票代码 code")

        if not market:
            raise ValueError("缺少市场 market")

        data = self.adapter.get_stock_kline(
            code=code,
            market=market,
            days=days,
            adjustment=adjustment,
        )

        return {
            "status": "success",
            "data": data.model_dump(),
        }