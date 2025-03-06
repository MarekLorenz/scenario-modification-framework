import json
import requests
import os
from dotenv import load_dotenv

OLLAMA_BASE_URL = "http://localhost:11434"

def send_local_llama_request(system_prompt, user_prompt):
    url = f"{OLLAMA_BASE_URL}/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "llama3.2:latest",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "stream": False
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()['message']['content']