from .tools import calculator_tool

TOOL_REGISTRY = {
    "calculator": (calculator_tool, "计算数学表达式")

}
def call_tool(tool_name, tool_input):
    if tool_name in TOOL_REGISTRY:
        tool_func, _ = TOOL_REGISTRY[tool_name]
        return tool_func(tool_input)
    else:
        raise ValueError(f"Tool '{tool_name}' not found in registry.")
    
def get_tool_description(tool_name):
    tool_info =[]
    for tool_name, (_, description) in TOOL_REGISTRY.items():
        tool_info.append(f"{tool_name}: {description}")
    return "\n".join(tool_info)