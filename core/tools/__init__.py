"""

工具注册表模块



统一管理所有可用工具的注册、定义和调用。提供：

- TOOL_FUNCTIONS: 工具名称到函数的映射

- TOOL_DEFINITIONS: 工具的元数据描述（用于LLM理解）

- TOOL_REGISTRY: 向后兼容的注册表格式

- call_tool: 统一的工具调用入口

- 辅助函数：获取描述、Schema、列表等



支持参数别名自动转换，提高容错性。

"""

from typing import Dict, Any, Callable, Tuple, Optional

from core.runtime.types import ToolDefinition

from .tools import *
from .tools import serial_send_tool, load_skill_tool



# 工具名称到函数的映射表

TOOL_FUNCTIONS: Dict[str, Callable] = {

    "read_file": read_file_tool,

    "write_file": write_file_tool,

    "shell": run_shell,

    "talk": talk_tool,

    "replace_content": replace_content_tool,

    "web_search": web_search_tool,

    "web_content": web_content_tool,

    "finish": finish_tool,

    "speaking": speaking_tool,

    "list_directory": list_directory,

    "create_directory": create_directory,

    "delete_path": delete_path,

    "copy_move": copy_move,

    "grep_files": grep_files,

    "file_info": file_info,

    "python_exec": python_exec_tool,

    "serial_send": serial_send_tool,
    "load_skill": load_skill_tool,

}



# 工具定义列表 - 包含名称、描述和JSON Schema

TOOL_DEFINITIONS = [

    ToolDefinition(

        name="read_file",

        description="读取文件内容（自动检测编码，支持搜索/行范围/max_lines）",

        input_schema={

            "type": "object",

            "properties": {

                "file_path": {"type": "string", "description": "文件路径"},

                "start_line": {"type": "integer", "description": "开始行号"},

                "end_line": {"type": "integer", "description": "结束行号"},

                "search": {"type": "string", "description": "搜索字符串"},

                "max_lines": {"type": "integer", "description": "最大行数，默认500"},

            },

            "required": ["file_path"]

        }

    ),

    ToolDefinition(

        name="write_file",

        description="写入文件（自动创建父目录，支持追加/备份）",

        input_schema={

            "type": "object",

            "properties": {

                "file_path": {"type": "string", "description": "文件路径"},

                "content": {"type": "string", "description": "写入内容"},

                "append": {"type": "boolean", "description": "追加模式"},

                "backup": {"type": "boolean", "description": "覆盖前备份为 .bak"},

            },

            "required": ["file_path", "content"]

        }

    ),

    ToolDefinition(

        name="shell",

        description="执行 PowerShell 命令",

        input_schema={

            "type": "object",

            "properties": {

                "command": {"type": "string", "description": "命令字符串"},

                "timeout": {"type": "integer", "description": "超时秒数，默认60"},

                "cwd": {"type": "string", "description": "工作目录"},

            },

            "required": ["command"]

        }

    ),

    ToolDefinition(

        name="talk",

        description="与用户对话/回复",

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

        description="替换文件内容（支持精确匹配/正则/计数）",

        input_schema={

            "type": "object",

            "properties": {

                "file_path": {"type": "string", "description": "文件路径"},

                "old_content": {"type": "string", "description": "旧内容"},

                "new_content": {"type": "string", "description": "新内容"},

                "regex": {"type": "boolean", "description": "使用正则模式"},

                "count": {"type": "integer", "description": "替换次数，0=全部"},

            },

            "required": ["file_path", "old_content", "new_content"]

        }

    ),

    ToolDefinition(

        name="web_search",

        description="Bing 网络搜索",

        input_schema={

            "type": "object",

            "properties": {

                "query": {"type": "string", "description": "搜索关键词"},

            },

            "required": ["query"]

        }

    ),

    ToolDefinition(

        name="web_content",

        description="获取网页纯文本内容",

        input_schema={

            "type": "object",

            "properties": {

                "urls": {"type": "array", "items": {"type": "string"}, "description": "URL 列表"},

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

        name="speaking",

        description="文字转语音朗读",

        input_schema={

            "type": "object",

            "properties": {

                "text": {"type": "string", "description": "文本内容"},

                "rate": {"type": "integer", "description": "语速，默认150"},

                "volume": {"type": "number", "description": "音量 0-1，默认1.0"},

            },

            "required": ["text"]

        }

    ),

    # ========== 新增工具 ==========

    ToolDefinition(

        name="list_directory",

        description="列出目录内容（含大小/修改时间/类型，可过滤隐藏和正则）",

        input_schema={

            "type": "object",

            "properties": {

                "path": {"type": "string", "description": "目录路径，默认当前"},

                "all": {"type": "boolean", "description": "包含隐藏文件"},

                "pattern": {"type": "string", "description": "文件名正则过滤"},

            },

            "required": []

        }

    ),

    ToolDefinition(

        name="create_directory",

        description="创建目录（递归创建父目录）",

        input_schema={

            "type": "object",

            "properties": {

                "path": {"type": "string", "description": "目录路径"},

            },

            "required": ["path"]

        }

    ),

    ToolDefinition(

        name="delete_path",

        description="删除文件或目录",

        input_schema={

            "type": "object",

            "properties": {

                "path": {"type": "string", "description": "路径"},

                "recursive": {"type": "boolean", "description": "递归删除（目录非空时必填）"},

            },

            "required": ["path"]

        }

    ),

    ToolDefinition(

        name="copy_move",

        description="复制或移动文件/目录",

        input_schema={

            "type": "object",

            "properties": {

                "src": {"type": "string", "description": "源路径"},

                "dst": {"type": "string", "description": "目标路径"},

                "action": {"type": "string", "description": "copy(默认) 或 move"},

            },

            "required": ["src", "dst"]

        }

    ),

    ToolDefinition(

        name="grep_files",

        description="在文件中搜索正则表达式（类似 grep -r）",

        input_schema={

            "type": "object",

            "properties": {

                "pattern": {"type": "string", "description": "正则模式"},

                "path": {"type": "string", "description": "搜索路径，默认当前目录"},

                "include": {"type": "string", "description": "文件 glob，默认 *"},

                "exclude": {"type": "string", "description": "排除文件 glob"},

                "max_results": {"type": "integer", "description": "最大结果数，默认50"},

                "ignore_case": {"type": "boolean", "description": "忽略大小写，默认True"},

            },

            "required": ["pattern"]

        }

    ),

    ToolDefinition(

        name="file_info",

        description="获取文件/目录详细信息（大小/时间/MD5/权限）",

        input_schema={

            "type": "object",

            "properties": {

                "path": {"type": "string", "description": "路径"},

            },

            "required": ["path"]

        }

    ),

    ToolDefinition(

        name="python_exec",

        description="执行 Python 代码片段（隔离沙箱）",

        input_schema={

            "type": "object",

            "properties": {

                "code": {"type": "string", "description": "Python 代码"},

            },

            "required": ["code"]

        }

    ),

    ToolDefinition(
        name="load_skill",
        description="按名称加载技能(skill)的完整指导内容到对话中，技能包含特定任务的标准化操作流程",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "技能名称，例如 axis-robot-control"},
            },
            "required": ["name"]
        }
    ),
    ToolDefinition(
        name="serial_send",
        description="通过串口发送数据到外部设备（如机械臂、Arduino等），支持文本和hex格式",
        input_schema={
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "要发送的数据（文本字符串 或 hex字符串）"},
                "port": {"type": "string", "description": "串口号，默认COM5"},
                "baudrate": {"type": "integer", "description": "波特率，默认115200"},
                "encoding": {"type": "string", "enum": ["text", "hex"], "description": "编码方式：text(默认) 或 hex"},
                "read_response": {"type": "boolean", "description": "是否读取设备回显，默认false"},
            },
            "required": ["data"]
        }
    ),

]



