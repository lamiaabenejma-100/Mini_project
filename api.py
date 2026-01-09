from fastapi import FastAPI
from pydantic import BaseModel
from model_loader import generate
import json

app = FastAPI(title="AI HR Assistant API")

# -------- REQUEST MODEL --------
class AIRequest(BaseModel):
    text: str
    task: str  # "extract" or "analyze"

# -------- HEALTH CHECK --------
@app.get("/")
def home():
    return {"status": "API running successfully"}

# -------- MAIN AI ENDPOINT --------
@app.post("/ai")
def ai_handler(data: AIRequest):

    # ===== CV EXTRACTION =====
    if data.task == "extract":
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an AI HR assistant.
Extract information from the resume text.
Return ONLY valid JSON. No markdown. No explanation.

JSON FORMAT:
{{
  "name": "",
  "applying_for": "",
  "technical_skills": [],
  "soft_skills": [],
  "experience": "",
  "summary": ""
}}

<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{data.text}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""
        raw_output = generate(prompt)

        try:
            clean = raw_output.replace("```json", "").replace("```", "").strip()
            start = clean.find("{")
            end = clean.rfind("}") + 1
            return json.loads(clean[start:end])
        except:
            return {"error": "Model failed to return valid JSON"}

    # ===== MATCHING / ANALYSIS =====
    elif data.task == "analyze":
        result = generate(data.text)
        return {"result": result}

    # ===== INVALID TASK =====
    else:
        return {"error": "Invalid task type"}
