from fastapi import FastAPI
from fastapi import UploadFile, File
from pydantic import BaseModel

from pathlib import Path
import uuid
import shutil

from App.rag_chain import generate_answer
from App.retriever import Retriever

from App.document_loader import UnifiedLoader
from App.chunking import TextChunker
from App.embedding_service import EmbeddingService
from App.vector_store import VectorStore

app = FastAPI(
    title="MediAssistAI API"
)

retriever = Retriever()

UPLOAD_DIR = Path(
    "Data/uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# -----------------------------
# Request Schema
# -----------------------------

class QueryRequest(BaseModel):
    query: str


# -----------------------------
# Health Check
# -----------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "message": "MediAssistAI API is running"
    }


# -----------------------------
# Retrieve Chunks
# -----------------------------

@app.post("/retrieve")
def retrieve(req: QueryRequest):

    try:

        results = retriever.retrieve(
            req.query,
            k=10
        )

        return {
            "query": req.query,
            "results": results
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# -----------------------------
# Chat Endpoint
# -----------------------------

@app.post("/chat")
def chat(req: QueryRequest):

    try:

        result = generate_answer(req.query)

        if isinstance(result, dict):
            answer = result.get("answer", "")
            sources = result.get("sources", [])
        else:
            answer = str(result)
            sources = []

        return {
            "answer": answer,
            "sources": sources
        }

    except Exception as e:

        return {
            "error": str(e)
        }
# -----------------------------
# Upload & Index Document
# -----------------------------

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    try:

        allowed_extensions = [
            ".pdf",
            ".docx",
            ".txt"
        ]

        extension = (
            Path(file.filename)
            .suffix
            .lower()
        )

        if extension not in allowed_extensions:

            return {
                "error":
                "Only PDF, DOCX and TXT files are allowed."
            }

        file_path = (
            UPLOAD_DIR /
            file.filename
        )

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # --------------------
        # Load Document
        # --------------------

        loader = UnifiedLoader()

        text = loader.load_document(
            file_path
        )

        if not text.strip():

            return {
                "error":
                "Document is empty."
            }

        # --------------------
        # Chunking
        # --------------------

        chunker = TextChunker()

        chunks = chunker.split(
            text
        )

        # --------------------
        # Embeddings
        # --------------------

        embedder = EmbeddingService()

        embeddings = (
            embedder.embed_documents(
                chunks
            )
        )

        # --------------------
        # Metadata
        # --------------------

        metadata = []

        for _ in chunks:

            metadata.append(
                {
                    "source":
                    file.filename
                }
            )

        ids = [

            str(
                uuid.uuid4()
            )

            for _ in chunks
        ]

        # --------------------
        # Store in ChromaDB
        # --------------------

        store = VectorStore()

        store.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadata
        )

        return {

            "message":
            "Document uploaded and indexed successfully",

            "filename":
            file.filename,

            "chunks":
            len(chunks)
        }

    except Exception as e:

        return {
            "error":
            str(e)
        }


# -----------------------------
# List Uploaded Files
# -----------------------------

@app.get("/documents")
def documents():

    try:

        files = [

            file.name

            for file in
            UPLOAD_DIR.glob("*")

            if file.is_file()
        ]

        return {

            "total_documents":
            len(files),

            "documents":
            files
        }

    except Exception as e:

        return {
            "error":
            str(e)
        }