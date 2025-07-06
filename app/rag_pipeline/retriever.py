import os
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

# Embed and store documents into FAISS index
def embed_and_store(docs, index_path="faiss_index"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(index_path)
    return db

# Load FAISS vectorstore
def load_vectorstore(index_path="faiss_index"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

# Get top-k relevant chunks with scores and metadata
def get_relevant_docs(query, k=3, index_path="faiss_index"):
    db = load_vectorstore(index_path)
    results_with_scores = db.similarity_search_with_score(query, k=k)

    # Convert result into a dict with content, score, and metadata
    processed = []
    for doc, score in results_with_scores:
        processed.append({
            "content": doc.page_content,
            "score": score,
            "metadata": doc.metadata  # includes things like 'source', 'page'
        })

    return processed
