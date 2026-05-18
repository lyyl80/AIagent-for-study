import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0
import "../components"

Rectangle {
    id: root

    property var theme: null
    property bool isThinking: false
    property bool sidebarVisible: false
    property var sessionList: []
    property var chatModel: []

    color: theme ? theme.bgColor : "#1b1b1b"

    signal userMessage(string text)
    signal loadSession(string filename)
    signal refreshSessions()
    signal newSession()
    signal deleteSession(string filename)

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            id: sessionSidebar
            visible: root.sidebarVisible
            color: theme ? theme.cardColor : "#2d2d2d"
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
                        color: theme ? theme.dividerColor : "#3d3d3d"
                    }

                    Row {
                        anchors.left: parent.left
                        anchors.leftMargin: 16
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 6

                        Icon {
                            iconName: "corner-right"
                            iconColor: theme ? theme.textColor : "#e0e0e0"
                            size: 14
                        }

                        Label {
                            text: "会话"
                            font.pixelSize: 14
                            font.bold: true
                            color: theme ? theme.textColor : "#e0e0e0"
                        }
                    }

                    Button {
                        anchors.right: parent.right
                        anchors.rightMargin: 8
                        anchors.verticalCenter: parent.verticalCenter
                        width: 28
                        height: 28
                        flat: true
                        onClicked: chatBridge.refreshSessions()
                        background: Rectangle {
                            radius: 4
                            color: parent.hovered ? (theme ? theme.navHoverBg : "#eee") : "transparent"
                        }
                        contentItem: Icon {
                            iconName: "refresh"
                            iconColor: theme ? theme.textColor : "#333"
                            size: 16
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
                        color: theme ? theme.secondaryText : "#909090"
                        visible: sessionListView.count === 0
                    }

                    delegate: Item {
                        width: sessionListView.width - 16
                        height: 52

                        MouseArea {
                            id: hoverArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.loadSession(modelData.filename)
                        }

                        Rectangle {
                            anchors.fill: parent
                            radius: 6
                            color: hoverArea.containsMouse
                                   ? (theme ? theme.navHoverBg : "#eee")
                                   : "transparent"
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 12
                            anchors.rightMargin: 4
                            spacing: 8

                            Column {
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignVCenter
                                spacing: 2

                                Label {
                                    text: modelData.filename || "(无标题)"
                                    font.pixelSize: 13
                                    color: theme ? theme.textColor : "#333"
                                    elide: Text.ElideRight
                                }

                                Label {
                                    text: (modelData.created_time || "").substring(0, 16)
                                    font.pixelSize: 10
                                    color: theme ? theme.secondaryText : "#909090"
                                }
                            }

                            Button {
                                Layout.alignment: Qt.AlignVCenter
                                width: 28
                                height: 28
                                text: "\u{2716}"
                                flat: true
                                onClicked: root.deleteSession(modelData.filename)
                                background: Rectangle {
                                    radius: 4
                                    color: parent.hovered ? "#ff444422" : "transparent"
                                }
                                contentItem: Label {
                                    anchors.centerIn: parent
                                    text: parent.text
                                    font.pixelSize: 12
                                    color: "#ff4444"
                                }
                            }
                        }
                    }

                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                        width: 4
                        contentItem: Rectangle { radius: 2; color: theme ? theme.dividerColor : "#555" }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 44
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    Layout.bottomMargin: 8
                    radius: 6
                    color: theme ? theme.accentColor : "#7c3aed"

                    Row {
                        anchors.centerIn: parent
                        spacing: 6

                        Icon {
                            iconName: "plus"
                            iconColor: "#ffffff"
                            size: 16
                        }

                        Label {
                            text: "新建会话"
                            color: "#fff"
                            font.pixelSize: 13
                            font.bold: true
                            font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                            antialiasing: true
                        }
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
                color: theme ? theme.cardColor : "#2d2d2d"

                Rectangle {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: 1
                    color: theme ? theme.dividerColor : "#3d3d3d"
                }

                Row {
                    anchors.left: parent.left
                    anchors.leftMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8

                    Button {
                        width: 32
                        height: 32
                        flat: true
                        onClicked: root.sidebarVisible = !root.sidebarVisible

                        background: Rectangle {
                            radius: 4
                            color: parent.hovered ? (theme ? theme.navHoverBg : "#eee") : "transparent"
                        }

                        contentItem: Icon {
                            iconName: "hamburger"
                            iconColor: theme ? theme.textColor : "#333"
                            size: 18
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
                        color: theme ? theme.dividerColor : "#555"
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
