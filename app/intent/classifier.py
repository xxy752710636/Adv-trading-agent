from app.intent.schema import (
    ResearchIntent,
    Target,
    TechnicalContext,
)

from app.intent.entity import extract_entities


def classify_intent(text: str) -> ResearchIntent:
    """
    将用户自然语言转换为统一的 ResearchIntent。

    当前版本：
    1. 使用已有 Entity Extractor 提取研究对象
    2. 根据实体类型判断基础研究方向
    3. 生成 Planner 所需要的 data_requirements

    后续可以将这里升级为 LLM Intent Classifier，
    但输出必须保持 ResearchIntent。
    """

    entities = extract_entities(text)

    targets = []

    for entity in entities:
        targets.append(
            Target(
                name=entity.name,
                type=entity.type,
                code=getattr(entity, "code", None),
            )
        )

    goal = text

    confidence = 0.5

    data_requirements = []
    dimensions = []
    questions = []

    technical_context = TechnicalContext()

    # =========================
    # 指数
    # =========================

    if any(e.type == "index" for e in entities):

        confidence = 0.95

        data_requirements = [
            "market_index",
        ]

        dimensions = [
            "market",
        ]

        questions = [
            f"获取{text}相关指数的最新行情数据"
        ]

    # =========================
    # 股票
    # =========================

    elif any(e.type == "stock" for e in entities):

        confidence = 0.90

        dimensions = [
            "stock",
        ]

        # 如果用户明确询问技术指标 / K线 / 均线
        if any(
            keyword in text
            for keyword in [
                "K线",
                "k线",
                "均线",
                "MA",
                "5日线",
                "10日线",
                "20日线",
                "60日线",
                "拐头",
                "技术",
                "MACD",
                "RSI",
                "成交量",
            ]
        ):

            data_requirements = [
                "stock_kline",
                "technical_indicators",
            ]

            dimensions.append("technical")

            technical_context = TechnicalContext(
                indicator="MA",
                periods=[5],
                question=text,
            )

            questions = [
                f"获取{text}相关股票近期K线数据",
                f"根据K线数据计算相关技术指标",
                text,
            ]

        else:

            data_requirements = [
                "stock_market",
            ]

            questions = [
                text,
            ]

    # =========================
    # 板块
    # =========================

    elif any(e.type == "sector" for e in entities):

        confidence = 0.90

        dimensions = [
            "sector",
        ]

        data_requirements = [
            "sector_market",
            "sector_capital_flow",
            "leader_stocks",
        ]

        questions = [
            f"获取{text}相关板块近期市场表现",
            f"获取{text}相关板块资金流向",
            f"获取{text}相关板块核心股票表现",
        ]

    # =========================
    # 未知
    # =========================

    else:

        confidence = 0.30

        questions = [
            text,
        ]

    return ResearchIntent(
        goal=goal,
        confidence=confidence,
        targets=targets,
        questions=questions,
        dimensions=dimensions,
        technical_context=technical_context,
        time_horizon="",
        trading_style="",
        data_requirements=data_requirements,
        constraints=[],
    )