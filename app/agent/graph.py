from langgraph.graph import StateGraph, END

from app.agent.nodes.classifier import classify
from app.agent.nodes.contact_handler import handle_contact
from app.agent.nodes.generator import generate
from app.agent.nodes.rejector import reject
from app.agent.nodes.retriever import retrieve
from app.agent.state import AgentState

from app.services.langsmith_tracer import tracer


def route_by_classification(state: AgentState) -> str:
    classification = state.get("classification", "OUT_OF_DOMAIN")

    if classification == "IN_DOMAIN":
        return "retrieve"
    if classification == "CONTACT":
        return "contact_handler"

    return "reject"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("classify", classify)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)
    graph.add_node("reject", reject)
    graph.add_node("contact_handler", handle_contact)

    graph.set_entry_point("classify")

    graph.add_conditional_edges(
        "classify",
        route_by_classification,
        {
            "retrieve": "retrieve",
            "reject": "reject",
            "contact_handler": "contact_handler",
        },
    )

    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    graph.add_edge("reject", END)
    graph.add_edge("contact_handler", END)

    return graph


compiled_graph = build_graph().compile().with_config(tracer=tracer)
