REASONING_PROMPT = """
Combine all agent outputs into a single comprehensive answer.

User Query:
{query}

RAG Context:
{rag_context}

MCP Database Results:
{mcp_result}

Image / Multimodal Results:
{multimodal_result}

Instructions:
- Synthesize information from all available sources.
- Use clear sections and bullet points.
- For image data: include Document Type, Visual Summary, Extracted Text, Key Medical Details.
- For database data: preserve patient IDs, dates, and table sources.
- For documents: cite source filenames.
- End with a brief summary when the answer is long.

Answer:
"""
