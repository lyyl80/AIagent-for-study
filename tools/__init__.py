from typing import Dict, Any, Callable, Tuple, Optional
from .tools import *


# 工具注册表类型定义
ToolEntry = Tuple[Callable, str, Optional[Dict[str, Any]]]
TOOL_REGISTRY: Dict[str, ToolEntry] = {
    "read_file": (
        read_file_tool,
        "读取文件内容。参数: file_path 或 path - 文件路径，可选: start_line/end_line - 行范围(1-based)，search - 搜索字符串",
        {
            "required_params": ["file_path"],
            "optional_params": ["start_line", "end_line", "search"]
        }
    ),
    "write_file": (
        write_file_tool,
        "写入文件内容。参数: file_path 或 path - 文件路径，content - 要写入的内容",
        {
            "required_params": ["file_path", "content"],
            "optional_params": []
        }
    ),
    "shell": (
        run_shell,
        "运行shell命令。参数: command - 要执行的命令字符串，可选: timeout - 超时时间(秒，默认30)，cwd - 工作目录,执行系统为windows的cmd或powershell",
        {
            "required_params": ["command"],
            "optional_params": ["timeout", "cwd"]
        }
    ),
    "talk": (
        talk_tool,
        "与用户进行对话，回答问题，解释概念，提供信息。参数: message 或 content 或 text - 要回复的内容",
        {
            "required_params": ["message"],
            "optional_params": []
        }
    ),
    "replace_content": (
        replace_content_tool,
        "替换文件中的现有内容。参数: file_path 或 path - 文件路径，old_content - 要替换的旧内容字符串，new_content - 新的内容字符串",
        {
            "required_params": ["file_path", "old_content", "new_content"],
            "optional_params": []
        }
    ),
    "web_search": (
        web_search_tool,
        "使用网络搜索,尽量搜索文字类网站。参数: query - 搜索查询字符串",
        {
            "required_params": ["query"],
            "optional_params": []
        }
    ),
    "web_content":(
        web_content_tool,
       """获取网页内容,尽量是文字类网站。参数: urls - 要获取内容的网址列表[
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"]""",
        {
            "required_params": ["urls"],
            "optional_params": []
        }
    ),
    "fusion360": (
        fusion360_tool,
        "与Fusion360进行交互。参数: tool_name - 要执行的Fusion360命令，params - 要执行的命令字符串 相关参数请查询D:\Python\Doc\AIagent\tools\fusion工具描述.txt",
        {
            "required_params": ["tool_name", "params"],
            "optional_params": []
        }
    ),
    "finish": (
        finish_tool,
        "结束任务。可选参数: response - 结语消息",
        {
            "required_params": [],
            "optional_params": ["response"]
        }
    )
}


def call_tool(tool_name: str, **kwargs) -> Any:
    """调用工具
    
    参数:
        tool_name: 工具名称
        **kwargs: 工具参数
        
    返回:
        Any: 工具执行结果
        
    异常:
        ValueError: 工具未找到或参数无效
    """
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"工具 '{tool_name}' 未在注册表中找到。")
    
    tool_func, _, schema = TOOL_REGISTRY[tool_name]
    
    # 参数验证（如果提供了模式）
    if schema:
        required = schema.get("required_params", [])
        for param in required:
            if param not in kwargs:
                # 尝试使用别名
                aliases = {
                    "file_path": ["path"],
                    "message": ["content", "text"]
                }
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
    """获取所有工具的描述
    
    返回:
        str: 工具描述字符串，每行一个工具
    """
    tool_info = []
    for tool_name, (_, description, _) in TOOL_REGISTRY.items():
        tool_info.append(f"{tool_name}: {description}")
    return "\n".join(tool_info)


def get_tool_schema(tool_name: str) -> Optional[Dict[str, Any]]:
    """获取工具的模式定义
    
    参数:
        tool_name: 工具名称
        
    返回:
        Optional[Dict[str, Any]]: 工具模式字典，如果工具不存在则返回None
    """
    if tool_name in TOOL_REGISTRY:
        _, _, schema = TOOL_REGISTRY[tool_name]
        return schema
    return None


def list_tools() -> list:
    """列出所有可用工具
    
    返回:
        list: 工具名称列表
    """
    return list(TOOL_REGISTRY.keys())
