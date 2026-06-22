import QtQuick
import QtQuick.Controls
import MARS 1.0
import "../components"

/**
 * InputBar — Apple Messages 风格输入栏
 * 自动增高、字符计数、Escape 清空、附件按钮预留
 */
Rectangle {
    id: root

    property var theme: null
    property bool isThinking: false
    signal sendMessage(string text)

    // 动态高度：跟随内容增长，最小 64，最大 200
    height: Math.min(Math.max(theme ? theme.inputBarHeight : 64, inputField.contentHeight + 24), 200)
    width: parent ? parent.width : 0
    color: "transparent"

    // 输入容器（胶囊形）
    Rectangle {
        id: capsule
        anchors.fill: parent
        anchors.topMargin: 8
        anchors.leftMargin: 12
        anchors.rightMargin: 12
        anchors.bottomMargin: 8
        radius: 16
        color: theme ? theme.cardColor : "#FFFFFF"
        border.color: theme ? theme.dividerColor : Qt.rgba(0,0,0,0.08)
        border.width: 1
        clip: true

        // 附件按钮（UI 预留）
        Item {
            id: attachBtn
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.leftMargin: 6
            anchors.bottomMargin: 6
            width: 36
            height: 36

            property bool hovered: false

            scale: hovered ? 1.05 : 1.0
            Behavior on scale {
                SpringAnimation { spring: 4; damping: 0.4; mass: 0.5 }
            }

            Rectangle {
                anchors.fill: parent
                radius: 18
                color: attachBtn.hovered
                       ? (theme ? theme.hoverColor : Qt.rgba(0,0,0,0.04))
                       : "transparent"
                Behavior on color { ColorAnimation { duration: 150 } }
            }

            Icon {
                anchors.centerIn: parent
                iconName: "plus-circle"
                iconColor: attachBtn.hovered
                           ? (theme ? theme.accentColor : "#AF52DE")
                           : (theme ? theme.secondaryText : "#8E8E93")
                size: 20
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                hoverEnabled: true
                onEntered: attachBtn.hovered = true
                onExited: attachBtn.hovered = false
                onClicked: {
                    // 文件附件功能开发中
                }
            }
        }

        // 文本输入区
        TextArea {
            id: inputField
            anchors.left: attachBtn.right
            anchors.right: sendBtn.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 4
            anchors.rightMargin: 4
            anchors.topMargin: 8
            anchors.bottomMargin: 8

            placeholderText: root.isThinking ? "AI 正在思考，请稍等..." : "输入消息，Enter 发送"
            placeholderTextColor: theme ? theme.secondaryText : "#8E8E93"
            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
            color: theme ? theme.textColor : "#1C1C1E"
            font.pixelSize: theme ? theme.fontSizeHeadline : 15
            enabled: !root.isThinking
            wrapMode: Text.Wrap
            background: null
            selectByMouse: true
            verticalAlignment: Text.AlignVCenter

            Keys.onPressed: function(event) {
                if (event.key === Qt.Key_Return && !(event.modifiers & Qt.ShiftModifier)) {
                    event.accepted = true
                    doSend()
                } else if (event.key === Qt.Key_Escape) {
                    event.accepted = true
                    inputField.text = ""
                }
            }
        }

        // 字符计数标签（浮动在右下角）
        Label {
            id: charCountLabel
            anchors.right: sendBtn.left
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 2
            anchors.rightMargin: 4
            z: 10

            text: inputField.length > 0 ? inputField.length.toString() : ""
            font.pixelSize: theme ? theme.fontSizeCaption : 11
            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
            color: inputField.length > 500
                   ? (theme ? theme.errorBg : "#FF3B30")
                   : (theme ? theme.tertiaryText : "#C7C7CC")
            visible: inputField.length > 0
        }

        // 发送按钮（圆形）
        Item {
            id: sendBtn
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.rightMargin: 6
            anchors.bottomMargin: 6
            width: 36
            height: 36

            property bool hovered: false
            property bool pressed: false

            // Spring 按压
            scale: pressed ? 0.85 : (hovered ? 1.05 : 1.0)
            Behavior on scale {
                SpringAnimation { spring: 4; damping: 0.4; mass: 0.5 }
            }

            Rectangle {
                anchors.fill: parent
                radius: 18
                color: {
                    if (!enabled) return theme ? theme.secondaryBg : "#E5E5EA"
                    if (sendBtn.pressed) return theme ? theme.accentPressed : Qt.darker("#AF52DE", 1.1)
                    if (sendBtn.hovered) return theme ? theme.accentHover : Qt.lighter("#AF52DE", 1.12)
                    return theme ? theme.accentColor : "#AF52DE"
                }
                Behavior on color { ColorAnimation { duration: 150 } }
            }

            // 图标
            Icon {
                anchors.centerIn: parent
                iconName: root.isThinking ? "refresh" : "arrow-up"
                iconColor: "#FFFFFF"
                size: 18

                // 思考时旋转
                RotationAnimator on rotation {
                    running: root.isThinking
                    from: 0
                    to: 360
                    duration: 800
                    loops: Animation.Infinite
                }
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                hoverEnabled: true
                enabled: !root.isThinking

                onEntered: sendBtn.hovered = true
                onExited: sendBtn.hovered = false
                onPressed: sendBtn.pressed = true
                onReleased: sendBtn.pressed = false
                onClicked: doSend()
            }
        }
    }

    function doSend() {
        var text = inputField.text.trim()
        if (text === "") return

        sendMessage(text)
        inputField.text = ""
    }
}
