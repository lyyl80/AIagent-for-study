from llm.client import  local_chat , llm_json
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
        print("Thinking...")
        prompt = self.build_prompt()
        response = self.llm_json([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ])
        return response
    def reflect(self,result,tool_name,tool_args):
        messages = REFLECT_PROMPT.format(result=result,history = self.history.get_recent_conversations(),tool_name=tool_name,tool_args=tool_args)
        return self.llm([
        {"role": "user", "content": messages}
        ])
        
    
    def execute(self,action):
        tool = action.get("tool")
        tool_args = action.get("tool_args", {})
        if tool not in TOOL_REGISTRY.keys():
            return "Invalid tool"
        
        # 打印工具调用信息
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
        else:
            # 打印其他工具的结果（截断长输出）
            if result and len(str(result)) > 200:
                print(f"Result: {str(result)[:200]}...")
            else:
                print(f"Result: {result}")
        
        return result
    def step(self):
        raw_action = self.think()
        inner_action = raw_action.get("action", raw_action)
        result = self.execute(inner_action)
        reflect = self.reflect(result, inner_action.get("tool"), inner_action.get("tool_args", {}))
        self.history.add_conversation({"input": inner_action, "output": result, "reflect": reflect})
        return inner_action
    def run(self):
        print(f"Task: {self.task}")
        for i in range(self.max_steps):
            action = self.step()
            if action.get("tool") == "finish":
                print("Task completed.")
                break
