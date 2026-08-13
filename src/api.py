import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

# Ensure 'src' is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.knowledge_base import build_knowledge_base
from src.pipeline import get_llm, ask_question

app = FastAPI(title="Q&A Chatbot API")

# Global variables to hold our model and vector store
vector_store = None
llm = None

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    answer: str
    sources: List[str]

@app.on_event("startup")
def load_models():
    global vector_store, llm
    print("Initializing models...")
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    if not os.path.isdir(data_dir):
        raise RuntimeError(f"Data directory not found at {data_dir}")
    
    vector_store = build_knowledge_base(data_dir)
    llm = get_llm()
    print("Models initialized successfully!")

@app.post("/ask", response_model=QuestionResponse)
def ask(req: QuestionRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if vector_store is None or llm is None:
        raise HTTPException(status_code=500, detail="Models are not loaded yet")
    
    try:
        result = ask_question(vector_store, llm, req.question)
        return QuestionResponse(answer=result["answer"], sources=result["sources"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
