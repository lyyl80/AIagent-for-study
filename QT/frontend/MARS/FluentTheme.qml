import QtQuick

QtObject {
    id: theme

    // 字体设置
    readonly property string defaultFontFamily: "Segoe UI"

    // ====== 亮/暗模式切换开关 ======
    property bool darkMode: true

    // ====== DeepSeek风格配色方案 ======
    
    // 渐变背景色（深色模式）
    readonly property color gradientStart:     "#1a1a2e"
    readonly property color gradientEnd:       "#16213e"
    readonly property color gradientMid:       "#1f1f3a"

    // ====== 页面基础色 ======
    readonly property color bgColor:           darkMode ? "#1a1a2e" : "#f8f8fa"   // 页面主背景色
    readonly property color cardColor:         darkMode ? "rgba(40, 40, 60, 0.95)" : "#ffffff"   // 卡片/容器背景色
    readonly property color textColor:         darkMode ? "#ffffff" : "#1a1a2e"   // 主要文本颜色
    readonly property color secondaryText:     darkMode ? "#a0a0b0" : "#4a4a60"   // 次要文本颜色（大幅加深）
    readonly property color dividerColor:      darkMode ? "rgba(255,255,255,0.15)" : "rgba(0,0,0,0.15)"   // 分割线颜色（加深）
    readonly property color hoverColor:        darkMode ? "rgba(255,255,255,0.1)" : "#e0e0ec"   // 悬停高亮色
    readonly property color inputBg:           darkMode ? "rgba(255,255,255,0.08)" : "#e8e8f2"   // 输入框背景色

    // ====== 主题色（accent）======
    property color accentColor: "#7c3aed"
    property color accentLight: "#a78bfa"
    property color accentDark:  "#5b21b6"

    // ====== 导航栏 ======
    readonly property real navWidth: 72
    readonly property color navBg:            darkMode ? "rgba(30, 30, 50, 0.95)" : "#f0f0f5"   // 亮色模式导航栏背景
    readonly property color navText:          darkMode ? "#8a8a9a" : "#3a3a50"   // 亮色模式图标文字颜色（大幅加深）
    readonly property color navActiveText:    darkMode ? "#ffffff" : "#7c3aed"   // 亮色模式选中时使用主题色
    readonly property color navActiveBg:      darkMode ? "rgba(99, 102, 241, 0.15)" : "rgba(124, 58, 237, 0.15)"   // 亮色模式选中背景
    readonly property color navIndicator:     accentColor
    readonly property color navHoverBg:       darkMode ? "rgba(255,255,255,0.06)" : "#d8d8e6"   // 亮色模式悬停背景

    // ====== 卡片样式 ======
    readonly property real cardRadius: 12
    readonly property real cardElevation: 8

    // ====== 消息气泡 ======
    readonly property color userBubbleBg:     "#7c3aed"
    readonly property color userBubbleText:   "#ffffff"
    readonly property color aiBubbleBg:       darkMode ? "rgba(255, 255, 255, 0.06)" : "#f8f8fa"
    readonly property color aiBubbleText:     darkMode ? "#f0f0f5" : "#1a1135"
    readonly property color toolBubbleBg:     darkMode ? "rgba(255, 255, 255, 0.04)" : "#f0f0f5"
    readonly property color toolBubbleBorder: darkMode ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)"

    // ====== 输入栏 ======
    readonly property real inputBarHeight: 64
    readonly property color inputBorder:      darkMode ? "rgba(255,255,255,0.15)" : "rgba(0,0,0,0.1)"

    // ====== 信息栏 ======
    readonly property color infoBg:           "#3b82f6"
    readonly property color successBg:        "#10b981"
    readonly property color warningBg:        "#f59e0b"
    readonly property color errorBg:          "#ef4444"

}