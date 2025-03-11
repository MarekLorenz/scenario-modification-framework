import json
import requests

OLLAMA_BASE_URL = "http://localhost:11434"

def send_local_llama_request(system_prompt, user_prompt, **kwargs):
    url = f"{OLLAMA_BASE_URL}/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "llama3.2:latest",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "stream": False,
        **kwargs
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()['message']['content']


def send_local_deepseek_request(system_prompt, user_prompt, **kwargs):
    url = f"{OLLAMA_BASE_URL}/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "deepseek-r1:latest",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "stream": False,
        **kwargs
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()['message']['content']
