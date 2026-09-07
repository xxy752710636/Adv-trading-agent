from app.workflow.graph import create_graph


graph = create_graph()


state = {
    "user_input": "宁德时代5日线是否拐头"
}


result = graph.invoke(state)


print("\n")
print("=" * 60)
print("              FINAL RESULT")
print("=" * 60)


response = result.get(
    "response"
)


if response:

    print(response)

else:

    print(
        "Agent 没有生成最终 response"
    )