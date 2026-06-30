from typing import List

from App.Graph.State import AgentState


def route_after_planner(state: AgentState) -> str:
    if state.get("blocked"):
        return "blocked"
    if state.get("query_type") == "greeting":
        return "reasoning"
    return "workers"


def get_worker_routes(state: AgentState) -> List[str]:
    return state.get("routes", ["retriever"])
