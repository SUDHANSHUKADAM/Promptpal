# app/prompt_optimizer/optimizer.py

import requests

# Intent-specific templates
PROMPT_TEMPLATES = {
    "data_analysis": """
You are a skilled data analyst.
Rewrite the following user prompt to be more precise and insightful for an LLM performing data analysis.

Original Prompt:
"{prompt}"

Improved Prompt:
""",
    "email_writing": """
You are an expert email writer.
Rephrase the following prompt to make it concise, polite, and professional.

Original Prompt:
"{prompt}"

Improved Prompt:
""",
    "code_debugging": """
You are a seasoned software engineer.
Reword the following prompt to clarify debugging intent and provide helpful context for better code support.

Original Prompt:
"{prompt}"

Improved Prompt:
""",
    "resume_optimization": """
You are a resume expert.
Rewrite the following prompt to maximize impact, clarity, and professional tone for resume enhancement.

Original Prompt:
"{prompt}"

Improved Prompt:
""",
    "general": """
You are a helpful AI assistant and expert in prompt engineering.
Rewrite the following user prompt to make it more clear, specific, and effective.

Original Prompt:
"{prompt}"

Improved Prompt:
"""
}

def classify_prompt_intent(prompt: str) -> str:
    prompt = prompt.lower()
    if any(word in prompt for word in ["analyze", "plot", "visualize", "data", "insight"]):
        return "data_analysis"
    elif any(word in prompt for word in ["email", "write to", "compose", "reply"]):
        return "email_writing"
    elif any(word in prompt for word in ["debug", "fix", "error", "bug", "issue"]):
        return "code_debugging"
    elif any(word in prompt for word in ["resume", "cv", "cover letter", "job application"]):
        return "resume_optimization"
    else:
        return "general"

def optimize_prompt(prompt: str) -> dict:
    intent = classify_prompt_intent(prompt)
    template = PROMPT_TEMPLATES[intent]
    full_prompt = template.format(prompt=prompt)

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": full_prompt,
            "stream": False
        }
    )

    if response.status_code == 200:
        improved_prompt = response.json()["response"].strip()
        return {
            "original_prompt": prompt,
            "intent": intent,
            "optimized_prompt": improved_prompt
        }
    else:
        return {
            "error": f"Error from Ollama API: {response.status_code}",
            "details": response.text
        }
