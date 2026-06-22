"""
目标坐标导出模块 — AI 友好的坐标读取格式

将 VisionBridge 接收到的视觉检测数据（bounding boxes + 世界坐标）转换为
结构化的、AI 容易解析的坐标文件，供 AI 自主决策夹取目标。

数据流:
    Camera/Depth sensor → Socket → VisionBridge → target_coordinates.py → AI

坐标系说明:
    - 像素坐标系 (pixel): 图像左上角为原点 (0,0)，x向右 y向下
    - 世界坐标系 (world): X/Y/Z 单位毫米 (mm)，由深度相机标定给出
    - 抓取姿态: 默认 Z 轴向下抓取，如需旋转需额外指定

输出格式:
    JSON 和 纯文本两种格式，均包含时间戳、目标数量、每个目标的完整坐标信息。
"""
import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Optional


# =============================================================================
# 数据结构
# =============================================================================

@dataclass
class TargetBox:
    """单个检测目标的数据结构"""
    # —— 基础信息 ——
    target_id: int                     # 目标ID（视觉追踪用）
    label: str = "unknown"            # 标签/类别名称

    # —— 像素坐标（图像中的位置，用于视觉定位） ——
    x1: int = 0                       # bounding box 左上角 x (px)
    y1: int = 0                       # bounding box 左上角 y (px)
    x2: int = 0                       # bounding box 右下角 x (px)
    y2: int = 0                       # bounding box 右下角 y (px)

    # —— 世界坐标（物理空间位置，用于夹取） ——
    X_mm: float = 0.0                 # X 坐标 (mm)
    Y_mm: float = 0.0                 # Y 坐标 (mm)
    Z_mm: float = 0.0                 # Z 坐标 (mm) — 夹取时的深度/高度

    # —— 衍生属性 ——
    @property
    def center_pixel(self) -> tuple:
        """目标中心点像素坐标 (x, y)"""
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    @property
    def center_world(self) -> tuple:
        """目标中心点世界坐标 (X, Y, Z) 单位 mm"""
        return (self.X_mm, self.Y_mm, self.Z_mm)

    @property
    def width_px(self) -> int:
        """目标在图像中的宽度 (px)"""
        return max(0, self.x2 - self.x1)

    @property
    def height_px(self) -> int:
        """目标在图像中的高度 (px)"""
        return max(0, self.y2 - self.y1)

    def to_dict(self) -> dict:
        """转为可序列化字典"""
        return {
            "target_id": self.target_id,
            "label": self.label,
            "pixel": {
                "x1": self.x1, "y1": self.y1,
                "x2": self.x2, "y2": self.y2,
                "center": {"x": self.center_pixel[0], "y": self.center_pixel[1]},
                "width": self.width_px,
                "height": self.height_px,
            },
            "world_mm": {
                "X": round(self.X_mm, 1),
                "Y": round(self.Y_mm, 1),
                "Z": round(self.Z_mm, 1),
                "center": {
                    "X": round(self.center_world[0], 1),
                    "Y": round(self.center_world[1], 1),
                    "Z": round(self.center_world[2], 1),
                }
            }
        }

    def to_ai_text(self, index: int) -> str:
        """生成 AI 友好的单目标文本描述"""
        return (
            f"[目标 #{self.target_id}]  "
            f"像素位置: ({self.x1},{self.y1})-({self.x2},{self.y2})  "
            f"中心: ({self.center_pixel[0]}, {self.center_pixel[1]})  "
            f"=> 抓取坐标: X={self.X_mm:.1f}mm  Y={self.Y_mm:.1f}mm  Z={self.Z_mm:.1f}mm"
        )


# =============================================================================
# 场景快照 — 某时刻所有目标的完整状态
# =============================================================================

