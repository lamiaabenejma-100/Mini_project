# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from model_loader import generate

app = FastAPI(title="AI HR Assistant API")

class CVRequest(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status":"API running successfully"}

@app.post("/extract-cv")
def extract_cv(data: CVRequest):
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Extract info into EXACT JSON format.

EXAMPLE:
Input: "Alex Rivera, Python Dev with 3 years at Tesla."
Output: {{
  "name": "Alex Rivera",
  "applying_for": "Python Developer",
  "technical_skills": ["Python"],
  "soft_skills": [],
  "experience": "3 years",
  "summary": "3 years at Tesla."
}}

Now extract this:
<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{data.text}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""
    result = generate(prompt)
    return {"result": result}

