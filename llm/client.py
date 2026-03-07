from ollama import chat
from openai import OpenAI
from config import *
from prompt import format_prompt, get_template

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