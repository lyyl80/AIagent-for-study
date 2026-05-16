import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0

Rectangle {
    id: root

    property var theme: null
    property bool isThinking: false
    property bool sidebarVisible: false
    property var sessionList: []
    property var chatModel: []

    color: theme ? theme.bgColor : "#f0f0f0"

    signal userMessage(string text)
    signal loadSession(string filename)
    signal newSession()

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            id: sessionSidebar
            visible: root.sidebarVisible
            color: theme ? theme.cardColor : "#fff"
            Layout.preferredWidth: 220
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 48
                    color: "transparent"

                    Rectangle {
                        anchors.bottom: parent.bottom
                        anchors.left: parent.left
                        anchors.right: parent.right
                        height: 1
                        color: theme ? theme.dividerColor : "#ddd"
                    }

                    Label {
                        anchors.left: parent.left
                        anchors.leftMargin: 16
                        anchors.verticalCenter: parent.verticalCenter
                        text: "\u{1F4C2} 会话"
                        font.pixelSize: 14
                        font.bold: true
                        color: theme ? theme.textColor : "#333"
                    }

                    Button {
                        anchors.right: parent.right
                        anchors.rightMargin: 8
                        anchors.verticalCenter: parent.verticalCenter
                        text: "\u{27F2}"
                        flat: true
                        onClicked: chatBridge.refreshSessions()
                        background: Rectangle {
                            radius: 4
                            color: parent.hovered ? (theme ? theme.navHoverBg : "#eee") : "transparent"
                        }
                        contentItem: Label {
                            anchors.centerIn: parent
                            text: parent.text
                            font.pixelSize: 14
                            color: theme ? theme.textColor : "#333"
                        }
                    }
                }

                ListView {
                    id: sessionListView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    Layout.topMargin: 8
                    model: root.sessionList
                    spacing: 4
                    clip: true

                    Label {
                        anchors.centerIn: parent
                        text: "暂无会话"
                        font.pixelSize: 13
                        color: theme ? theme.secondaryText : "#999"
                        visible: sessionListView.count === 0
                    }

                    delegate: Rectangle {
                        width: sessionListView.width - 16
                        height: 56
                        radius: 6
                        color: mouseArea.containsMouse
                               ? (theme ? theme.navHoverBg : "#eee")
                               : Qt.rgba(0, 0, 0, 0.03)

                        Column {
                            anchors.left: parent.left
                            anchors.leftMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 2

                            Label {
                                text: modelData.filename || "(无标题)"
                                font.pixelSize: 13
                                color: theme ? theme.textColor : "#333"
                                elide: Text.ElideRight
                                width: parent.parent.width - 60
                            }
                            Label {
                                text: (modelData.created_time || "").substring(0, 16)
                                font.pixelSize: 10
                                color: theme ? theme.secondaryText : "#999"
                            }
                        }

                        Button {
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.rightMargin: 4
                            text: "\u{2716}"
                            flat: true
                            visible: mouseArea.containsMouse
                            onClicked: chatBridge.deleteSession(modelData.filename)
                            background: Rectangle {
                                radius: 4
                                color: parent.hovered ? "#ff444422" : "transparent"
                            }
                            contentItem: Label {
                                anchors.centerIn: parent
                                text: parent.text
                                font.pixelSize: 10
                                color: "#ff4444"
                            }
                        }

                        MouseArea {
                            id: mouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.loadSession(modelData.filename)
                        }
                    }

                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                        width: 4
                        contentItem: Rectangle { radius: 2; color: theme ? theme.dividerColor : "#ccc" }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 44
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    Layout.bottomMargin: 8
                    radius: 6
                    color: theme ? theme.accentColor : "#f18cb9"

                    Label {
                        anchors.centerIn: parent
                        text: "\u{2795} 新建会话"
                        color: "#fff"
                        font.pixelSize: 13
                        font.bold: true
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.newSession()
                    }
                }
            }
        }

        Column {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            Rectangle {
                width: parent.width
                height: 48
                color: theme ? theme.cardColor : "#ffffff"

                Rectangle {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: 1
                    color: theme ? theme.dividerColor : "#ddd"
                }

                Row {
                    anchors.left: parent.left
                    anchors.leftMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8

                    Button {
                        text: "\u{2630}"
                        flat: true
                        onClicked: root.sidebarVisible = !root.sidebarVisible
                        background: Rectangle {
                            radius: 4
                            color: parent.hovered ? (theme ? theme.navHoverBg : "#eee") : "transparent"
                        }
                        contentItem: Label {
                            anchors.centerIn: parent
                            text: parent.text
                            font.pixelSize: 16
                            color: theme ? theme.textColor : "#333"
                        }
                    }

                    Label {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "MARS AI 助手"
                        font.pixelSize: 16
                        font.bold: true
                        color: theme ? theme.textColor : "#333"
                    }
                }

                Label {
                    anchors.right: parent.right
                    anchors.rightMargin: 16
                    anchors.verticalCenter: parent.verticalCenter
                    text: "\u{1F5D1}"
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
                height: parent.height - 48 - (theme ? theme.inputBarHeight : 56)
                model: chatModel
                clip: true
                spacing: 4
                cacheBuffer: 200

                onCountChanged: positionViewAtEnd()

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
                    background: Rectangle { color: "transparent" }
                    contentItem: Rectangle {
                        radius: 4
                        color: theme ? theme.dividerColor : "#ccc"
                    }
                }
            }

            InputBar {
                theme: root.theme
                isThinking: root.isThinking
                onSendMessage: function(text) {
                    root.userMessage(text)
                }
            }
        }
    }
}
