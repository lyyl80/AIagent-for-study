import QtQuick
import QtQuick.Controls
import "."

Rectangle {
    id: root

    property var theme: null
    property bool isThinking: false
    signal sendMessage(string text)

    height: theme ? theme.inputBarHeight : 56
    width: parent ? parent.width : 0
    color: "transparent"

    Rectangle {
        anchors.fill: parent
        anchors.topMargin: 8
        anchors.leftMargin: 8
        anchors.rightMargin: 8
        anchors.bottomMargin: 8
        radius: 10
        color: theme ? theme.cardColor : "#2d2d2d"
        border.color: theme ? theme.dividerColor : "#3d3d3d"
        border.width: 1
        clip: true

        TextArea {
            id: inputField
            anchors.fill: parent
            anchors.rightMargin: 48
            anchors.margins: 8

            placeholderText: root.isThinking ? "AI 正在思考，请稍等..." : "输入消息,Enter to send"
            placeholderTextColor: theme ? theme.secondaryText : "#909090"
            font.family: theme ? theme.defaultFontFamily : "Segoe UI"
            color: theme ? theme.textColor : "#e0e0e0"
            font.pixelSize: 14
            enabled: !root.isThinking
            wrapMode: Text.Wrap
            background: null

            Keys.onPressed: function(event) {
                if (event.key === Qt.Key_Return && !(event.modifiers & Qt.ShiftModifier)) {
                    event.accepted = true
                    doSend()
                }
            }
        }

        Button {
            id: sendBtn
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 4
            width: 36
            height: 36
            enabled: !root.isThinking

            background: Rectangle {
                radius: 8
                color: parent.enabled
                       ? (parent.hovered
                          ? Qt.lighter(theme ? theme.accentColor : "#7c3aed", 1.1)
                          : (theme ? theme.accentColor : "#7c3aed"))
                       : (theme ? theme.dividerColor : "#555555")
                Behavior on color { ColorAnimation { duration: 100 } }
            }

            contentItem: Icon {
                iconName: root.isThinking ? "refresh" : "arrow-right"
                iconColor: "#ffffff"
                size: 16
            }

            onClicked: doSend()
        }
    }

    function doSend() {
        var text = inputField.text.trim()
        if (text === "") return

        sendMessage(text)
        inputField.text = ""
    }
}
