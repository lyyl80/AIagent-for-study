import json
import socket
import struct
import threading

from PySide6.QtCore import QObject, Slot, Signal, Property, QMutex, QByteArray
from PySide6.QtGui import QImage, QPainter, QColor, QPen, QFont
from PySide6.QtQuick import QQuickImageProvider

from backend.target_coordinates import CoordinateManager


class CameraImageProvider(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.ImageType.Image)
        self._image = QImage(640, 480, QImage.Format.Format_RGB32)
        self._image.fill(QColor(20, 20, 20))
        self._mutex = QMutex()

    def requestImage(self, id, size, requestedSize):
        self._mutex.lock()
        img = self._image.copy()
        self._mutex.unlock()
        if img.isNull():
            img = QImage(640, 480, QImage.Format.Format_RGB32)
            img.fill(QColor(20, 20, 20))
        size.setWidth(img.width())
        size.setHeight(img.height())
        return img

    def updateFrame(self, image: QImage):
        self._mutex.lock()
        self._image = image
        self._mutex.unlock()


class VisionBridge(QObject):
    frameCountChanged = Signal()
    connectedChanged = Signal(bool)
    targetCountChanged = Signal(int)

    def __init__(self, provider: CameraImageProvider, parent=None):
        super().__init__(parent)
        self._provider = provider
        self._frame_count = 0
        self._connected = False
        self._target_count = 0
        self._running = False
        self._thread: threading.Thread | None = None
        self._host = "127.0.0.1"
        self._port = 12345
        self.coord_mgr = CoordinateManager()

    @Property(int, notify=frameCountChanged)
    def frameCount(self):
        return self._frame_count

    @Property(bool, notify=connectedChanged)
    def connected(self):
        return self._connected

    @Property(int, notify=targetCountChanged)
    def targetCount(self):
        return self._target_count

    @Slot()
    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._receiver_loop, daemon=True)
        self._thread.start()

    @Slot()
    def stop(self):
        self._running = False

    def _set_connected(self, val: bool):
        if self._connected != val:
            self._connected = val
            self.connectedChanged.emit(val)

    def _set_target_count(self, val: int):
        if self._target_count != val:
            self._target_count = val
            self.targetCountChanged.emit(val)

    @staticmethod
    def _recv_exact(sock: socket.socket, n: int) -> bytes:
        data = b""
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                raise ConnectionError("Connection closed")
            data += chunk
        return data

    def _receiver_loop(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self._host, self._port))
        server.listen(1)

        while self._running:
            try:
                server.settimeout(1.0)
                conn, addr = server.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            self._set_connected(True)
            try:
                while self._running:
                    size_data = self._recv_exact(conn, 4)
                    jpeg_size = struct.unpack("!I", size_data)[0]
                    jpeg_data = self._recv_exact(conn, jpeg_size)

                    size_data = self._recv_exact(conn, 4)
                    json_size = struct.unpack("!I", size_data)[0]
                    json_data = self._recv_exact(conn, json_size)

                    ba = QByteArray(jpeg_data)
                    img = QImage.fromData(ba)
                    if img.isNull():
                        continue

                    data = json.loads(json_data.decode("utf-8"))

                    painter = QPainter(img)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    pen = QPen(QColor(0, 255, 0), 2)
                    painter.setPen(pen)
                    font = QFont("Consolas", 10)
                    painter.setFont(font)

                    boxes = data.get("boxes", [])

                    # 实时写入坐标文件供 AI 读取
                    self.coord_mgr.update(boxes)

                    for box in boxes:
                        x1, y1, x2, y2 = box["x1"], box["y1"], box["x2"], box["y2"]
                        painter.drawRect(x1, y1, x2 - x1, y2 - y1)
                        label = f"#{box['id']} X:{box['X']:.0f} Y:{box['Y']:.0f} Z:{box['Z']:.0f}mm"
                        painter.drawText(x1, y1 - 5, label)

                    painter.setPen(QPen(QColor(0, 255, 0), 2))
                    painter.drawText(10, 30, f"Targets: {len(boxes)}")
                    painter.end()

                    self._provider.updateFrame(img)
                    self._frame_count += 1
                    try:
                        self.frameCountChanged.emit()
                        self._set_target_count(len(boxes))
                    except RuntimeError:
                        break  # 窗口已关闭

            except (ConnectionError, ConnectionResetError, BrokenPipeError, RuntimeError):
                pass
            finally:
                conn.close()
                try:
                    self._set_connected(False)
                    self._set_target_count(0)
                except RuntimeError:
                    pass  # 窗口已关闭

        server.close()
