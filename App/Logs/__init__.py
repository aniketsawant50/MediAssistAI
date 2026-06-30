import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

LOGS_DIR = Path("App/Logs")


def _append_json(log_path: Path, entry: Dict[str, Any]):
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if log_path.exists():
        try:
            data = json.loads(log_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    if not isinstance(data, list):
        data = [data]

    entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
    data.append(entry)

    log_path.write_text(
        json.dumps(data, indent=2, default=str),
        encoding="utf-8",
    )


def log_planner(entry: Dict[str, Any]):
    _append_json(LOGS_DIR / "Planner" / "planner_logs.json", entry)


def log_retrieval(entry: Dict[str, Any]):
    _append_json(LOGS_DIR / "Rag" / "retrieval_logs.json", entry)


def log_reasoning(entry: Dict[str, Any]):
    _append_json(LOGS_DIR / "Reason" / "reasoning_logs.json", entry)


def log_completed(entry: Dict[str, Any]):
    _append_json(LOGS_DIR / "Completed" / "completed_sessions.json", entry)


def log_evaluation(entry: Dict[str, Any]):
    _append_json(LOGS_DIR / "Evaluation" / "evaluation_logs.json", entry)
