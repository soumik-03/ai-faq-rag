from src.pipeline import query_rag
import os
from dotenv import load_dotenv

load_dotenv()

print("--- Testing Pipeline ---")
try:
    # 1. Check if key is loaded
    key = os.getenv("GEMINI_API_KEY")
    print(f"Key loaded: {key[:5]}..." if key else "Key NOT found!")

    # 2. Try the query
    ans, src = query_rag("Where is the office?")
    print(f"✅ Success!")
    print(f"Answer: {ans}")
except Exception as e:
    print("❌ CRASHED!")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()