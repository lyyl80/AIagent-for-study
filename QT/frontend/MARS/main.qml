import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0

Window {
    id: root
    width:960
    height:640
    minimumWidth:800
    minimumHeight: 500
    visible: true
    title: "MARS AI AGENT"
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
       NavigationPanel{
          id: navPanel
          theme: root.theme
          Layout.fillHeight: true

          onItemClicked:function(index) {
            pageStack.currentIndex = index
            
          }
       }
       
       StackLayout {
            id: pageStack
            Layout.fillWidth: true
            Layout.fillHeight: true

            // 聊天主界面
            ChatPage {
                id: chatPage
                theme: root.theme
                Layout.fillWidth: true
                Layout.fillHeight: true
                onUserMessage: function(text) {
                    chatBridge.sendMessage(text)
                }
            }
           
            
            Rectangle { color: theme.bgColor; Label { anchors.centerIn: parent; text: "会话"; color: theme.textColor } }
            Rectangle { color: theme.bgColor; Label { anchors.centerIn: parent; text: "工具"; color: theme.textColor } }
            Rectangle { color: theme.bgColor; Label { anchors.centerIn: parent; text: "设置"; color: theme.textColor } }
             // 连接桥接信号
           Connections {
                target: chatBridge

                function onMessageReceived(sender, text) {
                    // 检查是否是工具调用后的等待输入提示
                    if (sender === "ai" && text.includes("[等待用户输入...]")) {
                        // 更新最后一条 AI 消息,添加等待输入标记
                        if (chatPage.chatModel.length > 0) {
                            var lastMsg = chatPage.chatModel[chatPage.chatModel.length - 1]
                            if (lastMsg.sender === "ai") {
                                lastMsg.needInput = true
                                chatPage.chatModel = chatPage.chatModel.slice() // 触发更新
                                return
                            }
                        }
                    }
                    
                    // 正常添加消息
                    chatPage.chatModel = chatPage.chatModel.concat([
                        { 
                            sender: sender, 
                            message: text,
                            toolName: "",
                            toolResult: "",
                            needInput: false
                        }
                    ])
                }

                function onToolCalled(toolName, args, result) {
                    // 工具调用信息附加到最后一条 AI 消息上
                    if (chatPage.chatModel.length > 0) {
                        var lastMsg = chatPage.chatModel[chatPage.chatModel.length - 1]
                        if (lastMsg.sender === "ai") {
                            // 更新最后一条消息,添加工具信息
                            lastMsg.toolName = toolName
                            lastMsg.toolResult = result
                            chatPage.chatModel = chatPage.chatModel.slice() // 触发更新
                            return
                        }
                    }
                    
                    // 如果没有 AI 消息,创建新的工具消息
                    chatPage.chatModel = chatPage.chatModel.concat([
                        {
                            sender: "ai",
                            message: "",
                            toolName: toolName,
                            toolResult: result,
                            needInput: false
                        }
                    ])
                }

                function onErrorOccurred(message) {
                    chatPage.chatModel = chatPage.chatModel.concat([
                        { sender: "ai", message: "\u26A0\uFE0F " + message }
                    ])
                }

                function onThinkingChanged(isThinking) {
                    chatPage.isThinking = isThinking
                }
            }
        }
    }

    
    
}