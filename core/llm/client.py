from ollama import chat
from openai import OpenAI
import json
import os
import re
from typing import Dict, Any, List, Optional
from core.config import *
from core.runtime.types import (
    TextBlock, ToolUse, ToolResult, TokenUsage,
    ConversationMessage, MessageRole, ContentBlock,
    ToolDefinition, ApiRequest,
)
from core.runtime.permissions import PermissionMode
from core.tools import TOOL_DEFINITIONS


class ApiClient:
    active_model: str = "deepseek-v4-flash"

    def __init__(self, model: str = ""):
        self.model = model or self.active_model
        self._model_info: Dict[str, Any] = {}

    def get_tool_definitions(self) -> List[ToolDefinition]:
        return TOOL_DEFINITIONS

    def get_model_by_key(self, model_key: str) -> Dict[str, Any]:
        for category, models in ModelManager.available_models.items():
            if model_key in models:
                return {
                    "key": model_key, "category": category,
                    "type": models[model_key]["type"],
                    "name": models[model_key]["name"]
                }
        default_key = "gpt-oss:20b"
        return {
            "key": default_key, "category": "本地模型",
            "type": ModelManager.available_models["本地模型"][default_key]["type"],
            "name": ModelManager.available_models["本地模型"][default_key]["name"]
        }

    def stream(self, request: ApiRequest) -> tuple:
        raw_text = self._call_model_raw(request)
        blocks, usage = self._parse_response(raw_text)
        return blocks, usage

    def _call_model_raw(self, request: ApiRequest) -> str:
        model_info = self.get_model_by_key(request.model)
        messages = self._format_messages(request)

        try:
            if model_info["type"] == "cloud":
                return self._call_cloud(model_info["key"], messages, request.system)
            else:
                return self._call_local(model_info["key"], messages, request.system)
        except Exception as e:
            return json.dumps({
                "action": {
                    "tool": "talk",
                    "tool_args": {
                        "message": f"模型调用失败: {str(e)}"
                    }
                }
            }, ensure_ascii=False)

    def _format_messages(self, request: ApiRequest) -> List[Dict]:
        msg_list = []
        for m in request.messages:
            if m.role == MessageRole.USER:
                msg_list.append({"role": "user", "content": m.text_blocks[0] if m.text_blocks else ""})
            elif m.role == MessageRole.ASSISTANT:
                parts = []
                for b in m.blocks:
                    if isinstance(b, ToolUse):
                        parts.append(f"[调用工具 {b.name}: {json.dumps(b.input, ensure_ascii=False)}]")
                    elif isinstance(b, TextBlock) and b.text:
                        parts.append(b.text)
                text = "\n".join(parts)
                if text:
                    msg_list.append({"role": "assistant", "content": text})
            elif m.role == MessageRole.TOOL:
                for r in m.tool_results:
                    msg_list.append({"role": "user", "content": f"工具 [{m.role.value}] 结果: {r.content}"})
        return msg_list

    def _call_cloud(self, model_key: str, messages: List[Dict], system: str) -> str:
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            raise Exception("未找到DEEPSEEK_API_KEY环境变量")
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        full_messages = [{"role": "system", "content": system}] + messages
        response = client.chat.completions.create(model=model_key, messages=full_messages, stream=True, max_tokens=8192)
        full_content = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                full_content += chunk.choices[0].delta.content
        return full_content

    def _call_local(self, model_key: str, messages: List[Dict], system: str) -> str:
        full_messages = [{"role": "system", "content": system}] + messages
        try:
            response = chat(model=model_key, messages=full_messages, stream=True, options={"num_predict": 8192})
            full_content = ""
            for chunk in response:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    full_content += content
            return full_content
        except Exception as e:
            return f"本地模型调用失败: {str(e)}"

    def _parse_response(self, raw_text: str) -> tuple:
        text = raw_text.strip()
        start_idx = text.find('{')
        end_idx = text.rfind('}')

        if start_idx == -1:
            return [TextBlock(text=text[:500])], TokenUsage()

        if end_idx > start_idx:
            try:
                data = json.loads(text[start_idx:end_idx + 1])
                action = data.get("action", data)
                tool_name = action.get("tool", "")
                tool_args = action.get("tool_args", {})

                blocks: List[ContentBlock] = []
                if tool_name in ("talk", "finish"):
                    msg = (tool_args.get("message") or tool_args.get("content")
                           or tool_args.get("response") or tool_args.get("text") or "")
                    blocks.append(TextBlock(text=msg))
                    if tool_name == "finish":
                        blocks.append(TextBlock(text="[任务完成]"))
                else:
                    blocks.append(ToolUse(id=f"tu_{hash(str(tool_args))}", name=tool_name, input=tool_args))

                usage = TokenUsage(input_tokens=len(raw_text) // 2, output_tokens=max(1, len(raw_text) // 4))
                return blocks, usage
            except json.JSONDecodeError:
                pass

        for key in ("text", "message", "content", "response"):
            m = re.search(r'"' + key + r'"\s*:\s*"((?:[^"\\]|\\.)*)', text)
            if m:
                extracted = m.group(1).replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                return [TextBlock(text=extracted[:500])], TokenUsage()
        return [TextBlock(text=text[:500])], TokenUsage()


class ModelManager:
    available_models = {
        "云端模型": {
            "deepseek-v4-flash": {"name": "DeepSeek Flash", "type": "cloud"},
            "deepseek-v4-pro": {"name": "DeepSeek Pro", "type": "cloud"},
        },
        "本地模型": {
            "gemma3:12b": {"name": "gemma3:12b", "type": "local"},
            "gpt-oss:20b": {"name": "gpt-oss:20b", "type": "local"},
        }
    }

    def __init__(self):
        pass

    def add_custom_model(self, key, name=None):
        self.available_models.setdefault("自定义模型", {})[key] = {"name": name or key, "type": "local"}

    def remove_custom_model(self, key):
        for category in list(self.available_models):
            if key in self.available_models[category]:
                del self.available_models[category][key]
                if category == "自定义模型" and not self.available_models[category]:
                    del self.available_models[category]
                return

    def get_model_options(self):
        options = {}
        for category, models in self.available_models.items():
            for key, model in models.items():
                options[f"{category} - {model['name']}"] = {"key": key, "category": category, "type": model["type"]}
        return options

    def get_model_by_key(self, model_key):
        for category, models in self.available_models.items():
            if model_key in models:
                return {"key": model_key, "category": category, "type": models[model_key]["type"], "name": models[model_key]["name"]}
        default_key = "gpt-oss:20b"
        return {"key": default_key, "category": "本地模型", "type": self.available_models["本地模型"][default_key]["type"], "name": self.available_models["本地模型"][default_key]["name"]}

    def call_model(self, model_info, messages, system_prompt, output=True):
        try:
            if model_info["type"] == "cloud":
                api_key = os.environ.get('DEEPSEEK_API_KEY')
                if not api_key:
                    raise Exception("未找到DEEPSEEK_API_KEY环境变量")
                client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                full_messages = [{"role": "system", "content": system_prompt}] + messages
                response = client.chat.completions.create(model=model_info["key"], messages=full_messages, stream=True)
                full_content = ""
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        full_content += chunk.choices[0].delta.content
                        if output:
                            print(chunk.choices[0].delta.content, end="", flush=True)
                if output:
                    print()
                return full_content
            else:
                full_messages = [{"role": "system", "content": system_prompt}] + messages
                try:
                    response = chat(model=model_info["key"], messages=full_messages, stream=True)
                    full_content = ""
                    for chunk in response:
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            full_content += content
                            if output:
                                print(content, end="", flush=True)
                    if output:
                        print()
                    return full_content
                except Exception as e:
                    return f"本地模型调用失败: {str(e)}"
        except Exception as e:
            raise Exception(f"模型调用失败: {str(e)}")

    def llm_json(self, messages, system_prompt, max_retries=3):
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        for attempt in range(max_retries):
            try:
                current_messages = messages.copy()
                if attempt > 0:
                    enhanced = current_messages[0]["content"] + "\n\n重要：请返回纯JSON格式，不要包含任何其他文本、解释或代码块标记。确保JSON格式完全正确。"
                    current_messages = [{"role": "user", "content": enhanced}]
                response = self.call_model(self.get_model_by_key(ApiClient.active_model), current_messages, system_prompt, output=False)
                cleaned = self._clean_json(response)
                json_data = json.loads(cleaned)
                return json_data
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    print(f"JSON解析失败，第{attempt + 1}次重试...")
                    continue
                else:
                    print(f"JSON解析失败（{max_retries}次重试后）: {str(e)}")
                    return {"error": f"LLM返回的内容不是有效的JSON（{max_retries}次重试后）", "raw_response": response}, response
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"调用失败，第{attempt + 1}次重试...")
                    continue
                else:
                    return {"error": f"模型调用失败: {str(e)}", "raw_response": ""}, ""

    def _clean_json(self, response):
        cleaned = response.strip()
        for prefix, suffix in [("```json\n", "\n```"), ("```json", "```"), ("```\n", "\n```"), ("```", "```")]:
            if cleaned.startswith(prefix) and cleaned.endswith(suffix):
                cleaned = cleaned[len(prefix):-len(suffix)]
                break
        cleaned = cleaned.strip()
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start:end + 1]
        return cleaned.strip()
