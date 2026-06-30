import json
import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

load_dotenv()

LOGS_DIR = Path("App/Logs")
METRICS_FILE = LOGS_DIR / "metrics_session.json"


def check_rag_health() -> Dict:
    try:
        from App.Rag.vector_store import VectorStore

        store = VectorStore()
        count = store.collection.count()
        return {
            "status": "connected",
            "connected": True,
            "collection": "mediassist_docs",
            "document_count": count,
        }
    except Exception as e:
        return {"status": "disconnected", "connected": False, "error": str(e)}


def check_mcp_health() -> Dict:
    try:
        from App.MCP.connector import DBConnector

        conn = DBConnector.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {"status": "connected", "connected": True, "database": os.getenv("DB_NAME", "")}
    except Exception as e:
        return {"status": "disconnected", "connected": False, "error": str(e)}


def check_multimodal_health() -> Dict:
    try:
        from App.Multimodal.config import IMAGE_DIR, VISION_MODEL

        image_dir = Path(IMAGE_DIR)
        image_dir.mkdir(parents=True, exist_ok=True)
        image_count = len([
            f for f in image_dir.iterdir() if f.is_file()
        ])

        llm_ok = bool(os.getenv("GROQ_API_KEY"))
        return {
            "status": "connected",
            "connected": True,
            "vision_model": VISION_MODEL,
            "image_dir": str(image_dir),
            "image_count": image_count,
            "ocr": "easyocr",
            "llm_configured": llm_ok,
        }
    except Exception as e:
        return {"status": "disconnected", "connected": False, "error": str(e)}


def get_system_health() -> Dict:
    rag = check_rag_health()
    mcp = check_mcp_health()
    multimodal = check_multimodal_health()

    all_connected = rag["connected"] and mcp["connected"] and multimodal["connected"]

    return {
        "overall_status": "healthy" if all_connected else "degraded",
        "services": {
            "rag": rag,
            "mcp": mcp,
            "multimodal": multimodal,
        },
        "llm": {
            "provider": "groq",
            "model": os.getenv("MODEL_NAME", "llama-3.3-70b-versatile"),
            "configured": bool(os.getenv("GROQ_API_KEY")),
        },
    }


def load_session_metrics() -> Dict:
    if METRICS_FILE.exists():
        try:
            return json.loads(METRICS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {
        "total_requests": 0,
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "total_tokens": 0,
        "total_cost_usd": 0.0,
        "sessions": [],
    }


def update_session_metrics(tokens: Dict, cost_usd: float, agents_used: list):
    metrics = load_session_metrics()
    prompt = tokens.get("prompt_tokens", 0)
    completion = tokens.get("completion_tokens", 0)
    total = tokens.get("total_tokens", prompt + completion)

    metrics["total_requests"] += 1
    metrics["total_prompt_tokens"] += prompt
    metrics["total_completion_tokens"] += completion
    metrics["total_tokens"] += total
    metrics["total_cost_usd"] = round(
        metrics.get("total_cost_usd", 0) + cost_usd, 6
    )

    sessions = metrics.get("sessions", [])
    sessions.append({
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": total,
        "cost_usd": cost_usd,
        "agents_used": agents_used,
    })
    metrics["sessions"] = sessions[-50:]

    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def get_ai_metrics() -> Dict:
    metrics = load_session_metrics()
    health = get_system_health()

    return {
        "model": health["llm"]["model"],
        "provider": health["llm"]["provider"],
        "total_requests": metrics.get("total_requests", 0),
        "token_usage": {
            "prompt_tokens": metrics.get("total_prompt_tokens", 0),
            "completion_tokens": metrics.get("total_completion_tokens", 0),
            "total_tokens": metrics.get("total_tokens", 0),
        },
        "cost_estimation": {
            "total_usd": metrics.get("total_cost_usd", 0.0),
            "currency": "USD",
            "note": "Estimated from Groq llama-3.3-70b-versatile pricing",
        },
        "recent_sessions": metrics.get("sessions", [])[-10:],
    }
