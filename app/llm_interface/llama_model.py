# app/llm_interface/llama_model.py

import requests
import json

def run_llm(prompt: str):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt},
        stream=True
    )

    full_response = ""
    for line in response.iter_lines():
        if line:
            try:
                chunk = json.loads(line.decode())
                full_response += chunk.get("response", "")
            except Exception as e:
                print("Error parsing chunk:", e)
    return full_response.strip()
