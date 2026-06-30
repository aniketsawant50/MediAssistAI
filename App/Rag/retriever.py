from .embedding_service import EmbeddingService
from .vector_store import VectorStore


def retrieve(query, k: int = 10):
    """Retrieve top-k documents for a query and return list of dicts.

    This is the functional API used by the RAG flow.
    """
    embedder = EmbeddingService()                               #Create the object of the classes
    store = VectorStore()

    query_embedding = embedder.embed_query(query)                #Generate the vector representation 

    results = store.search(query_embedding, k)

    output = []

    # chroma returns lists inside lists per query; handle gracefully
    docs = results.get("documents", [[]])[0]                          #It is the documents that are retrived based on query
    scores = results.get("distances", [[]])[0]                        #It is the similarity score between the query and documents

    metadatas = results.get("metadatas", [[]])[0]

    for doc, score, metadata in zip(docs, scores, metadatas):
        output.append({
            "text": doc,
            "score": round(float(score), 4),
            "source": metadata.get("source") if isinstance(metadata, dict) else None,
            "type": metadata.get("type") if isinstance(metadata, dict) else None,
            "doc_type": metadata.get("doc_type") if isinstance(metadata, dict) else None,
        })

    return output


class Retriever:
    """Simple class wrapper providing a `retrieve` method for callers
    that expect an object with `.retrieve(query, k=...)`.
    """

    # def __init__(self):
        # self._service = None

    def retrieve(self, query: str, k: int = 10):
        return retrieve(query, k=k)


# expose a module-level name expected by other modules
retriever = retrieve