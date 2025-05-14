import json
import dotenv
import requests
import os
# from google.generativeai.types import GenerationConfig
from google import genai
from google.genai import types
import openai
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

    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-04-17",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=512),
            system_instruction=system_prompt,
            **kwargs
        ),
    )
    output_tokens = response.usage_metadata.candidates_token_count + response.usage_metadata.thoughts_token_count
    with open('tokens', 'a') as f:
        f.write(f"{output_tokens}\n")
    return response.text

def send_openai_request(system_prompt, user_prompt, **kwargs) -> str:
    dotenv.load_dotenv()
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        **kwargs
    )
    completion_tokens = response.usage.completion_tokens
    with open('tokens', 'a') as f:
        f.write(f"{completion_tokens}\n")
    print(f"OpenAI response: {response.choices[0].message.content}")
    return response.choices[0].message.content

def get_consistency_params() -> dict:
    return {
        "temperature": 0.0,
        "top_p": 0.001,
        "seed": 77,
        "stop": ["\n```"]
        #"stop_sequences": ["\n```"]
    }
