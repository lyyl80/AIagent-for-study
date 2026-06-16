# 关卡 5 —— AI 对话与控制

## 目标

接入 LLM（大语言模型），让 AI 能够理解用户意图并调用工具。从此 AI 成为系统的"大脑"。

## 前置知识

- 关卡 0-4 全部完成
- 拥有 DeepSeek API Key（或本地 Ollama）
- 理解 Function Calling / Tool Use 机制

## 步骤

### 步骤 1: 迁移 AIagent 核心模块

从 `D:\Python\Doc\AIagent` 复制以下文件到项目 `core/` 目录：

```
core/
├── runtime/
│   ├── types.py        ← 从 AIagent/core/runtime/types.py
│   ├── conversation.py ← 从 AIagent/core/runtime/conversation.py
│   ├── permissions.py  ← 从 AIagent/core/runtime/permissions.py
│   └── compact.py      ← 从 AIagent/core/runtime/compact.py
├── llm/
│   └── client.py       ← 从 AIagent/core/llm/client.py
├── prompt/
│   └── builder.py      ← 从 AIagent/core/prompt/builder.py (修改)
├── agent/
│   └── memory.py       ← 从 AIagent/core/agent/memory.py
└── config/
    └── settings.py     ← 已在关卡 0 创建
```

修改 `core/prompt/builder.py` 添加专用系统提示词：

```python
"""系统提示词构建 —— 瓶盖抓取专用版"""
import platform
import datetime


class SystemPromptBuilder:
    """构建发给 LLM 的系统提示词"""

    BOTTLECAP_SYSTEM_PROMPT = """你是瓶盖抓取机器人控制助手。

你拥有的设备:
- Orbbec 深度相机: 实时视频流, 支持瓶盖检测和3D定位
- 4轴机械臂: 串口控制, 支持抓取/释放

你有以下工具可用:
{tool_descriptions}

执行抓取任务的标准流程:
1. 调用 detect_bottlecaps 获取当前画面中所有瓶盖 (ID, 3D坐标, 颜色)
2. 根据用户语义选择目标: 
   - "红色的" → 匹配 color 字段
   - "最左边的" → X坐标最小
   - "最近的那个" → Z坐标最小(距离最近)
   - "最大的" → 比较 real_width
3. 调用 select_bottlecap(id) 在界面上高亮选中
4. 调用 move_arm_to(x, y, z) 移动机械臂
5. 调用 grasp() 执行抓取

安全规则:
- 机械臂操作前必须确认目标存在
- move_arm_to 前检查坐标是否在工作空间内
- 一次只操作一个瓶盖
- 如果工具调用失败, 向用户报告具体错误
"""

    def __init__(self, tool_definitions=None, disabled_tools=None):
        self._tools = tool_definitions or []
        self._disabled = disabled_tools or []

    def build(self):
        active_tools = [
            t for t in self._tools
            if t.get("name") not in self._disabled
        ]
        tool_descs = "\n".join(
            f"- {t['name']}: {t.get('description', '')}"
            for t in active_tools
        )

        env_info = f"""环境信息:
- 操作系统: {platform.system()} {platform.release()}
- 当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 工作目录: {os.getcwd()}
"""

        return env_info + self.BOTTLECAP_SYSTEM_PROMPT.format(
            tool_descriptions=tool_descs
        )
```

### 步骤 2: 编写工具注册

`tools/__init__.py`：

```python
"""工具注册表"""
import json

TOOL_DEFINITIONS = [
    {
        "name": "detect_bottlecaps",
        "description": "获取当前相机画面中检测到的所有瓶盖, 返回ID/3D坐标/颜色/置信度",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "select_bottlecap",
        "description": "在GUI上高亮选中指定ID的瓶盖",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "瓶盖ID"}
            },
            "required": ["id"]
        }
    },
    {
        "name": "get_bottlecap_info",
        "description": "获取指定瓶盖的完整信息(3D坐标、颜色、尺寸)",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "瓶盖ID"}
            },
            "required": ["id"]
        }
    },
    {
        "name": "move_arm_to",
        "description": "移动机械臂末端到指定3D坐标(mm), 机械臂会自动完成逆运动学和平滑步进",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "number", "description": "X坐标(mm), 相机坐标系"},
                "y": {"type": "number", "description": "Y坐标(mm), 相机坐标系"},
                "z": {"type": "number", "description": "Z坐标(mm), 深度距离"}
            },
            "required": ["x", "y", "z"]
        }
    },
    {
        "name": "grasp",
        "description": "闭合夹爪执行抓取动作",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "release",
        "description": "张开夹爪执行释放动作",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_arm_status",
        "description": "查询机械臂当前状态(各轴角度、夹爪开合、忙/闲)",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
]

TOOL_HANDLERS = {}

def register_tool(name, handler):
    TOOL_HANDLERS[name] = handler

def call_tool(name, args):
    if name not in TOOL_HANDLERS:
        return f"错误: 未知工具 '{name}'"
    try:
        result = TOOL_HANDLERS[name](**args)
        return result
    except Exception as e:
        return f"工具执行失败: {e}"
```

