import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from docx import Document

GOLDEN_DIR = Path("Data/GoldenDataset")
GOLDEN_DOCX = GOLDEN_DIR / "Golden_Dataset_50_QA.docx"
GOLDEN_JSON = GOLDEN_DIR / "golden_dataset.json"


def _parse_docx(path: Path) -> List[Dict]:
    doc = Document(str(path))
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    pairs: List[Dict] = []
    current_id = None
    current_q = None

    for line in lines:
        id_match = re.match(r"^Q(\d+)$", line, re.I)
        if id_match:
            current_id = int(id_match.group(1))
            continue

        if line.startswith("Question:"):
            current_q = line.replace("Question:", "").strip()
            continue

        if line.startswith("Answer:") and current_q:
            pairs.append({
                "id": current_id or len(pairs) + 1,
                "question": current_q,
                "golden_answer": line.replace("Answer:", "").strip(),
                "category": "document_rag",
            })
            current_q = None

    return pairs


def load_golden_dataset(refresh: bool = False) -> List[Dict]:
    """Load 50+ Q&A pairs from JSON cache or source docx."""
    if GOLDEN_JSON.exists() and not refresh:
        try:
            data = json.loads(GOLDEN_JSON.read_text(encoding="utf-8"))
            if isinstance(data, list) and len(data) >= 1:
                return data
        except json.JSONDecodeError:
            pass

    if not GOLDEN_DOCX.exists():
        raise FileNotFoundError(
            f"Golden dataset not found at {GOLDEN_DOCX}"
        )

    pairs = _parse_docx(GOLDEN_DOCX)
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    GOLDEN_JSON.write_text(
        json.dumps(pairs, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return pairs


def get_golden_item(question: str, dataset: Optional[List[Dict]] = None) -> Optional[Dict]:
    """Find golden reference by exact or fuzzy question match."""
    dataset = dataset or load_golden_dataset()
    q_norm = question.strip().lower()

    for item in dataset:
        if item["question"].strip().lower() == q_norm:
            return item

    for item in dataset:
        if q_norm in item["question"].lower() or item["question"].lower() in q_norm:
            return item

    return None
