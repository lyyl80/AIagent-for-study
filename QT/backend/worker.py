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
    def execute(self, tool_name: str, tool_input: dict) -> str:
        try:
            return str(call_tool(tool_name, **tool_input))
        except Exception as e:
            return f"Error: {e}"


class ChatWorker(QThread):
    textChunk = Signal(str)
    toolInvoked = Signal(str, str, str)
    stepCompleted = Signal(int, int)
    finished = Signal()
    errorHappened = Signal(str)

    def __init__(self, user_input, api_client=None, memory=None, parent=None):
        super().__init__(parent)
        self.user_input = user_input
        self.api_client = api_client
        self.memory = memory

    def run(self):
        try:
            client = self.api_client or ApiClient()
            runtime = ConversationRuntime(
                system_prompt=SystemPromptBuilder().build(),
                max_iterations=100,
                permission_policy=PermissionPolicy(PermissionMode.DANGER_FULL),
            )

            if self.memory and self.memory.history:
                runtime.messages = memory_to_runtime_messages(self.memory.history)

            executor = ToolExecutor()

            def save_msg(role, content, tool_name="", tool_args=""):
                if self.memory:
                    if role == "user":
                        pass  # already saved by bridge
                    elif role == "assistant":
                        self.memory.add_message("assistant", content)
                    elif role == "tool":
                        self.memory.add_conversation({
                            "input": {"tool": tool_name, "tool_args": tool_args},
                            "output": content,
                        })

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
            import traceback
            self.errorHappened.emit(f"Worker error: {e}\n{traceback.format_exc()}")
        finally:
            self.finished.emit()