### 步骤 3: 实现视觉工具

`tools/vision_tools.py`：

```python
"""视觉工具 — 供 LLM 调用"""
import json
from tools import register_tool


class VisionToolContext:
    """全局视觉上下文 (由 VideoProvider 维护)"""
    _detections = []
    _selected_id = None

    @classmethod
    def update(cls, detections):
        cls._detections = detections

    @classmethod
    def get_detections(cls):
        return cls._detections

    @classmethod
    def set_selected(cls, cap_id):
        cls._selected_id = cap_id

    @classmethod
    def get_selected(cls):
        return cls._selected_id


def detect_bottlecaps():
    """返回当前画面中所有瓶盖"""
    dets = VisionToolContext.get_detections()
    if not dets:
        return "当前画面未检测到瓶盖"

    result = []
    for d in dets:
        item = {
            "id": d["id"],
            "confidence": round(d["confidence"], 3),
        }
        if "X" in d:
            item["x"] = round(d["X"], 1)
            item["y"] = round(d["Y"], 1)
            item["z"] = round(d["Z"], 1)
        if "color" in d:
            item["color"] = d["color"]
        if "real_width" in d:
            item["width_mm"] = round(d["real_width"], 1)
        result.append(item)

    return json.dumps(result, ensure_ascii=False, indent=2)


def select_bottlecap(id: int):
    """高亮选中指定瓶盖"""
    dets = VisionToolContext.get_detections()
    target = next((d for d in dets if d["id"] == id), None)
    if target is None:
        return f"错误: 未找到ID={id}的瓶盖, 当前可用ID: {[d['id'] for d in dets]}"
    VisionToolContext.set_selected(id)
    pos = target.get("X", "?")
    return f"已选中瓶盖 #{id} (置信度: {target['confidence']:.2f}, X={pos})"


def get_bottlecap_info(id: int):
    """获取单个瓶盖完整信息"""
    dets = VisionToolContext.get_detections()
    target = next((d for d in dets if d["id"] == id), None)
    if target is None:
        return f"错误: 未找到ID={id}的瓶盖"
    info = {
        "id": target["id"],
        "bbox": [target["x1"], target["y1"], target["x2"], target["y2"]],
        "confidence": round(target["confidence"], 3),
    }
    if "X" in target:
        info["position_3d"] = {
            "x_mm": round(target["X"], 1),
            "y_mm": round(target["Y"], 1),
            "z_mm": round(target["Z"], 1),
        }
    if "color" in target:
        info["color"] = target["color"]
    if "real_width" in target:
        info["width_mm"] = round(target["real_width"], 1)
    return json.dumps(info, ensure_ascii=False, indent=2)


def register():
    register_tool("detect_bottlecaps", detect_bottlecaps)
    register_tool("select_bottlecap", select_bottlecap)
    register_tool("get_bottlecap_info", get_bottlecap_info)
```

### 步骤 4: 实现机械臂工具

`tools/robot_tools.py`：

```python
"""机械臂工具 — 供 LLM 调用"""
import json
from tools import register_tool


class RobotToolContext:
    """全局机械臂上下文"""
    _arm_client = None
    _coordinator = None

    @classmethod
    def init(cls, arm_client, coordinator):
        cls._arm_client = arm_client
        cls._coordinator = coordinator

    @classmethod
    def get_client(cls):
        return cls._arm_client

    @classmethod
    def get_coordinator(cls):
        return cls._coordinator


def move_arm_to(x: float, y: float, z: float):
    """移动机械臂到目标坐标"""
    client = RobotToolContext.get_client()
    coordinator = RobotToolContext.get_coordinator()

    if client is None:
        return "错误: 机械臂未连接"

    if coordinator and not coordinator.is_workspace_valid(x, y, z):
        return f"错误: 坐标 ({x:.0f}, {y:.0f}, {z:.0f}) 超出工作空间"

    if coordinator:
        rx, ry, rz = coordinator.transform(x, y, z)
    else:
        rx, ry, rz = int(x), int(y), int(z)

    client.send_grasp(rx, ry, rz)
    return f"机械臂已移动到 ({rx}, {ry}, {rz}) 并执行抓取"


def grasp():
    """夹爪闭合"""
    client = RobotToolContext.get_client()
    if client is None:
        return "错误: 机械臂未连接"
    client.send_grasp(0, 0, 0)
    return "夹爪已闭合"


def release():
    """夹爪张开"""
    client = RobotToolContext.get_client()
    if client is None:
        return "错误: 机械臂未连接"
    client.send_release(0, 0, 0)
    return "夹爪已张开"


def get_arm_status():
    """查询状态"""
    client = RobotToolContext.get_client()
    if client is None:
        return "错误: 机械臂未连接"
    return json.dumps(client.status, ensure_ascii=False, indent=2)


def register():
    register_tool("move_arm_to", move_arm_to)
    register_tool("grasp", grasp)
    register_tool("release", release)
    register_tool("get_arm_status", get_arm_status)
```

