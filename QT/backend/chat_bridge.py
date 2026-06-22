"""
聊天桥接器模块 - Qt后端核心

作为QML前端与Python后端的通信桥梁，提供：
- 消息发送和接收
- 工具调用执行
- 会话管理（新建、加载、删除）
- 模型切换
- 工具信息查询

使用Qt信号槽机制实现异步通信，避免阻塞UI线程。
"""
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path: sys.path.insert(0,project_root)

from PySide6.QtCore import QObject, Slot, Signal, Property
from PySide6.QtGui import QGuiApplication
from core.agent.memory import Memory
from core.tools import call_tool, list_tools, get_tool_description
from backend.worker import ChatWorker
from core.llm.client import ApiClient, ModelManager
from core.config.settings import Debugmode, save as save_settings, load as load_settings


class ChatBridge(QObject):
    """
    聊天桥接器类
    
    连接QML界面和AI代理核心逻辑，管理会话状态和工作线程。
    通过Qt属性系统和信号槽实现双向数据绑定。
    
    Signals:
        messageReceived (str, str): 收到新消息时发射，参数(role, content)
        toolCalled (str, str, str): 工具被调用时发射，参数(name, args, result)
        thinkingChanged (bool): 思考状态变化时发射
        errorOccurred (str): 发生错误时发射
        sessionListUpdated (list): 会话列表更新时发射
        sessionLoaded (str): 会话加载完成时发射
        
    Attributes:
        _current_memory (Memory): 当前会话的记忆对象
        _is_thinking (bool): 是否正在处理中
        _worker (ChatWorker): 后台工作线程
    """
    
    # ====== 向 QML 发射的信号 ======
    messageReceived = Signal(str, str)      # 消息接收信号
    toolCalled = Signal(str, str, str)      # 工具调用信号
    thinkingChanged = Signal(bool)          # 思考状态变化信号
    errorOccurred = Signal(str)             # 错误信号
    sessionListUpdated = Signal(list)       # 会话列表更新信号
    sessionLoaded = Signal(str)             # 会话加载信号

    def __init__(self, parent=None):
        """
        初始化桥接器
        
        Args:
            parent: Qt父对象
        """
        super().__init__(parent)
        self._current_memory = Memory()
        self._is_thinking = False
        self._worker = None
        self._load_persisted_settings()

    def _load_persisted_settings(self):
        data = load_settings()
        if data.get("env_var_name"):
            ApiClient.env_var_name = data["env_var_name"]
        if data.get("active_model"):
            ApiClient.active_model = data["active_model"]
        custom = data.get("custom_models", {})
        if isinstance(custom, list):
            custom = {k: {"name": k, "type": "local"} for k in custom}
        for key, info in custom.items():
            ModelManager().add_custom_model(key, info.get("name"), info.get("type", "local"))

    def _persist_settings(self):
        custom = {}
        for cat, models in ModelManager.available_models.items():
            if cat == "自定义模型":
                for key, info in models.items():
                    custom[key] = {"name": info.get("name", key), "type": info.get("type", "local")}
        save_settings(
            env_var_name=ApiClient.env_var_name,
            active_model=ApiClient.active_model,
            custom_models=custom,
        )

    # ====== isThinking 属性 ======
    @Property(bool, notify=thinkingChanged)
    def isThinking(self):
        """
        获取思考状态
        
        Returns:
            bool: 是否正在处理任务
        """
        return self._is_thinking

    @isThinking.setter
    def isThinking(self, value):
        """
        设置思考状态并发射通知信号
        
        Args:
            value (bool): 新的思考状态
        """
        if self._is_thinking != value:
            self._is_thinking = value
            self.thinkingChanged.emit(value)

    # ====== QML 调用的插槽 ======
    @Slot(str)
    def sendMessage(self, text):
        """
        发送用户消息并启动AI处理
        
        创建后台工作线程处理消息，连接所有信号处理器。
        如果已有任务在运行，则拒绝新请求。
        
        Args:
            text (str): 用户输入的文本
        """
        if self._worker and self._worker.isRunning():
            self.errorOccurred.emit("请等待当前任务完成")
            return

        self.isThinking = True
        self._current_memory.add_message("user", text)
        self.messageReceived.emit("user", text)

        # 创建并启动工作线程
        self._worker = ChatWorker(text, api_client=ApiClient(), memory=self._current_memory)
        self._worker.textChunk.connect(self._on_text_chunk)
        self._worker.toolInvoked.connect(self._on_tool_invoked)
        self._worker.stepCompleted.connect(self._on_step_completed)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.errorHappened.connect(self._on_worker_error)
        self._worker.start()

    def _on_text_chunk(self, chunk):
        """
        处理文本块回调
        
        Args:
            chunk (str): AI生成的文本片段
        """
        self.messageReceived.emit("ai", chunk)

    def _on_tool_invoked(self, tool_name, args, result):
        """
        处理工具调用回调
        
        Args:
            tool_name (str): 工具名称
            args (str): 工具参数字符串
            result (str): 工具执行结果
        """
        if tool_name in ("talk", "finish"):
            self.messageReceived.emit("ai", result)
        else:
            self.toolCalled.emit(tool_name, args, result)

    def _on_step_completed(self, current, total):
        """
        处理步骤完成回调（当前未使用）
        
        Args:
            current (int): 当前步骤数
            total (int): 总步骤数
        """
        pass

    def _on_worker_finished(self):
        """处理工作线程正常结束"""
        self.isThinking = False
        if self._worker:
            self._worker.wait(3000)
            self._worker = None

    def _on_worker_error(self, msg):
        """
        处理工作线程错误
        
        Args:
            msg (str): 错误消息
        """
        self.errorOccurred.emit(msg)
        self.isThinking = False
        if self._worker:
            self._worker.wait(3000)
            self._worker = None

    @Slot()
    def newSession(self):
        """创建新的空白会话"""
        self._current_memory = Memory()
        self._current_memory.save()
        

    @Slot()
    def clearHistory(self):
        """清空当前会话历史"""
        self._current_memory.clear()

    @Slot(str)
    def copyToClipboard(self, text):
        """复制文本到系统剪贴板"""
        QGuiApplication.clipboard().setText(text)

    @Slot(str)
    def loadSession(self, filename):
        """
        加载指定会话文件
        
        Args:
            filename (str): 会话文件名（不含扩展名）
        """
        try:
            self._current_memory = Memory.load_session(filename)
            self.sessionLoaded.emit(filename)
            self._rebuild_chat()
        except Exception as e:
            self.errorOccurred.emit(f"加载会话失败: {e}")

    def _rebuild_chat(self):
        """
        从Memory历史记录重建聊天界面
        
        遍历memory.history，按时间顺序发射消息和工具调用信号到QML。
        连续的工具调用会自动分组成一个组，避免界面混乱。
        """
        import json
        
        i = 0
        while i < len(self._current_memory.history):
            entry = self._current_memory.history[i]
            if "input" in entry:
                tool = entry.get("input", {}).get("tool", "")
                output = entry.get("output_summary") or entry.get("output", "")
                if tool in ("talk", "finish"):
                    self.messageReceived.emit("ai", output)
                    i += 1
                elif tool == "user":
                    pass  # 用户消息不需要重复显示
                    i += 1
                else:
                    tools = [{"name": tool, "result": output}]
                    j = i + 1
                    while j < len(self._current_memory.history):
                        next_entry = self._current_memory.history[j]
                        if "input" in next_entry:
                            next_tool = next_entry.get("input", {}).get("tool", "")
                            if next_tool not in ("talk", "finish", "user"):
                                next_output = next_entry.get("output_summary") or next_entry.get("output", "")
                                tools.append({"name": next_tool, "result": next_output})
                                j += 1
                                continue
                        break

                    if len(tools) == 1:
                        args = entry.get("input", {}).get("tool_args", {})
                        self.toolCalled.emit(tools[0]["name"], str(args), tools[0]["result"])
                    else:
                        self.toolCalled.emit(tools[0]["name"], "", tools[0]["result"])
                        for k in range(1, len(tools)):
                            self.toolCalled.emit(tools[k]["name"], "", tools[k]["result"])

                    i = j
            else:
                role = entry.get("role", "")
                content = entry.get("content", "")
                if role == "user":
                    self.messageReceived.emit("user", content)
                elif role == "assistant":
                    self.messageReceived.emit("ai", content)
                i += 1

    @Slot(str)
    def deleteSession(self, filename):
        """
        删除指定会话文件
        
        Args:
            filename (str): 要删除的会话文件名
        """
        import os as _os
        session_path = _os.path.join("session", filename + ".json")
        if _os.path.exists(session_path):
            _os.remove(session_path)
        self.refreshSessions()

    @Slot(str, str)
    def renameSession(self, old_filename, new_name):
        """
        重命名会话文件
        
        Args:
            old_filename (str): 旧文件名（不含扩展名）
            new_name (str): 新的会话名称
        """
        try:
            new_filename = Memory.rename_session(old_filename, new_name)
            # 如果当前正在查看的会话被重命名，更新引用
            if self._current_memory and self._current_memory.filename == old_filename:
                self._current_memory.filename = new_filename
                self._current_memory.persist_path = f"session/{new_filename}.json"
            self.refreshSessions()
        except Exception as e:
            self.errorOccurred.emit(f"重命名失败: {e}")

    @Slot(str, str)
    def exportSession(self, filename, export_path):
        """
        导出会话为文本文件
        
        Args:
            filename (str): 会话文件名（不含扩展名）
            export_path (str): 导出文件路径
        """
        try:
            memory = Memory.load_session(filename)
            lines = []
            lines.append(f"MARS AI Agent — 会话导出")
            lines.append(f"会话ID: {memory.session_id}")
            lines.append(f"创建时间: {memory.created_time}")
            lines.append(f"消息数: {len(memory.messages)}")
            lines.append("=" * 60)
            lines.append("")

            for msg in memory.messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    lines.append(f"【我】{content}")
                elif role == "assistant":
                    lines.append(f"【MARS】{content}")
                else:
                    lines.append(f"【{role}】{content}")
                lines.append("")

            # 导出工具调用历史
            tool_entries = [h for h in memory.history if "input" in h]
            if tool_entries:
                lines.append("=" * 60)
                lines.append("工具调用记录:")
                lines.append("")
                for entry in tool_entries:
                    tool_name = entry.get("input", {}).get("tool", "unknown")
                    output = entry.get("output_summary") or entry.get("output", "")
                    lines.append(f"  [{tool_name}] {output[:200]}")
                    lines.append("")

            export_text = "\n".join(lines)
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(export_text)
        except Exception as e:
            self.errorOccurred.emit(f"导出失败: {e}")

    @Slot()
    def refreshSessions(self):
        """刷新会话列表并发射更新信号"""
        sessions = Memory.list_sessions()
        self.sessionListUpdated.emit(sessions)

    @Slot(result=str)
    def getToolDescriptions(self):
        """
        获取所有工具的详细描述文本
        
        Returns:
            str: 格式化的工具描述
        """
        return get_tool_description()

    @Slot(result=list)
    def getToolNames(self):
        """
        获取所有工具名称列表
        
        Returns:
            list: 工具名称字符串列表
        """
        return list_tools()

    @Slot(result=list)
    def getModelOptions(self):
        """
        获取可用模型选项列表
        
        Returns:
            list: 包含label、key、category的字典列表
        """
        opts = ModelManager().get_model_options()
        return [{"label": k, "key": v["key"], "category": v["category"]} for k, v in opts.items()]

    @Slot(result=list)
    def getTools(self):
        """
        获取工具详细信息列表（用于UI展示）
        
        过滤掉内部工具（talk、finish），提取必需和可选参数。
        
        Returns:
            list: 包含name、description、required_params、optional_params、enabled的字典列表
        """
        from core.tools import TOOL_DEFINITIONS
        result = []
        for td in TOOL_DEFINITIONS:
            if td.name in ("talk", "finish"):
                continue
            required = ", ".join(td.input_schema.get("required", []))
            optional = ", ".join(k for k in td.input_schema.get("properties", {}) if k not in td.input_schema.get("required", []))
            result.append({
                "name": td.name,
                "description": td.description,
                "required_params": required,
                "optional_params": optional,
                "enabled": td.name not in ApiClient._disabled_tools
            })
        return result

    @Slot(str, bool)
    def setToolEnabled(self, name, enabled):
        """
        启用或禁用指定工具
        
        禁用的工具将不会出现在SendMessage时发送给AI的上下文里。
        
        Args:
            name (str): 工具名称
            enabled (bool): 是否启用
        """
        if enabled:
            ApiClient._disabled_tools.discard(name)
        else:
            ApiClient._disabled_tools.add(name)

    @Slot(str, str, result=str)
    def callToolDirectly(self, tool_name, args_json):
        """
        直接调用工具（用于测试或调试）
        
        Args:
            tool_name (str): 工具名称
            args_json (str): JSON格式的参数
            
        Returns:
            str: 工具执行结果或错误信息
        """
        import json
        try:
            args = json.loads(args_json) if args_json else {}
            result = call_tool(tool_name, **args)
            return str(result)
        except Exception as e:
            return f"调用失败: {e}"
        
    @Slot(str)
    def switchModel(self, model):
        """
        切换当前使用的LLM模型
        
        Args:
            model (str): 模型标识符
        """
        ApiClient.active_model = model
        self._persist_settings()

    @Slot(str)
    def setApiEnvVarName(self, name):
        """
        设置API密钥的环境变量名
        
        用户可通过Settings页面自定义环境变量名称，
        例如设置为 MY_CUSTOM_KEY 后，代码将读取 os.environ["MY_CUSTOM_KEY"]。
        
        Args:
            name (str): 环境变量名称
        """
        if name.strip():
            ApiClient.env_var_name = name.strip()
            self._persist_settings()

    @Slot(str, str, str)
    def addCustomModel(self, key, name, model_type):
        ModelManager().add_custom_model(key, name, model_type)
        self._persist_settings()

    @Slot(str)
    def removeCustomModel(self, key):
        ModelManager().remove_custom_model(key)
        self._persist_settings()
