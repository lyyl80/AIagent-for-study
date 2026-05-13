import QtQuick
import QtQuick.Controls

/**
 * FluentButton - Fluent 风格按钮组件
 * 提供主题支持、图标显示和主/次样式切换功能
 */
Button {
    id: root

    // ====== 自定义属性 ======
    property var theme: null              // 主题对象，用于动态配色
    property string iconText: ""          // 图标文本（Emoji 或 Unicode）
    property int iconSize: 16             // 图标字体大小
    property bool primary: true           // 主色填充 / 透明背景模式

    // 默认尺寸设置
    implicitHeight: 36                    // 默认高度 36px
    implicitWidth: iconText !== "" ? 80 : 60  // 有图标时宽度 80px，否则 60px
    padding: 0                            // 无内边距

    // ====== 背景样式 ======
    background: Rectangle {
        radius: 6                         // 圆角半径 6px
        
        // 动态颜色计算：根据状态返回不同颜色
        color: {
            if (!enabled) return theme ? theme.dividerColor : "#ccc"  // 禁用状态
            if (root.down) return Qt.darker(bgColor, 1.15)            // 按下状态（加深 15%）
            if (root.hovered) return Qt.lighter(bgColor, 1.08)        // 悬停状态（提亮 8%）
            return bgColor                                            // 默认状态
        }
        
        // 颜色变化动画效果（100ms）
        Behavior on color { ColorAnimation { duration: 100 } }

        // 基础背景色：主按钮使用主题强调色，次按钮透明
        readonly property color bgColor: primary
            ? (theme ? theme.accentColor : "#f18cb9")
            : "transparent"

        // 边框样式：主按钮无边框，次按钮使用分隔线颜色
        border.color: primary ? "transparent" : (theme ? theme.dividerColor : "#ccc")
        border.width: primary ? 0 : 1
    }

    // ====== 内容区域 ======
    contentItem: Item {
        Row {
            anchors.centerIn: parent      // 居中显示
            spacing: 4                    // 图标与文字间距 4px

            // 图标标签
            Label {
                text: root.iconText
                font.pixelSize: root.iconSize
                visible: root.iconText !== ""  // 仅在有图标文本时显示
                color: primary ? "#ffffff" : (theme ? theme.textColor : "#333")  // 主按钮白色，次按钮跟随主题
            }
            
            // 文字标签
            Label {
                text: root.text
                font.pixelSize: 13
                visible: root.text !== ""   // 仅在有文字时显示
                color: primary ? "#ffffff" : (theme ? theme.textColor : "#333")  // 主按钮白色，次按钮跟随主题
            }
        }
    }

}