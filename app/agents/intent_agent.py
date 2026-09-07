from app.intent.llm_classifier import llm_classify
from app.intent.llm_entity import llm_extract_entities
from app.entity.resolver import EntityResolver


resolver = EntityResolver()


def intent_agent(state):

    user_input = state["user_input"]

    print("\n")
    print("=" * 60)
    print("              INTENT AGENT")
    print("=" * 60)

    # ========================================
    # Step 1
    # Intent Classification
    # ========================================

    intent = llm_classify(user_input)

    state["intent"] = intent

    # ========================================
    # Step 2
    # Entity Extraction
    # ========================================

    extracted_entities = llm_extract_entities(user_input)

    state["extracted_entities"] = extracted_entities

    print("\n========== EXTRACTED ENTITIES ==========")

    for entity in extracted_entities:

        print(
            f"name={entity.name} | "
            f"type={entity.type} | "
            f"confidence={entity.confidence}"
        )

    # ========================================
    # Step 3
    # Entity Resolution
    # ========================================

    resolved_entities = []

    errors = []

    print("\n========== ENTITY RESOLUTION ==========")

    for entity in extracted_entities:

        result = resolver.resolve(
            name=entity.name,
            entity_type=entity.type,
        )

        print(
            f"\n实体: {entity.name}"
        )

        print(
            f"状态: {result.status}"
        )

        print(
            f"消息: {result.message}"
        )

        # -----------------------------
        # RESOLVED
        # -----------------------------

        if result.status.value == "resolved":

            if result.entity:

                resolved_entities.append(
                    result.entity
                )

                print(
                    f"解析成功: "
                    f"{result.entity.name} | "
                    f"{result.entity.code} | "
                    f"{result.entity.market}"
                )

        # -----------------------------
        # AMBIGUOUS
        # -----------------------------

        elif result.status.value == "ambiguous":

            error_message = (
                f"实体存在多个候选，无法自动确定: "
                f"{entity.name}"
            )

            errors.append(error_message)

            print(
                f"解析歧义: {error_message}"
            )

        # -----------------------------
        # NOT FOUND
        # -----------------------------

        elif result.status.value == "not_found":

            error_message = (
                f"未找到真实市场实体: "
                f"{entity.name}"
            )

            errors.append(error_message)

            print(
                f"解析失败: {error_message}"
            )

        # -----------------------------
        # ERROR
        # -----------------------------

        else:

            error_message = (
                f"实体解析异常: "
                f"{entity.name} | "
                f"{result.message}"
            )

            errors.append(error_message)

            print(
                f"解析异常: {error_message}"
            )

    state["resolved_entities"] = resolved_entities

    # ========================================
    # Step 4
    # 保存错误
    # ========================================

    state["errors"] = errors

    print("\n========== RESOLVED ENTITIES ==========")

    for entity in resolved_entities:

        print(
            f"{entity.name} | "
            f"{entity.type} | "
            f"{entity.code} | "
            f"{entity.market}"
        )

    return state