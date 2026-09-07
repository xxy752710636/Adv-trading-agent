import json

from app.intent.schema import ResearchIntent
from app.intent.validator import validate_targets
from app.llm.model import get_llm


def llm_classify(text: str) -> ResearchIntent:
    """
    LLM Intent Classifier

    职责：
        1. 理解用户真正想研究什么
        2. 提取研究目标 targets
        3. 判断研究问题 / 维度 / 时间范围 / 交易风格
        4. 判断回答当前问题真正需要哪些数据

    不负责：
        1. 股票代码确认
        2. 股票市场确认
        3. 实体真实存在性确认
        4. 具体 Tool 选择
        5. 行情数据获取

    重要原则：

        Intent Agent 负责“理解用户想研究什么”。

        Entity Resolver 负责“确认这个实体到底是谁”。

        Market Data Tool 负责“获取真实市场数据”。

        Planner 负责“把 data_requirements 转成研究步骤”。

    因此：

        LLM 不允许猜股票代码。
        LLM 不允许猜交易所。
        LLM 不允许虚构实体。
        LLM 不允许直接决定具体 Tool。
    """

    if not text or not text.strip():
        raise ValueError("用户输入不能为空")

    llm = get_llm()

    prompt = f"""
你是一个专业的 A 股投研 Intent Agent。

你的任务是：

把用户的自然语言问题解析成结构化的 ResearchIntent。

你只负责理解“用户想研究什么、想解决什么问题”。

你不是 Entity Resolver。
你不是 Market Data Tool。
你不是 Research Planner。

因此你不能负责确认股票代码、交易所、实时行情，也不能自行补充用户没有提到的研究对象。

==================================================
一、最重要的实体规则
==================================================

1. targets 只能来自用户当前输入。

严禁因为你的知识、Prompt 中的示例、工具说明、
常见市场知识而自动增加用户没有提到的研究对象。

例如：

用户：
“看看宁德时代最近怎么样”

targets 只能是：

[
    {{
        "name": "宁德时代",
        "type": "stock",
        "code": null
    }}
]

不能增加：

上证指数
新能源
锂电池
创业板
沪深300

除非用户明确提到这些对象。


2. 股票代码不是 Intent Agent 的职责。

对于股票：

    code 必须始终为 null。

即使你知道：

宁德时代 = 300750
比亚迪 = 002594
中际旭创 = 300308
剑桥科技 = 603083

你也不能填写这些代码。

股票代码必须由后续 Entity Resolver
通过真实市场实体数据库 / 真实市场数据源确认。


3. 股票市场也不能由 Intent Agent 猜测。

不要在 targets 中增加：

SH
SZ
BJ

市场信息由 Entity Resolver 后续确认。


4. 不允许根据股票名称自行推断代码。

例如：

“宁德时代怎么样”

必须：

"code": null

而不是：

"code": "300750"


5. 用户直接输入六位股票代码时：

可以把这个六位数字作为 target.name。

例如：

用户：
“分析 300750”

可以返回：

{{
    "name": "300750",
    "type": "stock",
    "code": null
}}

注意：

这里仍然不能把 code 设置为 300750。

后续 Resolver 再确认。


==================================================
二、Intent Agent 的职责
==================================================

你需要判断：

1. 用户真正想解决的问题是什么
2. 研究对象是什么
3. 用户需要哪些研究维度
4. 用户提出了哪些具体问题
5. 时间范围
6. 交易风格
7. 为了回答这个问题，真正需要哪些数据

==================================================
三、goal 规则
==================================================

goal 表示：

“用户真正想解决的问题”。

不要简单重复用户原话。

例如：

用户：
“看看宁德时代最近怎么样”

goal 可以是：

“了解宁德时代近期市场表现”

用户：
“宁德时代基本面怎么样”

goal 可以是：

“评估宁德时代当前基本面状况”

用户：
“剑桥科技5日线是否拐头”

goal 可以是：

“判断剑桥科技短期5日均线是否出现拐点”


==================================================
四、questions 规则
==================================================

questions 表示：

为了回答用户问题，需要解决的核心问题。

例如：

用户：
“看看宁德时代最近怎么样”

可以是：

[
    "宁德时代近期市场表现如何？",
    "近期价格走势有什么明显特征？"
]

不要加入用户没有问的：

“公司估值是否合理？”
“公司基本面是否优秀？”
“行业政策怎么样？”
“机构资金是否流入？”

除非用户明确要求。


==================================================
五、dimensions 规则
==================================================

dimensions 表示本次研究真正需要关注的维度。

例如：

“看看宁德时代最近怎么样”

可以：

[
    "市场表现",
    "价格走势"
]

“宁德时代基本面怎么样”

可以：

[
    "基本面"
]

“宁德时代估值高不高”

可以：

[
    "估值"
]

“宁德时代最近有什么重大消息”

可以：

[
    "公司新闻"
]


==================================================
六、data_requirements 规则
==================================================

这是非常重要的字段。

data_requirements 表示：

为了回答“当前这个具体问题”，真正需要获取的数据类型。

它不是 Tool 名称。

不要直接填写：

stock_kline_tool
eastmoney
akshare
xxx_api

而是使用标准的数据需求 ID。


允许的数据需求 ID：

--------------------------------------------------
股票
--------------------------------------------------

stock_market
    股票近期市场表现

stock_kline
    股票近期行情 / K线数据

stock_fundamental
    股票基本面数据

stock_valuation
    股票估值数据

technical_indicators
    根据行情数据计算技术指标


--------------------------------------------------
行业 / 板块
--------------------------------------------------

sector_market
    行业 / 板块近期市场表现

sector_capital_flow
    行业 / 板块资金流向

sector_fundamental
    行业 / 板块基本面

sector_valuation
    行业 / 板块估值


--------------------------------------------------
主题
--------------------------------------------------

theme_market
    主题近期市场表现

theme_capital_flow
    主题资金流向

theme_leaders
    主题相关核心个股及市场表现


--------------------------------------------------
市场
--------------------------------------------------

market_index
    主要市场指数行情

market_sentiment
    当前市场情绪 / 风险偏好

market_capital_flow
    市场整体资金流向


--------------------------------------------------
新闻 / 信息
--------------------------------------------------

industry_news
    行业相关新闻、政策、产业信息

company_news
    公司相关新闻、公告

policy_news
    政策、监管信息


--------------------------------------------------
其他
--------------------------------------------------

leader_stocks
    相关板块核心龙头股票

valuation_data
    相关标的估值数据


==================================================
七、data_requirements 必须遵守“最小必要原则”
==================================================

只选择回答当前问题真正需要的数据。

不要为了看起来“全面”而机械添加：

基本面
估值
新闻
资金流
行业
市场情绪
指数

除非用户的问题确实需要这些数据。


--------------------------------------------------
典型例子
--------------------------------------------------

用户：

“看看宁德时代最近怎么样”

推荐：

[
    "stock_market",
    "stock_kline"
]

不要自动增加：

stock_fundamental
stock_valuation
company_news
market_sentiment
industry_news


--------------------------------------------------

用户：

“宁德时代基本面怎么样”

推荐：

[
    "stock_fundamental"
]


--------------------------------------------------

用户：

“宁德时代估值高不高”

推荐：

[
    "stock_valuation"
]


--------------------------------------------------

用户：

“宁德时代最近有什么重大消息”

推荐：

[
    "company_news"
]


--------------------------------------------------

用户：

“宁德时代最近走势怎么样”

推荐：

[
    "stock_market",
    "stock_kline"
]


--------------------------------------------------

用户：

“剑桥科技5日线是否拐头”

推荐：

[
    "stock_kline",
    "technical_indicators"
]

因为技术指标必须基于真实行情数据计算。


--------------------------------------------------

用户：

“全面分析宁德时代”

这种情况下才可以进行相对全面的研究。

例如：

[
    "stock_market",
    "stock_kline",
    "stock_fundamental",
    "stock_valuation",
    "company_news"
]

但也不要机械加入与问题明显无关的数据。


--------------------------------------------------

用户：

“比较中际旭创和比亚迪最近的表现”

应该优先关注：

[
    "stock_market",
    "stock_kline"
]

不要因为是“比较”就自动加入：

stock_fundamental
stock_valuation
company_news
market_sentiment

除非用户明确要求全面比较。


==================================================
八、技术分析规则
==================================================

如果用户明确提到：

5日线
10日线
20日线
60日线
均线
MA
MACD
RSI
KDJ
布林带
支撑位
压力位
突破
死叉
金叉
拐头
趋势结构

需要根据问题决定是否加入：

stock_kline
technical_indicators


例如：

“剑桥科技5日线是否拐头”

应该：

stock_kline
technical_indicators

因为：

technical_indicators 必须基于真实 K 线计算。

不能直接让 LLM 凭知识判断。


==================================================
九、时间范围规则
==================================================

time_horizon 表示用户明确表达的研究时间范围。

例如：

“最近”
“近期”
“过去一个月”
“近60个交易日”
“未来一周”
“中长期”

如果用户没有明确表达：

不要自行编造具体时间。

可以返回：

""


==================================================
十、trading_style 规则
==================================================

如果用户明确表达：

短线
超短
波段
中线
长线
价值投资
趋势交易

才填写。

如果用户没有表达：

返回：

""


==================================================
十一、严禁预测真实行情
==================================================

Intent Agent 不负责预测价格。

不要因为用户问：

“未来会涨吗？”

就自行生成：

上涨
下跌
目标价
涨幅

这些属于后续研究 / 分析阶段。

Intent Agent 只需要识别：

用户想研究未来走势。

==================================================
十二、不要把“市场”自动变成“上证指数”
==================================================

例如：

用户：

“现在市场怎么样？”

不能自动增加：

上证指数

也不能自动增加：

创业板指
沪深300
深证成指

targets 可以为空。

后续由 Planner 根据具体问题决定需要哪些市场数据。


==================================================
十三、不要过度推理
==================================================

你的任务不是“替用户设计一份完整研报”。

你的任务是：

准确理解当前问题。

宁可少选一个数据需求，
也不要因为“可能有帮助”而加入大量无关数据。


==================================================
十四、输出格式
==================================================

只返回合法 JSON。

不要输出 Markdown。

不要输出解释。

不要输出：

```json

只输出 JSON 对象。

格式：

{{
    "goal": "",
    "confidence": 0,
    "targets": [
        {{
            "name": "",
            "type": "stock/sector/theme/index",
            "code": null
        }}
    ],
    "questions": [],
    "dimensions": [],
    "technical_context": {{
        "indicator": "",
        "periods": [],
        "question": ""
    }},
    "time_horizon": "",
    "trading_style": "",
    "data_requirements": [],
    "constraints": []
}}


==================================================
十五、当前用户问题
==================================================

用户输入：

{text}
"""

    # ==========================================================
    # 调用 LLM
    # ==========================================================

    result = llm.invoke(prompt)

    content = result.content

    if not content:
        raise ValueError("Intent LLM 没有返回内容")

    # ==========================================================
    # 清理可能存在的 Markdown JSON 包裹
    # ==========================================================

    content = content.strip()

    if content.startswith("```json"):
        content = content[7:]

    elif content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    # ==========================================================
    # JSON 解析
    # ==========================================================

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Intent LLM 返回的不是合法 JSON: {e}\n"
            f"原始返回内容:\n{content}"
        )

    # ==========================================================
    # 基础结构保护
    # ==========================================================

    if not isinstance(data, dict):
        raise ValueError("Intent LLM 返回结果必须是 JSON Object")

    if "targets" not in data or data["targets"] is None:
        data["targets"] = []

    if "questions" not in data or data["questions"] is None:
        data["questions"] = []

    if "dimensions" not in data or data["dimensions"] is None:
        data["dimensions"] = []

    if "data_requirements" not in data or data["data_requirements"] is None:
        data["data_requirements"] = []

    if "constraints" not in data or data["constraints"] is None:
        data["constraints"] = []

    if "technical_context" not in data or data["technical_context"] is None:
        data["technical_context"] = {
            "indicator": "",
            "periods": [],
            "question": "",
        }

    # ==========================================================
    # Intent Validator
    #
    # 这里主要负责：
    #   - 检查 targets 是否真的来自用户输入
    #   - 清理明显的错误目标
    # ==========================================================

    data = validate_targets(data, text)

    # ==========================================================
    # 最重要的程序级安全规则
    #
    # Intent Agent 永远不能决定股票代码。
    #
    # 即使 LLM 返回：
    #
    # {
    #     "name": "宁德时代",
    #     "type": "stock",
    #     "code": "300750"
    # }
    #
    # 到这里也必须强制清空。
    #
    # 后续由：
    #
    # LLM Entity Extraction
    #          ↓
    # Entity Resolver
    #          ↓
    # Market Database / Real Market Source
    #
    # 来确认真实 code / market。
    # ==========================================================

    for target in data.get("targets", []):
        if not isinstance(target, dict):
            continue

        if target.get("type") == "stock":
            target["code"] = None

    # ==========================================================
    # 去重 targets
    #
    # 防止 LLM 重复返回同一个研究对象。
    # ==========================================================

    unique_targets = []
    seen_targets = set()

    for target in data.get("targets", []):
        if not isinstance(target, dict):
            continue

        name = str(target.get("name", "")).strip()
        entity_type = str(target.get("type", "")).strip()

        if not name or not entity_type:
            continue

        key = (name, entity_type)

        if key in seen_targets:
            continue

        seen_targets.add(key)
        unique_targets.append(target)

    data["targets"] = unique_targets

    # ==========================================================
    # data_requirements 去重
    # ==========================================================

    requirements = data.get("data_requirements", [])

    if isinstance(requirements, list):
        unique_requirements = []

        for requirement in requirements:
            requirement = str(requirement).strip()

            if not requirement:
                continue

            if requirement not in unique_requirements:
                unique_requirements.append(requirement)

        data["data_requirements"] = unique_requirements

    # ==========================================================
    # 最终调试输出
    # ==========================================================

    print("\n========== AFTER VALIDATION ==========")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    # ==========================================================
    # 转换成 ResearchIntent
    # ==========================================================

    try:
        intent_result = ResearchIntent(**data)
    except Exception as e:
        raise ValueError(
            f"ResearchIntent 数据结构校验失败: {e}\n"
            f"最终数据:\n"
            f"{json.dumps(data, ensure_ascii=False, indent=2)}"
        )

    return intent_result