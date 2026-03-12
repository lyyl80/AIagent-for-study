from ollama import chat
from openai import OpenAI
import json
from config import *
    # 模型管理类 - 遵循Ollama本地模型调用规范
class ModelManager:
    def __init__(self):
        self.available_models = {
            "云端模型": {
                "deepseek-chat": {"name": "DeepSeek Chat", "type": "cloud"},
                "deepseek-reasoner": {"name": "DeepSeek Reasoner", "type": "cloud"},
            },
            "本地模型": {
                "gemma3:12b": {"name": "gemma3:12b", "type": "local"},
                "gpt-oss:20b": {"name": "gpt-oss:20b", "type": "local"},
                "geem3": {"name": "geem3", "type": "local"},
            }
        }
        
    def get_model_options(self):
        """获取所有可用模型选项"""
        options = {}
        for category, models in self.available_models.items():
            for key, model in models.items():
                options[f"{category} - {model['name']}"] = {
                    "key": key,
                    "category": category,
                    "type": model["type"]
                }
        return options
    
    def get_model_by_key(self, model_key):
        """根据模型键获取模型信息"""
        for category, models in self.available_models.items():
            if model_key in models:
                return {
                    "key": model_key,
                    "category": category,
                    "type": models[model_key]["type"],
                    "name": models[model_key]["name"]
                }
        # 如果没有找到，返回默认模型
        default_key = "gpt-oss:20b"
        return {
            "key": default_key,
            "category": "本地模型",
            "type": self.available_models["本地模型"][default_key]["type"],
            "name": self.available_models["本地模型"][default_key]["name"]
        }
    
    def call_model(self, model_info, messages, system_prompt, output=True):
        """调用指定模型"""
        try:
            if model_info["type"] == "cloud":
                return self._call_cloud_model(model_info["key"], messages, system_prompt, output=output)
            else:
                return self._call_local_model(model_info["key"], messages, system_prompt, output=output)
        except Exception as e:
            raise Exception(f"模型调用失败: {str(e)}")
    
    def _call_cloud_model(self, model_key, messages, system_prompt, prefix="Thinking: ", output=True):
        """调用云端模型"""
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            raise Exception("未找到DEEPSEEK_API_KEY环境变量")
            
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        response = client.chat.completions.create(
            model=model_key,
            messages=full_messages,
            stream=True
        )
        
        full_content = ""
        if prefix and output:
            print(prefix, end="", flush=True)
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                if output:
                    print(content, end="", flush=True)
        if output:
            print()  # 换行
        return full_content
    
    def _call_local_model(self, model_key, messages, system_prompt, prefix="Thinking: ",output=True):
        """调用本地模型"""
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        try:
            response = chat(
                model=model_key,
                messages=full_messages,
                stream=True,
            )
            full_content = ""
            if prefix:
                print(prefix, end="", flush=True)
            for chunk in response:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    full_content += content
                    if output:
                        print(content, end="", flush=True)
            if output:
                print()  # 换行
            return full_content
        except Exception as e:
            return f"本地模型调用失败: {str(e)}"
    def llm_json(self, messages, system_prompt):
        # 如果messages是字符串，转换为消息列表
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        response = self.call_model(self.get_model_by_key(MODEL_ING), messages, system_prompt,output=False)
        # 清理代码块
        cleaned = response.strip()
        if cleaned.startswith("``json"):
            cleaned = cleaned[7:]  # 移除 ```json
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]  # 移除 ```
        if cleaned.endswith("````"):
            cleaned = cleaned[:-4]  # 移除结尾的 ````
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]  # 移除结尾的 ```
        cleaned = cleaned.strip()
        try:
            json_data = json.loads(cleaned)
            # 返回解析后的JSON和原始响应
            return json_data
        except json.JSONDecodeError:
            return {"error": "LLM返回的内容不是有效的JSON", "raw_response": response}, response

