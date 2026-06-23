---
name: axis-robot-control
description: Use when controlling a 4-axis robotic arm via serial port, including grasp, release, and coordinate transform operations
---

# Axis Robot Control

4-axis robotic arm on COM5 @ 115200. Text protocol: `Gx y z` (grasp), `Rx y z` (release). Coordinates in mm.

## Commands

```bash
serial_send(data="G140 200 60", port="COM5")        # Grasp: move + close gripper
serial_send(data="R0 208 170", port="COM5")          # Release: move + open gripper
serial_send(data="G140 200 60", read_response=True)  # Read robot feedback
```

Workspace: x[-270,270] y[160,330] z[0,240]. Sending out-of-range coords will fail.

## Coordinate Transform

Camera coords (meters) → ×1000 → `camera_to_robot()` → robot coords (mm) → `serial_send`

Calibration file: `calibration/calibration.npz`. If missing, re-run `APP/calibrate.py`.

## Notes

- Robot responds `OK G` / `OK R` after completing movement
- Default home position: `R0 208 170` (release + return home)
- Default drop position: `G-140 200 160` (release at drop bin)

## 坐标获取

视觉检测实时写入 JSON 坐标文件，AI 直接用读文件工具查看：

```
coordinates/latest_coordinates.json
```

每个目标含 `world_mm.X/Y/Z`，已标定，直接填入 `serial_send` 的 `Gx y z` 指令即可。
