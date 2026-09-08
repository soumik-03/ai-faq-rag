import streamlit as st
import os
from src.pipeline import query_rag, add_documents

# Page Config
st.set_page_config(page_title="AI FAQ Assistant", page_icon="🤖")

st.title("🤖 AI FAQ RAG Assistant")
st.markdown("I answer questions based on your custom database using Gemini 3.5 Flash lite.")

# --- SIDEBAR: Database Management ---
with st.sidebar:
    st.header("Database Info")
    if st.button("🔄 Refresh/Initialize Database"):
        with st.spinner("Ingesting data..."):
            sample_faq = [
                "The secret office code is 998877.",
                "The return policy for opened items is 14 days exactly.",
                "Our support lead is named Alex AI.",
                "The office is located at 123 Tech Lane, Silicon Valley."
            ]
            add_documents(sample_faq)
            st.success("Database Loaded!")

# --- MAIN CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask me something..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Searching database & thinking..."):
            answer, sources = query_rag(prompt)
            st.markdown(answer)
            if sources:
                st.caption(f"Sources found: {', '.join(sources)}")
    
    st.session_state.messages.append({"role": "assistant", "content": answer})