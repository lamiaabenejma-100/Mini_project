# app_streamlit.py
import streamlit as st
import json
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
html, body, [data-testid="stAppViewContainer"] {background-color:#0E0E10 !important; color:#E3E3E3 !important;}
.brand-corner {position: fixed; top: 20px; left: 30px; font-size: 14px; font-weight: 700; color:#888; letter-spacing:1.5px; z-index:1000;}
.assistant-greeting {text-align:center; font-size:36px; font-weight:300; margin-top:30px; margin-bottom:40px; color:#FFFFFF; letter-spacing:-0.5px;}
.assistant-greeting span {color:#FFA500; font-weight:600;}
div[data-testid="stHorizontalBlock"] button {height:60px !important; width:60px !important; background-color:#161618 !important; border:1px solid #222 !important; border-radius:12px !important; display:flex !important; align-items:center !important; justify-content:center !important; transition: all 0.3s ease !important;}
div[data-testid="stHorizontalBlock"] button:hover {border-color:#FFA500 !important; background-color:#1A1A1C !important; box-shadow:0 4px 20px rgba(255,165,0,0.2) !important; transform:translateY(-2px);}
.stTextArea textarea, .stTextInput input {background-color:#161618 !important; color:#FFFFFF !important; border:1px solid #222 !important; border-radius:12px !important; transition: all 0.3s ease !important;}
.stTextArea textarea:hover, .stTextInput input:hover {box-shadow:0 0 15px rgba(255,165,0,0.1) !important; border-color:#444 !important;}
.candidate-card {background-color:#161618; border-left:4px solid #333; border-radius:8px; padding:22px; margin-bottom:18px; box-shadow:0 4px 12px rgba(0,0,0,0.3); transition:0.3s;}
.candidate-card:hover {border-left-color:#FFA500; background-color:#1C1C1E; transform:translateX(5px);}
.card-header {display:flex; justify-content:space-between; align-items:center;}
.card-name {font-size:22px; font-weight:600; color:#FFF;}
.card-tag {background:#FFA500; color:#000; padding:2px 10px; border-radius:4px; font-size:11px; font-weight:800;}
.response-box {background-color:#161618; border-radius:15px; padding:30px; border:1px solid #222; margin-top:30px; color:#E3E3E3; line-height:1.6;}
#MainMenu, footer, header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ================= BRANDING =================
st.markdown('<div class="brand-corner">🦙 llamaHR</div>', unsafe_allow_html=True)
st.markdown('<div class="assistant-greeting">Hi, I am ready to help you <span>recruit</span></div>', unsafe_allow_html=True)

# ================= NAVIGATION =================
_, n1, n2, n3, _ = st.columns([2.1, 0.3, 0.3, 0.3, 2.1])
with n1: 
    if st.button(":material/search:", key="nav1"): st.session_state.view_mode = "🎯"
with n2: 
    if st.button(":material/auto_awesome:", key="nav2"): st.session_state.view_mode = "🧩"
with n3: 
    if st.button(":material/database:", key="nav3"): st.session_state.view_mode = "📂"

# ================= MAIN CONTENT =================
content_col = st.columns([0.15,1,0.15])[1]

def run_integrity_pipeline(data):
    return isinstance(data, dict) and len(data)>0, "Valid JSON" if isinstance(data, dict) else "Invalid JSON"

with content_col:
    # --- MATCHER 🎯 ---
    if st.session_state.view_mode == "🎯":
        target_job = st.text_input("", placeholder="Position Title (e.g. Python Developer)")
        criteria = st.text_area("", placeholder="Hiring Criteria...", height=120)
        cols = st.columns([0.93, 0.07])
        with cols[1]: run_btn = st.button(":material/send:", key="run_match")
        if run_btn:
            db = [c for c in st.session_state.candidate_memory if target_job.lower() in str(c.get('applying_for','')).lower()]
            if not db: st.toast(f"No candidates found for '{target_job}'", icon="ℹ️")
            else:
                with st.spinner("Analyzing..."):
                    count = len(db)
                    db_context = json.dumps(db, indent=2)
                    task_type = "Rank the candidates" if count>1 else "Evaluate single candidate"
                    match_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a professional HR assistant.
STRICT DATA LIMIT: {count} candidate(s) in DB.
CONTEXT: {db_context}<|eot_id|><|start_header_id|>user<|end_header_id|>
{task_type} for role '{target_job}' based on: {criteria}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
                    st.session_state.last_res = generate(match_prompt)
        if "last_res" in st.session_state:
            st.markdown(f'<div class="response-box">{st.session_state.last_res}</div>', unsafe_allow_html=True)

    # --- EXTRACTOR 🧩 ---
    elif st.session_state.view_mode == "🧩":
        raw_text = st.text_area("", placeholder="Paste Resume/CV text here...", height=300)
        cols = st.columns([0.93, 0.07])
        with cols[1]: extract_btn = st.button(":material/add_task:", key="run_extract")
        if extract_btn:
            if not raw_text.strip(): st.toast("Please provide text.", icon="⚠️")
            else:
                with st.spinner("Processing..."):
                    json_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Extract info into EXACT JSON format.
EXAMPLE: Output: {{ "name": "Alex", "applying_for": "Dev", "technical_skills": [], "soft_skills": [], "experience": "", "summary": "" }}
Now extract this:<|eot_id|><|start_header_id|>user<|end_header_id|>{raw_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
                    raw_output = generate(json_prompt)
                    try:
                        clean_output = raw_output.replace("```json","").replace("```","").strip()
                        start = clean_output.find('{'); end = clean_output.rfind('}')+1
                        data = json.loads(clean_output[start:end])
                        valid, msg = run_integrity_pipeline(data)
                        if valid:
                            st.session_state.candidate_memory.append(data)
                            st.success(f"Profile created for {data.get('name','Candidate')}!")
                            st.json(data)
                        else: st.error(msg)
                    except: st.error("Model failed to generate clean JSON.")

    # --- DATABASE 📂 ---
    elif st.session_state.view_mode == "📂":
        if st.session_state.candidate_memory:
            for cand in st.session_state.candidate_memory:
                st.markdown(f"""
                <div class="candidate-card">
                    <div class="card-header">
                        <span class="card-name">{cand.get('name','N/A')}</span>
                        <span class="card-tag">{cand.get('applying_for','General')}</span>
                    </div>
                    <div style="margin-top:12px; color:#AAA; font-size:14px;">
                        <b>Skills:</b> {", ".join(cand.get('technical_skills',[]))}<br>
                        <p style="margin-top:8px;">{cand.get('summary','')}</p>
                    </div>
                </div>""", unsafe_allow_html=True)
            if st.button("Clear Records", type="secondary"):
                st.session_state.candidate_memory = []
                st.rerun()
        else:
            st.markdown("<div style='text-align:center; color:#444; margin-top:80px;'>Intelligence database is empty.</div>", unsafe_allow_html=True)
