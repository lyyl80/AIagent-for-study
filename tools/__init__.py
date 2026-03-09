from .tools import  read_file_tool, run_shell, write_file_tool ,talk_tool

TOOL_REGISTRY = {
    "read_file": (read_file_tool, "读取文件内容。参数: file_path 或 path - 文件路径"),
    "write_file": (write_file_tool, "写入文件内容。参数: file_path 或 path - 文件路径，content - 要写入的内容"),
    "shell": (run_shell, "运行shell命令。参数: command - 要执行的命令字符串"),
    "talk": (talk_tool, "与用户进行对话，回答问题，解释概念，提供信息。参数: message 或 content 或 text - 要回复的内容"),
    "finish": (lambda: "任务完成", "结束任务。无参数")
}
def call_tool(tool_name, **kwargs):
    if tool_name in TOOL_REGISTRY:
        tool_func, _ = TOOL_REGISTRY[tool_name]
        return tool_func(**kwargs)
    else:
        raise ValueError(f"Tool '{tool_name}' not found in registry.")
    
def get_tool_description():
    tool_info =[]
    for tool_name, (_, description) in TOOL_REGISTRY.items():
        tool_info.append(f"{tool_name}: {description}")
    return "\n".join(tool_info)
