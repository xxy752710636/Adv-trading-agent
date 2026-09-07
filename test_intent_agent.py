from app.agents.intent_agent import intent_agent


tests = [
    "看看宁德时代最近怎么样",
    "分析中际旭创和比亚迪",
    "剑桥科技5日线是否拐头",
]


for text in tests:

    print("\n")
    print("#" * 70)
    print("USER:", text)
    print("#" * 70)

    state = {
        "user_input": text
    }

    result = intent_agent(state)

    print("\n")
    print("========== FINAL STATE ==========")

    print("\nIntent:")
    print(result.get("intent"))

    print("\nExtracted Entities:")
    print(result.get("extracted_entities"))

    print("\nResolved Entities:")
    print(result.get("resolved_entities"))

    print("\nErrors:")
    print(result.get("errors"))