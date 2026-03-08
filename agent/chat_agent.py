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
        result = call_tool(tool, **tool_args)
        return result
    def step(self):
        print("Thinking...")
        raw_action = self.think()
        print(f"Action: {raw_action}")
        # 提取内部的action，兼容嵌套格式
        inner_action = raw_action.get("action", raw_action)
        print("Executing...")
        result = self.execute(inner_action)
        print(f"Result: {result}")
        print("Reflecting...")
        reflect = self.reflect(result, inner_action.get("tool"), inner_action.get("tool_args", {}))
        print(f"Reflect: {reflect}")
        self.history.add_conversation({"input": inner_action, "output": result, "reflect": reflect})
        return inner_action
    def run(self):
        print(f"Starting task: {self.task}")
        for i in range(self.max_steps):
            action = self.step()
            if action.get("tool") == "finish":
                print(f"Task completed: {self.task}")
                break
        print(f"Finished task: {self.task}")
