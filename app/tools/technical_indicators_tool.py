from app.tools.base import BaseTool
from app.analysis.technical import TechnicalAnalyzer
from app.data.schema import KlineBar


class TechnicalIndicatorsTool(BaseTool):
    name = "technical_indicators"
    description = "根据真实历史K线计算技术指标，包括MA、RSI、MACD、均线趋势等"

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