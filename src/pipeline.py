import os
import requests
import chromadb
import platform
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

# 1. SMART PATH LOGIC (Same as before)
if platform.system() == "Windows":
    DB_PATH = "C:/Users/Public/rag_db"
else:
    DB_PATH = "./chroma_db"

# 2. Setup Database
hf_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client_db = chromadb.PersistentClient(path=DB_PATH)
collection = client_db.get_or_create_collection(name="faq_collection", embedding_function=hf_ef)

def add_documents(text_list):
    """THIS IS THE FUNCTION THAT WAS MISSING"""
    import os as py_os
    # Generate unique IDs for each chunk
    ids = [f"id{i}_{py_os.urandom(2).hex()}" for i in range(len(text_list))]
    collection.add(documents=text_list, ids=ids)
    print(f"✅ Successfully added {len(text_list)} items to the database.")

def query_rag(question):
    """The 'Invincible' Query Logic with Fallbacks"""
    results = collection.query(query_texts=[question], n_results=2)
    
    if not results['documents'] or not results['documents'][0]:
        return "Database is empty! Use the sidebar to refresh it.", []

    context = " ".join(results['documents'][0])
    ids = results['ids'][0]
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Try multiple endpoints in case one is overloaded
    models_to_try = [
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent",
    ]
    
    last_error = ""
    for url_base in models_to_try:
        url = f"{url_base}?key={api_key}"
        payload = {"contents": [{"parts": [{"text": f"Context: {context}\n\nQuestion: {question}\n\nAnswer concisely:"}]}]}
        
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
            
    return f"Gemini Error: {last_error}", ids