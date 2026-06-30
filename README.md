# MediAssistAI

MediAssistAI is a healthcare-focused AI assistant that combines document retrieval, multimodal image understanding, and hospital database querying into a single conversational interface. The system is designed to help users ask questions about uploaded medical documents, prescriptions, lab reports, images, and structured hospital data.

## 1. Overview

<<<<<<< HEAD
3. Run the streamlit
streamlit run ui/streamlit.py
=======
The platform consists of three major capabilities:

- Document understanding and retrieval from PDF, DOCX, and TXT files
- Multimodal processing for uploaded images such as prescriptions and lab reports
- Structured querying over hospital data through an MCP-backed database layer

A FastAPI backend exposes the application services, while a Streamlit frontend provides the end-user experience.

## 2. Architecture

The repository is organized into the following major modules:

- App/Rag: document ingestion, chunking, embeddings, vector search, and answer generation
- App/Multimodal: image upload, OCR/vision processing, indexing, and retrieval
- App/MCP: database connector, query tools, and MCP API integration
- App/Agents: planner, retriever, MCP, multimodal, and reasoning agents
- App/Graph: agent orchestration and routing pipeline
- Backend: FastAPI services for RAG, MCP, and multimodal APIs
- Frontend: Streamlit-based web UI
- Data: uploaded files, processed artifacts, and golden evaluation data

### Core flow

1. User uploads documents or images through the UI.
2. Documents are ingested, chunked, embedded, and stored in a vector database.
3. Queries are routed through the agent pipeline.
4. Relevant document chunks, database results, and image context are combined.
5. The reasoning layer returns a grounded answer to the user.

## 3. Main Components

### 3.1 RAG pipeline

The retrieval and generation pipeline is implemented under App/Rag.

Key modules:
- document_loader.py: loads PDF, DOCX, and TXT files
- chunking.py: splits documents into chunk-sized segments
- embedding_service.py: generates embeddings
- vector_store.py: stores and retrieves vector data
- rag_chain.py: builds the answer generation pipeline with reranking
- retriever.py: retrieves relevant context for a query
- ingest.py: runs the ingestion workflow over uploaded documents

### 3.2 Multimodal pipeline

The multimodal subsystem is implemented under App/Multimodal.

Key modules:
- image_processor.py: processes uploaded images
- ocr_service.py: extracts text from images
- vision_service.py: handles visual understanding tasks
- indexer.py: indexes image content for retrieval
- ingest.py: ingests image assets into the multimodal store

### 3.3 MCP and hospital database layer

The database layer is implemented under App/MCP.

Key modules:
- connector.py: manages database connectivity
- tools.py: provides query helpers for patients, prescriptions, labs, appointments, billing, and other hospital data
- query_router.py: maps natural language requests to structured database retrieval
- server.py: MCP server entry point

### 3.4 Agent orchestration

The graph-based orchestration layer is implemented under App/Graph.

It coordinates:
- planner agent for route selection
- retriever agent for RAG context
- MCP agent for database access
- multimodal agent for image context
- reasoning agent for final synthesis

## 4. Technology Stack

- Python 3.11
- FastAPI for backend APIs
- Streamlit for the web UI
- LangChain and LangGraph for retrieval and orchestration workflows
- ChromaDB for vector storage
- Sentence Transformers and Transformers for embeddings and language models
- PyTorch for model support
- PostgreSQL-compatible database access via psycopg2-binary
- Groq API for LLM-based answer generation
- EasyOCR and Pillow for image processing

## 5. Project Structure

```text
App/
  Agents/
  Evaluation/
  Graph/
  Logs/
  MCP/
  Multimodal/
  Prompts/
  Rag/
Backend/
Frontend/
Data/
VectorDB/
```

## 6. Environment Setup

### Prerequisites

- Python 3.11+
- pip
- Docker (optional, recommended)
- Access to a PostgreSQL-compatible database if MCP queries are required
- A Groq API key if you want full LLM-generated answers

### Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\\Scripts\\activate      # Windows PowerShell
pip install -r Requirements.txt
```

### Required environment variables

Create a .env file with values such as:

```env
GROQ_API_KEY=your_groq_api_key
MODEL_NAME=llama-3.3-70b-versatile
DB_HOST=your_database_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

## 7. Running the Application Locally

### 7.1 Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r Requirements.txt
```

On Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r Requirements.txt
```

### 7.2 Ingest documents

Place supported files in the Data/uploads directory and run:

```bash
python -m App.Rag.ingest
```

This process:
- loads documents
- splits them into chunks
- creates embeddings
- stores them in the vector database
- also triggers image ingestion if applicable

### 7.3 Start the backend API

```bash
uvicorn Backend.rag_api:app --host 0.0.0.0 --port 8000 --reload
```

### 7.4 Start the Streamlit frontend

```bash
streamlit run Frontend/rag_streamlit.py --server.port 8501
```

### 7.5 Access the app

Once both services are running:
- Open the frontend at http://localhost:8501
- Use the backend API at http://localhost:8000
- The health endpoint is available at http://localhost:8000/health

### 7.6 Optional: run evaluation

```bash
python -m App.Evaluation.run_evaluation
```

## 8. Docker Deployment

The repository includes Docker support for running the backend and UI together.

### Build and run with Docker Compose

```bash
docker compose up --build
```

Then open:
- http://localhost:8000 for the API
- http://localhost:8501 for the Streamlit UI

### Docker files

- Dockerfile: container definition for the Python runtime
- docker-compose.yml: service configuration for API and UI
- .dockerignore: excludes unnecessary files from the build context

## 9. API Endpoints

The FastAPI backend exposes the following core endpoints:

- GET /health: basic health status
- GET /system/health: aggregated service health
- GET /system/metrics: usage and performance metrics
- POST /agent/chat: runs the full agent pipeline
- POST /chat: runs the simple RAG chat flow
- POST /retrieve: retrieves relevant chunks
- POST /upload: uploads and indexes documents
- POST /upload-image: uploads and indexes images

## 10. Evaluation and Testing

The project includes an evaluation module under App/Evaluation.

You can run the evaluation workflow with:

```bash
python -m App.Evaluation.run_evaluation
```

This module supports golden dataset testing and scoring for the assistant responses.

## 11. Notes and Recommendations

- The application works best when documents and images are uploaded before asking questions.
- If the LLM provider is not configured, the RAG flow can still retrieve context but answer generation may be limited.
- The MCP feature depends on a reachable and correctly configured database.
- For production deployments, consider using environment-based secrets, persistent storage for the vector database, and a managed database service.

>>>>>>> b55a983 (Added multi-agent architecture, MCP, multimodal, evaluation, dashboard and RAG modules)
