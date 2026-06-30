from pathlib import Path
from typing import Dict, List

from App.Multimodal.config import ALLOWED_IMAGE_EXTENSIONS, IMAGE_DIR
from App.Rag.retriever import retrieve
from App.Rag.reranker import rerank
from App.Logs import log_retrieval


class MultiModalAgent:
    """OCR + vision image analysis via indexed image chunks and on-disk images."""

    def _list_images(self) -> List[str]:
        if not IMAGE_DIR.exists():
            return []
        return [
            f.name for f in IMAGE_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in ALLOWED_IMAGE_EXTENSIONS
        ]

    def _match_image_in_query(self, query: str) -> List[str]:
        q = query.lower()
        return [img for img in self._list_images() if img.lower() in q]

    def run(self, query: str) -> Dict:
        try:
            matched = self._match_image_in_query(query)
            docs = retrieve(query, k=10)
            reranked = rerank(query, docs)
            image_chunks = [
                d for d in reranked if d.get("type") == "image"
            ]

            if not image_chunks and matched:
                docs = retrieve(" ".join(matched), k=10)
                reranked = rerank(" ".join(matched), docs)
                image_chunks = [
                    d for d in reranked if d.get("type") == "image"
                ]

            context = "\n\n".join(
                d["text"] for d in image_chunks if d.get("text")
            )

            sources = list({
                d.get("source") for d in image_chunks if d.get("source")
            })

            result = {
                "chunks": image_chunks,
                "context": context,
                "sources": sources,
                "available_images": self._list_images(),
                "matched_images": matched,
                "error": None,
            }

            log_retrieval({
                "agent": "multimodal",
                "query": query,
                "image_chunks": len(image_chunks),
                "sources": sources,
            })

            return result

        except Exception as e:
            return {
                "chunks": [],
                "context": "",
                "sources": [],
                "available_images": [],
                "matched_images": [],
                "error": str(e),
            }
