import streamlit as st
from health_dashboard import render_health_dashboard

st.set_page_config(
    page_title="System Health | MediAssistAI",
    page_icon="📊",
    layout="wide",
)

render_health_dashboard()
