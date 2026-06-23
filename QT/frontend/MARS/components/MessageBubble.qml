import QtQuick
import QtQuick.Controls
import MARS 1.0

/**
 * MessageBubble — Apple Messages 风格消息气泡
 * AI 消息支持 Markdown 渲染、hover 复制/重新生成
 */
Rectangle {
    id: root

    property var theme: null
    property string sender: "user"
    property string message: ""
    property string toolName: ""
    property string toolResult: ""
    property bool needInput: false
    property bool isNewMessage: false

    signal copyMessage(string text)
    signal regenerateMessage()

    width: parent ? parent.width : 0
    implicitHeight: contentColumn.height + 8
    color: "transparent"

    // 入场动画
    property real opacityValue: isNewMessage ? 0 : 1
    property real yOffsetValue: isNewMessage ? 12 : 0

    Behavior on opacityValue { enabled: root.isNewMessage; NumberAnimation { duration: 350; easing.type: Easing.OutQuart } }
    Behavior on yOffsetValue { enabled: root.isNewMessage; NumberAnimation { duration: 350; easing.type: Easing.OutQuart } }

    Component.onCompleted: {
        if (isNewMessage) {
            opacityValue = 1
            yOffsetValue = 0
        }
    }

    // hover 检测
    MouseArea {
        id: hoverArea
        anchors.fill: parent
        hoverEnabled: true
        enabled: sender === "ai" && root.message !== ""
        propagateComposedEvents: true
        acceptedButtons: Qt.NoButton  // 不拦截点击
    }

    Column {
        id: contentColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 12
        y: 4
        spacing: 4
        opacity: opacityValue
        transform: Translate { y: yOffsetValue }

        // 消息气泡
        Rectangle {
            id: bubble
            visible: root.toolName === "" || root.message !== ""

            anchors.left: sender === "ai" ? parent.left : undefined
            anchors.right: sender === "user" ? parent.right : undefined

            // AI 消息更宽（为代码块留空间），用户消息自适应
            width: sender === "ai"
                   ? Math.min(parent.width, parent.width * 0.85)
                   : Math.min(innerText.implicitWidth + 32, parent.width * 0.75)
            height: innerText.implicitHeight + 28
            radius: 18

            bottomLeftRadius: sender === "ai" ? 4 : 18
            bottomRightRadius: sender === "user" ? 4 : 18

            color: sender === "user"
                   ? (theme ? theme.userBubbleBg : "#AF52DE")
                   : (theme ? theme.aiBubbleBg : "#FFFFFF")

            border.color: sender === "ai"
                          ? (theme ? theme.aiBubbleBorder : Qt.rgba(0,0,0,0.08))
                          : "transparent"
            border.width: sender === "ai" ? 1 : 0

            // 消息文本 — AI 消息用 MarkdownText，用户消息用纯文本
            Text {
                id: innerText
                anchors.fill: parent
                anchors.margins: 16

                text: root.message
                textFormat: sender === "ai" ? Text.MarkdownText : Text.PlainText
                color: sender === "user"
                       ? (theme ? theme.userBubbleText : "#FFFFFF")
                       : (theme ? theme.aiBubbleText : "#1C1C1E")
                font.pixelSize: theme ? theme.fontSizeBody : 13
                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                antialiasing: true
                wrapMode: Text.Wrap
                lineHeight: 1.45

                onLinkActivated: Qt.openUrlExternally(link)
            }

            // hover 操作栏（仅 AI 消息）
            Row {
                id: hoverActions
                visible: sender === "ai" && root.message !== "" && hoverArea.containsMouse
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.topMargin: -4
                anchors.rightMargin: -4
                spacing: 2

                // 复制按钮
                Rectangle {
                    width: 28; height: 28; radius: 6
                    color: copyMouseArea.containsMouse
                           ? (theme ? theme.hoverColor : Qt.rgba(0,0,0,0.06))
                           : (theme ? theme.cardColor : "#FFFFFF")
                    border.color: theme ? theme.separatorColor : Qt.rgba(0,0,0,0.08)
                    border.width: 1
                    Behavior on color { ColorAnimation { duration: 100 } }

                    Icon {
                        anchors.centerIn: parent
                        iconName: "copy"
                        iconColor: copyMouseArea.containsMouse
                                   ? (theme ? theme.accentColor : "#AF52DE")
                                   : (theme ? theme.secondaryText : "#8E8E93")
                        size: 14
                    }

                    MouseArea {
                        id: copyMouseArea
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        hoverEnabled: true
                        onClicked: {
                            root.copyMessage(root.message)
                        }
                    }
                }

                // 重新生成按钮
                Rectangle {
                    width: 28; height: 28; radius: 6
                    color: regenMouseArea.containsMouse
                           ? (theme ? theme.hoverColor : Qt.rgba(0,0,0,0.06))
                           : (theme ? theme.cardColor : "#FFFFFF")
                    border.color: theme ? theme.separatorColor : Qt.rgba(0,0,0,0.08)
                    border.width: 1
                    Behavior on color { ColorAnimation { duration: 100 } }

                    Icon {
                        anchors.centerIn: parent
                        iconName: "refresh"
                        iconColor: regenMouseArea.containsMouse
                                   ? (theme ? theme.accentColor : "#AF52DE")
                                   : (theme ? theme.secondaryText : "#8E8E93")
                        size: 14
                    }

                    MouseArea {
                        id: regenMouseArea
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        hoverEnabled: true
                        onClicked: root.regenerateMessage()
                    }
                }
            }
        }

        // 工具调用卡片
        Rectangle {
            id: toolCard
            anchors.left: parent.left
            anchors.right: parent.right
            visible: root.toolName !== ""
            radius: 8
            color: theme ? theme.toolBubbleBg : Qt.rgba(0,0,0,0.02)
            border.color: theme ? theme.toolBubbleBorder : Qt.rgba(0,0,0,0.06)
            border.width: 1
            clip: true

            property bool toolExpanded: false

            // 折叠/展开动画
            height: toolExpanded ? toolBody.height + header.height + 10 : header.height
            Behavior on height {
                NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
            }

            Column {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top

                // 标题栏（点击展开/收起）
                Rectangle {
                    id: header
                    width: parent.width
                    height: 34
                    color: "transparent"

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: toolCard.toolExpanded = !toolCard.toolExpanded

                        Row {
                            anchors.left: parent.left
                            anchors.leftMargin: 10
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 6

                            Icon {
                                iconName: "chevron-right"
                                iconColor: theme ? theme.secondaryText : "#8E8E93"
                                size: 12
                                anchors.verticalCenter: parent.verticalCenter
                                rotation: toolCard.toolExpanded ? 90 : 0
                                Behavior on rotation {
                                    NumberAnimation { duration: 180; easing.type: Easing.OutCubic }
                                }
                            }

                            Icon {
                                iconName: "tools"
                                iconColor: theme ? theme.accentColor : "#AF52DE"
                                size: 14
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Label {
                                text: root.toolName
                                font.pixelSize: theme ? theme.fontSizeBody : 13
                                font.weight: theme ? theme.fontWeightMedium : Font.Medium
                                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                color: theme ? theme.textColor : "#1C1C1E"
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Label {
                                text: " · " + (root.toolResult || "").replace(/\n/g, ' ').trim().substring(0, 60)
                                font.pixelSize: theme ? theme.fontSizeCaption : 11
                                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                color: theme ? theme.tertiaryText : "#C7C7CC"
                                elide: Text.ElideRight
                                anchors.verticalCenter: parent.verticalCenter
                                visible: !toolCard.toolExpanded
                                clip: true
                            }
                        }
                    }
                }

                // 分割线
                Rectangle {
                    width: parent.width
                    height: 1
                    color: theme ? theme.separatorColor : Qt.rgba(0,0,0,0.06)
                    visible: toolCard.toolExpanded
                }

                // 结果内容
                Item {
                    id: toolBody
                    width: parent.width
                    visible: toolCard.toolExpanded

                    implicitHeight: resultText.implicitHeight + 16

                    Text {
                        id: resultText
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.leftMargin: 16
                        anchors.rightMargin: 12
                        anchors.topMargin: 8
                        anchors.bottomMargin: 8
                        text: root.toolResult
                        font.pixelSize: theme ? theme.fontSizeCaption : 11
                        font.family: "SF Mono, Courier New, Consolas, monospace"
                        color: theme ? theme.secondaryText : "#8E8E93"
                        wrapMode: Text.Wrap
                        textFormat: Text.PlainText
                    }
                }
            }
        }

        // 等待输入提示
        Rectangle {
            id: inputHint
            anchors.left: parent.left
            anchors.right: parent.right
            visible: root.needInput
            radius: theme ? theme.cornerRadiusSm : 6
            color: Qt.rgba(1, 0.624, 0.039, 0.12)
            border.color: Qt.rgba(1, 0.624, 0.039, 0.3)
            border.width: 1
            height: visible ? hintInner.height + 16 : 0

            Row {
                id: hintInner
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 8
                spacing: 6

                Icon {
                    iconName: "warning"
                    iconColor: theme ? theme.warningBg : "#FF9F0A"
                    size: 16
                    anchors.verticalCenter: parent.verticalCenter
                }

                Label {
                    text: "等待你的回复..."
                    font.pixelSize: theme ? theme.fontSizeBody : 13
                    font.weight: theme ? theme.fontWeightMedium : Font.Medium
                    font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                    color: theme ? theme.textColor : "#1C1C1E"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
        }

        // 发送者标签
        Label {
            anchors.left: sender === "ai" ? parent.left : undefined
            anchors.right: sender === "user" ? parent.right : undefined

            text: sender === "user" ? "你" : "MARS"
            font.pixelSize: theme ? theme.fontSizeCaption : 11
            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
            color: theme ? theme.tertiaryText : "#C7C7CC"
            leftPadding: 4
            rightPadding: 4
        }
    }
}
