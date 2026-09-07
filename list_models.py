import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("--- Available Models for your API Key ---")
try:
    for m in client.models.list():
        if 'generateContent' in m.supported_methods:
            print(f"Model Name: {m.name}")
except Exception as e:
    print(f"Error: {e}")