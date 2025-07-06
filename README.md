# PromptPal: AI Agent Assistant with RAG + Prompt Tools

**PromptPal** is a conversational assistant that:
- Suggests optimized prompts for various tasks
- Uses LLaMA 3 as the LLM backend
- Incorporates a RAG pipeline using LangChain + FAISS to retrieve relevant facts from documents

## 🔧 Tech Stack
- LLaMA 3 (via HuggingFace)
- LangChain + FAISS for RAG
- FastAPI backend
- Optional: Streamlit/React frontend

## 🚀 Getting Started
1. Create virtual environment and install dependencies:
python -m venv venv
venv\Scripts\activate # or source venv/bin/activate on Unix
pip install -r requirements.txt

2. Run the app:
uvicorn app.main:app --reload


## 📂 Project Structure
See `docs/system_architecture.png` for full module flow.
