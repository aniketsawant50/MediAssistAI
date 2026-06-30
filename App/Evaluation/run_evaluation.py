"""
Run golden dataset evaluation (50+ Q&A pairs).

Usage:
    python -m App.Evaluation.run_evaluation
    python -m App.Evaluation.run_evaluation --limit 5
"""

import argparse

from App.Evaluation.Evaluation_agent import EvaluationAgent
from App.Evaluation.golden_dataset import load_golden_dataset


def main():
    parser = argparse.ArgumentParser(description="MediAssistAI Golden Dataset Evaluation")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Evaluate only first N questions (default: all)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Reload golden dataset from docx",
    )
    args = parser.parse_args()

    if args.refresh:
        load_golden_dataset(refresh=True)

    dataset = load_golden_dataset()
    print(f"Loaded {len(dataset)} golden Q&A pairs")

    agent = EvaluationAgent()
    report = agent.run_golden_batch(limit=args.limit)

    summary = report.get("summary", {})
    print("\n=== Evaluation Summary ===")
    for key, val in summary.get("averages", {}).items():
        print(f"  {key}: {val}")
    print(f"  pass_rate: {summary.get('pass_rate', 0)}%")


if __name__ == "__main__":
    main()
