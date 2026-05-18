"""
Qt GUI应用程序入口

启动MARS AI Agent的图形界面版本，初始化：
- Qt应用程序和QML引擎
- 聊天桥接器（后端通信层）
- 默认字体配置（避免Windows字体警告）

加载QML主界面并进入事件循环。
"""
import sys
import os

# 高DPI支持（使QML字体在Windows上保持清晰）
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

# 设置Qt Quick Controls样式为Basic（简洁风格）
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtGui import QGuiApplication, QFont
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl
from backend.chat_bridge import ChatBridge

if __name__ == "__main__":
    # 创建Qt应用程序实例
    app = QGuiApplication(sys.argv)
    app.setApplicationName("MARS AI Agent")
    app.setOrganizationName("MARS")
    
    # 设置默认字体，Segoe UI + Segoe UI Variable 适合高DPI渲染
    default_font = QFont("Segoe UI", 10)
    app.setFont(default_font)

    # 创建QML应用程序引擎
    engine = QQmlApplicationEngine()
    
    # 创建聊天桥接器并注册到QML上下文
    bridge = ChatBridge()
    engine.rootContext().setContextProperty("chatBridge", bridge)
    
    # 添加前端模块导入路径
    engine.addImportPath(os.path.join(os.path.dirname(__file__), "frontend"))

    # 加载主QML文件
    qml_path = os.path.join(os.path.dirname(__file__), "frontend", "MARS", "main.qml")
    engine.load(QUrl.fromLocalFile(qml_path))

    # 检查是否成功加载根对象
    if not engine.rootObjects():
        sys.exit(-1)

    # 进入Qt事件循环
    sys.exit(app.exec())
