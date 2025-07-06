import streamlit as st
import requests

API_UPLOAD = "http://127.0.0.1:8000/upload"
API_ASK = "http://127.0.0.1:8000/ask"
API_UNIFIED_CHAT = "http://127.0.0.1:8000/unified_chat"

st.title("🤖 PromptPal Assistant")

# Select intent
intent = st.selectbox("Select Intent:", ["general_chat", "prompt_improvement", "ask_doc"])

# Upload document if intent is ask_doc
uploaded_file = None
if intent == "ask_doc":
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")
        if st.button("📤 Upload File to Vector DB"):
            with st.spinner("Uploading and processing file..."):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                res = requests.post(API_UPLOAD, files=files)
                if res.status_code == 200:
                    st.success("File uploaded and processed successfully.")
                else:
                    st.error(f"Upload failed: {res.text}")

# Prompt input
prompt = st.text_area("Enter your prompt/question:", height=200)

# Submit button
if st.button("🚀 Submit"):
    if intent == "ask_doc":
        if not uploaded_file:
            st.warning("Please upload a document first.")
        else:
            with st.spinner("Searching in document and generating answer..."):
                res = requests.post(API_ASK, data={"question": prompt})
                if res.status_code == 200:
                    st.subheader("📄 Answer from Document")
                    st.write(res.json().get("answer", "No answer found."))
                else:
                    st.error(f"Error: {res.text}")
    else:
        with st.spinner("Calling PromptPal..."):
            res = requests.post(API_UNIFIED_CHAT, json={"prompt": prompt, "intent": intent})
            if res.status_code == 200:
                data = res.json()

                # ✅ Show optimized prompt only for prompt_improvement or ask_doc
                if intent in ["prompt_improvement", "ask_doc"] and data.get("optimized_prompt"):
                    st.subheader("🎯 Optimized Prompt")
                    st.code(data["optimized_prompt"], language="markdown")

                # ✅ Always show optimized response (final answer)
                if data.get("optimized_response"):
                    st.subheader("🚀 Response")
                    st.write(data["optimized_response"])

                # ✅ Show sources if available
                if data.get("sources"):
                    st.subheader("📚 Sources")
                    for src in data["sources"]:
                        st.markdown(f"- {src}")
            else:
                st.error(f"Error: {res.text}")


