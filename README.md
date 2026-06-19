
1. Run the ingest file
python -m App.ingest

2. Run the backend
 uvicorn Backend.main:app --reload

3. Run the streamlit
streamlit run ui/streamlit.py


## DOCUMENT INGESTION

PDF / DOCX / TXT
        ↓
document_loader.py
        ↓
chunking.py
        ↓
embedding_service.py
        ↓
vector_store.py
        ↓
ChromaDB

## QUESTION ANSWERING

User
 ↓
Streamlit UI
 ↓
FastAPI (/chat)
 ↓
rag_chain.py
 ↓
retriever.py
 ↓
embedding_service.py
 ↓
vector_store.py
 ↓
ChromaDB
 ↓
Top 10 Chunks
 ↓
reranker.py
 ↓
Top 5 Chunks
 ↓
rag_chain.py
 ↓
Groq GPT-OSS-120B
 ↓
Generated Answer
 ↓
FastAPI
 ↓
Streamlit
 ↓
User