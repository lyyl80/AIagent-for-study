from llm.client import  local_chat , llm_json, local_chat_no_print
from agent.memory import Memory
from prompt.templates import SYSTEM_PROMPT , THINK_PROMPT , ACTION_SCHEMA, REFLECT_PROMPT
from tools import call_tool, get_tool_description, TOOL_REGISTRY
class ChatAgent:
    def __init__(self, task):
        self.llm_json = llm_json
        self.llm = local_chat
        self.history= Memory()
        self.task = task
        self.max_steps = 10

    def build_prompt(self):
        tools_desc = get_tool_description()
        return THINK_PROMPT.format(task=self.task, history=self.history.get_recent_conversations(), tools=tools_desc, action_schema=ACTION_SCHEMA.format(tools=tools_desc))
    def think(self):
        prompt = self.build_prompt()
    
        # 解析JSON，不显示任何内容
        result = self.llm_json([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ])
        
        # 处理llm_json可能的元组返回（JSON解析失败的情况）
        if isinstance(result, tuple):
            error_data, raw_response = result
            print(f"JSON解析错误: {error_data.get('error', '未知错误')}")
            print(f"原始响应: {raw_response[:200]}...")
            # 返回一个finish动作以结束任务
            return {"action": {"tool": "finish"}}
        
        return result
    def reflect(self,result,tool_name,tool_args):
        messages = REFLECT_PROMPT.format(result=result,history = self.history.get_recent_conversations(),tool_name=tool_name,tool_args=tool_args)
        return self.llm([
        {"role": "user", "content": messages}
        ], prefix="Reflecting: ")
        
    
    def execute(self,action):
        tool = action.get("tool")
        tool_args = action.get("tool_args", {})
        if tool not in TOOL_REGISTRY.keys():
            return ("Invalid tool", tool, False)
        
        # 对于talk工具，不打印工具调用信息
        if tool != "talk":
            # 打印工具调用信息（除了talk工具）
            print(f"Using tool: {tool}")
            if tool_args:
                # 简化参数显示，避免过长
                args_str = ", ".join([f"{k}={repr(v)[:50]}" for k, v in tool_args.items()])
                if args_str:
                    print(f"  Args: {args_str}")
        
        result = call_tool(tool, **tool_args)
        
        # 对于talk工具，打印助理回复，不打印结果
        if tool == "talk":
            message = tool_args.get("message") or tool_args.get("content") or ""
            if message:
                print(f"Assistant: {message}")
            # 启发式判断是否需要用户输入：如果消息包含问号或中文询问词
            need_user_input = any(keyword in message for keyword in ["?", "？", "请", "提供", "请输入", "请提供", "请告诉我", "需要什么", "需要哪些", "吗", "呢", "如何", "什么", "哪些", "谁", "哪里"])
        else:
            # 打印其他工具的结果（截断长输出）
            if result and len(str(result)) > 200:
                print(f"Result: {str(result)[:200]}...")
            else:
                print(f"Result: {result}")
            need_user_input = False
        
        return (result, tool, need_user_input)
    def step(self):
        raw_action = self.think()
        inner_action = raw_action.get("action", raw_action)
        
        # 检查是否为finish或talk工具，如果是则跳过反思
        if inner_action.get("tool") in ["finish", "talk"]:
            result, tool, need_user_input = self.execute(inner_action)
            # 直接返回，不进行反思
            self.history.add_conversation({"input": inner_action, "output": result})
            return inner_action, need_user_input
        # 对于非finish和talk工具，执行完整的流程（包括反思）
        result, tool, need_user_input = self.execute(inner_action)
        reflect = self.reflect(result, inner_action.get("tool"), inner_action.get("tool_args", {}))
        self.history.add_conversation({"input": inner_action, "output": result, "reflect": reflect})
        return inner_action, need_user_input
    def run(self):
        print(f"Task: {self.task}")
        for i in range(self.max_steps):
            action, need_user_input = self.step()
            if action.get("tool") == "finish":
                print("Task completed.")
                break
            if need_user_input:
                user_input = input("You: ")
                # 将用户输入添加到历史记录中，作为虚拟工具调用
                self.history.add_conversation({
                    "input": {"tool": "user", "tool_args": {"message": user_input}},
                    "output": user_input,
                    "reflect": "用户输入"
                })