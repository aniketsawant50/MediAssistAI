from typing import Dict, List, Optional


def average_score(scores: List[float]) -> float:
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores), 2)


def compute_overall(metrics: Dict[str, float]) -> float:
    """Weighted overall score (all metrics higher-is-better after inversion)."""
    hallucination_risk = metrics.get(
        "hallucination_risk",
        metrics.get("hallucination", 5),
    )
    hallucination_quality = 10 - hallucination_risk

    weights = {
        "faithfulness": 0.20,
        "grounding": 0.20,
        "relevance": 0.15,
        "completeness": 0.15,
        "hallucination_quality": 0.15,
        "golden_alignment": 0.15,
    }

    golden = metrics.get("golden_alignment")
    if golden is None:
        # Redistribute golden weight when not available
        weights = {
            "faithfulness": 0.25,
            "grounding": 0.25,
            "relevance": 0.20,
            "completeness": 0.15,
            "hallucination_quality": 0.15,
        }

    score = (
        metrics.get("faithfulness", 5) * weights["faithfulness"]
        + metrics.get("grounding", metrics.get("faithfulness", 5)) * weights["grounding"]
        + metrics.get("relevance", metrics.get("relevancy", 5)) * weights["relevance"]
        + metrics.get("completeness", 5) * weights["completeness"]
        + hallucination_quality * weights["hallucination_quality"]
    )

    if golden is not None:
        score += golden * weights.get("golden_alignment", 0)

    return round(score, 2)


def grade_score(score: float) -> str:
    if score >= 8.5:
        return "Excellent"
    if score >= 7.0:
        return "Good"
    if score >= 5.0:
        return "Fair"
    return "Needs Improvement"


def aggregate_batch_results(results: List[Dict]) -> Dict:
    """Summarize evaluation across golden dataset run."""
    if not results:
        return {"count": 0}

    keys = [
        "faithfulness", "grounding", "relevance",
        "completeness", "hallucination_risk", "golden_alignment", "overall_score",
    ]

    summary = {"count": len(results), "averages": {}, "grades": {}}

    for key in keys:
        values = [r.get(key) for r in results if r.get(key) is not None]
        if values:
            summary["averages"][key] = average_score(values)

    grades = [r.get("grade") for r in results if r.get("grade")]
    for g in ["Excellent", "Good", "Fair", "Needs Improvement"]:
        summary["grades"][g] = grades.count(g)

    summary["overall_average"] = summary["averages"].get("overall_score", 0)
    summary["pass_rate"] = round(
        len([r for r in results if r.get("overall_score", 0) >= 7.0]) / len(results) * 100,
        1,
    )

    return summary
