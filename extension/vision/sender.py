import json
import socket
import struct

import cv2
import numpy as np

HOST = "127.0.0.1"
PORT = 12345
JPEG_QUALITY = 80


class VisionSender:
    def __init__(self, host=HOST, port=PORT):
        self._addr = (host, port)
        self._sock = None

    def connect(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect(self._addr)
            self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            return True
        except Exception:
            self._sock = None
            return False

    def send(self, frame: np.ndarray, boxes: list[dict]):
        if self._sock is None:
            if not self.connect():
                return False
        try:
            ret, jpeg = cv2.imencode(".jpg", frame, [
                cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY
            ])
            if not ret:
                return False
            jpeg_bytes = jpeg.tobytes()
            payload = {
                "boxes": [{
                    "x1": b["x1"], "y1": b["y1"],
                    "x2": b["x2"], "y2": b["y2"],
                    "X": b.get("X", 0.0), "Y": b.get("Y", 0.0), "Z": b.get("Z", 0.0),
                    "conf": b.get("conf", 0.0), "cls": b.get("cls", ""),
                    "id": b.get("id", -1),
                } for b in boxes],
            }
            json_bytes = json.dumps(payload).encode("utf-8")
            self._sock.sendall(struct.pack("!I", len(jpeg_bytes)))
            self._sock.sendall(jpeg_bytes)
            self._sock.sendall(struct.pack("!I", len(json_bytes)))
            self._sock.sendall(json_bytes)
            return True
        except (ConnectionError, OSError):
            self._sock = None
            return False

    def close(self):
        if self._sock:
            self._sock.close()
            self._sock = None
