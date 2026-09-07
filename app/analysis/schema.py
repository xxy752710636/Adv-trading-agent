from typing import List, Optional

from pydantic import BaseModel, Field


class MovingAverage(BaseModel):
    period: int
    value: Optional[float] = None


class MovingAverageTrend(BaseModel):
    period: int

    current: Optional[float] = None
    previous: Optional[float] = None
    previous_2: Optional[float] = None

    slope: Optional[float] = None
    previous_slope: Optional[float] = None

    direction: str = "unknown"

    turning_point: str = "none"


class TechnicalAnalysis(BaseModel):

    code: str = ""
    name: str = ""
    market: str = ""

    latest_close: Optional[float] = None

    moving_averages: List[MovingAverage] = Field(
        default_factory=list
    )

    moving_average_trends: List[MovingAverageTrend] = Field(
        default_factory=list
    )

    rsi_14: Optional[float] = None

    macd_dif: Optional[float] = None
    macd_dea: Optional[float] = None
    macd_hist: Optional[float] = None

    volume_ma_5: Optional[float] = None

    price_vs_ma5: str = "unknown"
    price_vs_ma10: str = "unknown"
    price_vs_ma20: str = "unknown"

    ma_alignment: str = "unknown"

    trend: str = "unknown"

    volume_status: str = "unknown"

    data_quality: str = "real"

    source_step: str = ""