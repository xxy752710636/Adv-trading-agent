from typing import Any, Dict

from app.tools.registry import ToolRegistry


class ToolExecutor:
    """
    Tool Executor

    负责：
    1. 根据 data_requirement 找 Tool
    2. 给 Tool 传递参数
    3. 执行 Tool
    4. 返回完整结果

    注意：
    - 内部始终保留完整 Tool Result
    - 终端只输出摘要，避免打印大量 K 线数据
    """

    def __init__(
        self,
        registry: ToolRegistry
    ):
        self.registry = registry

    def execute(
        self,
        requirement: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:

        print("\n========== TOOL EXECUTION ==========")
        print(f"Requirement: {requirement}")

        # 只打印关键参数，不打印可能很大的数据字段
        safe_params = self._summarize_params(params)
        print(f"Params: {safe_params}")

        tool = self.registry.get(requirement)

        print(f"Tool: {tool.name}")

        result = tool.execute(params)

        # 只打印结果摘要
        print("\n========== TOOL RESULT ==========")
        print(self._summarize_result(requirement, result))

        # 注意：
        # 这里仍然返回完整 result。
        # 后续 technical_indicators / synthesizer 仍然可以拿到完整 K 线。
        return result

    @staticmethod
    def _summarize_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        压缩终端中的参数输出。

        特别处理：
        - bars
        - 大列表
        - 大字典

        避免把完整 K 线打印到终端。
        """

        summary = {}

        for key, value in params.items():

            # K线数据：只显示数量
            if key == "bars" and isinstance(value, list):
                summary[key] = f"<{len(value)} bars>"
                continue

            # 普通列表：过长时只显示数量
            if isinstance(value, list):
                if len(value) > 10:
                    summary[key] = f"<list length={len(value)}>"
                else:
                    summary[key] = value
                continue

            # 普通字典：避免输出特别大的嵌套结构
            if isinstance(value, dict):
                if len(value) > 10:
                    summary[key] = f"<dict keys={len(value)}>"
                else:
                    summary[key] = value
                continue

            summary[key] = value

        return summary

    @staticmethod
    def _summarize_result(
        requirement: str,
        result: Any
    ) -> str:
        """
        将 Tool Result 压缩成终端摘要。

        注意：
        这里只影响 print，不影响真正返回的数据。
        """

        if not isinstance(result, dict):
            return f"type={type(result).__name__}"

        status = result.get("status", "unknown")
        data = result.get("data")

        # Tool 执行失败
        if status != "success":
            return f"status={status}"

        # 没有 data
        if not isinstance(data, dict):
            return f"status={status}"

        summary_parts = [
            f"status={status}"
        ]

        # -------------------------
        # K线数据
        # -------------------------

        bars = data.get("bars")

        if isinstance(bars, list):
            summary_parts.append(f"bars={len(bars)}")

            if bars:
                latest_bar = bars[-1]

                if isinstance(latest_bar, dict):
                    latest_date = latest_bar.get("date")

                    if latest_date:
                        summary_parts.append(
                            f"latest_date={latest_date}"
                        )

        # -------------------------
        # 数据源
        # -------------------------

        meta = data.get("meta")

        if isinstance(meta, dict):
            source = meta.get("source")

            if source:
                summary_parts.append(
                    f"source={source}"
                )

            data_timestamp = meta.get("data_timestamp")

            if data_timestamp:
                summary_parts.append(
                    f"data_timestamp={data_timestamp}"
                )

            data_quality = meta.get("data_quality")

            if data_quality:
                summary_parts.append(
                    f"quality={data_quality}"
                )

        # -------------------------
        # 股票实时行情
        # -------------------------

        if "price" in data:
            summary_parts.append(
                f"price={data.get('price')}"
            )

        if "pct_change" in data:
            summary_parts.append(
                f"pct_change={data.get('pct_change')}"
            )

        # -------------------------
        # 技术指标
        # -------------------------

        if "moving_averages" in data:
            moving_averages = data.get("moving_averages")

            if isinstance(moving_averages, list):
                periods = []

                for item in moving_averages:
                    if isinstance(item, dict):
                        period = item.get("period")

                        if period is not None:
                            periods.append(str(period))

                if periods:
                    summary_parts.append(
                        f"MA={','.join(periods)}"
                    )

        if "rsi_14" in data:
            summary_parts.append("RSI14=computed")

        if "macd_dif" in data:
            summary_parts.append("MACD=computed")

        if "trend" in data:
            summary_parts.append(
                f"trend={data.get('trend')}"
            )

        return " | ".join(summary_parts)