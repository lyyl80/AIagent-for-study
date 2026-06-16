import json
import socket
import struct

import cv2
import numpy as np

HOST = "127.0.0.1"
PORT = 12345


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Connection closed")
        data += chunk
    return data


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"[Vision] Listening on {HOST}:{PORT} ...")

    try:
        while True:
            print("[Vision] Waiting for detector ...")
            conn, addr = server.accept()
            print(f"[Vision] Connected: {addr}")

            try:
                while True:
                    size_data = _recv_exact(conn, 4)
                    jpeg_size = struct.unpack("!I", size_data)[0]
                    jpeg_data = _recv_exact(conn, jpeg_size)
                    img = cv2.imdecode(
                        np.frombuffer(jpeg_data, dtype=np.uint8), cv2.IMREAD_COLOR
                    )
                    if img is None:
                        continue

                    size_data = _recv_exact(conn, 4)
                    json_size = struct.unpack("!I", size_data)[0]
                    json_data = _recv_exact(conn, json_size)
                    data = json.loads(json_data.decode("utf-8"))

                    for box in data.get("boxes", []):
                        x1, y1, x2, y2 = box["x1"], box["y1"], box["x2"], box["y2"]
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        label = f"#{box['id']} X:{box['X']*1000:.0f} Y:{box['Y']*1000:.0f} Z:{box['Z']*1000:.0f}mm"
                        cv2.putText(img, label, (x1, y1 - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)

                    cv2.putText(img, f"Targets: {len(data['boxes'])}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    cv2.imshow("Vision Receiver", img)
                    key = cv2.waitKey(1)
                    if key == ord("q") or key == 27:
                        raise KeyboardInterrupt

            except (ConnectionError, ConnectionResetError, BrokenPipeError):
                print("[Vision] Detector disconnected, waiting for next ...")
            finally:
                conn.close()

    except KeyboardInterrupt:
        print("\n[Vision] Shutting down")
    finally:
        server.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