# 向后兼容的注册表格式

# ToolEntry = (函数, 描述, Schema字典)

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

    """

    统一调用工具的入口函数

    

    验证工具存在性和必需参数，支持参数别名自动转换。

    

    Args:

        tool_name (str): 工具名称

        **kwargs: 工具参数

        

    Returns:

        Any: 工具执行结果

        

    Raises:

        ValueError: 当工具不存在或缺少必需参数时

    """

    if tool_name not in TOOL_REGISTRY:

        raise ValueError(f"工具 '{tool_name}' 未在注册表中找到。")



    tool_func, _, schema = TOOL_REGISTRY[tool_name]

    if schema:

        required = schema.get("required_params", [])

        # 参数别名映射表

        aliases = {

            "file_path": ["path"],

            "message": ["content", "text"],

            "src": ["source", "from"],

            "dst": ["dest", "destination", "to"],

        }

        for param in required:

            if param not in kwargs:

                found = False

                # 尝试查找别名

                for alt in aliases.get(param, []):

                    if alt in kwargs:

                        kwargs[param] = kwargs.pop(alt)

                        found = True

                        break

                if not found:

                    raise ValueError(f"工具 '{tool_name}' 缺少必需参数: {param}")

    return tool_func(**kwargs)





def get_tool_description() -> str:

    """

    获取所有工具的简要描述文本

    

    Returns:

        str: 每行一个工具的"名称: 描述"格式

    """

    return "\n".join(

        f"{td.name}: {td.description}" for td in TOOL_DEFINITIONS

    )





def get_tool_schema(tool_name: str) -> Optional[Dict[str, Any]]:

    """

    获取指定工具的JSON Schema

    

    Args:

        tool_name (str): 工具名称

        

    Returns:

        Optional[Dict]: 工具的input_schema，未找到返回None

    """

    for td in TOOL_DEFINITIONS:

        if td.name == tool_name:

            return td.input_schema

    return None





def list_tools() -> list:

    """

    获取所有工具名称列表

    

    Returns:

        list: 工具名称字符串列表

    """

    return [td.name for td in TOOL_DEFINITIONS]

