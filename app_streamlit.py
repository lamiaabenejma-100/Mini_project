import streamlit as st
import json
import pandas as pd
from model_loader import generate

# ================= SESSION =================
if "candidate_memory" not in st.session_state:
    st.session_state.candidate_memory = []

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "🎯"

# ================= PAGE =================
st.set_page_config(page_title="AI HR Assistant", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #0d0d0d; color: #ececec; }
.chat-bubble {
    background-color: #212121;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    border: 1px solid #333;
}
.stTextArea textarea, .stTextInput input {
    background-color: #1a1a1a !important;
    color: white !important;
}
.stButton>button {
    color: #10a37f !important;
    border: 1px solid #10a37f !important;
}
#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================= NAV =================
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🎯"): st.session_state.view_mode = "🎯"
with c2:
    if st.button("🧩"): st.session_state.view_mode = "🧩"
with c3:
    if st.button("📂"): st.session_state.view_mode = "📂"

st.divider()

# ================= TOOL 1 =================
if st.session_state.view_mode == "🎯":
    st.markdown("### 🎯 Candidate Matcher")

    job = st.text_input("Position", "Python Developer")
    criteria = st.text_area("Criteria", "Cloud, API, automation")

    if st.button("Analyze"):
        if not st.session_state.candidate_memory:
            st.warning("No candidates stored.")
        else:
            context = json.dumps(st.session_state.candidate_memory, indent=2)
            prompt = f"""
You are an HR expert.
Rank candidates for the position {job}.
Criteria: {criteria}.
Candidates: {context}
"""
            result = generate(prompt)
            st.markdown(f"<div class='chat-bubble'>{result}</div>", unsafe_allow_html=True)

# ================= TOOL 2 =================
elif st.session_state.view_mode == "🧩":
    st.markdown("### 🧩 Smart CV Extractor")

    raw_text = st.text_area("Paste CV text", height=250)

    if st.button("Extract"):
        if raw_text.strip():
            prompt = f"""
Extract CV data into JSON with fields:
name, applying_for, technical_skills, soft_skills, experience, summary.
Use "N/A" if missing.
Text:
{raw_text}
"""
            output = generate(prompt)

            try:
                start, end = output.find("{"), output.rfind("}") + 1
                data = json.loads(output[start:end])
                st.session_state.candidate_memory.append(data)
                st.success("Candidate saved successfully")
                st.json(data)
            except Exception as e:
                st.error("Extraction failed")

# ================= TOOL 3 =================
elif st.session_state.view_mode == "📂":
    st.markdown("### 📂 Session Records")

    if st.session_state.candidate_memory:
        st.dataframe(pd.DataFrame(st.session_state.candidate_memory))
        if st.button("Clear Memory"):
            st.session_state.candidate_memory = []
            st.rerun()
    else:
        st.info("No records found.")
