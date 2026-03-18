from typing import Dict, Any, Optional, Tuple
from llm.client import ModelManager
from agent.memory import Memory
from prompt.templates import *
from tools import call_tool, get_tool_description, TOOL_REGISTRY
from config import *
import sys
import time
import threading
from config.settings import *

model_manager = ModelManager()

class Spinner:
    """旋转动画类，在思考时显示动画效果"""
    def __init__(self, message="Thinking: "):
        self.message = message
        self.stop_spinning = threading.Event()
        self.spinner_thread = None

    def spin(self):
        spinner_chars = "|/-\\"
        idx = 0
        while not self.stop_spinning.is_set():
            sys.stdout.write(f"\r{self.message}{spinner_chars[idx % len(spinner_chars)]}")
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1

    def start(self):
        if self.spinner_thread is None or not self.spinner_thread.is_alive():
            self.spinner_thread = threading.Thread(target=self.spin)
            self.spinner_thread.daemon = True  # 守护线程，主线程退出时该线程也退出
            self.spinner_thread.start()

    def stop(self):
        if self.spinner_thread and self.spinner_thread.is_alive():
            self.stop_spinning.set()
            self.spinner_thread.join()
            sys.stdout.write("\r")  # 清空当前行
            sys.stdout.flush()


class ChatAgent:
    """
    实现思考-执行-反思循环。
    支持工具调用、历史记忆和用户交互。
    """
    
    def __init__(self, user_input: Optional[str] = None):
        
        self.llm_json = model_manager.llm_json
        model_info = model_manager.get_model_by_key(MODEL_ING)
        self.llm = lambda messages, system_prompt="": model_manager.call_model(
            model_info, 
            [{"role": "user", "content": messages}] if isinstance(messages, str) else messages,
            system_prompt
        )
        self.history = Memory(user_input=user_input)
        self.user_input = user_input
        self.tools = TOOL_REGISTRY
        self.max_steps = 100
        self.debug = Debugmode # 调试模式
        
    def build_prompt(self) -> str:
        """构建思考提示词
        
        返回:
            str: 格式化后的提示词
        """
        tools_desc = get_tool_description()
        action_schema = ACTION_SCHEMA.format(tools=tools_desc)
        # 只使用最近5步历史记录，避免提示词过长
        recent_history = self.history.get_history(5)
        return THINK_PROMPT.format(
            task=self.user_input,
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
        
        # 创建并启动旋转动画
        spinner = Spinner()
        spinner.start()
        
        try:
            # 调用LLM生成JSON格式的动作（带重试机制）
            result = self.llm_json(prompt, SYSTEM_PROMPT)
        finally:
            # 确保无论发生什么情况都会停止动画
            spinner.stop()
        
        if self.debug:
            print(f"[DEBUG] Raw result type: {type(result)}")
            print(f"[DEBUG] Raw result: {result}")
        
        # 处理JSON解析错误（新的错误格式）
        if isinstance(result, tuple):
            error_data, raw_response = result
            error_msg = error_data.get('error', '未知错误')
            print(f"JSON解析失败: {error_msg}")
            
            # 根据错误类型采取不同策略
            if "重试后" in error_msg:
                # 多次重试后仍然失败，尝试简化任务或请求用户帮助
                print("多次重试后仍然无法解析JSON，尝试简化请求...")
                # 返回一个talk动作询问用户或尝试简单操作
                return {
                    "action": {
                        "tool": "talk",
                        "tool_args": {
                            "message": f"抱歉，系统在处理您的请求时遇到技术问题（{error_msg}）。请尝试简化您的请求或重新表述。"
                        }
                    }
                }
            else:
                # 其他错误，同样使用talk工具
                return {
                    "action": {
                        "tool": "talk",
                        "tool_args": {
                            "message": f"处理请求时遇到错误：{error_msg}。请检查您的请求格式或重试。"
                        }
                    }
                }
        
        # 验证返回的JSON结构
        if not isinstance(result, dict):
            print(f"警告：LLM返回了非字典类型: {type(result)}")
            # 尝试包装或返回默认动作
            if isinstance(result, str) and len(result) > 0:
                # 可能是直接的文本响应，使用talk工具
                return {
                    "action": {
                        "tool": "talk",
                        "tool_args": {
                            "message": result[:500]  # 限制长度
                        }
                    }
                }
            else:
                # 返回默认的继续动作
                return {"action": {"tool": "talk", "tool_args": {"message": "继续执行任务"}}}
        
        # 确保有action字段
        if "action" not in result:
            # 如果没有action字段，尝试使用整个结果作为action
            if "tool" in result:
                return {"action": result}
            else:
                print(f"警告：LLM返回的JSON缺少action字段: {result}")
                return {"action": {"tool": "talk", "tool_args": {"message": "请提供具体的操作指令"}}}
        
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
    def execute(self, action: Dict[str, Any]) -> Tuple[Any, str, bool, bool]:
        """执行步骤：调用工具并处理结果
        
        参数:
            action: 动作字典，包含tool和tool_args
            
        返回:
            Tuple[结果, 工具名称, 是否需要用户输入, 是否执行失败]
        """
        tool = action.get("tool")
        tool_args = action.get("tool_args", {})
        
        # 验证工具是否存在
        if tool not in TOOL_REGISTRY:
            tool_name = tool if isinstance(tool, str) else "unknown"
            error_msg = f"Invalid tool: {tool_name}"
            print(f"错误: {error_msg}")
            return (error_msg, tool_name, False, True)
        
        # 打印工具调用信息（talk工具除外）
        if tool != "talk":
            print(f"Using tool: {tool}")
            if tool_args:
                args_str = ", ".join([f"{k}={repr(v)[:50]}" for k, v in tool_args.items()])
                if args_str:
                    print(f"  Args: {args_str}")
        failed = False
        # 调用工具
        try:
            result = call_tool(tool, **tool_args)
        except Exception as e:
            error_msg = f"工具调用异常: {str(e)}"
            failed = True
            print(f"错误: {error_msg}")
            return (error_msg, tool, False, True)
        
        # 标准化错误检测
        
        
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
            if failed:
                # 失败时显示完整错误信息
                print(f"Result: {result}")
            elif result and len(str(result)) > 200:
                print(f"Result: {str(result)[:200]}...")
            else:
                print(f"Result: {result}")
            need_user_input = False
        
        return (result, tool, need_user_input, failed)
    
    def step(self) -> Tuple[Dict[str, Any], bool]:
        """单步执行：思考→执行→反思
        
        返回:
            Tuple[动作字典, 是否需要用户输入]
        """
        raw_action = self.think()
        inner_action = raw_action.get("action", raw_action)
        tool_name = inner_action.get("tool", "")
        
        # 执行工具
        result, tool, need_user_input, failed = self.execute(inner_action)
        
        # 决定是否需要反思（优化反思频率）
        should_reflect = False
        
        # 反思条件：
        # 1. 工具执行失败
        # 2. 关键操作（文件写入、内容替换）
        # 3. 每5步反思一次（避免过度反思）
        # 4. 用户明确询问或需要输入
        key_tools = ["write_file", "replace_content", "shell"]
        
        if failed:
            should_reflect = True
            print("工具执行失败，进行反思分析...")
        elif tool_name in key_tools:
            should_reflect = True
            print(f"关键操作 {tool_name}，进行反思...")
        elif len(self.history) % 5 == 0 and tool_name not in ["finish", "talk"]:
            should_reflect = True
            print("定期反思检查...")
        elif need_user_input:
            should_reflect = True
            print("需要用户输入")
        
        # 对于finish工具，不进行反思
        if tool_name == "finish":
            should_reflect = False
        
        # 执行反思（如果需要）
        if should_reflect and tool_name != "talk":
            try:
                reflect = self.reflect(
                    result,
                    tool_name,
                    inner_action.get("tool_args", {})
                )
                self.history.add_conversation({
                    "input": inner_action,
                    "output": result,
                    "reflect": reflect,
                    "failed": failed
                })
            except Exception as e:
                print(f"反思步骤出错: {str(e)}")
                self.history.add_conversation({
                    "input": inner_action,
                    "output": result,
                    "reflect": f"反思出错: {str(e)}",
                    "failed": failed
                })
        else:
            # 不进行反思，直接记录
            self.history.add_conversation({
                "input": inner_action,
                "output": result,
                "failed": failed
            })
        
        return inner_action, need_user_input
    
    def run(self) -> None:
        """运行代理循环（带进度跟踪和停滞检测）"""
        print(f"Task: {self.user_input}")
        
        # 进度跟踪变量
        consecutive_failures = 0
        max_consecutive_failures = 3
        no_progress_steps = 0
        
        for step_num in range(self.max_steps):
            if self.debug:
                print(f"[DEBUG] Step {step_num + 1}/{self.max_steps}")
                print(f"[DEBUG] Failures: {consecutive_failures}, No-progress: {no_progress_steps}")
            
            action, need_user_input = self.step()
            
            # 检查步骤是否失败（从历史记录中获取）
            recent_history = self.history.get_history(1)
            if recent_history:
                last_step = recent_history[0]
                failed = last_step.get("failed", False)
                # 更新失败计数器
                if failed:
                    consecutive_failures += 1
                    print(f"警告：连续失败次数: {consecutive_failures}/{max_consecutive_failures}")

                else:
                    # 成功执行，重置失败计数器
                    consecutive_failures = 0
            # 检查是否完成任务
            if action.get("tool") == "finish":
                print("Task completed.")
                break
            
            # 如果需要用户输入，获取并添加到历史记录
            if need_user_input:
                try:
                    user_input = input("You: ")
                    
                    # 检查是否是退出命令
                    if user_input.lower() in ['exit', 'quit']:
                        print("收到退出命令，结束任务。")
                        break
                    
                    # 将用户输入添加到历史记录中，作为对需要输入的回应
                    self.history.add_conversation({
                        "input": {"tool": "user", "tool_args": {"message": user_input}},
                        "output": user_input,
                        "reflect": "用户输入回应"
                    })
                    
                    # 更新当前用户输入，以便下一次思考可以参考
                    self.user_input = user_input
                    
                    # 跳过本次循环的其余部分，继续下一步
                    continue
                except (KeyboardInterrupt, EOFError):
                    print("\n用户中断输入")
                    # 添加中断记录
                    self.history.add_conversation({
                        "input": {"tool": "user", "tool_args": {"message": "[用户中断]"}},
                        "output": "[用户中断]",
                        "reflect": "用户中断输入"
                    })
                    break
        
        # 循环结束检查
        if step_num == self.max_steps - 1:
            print(f"达到最大步骤限制 ({self.max_steps})，任务可能未完成")
            # 添加一个finish动作
            self.history.add_conversation({
                "input": {"tool": "finish", "tool_args": {"response": f"达到最大步骤限制 ({self.max_steps})"}},
                "output": "任务因步骤限制而结束"
            })
