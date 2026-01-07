# app_streamlit.py
import streamlit as st
import json
import pandas as pd
from model_loader import generate

# ================= SESSION =================
if "candidate_memory" not in st.session_state:
    st.session_state.candidate_memory = []
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "🎯"
if "last_res" not in st.session_state:
    st.session_state.last_res = ""

# ================= PAGE =================
st.set_page_config(page_title="llamaHR", layout="wide")

# ================= STYLING =================
st.markdown("""
<style>
/* App Background */
.stApp { background-color: #0E0E10; color: #E3E3E3; }
/* Header Title */
.title-area { display:flex; justify-content:center; align-items:center; gap:12px; margin-top:2vh; margin-bottom:10px; }
.llama-title { font-size:32px; font-weight:700; color:#FFFFFF; letter-spacing:-1px; }
/* Response Box */
.response-box { background-color:#1E1E20; border-radius:12px; padding:20px; border:1px solid #333; height:32vh; overflow-y:auto; margin-top:10px; }
/* Inputs */
.stTextArea textarea, .stTextInput input { background-color:#1E1E20 !important; color:white !important; border:none !important; border-radius:12px !important; padding:15px !important; box-shadow:0 4px 15px rgba(0,0,0,0.3) !important; transition:0.3s; }
.stTextArea textarea:focus, .stTextInput input:focus { outline:none !important; box-shadow:0 0 20px rgba(255,255,255,0.1) !important; }
/* Hover effect */
.stTextArea textarea:hover, .stTextInput input:hover { box-shadow:0 4px 25px rgba(255,255,255,0.05) !important; }
/* Buttons */
.stButton>button { color:#10a37f !important; border:1px solid #10a37f !important; transition:0.2s; }
.stButton>button:hover { transform:scale(1.05); }
/* DataFrame */
[data-testid="stDataFrame"] { background-color:#1E1E20; border-radius:12px; }
/* Hide default Streamlit UI */
#MainMenu, footer, header { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown('<div class="title-area"><span style="font-size:35px;">🦙</span><div class="llama-title">llamaHR</div></div>', unsafe_allow_html=True)

# ================= NAVIGATION =================
_, n1, n2, n3, _ = st.columns([2.2,0.4,0.4,0.4,2.2])
with n1: 
    if st.button(":material/search:", key="nav1"): st.session_state.view_mode = "🎯"
with n2: 
    if st.button(":material/auto_awesome:", key="nav2"): st.session_state.view_mode = "🧩"
with n3: 
    if st.button(":material/database:", key="nav3"): st.session_state.view_mode = "📂"

st.divider()
content_col = st.columns([0.15,1,0.15])[1]

with content_col:
    # --- MATCHER 🎯 ---
    if st.session_state.view_mode == "🎯":
        target_job = st.text_input("", placeholder="Position Title (e.g. Python Developer)")
        criteria = st.text_area("", placeholder="Hiring Criteria...", height=100)

        # Action button with arrow
        cols = st.columns([0.9, 0.1])
        with cols[1]:
            if st.button(":material/arrow_forward:", key="run_match"):
                db = [c for c in st.session_state.candidate_memory if target_job.lower() in str(c.get("applying_for","")).lower()]
                if not db:
                    st.toast(f"No candidates found for {target_job}", icon="ℹ️")
                else:
                    db_context = json.dumps(db, indent=2)
                    task_type = "Rank the candidates" if len(db)>1 else "Evaluate candidate"
                    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>Professional HR. Context: {db_context}<|eot_id|><|start_header_id|>user<|end_header_id|>{task_type} for {target_job}: {criteria}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
                    res = generate(prompt)
                    st.session_state.last_res = res
        
        if st.session_state.last_res:
            st.markdown(f'<div class="response-box">{st.session_state.last_res}</div>', unsafe_allow_html=True)

    # --- EXTRACTOR 🧩 ---
    elif st.session_state.view_mode == "🧩":
        raw_text = st.text_area("", placeholder="Paste Resume/CV text here...", height=250)

        cols = st.columns([0.9,0.1])
        with cols[1]:
            if st.button(":material/arrow_forward:", key="run_extract"):
                if raw_text.strip():
                    json_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>Extract into EXACT JSON format. Input: {raw_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
                    raw_output = generate(json_prompt)
                    try:
                        clean_output = raw_output.replace("```json","").replace("```","").strip()
                        start, end = clean_output.find("{"), clean_output.rfind("}")+1
                        data = json.loads(clean_output[start:end])
                        st.session_state.candidate_memory.append(data)
                        st.toast(f"Saved {data.get('name','Candidate')}!", icon="✅")
                        st.json(data)
                    except:
                        st.error("JSON parsing error. Model output may be invalid.")

    # --- VIEW DATABASE 📂 ---
    elif st.session_state.view_mode == "📂":
        if st.session_state.candidate_memory:
            df = pd.DataFrame(st.session_state.candidate_memory)
            st.dataframe(df, use_container_width=True, height=400)
            if st.button("Purge Database", type="secondary"):
                st.session_state.candidate_memory = []
                st.rerun()
        else:
            st.markdown("<div style='text-align:center; color:#555; margin-top:50px;'>Database is currently empty.</div>", unsafe_allow_html=True)
