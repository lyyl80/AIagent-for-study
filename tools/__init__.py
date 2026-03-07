from .tools import calculator_tool, read_file_tool, run_shell, write_file_tool

TOOL_REGISTRY = {
    "calculator": (calculator_tool, "计算数学表达式"),
    "read_file": (read_file_tool, "读取文件"),
    "write_file": (write_file_tool, "写入文件"),
    "shell": (run_shell, "运行shell命令"),
    "finish": (lambda: "任务完成", "结束任务")
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
