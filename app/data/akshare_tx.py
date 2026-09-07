import akshare as ak
from datetime import datetime, timezone, timedelta

from app.data.schema import (
    StockKlineData,
    KlineBar,
    MarketDataMeta,
)


class AkShareTencentDataAdapter:

    def get_stock_kline(
        self,
        code: str,
        market: str,
        days: int = 60,
        adjustment: str = "qfq",
    ) -> StockKlineData:

        symbol = f"{market.lower()}{code}"

        # 查询时间
        query_time = datetime.now(
            timezone(timedelta(hours=8))
        )

        end_date = query_time.strftime("%Y%m%d")
        start_date = "20200101"

        adjust_map = {
            "none": "",
            "qfq": "qfq",
            "hfq": "hfq",
        }

        adjust = adjust_map.get(
            adjustment,
            "qfq",
        )

        try:

            df = ak.stock_zh_a_hist_tx(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust,
            )

        except Exception as e:

            raise RuntimeError(
                f"AkShare/Tencent K线获取失败: {e}"
            )

        if df is None or df.empty:

            raise RuntimeError(
                f"AkShare/Tencent 未返回K线数据: {code}"
            )

        # 只保留最近 N 根
        df = df.tail(days)

        bars = []

        for _, row in df.iterrows():

            bars.append(
                KlineBar(
                    date=str(row["date"]),
                    open=float(row["open"]),
                    close=float(row["close"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    volume=float(
                        row.get("volume", 0)
                    ),
                    amount=float(
                        row.get("amount", 0)
                    ),
                    turnover=float(
                        row.get("turnover", 0)
                    ),
                )
            )

        # 数据时间
        # 这里使用返回数据中的最后一个交易日
        data_timestamp = str(
            df.iloc[-1]["date"]
        )

        return StockKlineData(

            code=code,

            market=market,

            period="daily",

            bars=bars,

            meta=MarketDataMeta(

                source="akshare_tencent",

                query_timestamp=query_time.isoformat(),

                data_timestamp=data_timestamp,

                market_status="unknown",

                timezone="Asia/Shanghai",

                data_quality="real",

                adjustment=adjustment,
            ),
        )