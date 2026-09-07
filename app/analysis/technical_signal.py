from pydantic import BaseModel


class TechnicalSignal(BaseModel):

    trend: str
    strength: float

    signals: list[str]

    bullish_score: float
    bearish_score: float

    support: float | None = None
    resistance: float | None = None

    conclusion: str