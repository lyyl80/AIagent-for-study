import QtQuick
import QtQuick.Controls
import MARS 1.0

Rectangle {
    id: root
    
    property var theme: null
    property bool isThinking: false

    //消息模型(由python桥接填充)
    property var chatModel: []

    color : theme ? theme.bgColor : "#f0f0f0"

    //信号
    signal userMessage(string text)

    Column{
        anchors.fill : parent
        spacing : 0

        //顶部标题栏
        Rectangle {
            width: parent.width
            height: 48
            color : theme ? theme.cardColor : "#ffffff"
            //分割线
            Rectangle{

                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: 1
                color: theme ? theme.dividerColor : "#ddd"

            }

            Label {
                anchors.centerIn: parent
                text: "MARS AI 助手"
                font.pixelSize: 16
                font.bold: true
                color: theme ? theme.dividerColor : "#333"
            }

             Label {
                anchors.right: parent.right
                anchors.rightMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                text: "\u{1F5D1}"  // 🗑
                font.pixelSize: 16
                visible: chatModel.length > 0

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: chatModel = []
                }
            }
        }

        ListView {
            id: messageList
            width: parent.width
            height:parent.height - 48 - (theme ? theme.inputBarHeight : 56)
            model: chatModel
            clip: true
            spacing: 4
            cacheBuffer: 200

            //自动滚动到底部
            onCountChanged: {
                positionViewAtEnd()
            }

            delegate: MessageBubble {
                width: messageList.width
                theme: root.theme
                sender: modelData.sender || "user"
                message: modelData.message || ""
                toolName: modelData.toolName || ""
                toolResult: modelData.toolResult || ""
            }

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
                width: 8
                background: Rectangle{color: "transparent"}
                contentItem: Rectangle{
                    radius: 4
                    color: theme ? theme.dividerColor : "#ccc"
                }

            }

        }

        InputBar {
            theme : root.theme
            isThinking: root.isThinking
            onSendMessage: function (text) {
                root.userMessage(text)
            }
        }
    }
}