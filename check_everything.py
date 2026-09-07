import os
import requests
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("--- 1. Testing Database ---")
hf_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="faq_collection", embedding_function=hf_ef)

count = collection.count()
print(f"Database contains {count} items.")
if count == 0:
    print("❌ ERROR: Database is empty! Run 'python ingest_data.py' first.")

print("\n--- 2. Finding Your Model Name ---")
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(list_url)
data = response.json()

if 'models' in data:
    # Filter for models that support generating content
    valid_models = [m['name'] for m in data['models'] if 'generateContent' in m['supportedMethods']]
    print("Your account supports these models:")
    for m in valid_models:
        print(f" - {m}")
else:
    print(f"❌ Error listing models: {data}")