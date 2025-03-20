import json
import dotenv
import requests
import google.generativeai as genai
import os
from google.generativeai.types import GenerationConfig

OLLAMA_BASE_URL = "http://localhost:11434"

def send_local_llama_request(system_prompt, user_prompt, debug=True, **kwargs):
    url = f"{OLLAMA_BASE_URL}/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "llama3.2:latest",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "stream": False,
        **kwargs
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if debug:
        print(f"Processed tokens: {response.json()['prompt_eval_count']}")
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

def send_gemini_request(system_prompt, user_prompt, **kwargs) -> str:
    dotenv.load_dotenv()
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    model = genai.GenerativeModel("gemini-2.0-flash")
    generation_config = GenerationConfig(
        **kwargs
    )
    response = model.generate_content(system_prompt + "\n" + user_prompt, generation_config=generation_config)
    return response.text

def get_consistency_params() -> dict:
    return {
        "temperature": 0.0,
        "top_p": 0.001,
        # "seed": 77,
        "stop_sequences": ["\n```"]
    }
