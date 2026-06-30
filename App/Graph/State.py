from typing import Any, Dict, List, TypedDict


class AgentState(TypedDict, total=False):
    query: str
    query_type: str
    routes: List[str]
    plan_reasoning: str
    blocked: bool
    error: str

    rag_context: str
    rag_chunks: List[Dict[str, Any]]
    mcp_result: str
    multimodal_result: str
    multimodal_sources: List[str]

    sources: List[str]
    agents_used: List[str]
    answer: str

    tokens: Dict[str, int]
    cost_usd: float
    evaluation: Dict[str, Any]
