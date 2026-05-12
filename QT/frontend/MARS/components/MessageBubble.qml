import QtQuick
import QtQuick.Controls

Rectangle {
    id: root

    property var theme: null
    property string sender: "user"
    property string message: ""
    property string toolName: ""
    property string toolResult: ""

    width: parent ? parent.width : 0
    implicitHeight: contentColumn.height + 24
    color: "transparent"

    Column {
        id: contentColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 16
        y: 12
        spacing: 4

        Rectangle {
            id: bubble
            anchors.left: sender === "ai" ? parent.left : undefined
            anchors.right: sender === "user" ? parent.right : undefined
            width: Math.min(innerText.implicitWidth + 32, parent.width * 0.75)
            height: innerText.implicitHeight + 32
            radius: 12
            color: sender === "user"
                   ? (theme ? theme.userBubbleBg : "#f18cb9")
                   : (theme ? theme.aiBubbleBg : "#f0f0f0")

            Label {
                id: innerText
                anchors.fill: parent
                anchors.margins: 16
                text: root.message
                color: sender === "user"
                       ? (theme ? theme.userBubbleText : "#fff")
                       : (theme ? theme.aiBubbleText : "#333")
                font.pixelSize: 14
                wrapMode: Text.Wrap
            }
        }

        Rectangle {
            id: toolCard
            anchors.left: parent.left
            anchors.right: parent.right
            visible: root.toolName !== ""
            radius: 8
            color: theme ? theme.toolBubbleBg : "#fafafa"
            border.color: theme ? theme.toolBubbleBorder : "#ddd"
            border.width: 1
            height: visible ? toolInner.height + 20 : 0

            Column {
                id: toolInner
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 10
                spacing: 4

                Label {
                    text: "\u{1F527} " + root.toolName
                    font.pixelSize: 12
                    font.bold: true
                    color: theme ? theme.textColor : "#333"
                }
                Label {
                    text: root.toolResult
                    font.pixelSize: 11
                    color: theme ? theme.secondaryText : "#666"
                    wrapMode: Text.Wrap
                    elide: Text.ElideRight
                    maximumLineCount: 3
                }
            }
        }

        Label {
            anchors.left: sender === "ai" ? bubble.left : undefined
            anchors.right: sender === "user" ? bubble.right : undefined
            text: sender === "user" ? "你" : "MARS"
            font.pixelSize: 11
            color: theme ? theme.secondaryText : "#999"
        }
    }
}
