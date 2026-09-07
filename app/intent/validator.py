def validate_targets(data: dict, user_text: str) -> dict:
    """
    校验 LLM 返回的 targets。

    原则：
    1. target 必须真实出现在用户输入中
    2. 防止 Prompt 中的示例实体污染结果
    3. 不修改 LLM 的其他字段
    """

    valid_targets = []

    for target in data.get("targets", []):

        name = target.get("name", "")

        if not name:
            continue

        # Target 必须出现在用户原始输入中
        if name not in user_text:
            print(
                f"[Target Validator] 移除未出现在用户输入中的目标: {name}"
            )
            continue

        valid_targets.append(target)

    data["targets"] = valid_targets

    return data