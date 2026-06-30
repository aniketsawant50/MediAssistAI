import os
import re
import json
from typing import Dict, List

from dotenv import load_dotenv

from App.Prompts.planner_prompt import PLANNER_PROMPT
from App.Logs import log_planner

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above)\s+instructions",
    r"disregard\s+(your\s+)?(rules|instructions)",
    r"you\s+are\s+now\s+",
    r"system\s+prompt",
    r"jailbreak",
    r"<\s*script",
    r"drop\s+table",
    r"delete\s+from",
]

MCP_KEYWORDS = [
    "patient", "pc0", "prescription", "billing", "appointment",
    "admission record", "doctor", "department", "insurance",
    "lab report of", "history of", "show patient",
]

IMAGE_KEYWORDS = [
    ".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff",
    "image", "x-ray", "xray", "scan", "ocr", "prescription image",
    "lab report image", "uploaded image", "summarize", "caption",
]

DOC_KEYWORDS = [
    "sop", "admission process", "compliance", "policy", "procedure",
    "document", "hospital rule", "guideline", "uploaded pdf",
]


class PlannerAgent:
    """Query understanding, guardrails, and route decision."""

    def detect_injection(self, query: str) -> bool:
        q = query.lower()
        return any(re.search(p, q, re.IGNORECASE) for p in INJECTION_PATTERNS)

    def classify_heuristic(self, query: str) -> Dict:
        q = query.lower()
        routes: List[str] = []

        if any(kw in q for kw in MCP_KEYWORDS) or re.search(r"pc\d+[a-z]?", q, re.I):
            routes.append("mcp")

        if any(kw in q for kw in IMAGE_KEYWORDS):
            routes.append("multimodal")

        if any(kw in q for kw in DOC_KEYWORDS) or not routes:
            routes.append("retriever")

        # Admission/process questions should search documents
        if any(kw in q for kw in ["admission", "process", "procedure", "sop", "compliance"]):
            if "retriever" not in routes:
                routes.append("retriever")

        if "mcp" in routes and "retriever" not in routes:
            query_type = "medical_database"
        elif "multimodal" in routes and len(routes) == 1:
            query_type = "image_analysis"
        elif len(routes) > 1:
            query_type = "hybrid"
        else:
            query_type = "document_rag"

        greetings = ["hi", "hello", "hey", "good morning", "good evening"]
        if q.strip() in greetings:
            query_type = "greeting"
            routes = []

        return {
            "query_type": query_type,
            "routes": list(dict.fromkeys(routes)),
            "reasoning": f"Heuristic routing for {query_type}",
            "is_medical": query_type != "unsafe",
            "blocked": False,
        }

    def classify_with_llm(self, query: str) -> Dict:
        if not GROQ_API_KEY:
            return self.classify_heuristic(query)

        try:
            from groq import Groq

            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Return only valid JSON. No markdown."
                        ),
                    },
                    {
                        "role": "user",
                        "content": PLANNER_PROMPT.format(query=query),
                    },
                ],
            )
            text = response.choices[0].message.content.strip()
            text = text.removeprefix("```json").removesuffix("```").strip()
            plan = json.loads(text)
            plan.setdefault("routes", ["retriever"])
            plan.setdefault("blocked", False)
            return plan
        except Exception:
            return self.classify_heuristic(query)

    def run(self, query: str) -> Dict:
        if not query or not query.strip():
            result = {
                "query": query,
                "query_type": "unsafe",
                "routes": [],
                "reasoning": "Empty query",
                "is_medical": False,
                "blocked": True,
                "error": "Query cannot be empty.",
            }
            log_planner(result)
            return result

        if self.detect_injection(query):
            result = {
                "query": query,
                "query_type": "unsafe",
                "routes": [],
                "reasoning": "Prompt injection detected",
                "is_medical": False,
                "blocked": True,
                "error": "Query blocked for security reasons.",
            }
            log_planner(result)
            return result

        # Heuristic routing is more reliable for MCP/RAG/multimodal keywords
        plan = self.classify_heuristic(query)
        plan["query"] = query
        log_planner(plan)
        return plan
