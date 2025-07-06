# app/chatbot.py

import requests

def generate_response(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False  # get full response at once
        }
    )

    if response.status_code == 200:
        return response.json()["response"].strip()
    else:
        return f"Error from Ollama API: {response.status_code} - {response.text}"


