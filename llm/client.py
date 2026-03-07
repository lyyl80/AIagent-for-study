from ollama import chat
from openai import OpenAI
import json
from config import *

def deep_seek_chat(messages):
    try:
        client = OpenAI(api_key=DEEP_SEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"DeepSeek API调用失败: {str(e)}"


def local_chat(messages):
    try:
        response = chat(
            model=LLM_MODEL,
            messages=messages,
            stream=False,
        )
        return response["message"]["content"]
    except Exception as e:
        return f"本地模型调用失败: {str(e)}"
    
def llm_json(messages):
    response = local_chat(messages)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"error": "LLM返回的内容不是有效的JSON", "raw_response": response}