import json
from typing import List

from app.intent.entity import ExtractedEntity
from app.llm.model import get_llm


def llm_extract_entities(text: str) -> List[ExtractedEntity]:
    """
    LLM Entity Extraction

    只负责：
        从用户自然语言中识别研究对象。

    不负责：
        股票代码确认
        股票市场确认
        股票实体真实性确认

    例如：

        用户：
        "分析宁德时代和中际旭创最近的走势"

        输出：

        宁德时代 -> stock
        中际旭创 -> stock

    然后由 EntityResolver 负责：

        宁德时代 -> 300750 / SZ
        中际旭创 -> 300308 / SZ
    """

    if not text or not text.strip():
        return []

    llm = get_llm()

    prompt = f"""
你是一个专业的 A 股投研 Entity Extraction Agent。

你的唯一任务：

从用户输入中提取用户明确提到的研究实体。

========================
用户输入
========================

{text}

========================
实体类型
========================

允许：

stock
sector
theme
index

========================
核心规则
========================

1. 只能提取用户输入中明确出现或明确指代的实体。

2. 不要因为用户提到“市场”就自动添加上证指数。

3. 不要因为用户提到“行业”就自动添加股票。

4. 不要因为用户询问股票，就自动添加行业或指数。

5. 不要添加用户没有提到的实体。

6. 股票名称只返回股票名称。

7. 股票代码如果用户明确输入，则可以直接作为 name 返回。

8. 严禁根据股票名称猜测股票代码。

9. 严禁根据股票名称猜测交易所。

10. 不需要返回 code。

11. 不需要返回 market。

12. 同一个实体只返回一次。

13. 如果无法确定某个词是不是研究实体，不要强行提取。

========================
示例
========================

用户：
分析宁德时代最近走势

输出：

{{
    "entities": [
        {{
            "name": "宁德时代",
            "type": "stock",
            "confidence": 0.99
        }}
    ]
}}

------------------------

用户：
看看中际旭创和比亚迪

输出：

{{
    "entities": [
        {{
            "name": "中际旭创",
            "type": "stock",
            "confidence": 0.99
        }},
        {{
            "name": "比亚迪",
            "type": "stock",
            "confidence": 0.99
        }}
    ]
}}

------------------------

用户：
分析半导体板块

输出：

{{
    "entities": [
        {{
            "name": "半导体",
            "type": "sector",
            "confidence": 0.99
        }}
    ]
}}

------------------------

用户：
AI 算力是不是下一轮主线

输出：

{{
    "entities": [
        {{
            "name": "AI 算力",
            "type": "theme",
            "confidence": 0.95
        }}
    ]
}}

------------------------

用户：
查询上证指数

输出：

{{
    "entities": [
        {{
            "name": "上证指数",
            "type": "index",
            "confidence": 0.99
        }}
    ]
}}

------------------------

用户：
现在市场怎么样

输出：

{{
    "entities": []
}}

不要因为“市场”这个词自动添加上证指数。

========================
最终输出
========================

只返回合法 JSON。

不要 Markdown。

不要解释。

格式：

{{
    "entities": [
        {{
            "name": "",
            "type": "stock/sector/theme/index",
            "confidence": 0
        }}
    ]
}}
"""

    result = llm.invoke(prompt)

    print("\n========== ENTITY EXTRACTION ==========")
    print("USER INPUT:")
    print(text)

    print("\n========== RAW LLM OUTPUT ==========")
    print(result.content)

    try:
        data = json.loads(result.content)
    except json.JSONDecodeError as e:
        print("\n[Entity Extraction] JSON 解析失败")
        print(e)
        raise

    entities_data = data.get("entities", [])

    entities = []

    for item in entities_data:

        name = str(item.get("name", "")).strip()
        entity_type = str(item.get("type", "")).strip()
        confidence = float(item.get("confidence", 0))

        if not name:
            continue

        if entity_type not in {
            "stock",
            "sector",
            "theme",
            "index",
        }:
            continue

        entities.append(
            ExtractedEntity(
                name=name,
                type=entity_type,
                confidence=confidence,
            )
        )

    return _deduplicate_entities(entities)


def _deduplicate_entities(
    entities: List[ExtractedEntity],
) -> List[ExtractedEntity]:

    result = {}

    for entity in entities:

        key = (
            entity.type,
            entity.name,
        )

        if key not in result:
            result[key] = entity

        elif entity.confidence > result[key].confidence:
            result[key] = entity

    return list(result.values())