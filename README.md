# 🏥 MediAssistAI

> **An Intelligent Healthcare Assistant powered by RAG, Multimodal AI, MCP, and Multi-Agent Architecture**

MediAssistAI is an advanced healthcare-focused AI platform that combines **Document Intelligence**, **Medical Image Understanding**, **Hospital Database Querying**, and **Agentic AI Reasoning** into a unified conversational experience.

The system enables healthcare professionals, administrators, and users to interact naturally with medical documents, prescriptions, reports, images, and structured hospital databases through a single AI-powered interface.

---

## ✨ Key Features

### 📄 Intelligent Document Analysis

* Upload and analyze PDF, DOCX, and TXT files
* Semantic search using Retrieval-Augmented Generation (RAG)
* Context-aware question answering
* Vector-based document retrieval

### 🖼️ Multimodal Medical Understanding

* Prescription image analysis
* Lab report interpretation
* OCR-based text extraction
* Vision-enabled healthcare document processing

### 🏥 MCP-Powered Hospital Database Access

* Patient information retrieval
* Prescription management
* Laboratory report lookup
* Appointment tracking
* Billing information access
* Natural language database querying

### 🤖 Multi-Agent Intelligence

* Planner Agent
* Retriever Agent
* MCP Agent
* Multimodal Agent
* Reasoning Agent

### 📊 Evaluation & Monitoring

* Golden Dataset Evaluation
* LLM-as-a-Judge Framework
* System Health Monitoring
* Performance Metrics Dashboard

---

# 🏗️ System Architecture

```text
                    ┌──────────────────┐
                    │      User        │
                    └────────┬─────────┘
                             │
                             ▼
                ┌─────────────────────────┐
                │  Streamlit Dashboard    │
                └──────────┬──────────────┘
                           │
                           ▼
                ┌─────────────────────────┐
                │     Planner Agent       │
                └──────────┬──────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼

 ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
 │ RAG Agent   │   │ MCP Agent   │   │ Multimodal  │
 │             │   │             │   │ Agent       │
 └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
        │                 │                 │
        ▼                 ▼                 ▼

  Vector DB        Hospital DB       OCR + Vision

        └─────────────────────────────────┘
                          │
                          ▼
                ┌─────────────────┐
                │ Reasoning Agent │
                └────────┬────────┘
                         │
                         ▼
                    Final Answer
```

---

# 🚀 Core Modules

## 📂 RAG Module

Location: `App/Rag`

Responsible for:

* Document Loading
* Chunking
* Embedding Generation
* Vector Database Storage
* Retrieval
* Re-ranking
* Answer Generation

### Components

| Module               | Purpose             |
| -------------------- | ------------------- |
| document_loader.py   | Load documents      |
| chunking.py          | Split documents     |
| embedding_service.py | Generate embeddings |
| vector_store.py      | Store vectors       |
| retriever.py         | Retrieve context    |
| rag_chain.py         | Generate responses  |
| ingest.py            | Document ingestion  |

---

## 🖼️ Multimodal Module

Location: `App/Multimodal`

Responsible for:

* OCR Processing
* Medical Image Understanding
* Image Indexing
* Image Retrieval

### Components

| Module             | Purpose             |
| ------------------ | ------------------- |
| image_processor.py | Image preprocessing |
| ocr_service.py     | OCR extraction      |
| vision_service.py  | Vision reasoning    |
| indexer.py         | Image indexing      |
| ingest.py          | Image ingestion     |

---

## 🏥 MCP Module

Location: `App/MCP`

Provides natural language access to hospital databases.

### Components

| Module          | Purpose             |
| --------------- | ------------------- |
| connector.py    | Database connection |
| tools.py        | Query utilities     |
| query_router.py | NL to SQL routing   |
| server.py       | MCP server          |

---

## 🤖 Agent Layer

Location: `App/Agents`

| Agent            | Responsibility         |
| ---------------- | ---------------------- |
| Planner Agent    | Query routing          |
| Retriever Agent  | Document retrieval     |
| MCP Agent        | Database retrieval     |
| Multimodal Agent | Image reasoning        |
| Reasoning Agent  | Final answer synthesis |

---

# 🛠️ Technology Stack

### Backend

* FastAPI
* Python 3.11
* LangChain
* LangGraph

### AI & ML

* Groq LLM
* Sentence Transformers
* Transformers
* PyTorch

### Retrieval

* ChromaDB
* Vector Embeddings
* Semantic Search

### Multimodal

* EasyOCR
* Pillow
* Computer Vision Models

### Database

* PostgreSQL
* Psycopg2

### Frontend

* Streamlit

### DevOps

* Docker
* Docker Compose

---

# 📁 Project Structure

```text
MediAssistAI
│
├── App
│   ├── Agents
│   ├── Evaluation
│   ├── Graph
│   ├── Logs
│   ├── MCP
│   ├── Multimodal
│   ├── Prompts
│   └── Rag
│
├── Backend
├── Frontend
├── Data
├── VectorDB
├── Dockerfile
├── docker-compose.yml
└── Requirements.txt
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/aniketsawant50/MediAssistAI.git
cd MediAssistAI
```

## Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r Requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key

DB_HOST=localhost
DB_PORT=5432
DB_NAME=database_name
DB_USER=username
DB_PASSWORD=password

MODEL_NAME=llama-3.3-70b-versatile
```

---

# ▶️ Running the Application

## 1. Ingest Documents

```bash
python -m App.Rag.ingest
```

## 2. Start Backend

```bash
uvicorn Backend.Dashboard_api:app --reload
```

## 3. Launch Dashboard

```bash
streamlit run Frontend/Dashboard_streamlit.py
```

---

# 🐳 Docker Deployment

## Build & Run

```bash
docker compose up --build
```

### Services

| Service   | URL                   |
| --------- | --------------------- |
| API       | http://localhost:8000 |
| Dashboard | http://localhost:8501 |

---

# 📡 API Endpoints

| Method | Endpoint        | Description      |
| ------ | --------------- | ---------------- |
| GET    | /health         | Health check     |
| GET    | /system/health  | System status    |
| GET    | /system/metrics | Metrics          |
| POST   | /agent/chat     | Agent workflow   |
| POST   | /chat           | RAG chat         |
| POST   | /retrieve       | Retrieve context |
| POST   | /upload         | Upload documents |
| POST   | /upload-image   | Upload images    |

---

# 📈 Evaluation Framework

The project includes an advanced evaluation pipeline based on:

* Faithfulness
* Grounding
* Relevance
* Completeness
* Hallucination Detection

Run evaluation:

```bash
python -m App.Evaluation.run_evaluation
```

Golden Dataset Included:

```text
Data/GoldenDataset/
├── Golden_Dataset_50_QA.docx
└── golden_dataset.json
```

---

# 🔮 Future Enhancements

* Voice-based healthcare assistant
* Real-time EHR integration
* Clinical decision support
* Medical report summarization
* Multi-language healthcare support
* Cloud-native deployment


## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub and sharing feedback to help improve MediAssistAI.
