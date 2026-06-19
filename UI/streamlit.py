import streamlit as st
import requests

# ---------------------------
# API Configuration
# ---------------------------

CHAT_API = "http://localhost:8000/chat"
UPLOAD_API = "http://localhost:8000/upload"
DOCUMENT_API = "http://localhost:8000/documents"

# ---------------------------
# Page Config
# ---------------------------

st.set_page_config(
    page_title="MediAssistAI",
    layout="wide"
)

# ---------------------------
# Minimal Styling
# ---------------------------

st.markdown("""
<style>

.main-header{
    position:sticky;
    top:0;
    background:white;
    z-index:999;
    padding:10px;
    border-bottom:1px solid #ddd;
}

.source{
    font-size:12px;
    color:gray;
    margin-top:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# Header
# ---------------------------

st.markdown("""
<div class="main-header">
<h1>🏥 MediAssistAI</h1>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# Session State
# ---------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "question_history" not in st.session_state:
    st.session_state.question_history = []

# ---------------------------
# Sidebar
# ---------------------------

with st.sidebar:

    st.header("📂 Upload Document")

    uploaded_file = st.file_uploader(
        "Upload PDF / DOCX / TXT",
        type=["pdf", "docx", "txt"]
    )

    if uploaded_file:

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue()
            )
        }

        try:

            response = requests.post(
                UPLOAD_API,
                files=files,
                timeout=300
            )

            if response.status_code == 200:

                st.success(
                    f"{uploaded_file.name} uploaded successfully"
                )

            else:

                st.error(
                    response.text
                )

        except Exception as e:

            st.error(str(e))

    st.divider()

    st.header("📑 Uploaded Documents")

    try:

        response = requests.get(
            DOCUMENT_API
        )

        if response.status_code == 200:

            docs = response.json().get(
                "documents",
                []
            )

            if docs:

                for doc in docs:

                    st.write(
                        f" {doc}"
                    )

            else:

                st.info(
                    "No documents uploaded"
                )

    except:

        st.warning(
            "Backend not connected"
        )

    # st.divider()

    # st.header(" Last 10 Questions")

    # if st.session_state.question_history:

    #     for q in reversed(
    #         st.session_state.question_history[-10:]
    #     ):

    #         st.write(
    #             f"• {q}"
    #         )

    # else:

    #     st.caption(
    #         "No questions yet"
    #     )

# ---------------------------
# Recent Questions
# ---------------------------

# history_items = list(reversed(st.session_state.question_history[-10:]))

# with st.expander("Recent Questions", expanded=False):
#     if history_items:
#         selected_question = st.selectbox(
#              history_items,
#             key="history_dropdown"
#         )
#         if selected_question != "Select a question":
#             st.write(f"• {selected_question}")
#     else:
#         st.write("No questions yet.")

# ---------------------------
# Chat History
# ---------------------------

for msg in st.session_state.messages:

    with st.chat_message(
        msg["role"]
    ):

        st.markdown(
            msg["content"],
            unsafe_allow_html=True
        )

# ---------------------------
# Chat Input
# ---------------------------

st.divider()

query = st.chat_input(
    "Ask your medical question..."
)

 




# ---------------------------
# Process Query
# ---------------------------

if query:

    # Save Question

    st.session_state.question_history.append(
        query
    )

    # User Message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(query)

    # Assistant Response

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Thinking..."
        ):

            try:

                response = requests.post(
                    CHAT_API,
                    json={
                        "query": query
                    },
                    timeout=120
                )

                if response.status_code == 200:

                    data = response.json()

                    answer = data.get(
                        "answer",
                        "No answer generated."
                    )

                    sources = data.get(
                        "sources",
                        []
                    )

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

                else:

                    answer = (
                        f"Error: {response.text}"
                    )

            except Exception as e:

                answer = (
                    f"Connection Error: {e}"
                )

            st.markdown(
                answer,
                unsafe_allow_html=True
            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )