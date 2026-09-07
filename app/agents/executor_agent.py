from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry
from app.tools.technical_indicators_tool import TechnicalIndicatorsTool

from app.tools.stock_kline_tool import (
    StockKlineTool,
)

from app.tools.stock_market_tool import (
    StockMarketTool,
)

from app.workflow.executor import (
    ResearchExecutor,
)


def build_tool_registry() -> ToolRegistry:

    registry = ToolRegistry()

    registry.register(
        "stock_market",
        StockMarketTool(),
    )

    registry.register(
        "stock_kline",
        StockKlineTool(),
    )

    registry.register(
        "technical_indicators",
        TechnicalIndicatorsTool(),
    )

    return registry


def _summarize_tool_result(
    step_id: str,
    result,
) -> str:
    """
    终端日志摘要。

    注意：
    - 这里只负责打印摘要
    - 不修改 tool_results
    - 不删除完整 K 线
    """

    if not isinstance(result, dict):
        return f"type={type(result).__name__}"

    status = result.get(
        "status",
        "unknown",
    )

    data = result.get("data")

    # ----------------------------------------
    # 非成功结果
    # ----------------------------------------

    if status != "success":

        if status == "completed":

            report = result.get("report")

            if isinstance(report, dict):

                question = report.get(
                    "question",
                    "",
                )

                conclusion = report.get(
                    "conclusion",
                    "",
                )

                confidence = report.get(
                    "confidence",
                    "",
                )

                summary_parts = [
                    "status=completed",
                    "report=generated",
                ]

                if question:
                    summary_parts.append(
                        f"question={question}"
                    )

                if conclusion:
                    summary_parts.append(
                        f"conclusion={conclusion}"
                    )

                if confidence != "":
                    summary_parts.append(
                        f"confidence={confidence}"
                    )

                return " | ".join(
                    summary_parts
                )

            return "status=completed | report=generated"

        return f"status={status}"

    # ----------------------------------------
    # 没有 data
    # ----------------------------------------

    if not isinstance(data, dict):

        return (
            f"status={status} "
            f"| data_type={type(data).__name__}"
        )

    summary_parts = [
        f"status={status}"
    ]

    # ----------------------------------------
    # K线数据
    # ----------------------------------------

    bars = data.get("bars")

    if isinstance(bars, list):

        summary_parts.append(
            f"bars={len(bars)}"
        )

        if bars:

            latest_bar = bars[-1]

            if isinstance(
                latest_bar,
                dict,
            ):

                latest_date = latest_bar.get(
                    "date"
                )

                latest_close = latest_bar.get(
                    "close"
                )

                if latest_date:
                    summary_parts.append(
                        f"latest_date={latest_date}"
                    )

                if latest_close is not None:
                    summary_parts.append(
                        f"latest_close={latest_close}"
                    )

    # ----------------------------------------
    # K线 metadata
    # ----------------------------------------

    meta = data.get("meta")

    if isinstance(meta, dict):

        source = meta.get(
            "source"
        )

        if source:
            summary_parts.append(
                f"source={source}"
            )

        data_timestamp = meta.get(
            "data_timestamp"
        )

        if data_timestamp:
            summary_parts.append(
                f"data_timestamp={data_timestamp}"
            )

        data_quality = meta.get(
            "data_quality"
        )

        if data_quality:
            summary_parts.append(
                f"quality={data_quality}"
            )

    # ----------------------------------------
    # 股票实时数据
    # ----------------------------------------

    if "price" in data:

        summary_parts.append(
            f"price={data.get('price')}"
        )

    if "pct_change" in data:

        summary_parts.append(
            f"pct_change={data.get('pct_change')}"
        )

    # ----------------------------------------
    # 技术指标
    # ----------------------------------------

    if "moving_averages" in data:

        moving_averages = data.get(
            "moving_averages"
        )

        if isinstance(
            moving_averages,
            list,
        ):

            periods = []

            for item in moving_averages:

                if isinstance(
                    item,
                    dict,
                ):

                    period = item.get(
                        "period"
                    )

                    if period is not None:

                        periods.append(
                            str(period)
                        )

            if periods:

                summary_parts.append(
                    f"MA={','.join(periods)}"
                )

    if "rsi_14" in data:

        summary_parts.append(
            "RSI14=computed"
        )

    if "macd_dif" in data:

        summary_parts.append(
            "MACD=computed"
        )

    if "trend" in data:

        summary_parts.append(
            f"trend={data.get('trend')}"
        )

    return " | ".join(
        summary_parts
    )


def executor_agent(state):

    print("\n")
    print("=" * 60)
    print("              RESEARCH EXECUTOR")
    print("=" * 60)

    plan = state.get("plan")

    if plan is None:

        raise ValueError(
            "Executor Agent 缺少 ResearchPlan"
        )

    resolved_entities = state.get(
        "resolved_entities",
        [],
    )

    if not resolved_entities:

        raise ValueError(
            "Executor Agent 缺少 resolved_entities"
        )

    registry = build_tool_registry()

    print(
        "\n========== REGISTERED TOOLS =========="
    )

    for tool_name in registry.list_tools():

        print(
            f"- {tool_name}"
        )

    tool_executor = ToolExecutor(
        registry=registry
    )

    research_executor = ResearchExecutor(
        tool_executor=tool_executor
    )

    tool_results = (
        research_executor.execute(
            plan=plan,
            context=state,
        )
    )

    state["tool_results"] = tool_results

    # ========================================
    # TOOL RESULTS SUMMARY
    #
    # 只打印摘要
    # 完整结果仍然保存在 state["tool_results"]
    # ========================================

    print(
        "\n========== TOOL RESULTS SUMMARY =========="
    )

    for step_id, result in tool_results.items():

        print(
            f"\n[{step_id}]"
        )

        print(
            _summarize_tool_result(
                step_id=step_id,
                result=result,
            )
        )

    return state