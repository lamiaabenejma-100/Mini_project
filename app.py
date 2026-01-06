
# app.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
import re

# --- Private HF token ---
HF_TOKEN = os.getenv("HF_TOKEN") 

# --- FastAPI App ---
app = FastAPI()

# --- Cached Model Loading ---
def load_model(model_name="meta-llama/Llama-3.2-1B-Instruct"):
    """Load model once and keep in memory to prevent crashes"""
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=HF_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.float16,
        token=HF_TOKEN
    )
    return tokenizer, model

# --- Helper for SQL validation ---
def validate_sql(sql, schema):
    schema_cols = set(re.findall(r"\b(\w+)\b", schema.lower()))
    sql_tokens = set(re.findall(r"\b(\w+)\b", sql.lower()))
    sql_keywords = {
        "select", "from", "where", "join", "on", "group", "by",
        "order", "having", "avg", "sum", "count", "min", "max",
        "and", "or", "as", "distinct", "limit", "desc", "asc"
    }
    invalid = [tok for tok in sql_tokens if tok not in sql_keywords and tok not in schema_cols]
    return invalid

# --- Generate output from LLaMA ---
def generate_from_llama(prompt, max_tokens=150):
    tokenizer, model = load_model()
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=max_tokens, temperature=0.1)
    
    decoded = tokenizer.decode(out[0], skip_special_tokens=True)
    return decoded

# --- API Route for SQL Generation ---
class SQLRequest(BaseModel):
    schema: str
    query: str

@app.post("/generate-sql")
async def generate_sql(request: SQLRequest):
    full_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a SQL generator. Return ONLY the SQL query. No explanation.<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Schema: {request.schema}
Request: {request.query}
SQL:<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>"""
    
    raw_output = generate_from_llama(full_prompt)
    
    # ISOLATION: Remove prompt and conversational fluff
    sql_output = raw_output.split("assistant")[-1].strip()
    sql_output = sql_output.replace("```sql", "").replace("```", "").strip()

    invalid = validate_sql(sql_output, request.schema)
    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid SQL: {invalid}")
    
    return {"sql": sql_output}

# --- API Route for JSON Extraction ---
class JSONRequest(BaseModel):
    raw_text: str

@app.post("/extract-json")
async def extract_json(request: JSONRequest):
    json_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Extract JSON with fields: name, age, job. Return ONLY JSON.<|eot_id|> 
<|start_header_id|>user<|end_header_id|>
{request.raw_text}<|end_header_id|>
<|start_header_id|>assistant<|end_header_id|>"""
    
    raw_output = generate_from_llama(json_prompt)
    
    json_part = raw_output.split("assistant")[-1].strip()
    try:
        start = json_part.find('{')
        end = json_part.rfind('}') + 1
        json_data = json.loads(json_part[start:end])
        return {"json": json_data}
    except:
        raise HTTPException(status_code=400, detail="Model did not return valid JSON.")
