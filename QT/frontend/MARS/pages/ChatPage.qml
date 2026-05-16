import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0

/**
 * ChatPage - 聊天页面组件
 * 
 * 功能说明：
 * - 显示聊天消息列表，支持用户和AI的消息展示
 * - 提供会话侧边栏管理（新建、加载、删除会话）
 * - 集成输入框组件，支持消息发送
 * - 支持主题切换和响应式布局
 * 
 * 架构设计：
 * - 采用信号驱动模式与父组件通信
 * - 通过属性绑定实现主题适配
 * - 使用 ListView + delegate 渲染消息气泡
 */
Rectangle {
    id: root

    // ==================== 属性定义 ====================
    
    /** 主题对象，用于获取颜色配置 */
    property var theme: null
    
    /** AI思考状态标志，控制输入框的禁用状态 */
    property bool isThinking: false
    
    /** 会话侧边栏可见性开关 */
    property bool sidebarVisible: false
    
    /** 会话列表数据，包含文件名和创建时间 */
    property var sessionList: []
    
    /** 聊天消息模型，存储所有对话记录 */
    property var chatModel: []

    // 背景颜色：根据主题动态设置，默认浅灰色
    color: theme ? theme.bgColor : "#f0f0f0"

    // ==================== 信号定义 ====================
    
    /** 用户发送消息信号，传递消息文本 */
    signal userMessage(string text)
    
    /** 加载指定会话信号，传递会话文件名 */
    signal loadSession(string filename)
    
    /** 刷新会话列表信号 */
    signal refreshSessions()
    
    /** 新建会话信号 */
    signal newSession()
    
    /** 删除指定会话信号，传递会话文件名 */
    signal deleteSession(string filename)

    // ==================== 主布局 ====================
    
    RowLayout {
        anchors.fill: parent
        spacing: 0

        // ==================== 会话侧边栏 ====================
        
        Rectangle {
            id: sessionSidebar
            visible: root.sidebarVisible  // 根据开关控制显示/隐藏
            color: theme ? theme.cardColor : "#fff"
            Layout.preferredWidth: 220
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                // --- 侧边栏标题栏 ---
                
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 48
                    color: "transparent"

                    // 底部分隔线
                    Rectangle {
                        anchors.bottom: parent.bottom
                        anchors.left: parent.left
                        anchors.right: parent.right
                        height: 1
                        color: theme ? theme.dividerColor : "#ddd"
                    }

                    // 标题文字："📂 会话"
                    Label {
                        anchors.left: parent.left
                        anchors.leftMargin: 16
                        anchors.verticalCenter: parent.verticalCenter
                        text: "\u{1F4C2} 会话"
                        font.pixelSize: 14
                        font.bold: true
                        color: theme ? theme.textColor : "#333"
                    }

                    // 刷新按钮
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

                // --- 会话列表 ---
                
                ListView {
                    id: sessionListView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    Layout.topMargin: 8
                    model: root.sessionList  // 绑定会话列表数据
                    spacing: 4  // 列表项间距
                    clip: true  // 裁剪超出边界的内容

                    // 空状态提示：当没有会话时显示
                    Label {
                        anchors.centerIn: parent
                        text: "暂无会话"
                        font.pixelSize: 13
                        color: theme ? theme.secondaryText : "#999"
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
                                    color: theme ? theme.secondaryText : "#999"
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

                    // 垂直滚动条
                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded  // 需要时自动显示
                        width: 4
                        contentItem: Rectangle { radius: 2; color: theme ? theme.dividerColor : "#ccc" }
                    }
                }

                // --- 新建会话按钮 ---
                
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 44
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    Layout.bottomMargin: 8
                    radius: 6
                    color: theme ? theme.accentColor : "#f18cb9"  // 使用强调色

                    // 按钮文字："➕ 新建会话"
                    Label {
                        anchors.centerIn: parent
                        text: "\u{2795} 新建会话"
                        color: "#fff"
                        font.pixelSize: 13
                        font.bold: true
                    }

                    // 鼠标区域：点击触发新建会话
                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.newSession()
                    }
                }
            }
        }

        // ==================== 主聊天区域 ====================
        
        Column {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // --- 顶部标题栏 ---
            
            Rectangle {
                width: parent.width
                height: 48
                color: theme ? theme.cardColor : "#ffffff"

                // 底部分隔线
                Rectangle {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: 1
                    color: theme ? theme.dividerColor : "#ddd"
                }

                // 左侧：菜单按钮 + 标题
                Row {
                    anchors.left: parent.left
                    anchors.leftMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8

                    // 侧边栏切换按钮
                    Button {
                        text: "\u{2630}"  // ☰ 汉堡菜单图标
                        flat: true
                        onClicked: root.sidebarVisible = !root.sidebarVisible  // 切换侧边栏显示状态
                        
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

                    // 应用标题
                    Label {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "MARS AI 助手"
                        font.pixelSize: 16
                        font.bold: true
                        color: theme ? theme.textColor : "#333"
                    }
                }
                
            }

            // --- 消息列表 ---
            
            ListView {
                id: messageList
                width: parent.width
                // 动态计算高度：总高度 - 标题栏 - 输入框
                height: parent.height - 48 - (theme ? theme.inputBarHeight : 56)
                model: chatModel  // 绑定聊天消息数据
                clip: true
                spacing: 4  // 消息间距
                cacheBuffer: 200  // 缓存缓冲区大小，提升滚动性能

                // 消息数量变化时自动滚动到底部
                onCountChanged: positionViewAtEnd()

                // 消息项委托：使用 MessageBubble 组件渲染
                delegate: MessageBubble {
                    width: messageList.width
                    theme: root.theme
                    sender: modelData.sender || "user"      // 发送者：user 或 ai
                    message: modelData.message || ""         // 消息文本
                    toolName: modelData.toolName || ""       // 工具名称（如果有）
                    toolResult: modelData.toolResult || ""   // 工具结果（如果有）
                }

                // 垂直滚动条
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                    width: 8
                    background: Rectangle { color: "transparent" }  // 透明背景
                    contentItem: Rectangle {
                        radius: 4
                        color: theme ? theme.dividerColor : "#ccc"
                    }
                }
            }

            // --- 底部输入框 ---
            
            InputBar {
                theme: root.theme
                isThinking: root.isThinking  // 传递AI思考状态，控制输入框禁用
                
                // 发送消息信号处理器
                onSendMessage: function(text) {
                    root.userMessage(text)  // 向父组件发射用户消息信号
                }
            }
        }
    }
}
