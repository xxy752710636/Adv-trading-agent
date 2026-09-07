from app.planner.planner import ResearchPlanner


planner = ResearchPlanner()


def planner_agent(state):
    print("\n")
    print("=" * 60)
    print("              PLANNER AGENT")
    print("=" * 60)

    intent = state.get("intent")
    resolved_entities = state.get("resolved_entities", [])

    if intent is None:
        raise ValueError("Planner Agent 缺少 intent")

    if not resolved_entities:
        raise ValueError(
            "Planner Agent 没有收到 resolved_entities，"
            "禁止继续生成研究计划"
        )

    print("\n========== RESOLVED ENTITIES ==========")

    for entity in resolved_entities:
        print(
            f"name={entity.name} | "
            f"type={entity.type} | "
            f"code={entity.code} | "
            f"market={entity.market}"
        )

    plan = planner.plan(intent)

    # 真实实体写入 ResearchPlan
    plan.resolved_entities = resolved_entities

    state["plan"] = plan

    print("\n========== RESEARCH PLAN ==========")

    print(f"Goal: {plan.goal}")
    print(f"Target: {plan.target_name}")
    print(f"Target Type: {plan.target_type}")

    print("\nResolved Entities:")

    for entity in plan.resolved_entities:
        print(
            f"{entity.name} | "
            f"{entity.type} | "
            f"{entity.code} | "
            f"{entity.market}"
        )

    print("\nSteps:")

    for step in plan.steps:
        print(
            f"{step.id} | "
            f"type={step.type} | "
            f"requirement={step.data_requirement} | "
            f"dependencies={step.dependencies}"
        )

    return state