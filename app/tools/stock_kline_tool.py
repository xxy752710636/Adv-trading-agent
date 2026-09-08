from app.tools.base import BaseTool
from app.data.akshare_tx import AkShareTencentDataAdapter
from app.tools.metadata import ToolMetadata
from app.tools.schema import (
    ToolField,
    ToolInputSchema,
    ToolOutputSchema,
)


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

    @property
    def metadata(self):

        return ToolMetadata(

            name=self.name,

            description=self.description,

            category="market",

            # ==================================================
            # Schema 1.0 compatibility
            # ==================================================

            input_fields=[
                "code",
                "market",
                "days",
                "adjustment",
            ],

            output_fields=[
                "code",
                "name",
                "market",
                "bars",
                "meta",
            ],

            # ==================================================
            # Schema 2.0
            # ==================================================

            inputs=ToolInputSchema(
                fields=[

                    ToolField(
                        name="code",
                        type="string",
                        description="股票代码，例如 300750",
                        required=True,
                    ),

                    ToolField(
                        name="market",
                        type="string",
                        description="股票市场，例如 SZ、SH、BJ",
                        required=True,
                    ),

                    ToolField(
                        name="days",
                        type="integer",
                        description="获取历史K线数量",
                        required=False,
                        default=60,
                    ),

                    ToolField(
                        name="adjustment",
                        type="string",
                        description="复权方式，例如 qfq、hfq、none",
                        required=False,
                        default="qfq",
                    ),
                ]
            ),

            outputs=ToolOutputSchema(
                fields=[

                    ToolField(
                        name="code",
                        type="string",
                        description="股票代码",
                    ),

                    ToolField(
                        name="name",
                        type="string",
                        description="股票名称",
                    ),

                    ToolField(
                        name="market",
                        type="string",
                        description="股票市场",
                    ),

                    ToolField(
                        name="bars",
                        type="list[KlineBar]",
                        description="历史K线数据",
                    ),

                    ToolField(
                        name="meta",
                        type="MarketDataMeta",
                        description="市场数据元信息",
                    ),
                ]
            ),

            # ==================================================
            # Capability
            # ==================================================

            data_type=[
                "stock_kline",
                "daily_kline",
                "historical_market_data",
            ],

            requires_entity=True,

            dependencies=[],

            realtime=False,

            historical=True,

            source_independent=True,

            enabled=True,

            tags=[
                "stock",
                "kline",
                "daily",
                "historical",
            ],
        )