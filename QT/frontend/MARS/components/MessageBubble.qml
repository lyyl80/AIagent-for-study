import QtQuick
import QtQuick.Controls

Rectangle {
    id: root

    property var theme: null
    property string sender: "user"
    property string message: ""
    property string toolName: ""
    property string toolResult: ""
    property bool needInput: false

    width: parent ? parent.width : 0
    implicitHeight: contentColumn.height + 8
    color: "transparent"

    // 进入动画
    property real opacityValue: 0
    property real scaleValue: 0.95

    Behavior on opacityValue { NumberAnimation { duration: 200; easing.type: Easing.OutQuad } }
    Behavior on scaleValue { NumberAnimation { duration: 200; easing.type: Easing.OutQuad } }

    Component.onCompleted: {
        opacityValue = 1
        scaleValue = 1
    }

    Column {
        id: contentColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 8
        y: 4
        spacing: 2
        opacity: opacityValue
        scale: scaleValue
        transformOrigin: Item.Center

        Rectangle {
            id: bubble
            visible: root.toolName === "" || root.message !== ""

            anchors.left: sender === "ai" ? parent.left : undefined
            anchors.right: sender === "user" ? parent.right : undefined

            width: Math.min(innerText.implicitWidth + 32, parent.width * 0.75)
            height: innerText.implicitHeight + 32
            radius: 12

            color: sender === "user"
                   ? (theme ? theme.userBubbleBg : "#7c3aed")
                   : (theme ? theme.aiBubbleBg : "#3a3a3a")

            Label {
                id: innerText
                anchors.fill: parent
                anchors.margins: 16

                text: root.message
                color: sender === "user"
                       ? (theme ? theme.userBubbleText : "#fff")
                       : (theme ? theme.aiBubbleText : "#e0e0e0")
                font.pixelSize: 14
                font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                renderType: Text.NativeRendering
                antialiasing: true
                wrapMode: Text.Wrap
                lineHeight: 1.5
            }
        }

        Rectangle {
            id: toolCard
            anchors.left: parent.left
            anchors.right: parent.right
            visible: root.toolName !== ""
            radius: 8
            color: theme ? Qt.rgba(theme.textColor.r, theme.textColor.g, theme.textColor.b, 0.05) : Qt.rgba(0,0,0,0.03)
            border.color: theme ? Qt.rgba(theme.textColor.r, theme.textColor.g, theme.textColor.b, 0.1) : Qt.rgba(0,0,0,0.06)
            border.width: 1
            height: visible ? toolInner.height + 10 : 0

            property bool toolExpanded: false

            Column {
                id: toolInner
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 5
                spacing: 0

                MouseArea {
                    height: 26
                    anchors.left: parent.left
                    anchors.right: parent.right
                    cursorShape: Qt.PointingHandCursor
                    onClicked: toolCard.toolExpanded = !toolCard.toolExpanded

                    Row {
                        anchors.left: parent.left
                        anchors.leftMargin: 4
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 6

                        Label {
                            text: toolCard.toolExpanded ? "\u25BC" : "\u25B6"
                            font.pixelSize: 9
                            color: theme ? theme.secondaryText : "#999"
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Label {
                            text: "\u2699 " + root.toolName
                            font.pixelSize: 12
                            font.bold: false
                            color: theme ? theme.textColor : "#444"
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Label {
                            text: " · " + (root.toolResult || "").replace(/\n/g, ' ').substring(0, 40)
                            font.pixelSize: 11
                            color: theme ? theme.secondaryText : "#999"
                            elide: Text.ElideRight
                            anchors.verticalCenter: parent.verticalCenter
                            visible: !toolCard.toolExpanded
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 1
                    color: theme ? Qt.rgba(theme.textColor.r, theme.textColor.g, theme.textColor.b, 0.06) : Qt.rgba(0,0,0,0.04)
                    visible: toolCard.toolExpanded
                }

                Text {
                    text: root.toolResult
                    font.pixelSize: 12
                    font.family: "Courier New, Consolas, monospace"
                    color: theme ? theme.secondaryText : "#666"
                    wrapMode: Text.Wrap
                    visible: toolCard.toolExpanded
                    leftPadding: 18
                    topPadding: 6
                    bottomPadding: 4
                    rightPadding: 4
                }
            }
        }

        Rectangle {
            id: inputHint
            anchors.left: parent.left
            anchors.right: parent.right
            visible: root.needInput
            radius: 6
            color: theme ? theme.warningBg : "#fff3cd"
            border.color: theme ? theme.dividerColor : "#ffc107"
            border.width: 1
            height: visible ? hintInner.height + 16 : 0

            Row {
                id: hintInner
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 8
                spacing: 6

                Label {
                    text: "\u23F3"
                    font.pixelSize: 14
                    color: theme ? theme.textColor : "#856404"
                }

                Label {
                    text: "等待你的回复..."
                    font.pixelSize: 12
                    font.bold: true
                    color: theme ? theme.textColor : "#856404"
                }
            }
        }

        Label {
            anchors.left: sender === "ai" ? parent.left : undefined
            anchors.right: sender === "user" ? parent.right : undefined

            text: sender === "user" ? "你" : "MARS"
            font.pixelSize: 11
            color: theme ? theme.secondaryText : "#999"
        }
    }
}
