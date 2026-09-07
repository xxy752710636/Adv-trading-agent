from typing import List
from pydantic import BaseModel


class ExtractedEntity(BaseModel):
    """
    Entity Extraction 阶段的实体。

    注意：
    这里只负责理解用户说了什么。
    不负责确认股票代码、市场。
    """
    name: str
    type: str
    confidence: float = 0.0


def extract_entities(text: str) -> List[ExtractedEntity]:
    """
    从用户输入中提取实体。

    当前阶段先采用轻量规则 + 结构化方式，
    后续接入 LLM 后可以直接替换内部实现。

    核心原则：
        Extraction 只识别：
            宁德时代 -> stock

        不负责：
            宁德时代 -> 300750 / SZ

        股票代码和市场必须交给 EntityResolver。
    """

    if not text:
        return []

    text = text.strip()

    entities = []

    # --------------------------------
    # 1. 股票代码直接识别
    # --------------------------------
    import re

    stock_codes = re.findall(
        r"(?<!\d)(\d{6})(?!\d)",
        text,
    )

    for code in stock_codes:
        entities.append(
            ExtractedEntity(
                name=code,
                type="stock",
                confidence=0.99,
            )
        )

    # --------------------------------
    # 2. 常见市场指数
    # --------------------------------

    index_keywords = [
        "上证指数",
        "沪指",
        "深证成指",
        "深成指",
        "创业板指",
        "科创50",
        "沪深300",
        "中证500",
        "中证1000",
    ]

    for keyword in index_keywords:
        if keyword in text:
            entities.append(
                ExtractedEntity(
                    name=keyword,
                    type="index",
                    confidence=0.95,
                )
            )

    # --------------------------------
    # 3. 常见板块
    # --------------------------------

    sector_keywords = [
        "半导体",
        "芯片",
        "人工智能",
        "AI",
        "机器人",
        "新能源",
        "光伏",
        "锂电池",
        "军工",
        "证券",
        "银行",
        "保险",
        "房地产",
        "有色金属",
        "汽车",
        "医药",
        "消费电子",
        "通信",
        "计算机",
    ]

    for keyword in sector_keywords:
        if keyword in text:
            entities.append(
                ExtractedEntity(
                    name=keyword,
                    type="sector",
                    confidence=0.85,
                )
            )

    # --------------------------------
    # 4. 当前不再维护股票固定名单
    # --------------------------------
    #
    # 股票名称识别最终交给 LLM Entity Extraction。
    #
    # 这里故意不写：
    #
    # STOCKS = [
    #     "剑桥科技",
    #     "东山精密",
    #     ...
    # ]
    #
    # 因为 A 股有 5000+ 股票，
    # 不应该依赖人工维护的股票列表。

    return _deduplicate_entities(entities)


def _deduplicate_entities(
        entities: List[ExtractedEntity],
) -> List[ExtractedEntity]:
    """
    去除重复实体。
    """

    result = {}

    for entity in entities:
        key = (entity.type, entity.name)

        if key not in result:
            result[key] = entity
        else:
            # 保留置信度更高的结果
            if entity.confidence > result[key].confidence:
                result[key] = entity

    return list(result.values())