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
        k=10
    )

    reranked_docs = rerank(query, retrieved_docs)

    sources = list(
        {
            doc.get("source")
            for doc in reranked_docs
            if doc.get("source")
        }
    )

    has_image_context = any(
        doc.get("type") == "image" for doc in reranked_docs
    )

    # Convert retrieved docs to context
    context = "\n\n".join(
        [doc["text"] for doc in reranked_docs if doc.get("text")]
    )

    image_instructions = ""
    if has_image_context:
        image_instructions = """
- The context includes medical images (prescriptions, lab reports, or scans).
- Present extracted information in a structured format with clear sections:
  **Document Type**, **Source File**, **Visual Summary**, **Extracted Text**, **Key Medical Details**.
- For prescriptions: list patient name, doctor, date, medications, dosage, and instructions when present.
- For lab reports: list test names, values, units, and reference ranges when present.
- If the user asks to summarize an image, organize the OCR and visual data clearly.
"""

    # No context found
    if not context.strip():
        return {
            "answer": (
                "I couldn't find relevant information "
                "in the uploaded hospital documents or images."
            ),
            "sources": []
        }

    # Prompt
    prompt = f"""
Context:
{context}

Question:
{query}

Instructions:
- Answer ONLY from the provided context.
- Provide a detailed and comprehensive explanation.
- Include all relevant information from the context.
- Use bullet points when appropriate.
- Explain procedures step-by-step if available.
- Mention SOP names, departments, contact information, timings, and requirements when present.
- If information is missing, clearly state what is unavailable.
{image_instructions}
Answer:
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
        temperature=0.2,
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
   - Detailed
   - Well structured

6. When sufficient context is available:
   - Explain thoroughly
   - Use bullet points
   - Include all relevant details
   - Summarize key points at the end

7. Do not shorten answers unless the user specifically asks for a brief response.

8. Mention SOP names when available.
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