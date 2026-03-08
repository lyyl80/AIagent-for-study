from .tools import  read_file_tool, run_shell, write_file_tool ,talk_tool

TOOL_REGISTRY = {
    "read_file": (read_file_tool, "读取文件"),
    "write_file": (write_file_tool, "写入文件"),
    "shell": (run_shell, "运行shell命令常用windows shell命令有: dir, cat, echo, mkdir, rm,pwd, mv, cp, find, grep, sort, uniq, head, tail, wc, man, ps, kill, netstat, ifconfig, ip, ping, traceroute, dig, nslookup, whois, telnet, ssh, scp, ftp, rsync, vim, emacs, nano, less, more, head, tail, cat, sort, uniq,"),
    "talk": (talk_tool, "与用户进行对话，参数: message/content/text - 聊天内容"),
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
