from app.intent.schema import ResearchIntent
from app.planner.schema import ResearchPlan, ResearchStep


class ResearchPlanner:
    """
    Research Planner

    负责把 ResearchIntent 转换成 ResearchPlan。

    当前版本：
    使用确定性规则生成研究计划。

    注意：
    Planner 不直接调用 Tool。
    Planner 只决定“研究什么、先后关系是什么”。
    """

    DATA_REQUIREMENT_MAP = {

        # =========================
        # 行业
        # =========================

        "sector_market": {
            "type": "data",
            "description": "获取行业/板块近期市场表现",
        },

        "sector_capital_flow": {
            "type": "data",
            "description": "获取行业/板块资金流向",
        },

        "sector_fundamental": {
            "type": "data",
            "description": "获取行业基本面数据",
        },

        "sector_valuation": {
            "type": "data",
            "description": "获取行业估值及估值分位",
        },

        # =========================
        # 主题
        # =========================

        "theme_market": {
            "type": "data",
            "description": "获取主题近期市场表现",
        },

        "theme_capital_flow": {
            "type": "data",
            "description": "获取主题资金流向",
        },

        "theme_leaders": {
            "type": "data",
            "description": "获取主题相关核心个股及市场表现",
        },

        # =========================
        # 股票
        # =========================

        "stock_market": {
            "type": "data",
            "description": "获取股票近期市场表现",
        },

        "stock_kline": {
            "type": "data",
            "description": "获取股票近期行情及K线数据",
        },

        "stock_fundamental": {
            "type": "data",
            "description": "获取股票基本面数据",
        },

        "stock_valuation": {
            "type": "data",
            "description": "获取股票估值数据",
        },

        # =========================
        # 技术分析
        # =========================

        "technical_indicators": {
            "type": "analysis",
            "description": "根据行情数据计算技术指标",
        },

        # =========================
        # 市场
        # =========================

        "market_index": {
            "type": "data",
            "description": "获取主要市场指数行情",
        },

        "market_sentiment": {
            "type": "data",
            "description": "获取当前市场情绪及风险偏好",
        },

        "market_capital_flow": {
            "type": "data",
            "description": "获取市场整体资金流向",
        },

        # =========================
        # 新闻
        # =========================

        "industry_news": {
            "type": "data",
            "description": "获取行业相关新闻、政策及产业信息",
        },

        "company_news": {
            "type": "data",
            "description": "获取公司相关新闻及公告信息",
        },

        "policy_news": {
            "type": "data",
            "description": "获取相关政策及监管信息",
        },

        # =========================
        # 龙头
        # =========================

        "leader_stocks": {
            "type": "data",
            "description": "获取相关板块核心龙头股票",
        },

        # =========================
        # 估值
        # =========================

        "valuation_data": {
            "type": "data",
            "description": "获取相关标的估值数据",
        },
    }

    def plan(self, intent: ResearchIntent) -> ResearchPlan:

        steps = []

        # ==================================================
        # 第一阶段：数据获取 / 基础分析
        # ==================================================

        for index, requirement in enumerate(
            intent.data_requirements,
            start=1
        ):

            config = self.DATA_REQUIREMENT_MAP.get(requirement)

            if not config:
                print(
                    f"[ResearchPlanner] "
                    f"未知的数据需求: {requirement}"
                )
                continue

            dependencies = []

            # ----------------------------------------------
            # 技术指标依赖 K 线数据
            # ----------------------------------------------

            if requirement == "technical_indicators":

                kline_step = self._find_step_by_requirement(
                    steps,
                    "stock_kline"
                )

                if kline_step:
                    dependencies.append(kline_step.id)

            step = ResearchStep(
                id=f"step_{index}",
                type=config["type"],
                data_requirement=requirement,
                description=config["description"],
                dependencies=dependencies,
            )

            steps.append(step)

        # ==================================================
        # 第二阶段：综合研究
        # ==================================================

        if steps:

            dependency_ids = [
                step.id
                for step in steps
            ]

            synthesis_step = ResearchStep(
                id=f"step_{len(steps) + 1}",
                type="synthesis",
                data_requirement="research_synthesis",
                description="综合所有研究数据与分析结果",
                dependencies=dependency_ids,
            )

            steps.append(synthesis_step)

        # ==================================================
        # 创建 ResearchPlan
        # ==================================================

        return ResearchPlan(
            goal=intent.goal,

            target_name=(
                intent.targets[0].name
                if intent.targets
                else ""
            ),

            target_type=(
                intent.targets[0].type
                if intent.targets
                else ""
            ),

            steps=steps,

            reasoning=(
                "根据 ResearchIntent 中的数据需求，"
                "通过确定性规则生成研究步骤，并建立步骤之间的依赖关系。"
            ),
        )

    @staticmethod
    def _find_step_by_requirement(
        steps,
        requirement: str
    ):
        """
        根据 data_requirement 查找已经生成的 Step。
        """

        for step in steps:

            if step.data_requirement == requirement:
                return step

        return None