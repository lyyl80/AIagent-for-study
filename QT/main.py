import sys
import os

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    app.setApplicationName("MARS AI Agent")
    app.setOrganizationName("MARS")

    engine = QQmlApplicationEngine()
    
    # 添加 frontend 目录到 QML 导入路径
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
    engine.addImportPath(frontend_path)
    
    qml_path = os.path.join(os.path.dirname(__file__), "frontend", "main.qml")
    engine.load(QUrl.fromLocalFile(qml_path))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())