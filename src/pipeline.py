import os
import requests
import chromadb
import platform
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

# 1. SMART PATH LOGIC
if platform.system() == "Windows":
    DB_PATH = "C:/Users/Public/rag_db"
else:
    DB_PATH = "/app/chroma_db"

# 2. Setup Database
hf_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client_db = chromadb.PersistentClient(path=DB_PATH)
collection = client_db.get_or_create_collection(name="faq_collection", embedding_function=hf_ef)

# --- DOCKER SELF-HEAL ---
# If the database is empty, fill it automatically
if collection.count() == 0:
    print("⚠️ Database empty! Automatically ingesting sample data...")
    sample_data = [
        "The secret office code is 998877.",
        "The return policy for opened items is 14 days exactly.",
        "Our support lead is named Alex AI."
    ]
    ids = [f"id_{i}" for i in range(len(sample_data))]
    collection.add(documents=sample_data, ids=ids)
# ------------------------

def query_rag(question):
    # 1. Retrieval
    results = collection.query(query_texts=[question], n_results=2)
    context = " ".join(results['documents'][0])
    ids = results['ids'][0]
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    # 2. THE ULTIMATE MODEL FALLBACK LOOP
    # We try 3 different ways to call Gemini until one works.
    models_to_try = [
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent",
        
    ]
    
    last_error = ""
    for url_base in models_to_try:
        url = f"{url_base}?key={api_key}"
        payload = {"contents": [{"parts": [{"text": f"Context: {context}\n\nQuestion: {question}"}]}]}
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            if 'candidates' in result:
                answer = result['candidates'][0]['content']['parts'][0]['text']
                return answer, ids
            else:
                last_error = result.get('error', {}).get('message', str(result))
        except Exception as e:
            last_error = str(e)
            continue
            
    return f"Google API Error after 3 attempts: {last_error}", ids