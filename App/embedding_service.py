from typing import List, Optional


class EmbeddingService:

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self.model = None

    def _ensure_model(self):
        if self.model is None:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(self.model_name)

    def embed_documents(self, texts: List[str]):
        self._ensure_model()

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings

    def embed_query(self, query: str):
        self._ensure_model()

        embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding[0]