import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0

Window {
    id: root
    width: 960
    height: 640
    minimumWidth: 800
    minimumHeight: 500
    visible: true
    title: ""
    flags: Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint
    readonly property var theme: FluentTheme {}
    color: theme.bgColor

    Shortcut {
        sequence: "T"
        onActivated: {
            root.theme.darkMode = !root.theme.darkMode
            console.log("darkMode toggled:", root.theme.darkMode)
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        NavigationPanel {
            id: navPanel
            theme: root.theme
            Layout.fillHeight: true

            onItemClicked: function(index) {
                pageStack.currentIndex = index
            }
        }

        StackLayout {
            id: pageStack
            Layout.fillWidth: true
            Layout.fillHeight: true

            ChatPage {
                id: chatPage
                theme: root.theme
                Layout.fillWidth: true
                Layout.fillHeight: true

                onUserMessage: function(text) {
                    chatBridge.sendMessage(text)
                }

                onLoadSession: function(filename) {
                    chatBridge.loadSession(filename)
                }

                onNewSession: function() {
                    chatBridge.newSession()
                    chatPage.chatModel.clear()
                    chatBridge.refreshSessions()
                }

                onDeleteSession: function(filename) {
                    chatBridge.deleteSession(filename)
                }
            }

            VisionPage {
                id: visionPage
                theme: root.theme
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

            ToolsPage {
                id: toolsPage
                theme: root.theme
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

            SettingsPage {
                id: settingsPage
                theme: root.theme
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

            Connections {
                target: chatBridge

                function onMessageReceived(sender, text) {
                    if (sender === "ai" && text.includes("[等待用户输入...]")) {
                        if (chatPage.chatModel.count > 0) {
                            var lastIdx = chatPage.chatModel.count - 1
                            if (chatPage.chatModel.get(lastIdx).sender === "ai") {
                                chatPage.chatModel.setProperty(lastIdx, "needInput", true)
                                return
                            }
                        }
                    }

                    chatPage.chatModel.append({
                        sender: sender,
                        message: text,
                        toolName: "",
                        toolResult: "",
                        needInput: false
                    })
                }

                function onToolCalled(toolName, args, result) {
                    chatPage.chatModel.append({
                        sender: "ai",
                        message: "",
                        toolName: toolName,
                        toolResult: result,
                        needInput: false
                    })
                }

                function onErrorOccurred(message) {
                    chatPage.chatModel.append({ sender: "ai", message: "\u26A0\uFE0F " + message })
                }

                function onThinkingChanged(isThinking) {
                    chatPage.isThinking = isThinking
                }

                function onSessionListUpdated(sessions) {
                    chatPage.sessionList = sessions
                }

                function onSessionLoaded(filename) {
                    chatPage.chatModel.clear()
                }
            }
        }
    }

    Component.onCompleted: chatBridge.refreshSessions()
}
