# streamlit_frontend.py
import streamlit as st
import requests

# --- FastAPI Backend URL ---
API_URL = "http://127.0.0.1:8000"  # L'URL de ton serveur FastAPI local

# --- Dashboard UI ---
st.set_page_config(page_title="LLaMA Data Tools", page_icon="⚡", layout="wide")
st.markdown("""
<style>
.main { background-color: #0d1117; color: #c9d1d9; }
.stTextArea textarea { font-family: 'Courier New', monospace; background-color: #161b22; color: #58a6ff; border-radius: 10px; }
.stButton>button { background-color: #238636; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; padding: 10px; }
.stCode { background-color: #010409 !important; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("SQL & JSON Tools")
app_mode = st.sidebar.selectbox("Choose Tool", ["📊 SQL Generator", "🧩 JSON Extractor"])

# --- SQL Generator ---
if app_mode == "📊 SQL Generator":
    st.header("🗄️ SQL Generator (Schema-aware)")

    schema = st.text_area("Database Schema", "Users(id, full_name); Orders(id, user_id, total_amount);")
    query = st.text_input("Request", "Show total order amounts per user.")

    if st.button("Generate SQL"):
        response = requests.post(f"{API_URL}/generate-sql", json={"schema": schema, "query": query})
        if response.status_code == 200:
            result = response.json()
            st.success("✅ Valid SQL Generated")
            st.code(result['sql'], language="sql")
        else:
            st.error(f"Error: {response.json()['detail']}")

# --- JSON Extractor ---
elif app_mode == "🧩 JSON Extractor":
    st.header("📝 JSON Entity Extractor")

    raw_text = st.text_area("Paste unstructured text", "Alice is 25, Engineer in NYC.")
    
    if st.button("Extract JSON"):
        response = requests.post(f"{API_URL}/extract-json", json={"raw_text": raw_text})
        if response.status_code == 200:
            result = response.json()
            st.json(result['json'])
        else:
            st.error(f"Error: {response.json()['detail']}")
