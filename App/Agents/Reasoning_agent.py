import os
from typing import Dict, List

from dotenv import load_dotenv

from App.Prompts.system_prompt import SYSTEM_PROMPT
from App.Prompts.reasoning_prompt import REASONING_PROMPT
from App.Logs import log_reasoning

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

# Groq llama-3.3-70b-versatile approximate pricing per 1M tokens (USD)
COST_PER_M_INPUT = 0.59
COST_PER_M_OUTPUT = 0.79


class ReasoningAgent:
    """Combine agent outputs and generate final answer with citations."""

    def __init__(self):
        self.client = None
        if GROQ_API_KEY:
            try:
                from groq import Groq
                self.client = Groq(api_key=GROQ_API_KEY)
            except Exception:
                self.client = None

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_cost = (prompt_tokens / 1_000_000) * COST_PER_M_INPUT
        output_cost = (completion_tokens / 1_000_000) * COST_PER_M_OUTPUT
        return round(input_cost + output_cost, 6)

    def _build_fallback(
        self,
        rag_context: str,
        mcp_result: str,
        multimodal_result: str,
        sources: List[str],
    ) -> str:
        parts = []
        if mcp_result and mcp_result.strip():
            parts.append(mcp_result.strip())
        if multimodal_result and multimodal_result.strip():
            parts.append(f"## Image Analysis\n\n{multimodal_result.strip()}")
        if rag_context and rag_context.strip():
            parts.append(f"## Document Context\n\n{rag_context.strip()}")

        if not parts:
            return (
                "I couldn't find relevant information in documents, "
                "images, or the hospital database. "
                "Please check that files are uploaded and the database is connected."
            )

        answer = "\n\n".join(parts)
        if sources:
            answer += f"\n\n**Sources:** {', '.join(sources)}"
        return answer

    def _direct_answer(self, state: Dict) -> str:
        """Return agent output directly when a single source has a clear result."""
        routes = state.get("routes", [])
        mcp_result = (state.get("mcp_result") or "").strip()
        rag_context = (state.get("rag_context") or "").strip()
        multimodal_result = (state.get("multimodal_result") or "").strip()
        sources = state.get("sources", [])

        if routes == ["mcp"] and mcp_result and "not found" not in mcp_result.lower():
            return mcp_result

        if routes == ["retriever"] and rag_context and not self.client:
            answer = rag_context
            if sources:
                answer += f"\n\n**Sources:** {', '.join(sources)}"
            return answer

        if routes == ["multimodal"] and multimodal_result:
            answer = multimodal_result
            if sources:
                answer += f"\n\n**Sources:** {', '.join(sources)}"
            return answer

        return ""

    def run(self, state: Dict) -> Dict:
        query = state.get("query", "")
        rag_context = state.get("rag_context", "")
        mcp_result = state.get("mcp_result", "")
        multimodal_result = state.get("multimodal_result", "")
        sources = state.get("sources", [])
        query_type = state.get("query_type", "")

        empty_tokens = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

        if query_type == "greeting":
            return {
                "answer": (
                    "Hello! I am MediAssistAI. "
                    "Ask me about hospital documents, patient records, or medical images."
                ),
                "sources": [],
                "tokens": empty_tokens,
                "cost_usd": 0.0,
            }

        direct = self._direct_answer(state)
        if direct:
            log_reasoning({"query": query, "answer": direct, "llm": False, "direct": True})
            return {
                "answer": direct,
                "sources": sources,
                "tokens": empty_tokens,
                "cost_usd": 0.0,
            }

        fallback = self._build_fallback(
            rag_context, mcp_result, multimodal_result, sources
        )

        if not self.client:
            log_reasoning({"query": query, "answer": fallback, "llm": False})
            return {
                "answer": fallback,
                "sources": sources,
                "tokens": empty_tokens,
                "cost_usd": 0.0,
            }

        prompt = REASONING_PROMPT.format(
            query=query,
            rag_context=rag_context or "No document context available.",
            mcp_result=mcp_result or "No database results available.",
            multimodal_result=multimodal_result or "No image analysis available.",
        )

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )

            answer = (response.choices[0].message.content or "").strip()
            usage = response.usage
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0
            cost = self._estimate_cost(prompt_tokens, completion_tokens)

            if not answer:
                answer = fallback

            if sources and "**Sources:**" not in answer:
                answer += f"\n\n**Sources:** {', '.join(sources)}"

            log_reasoning({
                "query": query,
                "answer": answer,
                "tokens": total_tokens,
                "cost_usd": cost,
            })

            return {
                "answer": answer,
                "sources": sources,
                "tokens": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                },
                "cost_usd": cost,
            }

        except Exception as e:
            answer = fallback
            if not answer.strip():
                answer = f"LLM error: {e}"
            else:
                answer += f"\n\n(LLM error: {e})"

            return {
                "answer": answer,
                "sources": sources,
                "tokens": empty_tokens,
                "cost_usd": 0.0,
            }
