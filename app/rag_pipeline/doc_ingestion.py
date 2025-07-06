# app/rag_pipeline/doc_ingestion.py

from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_document(file_path: str, file_type: str):
    if file_type == "pdf":
        loader = PyMuPDFLoader(file_path)
    elif file_type == "txt":
        from langchain.document_loaders import TextLoader
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file type")
    return loader.load()

def chunk_documents(documents, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(documents)
