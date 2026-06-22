import QtQuick

/**
 * Icon — SF Symbols 风格矢量图标系统
 * 使用 Canvas 绘制高质量矢量路径，确保任意尺寸下清晰锐利
 * 统一线条粗细，圆角线帽，Apple 设计语言
 */
Item {
    id: root

    property string iconName: "circle"
    property color iconColor: "#ffffff"
    property real size: 24
    property bool filled: false  // 部分图标支持填充模式

    width: size
    height: size

    Canvas {
        id: canvas
        anchors.fill: parent
        renderStrategy: Canvas.Threaded
        renderTarget: Canvas.FramebufferObject

        onPaint: {
            var ctx = getContext("2d")
            ctx.resetTransform()
            ctx.clearRect(0, 0, width, height)
            ctx.fillStyle = iconColor
            ctx.strokeStyle = iconColor
            ctx.lineCap = "round"
            ctx.lineJoin = "round"

            var s = size
            var lw = Math.max(1.2, s * 0.08)  // 统一线宽，随尺寸缩放

            drawIcon(ctx, s, lw)
        }
    }

    function drawIcon(ctx, s, lw) {
        switch (iconName) {
            // ====== 基础形状 ======
            case "circle":       drawCircle(ctx, s, lw); break
            case "circle-outline": drawCircleOutline(ctx, s, lw); break
            case "square":       drawSquare(ctx, s, lw); break
            case "square-outline": drawSquareOutline(ctx, s, lw); break
            case "line":         drawLine(ctx, s, lw); break

            // ====== 操作符号 ======
            case "plus":         drawPlus(ctx, s, lw); break
            case "minus":        drawMinus(ctx, s, lw); break
            case "cross":        drawCross(ctx, s, lw); break
            case "checkmark":    drawCheckmark(ctx, s, lw); break
            case "xmark":        drawXmark(ctx, s, lw); break
            case "refresh":      drawRefresh(ctx, s, lw); break

            // ====== 箭头 ======
            case "arrow-right":  drawArrowRight(ctx, s, lw); break
            case "arrow-up":     drawArrowUp(ctx, s, lw); break
            case "arrow-left":   drawArrowLeft(ctx, s, lw); break
            case "chevron-right": drawChevronRight(ctx, s, lw); break
            case "chevron-left":  drawChevronLeft(ctx, s, lw); break

            // ====== 导航/菜单 ======
            case "hamburger":    drawHamburger(ctx, s, lw); break
            case "corner-right":  drawCornerRight(ctx, s, lw); break

            // ====== 功能图标 ======
            case "chat":         drawChat(ctx, s, lw); break
            case "tools":        drawTools(ctx, s, lw); break
            case "tools-outline": drawToolsOutline(ctx, s, lw); break
            case "camera":       drawCamera(ctx, s, lw); break
            case "settings":     drawSettings(ctx, s, lw); break

            // ====== 新增图标 ======
            case "send":         drawSend(ctx, s, lw); break
            case "search":       drawSearch(ctx, s, lw); break
            case "trash":        drawTrash(ctx, s, lw); break
            case "sun":          drawSun(ctx, s, lw); break
            case "moon":         drawMoon(ctx, s, lw); break
            case "plus-circle":  drawPlusCircle(ctx, s, lw); break
            case "info":         drawInfo(ctx, s, lw); break
            case "warning":      drawWarning(ctx, s, lw); break
            case "error":        drawError(ctx, s, lw); break
            case "success":      drawSuccess(ctx, s, lw); break
            case "sidebar":      drawSidebar(ctx, s, lw); break

            default:             drawCircle(ctx, s, lw); break
        }
    }

    // ====== 图标绘制函数 ======

    function drawCircle(ctx, s, lw) {
        ctx.beginPath()
        ctx.arc(s/2, s/2, s*0.33, 0, 2*Math.PI)
        ctx.fill()
    }

    function drawCircleOutline(ctx, s, lw) {
        ctx.lineWidth = lw
        ctx.beginPath()
        ctx.arc(s/2, s/2, s*0.33, 0, 2*Math.PI)
        ctx.stroke()
    }

    function drawSquare(ctx, s, lw) {
        ctx.beginPath()
        roundRect(ctx, s*0.17, s*0.17, s*0.66, s*0.66, s*0.06)
        ctx.fill()
    }

    function drawSquareOutline(ctx, s, lw) {
        ctx.lineWidth = lw
        ctx.beginPath()
        roundRect(ctx, s*0.17, s*0.17, s*0.66, s*0.66, s*0.06)
        ctx.stroke()
    }

    function drawLine(ctx, s, lw) {
        ctx.lineWidth = lw
        ctx.beginPath()
        ctx.moveTo(s*0.2, s*0.5)
        ctx.lineTo(s*0.8, s*0.5)
        ctx.stroke()
    }

    function drawPlus(ctx, s, lw) {
        ctx.lineWidth = lw
        ctx.beginPath()
        ctx.moveTo(s*0.5, s*0.22)
        ctx.lineTo(s*0.5, s*0.78)
        ctx.moveTo(s*0.22, s*0.5)
        ctx.lineTo(s*0.78, s*0.5)
        ctx.stroke()
    }

    function drawMinus(ctx, s, lw) {
        ctx.lineWidth = lw
        ctx.beginPath()
        ctx.moveTo(s*0.22, s*0.5)
        ctx.lineTo(s*0.78, s*0.5)
        ctx.stroke()
    }

    function drawCross(ctx, s, lw) {
        ctx.lineWidth = lw
        ctx.beginPath()
        ctx.moveTo(s*0.28, s*0.28)
        ctx.lineTo(s*0.72, s*0.72)
        ctx.moveTo(s*0.72, s*0.28)
        ctx.lineTo(s*0.28, s*0.72)
        ctx.stroke()
    }

    function drawXmark(ctx, s, lw) {
        ctx.lineWidth = lw
        ctx.beginPath()
        ctx.moveTo(s*0.3, s*0.3)
        ctx.lineTo(s*0.7, s*0.7)
        ctx.moveTo(s*0.7, s*0.3)
        ctx.lineTo(s*0.3, s*0.7)
        ctx.stroke()
    }

    function drawCheckmark(ctx, s, lw) {
        ctx.lineWidth = lw * 1.2
        ctx.beginPath()
        ctx.moveTo(s*0.22, s*0.52)
        ctx.lineTo(s*0.42, s*0.72)
        ctx.lineTo(s*0.78, s*0.28)
        ctx.stroke()
    }

    function drawRefresh(ctx, s, lw) {
        ctx.lineWidth = lw
        // 弧形
        ctx.beginPath()
        ctx.arc(s/2, s/2, s*0.3, -Math.PI*0.3, Math.PI*1.2)
        ctx.stroke()
        // 箭头
        ctx.beginPath()
        var ax = s/2 + s*0.3 * Math.cos(-Math.PI*0.3)
        var ay = s/2 + s*0.3 * Math.sin(-Math.PI*0.3)
        ctx.moveTo(ax - s*0.12, ay - s*0.04)
        ctx.lineTo(ax, ay)
        ctx.lineTo(ax + s*0.04, ay - s*0.12)
        ctx.stroke()
    }

    function drawArrowRight(ctx, s, lw) {
        ctx.lineWidth = lw
        ctx.beginPath()
        ctx.moveTo(s*0.25, s*0.5)
        ctx.lineTo(s*0.75, s*0.5)
        ctx.moveTo(s*0.55, s*0.3)
        ctx.lineTo(s*0.75, s*0.5)
        ctx.lineTo(s*0.55, s*0.7)
        ctx.stroke()
    }

    function drawArrowUp(ctx, s, lw) {
        ctx.lineWidth = lw
        ctx.beginPath()
        ctx.moveTo(s*0.5, s*0.25)
        ctx.lineTo(s*0.5, s*0.75)
        ctx.moveTo(s*0.3, s*0.45)
        ctx.lineTo(s*0.5, s*0.25)
        ctx.lineTo(s*0.7, s*0.45)
        ctx.stroke()
    }

    function drawArrowLeft(ctx, s, lw) {
        ctx.lineWidth = lw
        ctx.beginPath()
        ctx.moveTo(s*0.75, s*0.5)
        ctx.lineTo(s*0.25, s*0.5)
        ctx.moveTo(s*0.45, s*0.3)
        ctx.lineTo(s*0.25, s*0.5)
        ctx.lineTo(s*0.45, s*0.7)
        ctx.stroke()
    }

    function drawChevronRight(ctx, s, lw) {
        ctx.lineWidth = lw * 1.3
        ctx.beginPath()
        ctx.moveTo(s*0.42, s*0.25)
        ctx.lineTo(s*0.62, s*0.5)
        ctx.lineTo(s*0.42, s*0.75)
        ctx.stroke()
    }

    function drawChevronLeft(ctx, s, lw) {
        ctx.lineWidth = lw * 1.3
        ctx.beginPath()
        ctx.moveTo(s*0.58, s*0.25)
        ctx.lineTo(s*0.38, s*0.5)
        ctx.lineTo(s*0.58, s*0.75)
        ctx.stroke()
    }

    function drawHamburger(ctx, s, lw) {
        ctx.lineWidth = lw
        ctx.beginPath()
        ctx.moveTo(s*0.22, s*0.35)
        ctx.lineTo(s*0.78, s*0.35)
        ctx.moveTo(s*0.22, s*0.5)
        ctx.lineTo(s*0.78, s*0.5)
        ctx.moveTo(s*0.22, s*0.65)
        ctx.lineTo(s*0.78, s*0.65)
        ctx.stroke()
    }

    function drawCornerRight(ctx, s, lw) {
        ctx.lineWidth = lw
        ctx.beginPath()
        ctx.moveTo(s*0.2, s*0.3)
        ctx.lineTo(s*0.8, s*0.3)
        ctx.moveTo(s*0.2, s*0.5)
        ctx.lineTo(s*0.6, s*0.5)
        ctx.moveTo(s*0.2, s*0.7)
        ctx.lineTo(s*0.4, s*0.7)
        ctx.stroke()
    }

    function drawChat(ctx, s, lw) {
        ctx.lineWidth = lw
        // 气泡轮廓
        ctx.beginPath()
        roundRect(ctx, s*0.18, s*0.2, s*0.64, s*0.48, s*0.1)
        ctx.stroke()
        // 尾巴
        ctx.beginPath()
        ctx.moveTo(s*0.3, s*0.68)
        ctx.lineTo(s*0.24, s*0.8)
        ctx.lineTo(s*0.4, s*0.68)
        ctx.stroke()
    }

    function drawTools(ctx, s, lw) {
        ctx.lineWidth = lw
        var r = s * 0.09
        var gap = s * 0.06
        // 2x2 网格圆角方块
        ctx.beginPath()
        roundRect(ctx, s*0.22 - r, s*0.22 - r, r*2, r*2, r*0.4)
        ctx.fill()
        ctx.beginPath()
        roundRect(ctx, s*0.5 + gap - r, s*0.22 - r, r*2, r*2, r*0.4)
        ctx.fill()
        ctx.beginPath()
        roundRect(ctx, s*0.22 - r, s*0.5 + gap - r, r*2, r*2, r*0.4)
        ctx.fill()
        ctx.beginPath()
        roundRect(ctx, s*0.5 + gap - r, s*0.5 + gap - r, r*2, r*2, r*0.4)
        ctx.fill()
    }

    function drawToolsOutline(ctx, s, lw) {
        ctx.lineWidth = lw
        // 扳手形状 — Apple SF Symbols 风格
        ctx.beginPath()
        // 左侧弯钩
        ctx.moveTo(s*0.2, s*0.3)
        ctx.arc(s*0.3, s*0.3, s*0.1, Math.PI, Math.PI*0.5, false)
        ctx.lineTo(s*0.55, s*0.55)
        // 底部直线
        ctx.lineTo(s*0.8, s*0.8)
        ctx.stroke()
        // 右侧交叉
        ctx.beginPath()
        ctx.moveTo(s*0.8, s*0.2)
        ctx.lineTo(s*0.2, s*0.8)
        ctx.stroke()
    }

    function drawCamera(ctx, s, lw) {
        ctx.lineWidth = lw
        // 机身
        ctx.beginPath()
        roundRect(ctx, s*0.15, s*0.28, s*0.7, s*0.5, s*0.06)
        ctx.stroke()
        // 顶部凸起
        ctx.beginPath()
        roundRect(ctx, s*0.38, s*0.22, s*0.24, s*0.08, s*0.02)
        ctx.stroke()
        // 镜头
        ctx.beginPath()
        ctx.arc(s*0.5, s*0.53, s*0.14, 0, 2*Math.PI)
        ctx.stroke()
        // 闪光灯
        ctx.beginPath()
        ctx.arc(s*0.74, s*0.38, s*0.03, 0, 2*Math.PI)
        ctx.fill()
    }

    function drawSettings(ctx, s, lw) {
        ctx.lineWidth = lw
        var cx = s/2, cy = s/2
        // 齿轮外圈 — 8 个齿
        ctx.beginPath()
        var outerR = s * 0.36
        var innerR = s * 0.26
        var teeth = 8
        for (var i = 0; i < teeth * 2; i++) {
            var angle = (i / (teeth * 2)) * Math.PI * 2
            var r = (i % 2 === 0) ? outerR : innerR
            var x = cx + r * Math.cos(angle)
            var y = cy + r * Math.sin(angle)
            if (i === 0) ctx.moveTo(x, y)
            else ctx.lineTo(x, y)
        }
        ctx.closePath()
        ctx.stroke()
        // 中心圆
        ctx.beginPath()
        ctx.arc(cx, cy, s * 0.09, 0, 2*Math.PI)
        ctx.stroke()
    }

    function drawSend(ctx, s, lw) {
        ctx.lineWidth = lw
        // 纸飞机 — SF Symbols "paperplane.fill" 风格
        ctx.beginPath()
        ctx.moveTo(s*0.15, s*0.5)
        ctx.lineTo(s*0.85, s*0.2)
        ctx.lineTo(s*0.7, s*0.8)
        ctx.lineTo(s*0.5, s*0.55)
        ctx.closePath()
        ctx.fill()
        // 折叠线
        ctx.strokeStyle = iconColor
        ctx.beginPath()
        ctx.moveTo(s*0.85, s*0.2)
        ctx.lineTo(s*0.5, s*0.55)
        ctx.stroke()
    }

    function drawSearch(ctx, s, lw) {
        ctx.lineWidth = lw
        // 圆圈
        ctx.beginPath()
        ctx.arc(s*0.42, s*0.42, s*0.2, 0, 2*Math.PI)
        ctx.stroke()
        // 手柄
        ctx.beginPath()
        ctx.moveTo(s*0.56, s*0.56)
        ctx.lineTo(s*0.78, s*0.78)
        ctx.stroke()
    }

    function drawTrash(ctx, s, lw) {
        ctx.lineWidth = lw
        // 盖子
        ctx.beginPath()
        ctx.moveTo(s*0.25, s*0.3)
        ctx.lineTo(s*0.75, s*0.3)
        ctx.stroke()
        // 把手
        ctx.beginPath()
        ctx.moveTo(s*0.4, s*0.22)
        ctx.lineTo(s*0.6, s*0.22)
        ctx.stroke()
        // 桶身
        ctx.beginPath()
        roundRect(ctx, s*0.3, s*0.3, s*0.4, s*0.5, s*0.03)
        ctx.stroke()
        // 竖线
        ctx.beginPath()
        ctx.moveTo(s*0.42, s*0.38)
        ctx.lineTo(s*0.42, s*0.7)
        ctx.moveTo(s*0.58, s*0.38)
        ctx.lineTo(s*0.58, s*0.7)
        ctx.stroke()
    }

    function drawSun(ctx, s, lw) {
        ctx.lineWidth = lw
        var cx = s/2, cy = s/2
        // 中心圆
        ctx.beginPath()
        ctx.arc(cx, cy, s*0.2, 0, 2*Math.PI)
        ctx.stroke()
        // 8 条射线
        for (var i = 0; i < 8; i++) {
            var angle = (i / 8) * Math.PI * 2
            ctx.beginPath()
            ctx.moveTo(cx + s*0.28 * Math.cos(angle), cy + s*0.28 * Math.sin(angle))
            ctx.lineTo(cx + s*0.38 * Math.cos(angle), cy + s*0.38 * Math.sin(angle))
            ctx.stroke()
        }
    }

    function drawMoon(ctx, s, lw) {
        ctx.lineWidth = lw
        // 月牙
        ctx.beginPath()
        ctx.arc(s*0.5, s*0.5, s*0.3, Math.PI*0.25, Math.PI*1.25, false)
        ctx.arc(s*0.62, s*0.42, s*0.26, Math.PI*1.15, Math.PI*0.35, true)
        ctx.closePath()
        ctx.fill()
    }

    function drawPlusCircle(ctx, s, lw) {
        ctx.lineWidth = lw
        // 圆圈
        ctx.beginPath()
        ctx.arc(s/2, s/2, s*0.34, 0, 2*Math.PI)
        ctx.stroke()
        // 加号
        ctx.beginPath()
        ctx.moveTo(s*0.5, s*0.3)
        ctx.lineTo(s*0.5, s*0.7)
        ctx.moveTo(s*0.3, s*0.5)
        ctx.lineTo(s*0.7, s*0.5)
        ctx.stroke()
    }

    function drawInfo(ctx, s, lw) {
        ctx.lineWidth = lw
        // 圆圈
        ctx.beginPath()
        ctx.arc(s/2, s/2, s*0.34, 0, 2*Math.PI)
        ctx.stroke()
        // i 点
        ctx.beginPath()
        ctx.arc(s/2, s*0.32, s*0.035, 0, 2*Math.PI)
        ctx.fill()
        // i 竖线
        ctx.beginPath()
        ctx.moveTo(s*0.5, s*0.42)
        ctx.lineTo(s*0.5, s*0.68)
        ctx.stroke()
    }

    function drawWarning(ctx, s, lw) {
        ctx.lineWidth = lw
        // 三角形
        ctx.beginPath()
        ctx.moveTo(s*0.5, s*0.18)
        ctx.lineTo(s*0.82, s*0.72)
        ctx.lineTo(s*0.18, s*0.72)
        ctx.closePath()
        ctx.stroke()
        // 感叹号
        ctx.beginPath()
        ctx.moveTo(s*0.5, s*0.38)
        ctx.lineTo(s*0.5, s*0.56)
        ctx.stroke()
        ctx.beginPath()
        ctx.arc(s*0.5, s*0.64, s*0.025, 0, 2*Math.PI)
        ctx.fill()
    }

    function drawError(ctx, s, lw) {
        ctx.lineWidth = lw
        // 圆圈
        ctx.beginPath()
        ctx.arc(s/2, s/2, s*0.34, 0, 2*Math.PI)
        ctx.stroke()
        // X
        ctx.beginPath()
        ctx.moveTo(s*0.38, s*0.38)
        ctx.lineTo(s*0.62, s*0.62)
        ctx.moveTo(s*0.62, s*0.38)
        ctx.lineTo(s*0.38, s*0.62)
        ctx.stroke()
    }

    function drawSuccess(ctx, s, lw) {
        ctx.lineWidth = lw
        // 圆圈
        ctx.beginPath()
        ctx.arc(s/2, s/2, s*0.34, 0, 2*Math.PI)
        ctx.stroke()
        // 对勾
        ctx.beginPath()
        ctx.moveTo(s*0.35, s*0.52)
        ctx.lineTo(s*0.45, s*0.62)
        ctx.lineTo(s*0.65, s*0.38)
        ctx.stroke()
    }

    function drawSidebar(ctx, s, lw) {
        ctx.lineWidth = lw
        // 外框
        ctx.beginPath()
        roundRect(ctx, s*0.15, s*0.2, s*0.7, s*0.6, s*0.06)
        ctx.stroke()
        // 左侧分割线
        ctx.beginPath()
        ctx.moveTo(s*0.4, s*0.2)
        ctx.lineTo(s*0.4, s*0.8)
        ctx.stroke()
    }

    // ====== 工具函数 ======

    function roundRect(ctx, x, y, w, h, r) {
        ctx.moveTo(x + r, y)
        ctx.lineTo(x + w - r, y)
        ctx.quadraticCurveTo(x + w, y, x + w, y + r)
        ctx.lineTo(x + w, y + h - r)
        ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h)
        ctx.lineTo(x + r, y + h)
        ctx.quadraticCurveTo(x, y + h, x, y + h - r)
        ctx.lineTo(x, y + r)
        ctx.quadraticCurveTo(x, y, x + r, y)
    }

    // 当属性变化时重绘
    onIconNameChanged: canvas.requestPaint()
    onIconColorChanged: canvas.requestPaint()
    onSizeChanged: canvas.requestPaint()
}
