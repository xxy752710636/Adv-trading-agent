from app.tools.base import BaseTool
from app.data.stock_market import TencentRealtimeAdapter
from app.tools.metadata import ToolMetadata
from app.tools.schema import (
    ToolField,
    ToolInputSchema,
    ToolOutputSchema,
)


class StockMarketTool(BaseTool):

    name = "stock_market"

    description = "获取股票真实实时市场行情"

    def __init__(self):
        self.adapter = TencentRealtimeAdapter()

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

        data = self.adapter.get_stock_market(
            code=code,
            market=market,
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
            ],

            output_fields=[
                "code",
                "name",
                "market",
                "price",
                "previous_close",
                "open",
                "high",
                "low",
                "change",
                "pct_change",
                "volume",
                "amount",
                "query_timestamp",
                "data_timestamp",
                "source",
                "data_quality",
                "data_freshness",
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
                        name="price",
                        type="float",
                        description="最新行情价格",
                    ),

                    ToolField(
                        name="previous_close",
                        type="float",
                        description="前收盘价",
                    ),

                    ToolField(
                        name="open",
                        type="float",
                        description="开盘价",
                    ),

                    ToolField(
                        name="high",
                        type="float",
                        description="最高价",
                    ),

                    ToolField(
                        name="low",
                        type="float",
                        description="最低价",
                    ),

                    ToolField(
                        name="change",
                        type="float",
                        description="涨跌额",
                    ),

                    ToolField(
                        name="pct_change",
                        type="float",
                        description="涨跌幅",
                    ),

                    ToolField(
                        name="volume",
                        type="float",
                        description="成交量",
                    ),

                    ToolField(
                        name="amount",
                        type="float",
                        description="成交额",
                    ),

                    ToolField(
                        name="query_timestamp",
                        type="datetime",
                        description="查询时间",
                    ),

                    ToolField(
                        name="data_timestamp",
                        type="datetime",
                        description="行情数据时间",
                    ),

                    ToolField(
                        name="source",
                        type="string",
                        description="数据来源",
                    ),

                    ToolField(
                        name="data_quality",
                        type="string",
                        description="数据质量",
                    ),

                    ToolField(
                        name="data_freshness",
                        type="string",
                        description="数据新鲜度",
                    ),
                ]
            ),

            # ==================================================
            # Capability
            # ==================================================

            data_type=[
                "stock_market",
                "stock_realtime",
                "market_snapshot",
            ],

            requires_entity=True,

            dependencies=[],

            realtime=True,

            historical=False,

            source_independent=True,

            enabled=True,

            tags=[
                "stock",
                "realtime",
                "price",
                "volume",
            ],
        )