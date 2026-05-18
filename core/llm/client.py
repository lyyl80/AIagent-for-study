"""
LLM客户端模块

提供统一的LLM调用接口，支持云端模型（DeepSeek）和本地模型（Ollama）。
负责消息格式化、API调用、响应解析和JSON数据处理。
"""
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
    """
    API客户端类 - 统一封装LLM调用逻辑
    
    支持多种模型后端（云端/本地），处理消息格式化、工具定义管理、
    响应解析等功能。采用流式输出提升用户体验。
    
    Attributes:
        active_model (str): 当前激活的模型标识符
        model (str): 实例使用的模型标识符
        _model_info (Dict): 模型元信息缓存
    """
    
    active_model: str = "deepseek-v4-flash"

    def __init__(self, model: str = ""):
        """
        初始化API客户端
        
        Args:
            model (str): 指定使用的模型标识符，为空则使用active_model
        """
        self.model = model or self.active_model
        self._model_info: Dict[str, Any] = {}

    def get_tool_definitions(self) -> List[ToolDefinition]:
        """
        获取所有可用工具的定义列表
        
        Returns:
            List[ToolDefinition]: 工具定义列表，包含名称、描述、参数等信息
        """
        return TOOL_DEFINITIONS

    def get_model_by_key(self, model_key: str) -> Dict[str, Any]:
        """
        根据模型键获取模型详细信息
        
        遍历ModelManager的模型注册表，查找匹配的模型配置。
        如果未找到，返回默认的本地模型作为后备。
        
        Args:
            model_key (str): 模型标识符
            
        Returns:
            Dict[str, Any]: 包含key、category、type、name的模型信息字典
        """
        for category, models in ModelManager.available_models.items():
            if model_key in models:
                return {
                    "key": model_key, "category": category,
                    "type": models[model_key]["type"],
                    "name": models[model_key]["name"]
                }
        # 默认后备模型
        default_key = "gpt-oss:20b"
        return {
            "key": default_key, "category": "本地模型",
            "type": ModelManager.available_models["本地模型"][default_key]["type"],
            "name": ModelManager.available_models["本地模型"][default_key]["name"]
        }

    def stream(self, request: ApiRequest) -> tuple:
        """
        执行流式请求并解析响应
        
        调用模型获取原始文本，然后解析为结构化内容块和使用统计。
        
        Args:
            request (ApiRequest): API请求对象，包含消息、系统提示等
            
        Returns:
            tuple: (blocks, usage) - 内容块列表和token使用统计
        """
        raw_text = self._call_model_raw(request)
        blocks, usage = self._parse_response(raw_text)
        return blocks, usage

    def _call_model_raw(self, request: ApiRequest) -> str:
        """
        调用模型获取原始文本响应
        
        根据模型类型（云端/本地）选择相应的调用方式。
        异常时返回错误信息的JSON格式字符串。
        
        Args:
            request (ApiRequest): API请求对象
            
        Returns:
            str: 模型的原始文本响应
        """
        model_info = self.get_model_by_key(request.model)
        messages = self._format_messages(request)

        try:
            if model_info["type"] == "cloud":
                return self._call_cloud(model_info["key"], messages, request.system)
            else:
                return self._call_local(model_info["key"], messages, request.system)
        except Exception as e:
            # 异常时返回结构化的错误信息
            return json.dumps({
                "action": {
                    "tool": "talk",
                    "tool_args": {
                        "message": f"模型调用失败: {str(e)}"
                    }
                }
            }, ensure_ascii=False)

    def _format_messages(self, request: ApiRequest) -> List[Dict]:
        """
        将运行时消息格式化为LLM API所需的格式
        
        处理不同类型的消息（用户、助手、工具结果），提取文本内容，
        对长内容进行截断以避免超出上下文限制。
        
        Args:
            request (ApiRequest): 包含消息列表的API请求对象
            
        Returns:
            List[Dict]: 格式化后的消息列表，每个元素包含role和content
        """
        msg_list = []
        for m in request.messages:
            if m.role == MessageRole.USER:
                # 用户消息：直接提取文本
                msg_list.append({"role": "user", "content": m.text_blocks[0] if m.text_blocks else ""})
            elif m.role == MessageRole.ASSISTANT:
                # 助手消息：合并文本块和工具调用信息
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
                # 工具结果：添加前缀标识并截断过长内容
                for r in m.tool_results:
                    content = r.content
                    if len(content) > 2000:
                        content = content[:1500] + f"\n... (剩余 {len(content)-1500} 字符)"
                    msg_list.append({"role": "user", "content": f"工具 [{m.role.value}] 结果: {content}"})
        return msg_list

    def _call_cloud(self, model_key: str, messages: List[Dict], system: str) -> str:
        """
        调用云端模型（DeepSeek API）
        
        使用OpenAI兼容接口进行流式调用，累积所有chunk的内容。
        
        Args:
            model_key (str): 模型标识符
            messages (List[Dict]): 格式化后的消息列表
            system (str): 系统提示词
            
        Returns:
            str: 完整的模型响应文本
            
        Raises:
            Exception: 当环境变量DEEPSEEK_API_KEY未设置时
        """
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            raise Exception("未找到DEEPSEEK_API_KEY环境变量")
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        full_messages = [{"role": "system", "content": system}] + messages
        response = client.chat.completions.create(
            model=model_key, 
            messages=full_messages, 
            stream=True, 
            max_tokens=16384
        )
        full_content = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                full_content += chunk.choices[0].delta.content
        return full_content

    def _call_local(self, model_key: str, messages: List[Dict], system: str) -> str:
        """
        调用本地模型（Ollama）
        
        使用ollama库进行流式调用，从响应chunk中提取消息内容。
        
        Args:
            model_key (str): 模型标识符
            messages (List[Dict]): 格式化后的消息列表
            system (str): 系统提示词
            
        Returns:
            str: 完整的模型响应文本，或错误信息
        """
        full_messages = [{"role": "system", "content": system}] + messages
        try:
            response = chat(
                model=model_key, 
                messages=full_messages, 
                stream=True, 
                options={"num_predict": 16384}
            )
            full_content = ""
            for chunk in response:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    full_content += content
            return full_content
        except Exception as e:
            return f"本地模型调用失败: {str(e)}"

    def _parse_response(self, raw_text: str) -> tuple:
        """
        解析模型原始响应为结构化数据
        
        尝试从文本中提取JSON格式的工具调用指令，支持多种降级策略：
        1. 完整JSON解析
        2. 正则表达式提取关键字段
        3. 纯文本回退
        
        Args:
            raw_text (str): 模型的原始文本响应
            
        Returns:
            tuple: (blocks, usage) - 解析后的内容块列表和token使用统计
        """
        text = raw_text.strip()
        start_idx = text.find('{')
        end_idx = text.rfind('}')

        # 如果没有JSON结构，直接返回纯文本
        if start_idx == -1:
            return [TextBlock(text=text[:3000])], TokenUsage()

        # 尝试解析JSON
        if end_idx > start_idx:
            try:
                data = json.loads(text[start_idx:end_idx + 1])
                action = data.get("action", data)
                tool_name = action.get("tool", "")
                tool_args = action.get("tool_args", {})

                blocks: List[ContentBlock] = []
                # 特殊处理对话和完成工具
                if tool_name in ("talk", "finish"):
                    msg = (tool_args.get("message") or tool_args.get("content")
                           or tool_args.get("response") or tool_args.get("text") or "")
                    blocks.append(TextBlock(text=msg))
                    if tool_name == "finish":
                        blocks.append(TextBlock(text="[任务完成]"))
                else:
                    # 普通工具调用
                    blocks.append(ToolUse(id=f"tu_{hash(str(tool_args))}", name=tool_name, input=tool_args))

                # 估算token使用量
                usage = TokenUsage(input_tokens=len(raw_text) // 2, output_tokens=max(1, len(raw_text) // 4))
                return blocks, usage
            except json.JSONDecodeError:
                pass

        # 降级策略：使用正则提取常见字段
        for key in ("text", "message", "content", "response"):
            m = re.search(r'"' + key + r'"\s*:\s*"((?:[^"\\]|\\.)*)', text)
            if m:
                extracted = m.group(1).replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                return [TextBlock(text=extracted[:4000])], TokenUsage()
        
        # 最终回退：返回截断的原始文本
        return [TextBlock(text=text[:3000])], TokenUsage()


class ModelManager:
    """
    模型管理器类 - 管理可用的LLM模型注册表
    
    维护云端和本地模型的配置信息，支持动态添加/删除自定义模型。
    提供模型查询和调用功能。
    
    Attributes:
        available_models (Dict): 模型注册表，按类别组织
    """
    
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
        """初始化模型管理器（当前无需特殊初始化）"""
        pass

    def add_custom_model(self, key, name=None):
        """
        添加自定义模型到注册表
        
        Args:
            key (str): 模型标识符
            name (Optional[str]): 模型显示名称，默认为key
        """
        self.available_models.setdefault("自定义模型", {})[key] = {"name": name or key, "type": "local"}

    def remove_custom_model(self, key):
        """
        从注册表中移除自定义模型
        
        如果移除后"自定义模型"类别为空，则删除该类别。
        
        Args:
            key (str): 要移除的模型标识符
        """
        for category in list(self.available_models):
            if key in self.available_models[category]:
                del self.available_models[category][key]
                if category == "自定义模型" and not self.available_models[category]:
                    del self.available_models[category]
                return

    def get_model_options(self):
        """
        获取所有可用模型的选项列表
        
        Returns:
            Dict: 以"类别 - 名称"为键的模型选项字典
        """
        options = {}
        for category, models in self.available_models.items():
            for key, model in models.items():
                options[f"{category} - {model['name']}"] = {"key": key, "category": category, "type": model["type"]}
        return options

    def get_model_by_key(self, model_key):
        """
        根据模型键获取模型信息
        
        Args:
            model_key (str): 模型标识符
            
        Returns:
            Dict: 包含key、category、type、name的模型信息
        """
        for category, models in self.available_models.items():
            if model_key in models:
                return {"key": model_key, "category": category, "type": models[model_key]["type"], "name": models[model_key]["name"]}
        default_key = "gpt-oss:20b"
        return {"key": default_key, "category": "本地模型", "type": self.available_models["本地模型"][default_key]["type"], "name": self.available_models["本地模型"][default_key]["name"]}

    def call_model(self, model_info, messages, system_prompt, output=True):
        """
        调用指定模型生成响应
        
        支持流式输出，可选择是否实时打印内容。
        
        Args:
            model_info (Dict): 模型信息字典
            messages (List[Dict]): 消息列表
            system_prompt (str): 系统提示词
            output (bool): 是否实时输出内容，默认True
            
        Returns:
            str: 完整的模型响应文本
        """
        try:
            if model_info["type"] == "cloud":
                api_key = os.environ.get('DEEPSEEK_API_KEY')
                if not api_key:
                    raise Exception("未找到DEEPSEEK_API_KEY环境变量")
                client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                full_messages = [{"role": "system", "content": system_prompt}] + messages
                response = client.chat.completions.create(
                    model=model_info["key"], 
                    messages=full_messages, 
                    stream=True
                )
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
        """
        调用LLM获取JSON格式的响应
        
        自动重试机制处理JSON解析失败，通过增强提示词提高成功率。
        清理响应中的Markdown代码块标记，提取有效的JSON内容。
        
        Args:
            messages: 消息列表或单个消息字符串
            system_prompt (str): 系统提示词
            max_retries (int): 最大重试次数，默认3次
            
        Returns:
            Union[Dict, Tuple]: 成功时返回解析后的JSON字典；
                               失败时返回包含错误信息和原始响应的元组
        """
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        for attempt in range(max_retries):
            try:
                current_messages = messages.copy()
                # 重试时增强提示词，强调JSON格式要求
                if attempt > 0:
                    enhanced = current_messages[0]["content"] + "\n\n重要：请返回纯JSON格式，不要包含任何其他文本、解释或代码块标记。确保JSON格式完全正确。"
                    current_messages = [{"role": "user", "content": enhanced}]
                
                response = self.call_model(
                    self.get_model_by_key(ApiClient.active_model), 
                    current_messages, 
                    system_prompt, 
                    output=False
                )
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
        """
        清理LLM响应中的JSON内容
        
        移除Markdown代码块标记（```json ... ```），提取最外层的JSON对象。
        
        Args:
            response (str): LLM的原始响应文本
            
        Returns:
            str: 清理后的JSON字符串
        """
        cleaned = response.strip()
        # 移除常见的代码块标记
        for prefix, suffix in [("```json\n", "\n```"), ("```json", "```"), ("```\n", "\n```"), ("```", "```")]:
            if cleaned.startswith(prefix) and cleaned.endswith(suffix):
                cleaned = cleaned[len(prefix):-len(suffix)]
                break
        cleaned = cleaned.strip()
        # 提取最外层的JSON对象
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start:end + 1]
        return cleaned.strip()
