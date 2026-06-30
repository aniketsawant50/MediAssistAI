import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from App.Evaluation.Judge import Judge
from App.Evaluation.Metrics import aggregate_batch_results, compute_overall, grade_score
from App.Evaluation.golden_dataset import get_golden_item, load_golden_dataset
from App.Logs import log_evaluation

REPORT_DIR = Path("App/Logs/Evaluation")


class EvaluationAgent:
    """
    Testing & evaluation pipeline:
    User query -> retrieved context -> generated answer -> evaluation agent
    """

    def __init__(self):
        self.judge = Judge()

    def _build_context(self, state: Dict) -> str:
        return "\n\n".join(filter(None, [
            state.get("rag_context", ""),
            state.get("mcp_result", ""),
            state.get("multimodal_result", ""),
        ]))

    def _format_scores(self, scores: Dict, golden_answer: Optional[str] = None) -> Dict:
        overall = compute_overall(scores)
        grade = grade_score(overall)

        evaluation = {
            "faithfulness": scores.get("faithfulness", 0),
            "grounding": scores.get("grounding", scores.get("faithfulness", 0)),
            "relevance": scores.get("relevance", scores.get("relevancy", 0)),
            "relevancy": scores.get("relevance", scores.get("relevancy", 0)),
            "completeness": scores.get("completeness", 0),
            "hallucination_risk": scores.get(
                "hallucination_risk", scores.get("hallucination", 5)
            ),
            "hallucination": scores.get(
                "hallucination_risk", scores.get("hallucination", 5)
            ),
            "overall_score": overall,
            "grade": grade,
            "method": scores.get("method", "unknown"),
            "details": scores.get("details", {}),
        }

        if scores.get("golden_alignment") is not None:
            evaluation["golden_alignment"] = scores["golden_alignment"]

        if golden_answer:
            evaluation["golden_answer"] = golden_answer

        return evaluation

    def evaluate(
        self,
        query: str,
        context: str,
        answer: str,
        golden_answer: Optional[str] = None,
    ) -> Dict:
        """Evaluate a single query-context-answer triple."""
        scores = self.judge.evaluate(query, answer, context, golden_answer)
        return self._format_scores(scores, golden_answer)

    def run(self, state: Dict) -> Dict:
        """Evaluate from agent pipeline state (live chat)."""
        query = state.get("query", "")
        answer = state.get("answer", "")
        context = self._build_context(state)

        golden = get_golden_item(query)
        golden_answer = golden["golden_answer"] if golden else None

        evaluation = self.evaluate(query, context, answer, golden_answer)

        log_evaluation({
            "query": query,
            "evaluation": evaluation,
            "agents_used": state.get("agents_used", []),
            "mode": "live",
        })

        return evaluation

    def run_golden_item(self, item: Dict, pipeline_result: Dict) -> Dict:
        """Evaluate one golden dataset item against pipeline output."""
        query = item["question"]
        golden_answer = item["golden_answer"]
        answer = pipeline_result.get("answer", "")
        context = "\n\n".join(filter(None, [
            pipeline_result.get("rag_context", ""),
            pipeline_result.get("mcp_result", ""),
            pipeline_result.get("multimodal_result", ""),
        ]))

        evaluation = self.evaluate(query, context, answer, golden_answer)
        evaluation["golden_id"] = item.get("id")
        evaluation["generated_answer"] = answer
        evaluation["routes"] = pipeline_result.get("routes", [])
        evaluation["agents_used"] = pipeline_result.get("agents_used", [])
        return evaluation

    def run_golden_batch(
        self,
        limit: Optional[int] = None,
        save_report: bool = True,
    ) -> Dict:
        """
        Run full evaluation on golden dataset:
        for each Q -> agent pipeline -> LLM judge vs golden answer.
        """
        from App.Graph.Graph import run_agent_pipeline

        dataset = load_golden_dataset()
        if limit:
            dataset = dataset[:limit]

        results: List[Dict] = []

        print(f"\nEvaluating {len(dataset)} golden dataset items...\n")

        for i, item in enumerate(dataset, 1):
            print(f"[{i}/{len(dataset)}] {item['question'][:60]}...")

            pipeline_result = run_agent_pipeline(item["question"])
            eval_result = self.run_golden_item(item, pipeline_result)

            results.append({
                "id": item.get("id"),
                "question": item["question"],
                "golden_answer": item["golden_answer"],
                "generated_answer": pipeline_result.get("answer", ""),
                "faithfulness": eval_result["faithfulness"],
                "grounding": eval_result["grounding"],
                "relevance": eval_result["relevance"],
                "completeness": eval_result["completeness"],
                "hallucination_risk": eval_result["hallucination_risk"],
                "golden_alignment": eval_result.get("golden_alignment"),
                "overall_score": eval_result["overall_score"],
                "grade": eval_result["grade"],
                "details": eval_result.get("details", {}),
                "routes": pipeline_result.get("routes", []),
            })

        summary = aggregate_batch_results(results)

        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "dataset": str(Path("Data/GoldenDataset/golden_dataset.json")),
            "total_items": len(results),
            "summary": summary,
            "results": results,
        }

        if save_report:
            REPORT_DIR.mkdir(parents=True, exist_ok=True)
            report_path = REPORT_DIR / "golden_evaluation_report.json"
            report_path.write_text(
                json.dumps(report, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            print(f"\nReport saved: {report_path}")
            print(f"Overall average: {summary.get('overall_average', 0)}/10")
            print(f"Pass rate (>=7.0): {summary.get('pass_rate', 0)}%")

        log_evaluation({"mode": "golden_batch", "summary": summary})

        return report
