"""
Evaluation prompts for LLM-as-a-Judge.

Each matrix is scored 1-10 (higher is better) except hallucination_risk
where 1 = no hallucination and 10 = severe hallucination.
"""

EVALUATION_SYSTEM_PROMPT = """
You are an expert AI evaluator for a hospital intelligence system (MediAssistAI).
You assess RAG/MCP/Multimodal answers strictly and objectively.
Return ONLY valid JSON. No markdown fences.
"""

EVALUATION_USER_PROMPT = """
You are an AI evaluator. Given the question, retrieved context, generated answer,
and optionally a golden (reference) answer, evaluate the generated answer using
the matrices below.

## Matrices

1. **faithfulness** (1-10, higher is better)
   Definition: The degree to which every claim in the answer is supported by the
   retrieved context. Penalize unsupported or contradictory statements.
   Formula: (supported_claims / total_claims) × 10

2. **grounding** (1-10, higher is better)
   Definition: How well specific facts, entities, numbers, and procedures in the
   answer trace back to the provided context (not general knowledge).
   Formula: (grounded_facts / total_facts) × 10

3. **relevance** (1-10, higher is better)
   Definition: How directly and completely the answer addresses the user question
   without unnecessary or off-topic content.
   Formula: relevance_to_query × 10 (subjective 0-1 scale)

4. **completeness** (1-10, higher is better)
   Definition: Whether the answer covers all key points expected for the question
   compared to the golden answer (if provided) or the context.
   Formula: (covered_key_points / expected_key_points) × 10

5. **hallucination_risk** (1-10, lower is better)
   Definition: Risk that the answer invents facts, patients, policies, or values
   not present in context. 1 = no hallucination, 10 = severe hallucination.
   Formula: (invented_or_unsupported_claims / total_claims) × 10

6. **golden_alignment** (1-10, higher is better) — only when golden answer provided
   Definition: Semantic and factual alignment between generated answer and the
   reference golden answer.
   Formula: factual_overlap_score × 10

---

**User Question:**
{query}

**Retrieved Context:**
{context}

**Generated Answer:**
{answer}

**Golden Reference Answer:**
{golden_answer}

---

Return JSON in this exact structure:
{{
  "faithfulness": {{"score": <1-10>, "reason": "<brief reason>"}},
  "grounding": {{"score": <1-10>, "reason": "<brief reason>"}},
  "relevance": {{"score": <1-10>, "reason": "<brief reason>"}},
  "completeness": {{"score": <1-10>, "reason": "<brief reason>"}},
  "hallucination_risk": {{"score": <1-10>, "reason": "<brief reason>"}},
  "golden_alignment": {{"score": <1-10 or null>, "reason": "<brief reason or null>"}}
}}
"""

# Legacy single-metric prompts (kept for backward compatibility)
FAITHFULNESS_PROMPT = EVALUATION_USER_PROMPT
RELEVANCY_PROMPT = EVALUATION_USER_PROMPT
RELEVANCE_PROMPT = EVALUATION_USER_PROMPT
HALLUCINATION_PROMPT = EVALUATION_USER_PROMPT
COMPLETENESS_PROMPT = EVALUATION_USER_PROMPT
