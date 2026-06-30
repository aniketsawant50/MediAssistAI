from typing import Dict, List

from App.Agents.Planner_agent import PlannerAgent
from App.Agents.Retriever_agent import RetrieverAgent
from App.Agents.Mcp_agent import McpAgent
from App.Agents.Multi_modal_agent import MultiModalAgent
from App.Agents.Reasoning_agent import ReasoningAgent
from App.Evaluation.Evaluation_agent import EvaluationAgent
from App.Graph.State import AgentState
from App.Graph.Router import route_after_planner, get_worker_routes
from App.Logs import log_completed


def planner_node(state: AgentState) -> AgentState:
    plan = PlannerAgent().run(state["query"])
    return {
        **state,
        "query_type": plan.get("query_type", "document_rag"),
        "routes": plan.get("routes", ["retriever"]),
        "plan_reasoning": plan.get("reasoning", ""),
        "blocked": plan.get("blocked", False),
        "error": plan.get("error", ""),
        "agents_used": ["planner"],
    }


def workers_node(state: AgentState) -> AgentState:
    routes = get_worker_routes(state)
    agents_used = list(state.get("agents_used", []))
    sources: List[str] = []
    rag_context = ""
    mcp_result = ""
    multimodal_result = ""
    rag_chunks = []

    if "retriever" in routes:
        rag = RetrieverAgent().run(state["query"])
        rag_context = rag.get("context", "")
        sources.extend(rag.get("sources", []))
        agents_used.append("retriever")
        rag_chunks = rag.get("chunks", [])

    if "mcp" in routes:
        mcp = McpAgent().run(state["query"])
        mcp_result = mcp.get("content", "")
        if mcp.get("error"):
            mcp_result = f"Database error: {mcp['error']}"
        agents_used.append("mcp")

    if "multimodal" in routes:
        mm = MultiModalAgent().run(state["query"])
        multimodal_result = mm.get("context", "")
        sources.extend(mm.get("sources", []))
        agents_used.append("multimodal")

        if not multimodal_result and mm.get("available_images"):
            multimodal_result = (
                "Available indexed images: "
                + ", ".join(mm["available_images"])
            )

    return {
        **state,
        "rag_context": rag_context,
        "rag_chunks": rag_chunks,
        "mcp_result": mcp_result,
        "multimodal_result": multimodal_result,
        "sources": list(dict.fromkeys(sources)),
        "agents_used": agents_used,
    }


def reasoning_node(state: AgentState) -> AgentState:
    if state.get("blocked"):
        return {
            **state,
            "answer": state.get("error", "Query was blocked."),
            "agents_used": state.get("agents_used", []) + ["reasoning"],
            "tokens": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "cost_usd": 0.0,
        }

    result = ReasoningAgent().run(state)
    answer = result.get("answer") or ""

    return {
        **state,
        "answer": answer,
        "sources": result.get("sources", state.get("sources", [])),
        "tokens": result.get("tokens", {}),
        "cost_usd": result.get("cost_usd", 0.0),
        "agents_used": state.get("agents_used", []) + ["reasoning"],
    }


def evaluation_node(state: AgentState) -> AgentState:
    evaluation = EvaluationAgent().run(state)
    log_completed({
        "query": state.get("query"),
        "agents_used": state.get("agents_used", []),
        "routes": state.get("routes", []),
        "evaluation_grade": evaluation.get("grade"),
        "cost_usd": state.get("cost_usd", 0.0),
        "tokens": state.get("tokens", {}),
    })
    return {
        **state,
        "evaluation": evaluation,
        "agents_used": state.get("agents_used", []) + ["evaluation"],
    }


def blocked_node(state: AgentState) -> AgentState:
    return reasoning_node(state)


def build_graph():
    """Build LangGraph workflow; returns None if unavailable or incompatible."""
    try:
        from langgraph.graph import END, StateGraph

        workflow = StateGraph(AgentState)
        workflow.add_node("planner", planner_node)
        workflow.add_node("workers", workers_node)
        workflow.add_node("reasoning", reasoning_node)
        workflow.add_node("evaluation", evaluation_node)
        workflow.add_node("blocked", blocked_node)

        workflow.set_entry_point("planner")
        workflow.add_conditional_edges(
            "planner",
            route_after_planner,
            {
                "workers": "workers",
                "reasoning": "reasoning",
                "blocked": "blocked",
            },
        )
        workflow.add_edge("workers", "reasoning")
        workflow.add_edge("reasoning", "evaluation")
        workflow.add_edge("evaluation", END)
        workflow.add_edge("blocked", "evaluation")

        return workflow.compile()
    except Exception:
        return None


def _run_sequential(query: str) -> Dict:
    """Reliable sequential agent pipeline (no LangGraph dependency)."""
    state: AgentState = {"query": query}
    state = planner_node(state)
    route = route_after_planner(state)

    if route == "blocked":
        state = blocked_node(state)
    elif route == "reasoning":
        state = reasoning_node(state)
    else:
        state = workers_node(state)
        state = reasoning_node(state)

    state = evaluation_node(state)
    return dict(state)


def run_agent_pipeline(query: str) -> Dict:
    """Run the full agent pipeline; falls back to sequential on any graph error."""
    graph = build_graph()

    if graph is not None:
        try:
            result = graph.invoke({"query": query})
            answer = result.get("answer") if isinstance(result, dict) else None
            if answer:
                return dict(result)
        except Exception:
            pass

    return _run_sequential(query)
