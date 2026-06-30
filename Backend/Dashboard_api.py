from fastapi import FastAPI
from fastapi import UploadFile, File
from pydantic import BaseModel

from pathlib import Path
import uuid
import shutil

from App.Rag.rag_chain import generate_answer
from App.Rag.retriever import Retriever

from App.Rag.document_loader import UnifiedLoader
from App.Rag.chunking import TextChunker
from App.Rag.embedding_service import EmbeddingService
from App.Rag.vector_store import VectorStore

try:
    from Backend.multimodal_api import router as multimodal_router
except ImportError:
    from multimodal_api import router as multimodal_router

from App.MCP.query_router import ask_database
from App.Graph.Graph import run_agent_pipeline
from App.system_health import get_system_health, get_ai_metrics, update_session_metrics
from App.Evaluation.Evaluation_agent import EvaluationAgent
from App.Evaluation.golden_dataset import get_golden_item, load_golden_dataset

app = FastAPI(
    title="MediAssistAI API"
)

app.include_router(multimodal_router)

retriever = Retriever()

UPLOAD_DIR = Path(
    "Data/uploads"
)

IMAGE_DIR = Path(
    "Data/images"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

IMAGE_DIR.mkdir(
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


@app.get("/system/health")
def system_health():
    try:
        return get_system_health()
    except Exception as e:
        return {"error": str(e)}


@app.get("/system/metrics")
def system_metrics():
    try:
        return get_ai_metrics()
    except Exception as e:
        return {"error": str(e)}


@app.post("/agent/chat")
def agent_chat(req: QueryRequest):
    try:
        result = run_agent_pipeline(req.query)

        tokens = result.get("tokens") or {}
        cost = result.get("cost_usd", 0.0) or 0.0
        agents = result.get("agents_used", [])
        answer = result.get("answer") or ""

        if not answer.strip():
            answer = (
                "I couldn't generate an answer. "
                "Please verify RAG documents are uploaded, "
                "MCP database is connected, or images are indexed."
            )

        update_session_metrics(tokens, cost, agents)

        return {
            "answer": answer,
            "sources": result.get("sources", []),
            "agents_used": agents,
            "routes": result.get("routes", []),
            "query_type": result.get("query_type", ""),
            "plan_reasoning": result.get("plan_reasoning", ""),
            "evaluation": result.get("evaluation", {}),
            "tokens": tokens,
            "cost_usd": cost,
        }
    except Exception as e:
        return {
            "error": str(e),
            "answer": f"Agent pipeline error: {e}",
            "sources": [],
            "agents_used": [],
            "tokens": {},
            "cost_usd": 0.0,
        }


@app.get("/evaluation/golden")
def evaluation_golden_dataset():
    try:
        return {
            "total": len(load_golden_dataset()),
            "items": load_golden_dataset(),
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/evaluation/golden/run")
def evaluation_golden_run(limit: int = None):
    try:
        agent = EvaluationAgent()
        report = agent.run_golden_batch(limit=limit)
        return report
    except Exception as e:
        return {"error": str(e)}


@app.post("/evaluation/single")
def evaluation_single(req: QueryRequest):
    """Evaluate: query -> agent pipeline -> LLM judge."""
    try:
        result = run_agent_pipeline(req.query)
        agent = EvaluationAgent()
        context = "\n\n".join(filter(None, [
            result.get("rag_context", ""),
            result.get("mcp_result", ""),
            result.get("multimodal_result", ""),
        ]))
        golden = get_golden_item(req.query)
        evaluation = agent.evaluate(
            req.query,
            context,
            result.get("answer", ""),
            golden["golden_answer"] if golden else None,
        )
        return {
            "query": req.query,
            "answer": result.get("answer", ""),
            "context_preview": context[:500],
            "evaluation": evaluation,
            "agents_used": result.get("agents_used", []),
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/ask")
def ask(query: str):
    try:
        return ask_database(query)
    except Exception as e:
        return {"error": str(e)}


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

        doc_files = [
            file.name
            for file in UPLOAD_DIR.glob("*")
            if file.is_file()
        ]

        image_files = [
            file.name
            for file in IMAGE_DIR.glob("*")
            if file.is_file()
        ]

        return {
            "total_documents": len(doc_files) + len(image_files),
            "documents": doc_files,
            "images": image_files,
        }

    except Exception as e:

        return {
            "error":
            str(e)
        }