@dataclass
class SceneSnapshot:
    """某一时刻的场景快照（包含所有检测到的目标）"""
    timestamp: float = 0.0             # 快照时间戳
    target_count: int = 0              # 目标数量
    targets: list = field(default_factory=list)  # list[TargetBox]
    image_width: int = 0               # 图像宽度 (px)
    image_height: int = 0              # 图像高度 (px)

    @property
    def timestamp_str(self) -> str:
        """可读的时间字符串"""
        return time.strftime("%H:%M:%S", time.localtime(self.timestamp))

    def to_dict(self) -> dict:
        """转为完整的可序列化字典"""
        return {
            "capture_time": self.timestamp_str,
            "timestamp_unix": self.timestamp,
            "image_size": {"width": self.image_width, "height": self.image_height},
            "target_count": self.target_count,
            "targets": [t.to_dict() for t in self.targets],
            "coordinate_system": {
                "pixel": "原点在图像左上角, x向右 y向下",
                "world_mm": "X/Y/Z 单位毫米, 由深度相机标定给出",
                "grab_orientation": "默认 Z 轴向下抓取",
            }
        }

    def to_json(self, indent: int = 2) -> str:
        """导出为格式化的 JSON 字符串（AI 最易解析）"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def to_ai_text(self) -> str:
        """生成 AI 友好的纯文本描述（人类/AI 都易读）"""
        lines = [
            "+" + "=" * 50 + "+",
            "|          目标坐标报告 - AI 抓取决策输入             |",
            "+" + "=" * 50 + "+",
            f"  捕获时间: {self.timestamp_str}",
            f"  图像尺寸: {self.image_width} x {self.image_height} px",
            f"  目标数量: {self.target_count}",
            "",
            "-- 坐标系统 --",
            "  像素坐标 (pixel) : 原点左上角 (0,0), x向右 y向下",
            "  世界坐标 (world)  : X/Y/Z 单位为毫米 (mm)",
            "  抓取朝向          : 默认 Z 轴向下",
            "",
            "-- 检测目标 --",
        ]
        for i, tgt in enumerate(self.targets, 1):
            lines.append(f"  {tgt.to_ai_text(i)}")
        lines.extend([
            "",
            "-- 抓取建议 --",
            "  1. 选择距离当前机械臂末端最近的目标以节省行程",
            "  2. 优先抓取 bounding box 面积最大的目标（更稳定）",
            "  3. 若 Z_mm 值异常（过小或过大），请验证深度数据",
            "  4. 夹取时建议先移动到目标上方 (X, Y)，再沿 Z 轴下降",
            "",
            "-- 原始 JSON --",
            self.to_json(),
        ])
        return "\n".join(lines)

    def save_json(self, filepath: str):
        """保存为 JSON 文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    def save_ai_report(self, filepath: str):
        """保存 AI 友好的完整报告到文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_ai_text())

    def best_target_by_size(self) -> Optional[TargetBox]:
        """按像素面积排序，返回最大的目标（通常最易抓取）"""
        if not self.targets:
            return None
        return max(self.targets, key=lambda t: t.width_px * t.height_px)

    def best_target_by_distance(self, ref_x: float = 0, ref_y: float = 0) -> Optional[TargetBox]:
        """
        按 (X,Y) 距离参考点排序，返回最近的目标

        Args:
            ref_x: 参考点 X 坐标 (mm)，默认为机械臂原点
            ref_y: 参考点 Y 坐标 (mm)

        Returns:
            距离参考点最近的目标，无目标时返回 None
        """
        if not self.targets:
            return None
        return min(self.targets, key=lambda t: (t.X_mm - ref_x)**2 + (t.Y_mm - ref_y)**2)


# =============================================================================
# 坐标管理器 — 绑定到 VisionBridge，持续维护最新坐标快照
# =============================================================================

class CoordinateManager:
    """
    坐标管理器

    与 VisionBridge 配合使用，将原始 socket 数据转换为 AI 友好的坐标文件。
    自动维护最新的场景快照，并支持导出到文件。

    用法:
        manager = CoordinateManager()
        # 在 VisionBridge._receiver_loop 中更新:
        manager.update(boxes_data, image_width, image_height)
        # AI 读取坐标:
        snapshot = manager.latest_snapshot
        ai_input = snapshot.to_ai_text()
        # 或导出文件供 AI 读取:
        manager.export_report("coordinates/latest.txt")
    """

    def __init__(self, export_dir: str = "coordinates"):
        self.latest_snapshot: Optional[SceneSnapshot] = None
        self._export_dir = export_dir
        self._export_path = os.path.join(export_dir, "latest_coordinates.txt")
        self._history: list[SceneSnapshot] = []
        self._max_history = 100
        os.makedirs(self._export_dir, exist_ok=True)

    def update(self, boxes: list[dict], img_width: int = 0, img_height: int = 0):
        """
        从 VisionBridge 的 boxes 数据更新坐标快照

        Args:
            boxes: 检测框列表，每个元素应包含
                   id, x1, y1, x2, y2, X, Y, Z（与 vision_bridge.py 格式一致）
            img_width: 图像宽度 (px)
            img_height: 图像高度 (px)
        """
        targets = []
        for box in boxes:
            target = TargetBox(
                target_id=box.get("id", 0),
                label=box.get("label", f"target_{box.get('id', 0)}"),
                x1=int(box.get("x1", 0)),
                y1=int(box.get("y1", 0)),
                x2=int(box.get("x2", 0)),
                y2=int(box.get("y2", 0)),
                X_mm=float(box.get("X", 0.0)),
                Y_mm=float(box.get("Y", 0.0)),
                Z_mm=float(box.get("Z", 0.0)),
            )
            targets.append(target)

        snapshot = SceneSnapshot(
            timestamp=time.time(),
            target_count=len(targets),
            targets=targets,
            image_width=img_width,
            image_height=img_height,
        )

        self.latest_snapshot = snapshot
        self._history.append(snapshot)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        # 自动写入文件，供 AI 直接读取
        try:
            with open(self._export_path, "w", encoding="utf-8") as f:
                f.write(snapshot.to_ai_text())
        except OSError:
            pass

    def export_report(self, filename: str = "latest_coordinates.txt") -> str:
        """
        导出 AI 友好坐标报告

        Args:
            filename: 导出文件名（相对于 export_dir）

        Returns:
            导出文件的完整路径
        """
        if not self.latest_snapshot:
            return ""
        filepath = os.path.join(self._export_dir, filename)
        self.latest_snapshot.save_ai_report(filepath)
        return os.path.abspath(filepath)

    def export_json(self, filename: str = "latest_coordinates.json") -> str:
        """
        导出 JSON 格式坐标数据

        Args:
            filename: 导出文件名

        Returns:
            导出文件的完整路径
        """
        if not self.latest_snapshot:
            return ""
        filepath = os.path.join(self._export_dir, filename)
        self.latest_snapshot.save_json(filepath)
        return os.path.abspath(filepath)

    def get_ai_input(self) -> str:
        """
        获取当前快照的 AI 输入文本。
        无目标时返回提示信息，避免 AI 得到空数据。
        """
        if not self.latest_snapshot or self.latest_snapshot.target_count == 0:
            return "[坐标报告] 当前视野中未检测到目标，请确认相机是否对准工作区域。"
        return self.latest_snapshot.to_ai_text()

    def get_best_grab_target(self) -> Optional[TargetBox]:
        """
        智能选择最适合夹取的目标

        策略: 取像素面积最大的目标（假设最近/最稳定）
        """
        if not self.latest_snapshot:
            return None
        return self.latest_snapshot.best_target_by_size()


# =============================================================================
# 快捷入口 — 直接调用生成坐标文件
# =============================================================================

def demo_generate_sample():
    """生成示例坐标文件（无相机时测试用）"""
    boxes = [
        {"id": 1, "x1": 120, "y1": 200, "x2": 280, "y2": 350,
         "X": 150.0, "Y": -30.0, "Z": 85.0},
        {"id": 2, "x1": 400, "y1": 150, "x2": 520, "y2": 310,
         "X": -80.0, "Y": 120.0, "Z": 92.0},
        {"id": 3, "x1": 50, "y1": 50, "x2": 180, "y2": 190,
         "X": 200.0, "Y": 200.0, "Z": 45.0},
    ]
    mgr = CoordinateManager()
    mgr.update(boxes, img_width=640, img_height=480)
    report_path = mgr.export_report("demo_coordinates.txt")
    json_path = mgr.export_json("demo_coordinates.json")
    print(f"[坐标报告] 已生成: {report_path}")
    print(f"[JSON数据] 已生成: {json_path}")
    print()
    print(mgr.get_ai_input())
    return mgr


if __name__ == "__main__":
    demo_generate_sample()
