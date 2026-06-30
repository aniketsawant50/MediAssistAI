FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY Requirements.txt ./
RUN pip install --upgrade pip && pip install -r Requirements.txt

COPY . .

RUN mkdir -p Data/uploads Data/images Data/processed VectorDB chroma_db

EXPOSE 8000 8501

CMD ["sh", "-c", "uvicorn Backend.rag_api:app --host 0.0.0.0 --port 8000 & streamlit run Frontend/rag_streamlit.py --server.headless true --server.address 0.0.0.0 --server.port 8501 & wait -n"]
