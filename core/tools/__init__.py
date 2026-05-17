from typing import Dict, Any, Callable, Tuple, Optional
from core.runtime.types import ToolDefinition
from .tools import *

TOOL_FUNCTIONS: Dict[str, Callable] = {
    "read_file": read_file_tool,
    "write_file": write_file_tool,
    "shell": run_shell,
    "talk": talk_tool,
    "replace_content": replace_content_tool,
    "web_search": web_search_tool,
    "web_content": web_content_tool,
    "finish": finish_tool,
    "weather": weather_tool,
    "speaking": speaking_tool,
}

TOOL_DEFINITIONS = [
    ToolDefinition(
        name="read_file",
        description="读取文件内容",
        input_schema={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "文件路径"},
                "start_line": {"type": "integer", "description": "开始行号(1-based)"},
                "end_line": {"type": "integer", "description": "结束行号"},
                "search": {"type": "string", "description": "搜索字符串，返回匹配行"},
            },
            "required": ["file_path"]
        }
    ),
    ToolDefinition(
        name="write_file",
        description="写入文件内容",
        input_schema={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "文件路径"},
                "content": {"type": "string", "description": "要写入的内容"},
            },
            "required": ["file_path", "content"]
        }
    ),
    ToolDefinition(
        name="shell",
        description="执行shell命令(Windows PowerShell)",
        input_schema={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "命令字符串"},
                "timeout": {"type": "integer", "description": "超时时间(秒)", "default": 30},
                "cwd": {"type": "string", "description": "工作目录"},
            },
            "required": ["command"]
        }
    ),
    ToolDefinition(
        name="talk",
        description="与用户对话/回复/说明进度",
        input_schema={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "回复内容"},
            },
            "required": ["message"]
        }
    ),
    ToolDefinition(
        name="replace_content",
        description="替换文件中内容(精确匹配)",
        input_schema={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "文件路径"},
                "old_content": {"type": "string", "description": "要替换的旧内容"},
                "new_content": {"type": "string", "description": "新内容"},
            },
            "required": ["file_path", "old_content", "new_content"]
        }
    ),
    ToolDefinition(
        name="web_search",
        description="网络搜索",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索查询"},
            },
            "required": ["query"]
        }
    ),
    ToolDefinition(
        name="web_content",
        description="获取网页内容",
        input_schema={
            "type": "object",
            "properties": {
                "urls": {"type": "array", "items": {"type": "string"}, "description": "网址列表"},
            },
            "required": ["urls"]
        }
    ),
    ToolDefinition(
        name="finish",
        description="完成任务",
        input_schema={
            "type": "object",
            "properties": {
                "response": {"type": "string", "description": "完成说明"},
            },
            "required": []
        }
    ),
    ToolDefinition(
        name="weather",
        description="查询天气",
        input_schema={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称"},
            },
            "required": ["city"]
        }
    ),
    ToolDefinition(
        name="speaking",
        description="文字转语音朗读",
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "文本内容"},
            },
            "required": ["text"]
        }
    ),
]

# Backward-compatible registry
ToolEntry = Tuple[Callable, str, Optional[Dict[str, Any]]]
TOOL_REGISTRY: Dict[str, ToolEntry] = {}
for td in TOOL_DEFINITIONS:
    TOOL_REGISTRY[td.name] = (
        TOOL_FUNCTIONS.get(td.name, lambda **_: f"Error: {td.name} 未实现"),
        td.description,
        {
            "required_params": td.input_schema.get("required", []),
            "optional_params": [k for k in td.input_schema.get("properties", {})
                              if k not in td.input_schema.get("required", [])]
        }
    )


def call_tool(tool_name: str, **kwargs) -> Any:
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"工具 '{tool_name}' 未在注册表中找到。")

    tool_func, _, schema = TOOL_REGISTRY[tool_name]
    if schema:
        required = schema.get("required_params", [])
        aliases = {
            "file_path": ["path"],
            "message": ["content", "text"]
        }
        for param in required:
            if param not in kwargs:
                found = False
                for alt in aliases.get(param, []):
                    if alt in kwargs:
                        kwargs[param] = kwargs.pop(alt)
                        found = True
                        break
                if not found:
                    raise ValueError(f"工具 '{tool_name}' 缺少必需参数: {param}")
    return tool_func(**kwargs)


def get_tool_description() -> str:
    return "\n".join(
        f"{td.name}: {td.description}" for td in TOOL_DEFINITIONS
    )


def get_tool_schema(tool_name: str) -> Optional[Dict[str, Any]]:
    for td in TOOL_DEFINITIONS:
        if td.name == tool_name:
            return td.input_schema
    return None


def list_tools() -> list:
    return [td.name for td in TOOL_DEFINITIONS]
