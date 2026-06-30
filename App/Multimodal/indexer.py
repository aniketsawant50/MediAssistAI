import uuid
from pathlib import Path
from typing import Dict, List

from App.Rag.chunking import TextChunker
from App.Rag.embedding_service import EmbeddingService
from App.Rag.vector_store import VectorStore

from .image_processor import ImageProcessor


class ImageIndexer:

    def __init__(self):
        self.processor = ImageProcessor()

    def index_image(self, image_path: Path) -> Dict:
        result = self.processor.process_image(image_path)

        chunker = TextChunker()
        chunks = chunker.split(result["structured_text"])

        if not chunks:
            chunks = [result["structured_text"]]

        embedder = EmbeddingService()
        embeddings = embedder.embed_documents(chunks)

        metadata: List[Dict] = []
        for _ in chunks:
            metadata.append(
                {
                    "source": result["filename"],
                    "type": "image",
                    "doc_type": result["doc_type"],
                    "path": str(image_path),
                }
            )

        ids = [str(uuid.uuid4()) for _ in chunks]

        store = VectorStore()
        store.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadata,
        )

        return {
            "filename": result["filename"],
            "doc_type": result["doc_type"],
            "caption": result["caption"],
            "ocr_preview": result["ocr_text"][:500],
            "chunks": len(chunks),
            "structured_text": result["structured_text"],
        }
