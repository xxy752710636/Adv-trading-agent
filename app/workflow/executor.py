from typing import Any, Dict

from app.planner.schema import ResearchPlan
from app.tools.executor import ToolExecutor
from app.research.synthesizer import ResearchSynthesizer


class ResearchExecutor:
    """
    Research Execution Engine

    ResearchPlan
        ↓
    ResearchStep
        ↓
    Tool / Synthesizer
        ↓
    Result

    核心原则：

        Intent.targets
            ↓
        用户想研究什么

        resolved_entities
            ↓
        真实确认后的市场实体

        ResearchExecutor
            ↓
        只能使用 resolved_entities

    日志原则：

        完整数据保留在程序内部
        ↓
        日志只输出摘要
    """

    def __init__(
        self,
        tool_executor: ToolExecutor
    ):
        self.tool_executor = tool_executor
        self.synthesizer = ResearchSynthesizer()

    def execute(
        self,
        plan: ResearchPlan,
        context: Any
    ) -> Dict[str, Any]:

        results: Dict[str, Any] = {}

        pending_steps = list(plan.steps)

        print("\n")
        print("=" * 50)
        print("RESEARCH EXECUTOR")
        print("=" * 50)

        # ======================================================
        # LangGraph AgentState
        # ======================================================

        user_input = self._get_context_value(
            context,
            "user_input"
        )

        intent = self._get_context_value(
            context,
            "intent"
        )

        resolved_entities = self._get_context_value(
            context,
            "resolved_entities",
            default=[]
        )

        # ======================================================
        # 基础检查
        # ======================================================

        if not user_input:
            raise ValueError(
                "ResearchExecutor 缺少 user_input"
            )

        if intent is None:
            raise ValueError(
                "ResearchExecutor 缺少 intent"
            )

        if not resolved_entities:
            raise ValueError(
                "ResearchExecutor 缺少 resolved_entities"
            )

        print(
            f"[Context] entities={len(resolved_entities)}"
        )

        for entity in resolved_entities:
            print(
                f"[Entity] "
                f"{entity.name} | "
                f"{entity.type} | "
                f"{entity.code} | "
                f"{entity.market}"
            )

        # ======================================================
        # Research Step Execution Loop
        # ======================================================

        while pending_steps:

            progress = False

            for step in pending_steps[:]:

                # ==================================================
                # 检查依赖
                # ==================================================

                dependencies_ready = all(
                    dependency in results
                    for dependency in step.dependencies
                )

                if not dependencies_ready:
                    continue

                # ==================================================
                # 检查依赖是否执行成功
                # ==================================================

                failed_dependencies = []

                for dependency in step.dependencies:

                    dependency_result = results.get(
                        dependency
                    )

                    if not dependency_result:
                        continue

                    status = dependency_result.get(
                        "status"
                    )

                    if status not in {
                        "success",
                        "completed"
                    }:

                        if dependency not in failed_dependencies:
                            failed_dependencies.append(
                                dependency
                            )

                # ==================================================
                # 依赖失败
                # ==================================================

                if failed_dependencies:

                    error_message = (
                        f"步骤 {step.id} 的部分依赖执行失败: "
                        f"{failed_dependencies}"
                    )

                    print(
                        f"\n[Dependency] "
                        f"{error_message}"
                    )

                    # synthesis 允许使用成功的数据继续生成报告
                    if step.type == "synthesis":

                        print(
                            "[Synthesis] "
                            "部分数据失败，继续使用成功数据"
                        )

                    else:

                        results[step.id] = {
                            "status": "blocked",
                            "error": error_message,
                            "failed_dependencies": (
                                failed_dependencies
                            )
                        }

                        pending_steps.remove(step)
                        progress = True
                        continue

                # ==================================================
                # Synthesis
                # ==================================================

                if step.type == "synthesis":

                    print(
                        "\n[Synthesis] 开始"
                    )

                    try:

                        report = (
                            self.synthesizer.synthesize(
                                user_input=user_input,
                                intent=intent,
                                entities=resolved_entities,
                                plan=plan,
                                tool_results=results,
                            )
                        )

                        report_data = (
                            report.model_dump()
                            if hasattr(
                                report,
                                "model_dump"
                            )
                            else report
                        )

                        # ------------------------------------------
                        # LangGraph State
                        # ------------------------------------------

                        context["report"] = report_data

                        # ------------------------------------------
                        # Step Result
                        # ------------------------------------------

                        results[step.id] = {
                            "status": "completed",
                            "report": report_data
                        }

                        print(
                            "[Synthesis] 完成"
                        )

                    except Exception as e:

                        results[step.id] = {
                            "status": "failed",
                            "error": str(e)
                        }

                        print(
                            f"[Synthesis] 失败: {e}"
                        )

                    pending_steps.remove(step)

                    progress = True

                    continue

                # ==================================================
                # 普通 Tool
                # ==================================================

                try:

                    params = self._build_params(
                        step=step,
                        context=context,
                        results=results
                    )

                    result = (
                        self.tool_executor.execute(
                            requirement=(
                                step.data_requirement
                            ),
                            params=params
                        )
                    )

                    results[step.id] = result

                    # ----------------------------------------------
                    # 只打印摘要
                    # 不打印完整 Tool Result
                    # ----------------------------------------------

                    summary = self._result_summary(
                        requirement=step.data_requirement,
                        result=result
                    )

                    print(
                        f"[Tool] "
                        f"{step.id} | "
                        f"{step.data_requirement} | "
                        f"{result.get('status', 'unknown')}"
                        f"{summary}"
                    )

                except Exception as e:

                    results[step.id] = {
                        "status": "failed",
                        "error": str(e)
                    }

                    print(
                        f"[Tool] "
                        f"{step.id} | "
                        f"{step.data_requirement} | "
                        f"failed | "
                        f"{e}"
                    )

                pending_steps.remove(step)

                progress = True

            # ======================================================
            # 防止死循环
            # ======================================================

            if not progress:

                unresolved = [
                    step.id
                    for step in pending_steps
                ]

                raise RuntimeError(
                    "ResearchPlan 存在无法满足的依赖关系: "
                    f"{unresolved}"
                )

        return results

    # ==========================================================
    # Tool Result 日志摘要
    # ==========================================================

    @staticmethod
    def _result_summary(
        requirement: str,
        result: Dict[str, Any]
    ) -> str:
        """
        只生成日志摘要。

        注意：

        这里绝对不删除真实数据。
        只是避免 print 完整 K 线 / 财务数据 / 新闻内容。
        """

        if not isinstance(result, dict):
            return ""

        data = result.get("data")

        if not isinstance(data, dict):
            return ""

        # ------------------------------------------------------
        # K线
        # ------------------------------------------------------

        if requirement == "stock_kline":

            bars = data.get("bars", [])

            meta = data.get("meta", {})

            latest_date = ""

            if bars:
                latest_bar = bars[-1]

                if isinstance(latest_bar, dict):
                    latest_date = latest_bar.get(
                        "date",
                        ""
                    )

            source = meta.get(
                "source",
                ""
            )

            return (
                f" | bars={len(bars)}"
                f" | latest_date={latest_date}"
                f" | source={source}"
            )

        # ------------------------------------------------------
        # 技术指标
        # ------------------------------------------------------

        if requirement == "technical_indicators":

            return " | indicators=computed"

        # ------------------------------------------------------
        # 股票行情
        # ------------------------------------------------------

        if requirement == "stock_market":

            return (
                f" | code={data.get('code', '')}"
                f" | data_timestamp="
                f"{data.get('data_timestamp', '')}"
            )

        return ""

    # ==========================================================
    # Context 读取工具
    # ==========================================================

    @staticmethod
    def _get_context_value(
        context: Any,
        key: str,
        default=None
    ):
        """
        同时兼容：

            LangGraph AgentState(dict)

        以及未来：

            ResearchContext(object)
        """

        if isinstance(context, dict):
            return context.get(
                key,
                default
            )

        return getattr(
            context,
            key,
            default
        )

    # ==========================================================
    # Tool 参数构造
    # ==========================================================

    def _build_params(
        self,
        step,
        context,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:

        requirement = step.data_requirement

        # ======================================================
        # 股票行情
        # ======================================================

        if requirement == "stock_market":

            resolved_entities = self._get_context_value(
                context,
                "resolved_entities",
                default=[],
            )

            if not resolved_entities:
                raise ValueError(
                    "stock_market 缺少 resolved_entities"
                )

            stock_entities = [
                entity
                for entity in resolved_entities
                if entity.type == "stock"
            ]

            if not stock_entities:
                raise ValueError(
                    "stock_market 没有找到股票实体"
                )

            entity = stock_entities[0]

            if not entity.code:
                raise ValueError(
                    f"股票实体缺少真实代码: "
                    f"{entity.name}"
                )

            if not entity.market:
                raise ValueError(
                    f"股票实体缺少真实市场: "
                    f"{entity.name}"
                )

            return {
                "code": entity.code,
                "market": entity.market,
            }

        # ======================================================
        # 股票 K 线
        # ======================================================

        if requirement == "stock_kline":

            resolved_entities = self._get_context_value(
                context,
                "resolved_entities",
                default=[]
            )

            if not resolved_entities:
                raise ValueError(
                    "stock_kline 缺少 resolved_entities"
                )

            stock_entities = [
                entity
                for entity in resolved_entities
                if entity.type == "stock"
            ]

            if not stock_entities:
                raise ValueError(
                    "stock_kline 没有找到股票实体"
                )

            entity = stock_entities[0]

            if not entity.code:
                raise ValueError(
                    f"股票实体缺少真实代码: "
                    f"{entity.name}"
                )

            if not entity.market:
                raise ValueError(
                    f"股票实体缺少真实市场: "
                    f"{entity.name}"
                )

            return {
                "code": entity.code,
                "market": entity.market,
                "days": 60,
                "adjustment": "qfq"
            }

        # ======================================================
        # 技术指标
        # ======================================================

        if requirement == "technical_indicators":

            if not step.dependencies:
                raise ValueError(
                    "technical_indicators 缺少 K 线依赖"
                )

            kline_step_id = None
            kline_result = None

            # --------------------------------------------------
            # 从依赖中寻找真正的 K 线结果
            # --------------------------------------------------

            for dependency in step.dependencies:

                dependency_result = results.get(
                    dependency
                )

                if not dependency_result:
                    continue

                dependency_data = dependency_result.get(
                    "data"
                )

                if (
                    isinstance(dependency_data, dict)
                    and "bars" in dependency_data
                ):
                    kline_step_id = dependency
                    kline_result = dependency_result
                    break

            if not kline_result:
                raise ValueError(
                    "technical_indicators "
                    "找不到有效的 K 线依赖结果"
                )

            # --------------------------------------------------
            # 获取 K 线
            # --------------------------------------------------

            kline_data = kline_result.get(
                "data"
            )

            if not kline_data:
                raise ValueError(
                    "technical_indicators "
                    "的 K 线数据为空"
                )

            bars = kline_data.get(
                "bars"
            )

            if not bars:
                raise ValueError(
                    "technical_indicators "
                    "缺少 K 线 bars"
                )

            # --------------------------------------------------
            # 获取真实实体
            # --------------------------------------------------

            resolved_entities = self._get_context_value(
                context,
                "resolved_entities",
                default=[]
            )

            if not resolved_entities:
                raise ValueError(
                    "technical_indicators "
                    "缺少 resolved_entities"
                )

            stock_entities = [
                entity
                for entity in resolved_entities
                if entity.type == "stock"
            ]

            if not stock_entities:
                raise ValueError(
                    "technical_indicators "
                    "没有找到股票实体"
                )

            entity = stock_entities[0]

            if not entity.code:
                raise ValueError(
                    f"股票实体缺少真实代码: "
                    f"{entity.name}"
                )

            if not entity.market:
                raise ValueError(
                    f"股票实体缺少真实市场: "
                    f"{entity.name}"
                )

            # --------------------------------------------------
            # 注意：
            #
            # bars 是完整 K 线数据。
            # 这里不打印。
            # 直接传给 TechnicalIndicatorsTool。
            # --------------------------------------------------

            return {
                "bars": bars,
                "code": entity.code,
                "name": entity.name,
                "market": entity.market,
                "source_step": kline_step_id,
            }

        # ======================================================
        # 当前未实现的 Data Requirement
        # ======================================================

        raise ValueError(
            f"暂时不知道如何构造 "
            f"{requirement} 的参数"
        )