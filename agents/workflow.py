from langgraph.graph import StateGraph, END
from state import DataState
from agents.supervisor import supervisor_agent
from agents.presenter import presenter_agent
from agents.retriever import retriever_agent
from agents.sql_retriever import sql_retriever_agent
from agents.sql_executor import sql_executor_agent

def create_workflow():
    workflow = StateGraph(DataState)

    workflow.add_node("supervisor_agent", supervisor_agent)
    workflow.add_node("retriever_agent", retriever_agent)
    workflow.add_node("sql_retriever_agent", sql_retriever_agent)
    workflow.add_node("sql_executor_agent", sql_executor_agent)
    workflow.add_node("presenter_agent", presenter_agent)

    def route_supervisor(state: DataState):
        next_agent = state.get("next", "retriever_agent")
        return next_agent

    def route_sql_retriever(state: DataState):
        # After SQL retrieval, route to executor to run the query
        return "sql_executor_agent"

    # Supervisor routing
    workflow.add_conditional_edges(
        "supervisor_agent",
        route_supervisor,
        {
            "retriever_agent": "retriever_agent",
            "sql_retriever_agent": "sql_retriever_agent",
            "presenter_agent": "presenter_agent"
        }
    )

    # SQL retriever routes to SQL executor
    workflow.add_edge("sql_retriever_agent", "sql_executor_agent")
    
    # All processing agents route to presenter
    workflow.add_edge("retriever_agent", "presenter_agent")
    workflow.add_edge("sql_executor_agent", "presenter_agent")
    workflow.add_edge("presenter_agent", END)

    workflow.set_entry_point("supervisor_agent")
    return workflow.compile()