import QtQuick

QtObject {
    id: theme

    // ====== 亮/暗模式切换开关 ======
    property bool darkMode: false

    // ====== 页面基础色 ======
    readonly property color bgColor:           darkMode ? "#1b1b1b" : "#f0f0f0"   // 页面主背景色
    readonly property color cardColor:         darkMode ? "#2d2d2d" : "#ffffff"   // 卡片/容器背景色（对话框、面板等）
    readonly property color textColor:         darkMode ? "#e0e0e0" : "#2d2d2d"   // 主要文本颜色（标题、正文等）
    readonly property color secondaryText:     darkMode ? "#909090" : "#666666"   // 次要文本颜色（副标题、提示文字、时间戳等）
    readonly property color dividerColor:      darkMode ? "#3d3d3d" : "#e0e0e0"   // 分割线颜色（列表分隔线、区域分割线等）
    readonly property color hoverColor:        darkMode ? "#3a3a3a" : "#e8e8e8"   // 悬停高亮色（鼠标悬停时的按钮、菜单项、列表项背景）
    readonly property color inputBg:           darkMode ? "#3a3a3a" : "#ffffff"   // 输入框背景色（文本输入框、搜索框等表单元素）

    // ====== 主题色（accent）======
    property color accentColor: "#f18cb9"

     // ====== 导航栏 ======
    readonly property real navWidth: 68
    readonly property color navBg:            darkMode ? "#252525" : "#fafafa"
    readonly property color navText:          darkMode ? "#aaaaaa" : "#888888"
    readonly property color navActiveText:    darkMode ? "#ffffff" : "#2d2d2d"
    readonly property color navActiveBg:      darkMode ? "#3a3a3a" : "#e8e8e8"
    readonly property color navIndicator:     accentColor
    readonly property color navHoverBg:       darkMode ? "#303030" : "#f0f0f0"

    // ====== 卡片阴影 ======
    readonly property real cardRadius: 8
    readonly property real cardElevation: 4

    // ====== 消息气泡 ======
    readonly property color userBubbleBg:     accentColor
    readonly property color userBubbleText:   "#ffffff"
    readonly property color aiBubbleBg:       darkMode ? "#3a3a3a" : "#ffffff"
    readonly property color aiBubbleText:     darkMode ? "#e0e0e0" : "#2d2d2d"
    readonly property color toolBubbleBg:     darkMode ? "#2d2d2d" : "#fafafa"
    readonly property color toolBubbleBorder: dividerColor

    // ====== 输入栏 ======
    readonly property real inputBarHeight: 56
    readonly property color inputBorder:      darkMode ? "#555555" : "#cccccc"

    // ====== 信息栏 ======
    readonly property color infoBg:           "#2196F3"
    readonly property color successBg:        "#4CAF50"
    readonly property color warningBg:        "#FF9800"
    readonly property color errorBg:          "#F44336"

}