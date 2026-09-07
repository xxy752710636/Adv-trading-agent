def report_agent(state):

    print("\n")
    print("=" * 60)
    print("              REPORT AGENT")
    print("=" * 60)

    tool_results = state.get(
        "tool_results",
        {},
    )

    if not tool_results:
        raise ValueError(
            "Report Agent 缺少 tool_results"
        )

    print(
        "\n========== REPORT INPUT =========="
    )

    # ==========================================================
    # 只打印 Tool Result 摘要
    # 不打印完整 K 线 / 技术指标 / 报告内容
    # ==========================================================

    for step_id, result in tool_results.items():

        print(
            f"\n[{step_id}]"
        )

        print(
            _summarize_tool_result(result)
        )

    # ==========================================================
    # 获取 ResearchExecutor 生成的 ResearchReport
    # ==========================================================

    report = state.get(
        "report"
    )

    if report:

        response = _build_response(
            report
        )

        state["response"] = response

        print(
            "\n========== FINAL RESPONSE =========="
        )

        print(response)

        return state

    # ==========================================================
    # 如果 state 中还没有 report
    # 则从 synthesis step 中寻找
    # ==========================================================

    for step_id, result in tool_results.items():

        if (
            isinstance(result, dict)
            and result.get("status")
            == "completed"
            and result.get("report")
        ):

            report = result["report"]

            state["report"] = report

            response = _build_response(
                report
            )

            state["response"] = response

            print(
                "\n========== FINAL RESPONSE =========="
            )

            print(response)

            return state

    raise ValueError(
        "ResearchExecutor 没有生成 ResearchReport"
    )


# ==============================================================
# ResearchReport → 最终用户回答
# ==============================================================

def _build_response(report):
    """
    将 ResearchReport 转换成最终用户看到的 response。

    核心原则：

    1. 不打印整个 report dict
    2. 优先使用 conclusion
    3. 保留必要的证据
    4. 保留风险和不确定性
    5. 不重新进行市场分析
    6. 不生成 ResearchReport 中不存在的新数据
    """

    # ----------------------------------------------------------
    # 非 dict
    # ----------------------------------------------------------

    if not isinstance(report, dict):

        return str(report)

    sections = []

    # ----------------------------------------------------------
    # Question
    # ----------------------------------------------------------

    question = report.get(
        "question"
    )

    if question:

        sections.append(
            f"问题：{question}"
        )

    # ----------------------------------------------------------
    # Conclusion
    # ----------------------------------------------------------

    conclusion = report.get(
        "conclusion"
    )

    if conclusion:

        sections.append(
            f"结论：{conclusion}"
        )

    # ----------------------------------------------------------
    # Evidence
    # ----------------------------------------------------------

    evidence = report.get(
        "evidence",
        []
    )

    if isinstance(evidence, list) and evidence:

        evidence_lines = []

        for item in evidence:

            if not isinstance(item, dict):
                continue

            statement = item.get(
                "statement"
            )

            source_step = item.get(
                "source_step"
            )

            if statement and source_step:

                evidence_lines.append(
                    f"- {statement} "
                    f"（数据来源：{source_step}）"
                )

            elif statement:

                evidence_lines.append(
                    f"- {statement}"
                )

        if evidence_lines:

            sections.append(
                "依据：\n"
                + "\n".join(evidence_lines)
            )

    # ----------------------------------------------------------
    # Risks
    # ----------------------------------------------------------

    risks = report.get(
        "risks",
        []
    )

    if isinstance(risks, list) and risks:

        risk_lines = []

        for item in risks:

            if item:
                risk_lines.append(
                    f"- {item}"
                )

        if risk_lines:

            sections.append(
                "风险：\n"
                + "\n".join(risk_lines)
            )

    # ----------------------------------------------------------
    # Uncertainties
    # ----------------------------------------------------------

    uncertainties = report.get(
        "uncertainties",
        []
    )

    if (
        isinstance(uncertainties, list)
        and uncertainties
    ):

        uncertainty_lines = []

        for item in uncertainties:

            if item:
                uncertainty_lines.append(
                    f"- {item}"
                )

        if uncertainty_lines:

            sections.append(
                "不确定性：\n"
                + "\n".join(
                    uncertainty_lines
                )
            )

    # ----------------------------------------------------------
    # Confidence
    # ----------------------------------------------------------

    confidence = report.get(
        "confidence"
    )

    if confidence is not None:

        sections.append(
            f"数据支持度：{confidence}"
        )

    # ----------------------------------------------------------
    # 如果没有任何可用字段
    # ----------------------------------------------------------

    if not sections:

        conclusion = report.get(
            "conclusion"
        )

        if conclusion:
            return str(conclusion)

        return "ResearchReport 未包含可展示的结果。"

    return "\n\n".join(
        sections
    )


# ==============================================================
# Tool Result 日志摘要
# ==============================================================

def _summarize_tool_result(result):
    """
    只用于终端日志。

    不修改、不删除真实 Tool Result。
    """

    if not isinstance(result, dict):

        return (
            f"type={type(result).__name__}"
        )

    status = result.get(
        "status",
        "unknown",
    )

    # ==========================================================
    # synthesis / report
    # ==========================================================

    if result.get("report"):

        return (
            f"status={status} | "
            f"report=generated"
        )

    data = result.get("data")

    if not isinstance(data, dict):

        return (
            f"status={status}"
        )

    summary = [
        f"status={status}"
    ]

    # ==========================================================
    # K线
    # ==========================================================

    bars = data.get("bars")

    if isinstance(bars, list):

        summary.append(
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

                if latest_date:

                    summary.append(
                        f"latest_date={latest_date}"
                    )

    # ==========================================================
    # 数据源
    # ==========================================================

    meta = data.get("meta")

    if isinstance(meta, dict):

        source = meta.get(
            "source"
        )

        if source:

            summary.append(
                f"source={source}"
            )

        data_timestamp = meta.get(
            "data_timestamp"
        )

        if data_timestamp:

            summary.append(
                f"data_timestamp={data_timestamp}"
            )

    # ==========================================================
    # 技术指标
    # ==========================================================

    if "moving_averages" in data:

        summary.append(
            "indicators=computed"
        )

    elif (
        "rsi_14" in data
        or "macd_dif" in data
    ):

        summary.append(
            "indicators=computed"
        )

    # ==========================================================
    # 实时行情
    # ==========================================================

    if "price" in data:

        summary.append(
            f"price={data.get('price')}"
        )

    if "pct_change" in data:

        summary.append(
            f"pct_change={data.get('pct_change')}"
        )

    return " | ".join(summary)