# model_loader.py
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from dotenv import load_dotenv
from pathlib import Path

# ===== LOAD .env SAFELY =====
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
MODEL_NAME = "meta-llama/Llama-3.2-1B-Instruct"

_tokenizer = None
_model = None

def load_model():
    global _tokenizer, _model

    if not HF_TOKEN:
        return None, None   # ❌ Pas de crash, juste message d'erreur

    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            token=HF_TOKEN
        )
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            torch_dtype=torch.float16,
            token=HF_TOKEN,
            low_cpu_mem_usage=True
        )

    return _tokenizer, _model

def generate(prompt: str, max_new_tokens: int = 500) -> str:
    tokenizer, model = load_model()
    if model is None:
        return "ERROR: Model not loaded. Check HF_TOKEN."

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
