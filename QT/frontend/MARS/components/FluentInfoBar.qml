import QtQuick
import QtQuick.Controls
import MARS 1.0

/**
 * FluentInfoBar — Apple 风格信息提示条
 * 圆角12px、半透明背景、滑入动画
 * 支持 info / success / warning / error 四种类型
 */
Item {
    id: root

    property var theme: null
    property string infoText: ""
    property string infoType: "info"
    property int displayDuration: 3000

    visible: false
    height: visible ? 48 : 0
    clip: true

    signal dismissed()

    // 入场/退场动画
    Behavior on height { NumberAnimation { duration: 300; easing.type: Easing.OutCubic } }
    transform: Translate { id: slideY; y: root.visible ? 0 : -20 }
    Behavior on y {
        id: slideBehavior
        NumberAnimation { duration: 300; easing.type: Easing.OutCubic }
        target: slideY
        property: "y"
    }

    Rectangle {
        anchors.fill: parent
        anchors.margins: 4
        radius: theme ? theme.cornerRadiusLg : 12

        // 半透明背景色
        color: {
            var c = getTypeColor()
            return Qt.rgba(c.r, c.g, c.b, theme && theme.darkMode ? 0.85 : 0.9)
        }

        // 细边框
        border.color: Qt.rgba(1, 1, 1, theme && theme.darkMode ? 0.08 : 0.5)
        border.width: 1

        Row {
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            spacing: 10

            // 图标
            Icon {
                iconName: {
                    switch (infoType) {
                        case "success": return "checkmark"
                        case "warning": return "warning"
                        case "error":   return "xmark"
                        default:        return "info"
                    }
                }
                iconColor: "#FFFFFF"
                size: 18
                anchors.verticalCenter: parent.verticalCenter
            }

            // 文本
            Label {
                text: infoText
                font.pixelSize: theme ? theme.fontSizeBody : 13
                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                font.weight: theme ? theme.fontWeightMedium : Font.Medium
                color: "#FFFFFF"
                anchors.verticalCenter: parent.verticalCenter
                elide: Text.ElideRight
            }
        }

        // 关闭按钮
        Icon {
            anchors.right: parent.right
            anchors.rightMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            iconName: "xmark"
            iconColor: Qt.rgba(1, 1, 1, 0.7)
            size: 14
            visible: displayDuration === 0

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: dismiss()
            }
        }
    }

    function getTypeColor() {
        switch (infoType) {
            case "success": return theme ? theme.successBg : "#34C759"
            case "warning": return theme ? theme.warningBg : "#FF9F0A"
            case "error":   return theme ? theme.errorBg : "#FF3B30"
            default:        return theme ? theme.infoBg : "#007AFF"
        }
    }

    function show(text, type, duration) {
        infoText = text
        infoType = type || "info"
        displayDuration = duration || 3000
        visible = true

        if (displayDuration > 0) {
            hideTimer.interval = displayDuration
            hideTimer.start()
        }
    }

    function dismiss() {
        hideTimer.stop()
        root.visible = false
        dismissed()
    }

    Timer {
        id: hideTimer
        onTriggered: dismiss()
    }
}
