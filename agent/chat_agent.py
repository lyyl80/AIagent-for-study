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
            return "Invalid tool"
        
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
        
        # 检查是否为finish或talk工具，如果是则跳过反思
        if inner_action.get("tool") in ["finish", "talk"]:
            result = self.execute(inner_action)
            # 直接返回，不进行反思
            self.history.add_conversation({"input": inner_action, "output": result})
            return inner_action
        # 对于非finish和talk工具，执行完整的流程（包括反思）
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