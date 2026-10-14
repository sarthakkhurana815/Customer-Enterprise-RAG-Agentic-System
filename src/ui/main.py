import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
st.set_page_config(page_title="Customer Support Assistant", page_icon="💬")
st.title("Customer Support Knowledge Assistant")
st.caption("Demo uses synthetic support policies and FAQs. Do not enter personal or confidential data.")

if "session_id" not in st.session_state:
    st.session_state.session_id = "demo-session"
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption("Sources: " + ", ".join(msg["sources"]))

question = st.chat_input("Ask about orders, refunds, delivery, or account support...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    try:
        response = requests.post(
            f"{API_BASE}/query",
            json={"query": question, "session_id": st.session_state.session_id},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        answer = data.get("answer", "No answer returned.")
        sources = data.get("sources", [])
        with st.chat_message("assistant"):
            st.markdown(answer)
            st.caption(f"Intent: {data.get('intent')} | Sentiment: {data.get('sentiment')} | Escalation: {data.get('needs_escalation')}")
            if sources:
                st.caption("Sources: " + ", ".join(sources))
            with st.expander("Retrieved context and agent trace"):
                st.json({"evidence": data.get("evidence", []), "trace": data.get("trace", [])})
        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
        with st.expander("Rate this answer"):
            rating = st.slider("Rating", 1, 5, 4, key=f"rating_{len(st.session_state.messages)}")
            comment = st.text_input("Optional correction/comment", key=f"comment_{len(st.session_state.messages)}")
            if st.button("Submit feedback", key=f"feedback_{len(st.session_state.messages)}"):
                fb = requests.post(f"{API_BASE}/feedback", json={
                    "session_id": st.session_state.session_id,
                    "rating": rating, "comment": comment, "query": question
                }, timeout=20)
                st.success("Feedback submitted." if fb.ok else "Could not submit feedback.")
    except requests.RequestException as exc:
        st.error(f"API request failed. Is FastAPI running? Details: {exc}")
