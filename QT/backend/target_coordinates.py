"""
目标坐标导出模块

VisionBridge 每帧检测到的目标坐标实时写入 JSON 文件，
AI 直接读 coordinates/latest_coordinates.json 获取目标位置并发指令。
"""
import json
import os
import time


class CoordinateManager:
    """
    坐标管理器

    用法:
        mgr = CoordinateManager()
        mgr.update(boxes, img_width, img_height)  # 自动写 JSON
    """

    def __init__(self, export_dir: str = "coordinates"):
        self._export_path = os.path.join(export_dir, "latest_coordinates.json")
        os.makedirs(export_dir, exist_ok=True)

    def update(self, boxes: list[dict]):
        """
        从视觉检测数据更新坐标文件

        Args:
            boxes: 检测框列表，每项含 id, x1, y1, x2, y2, X, Y, Z
        """
        ts = time.time()
        time_str = time.strftime("%H:%M:%S", time.localtime(ts))

        data = {
            "capture_time": time_str,
            "target_count": len(boxes),
            "targets": [],
        }

        for box in boxes:
            data["targets"].append({
                "target_id": box.get("id", 0),
                "pixel": {
                    "x1": int(box.get("x1", 0)),
                    "y1": int(box.get("y1", 0)),
                    "x2": int(box.get("x2", 0)),
                    "y2": int(box.get("y2", 0)),
                },
                "world_mm": {
                    "X": round(float(box.get("X", 0.0)), 1),
                    "Y": round(float(box.get("Y", 0.0)), 1),
                    "Z": round(float(box.get("Z", 0.0)), 1),
                },
            })

        try:
            with open(self._export_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass
