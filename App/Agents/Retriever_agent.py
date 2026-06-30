from typing import Dict, List

from App.Rag.retriever import retrieve
from App.Rag.reranker import rerank
from App.Logs import log_retrieval


class RetrieverAgent:
    """ChromaDB retrieval, similarity search, metadata filtering, reranking."""

    def run(self, query: str, k: int = 10) -> Dict:
        try:
            docs = retrieve(query, k=k)
            reranked = rerank(query, docs)

            image_docs = [d for d in reranked if d.get("type") == "image"]
            text_docs = [d for d in reranked if d.get("type") != "image"]

            sources = list({
                d.get("source") for d in reranked if d.get("source")
            })

            result = {
                "chunks": reranked[:5],
                "text_chunks": text_docs[:5],
                "image_chunks": image_docs[:5],
                "sources": sources,
                "context": "\n\n".join(
                    d["text"] for d in reranked[:5] if d.get("text")
                ),
                "error": None,
            }

            log_retrieval({
                "query": query,
                "chunk_count": len(reranked),
                "sources": sources,
            })

            return result

        except Exception as e:
            return {
                "chunks": [],
                "text_chunks": [],
                "image_chunks": [],
                "sources": [],
                "context": "",
                "error": str(e),
            }
