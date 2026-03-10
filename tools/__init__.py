from .tools import  read_file_tool, run_shell, write_file_tool ,talk_tool, replace_content_tool

TOOL_REGISTRY = {
    "read_file": (read_file_tool, "读取文件内容。参数: file_path 或 path - 文件路径，可选: start_line/end_line - 行范围(1-based)，search - 搜索字符串"),
    "write_file": (write_file_tool, "写入文件内容。参数: file_path 或 path - 文件路径，content - 要写入的内容"),
    "shell": (run_shell, "运行shell命令。参数: command - 要执行的命令字符串，可选: timeout - 超时时间(秒，默认30)，cwd - 工作目录"),
    "talk": (talk_tool, "与用户进行对话，回答问题，解释概念，提供信息。参数: message 或 content 或 text - 要回复的内容"),
    "replace_content": (replace_content_tool, "替换文件中的现有内容。参数: file_path 或 path - 文件路径，old_content - 要替换的旧内容字符串，new_content - 新的内容字符串"),
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
