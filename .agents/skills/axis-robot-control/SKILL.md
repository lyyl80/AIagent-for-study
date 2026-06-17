---
name: axis-robot-control
description: Use when controlling a 4-axis robotic arm via serial port, including grasp, release, and coordinate transform operations
---

# Axis Robot Control

## Overview

4-axis robotic arm controlled via serial text protocol. Vision-guided grasping using Orbbec depth camera + YOLO detection.

## Hardware

| Component | Detail |
|-----------|--------|
| Robot arm | 4-axis, serial control (text protocol) |
| Serial | COM5 @ 115200 baud |
| Camera | Orbbec depth camera |
| Detection | YOLO bottlecap model |

## Serial Protocol

### Command Format

```
Gx y z   → 移动到(x,y,z) + 闭合夹爪（抓取）
Rx y z   → 移动到(x,y,z) + 张开夹爪（释放）
```

- x, y, z: **机械臂基座坐标系**坐标 (mm)
- 坐标范围: workspace_x[-270, 270], workspace_y[160, 330], workspace_z[0, 240]

### Use with AI Agent Tool

Send commands via the `serial_send` tool:

```python
serial_send(data="G50 30 -20", port="COM5")
serial_send(data="R0 0 0",   port="COM5")
```

## Coordinate Systems

### Camera → Robot Transform

```
相机3D坐标(m) → ×1000 → 相机坐标(mm) → camera_to_robot() → 机械臂坐标(mm) → serial_send
```

### Calibration

- Calibration file: `calibration/calibration.npz`
- Contains R (rotation matrix) and T (translation vector)
- Loaded automatically by `Lib.kinematics.load_calibration()`
- Re-calibrate with `APP/calibrate.py` after moving camera

### Key Files

| File | Purpose |
|------|---------|
| `Lib/kinematics.py` | pixel_to_3d(), camera_to_robot(), load_calibration() |
| `Lib/serial_protocol.py` | SerialProtocol class (G/R commands) |
| `Lib/tracker.py` | Target tracking with ID recycling |
| `Lib/detector.py` | YOLO bottlecap detection |
| `Lib/camera.py` | Orbbec camera access |

## Workflows

### 1. Full Grasp Flow

```
detect targets → select one → transform coords → serial_send(grasp) → confirm
```

Steps:
1. `list_alltarget.py` detects bottlecaps and sends frames via TCP
2. AI reviews detected targets from receiver GUI
3. AI calls `serial_send(data="Gx y z", port="COM5")` with robot coordinates
4. Wait for robot to complete
5. `serial_send(data="Rx_drop y_drop z_drop", port="COM5")` to release at drop position

### 2. Coordinate Transform (Manual)

If no calibration loaded, approximate transform:

```python
# Camera coords (mm) → Robot base coords (mm)
# Offset: x+0, y+200, z+150 (typical)
robot_x = cam_x + offset_x
robot_y = cam_z + offset_y
robot_z = -cam_y + offset_z
```

### 3. Workspace Safety Check

Before sending coordinates, verify they are within range:

```python
wx = [-270, 270]   # workspace_x
wy = [160, 330]    # workspace_y
wz = [0, 240]      # workspace_z

if not (wx[0] <= x <= wx[1] and wy[0] <= y <= wy[1] and wz[0] <= z <= wz[1]):
    # Coordinate out of range, do NOT send
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Sending camera coordinates directly to robot | Always run `camera_to_robot()` transform first |
| Forgetting `×1000` (detector returns meters) | Convert m → mm before transform |
| Serial port busy/not found | Check COM port, close other programs (serial assistants, IDE) |
| Sending out-of-workspace coordinates | Run workspace check before `serial_send` |
| Forgetting to wait for robot to finish | Robot needs time to reach position before next command |

## Default Configuration

From `config.yaml`:

```yaml
serial:
  port: COM5
  baudrate: 115200

grasp:
  workspace_x: [-270, 270]
  workspace_y: [160, 330]
  workspace_z: [0, 240]
  drop_pos: [-140, 200, 160]
  home_pos: [0, 208, 170]
```
