# app_streamlit.py
import streamlit as st
import json
import requests  

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
st.markdown("""...""", unsafe_allow_html=True)  

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

API_URL = "http://127.0.0.1:8000/extract-cv"  

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
                    
                    # ---------- appel à l'API ----------
                    try:
                        response = requests.post(API_URL, json={"text": match_prompt})
                        st.session_state.last_res = response.json()["result"]
                    except Exception as e:
                        st.error(f"Erreur API : {e}")
                        st.session_state.last_res = ""
        
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
                    try:
                        response = requests.post(API_URL, json={"text": raw_text})
                        raw_output = response.json()["result"]
                    except Exception as e:
                        st.error(f"Erreur API : {e}")
                        raw_output = ""
                    
                    # Nettoyage JSON
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
