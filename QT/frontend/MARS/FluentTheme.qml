import QtQuick

/**
 * FluentTheme — 紫罗兰原创设计语言主题系统
 * 深色/亮色双模式
 */
QtObject {
    id: theme

    // ====== 字体设置 ======
    readonly property string defaultFontFamily: "SF Pro Display"
    readonly property string textFontFamily: "SF Pro Text"
    // 备用字体链（QML 不支持 fallback list，此处仅记录，实际使用时用 defaultFontFamily）

    // ====== 亮/暗模式切换开关 ======
    property bool darkMode: true

    // ====== Apple 色彩系统 ======

    // --- 主色（Accent — Apple Purple） ---
    property color accentColor: "#AF52DE"
    property color accentLight: "#C77BFF"
    property color accentDark: "#8944AB"
    property color accentHover: Qt.lighter("#AF52DE", 1.12)
    property color accentPressed: Qt.darker("#AF52DE", 1.1)
    property color accentTint: Qt.rgba(0.686, 0.322, 0.870, 0.12)   // 12% 透明度主色

    // --- 页面基础色 ---
    readonly property color bgColor:        darkMode ? "#000000" : "#F2F2F7"       // 系统分组背景
    readonly property color cardColor:      darkMode ? "#1C1C1E" : "#FFFFFF"        // 卡片/容器背景
    readonly property color secondaryBg:    darkMode ? "#2C2C2E" : "#E5E5EA"        // 次级背景
    readonly property color textColor:      darkMode ? "#FFFFFF" : "#1C1C1E"        // 主文本（label）
    readonly property color secondaryText:  darkMode ? "#98989F" : "#8E8E93"        // 次文本（secondaryLabel）
    readonly property color tertiaryText:   darkMode ? "#48484A" : "#C7C7CC"        // 三级文本
    readonly property color dividerColor:   darkMode ? "rgba(84,84,88,0.36)" : "rgba(60,60,67,0.12)"   // 分割线
    readonly property color separatorColor: darkMode ? "rgba(84,84,88,0.36)" : "rgba(60,60,67,0.12)"   // 分割线别名
    readonly property color hoverColor:     darkMode ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.04)"    // 悬停高亮
    readonly property color inputBg:        darkMode ? "#1C1C1E" : "#F2F2F7"        // 输入框背景
    readonly property color inputBorder:    darkMode ? "rgba(84,84,88,0.3)" : "rgba(60,60,67,0.12)"   // 输入框边框

    // --- 导航栏 ---
    readonly property real navWidth: 72
    readonly property color navBg:            darkMode ? "#1C1C1E" : "#E5E5EA"             // 不透明背景（避免 alpha 混合问题）
    readonly property color navText:          darkMode ? "#98989F" : "#8E8E93"
    readonly property color navActiveText:    accentColor
    readonly property color navActiveBg:      darkMode ? Qt.rgba(0.686, 0.322, 0.870, 0.18) : Qt.rgba(0.686, 0.322, 0.870, 0.12)
    readonly property color navIndicator:     accentColor
    readonly property color navHoverBg:       darkMode ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.03)"

    // --- 渐变背景（保留兼容） ---
    readonly property color gradientStart:    darkMode ? "#000000" : "#F2F2F7"
    readonly property color gradientEnd:      darkMode ? "#1C1C1E" : "#FFFFFF"
    readonly property color gradientMid:      darkMode ? "#0A0A0B" : "#F8F8FA"

    // --- 卡片样式 ---
    readonly property real cardRadius: 10
    readonly property real cardElevation: 0   // Apple 风格不用 elevation，用阴影代替

    // 阴影参数
    readonly property color shadowColor:      darkMode ? Qt.rgba(0,0,0,0.3) : Qt.rgba(0,0,0,0.04)
    readonly property real shadowOffset:     darkMode ? 1 : 2
    readonly property real shadowRadius:     darkMode ? 4 : 8

    // --- 消息气泡 ---
    readonly property color userBubbleBg:     accentColor
    readonly property color userBubbleText:   "#FFFFFF"
    readonly property color aiBubbleBg:       darkMode ? "#1C1C1E" : "#FFFFFF"
    readonly property color aiBubbleText:     darkMode ? "#F2F2F7" : "#1C1C1E"
    readonly property color aiBubbleBorder:  darkMode ? "rgba(84,84,88,0.2)" : "rgba(60,60,67,0.08)"
    readonly property color toolBubbleBg:     darkMode ? "rgba(255,255,255,0.04)" : "rgba(0,0,0,0.02)"
    readonly property color toolBubbleBorder: darkMode ? "rgba(84,84,88,0.15)" : "rgba(60,60,67,0.06)"

    // --- 输入栏 ---
    readonly property real inputBarHeight: 64
    readonly property color inputBarBg:    cardColor

    // --- 信息栏（Apple 系统色） ---
    readonly property color infoBg:       "#007AFF"   // Apple Blue
    readonly property color successBg:    "#34C759"   // Apple Green
    readonly property color warningBg:    "#FF9F0A"   // Apple Orange
    readonly property color errorBg:      "#FF3B30"   // Apple Red

    // ====== Apple 设计 Token ======

    // --- 圆角阶梯 ---
    readonly property real cornerRadiusXs: 4
    readonly property real cornerRadiusSm: 6
    readonly property real cornerRadiusMd: 10
    readonly property real cornerRadiusLg: 14
    readonly property real cornerRadiusXl: 18

    // --- 间距阶梯（4pt 网格） ---
    readonly property real spacing1: 4
    readonly property real spacing2: 8
    readonly property real spacing3: 12
    readonly property real spacing4: 16
    readonly property real spacing5: 20
    readonly property real spacing6: 24
    readonly property real spacing7: 32
    readonly property real spacing8: 48

    // --- 字号阶梯 ---
    readonly property real fontSizeCaption: 11
    readonly property real fontSizeBody: 13
    readonly property real fontSizeHeadline: 15
    readonly property real fontSizeTitle: 17
    readonly property real fontSizeTitle2: 20
    readonly property real fontSizeLargeTitle: 28

    // --- 字重 ---
    readonly property int fontWeightRegular: Font.Normal
    readonly property int fontWeightMedium: Font.Medium
    readonly property int fontWeightSemibold: Font.DemiBold
    readonly property int fontWeightBold: Font.Bold

    // --- 动效时长 ---
    readonly property int durationFast: 200
    readonly property int durationNormal: 300
    readonly property int durationSlow: 400

    // --- 按钮高度 ---
    readonly property real buttonHeight: 36
    readonly property real buttonHeightSm: 28
}
