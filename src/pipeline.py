import os
import requests
import chromadb

from pathlib import Path
from chromadb.utils import embedding_functions
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = str(
    BASE_DIR / "chroma_db"
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

hf_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


# ============================================================
# CHROMADB
# ============================================================

client_db = chromadb.PersistentClient(
    path=DB_PATH
)


collection = client_db.get_or_create_collection(
    name="faq_collection",
    embedding_function=hf_ef
)


# ============================================================
# ADD DOCUMENTS
# ============================================================

def add_documents(text_list):

    if not text_list:
        return

    ids = [
        f"faq_{i}_{os.urandom(2).hex()}"
        for i in range(len(text_list))
    ]

    collection.add(
        documents=text_list,
        ids=ids
    )

    print(
        f"Successfully added "
        f"{len(text_list)} documents."
    )


# ============================================================
# QUERY RAG
# ============================================================

def query_rag(question):

    # --------------------------------------------------------
    # DATABASE CHECK
    # --------------------------------------------------------

    count = collection.count()

    if count == 0:

        return (
            "The FAQ database is currently empty. "
            "Please initialize the dataset first.",
            []
        )


    # --------------------------------------------------------
    # SEMANTIC SEARCH
    # --------------------------------------------------------

    results = collection.query(
        query_texts=[question],
        n_results=min(3, count),
        include=[
            "documents",
            "distances"
        ]
    )


    # --------------------------------------------------------
    # RESULT VALIDATION
    # --------------------------------------------------------

    if (
        not results.get("documents")
        or not results["documents"][0]
    ):

        return (
            "I couldn't find that information "
            "in the FAQ dataset.",
            []
        )


    documents = results["documents"][0]

    ids = results["ids"][0]

    distances = results["distances"][0]


    # --------------------------------------------------------
    # RELEVANCE CHECK
    # --------------------------------------------------------

    best_distance = distances[0]


    if best_distance > 1.0:

        return (
            "I couldn't find that information in "
            "the FAQ dataset.\n\n"
            "You can raise an enquiry using the "
            "Enquiry option.",
            []
        )


    # --------------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------------

    context_parts = []

    for index, document in enumerate(documents):

        context_parts.append(
            f"FAQ SOURCE {index + 1}:\n"
            f"{document}"
        )


    context = "\n\n".join(
        context_parts
    )


    # --------------------------------------------------------
    # GEMINI API KEY
    # --------------------------------------------------------

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )


    if not api_key:

        return (
            "Gemini API key is missing. "
            "Please check your .env file.",
            ids
        )


    # --------------------------------------------------------
    # GEMINI ENDPOINT
    # --------------------------------------------------------

    model_url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.5-flash-lite:"
        "generateContent"
    )


    url = (
        f"{model_url}?key={api_key}"
    )


    # --------------------------------------------------------
    # RAG PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are Lumen, an AI customer support assistant.

You answer questions using ONLY the information
contained in the FAQ SOURCES below.

RULES:

1. Only use information from the provided sources.
2. Never invent information.
3. Never make assumptions.
4. Never use outside knowledge.
5. If the sources do not contain enough information,
   respond exactly with:

   "I couldn't find that information in the FAQ dataset."

6. Keep answers clear and concise.
7. If multiple sources are relevant, combine them.
8. Do not claim an action was completed unless the
   source explicitly says it was completed.

FAQ SOURCES:

{context}

CUSTOMER QUESTION:

{question}

ANSWER:
"""


    # --------------------------------------------------------
    # REQUEST PAYLOAD
    # --------------------------------------------------------

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }


    # --------------------------------------------------------
    # CALL GEMINI
    # --------------------------------------------------------

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=20
        )


        result = response.json()


        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        if "candidates" in result:

            answer = (
                result["candidates"][0]
                ["content"]
                ["parts"][0]
                ["text"]
            )

            return answer, ids


        # ----------------------------------------------------
        # API ERROR
        # ----------------------------------------------------

        error_message = (
            result
            .get("error", {})
            .get(
                "message",
                str(result)
            )
        )


        return (
            f"Gemini Error: {error_message}",
            ids
        )


    # --------------------------------------------------------
    # TIMEOUT
    # --------------------------------------------------------

    except requests.exceptions.Timeout:

        return (
            "The AI service took too long to respond. "
            "Please try again.",
            ids
        )


    # --------------------------------------------------------
    # NETWORK ERROR
    # --------------------------------------------------------

    except requests.exceptions.RequestException as e:

        return (
            f"Network error while contacting Gemini: {e}",
            ids
        )


    # --------------------------------------------------------
    # OTHER ERROR
    # --------------------------------------------------------

    except Exception as e:

        return (
            f"Unexpected error: {e}",
            ids
        )