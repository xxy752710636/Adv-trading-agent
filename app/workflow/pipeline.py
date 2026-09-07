from app.intent.llm_classifier import llm_classify
from app.entity.resolver import EntityResolver
from app.planner.planner import ResearchPlanner
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry
from app.workflow.context import ResearchContext
from app.workflow.executor import ResearchExecutor


class ResearchPipeline:
    """
    Research Pipeline

    负责串联整个研究流程：

        User Input
            ↓
        Intent Agent
            ↓
        Entity Resolver
            ↓
        Research Planner
            ↓
        Research Executor
            ↓
        Research Context

    Pipeline 负责流程编排，
    ResearchExecutor 负责具体研究步骤的执行。
    """

    def __init__(self, registry: ToolRegistry):

        self.registry = registry

        # 单个 Tool 执行器
        self.tool_executor = ToolExecutor(
            registry
        )

        # 整体 Research Plan 执行器
        self.research_executor = ResearchExecutor(
            tool_executor=self.tool_executor
        )

        # 实体解析器
        self.entity_resolver = EntityResolver()

        # Research Planner
        self.planner = ResearchPlanner()

    def run(
        self,
        user_input: str
    ) -> ResearchContext:

        # ========================================
        # 初始化 Research Context
        # ========================================

        context = ResearchContext(
            user_input=user_input
        )

        # ========================================
        # STEP 1
        # Intent Agent
        # ========================================

        print("\n")
        print("=" * 60)
        print("STEP 1: INTENT")
        print("=" * 60)

        intent = llm_classify(
            user_input
        )

        context.intent = intent

        # ========================================
        # STEP 2
        # Entity Resolution
        # ========================================

        print("\n")
        print("=" * 60)
        print("STEP 2: ENTITY RESOLUTION")
        print("=" * 60)

        for target in intent.targets:

            entity = self.entity_resolver.resolve(
                name=target.name,
                entity_type=target.type
            )

            if entity is None:

                error = (
                    f"无法解析实体: "
                    f"{target.name}"
                )

                context.errors.append(
                    error
                )

                print(error)

                continue

            context.entities.append(
                entity
            )

            print(
                f"实体解析成功: "
                f"{entity.name} "
                f"{entity.code} "
                f"{entity.market}"
            )

        # ========================================
        # STEP 3
        # Research Planner
        # ========================================

        print("\n")
        print("=" * 60)
        print("STEP 3: RESEARCH PLANNER")
        print("=" * 60)

        plan = self.planner.plan(
            intent
        )

        context.plan = plan

        print(
            plan.model_dump_json(
                indent=2
            )
        )

        # ========================================
        # STEP 4
        # Research Executor
        # ========================================

        print("\n")
        print("=" * 60)
        print("STEP 4: RESEARCH EXECUTION")
        print("=" * 60)

        try:

            tool_results = (
                self.research_executor.execute(
                    plan=plan,
                    context=context
                )
            )

            context.tool_results = (
                tool_results
            )

        except Exception as e:

            error = (
                "Research Execution "
                f"执行失败: {str(e)}"
            )

            context.errors.append(
                error
            )

            print(error)

        # ========================================
        # 返回完整 Research Context
        # ========================================

        return context