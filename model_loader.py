import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from dotenv import load_dotenv
from pathlib import Path

# ================= FORCE LOAD .env =================
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)

HF_TOKEN = os.getenv("HF_TOKEN")

print("DEBUG HF_TOKEN:", "FOUND" if HF_TOKEN else "NOT FOUND")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN n'est pas défini dans l'environnement")

MODEL_NAME = "meta-llama/Llama-3.2-1B-Instruct"

tokenizer = None
model = None

def load_model():
    global tokenizer, model
    if model is None:
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            token=HF_TOKEN
        )
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            torch_dtype=torch.float16,
            token=HF_TOKEN,
            low_cpu_mem_usage=True
        )
    return tokenizer, model

def generate(prompt, max_new_tokens=500):
    tokenizer, model = load_model()
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.1
        )

    return tokenizer.decode(
        output[0][inputs.input_ids.shape[1]:],
        skip_special_tokens=True
    )
