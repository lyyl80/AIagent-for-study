import sys
import os

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl
from backend.chat_bridge import ChatBridge
from backend.session_model import SessionListModel

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    app.setApplicationName("MARS AI Agent")
    app.setOrganizationName("MARS")

    # 创建引擎对象
    engine = QQmlApplicationEngine()
    
    # 创建桥接对象
    bridge = ChatBridge()

    session_model = SessionListModel()
    engine.rootContext().setContextProperty("sessionModel", session_model)

    engine.rootContext().setContextProperty("chatBridge", bridge)
    
    engine.addImportPath(os.path.join(os.path.dirname(__file__), "frontend"))

    qml_path = os.path.join(os.path.dirname(__file__), "frontend", "MARS", "main.qml")
    engine.load(QUrl.fromLocalFile(qml_path))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())