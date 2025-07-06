from fastapi import FastAPI, UploadFile, Form, HTTPException
from pydantic import BaseModel
from app.chatbot import generate_response
from app.prompt_optimizer import optimize_prompt
from app.rag_pipeline.doc_ingestion import load_document, chunk_documents
from app.rag_pipeline.retriever import embed_and_store, load_vectorstore
from app.llm_interface.llama_model import run_llm
from app.storage.logger import log_prompt_interaction, update_feedback
import os
from app.routes import unified_chat 
print("✅ unified_chat router imported successfully") # ✅ Phase 5 router import



app = FastAPI()
app.include_router(unified_chat.router) 
print("✅ unified_chat router registered to FastAPI")
 # ✅ Register unified_chat route

# ----------------- Schemas -----------------

class PromptInput(BaseModel):
    prompt: str

class OptimizedPromptResponse(BaseModel):
    original_prompt: str
    intent: str
    optimized_prompt: str

class ComparisonResponse(BaseModel):
    original_prompt: str
    optimized_prompt: str
    original_response: str
    optimized_response: str
    intent: str

class FeedbackRequest(BaseModel):
    prompt_id: int
    feedback: str  # e.g., "up", "down", "5 stars"

# ----------------- Existing Endpoints -----------------

@app.post("/chat")
def chat_with_bot(user_input: PromptInput):
    response = generate_response(user_input.prompt)
    return {"response": response}

@app.post("/optimize_prompt", response_model=OptimizedPromptResponse)
def rewrite_prompt(user_input: PromptInput):
    result = optimize_prompt(user_input.prompt)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result)

    log_prompt_interaction(
        intent=result["intent"],
        original_prompt=user_input.prompt,
        optimized_prompt=result["optimized_prompt"]
    )
    return result

@app.post("/optimize_and_compare", response_model=ComparisonResponse)
def optimize_and_compare(user_input: PromptInput):
    try:
        result = optimize_prompt(user_input.prompt)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result)

        original_response = run_llm(user_input.prompt)
        optimized_response = run_llm(result["optimized_prompt"])

        log_prompt_interaction(
            intent=result["intent"],
            original_prompt=user_input.prompt,
            optimized_prompt=result["optimized_prompt"],
            original_response=original_response,
            optimized_response=optimized_response
        )

        return {
            "original_prompt": user_input.prompt,
            "optimized_prompt": result["optimized_prompt"],
            "original_response": original_response,
            "optimized_response": optimized_response,
            "intent": result["intent"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- New Feedback Endpoint -----------------

@app.post("/feedback")
def submit_feedback(feedback: FeedbackRequest):
    try:
        update_feedback(feedback.prompt_id, feedback.feedback)
        return {"message": f"Feedback saved for prompt ID {feedback.prompt_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- Phase 3 Endpoints -----------------

@app.post("/upload")
async def upload_file(file: UploadFile):
    os.makedirs("temp", exist_ok=True)
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    ext = file.filename.split(".")[-1].lower()
    try:
        docs = load_document(file_path, ext)
        chunks = chunk_documents(docs)
        embed_and_store(chunks)
        return {"status": "Document uploaded and indexed successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/ask")
async def ask_question(question: str = Form(...)):
    try:
        db = load_vectorstore()
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        docs = retriever.get_relevant_documents(question)

        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = f"Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {question}"

        answer = run_llm(prompt)
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}


