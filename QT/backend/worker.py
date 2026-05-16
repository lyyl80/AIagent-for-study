import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtCore import QThread, Signal
from core.agent.chat_agent import ChatAgent
from core.agent.memory import Memory
from core.config.settings import MODEL_ING, Debugmode

class ChatWorker(QThread):
    textChunk = Signal(str)
    toolInvoked = Signal(str, str, str)
    stepCompleted = Signal(int, int)
    finished = Signal()
    errorHappened = Signal(str)

    def __init__(self, user_input, memory=None, parent=None):
        super().__init__(parent)
        self.user_input = user_input
        self.memory = memory or Memory()

    def run(self):
        try:
            

            agent = ChatAgent(user_input=self.user_input, memory=self.memory)
            self._run_agent(agent)

        except Exception as e:
            import traceback
            self.errorHappened.emit(f"Worker error: {e}\n{traceback.format_exc()}")
        finally:
            self.finished.emit()

    def _run_agent(self, agent):
        """复用 ChatAgent.step() 循环，发射信号"""
        consecutive_failures = 0

        for step_num in range(agent.max_steps):
            action, need_user_input = agent.step()

            recent = agent.history.get_history(1)
            failed = recent and recent[0].get("failed", False) if recent else False
            actual_result = recent[0].get("output", "") if recent else ""

            tool_name = action.get("tool", "")
            tool_args = action.get("tool_args", {})

            self.stepCompleted.emit(step_num + 1, agent.max_steps)

            if tool_name in ("talk", "finish"):
                msg = tool_args.get("message", "") or tool_args.get("content", "") or tool_args.get("response", "")
                if msg:
                    self.textChunk.emit(msg + "\n")
            else:
                self.toolInvoked.emit(tool_name, str(tool_args),
                                      actual_result if not failed else f"执行失败: {actual_result}")

            if failed:
                consecutive_failures += 1
                if consecutive_failures >= 3:
                    self.textChunk.emit("连续失败次数过多，终止\n")
                    break
            else:
                consecutive_failures = 0

            if tool_name == "finish":
                msg = tool_args.get("response", "") 
                if msg:
                    self.textChunk.emit(msg + "\n")
                break

            if need_user_input:
                self.textChunk.emit("[等待用户输入...]\n")
                break
