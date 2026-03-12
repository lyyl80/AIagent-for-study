from typing import Dict, Any, Optional, Tuple
from llm.client import ModelManager
from agent.memory import Memory
from prompt.templates import SYSTEM_PROMPT, THINK_PROMPT, ACTION_SCHEMA, REFLECT_PROMPT
from tools import call_tool, get_tool_description, TOOL_REGISTRY
from config import *

model_manager = ModelManager()
class ChatAgent:
    """
    实现思考-执行-反思循环。
    支持工具调用、历史记忆和用户交互。
    """
    
    def __init__(self, task: str,user_input: Optional[str] = None):
        
        self.llm_json = model_manager.llm_json
        model_info = model_manager.get_model_by_key(MODEL_ING)
        self.llm = lambda messages, system_prompt="": model_manager.call_model(
            model_info, 
            [{"role": "user", "content": messages}] if isinstance(messages, str) else messages,
            system_prompt
        )
        self.history = Memory(user_input=user_input)
        self.task = task
        self.max_steps = 10
        self.debug = True  # 调试模式
        
    def build_prompt(self) -> str:
        """构建思考提示词
        
        返回:
            str: 格式化后的提示词
        """
        tools_desc = get_tool_description()
        action_schema = ACTION_SCHEMA.format(tools=tools_desc)
        # 只使用最近3步历史记录，避免提示词过长
        recent_history = self.history.get_recent_steps(3)
        return THINK_PROMPT.format(
            task=self.task,
            history=recent_history,
            tools=tools_desc,
            action_schema=action_schema
        )
    
    def think(self) -> Dict[str, Any]:
        """思考步骤：生成下一步动作
        
        返回:
            Dict[str, Any]: 动作字典，包含工具和参数
        """
        prompt = self.build_prompt()
        
        
        # 调用LLM生成JSON格式的动作
        result = self.llm_json( prompt, SYSTEM_PROMPT)
        
        if self.debug:
            print(f"[DEBUG] Raw result type: {type(result)}")
            print(f"[DEBUG] Raw result: {result}")
        
        # 处理JSON解析错误
        if isinstance(result, tuple):
            error_data, raw_response = result
            print(f"JSON解析错误: {error_data.get('error', '未知错误')}")
            print(f"原始响应: {raw_response[:200]}...")
            # 返回finish动作以结束任务
            return {"action": {"tool": "finish"}}
        
        return result
    
    def reflect(self, result: Any, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """反思步骤：分析工具执行结果
        
        参数:
            result: 工具执行结果
            tool_name: 工具名称
            tool_args: 工具参数
            
        返回:
            str: 反思内容
        """
        messages = REFLECT_PROMPT.format(
            result=result,
            history=self.history.get_history(),
            tool_name=tool_name,
            tool_args=tool_args
        )
        return self.llm(messages)
    
    def execute(self, action: Dict[str, Any]) -> Tuple[Any, str, bool]:
        """执行步骤：调用工具并处理结果
        
        参数:
            action: 动作字典，包含tool和tool_args
            
        返回:
            Tuple[结果, 工具名称, 是否需要用户输入]
        """
        tool = action.get("tool")
        tool_args = action.get("tool_args", {})
        
        # 验证工具是否存在
        if tool not in TOOL_REGISTRY:
            tool_name = tool if isinstance(tool, str) else "unknown"
            return ("Invalid tool", tool_name, False)
        
        # 打印工具调用信息（talk工具除外）
        if tool != "talk":
            print(f"Using tool: {tool}")
            if tool_args:
                args_str = ", ".join([f"{k}={repr(v)[:50]}" for k, v in tool_args.items()])
                if args_str:
                    print(f"  Args: {args_str}")
        
        # 调用工具
        result = call_tool(tool, **tool_args)
        
        # 处理工具结果
        if tool == "talk":
            message = tool_args.get("message") or tool_args.get("content") or ""
            if message:
                print(f"Assistant: {message}")
            # 启发式判断是否需要用户输入
            need_user_input = any(keyword in message for keyword in 
                ["?", "？", "请", "提供", "请输入", "请提供", "请告诉我", 
                 "需要什么", "需要哪些", "吗", "呢", "如何", "什么", "哪些", "谁", "哪里"])
        else:
            # 打印其他工具的结果（截断长输出）
            if result and len(str(result)) > 200:
                print(f"Result: {str(result)[:200]}...")
            else:
                print(f"Result: {result}")
            need_user_input = False
        
        return (result, tool, need_user_input)
    
    def step(self) -> Tuple[Dict[str, Any], bool]:
        """单步执行：思考→执行→反思
        
        返回:
            Tuple[动作字典, 是否需要用户输入]
        """
        raw_action = self.think()
        inner_action = raw_action.get("action", raw_action)
        
        # 对于finish和talk工具，跳过反思
        if inner_action.get("tool") in ["finish", "talk"]:
            result, tool, need_user_input = self.execute(inner_action)
            self.history.add_conversation({
                "input": inner_action,
                "output": result
            })
            return inner_action, need_user_input
        
        # 对于其他工具，执行完整的思考-执行-反思循环
        result, tool, need_user_input = self.execute(inner_action)
        reflect = self.reflect(
            result,
            inner_action.get("tool"),
            inner_action.get("tool_args", {})
        )
        self.history.add_conversation({
            "input": inner_action,
            "output": result,
            "reflect": reflect
        })
        return inner_action, need_user_input
    
    def run(self) -> None:
        """运行代理循环"""
        print(f"Task: {self.task}")
        
        for step_num in range(self.max_steps):
            action, need_user_input = self.step()
            
            # 检查是否完成任务
            if action.get("tool") == "finish":
                print("Task completed.")
                break
            
            # 如果需要用户输入，获取并添加到历史记录
            if need_user_input:
                user_input = input("You: ")
                self.history.add_conversation({
                    "input": {"tool": "user", "tool_args": {"message": user_input}},
                    "output": user_input,
                    "reflect": "用户输入"
                })