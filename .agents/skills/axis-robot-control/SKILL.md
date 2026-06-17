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
