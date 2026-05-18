"""
聊天工作线程模块

在后台线程中执行AI代理的对话逻辑，避免阻塞UI主线程。
通过Qt信号将进度和结果异步通知给前端界面。
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtCore import QThread, Signal
from core.llm.client import ApiClient
from core.runtime.conversation import ConversationRuntime, memory_to_runtime_messages
from core.runtime.permissions import PermissionPolicy, PermissionMode
from core.prompt.builder import SystemPromptBuilder
from core.tools import call_tool


class ToolExecutor:
    """
    工具执行器类

    封装工具调用的异常处理，供ConversationRuntime使用。
    """

    def __init__(self, disabled_tools: set = None):
        self._disabled_tools = disabled_tools or set()

    def execute(self, tool_name: str, tool_input: dict) -> str:
        if tool_name in self._disabled_tools:
            return "工具已被禁用"
        try:
            return str(call_tool(tool_name, **tool_input))
        except Exception as e:
            return f"Error: {e}"


class ChatWorker(QThread):
    """
    聊天工作线程类
    
    在独立线程中运行完整的对话轮次（run_turn），包括：
    - LLM调用
    - 工具执行
    - 消息保存
    
    通过信号实时向前端报告进度。
    
    Signals:
        textChunk (str): AI生成的文本片段
        toolInvoked (str, str, str): 工具被调用，参数(name, args, result)
        stepCompleted (int, int): 步骤完成，参数(current, total)
        finished (): 任务完成
        errorHappened (str): 发生错误
        
    Attributes:
        user_input (str): 用户输入文本
        api_client (ApiClient): LLM客户端实例
        memory (Memory): 会话记忆对象
    """
    
    textChunk = Signal(str)              # 文本块信号
    toolInvoked = Signal(str, str, str)  # 工具调用信号
    stepCompleted = Signal(int, int)     # 步骤完成信号
    finished = Signal()                  # 完成信号
    errorHappened = Signal(str)          # 错误信号

    def __init__(self, user_input, api_client=None, memory=None, parent=None):
        """
        初始化工作线程
        
        Args:
            user_input (str): 用户输入的文本
            api_client (ApiClient, optional): LLM客户端，默认创建新实例
            memory (Memory, optional): 会话记忆对象
            parent: Qt父对象
        """
        super().__init__(parent)
        self.user_input = user_input
        self.api_client = api_client
        self.memory = memory

    def run(self):
        """
        线程主函数
        
        执行完整的对话流程：
        1. 创建运行时环境
        2. 加载历史消息（如果有）
        3. 执行对话轮次
        4. 保存消息到memory
        5. 发射完成信号
        
        异常时发射错误信号并包含堆栈追踪。
        """
        try:
            client = self.api_client or ApiClient()
            runtime = ConversationRuntime(
                system_prompt=SystemPromptBuilder().build(disabled_tools=ApiClient._disabled_tools),
                max_iterations=100,
                permission_policy=PermissionPolicy(PermissionMode.DANGER_FULL),
            )

            # 加载历史消息到运行时
            if self.memory and self.memory.history:
                runtime.messages = memory_to_runtime_messages(self.memory.history)

            executor = ToolExecutor(disabled_tools=ApiClient._disabled_tools)

            def save_msg(role, content, tool_name="", tool_args=""):
                """
                保存消息到memory
                
                Args:
                    role (str): 消息角色
                    content: 消息内容
                    tool_name (str): 工具名称（仅tool角色）
                    tool_args (str): 工具参数（仅tool角色）
                """
                if self.memory:
                    if role == "user":
                        pass  # 用户消息已由bridge保存
                    elif role == "assistant":
                        self.memory.add_message("assistant", content)
                    elif role == "tool":
                        if tool_name in ("talk", "finish"):
                            self.memory.add_message("assistant", content)
                        else:
                            self.memory.add_conversation({
                                "input": {"tool": tool_name, "tool_args": tool_args},
                                "output": content,
                            })

            # 执行对话轮次
            runtime.run_turn(
                self.user_input, client, executor,
                on_text=lambda text: self.textChunk.emit(text + "\n"),
                on_tool=lambda name, args, result, failed:
                    self.toolInvoked.emit(
                        name, str(args), str(result) if not failed else f"执行失败: {result}"
                    ),
                on_save=save_msg,
            )

        except Exception as e:
            # 异常时发送详细错误信息
            import traceback
            self.errorHappened.emit(f"Worker error: {e}\n{traceback.format_exc()}")
        finally:
            # 无论成功或失败都发射完成信号
            self.finished.emit()
