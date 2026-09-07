from langgraph.graph import StateGraph

from app.workflow.state import AgentState


from app.agents.intent_agent import intent_agent

from app.agents.planner_agent import planner_agent

from app.agents.executor_agent import executor_agent

from app.agents.report_agent import report_agent

def create_graph():


    graph = StateGraph(AgentState)


    graph.add_node(
        "intent",
        intent_agent
    )


    graph.add_node(
        "planner",
        planner_agent
    )


    graph.add_node(
        "executor",
        executor_agent
    )



    graph.set_entry_point(
        "intent"
    )


    graph.add_edge(
        "intent",
        "planner"
    )


    graph.add_edge(
        "planner",
        "executor"
    )


    graph.set_finish_point(
        "executor"
    )

    graph.add_node(
        "report",
        report_agent
    )

    graph.add_edge(
        "executor",
        "report"
    )

    graph.set_finish_point(
        "report"
    )


    return graph.compile()
