from fastapi import FastAPI
from src.pipeline import query_rag

app = FastAPI()

@app.get("/")
def home():
    return {"status": "RAG API is running"}

@app.get("/ask")
def ask(question: str):
    # This calls the function in pipeline.py
    answer, sources = query_rag(question)
    return {"answer": answer, "sources": sources}