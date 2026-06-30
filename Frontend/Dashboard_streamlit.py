import streamlit as st
import requests

# ---------------------------
# API Configuration
# ---------------------------

BASE_API = "http://localhost:8000"
AGENT_API = f"{BASE_API}/agent/chat"
UPLOAD_API = f"{BASE_API}/upload"
IMAGE_UPLOAD_API = f"{BASE_API}/upload-image"
DOCUMENT_API = f"{BASE_API}/documents"
HEALTH_API = f"{BASE_API}/system/health"

# ---------------------------
# Page Config
# ---------------------------

st.set_page_config(
    page_title="MediAssistAI",
    page_icon="🏥",
    layout="wide",
)

# ---------------------------
# Styling
# ---------------------------

st.markdown(
    """
<style>
.main-header {
    position: sticky;
    top: 0;
    background: white;
    z-index: 999;
    padding: 10px;
    border-bottom: 1px solid #ddd;
}
.status-pill {
    display: block;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 8px;
    text-align: center;
}
.status-green {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}
.status-red {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}
.source {
    font-size: 12px;
    color: gray;
    margin-top: 10px;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# Session State
# ---------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "question_history" not in st.session_state:
    st.session_state.question_history = []

if "current_page" not in st.session_state:
    st.session_state.current_page = "chat"


# ---------------------------
# Helpers
# ---------------------------


def fetch_service_health():
    try:
        response = requests.get(HEALTH_API, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def render_status_pill(label, connected):
    css = "status-green" if connected else "status-red"
    text = "Connected" if connected else "Not Connected"
    st.markdown(
        f'<span class="status-pill {css}">{label}: {text}</span>',
        unsafe_allow_html=True,
    )


def handle_agent_query(query):
    response = requests.post(
        AGENT_API,
        json={"query": query},
        timeout=180,
    )

    data = response.json()

    if response.status_code != 200:
        return {"answer": f"Error: {response.text}", "sources": [], "agents_used": []}

    if not data.get("answer") and data.get("error"):
        data["answer"] = data["error"]

    return data


# ---------------------------
# Header
# ---------------------------

st.markdown(
    """
<div class="main-header">
<h1>🏥 MediAssistAI</h1>
<p>Documents · Images · Hospital Database</p>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# Sidebar
# ---------------------------

health = fetch_service_health()

with st.sidebar:
    st.header("Service Status")

    if health and health.get("services"):
        services = health["services"]
        render_status_pill(
            "RAG",
            services.get("rag", {}).get("connected", False),
        )
        render_status_pill(
            "MCP",
            services.get("mcp", {}).get("connected", False),
        )
        render_status_pill(
            "Multimodal",
            services.get("multimodal", {}).get("connected", False),
        )
    else:
        render_status_pill("RAG", False)
        render_status_pill("MCP", False)
        render_status_pill("Multimodal", False)

    if st.session_state.current_page == "chat":
        if st.button("📊 System Health", use_container_width=True, key="open_health"):
            st.session_state.current_page = "health"
            st.rerun()
    else:
        if st.button("🏥 Back to Chat", use_container_width=True, key="back_chat"):
            st.session_state.current_page = "chat"
            st.rerun()

    st.divider()

    st.header("📂 Upload Document")

    uploaded_file = st.file_uploader(
        "Upload PDF / DOCX / TXT",
        type=["pdf", "docx", "txt"],
    )

    if uploaded_file:
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue())
        }
        try:
            response = requests.post(UPLOAD_API, files=files, timeout=300)
            if response.status_code == 200:
                data = response.json()
                if data.get("error"):
                    st.error(data["error"])
                else:
                    st.success(f"{uploaded_file.name} uploaded successfully")
            else:
                st.error(response.text)
        except Exception as e:
            st.error(str(e))

    st.divider()

    st.header("🖼️ Upload Image")

    st.caption("Prescriptions, lab reports, or medical images")

    uploaded_image = st.file_uploader(
        "Upload prescription / lab report / image",
        type=["jpg", "jpeg", "png", "bmp", "tiff", "webp"],
        key="image_uploader",
    )

    if uploaded_image:
        image_files = {
            "file": (uploaded_image.name, uploaded_image.getvalue())
        }
        try:
            response = requests.post(
                IMAGE_UPLOAD_API, files=image_files, timeout=600
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("error"):
                    st.error(data["error"])
                else:
                    st.success(f"{uploaded_image.name} indexed successfully")
                    if data.get("doc_type"):
                        st.caption(f"Detected type: {data['doc_type']}")
                    if data.get("caption"):
                        st.caption(f"Visual summary: {data['caption']}")
            else:
                st.error(response.text)
        except Exception as e:
            st.error(str(e))

    st.divider()

    st.header("Uploaded Files")

    try:
        response = requests.get(DOCUMENT_API)
        if response.status_code == 200:
            docs = response.json().get("documents", [])
            images = response.json().get("images", [])

            if docs:
                st.subheader("Documents")
                for doc in docs:
                    st.write(f"📄 {doc}")

            if images:
                st.subheader("Images")
                for image in images:
                    st.write(f"🖼️ {image}")

            if not docs and not images:
                st.info("No files uploaded yet")
    except Exception:
        st.warning("Backend not connected")

# ---------------------------
# Main Content
# ---------------------------

if st.session_state.current_page == "health":
    from health_dashboard import render_health_dashboard

    render_health_dashboard()
    st.stop()

# ---------------------------
# Sample Questions
# ---------------------------
with st.expander("📋 Sample MCP Questions"):
    selected_question = st.selectbox(
        "Choose a question",
        [
            "1.Show patient PC00001Q",
            "2.Give history of Patient 1 ML",
            "3.Show prescriptions of Patient 1 ML",
            "4.Show lab reports of Patient 1 ML",
            "5.Show billing of Patient 1 ML",
            
        ]
    )


# ==========================================
# RAG SAMPLE QUESTIONS
# ==========================================

with st.expander("📚 Sample RAG Questions"):
    selected_rag_question = st.selectbox(
        "Choose a question",
        [
            "1. Summarize the uploaded medical document",
            "2. What should be verified before surgery?",
            "3. What Admission process?",
            "4. What information must a discharge summary contain?"
        ],
        key="rag_questions"
    )


# ==========================================
# MULTIMODAL SAMPLE QUESTIONS
# ==========================================

with st.expander("🖼️ Sample Multimodal Questions"):
    selected_multimodal_question = st.selectbox(
        "Choose a question",
        [
            "1. Analyze the uploaded prescription image",
            "2. Extract all text from the uploaded medical report",
            "3. Identify medicines mentioned in the uploaded prescription",
            "4. Summarize the uploaded laboratory report image"
        ],
        key="multimodal_questions"
    )
# ---------------------------
# Chat History
# ---------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# ---------------------------
# Chat Input
# ---------------------------

st.divider()

query = st.chat_input("Ask your medical question...")

if query:
    st.session_state.question_history.append(query)
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                data = handle_agent_query(query)
                answer = data.get("answer") or "No answer generated."
                sources = data.get("sources", [])
                agents_used = data.get("agents_used", [])

                if sources:
                    answer += (
                        "<div class='source'>"
                        f"(Source: {', '.join(sources)})"
                        "</div>"
                    )
                else:
                    answer += (
                        "<div class='source'>"
                        "(Source: Not Available)"
                        "</div>"
                    )

                if agents_used:
                    agent_labels = ", ".join(
                        a for a in agents_used if a not in ("evaluation",)
                    )
                    answer += (
                        "<div class='source'>"
                        f"(Agents: {agent_labels})"
                        "</div>"
                    )

            except Exception as e:
                answer = f"Connection Error: {e}"
                agents_used = []

        st.markdown(answer, unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })
