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

from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import QUrl, Qt, QRect
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QSplashScreen
from backend.chat_bridge import ChatBridge
from backend.vision_bridge import VisionBridge, CameraImageProvider


def make_splash_pixmap():
    pm = QPixmap(80, 80)
    pm.fill(QColor("#7c3aed"))
    with QPainter(pm) as p:
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor("#7c3aed"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, 80, 80, 18, 18)
        p.setPen(QColor("#ffffff"))
        f = QFont("Segoe UI", 42, QFont.Weight.Bold)
        p.setFont(f)
        p.drawText(QRect(0, 0, 80, 80), Qt.AlignmentFlag.AlignCenter, "M")
    return pm


def create_app_icon():
    pm = QPixmap(64, 64)
    pm.fill(Qt.GlobalColor.transparent)
    with QPainter(pm) as p:
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor("#7c3aed"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(2, 2, 60, 60, 12, 12)
        p.setPen(QColor("#ffffff"))
        f = QFont("Segoe UI", 32, QFont.Weight.Bold)
        p.setFont(f)
        p.drawText(QRect(0, 0, 64, 64), Qt.AlignmentFlag.AlignCenter, "M")
    return QIcon(pm)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("MARS AI Agent")
    app.setOrganizationName("MARS")
    app.setWindowIcon(create_app_icon())

    splash = QSplashScreen(make_splash_pixmap(), Qt.WindowType.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()

    default_font = QFont("Segoe UI", 10)
    app.setFont(default_font)

    engine = QQmlApplicationEngine()

    bridge = ChatBridge()
    engine.rootContext().setContextProperty("chatBridge", bridge)

    camera_provider = CameraImageProvider()
    engine.addImageProvider("camera", camera_provider)

    vision_bridge = VisionBridge(camera_provider)
    engine.rootContext().setContextProperty("visionBridge", vision_bridge)
    app.aboutToQuit.connect(vision_bridge.stop)

    engine.addImportPath(os.path.join(os.path.dirname(__file__), "frontend"))

    qml_path = os.path.join(os.path.dirname(__file__), "frontend", "MARS", "main.qml")
    engine.load(QUrl.fromLocalFile(qml_path))

    if not engine.rootObjects():
        splash.close()
        sys.exit(-1)

    vision_bridge.start()

    splash.close()
    sys.exit(app.exec())
