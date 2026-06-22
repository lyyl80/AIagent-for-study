import QtQuick

/**
 * 全局主题配置
 * 定义深色/浅色双主题配色方案与设计变量
 */
QtObject {
    id: theme

    // ====== 字体 ======
    readonly property string defaultFontFamily: "Segoe UI"

    // ====== 深色/浅色切换 ======
    property bool darkMode: true

    // ====== 页面基础色 ======
    readonly property color bgColor:           darkMode ? "#1a1a2e" : "#f8f8fa"
    readonly property color cardColor:         darkMode ? "#2d2d44" : "#ffffff"
    readonly property color textColor:         darkMode ? "#e8e8f0" : "#1a1a2e"
    readonly property color secondaryText:     darkMode ? "#a0a0b8" : "#5a5a7a"
    readonly property color tertiaryText:      darkMode ? "#70708a" : "#9a9ab0"
    readonly property color dividerColor:      darkMode ? "rgba(255,255,255,0.10)" : "rgba(0,0,0,0.10)"
    readonly property color hoverColor:        darkMode ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.05)"
    readonly property color inputBg:           darkMode ? "rgba(255,255,255,0.06)" : "#e8e8f2"

    // ====== 强调色（紫罗兰主题）======
    property color accentColor: "#7c3aed"
    property color accentLight: "#a78bfa"
    property color accentDark:  "#5b21b6"

    // ====== 导航栏 ======
    readonly property real navWidth: 72
    readonly property color navBg:            darkMode ? "rgba(26, 26, 46, 0.95)" : "#f0f0f5"
    readonly property color navText:          darkMode ? "#8a8a9e" : "#5a5a7a"
    readonly property color navActiveText:    darkMode ? "#ffffff" : "#7c3aed"
    readonly property color navActiveBg:      darkMode ? "rgba(124, 58, 237, 0.20)" : "rgba(124, 58, 237, 0.12)"
    readonly property color navIndicator:     accentColor
    readonly property color navHoverBg:       darkMode ? "rgba(255,255,255,0.06)" : "#d8d8e6"

    // ====== 圆角 ======
    readonly property real cardRadius: 12
    readonly property real cardElevation: 8
    readonly property real cornerRadiusSm: 8
    readonly property real cornerRadiusMd: 12
    readonly property real cornerRadiusLg: 16
    readonly property color separatorColor:   dividerColor

    // ====== 字体层级 ======
    readonly property int fontSizeCaption:    11
    readonly property int fontSizeBody:       13
    readonly property int fontSizeHeadline:   15
    readonly property int fontWeightMedium:   500
    readonly property int fontWeightSemibold: 600

    // ====== 消息气泡 ======
    readonly property color userBubbleBg:     accentColor
    readonly property color userBubbleText:   "#ffffff"
    readonly property color aiBubbleBg:       darkMode ? "#2d2d44" : "#f0f0f5"
    readonly property color aiBubbleText:     darkMode ? "#e8e8f0" : "#1a1135"
    readonly property color toolBubbleBg:     darkMode ? "rgba(255,255,255,0.03)" : "rgba(0,0,0,0.03)"
    readonly property color toolBubbleBorder: darkMode ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)"

    // ====== 输入栏 ======
    readonly property real inputBarHeight: 64
    readonly property color inputBorder:      darkMode ? "rgba(255,255,255,0.15)" : "rgba(0,0,0,0.12)"

    // ====== 状态色 ======
    readonly property color infoBg:           "#3b82f6"
    readonly property color successBg:        "#10b981"
    readonly property color warningBg:        "#f59e0b"
    readonly property color errorBg:          "#ef4444"
}
