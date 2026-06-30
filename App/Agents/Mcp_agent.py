from typing import Dict

from App.MCP.query_router import ask_database
from App.Logs import log_retrieval


class McpAgent:
    """MCP tool execution — patient DB, prescriptions, labs, appointments, billing."""

    def run(self, query: str) -> Dict:
        try:
            result = ask_database(query)

            if isinstance(result, dict) and result.get("error"):
                return {"content": "", "error": result["error"]}

            content = result if isinstance(result, str) else str(result)

            log_retrieval({
                "agent": "mcp",
                "query": query,
                "has_result": bool(content.strip()),
            })

            return {"content": content, "error": None}

        except Exception as e:
            return {"content": "", "error": str(e)}
