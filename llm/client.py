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


def local_chat(messages, prefix="Thinking: "):
    try:
        response = chat(
            model=LLM_MODEL,
            messages=messages,
            stream=True,
        )
        full_content = ""
        if prefix:
            print(prefix, end="", flush=True)
        for chunk in response:
            content = chunk.get("message", {}).get("content", "")
            if content:
                full_content += content
                print(content, end="", flush=True)
        print()  # 换行
        return full_content
    except Exception as e:
        return f"本地模型调用失败: {str(e)}"

def local_chat_no_print(messages):
    """与local_chat相同功能但不打印输出的版本"""
    try:
        response = chat(
            model=LLM_MODEL,
            messages=messages,
            stream=True,
        )
        full_content = ""
        for chunk in response:
            content = chunk.get("message", {}).get("content", "")
            if content:
                full_content += content
        return full_content
    except Exception as e:
        return f"本地模型调用失败: {str(e)}"
    
def llm_json(messages):
    response = local_chat_no_print(messages)
    # 清理markdown代码块
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]  # 移除 ```json
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]  # 移除 ```
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]  # 移除结尾的 ```
    cleaned = cleaned.strip()
    try:
        json_data = json.loads(cleaned)
        # 返回解析后的JSON和原始响应
        return json_data
    except json.JSONDecodeError:
        return {"error": "LLM返回的内容不是有效的JSON", "raw_response": response}, response