from app.tools.base import BaseTool
from app.analysis.technical import TechnicalAnalyzer
from app.data.schema import KlineBar
from app.tools.metadata import ToolMetadata
from app.tools.schema import (
    ToolField,
    ToolInputSchema,
    ToolOutputSchema,
)


class TechnicalIndicatorsTool(BaseTool):

    name = "technical_indicators"

    description = (
        "根据真实历史K线计算技术指标，包括MA、RSI、MACD、均线趋势等"
    )

    def __init__(self):
        self.analyzer = TechnicalAnalyzer()

    def execute(self, params):

        bars = params.get("bars")

        if not bars:
            raise ValueError(
                "technical_indicators 缺少 K 线数据 bars"
            )

        code = params.get("code", "")
        name = params.get("name", "")
        market = params.get("market", "")
        source_step = params.get("source_step", "")

        # ======================================================
        # 将 ToolExecutor / LangGraph 传递过来的 dict
        # 转换为 TechnicalAnalyzer 使用的 KlineBar 对象
        # ======================================================

        normalized_bars = []

        for bar in bars:

            if isinstance(bar, KlineBar):

                normalized_bars.append(bar)

            elif isinstance(bar, dict):

                normalized_bars.append(
                    KlineBar(**bar)
                )

            else:

                raise TypeError(
                    "technical_indicators 收到未知 K 线数据类型: "
                    f"{type(bar)}"
                )

        print(
            "\n[TechnicalIndicatorsTool] "
            f"收到 {len(normalized_bars)} 根 K 线"
        )

        # ======================================================
        # 技术分析
        # ======================================================

        result = self.analyzer.analyze(
            bars=normalized_bars,
            code=code,
            name=name,
            market=market,
            source_step=source_step,
        )

        return {
            "status": "success",
            "data": result.model_dump(),
        }

    @property
    def metadata(self):

        return ToolMetadata(

            name=self.name,

            description=self.description,

            category="analysis",

            # ==================================================
            # Schema 1.0 compatibility
            # ==================================================

            input_fields=[
                "bars",
                "code",
                "name",
                "market",
                "source_step",
            ],

            output_fields=[
                "code",
                "name",
                "market",
                "latest_close",
                "moving_averages",
                "moving_average_trends",
                "rsi_14",
                "macd_dif",
                "macd_dea",
                "macd_hist",
                "volume_ma_5",
                "price_vs_ma5",
                "price_vs_ma10",
                "price_vs_ma20",
                "ma_alignment",
                "trend",
                "volume_status",
                "data_quality",
            ],

            # ==================================================
            # Schema 2.0
            # ==================================================

            inputs=ToolInputSchema(
                fields=[

                    ToolField(
                        name="bars",
                        type="list[KlineBar]",
                        description="真实历史K线数据",
                        required=True,
                    ),

                    ToolField(
                        name="code",
                        type="string",
                        description="股票代码",
                        required=False,
                        default="",
                    ),

                    ToolField(
                        name="name",
                        type="string",
                        description="股票名称",
                        required=False,
                        default="",
                    ),

                    ToolField(
                        name="market",
                        type="string",
                        description="股票市场",
                        required=False,
                        default="",
                    ),

                    ToolField(
                        name="source_step",
                        type="string",
                        description="产生K线数据的上游步骤ID",
                        required=False,
                        default="",
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
                        name="latest_close",
                        type="float",
                        description="最新收盘价",
                    ),

                    ToolField(
                        name="moving_averages",
                        type="object",
                        description="MA均线数据",
                    ),

                    ToolField(
                        name="moving_average_trends",
                        type="object",
                        description="均线趋势",
                    ),

                    ToolField(
                        name="rsi_14",
                        type="float",
                        description="14日RSI",
                    ),

                    ToolField(
                        name="macd_dif",
                        type="float",
                        description="MACD DIF",
                    ),

                    ToolField(
                        name="macd_dea",
                        type="float",
                        description="MACD DEA",
                    ),

                    ToolField(
                        name="macd_hist",
                        type="float",
                        description="MACD Histogram",
                    ),

                    ToolField(
                        name="volume_ma_5",
                        type="float",
                        description="5日成交量均线",
                    ),

                    ToolField(
                        name="price_vs_ma5",
                        type="string",
                        description="价格与MA5关系",
                    ),

                    ToolField(
                        name="price_vs_ma10",
                        type="string",
                        description="价格与MA10关系",
                    ),

                    ToolField(
                        name="price_vs_ma20",
                        type="string",
                        description="价格与MA20关系",
                    ),

                    ToolField(
                        name="ma_alignment",
                        type="string",
                        description="均线排列状态",
                    ),

                    ToolField(
                        name="trend",
                        type="string",
                        description="趋势判断",
                    ),

                    ToolField(
                        name="volume_status",
                        type="string",
                        description="成交量状态",
                    ),

                    ToolField(
                        name="data_quality",
                        type="string",
                        description="数据质量",
                    ),
                ]
            ),

            # ==================================================
            # Capability
            # ==================================================

            data_type=[
                "technical_indicators",
                "technical_analysis",
            ],

            requires_entity=False,

            dependencies=[
                "stock_kline",
            ],

            realtime=False,

            historical=True,

            source_independent=True,

            enabled=True,

            tags=[
                "technical",
                "ma",
                "rsi",
                "macd",
                "trend",
            ],
        )