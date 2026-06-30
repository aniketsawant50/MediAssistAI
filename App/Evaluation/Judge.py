import json
import os
import re
from typing import Dict, Optional

from dotenv import load_dotenv

from App.Evaluation.Prompts import (
    EVALUATION_SYSTEM_PROMPT,
    EVALUATION_USER_PROMPT,
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")


class Judge:
    """LLM-as-a-Judge: faithfulness, grounding, relevance, completeness, hallucination."""

    def __init__(self):
        self.client = None
        if GROQ_API_KEY:
            try:
                from groq import Groq
                self.client = Groq(api_key=GROQ_API_KEY)
            except Exception:
                self.client = None

    def _parse_json(self, text: str) -> Dict:
        text = text.strip()
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)

    def _extract_score(self, data: Dict, key: str) -> tuple:
        block = data.get(key, {})
        if isinstance(block, dict):
            score = block.get("score")
            reason = block.get("reason", "")
            if score is not None:
                return float(score), reason
        if isinstance(block, (int, float)):
            return float(block), ""
        return None, ""

    def _heuristic_score(
        self,
        query: str,
        answer: str,
        context: str,
        golden_answer: Optional[str] = None,
    ) -> Dict:
        has_answer = bool(answer.strip())
        context_words = set(context.lower().split()) if context else set()
        answer_words = set(answer.lower().split()) if answer else set()
        overlap = len(context_words & answer_words) / max(len(answer_words), 1)

        golden_overlap = 0.0
        if golden_answer:
            golden_words = set(golden_answer.lower().split())
            golden_overlap = len(golden_words & answer_words) / max(len(golden_words), 1)

        faithfulness = round(min(overlap * 10, 10), 1)
        grounding = faithfulness
        relevance = (
            8.0 if has_answer and any(
                w in answer.lower() for w in query.lower().split()[:4] if len(w) > 3
            ) else 5.0
        )
        completeness = (
            round(min(golden_overlap * 10, 10), 1) if golden_answer
            else (7.0 if len(answer) > 80 else 5.0)
        )
        hallucination_risk = round(max(1, 10 - faithfulness), 1)

        result = {
            "faithfulness": faithfulness,
            "grounding": grounding,
            "relevance": relevance,
            "relevancy": relevance,
            "completeness": completeness,
            "hallucination_risk": hallucination_risk,
            "hallucination": hallucination_risk,
            "method": "heuristic",
            "details": {
                "faithfulness": "Heuristic word overlap with context",
                "grounding": "Heuristic grounding via context overlap",
                "relevance": "Keyword overlap with query",
                "completeness": "Length / golden word overlap",
                "hallucination_risk": "Inverse of faithfulness",
            },
        }

        if golden_answer:
            result["golden_alignment"] = round(min(golden_overlap * 10, 10), 1)
            result["details"]["golden_alignment"] = "Word overlap with golden answer"

        return result

    def evaluate(
        self,
        query: str,
        answer: str,
        context: str,
        golden_answer: Optional[str] = None,
    ) -> Dict:
        if not self.client or not answer.strip():
            return self._heuristic_score(query, answer, context, golden_answer)

        prompt = EVALUATION_USER_PROMPT.format(
            query=query,
            context=context[:4000] or "No context provided.",
            answer=answer[:3000],
            golden_answer=golden_answer or "Not provided.",
        )

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                temperature=0,
                messages=[
                    {"role": "system", "content": EVALUATION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )

            raw = self._parse_json(response.choices[0].message.content)
            details = {}
            scores = {}

            for key in [
                "faithfulness", "grounding", "relevance",
                "completeness", "hallucination_risk", "golden_alignment",
            ]:
                score, reason = self._extract_score(raw, key)
                if score is not None:
                    scores[key] = score
                    details[key] = reason

            if "relevance" in scores:
                scores["relevancy"] = scores["relevance"]
            if "hallucination_risk" in scores:
                scores["hallucination"] = scores["hallucination_risk"]

            scores["details"] = details
            scores["method"] = "llm_judge"
            return scores

        except Exception as e:
            result = self._heuristic_score(query, answer, context, golden_answer)
            result["details"]["error"] = str(e)
            return result
