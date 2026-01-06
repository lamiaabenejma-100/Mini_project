# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model_handler import generate_from_llama, extract_json_from_text, validate_sql    # les focntions des autres 

# --- FastAPI App ---
app = FastAPI()

# --- Domain-Specific Assistant Route ---
class AssistantRequest(BaseModel):
    user_message: str

@app.post("/assistant")
async def assistant(request: AssistantRequest):
    """This route is the domain-specific assistant"""
    user_message = request.user_message
    prompt = f"Answer this question based on your knowledge: {user_message}"
    
    # Generate model response
    response = generate_from_llama(prompt)
    
    # Return the assistant's response
    return {"response": response}

# --- Structured Output Generator Route ---
class StructuredOutputRequest(BaseModel):
    raw_text: str

@app.post("/generate-structured-output")
async def generate_structured_output(request: StructuredOutputRequest):
    """This route generates structured output (JSON) from raw text"""
    raw_text = request.raw_text
    
    try:
        # Extract structured data from the raw text
        structured_output = extract_json_from_text(raw_text)
        return {"json": structured_output}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# --- Model Evaluation Route ---
class EvaluationRequest(BaseModel):
    input_text: str
    expected_output: str

@app.post("/evaluate-model")
async def evaluate_model(request: EvaluationRequest):
    """This route evaluates the model's response against an expected output"""
    input_text = request.input_text
    expected_output = request.expected_output
    
    # Generate the model's output
    generated_output = generate_from_llama(input_text)
    
    # Perform a simple evaluation (you can expand this to use a more complex evaluation metric)
    is_correct = (generated_output.strip() == expected_output.strip())
    
    return {"generated_output": generated_output, "is_correct": is_correct}
