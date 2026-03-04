from ollama import chat
from openai import OpenAI
from config import *
from prompt import format_prompt, get_template

def deep_seek_chat(messages, template_name=None, **template_kwargs):
    try:
        # 如果指定了模板，则格式化消息
        if template_name:
            formatted_content = format_prompt(template_name, **template_kwargs)
            # 将格式化的提示添加到消息的最后
            messages = messages + [{"role": "system", "content": formatted_content}]
        
        client = OpenAI(api_key=DEEP_SEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"DeepSeek API调用失败: {str(e)}"


def local_chat(messages, template_name=None, **template_kwargs):
    try:
        # 如果指定了模板，则格式化消息
        if template_name:
            formatted_content = format_prompt(template_name, **template_kwargs)
            # 将格式化的提示添加到消息的最后
            messages = messages + [{"role": "system", "content": formatted_content}]
            
        response = chat(
            model=LLM_MODEL,
            messages=messages,
        )
        return response["message"]["content"]
    except Exception as e:
        return f"本地模型调用失败: {str(e)}"