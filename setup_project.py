import os
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 1. Setup the Embedding Model (Hugging Face)
# This runs locally on your computer!
hf_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# 2. Setup Vector Database (ChromaDB)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="faq_collection", embedding_function=hf_ef)

# 3. Setup the LLM (Using Groq - The free provider)
llm_client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.groq.com/openai/v1" # Change to Groq
)

def add_documents(text_list):
    """Add your documents to the vector database"""
    # We create simple IDs like 'id1', 'id2'
    ids = [f"id{i}" for i in range(len(text_list))]
    collection.add(documents=text_list, ids=ids)
    print(f"Added {len(text_list)} chunks to the database.")

def query_rag(question):
    """Search for context and then ask the AI"""
    # Search for the top 2 most relevant chunks
    results = collection.query(query_texts=[question], n_results=2)
    context = " ".join(results['documents'][0])
    
    # Send to the LLM
    response = llm_client.chat.completions.create(
        model="llama-3.1-8b-instant", # This is a fast, free Groq model
        messages=[
            {"role": "system", "content": f"You are a helpful assistant. Use ONLY this context to answer: {context}"},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content, results['ids'][0]