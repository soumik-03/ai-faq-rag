import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parent / "chroma_db")

hf_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="faq_collection", embedding_function=hf_ef)

sample_faq = [
    "The secret office code is 998877.",
    "The return policy is 14 days.",
    "Office location: 123 Tech Lane."
]

ids = [f"id_{i}" for i in range(len(sample_faq))]
collection.add(documents=sample_faq, ids=ids)
print(f"✅ Success! Database created at {DB_PATH}")