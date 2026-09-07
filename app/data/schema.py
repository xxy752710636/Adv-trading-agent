from typing import List
from pydantic import BaseModel, Field


class MarketDataMeta(BaseModel):
    source: str
    query_timestamp: str
    data_timestamp: str

    market_status: str = "unknown"

    timezone: str = "Asia/Shanghai"

    data_quality: str = "unknown"

    # 数据新鲜度
    # same_day
    # previous_trading_day
    # older
    # unknown
    data_freshness: str = "unknown"

    adjustment: str = "none"


class KlineBar(BaseModel):
    date: str

    open: float
    close: float
    high: float
    low: float

    volume: float = 0
    amount: float = 0

    amplitude: float = 0
    pct_change: float = 0
    change: float = 0
    turnover: float = 0


class StockKlineData(BaseModel):
    code: str
    name: str = ""
    market: str = ""

    period: str = "daily"

    bars: List[KlineBar] = Field(
        default_factory=list
    )

    meta: MarketDataMeta