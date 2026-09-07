from app.analysis.technical_signal import TechnicalSignal


class TechnicalAnalyzer:

    def analyze(self, technical):

        bullish = 0
        bearish = 0

        signals = []

        # MA

        if technical.ma_alignment == "bullish":
            bullish += 2
            signals.append("均线多头排列")

        elif technical.ma_alignment == "bearish":
            bearish += 2
            signals.append("均线空头排列")

        # RSI

        if technical.rsi_14:

            if technical.rsi_14 < 30:
                bullish += 1
                signals.append("RSI超卖")

            elif technical.rsi_14 > 70:
                bearish += 1
                signals.append("RSI超买")

        # MACD

        if technical.macd_hist:

            if technical.macd_hist > 0:
                bullish += 1
                signals.append("MACD多头")

            else:
                bearish += 1
                signals.append("MACD空头")

        total = bullish + bearish

        strength = (
            max(bullish, bearish) / total
            if total > 0
            else 0
        )

        trend = (
            "bullish"
            if bullish > bearish
            else "bearish"
        )

        return TechnicalSignal(
            trend=trend,
            strength=strength,
            signals=signals,
            bullish_score=bullish,
            bearish_score=bearish,
            conclusion="；".join(signals)
        )