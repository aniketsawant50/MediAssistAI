import os
from dotenv import load_dotenv

from .retriever import retriever
from .reranker import rerank

load_dotenv()

# Initialize Groq client only if API key is provided to avoid hangs/errors
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)
    except Exception:
        client = None
else:
    client = None

# Model name for LLM; if not configured, we won't call the remote API
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")


def is_greeting(query: str):

    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good evening"
    ]

    return query.lower().strip() in greetings


def generate_answer(query: str):

    # Greeting handling
    if is_greeting(query):
        return {
            "answer": (
                "Hello! I am MediAssistAI. "
                "How can I assist you today?"
            ),
            "sources": []
        }

    # Retrieve relevant chunks
    retrieved_docs = retriever(
        query=query,
        k=5
    )

    reranked_docs = rerank(query, retrieved_docs)

    sources = list(
        {
            doc.get("source")
            for doc in reranked_docs
            if doc.get("source")
        }
    )

    # Convert retrieved docs to context
    context = "\n\n".join(
        [doc["text"] for doc in reranked_docs if doc.get("text")]
    )

    # No context found
    if not context.strip():
        return {
            "answer": (
                "I couldn't find relevant information "
                "in the uploaded hospital documents."
            ),
            "sources": []
        }

    # Prompt
    prompt = f"""
Context:
{context}

Question:
{query}

Answer based ONLY on the provided context.
"""

    # LLM Call
    if client is None:
        return {
            "answer": (
                "LLM is not configured. Please set GROQ_API_KEY in your environment "
                "or in a .env file to enable full answers."
            ),
            "sources": sources,
        }

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": """
You are MediAssistAI.

You answer questions only from
hospital documents provided in context.

Rules:

1. Use only provided context.
2. Never use outside knowledge.
3. If answer not found:
   "I don't know based on the provided documents."

4. If question unrelated:
   "I can only answer questions related to the uploaded hospital documents."

5. Keep answers:
   - Professional
   - Accurate
   - Clear
   - Concise

6. Mention SOP names when available.
"""
                },
                {"role": "user", "content": prompt},
            ],
        )

        return {
            "answer": response.choices[0].message.content,
            "sources": sources,
        }
    except Exception as e:
        return {
            "answer": f"LLM error: {e}",
            "sources": sources,
        }