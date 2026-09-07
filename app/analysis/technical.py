from typing import List, Optional

from app.analysis.schema import (
    TechnicalAnalysis,
    MovingAverage,
    MovingAverageTrend,
)


class TechnicalAnalyzer:
    """
    确定性技术指标计算引擎。

    这里只负责计算，不负责：
        买入
        卖出
        预测未来价格
    """

    def analyze(
        self,
        bars: List,
        code: str = "",
        name: str = "",
        market: str = "",
        source_step: str = "",
    ) -> TechnicalAnalysis:

        if not bars:
            raise ValueError(
                "TechnicalAnalyzer 缺少 K 线数据"
            )

        closes = [
            float(bar.close)
            for bar in bars
        ]

        volumes = [
            float(bar.volume)
            for bar in bars
        ]

        latest_close = closes[-1]

        # ==========================
        # Moving Average
        # ==========================

        ma5_series = self._sma_series(
            closes,
            5,
        )

        ma10_series = self._sma_series(
            closes,
            10,
        )

        ma20_series = self._sma_series(
            closes,
            20,
        )

        ma60_series = self._sma_series(
            closes,
            60,
        )

        ma5 = self._last(
            ma5_series
        )

        ma10 = self._last(
            ma10_series
        )

        ma20 = self._last(
            ma20_series
        )

        ma60 = self._last(
            ma60_series
        )

        # ==========================
        # MA Trend
        # ==========================

        ma5_trend = self._analyze_ma_trend(
            ma5_series,
            5,
        )

        ma10_trend = self._analyze_ma_trend(
            ma10_series,
            10,
        )

        ma20_trend = self._analyze_ma_trend(
            ma20_series,
            20,
        )

        ma60_trend = self._analyze_ma_trend(
            ma60_series,
            60,
        )

        # ==========================
        # RSI
        # ==========================

        rsi14 = self._rsi(
            closes,
            14,
        )

        # ==========================
        # MACD
        # ==========================

        macd_dif, macd_dea, macd_hist = self._macd(
            closes
        )

        # ==========================
        # Volume
        # ==========================

        volume_ma5 = self._sma(
            volumes,
            5,
        )

        return TechnicalAnalysis(

            code=code,
            name=name,
            market=market,

            latest_close=latest_close,

            moving_averages=[
                MovingAverage(
                    period=5,
                    value=ma5,
                ),
                MovingAverage(
                    period=10,
                    value=ma10,
                ),
                MovingAverage(
                    period=20,
                    value=ma20,
                ),
                MovingAverage(
                    period=60,
                    value=ma60,
                ),
            ],

            moving_average_trends=[
                ma5_trend,
                ma10_trend,
                ma20_trend,
                ma60_trend,
            ],

            rsi_14=rsi14,

            macd_dif=macd_dif,
            macd_dea=macd_dea,
            macd_hist=macd_hist,

            volume_ma_5=volume_ma5,

            price_vs_ma5=self._compare(
                latest_close,
                ma5,
            ),

            price_vs_ma10=self._compare(
                latest_close,
                ma10,
            ),

            price_vs_ma20=self._compare(
                latest_close,
                ma20,
            ),

            ma_alignment=self._ma_alignment(
                ma5,
                ma10,
                ma20,
            ),

            trend=self._trend(
                latest_close,
                ma5,
                ma10,
                ma20,
            ),

            volume_status=self._volume_status(
                volumes,
                volume_ma5,
            ),

            data_quality="real",

            source_step=source_step,
        )

    # ==========================================================
    # SMA
    # ==========================================================

    @staticmethod
    def _sma(
        values: List[float],
        period: int,
    ) -> Optional[float]:

        if len(values) < period:
            return None

        return sum(
            values[-period:]
        ) / period

    @staticmethod
    def _sma_series(
        values: List[float],
        period: int,
    ) -> List[float]:

        if len(values) < period:
            return []

        result = []

        for i in range(
            period - 1,
            len(values),
        ):

            window = values[
                i - period + 1:
                i + 1
            ]

            result.append(
                sum(window) / period
            )

        return result

    # ==========================================================
    # EMA
    # ==========================================================

    @staticmethod
    def _ema_series(
        values: List[float],
        period: int,
    ) -> List[float]:

        if len(values) < period:
            return []

        multiplier = 2 / (
            period + 1
        )

        ema = (
            sum(values[:period])
            / period
        )

        result = [ema]

        for value in values[period:]:

            ema = (
                value - ema
            ) * multiplier + ema

            result.append(ema)

        return result

    # ==========================================================
    # MACD
    # ==========================================================

    @classmethod
    def _macd(
            cls,
            values: List[float],
    ):
        """
        标准 MACD(12, 26, 9)

        DIF = EMA12 - EMA26
        DEA = DIF 的 EMA9
        HIST = DIF - DEA
        """

        if len(values) < 35:
            return None, None, None

        ema12 = cls._ema_series(
            values,
            12,
        )

        ema26 = cls._ema_series(
            values,
            26,
        )

        # EMA12 与 EMA26 对齐
        # EMA12 第一个值对应第12根数据
        # EMA26 第一个值对应第26根数据
        offset = 26 - 12

        ema12_aligned = ema12[offset:]

        length = min(
            len(ema12_aligned),
            len(ema26),
        )

        dif_series = []

        for i in range(length):
            dif_series.append(
                ema12_aligned[i]
                - ema26[i]
            )

        if len(dif_series) < 9:
            return None, None, None

        dea_series = cls._ema_series(
            dif_series,
            9,
        )

        # DEA 第一个值对应 DIF 第9个值
        dif_aligned = dif_series[8:]

        length = min(
            len(dif_aligned),
            len(dea_series),
        )

        dif_final = dif_aligned[-length:]
        dea_final = dea_series[-length:]

        hist_series = []

        for dif, dea in zip(
                dif_final,
                dea_final,
        ):
            hist_series.append(
                dif - dea
            )

        return (
            dif_final[-1],
            dea_final[-1],
            hist_series[-1],
        )

    # ==========================================================
    # RSI
    # ==========================================================

    @staticmethod
    def _rsi(
        values: List[float],
        period: int,
    ) -> Optional[float]:

        if len(values) <= period:
            return None

        changes = []

        for i in range(
            1,
            len(values),
        ):
            changes.append(
                values[i]
                - values[i - 1]
            )

        gains = [
            max(change, 0)
            for change in changes
        ]

        losses = [
            max(-change, 0)
            for change in changes
        ]

        avg_gain = (
            sum(gains[:period])
            / period
        )

        avg_loss = (
            sum(losses[:period])
            / period
        )

        for i in range(
            period,
            len(gains),
        ):

            avg_gain = (
                avg_gain * (period - 1)
                + gains[i]
            ) / period

            avg_loss = (
                avg_loss * (period - 1)
                + losses[i]
            ) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss

        return 100 - (
            100 / (1 + rs)
        )

    # ==========================================================
    # MA Trend / Turning Point
    # ==========================================================

    @classmethod
    def _analyze_ma_trend(
        cls,
        series: List[float],
        period: int,
    ) -> MovingAverageTrend:

        if len(series) < 3:

            return MovingAverageTrend(
                period=period
            )

        current = series[-1]
        previous = series[-2]
        previous_2 = series[-3]

        slope = (
            current - previous
        )

        previous_slope = (
            previous - previous_2
        )

        if slope > 0:
            direction = "rising"

        elif slope < 0:
            direction = "falling"

        else:
            direction = "flat"

        turning_point = "none"

        # 从下降转向上升
        if (
            previous_slope < 0
            and slope > 0
        ):
            turning_point = "bullish_turn"

        # 从上升转向下降
        elif (
            previous_slope > 0
            and slope < 0
        ):
            turning_point = "bearish_turn"

        # 下降，但下降速度减缓
        elif (
            previous_slope < 0
            and slope < 0
            and slope > previous_slope
        ):
            turning_point = (
                "falling_deceleration"
            )

        # 上升，但上升速度减缓
        elif (
            previous_slope > 0
            and slope > 0
            and slope < previous_slope
        ):
            turning_point = (
                "rising_deceleration"
            )

        return MovingAverageTrend(
            period=period,

            current=current,
            previous=previous,
            previous_2=previous_2,

            slope=slope,
            previous_slope=previous_slope,

            direction=direction,

            turning_point=turning_point,
        )

    # ==========================================================
    # Price vs MA
    # ==========================================================

    @staticmethod
    def _compare(
        price,
        ma,
    ):

        if ma is None:
            return "unknown"

        if price > ma:
            return "above"

        if price < ma:
            return "below"

        return "equal"

    # ==========================================================
    # MA Alignment
    # ==========================================================

    @staticmethod
    def _ma_alignment(
        ma5,
        ma10,
        ma20,
    ):

        if (
            ma5 is None
            or ma10 is None
            or ma20 is None
        ):
            return "unknown"

        if (
            ma5 > ma10
            and ma10 > ma20
        ):
            return "bullish"

        if (
            ma5 < ma10
            and ma10 < ma20
        ):
            return "bearish"

        return "mixed"

    # ==========================================================
    # Trend
    # ==========================================================

    @staticmethod
    def _trend(
        price,
        ma5,
        ma10,
        ma20,
    ):

        if (
            ma5 is None
            or ma10 is None
            or ma20 is None
        ):
            return "unknown"

        if (
            price > ma5
            and ma5 > ma10
            and ma10 > ma20
        ):
            return "uptrend"

        if (
            price < ma5
            and ma5 < ma10
            and ma10 < ma20
        ):
            return "downtrend"

        return "sideways_or_mixed"

    # ==========================================================
    # Volume
    # ==========================================================

    @staticmethod
    def _volume_status(
        volumes,
        volume_ma5,
    ):

        if (
            not volumes
            or volume_ma5 is None
        ):
            return "unknown"

        current_volume = volumes[-1]

        if current_volume > volume_ma5 * 1.2:
            return "expanded"

        if current_volume < volume_ma5 * 0.8:
            return "contracted"

        return "normal"

    @staticmethod
    def _last(
        values,
    ):

        if not values:
            return None

        return values[-1]