import QtQuick
import QtQuick.Controls
import MARS 1.0
import "../components"

/**
 * InputBar — Apple Messages 风格输入栏
 * 胶囊形容器、圆形发送按钮、Spring 按压动画
 */
Rectangle {
    id: root

    property var theme: null
    property bool isThinking: false
    signal sendMessage(string text)

    height: theme ? theme.inputBarHeight : 64
    width: parent ? parent.width : 0
    color: "transparent"

    // 输入容器（胶囊形）
    Rectangle {
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

        TextArea {
            id: inputField
            anchors.fill: parent
            anchors.rightMargin: 48
            anchors.margins: 8

            placeholderText: root.isThinking ? "AI 正在思考，请稍等..." : "输入消息，Enter 发送"
            placeholderTextColor: theme ? theme.secondaryText : "#8E8E93"
            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
            color: theme ? theme.textColor : "#1C1C1E"
            font.pixelSize: theme ? theme.fontSizeHeadline : 15
            enabled: !root.isThinking
            wrapMode: Text.Wrap
            background: null
            selectByMouse: true

            Keys.onPressed: function(event) {
                if (event.key === Qt.Key_Return && !(event.modifiers & Qt.ShiftModifier)) {
                    event.accepted = true
                    doSend()
                }
            }
        }

        // 发送按钮（圆形）
        Item {
            id: sendBtn
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 6
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
                    target: parent
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
