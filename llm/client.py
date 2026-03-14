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
    
    def _call_cloud_model(self, model_key, messages, system_prompt, prefix="", output=True):
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
        if prefix :
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
    
    def _call_local_model(self, model_key, messages, system_prompt, prefix="",output=True):
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
    def llm_json(self, messages, system_prompt, max_retries=3):
        # 如果messages是字符串，转换为消息列表
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        for attempt in range(max_retries):
            try:
                # 如果是重试，增强提示词要求严格的JSON格式
                current_messages = messages.copy()
                if attempt > 0:
                    # 增强提示：要求纯JSON格式
                    enhanced_content = current_messages[0]["content"] + "\n\n重要：请返回纯JSON格式，不要包含任何其他文本、解释或代码块标记。确保JSON格式完全正确。"
                    current_messages = [{"role": "user", "content": enhanced_content}]
                
                response = self.call_model(self.get_model_by_key(MODEL_ING), current_messages, system_prompt, output=False)
                
                # 增强的JSON清理逻辑
                cleaned = self._clean_json_response(response)
                
                # 尝试解析JSON
                json_data = json.loads(cleaned)
                return json_data
                
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    print(f"JSON解析失败，第{attempt + 1}次重试...")
                    continue
                else:
                    print(f"JSON解析失败（{max_retries}次重试后）: {str(e)}")
                    print(f"清理后的响应: {cleaned[:200]}...")
                    return {"error": f"LLM返回的内容不是有效的JSON（{max_retries}次重试后）", "raw_response": response}, response
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"调用失败，第{attempt + 1}次重试...")
                    continue
                else:
                    return {"error": f"模型调用失败: {str(e)}", "raw_response": ""}, ""
    
    def _clean_json_response(self, response):
        """清理LLM响应，提取JSON内容"""
        cleaned = response.strip()
        
        # 移除各种可能的代码块标记
        json_markers = [
            ("```json\n", "\n```"),
            ("```json", "```"),
            ("```JSON\n", "\n```"),
            ("```JSON", "```"),
            ("```\n", "\n```"),
            ("```", "```"),
            ("`json\n", "\n`"),
            ("`json", "`"),
            ("`JSON\n", "\n`"),
            ("`JSON", "`"),
            ("`", "`"),
        ]
        
        for start_marker, end_marker in json_markers:
            if cleaned.startswith(start_marker) and cleaned.endswith(end_marker):
                cleaned = cleaned[len(start_marker):-len(end_marker)]
                break
        
        # 移除可能的Markdown格式
        cleaned = cleaned.strip()
        
        # 如果响应以{开头，}结尾，尝试提取最外层的JSON对象
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx:end_idx+1]
        
        # 移除可能的前后空白字符
        cleaned = cleaned.strip()
        
        return cleaned

