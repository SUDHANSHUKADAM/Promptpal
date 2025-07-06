from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.llm_interface.llama_model import run_llm as chat_with_llm
from app.prompt_optimizer import optimize_prompt
from app.rag_pipeline.retriever import get_relevant_docs
from app.storage.logger import log_prompt_interaction, update_feedback

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str
    intent: str

class FeedbackRequest(BaseModel):
    prompt_id: int
    feedback: str

# 📩 Feedback submission route
@router.post("/submit_feedback")
def submit_feedback(req: FeedbackRequest):
    try:
        update_feedback(req.prompt_id, req.feedback)
        return {"message": "Feedback submitted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


# 🧠 Main unified route
@router.post("/unified_chat")
def unified_chat(req: ChatRequest):
    prompt = req.prompt
    intent = req.intent
    optimized_prompt = None
    original_response = None
    optimized_response = None
    sources = []

    try:
        # 1️⃣ Prompt Improvement
        if intent == "prompt_improvement":
            result = optimize_prompt(prompt)
            optimized_prompt = result.get("optimized_prompt", "")
            
            # ✅ For internal evaluation: get both responses
            original_response = chat_with_llm(prompt)
            optimized_response = chat_with_llm(optimized_prompt)

            # ✅ Only return optimized response to frontend
            response_payload = {
                "original_prompt": prompt,
                "optimized_prompt": optimized_prompt,
                "optimized_response": optimized_response,
                "sources": [],
                "feedback": None
            }

        # 2️⃣ RAG: Ask from Docs
        elif intent == "ask_doc":
            docs = get_relevant_docs(prompt)
            sources = sorted(docs, key=lambda x: x["score"], reverse=True)[:3]
            context = "\n\n".join([doc["content"] for doc in sources])
            optimized_prompt = f"Answer the question using the following context:\n{context}\n\nQuestion: {prompt}"
            optimized_response = chat_with_llm(optimized_prompt)

            response_payload = {
                "original_prompt": prompt,
                "optimized_prompt": optimized_prompt,
                "optimized_response": optimized_response,
                "sources": sources,
                "feedback": None
            }

        # 3️⃣ General Chat
        elif intent == "general_chat":
            optimized_response = chat_with_llm(prompt)
            response_payload = {
                "original_prompt": prompt,
                "optimized_prompt": None,
                "optimized_response": optimized_response,
                "sources": [],
                "feedback": None
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid intent")

        # ✅ Log the interaction for all intents
        log_prompt_interaction(
            intent=str(intent),
            original_prompt=str(prompt),
            optimized_prompt=str(optimized_prompt) if optimized_prompt else None,
            original_response=str(original_response) if original_response else None,
            optimized_response=str(optimized_response) if optimized_response else None,
            feedback=None
        )

        return response_payload

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




