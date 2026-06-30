import streamlit as st
import requests
import pandas as pd

BASE_API = "http://localhost:8000"
HEALTH_API = f"{BASE_API}/system/health"
METRICS_API = f"{BASE_API}/system/metrics"


def render_health_dashboard():
    st.markdown(
        """
<style>
.health-card {
    background: #ffffff;
    border: 1px solid #e6e9ef;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #1a1a2e;
}
.metric-label {
    font-size: 13px;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
</style>
""",
        unsafe_allow_html=True,
    )

    st.title("📊 System Health & AI Metrics")
    st.caption("Enterprise monitoring dashboard for MediAssistAI services")

    health = {}
    metrics = {}

    try:
        h_resp = requests.get(HEALTH_API, timeout=10)
        if h_resp.status_code == 200:
            health = h_resp.json()
    except Exception:
        pass

    try:
        m_resp = requests.get(METRICS_API, timeout=10)
        if m_resp.status_code == 200:
            metrics = m_resp.json()
    except Exception:
        pass

    overall = health.get("overall_status", "unknown")
    overall_color = (
        "🟢" if overall == "healthy"
        else "🟡" if overall == "degraded"
        else "🔴"
    )

    st.markdown(f"### {overall_color} Platform Status: **{overall.upper()}**")

    st.markdown("---")
    st.subheader("Service Connectivity")

    services = health.get("services", {})
    cols = st.columns(3)

    service_labels = {
        "rag": ("RAG (Vector DB)", "ChromaDB document & image retrieval"),
        "mcp": ("MCP (Database)", "PostgreSQL hospital records"),
        "multimodal": ("Multimodal", "OCR + Vision image analysis"),
    }

    for i, (key, (title, desc)) in enumerate(service_labels.items()):
        svc = services.get(key, {})
        connected = svc.get("connected", False)
        dot = "🟢" if connected else "🔴"
        status_text = "Connected" if connected else "Not Connected"

        with cols[i]:
            st.markdown('<div class="health-card">', unsafe_allow_html=True)
            st.markdown(f"### {dot} {title}")
            st.markdown(f"**Status:** {status_text}")
            st.caption(desc)

            if key == "rag" and connected:
                st.write(f"Collection: `{svc.get('collection', 'N/A')}`")
                st.write(f"Indexed chunks: **{svc.get('document_count', 0)}**")
            elif key == "mcp" and connected:
                st.write(f"Database: `{svc.get('database', 'N/A')}`")
            elif key == "multimodal" and connected:
                st.write(f"Vision model: `{svc.get('vision_model', 'N/A')}`")
                st.write(f"Images stored: **{svc.get('image_count', 0)}**")
                st.write(f"OCR engine: `{svc.get('ocr', 'N/A')}`")
            elif not connected:
                st.error(svc.get("error", "Service unavailable"))

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("LLM Configuration")

    llm = health.get("llm", {})
    llm_cols = st.columns(3)

    with llm_cols[0]:
        st.metric("Provider", llm.get("provider", "N/A").upper())

    with llm_cols[1]:
        st.metric("Model", llm.get("model", "N/A"))

    with llm_cols[2]:
        configured = llm.get("configured", False)
        st.metric("API Key", "Configured" if configured else "Missing")

    st.markdown("---")
    st.subheader("Groq LLM — Token Usage & Cost")

    token_usage = metrics.get("token_usage", {})
    cost = metrics.get("cost_estimation", {})

    st.caption(
        f"Model: **{metrics.get('model', 'N/A')}** · "
        f"Provider: **{metrics.get('provider', 'groq').upper()}**"
    )

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.markdown('<p class="metric-label">Total Requests</p>', unsafe_allow_html=True)
        st.markdown(
            f'<p class="metric-value">{metrics.get("total_requests", 0)}</p>',
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown('<p class="metric-label">Prompt Tokens</p>', unsafe_allow_html=True)
        st.markdown(
            f'<p class="metric-value">{token_usage.get("prompt_tokens", 0):,}</p>',
            unsafe_allow_html=True,
        )

    with m3:
        st.markdown('<p class="metric-label">Completion Tokens</p>', unsafe_allow_html=True)
        st.markdown(
            f'<p class="metric-value">{token_usage.get("completion_tokens", 0):,}</p>',
            unsafe_allow_html=True,
        )

    with m4:
        st.markdown('<p class="metric-label">Total Tokens</p>', unsafe_allow_html=True)
        st.markdown(
            f'<p class="metric-value">{token_usage.get("total_tokens", 0):,}</p>',
            unsafe_allow_html=True,
        )

    with m5:
        st.markdown('<p class="metric-label">Est. Cost (USD)</p>', unsafe_allow_html=True)
        st.markdown(
            f'<p class="metric-value">${cost.get("total_usd", 0.0):.4f}</p>',
            unsafe_allow_html=True,
        )

    st.caption(
        cost.get(
            "note",
            "Cost estimated from Groq token usage (input $0.59/M · output $0.79/M)",
        )
    )

    sessions = metrics.get("recent_sessions", [])

    if sessions:
        last = sessions[-1]
        st.markdown("**Last request**")
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            st.metric("Last Tokens", last.get("total_tokens", 0))
        with lc2:
            st.metric("Last Cost (USD)", f"${last.get('cost_usd', 0.0):.6f}")
        with lc3:
            agents = last.get("agents_used", [])
            st.metric("Agents Used", len(agents))

    st.markdown("---")
    st.subheader("Recent Agent Sessions")

    if sessions:
        df = pd.DataFrame(sessions)
        display_cols = [
            c for c in [
                "prompt_tokens", "completion_tokens", "total_tokens",
                "cost_usd", "agents_used",
            ]
            if c in df.columns
        ]
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No agent sessions recorded yet. Start chatting to see metrics.")

    st.markdown("---")
    st.subheader("Agent Pipeline Architecture")

    st.markdown(
        """
```
User Query
    │
    ▼
Planner Agent  (validation · classification · routing)
    │
    ├────────► MCP Agent          (PostgreSQL hospital DB)
    ├────────► Retriever Agent    (ChromaDB documents)
    └────────► Multimodal Agent   (OCR + Vision images)
                    │
                    ▼
           Reasoning Agent         (final answer synthesis)
                    │
                    ▼
          Evaluation Agent         (faithfulness · relevancy · quality)
                    │
                    ▼
               Response
```
"""
    )

    st.markdown("---")
    st.caption("MediAssistAI Enterprise Monitoring · Auto-refreshes on page load")
