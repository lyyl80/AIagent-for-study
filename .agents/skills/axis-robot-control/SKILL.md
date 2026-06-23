---
name: axis-robot-control
description: Use when controlling a 4-axis robotic arm via serial port, including grasp, release, and coordinate transform operations
---

# Axis Robot Control

4-axis robotic arm on COM5 @ 115200. Text protocol: `G x y z` (grasp), `R x y z` (release). Coords in mm.

## 实操要点

1. **坐标取整** — 视觉输出带小数，协议不认，`G 117 251 4` 往小取整
3. **释放用 R** — `R -140 200 160` 放料仓，不是 G
4. **每次抓前重读坐标** — `coordinates/latest_coordinates.json`

## 标准流程

```
读取最新坐标 → 取整(S) → G x y z 抓取 → R x y z 释放
```

## 命令

```bash
serial_send(data="G 117 251 10", port="COM5")       # 抓取
serial_send(data="R 0 208 170", port="COM5")         # 回原点释放
serial_send(data="R -140 200 160", port="COM5")      # 放料仓
```

## 默认位置

| 位置 | 指令 |
|------|------|
| Home | `R 0 208 170` |
| Drop | `R -140 200 160` |

## 工作空间

X[-270,270] Y[160,330] Z[0,240]

## 故障排查

- **无响应** → 检查电源/USB
- **ERR** → 命令格式错误（G后面要加空格）/ 坐标超范围 / 带小数 / Z太低
- **掉线** → 硬件复位重试