### 步骤 5: 编写 ChatWorker

`gui/backend/worker.py`：

```python
"""后台 AI 工作线程"""
from PySide6.QtCore import QThread, Signal
from core.runtime.conversation import ConversationRuntime
from tools import TOOL_DEFINITIONS, call_tool
from tools.vision_tools import VisionToolContext


class ChatWorker(QThread):
    """在子线程中运行 ConversationRuntime"""

    textChunk = Signal(str)
    toolInvoked = Signal(str, object)
    finished = Signal(str)
    errorHappened = Signal(str)

    def __init__(self, runtime_context=None, parent=None):
        super().__init__(parent)
        self._ctx = runtime_context
        self._task_text = ""

    def set_context(self, ctx):
        self._ctx = ctx

    def start_task(self, text):
        self._task_text = text
        if not self.isRunning():
            self.start()
        else:
            print("[Worker] 上一个任务仍在执行中")

    def run(self):
        try:
            # 调用 ConversationRuntime
            rt = self._ctx["runtime"]
            rt.run_turn(
                user_input=self._task_text,
                tool_definitions=TOOL_DEFINITIONS,
                tool_executor=self._execute_tool,
                on_text=lambda chunk: self.textChunk.emit(chunk),
                on_tool=lambda name, args: self.toolInvoked.emit(name, args),
            )
            self.finished.emit("任务完成")
        except Exception as e:
            self.errorHappened.emit(str(e))

    def _execute_tool(self, name, args):
        """工具执行 + 视觉上下文更新"""
        result = call_tool(name, args)
        return result
```

### 步骤 6: 更新桥接器整合 AI

修改 `gui/backend/bridge.py` 初始化部分：

```python
class ChatBridge(QObject):
    # ... 其他代码同前

    def __init__(self, camera, detector=None, arm_client=None, coordinator=None, parent=None):
        super().__init__(parent)
        self._messages = []
        self._fps_text = "FPS: --"

        self.video_provider = VideoProvider(camera, detector)
        self.video_provider.frameReady.connect(self._on_frame)
        self.video_provider.fpsChanged.connect(self._on_fps)

        # 初始化视觉上下文
        from tools.vision_tools import VisionToolContext, register as register_vision
        register_vision()

        # 初始化机械臂上下文
        from tools.robot_tools import RobotToolContext
        RobotToolContext.init(arm_client, coordinator)

        from tools.robot_tools import register as register_robot
        register_robot()

        # Worker
        self.worker = ChatWorker()
        self.worker.textChunk.connect(self._on_text_chunk)
        self.worker.toolInvoked.connect(self._on_tool)
        self.worker.finished.connect(self._on_finished)
        self.worker.errorHappened.connect(self._on_error)

    def _on_frame(self, qimg, detections):
        # 每次帧更新时同步检测结果到视觉上下文
        from tools.vision_tools import VisionToolContext
        VisionToolContext.update(detections)
        self.frameReady.emit(qimg, detections)
```

### 步骤 7: 更新 GUI 入口

`gui/main.py`：

```python
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("瓶盖抓取系统")

    camera = create_camera(use_mock=True)
    camera.start()

    detector = BottlecapDetector()

    arm = create_arm_client(use_mock=True)
    arm.connect()

    from extension.robot.coordinator import CoordinateTransformer
    coordinator = CoordinateTransformer()

    bridge = ChatBridge(camera, detector, arm, coordinator)
    bridge.start_video(fps=30)

    engine = QQmlApplicationEngine()
    qml_dir = os.path.dirname(os.path.abspath(__file__))
    qml_path = os.path.join(qml_dir, "frontend", "main.qml")
    context = engine.rootContext()
    context.setContextProperty("bridge", bridge)
    engine.load(QUrl.fromLocalFile(qml_path))

    code = app.exec()
    bridge.stop_video()
    camera.stop()
    arm.disconnect()
    sys.exit(code)
```

## 运行验证

```powershell
python main.py --gui
```

1. 在 AI 对话输入框输入: `"检测瓶盖"` → AI 应调用 `detect_bottlecaps` 工具
2. 输入: `"夹取ID为0的瓶盖"` → AI 调用 `select_bottlecap(0)` + `move_arm_to(...)` + `grasp()`
3. 右侧面板显示工具调用记录

## 常见问题

**Q: AI 无响应？**
A: 检查 `.env` 中 `DEEPSEEK_API_KEY` 是否正确，网络是否可达。

**Q: 工具调用不被 LLM 识别？**
A: 确认 `TOOL_DEFINITIONS` 的 JSON Schema 格式正确（函数名和参数描述必须匹配）。

**Q: 本地 Ollama 模型不理解工具调用？**
A: 部分本地模型不支持原生 tool_calls，需升级到支持 function calling 的版本（如 llama3.1:8b）。

## 通关奖励

- AI 能正确调用 `detect_bottlecaps` 返回瓶盖列表
- AI 能根据语义选择目标瓶盖
- AI 工具调用成功执行并返回结果
