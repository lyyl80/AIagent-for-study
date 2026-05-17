import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path: sys.path.insert(0,project_root)

from PySide6.QtCore import QObject, Slot, Signal, Property
from core.agent.memory import Memory
from core.tools import call_tool, list_tools, get_tool_description
from backend.worker import ChatWorker
from core.tools import TOOL_REGISTRY
from core.config.settings import switch_model


class ChatBridge(QObject):
    # ====== 向 QML 发射的信号 ======
    messageReceived = Signal(str, str)
    toolCalled = Signal(str, str, str)
    thinkingChanged = Signal(bool)
    errorOccurred = Signal(str)
    sessionListUpdated = Signal(list)
    sessionLoaded = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_memory = Memory()
        self._is_thinking = False
        self._worker = None

    # ====== isThinking 属性 ======
    @Property(bool, notify=thinkingChanged)
    def isThinking(self):
        return self._is_thinking

    @isThinking.setter
    def isThinking(self, value):
        if self._is_thinking != value:
            self._is_thinking = value
            self.thinkingChanged.emit(value)

    # ====== QML 调用的插槽 ======
    @Slot(str)
    def sendMessage(self, text):
        if self._worker and self._worker.isRunning():
            self.errorOccurred.emit("请等待当前任务完成")
            return

        self.isThinking = True
        self._current_memory.add_message("user", text)
        self.messageReceived.emit("user", text)

        self._worker = ChatWorker(text, memory=self._current_memory)
        self._worker.textChunk.connect(self._on_text_chunk)
        self._worker.toolInvoked.connect(self._on_tool_invoked)
        self._worker.stepCompleted.connect(self._on_step_completed)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.errorHappened.connect(self._on_worker_error)
        self._worker.start()

    def _on_text_chunk(self, chunk):
        self.messageReceived.emit("ai", chunk)

    def _on_tool_invoked(self, tool_name, args, result):
        self.toolCalled.emit(tool_name, args, result)

    def _on_step_completed(self, current, total):
        pass

    def _on_worker_finished(self):
        self.isThinking = False
        if self._worker:
            self._worker.wait(3000)
            self._worker = None

    def _on_worker_error(self, msg):
        self.errorOccurred.emit(msg)
        self.isThinking = False
        if self._worker:
            self._worker.wait(3000)
            self._worker = None

    @Slot()
    def newSession(self):
        self._current_memory = Memory()
        self._current_memory.save()
        

    @Slot()
    def clearHistory(self):
        self._current_memory.clear()

    @Slot(str)
    def loadSession(self, filename):
        try:
            self._current_memory = Memory.load_session(filename)
            self.sessionLoaded.emit(filename)
            self._rebuild_chat()
        except Exception as e:
            self.errorOccurred.emit(f"加载会话失败: {e}")

    def _rebuild_chat(self):
        """从 Memory.history 重建聊天消息到 QML"""
        for entry in self._current_memory.history:
            if "role" in entry and entry.get("role") == "user":
                self.messageReceived.emit("user", entry.get("content", ""))
            elif "input" in entry:
                tool = entry.get("input", {}).get("tool", "")
                output = entry.get("output", "")
                if tool in ("talk", "finish"):
                    self.messageReceived.emit("ai", output)
                else:
                    args = entry.get("input", {}).get("tool_args", {})
                    self.toolCalled.emit(tool, str(args), output)

    @Slot(str)
    def deleteSession(self, filename):
        import os as _os
        session_path = _os.path.join("session", filename + ".json")
        if _os.path.exists(session_path):
            _os.remove(session_path)
        self.refreshSessions()

    @Slot()
    def refreshSessions(self):
        sessions = Memory.list_sessions()
        self.sessionListUpdated.emit(sessions)

    @Slot(result=str)
    def getToolDescriptions(self):
        return get_tool_description()

    @Slot(result=list)
    def getToolNames(self):
        return list_tools()

    @Slot(result=list)
    def getModelOptions(self):
        from core.llm.client import ModelManager
        mgr = ModelManager()
        opts = mgr.get_model_options()
        return [{"label": k, "key": v["key"]} for k, v in opts.items()]

    @Slot(result=list)
    def getTools(self):
        result = []
        for name, (func, desc, schema) in TOOL_REGISTRY.items():
            if name in ("talk", "finish"):
                continue
            entry = {
                "name": name,
                "description": desc.strip(),
                "required_params": ", ".join(schema.get("required_params", [])) if schema else "",
                "optional_params": ", ".join(schema.get("optional_params", [])) if schema else ""
            }
            result.append(entry)
        return result

    @Slot(str, str, result=str)
    def callToolDirectly(self, tool_name, args_json):
        import json
        try:
            args = json.loads(args_json) if args_json else {}
            result = call_tool(tool_name, **args)
            return str(result)
        except Exception as e:
            return f"调用失败: {e}"
        
    @Slot(str)
    def switchModel(self, model): 
        switch_model(model)
        

  
