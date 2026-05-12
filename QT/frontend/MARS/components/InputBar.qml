import QtQuick
import QtQuick.Controls

Rectangle {
    id: root

    property var theme: null
    property bool isthinking: false
    signal sendMessage(string text)

    height: theme ? theme.inputBarHeight : 56
    color: theme ? theme.cardColor : "#ffffff"

    // 上分割线
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        color: theme ? theme.dividerColor : "#ddd"
    }

    TextArea {
        id: inputField
        anchors.fill: parent
        anchors.margins: 8
        placeholderText: root.isthinking ? "AI 正在思考，请稍等..." : "输入消息,Enter to send"
        placeholderTextColor: theme ? theme.secondaryText: "#999"
        color: theme ? theme.textColor : "#333"
        font.pixelSize: 14
        enabled: !root.isthinking
        wrapMode: Text.Wrap

        //Enter 发送,Shift+Enter 换行
        Keys.onPressed: function(event) {
            if (event.key === Qt.Key_Return && !(event.modifiers & Qt.ShiftModifier)) {
                 event.accepted = true
                    doSend()
                }
            }
   }

    // 发送按钮
        Button {
            id: sendBtn
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 8
            width: 40
            height: 40
            enabled: !root.isthinking

            background: Rectangle {
                radius: 8
                color: parent.enabled
                       ? (parent.hovered
                          ? Qt.lighter(theme ? theme.accentColor : "#f18cb9", 1.1)
                          : (theme ? theme.accentColor : "#f18cb9"))
                       : (theme ? theme.dividerColor : "#ccc")
                Behavior on color { ColorAnimation { duration: 100 } }
            }

            contentItem: Label {
                anchors.centerIn: parent
                text: root.isthinking ? "\u23F3" : "\u25B6"  // ⏳ / ▶
                color: "#ffffff"
                font.pixelSize: 18
            }

            onClicked: doSend()
        }

        function doSend() {
            var text = inputField.text.trim()
            if(text === "")return
            sendMessage(text)
            inputField.text = ""
        }
    
}