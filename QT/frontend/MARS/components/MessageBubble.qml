import QtQuick
import QtQuick.Controls
import MARS 1.0

/**
 * MessageBubble — Apple Messages 风格消息气泡
 * 18px 圆角、Apple 色彩、弹性入场动画
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

    width: parent ? parent.width : 0
    implicitHeight: contentColumn.height + 8
    color: "transparent"

    // 入场动画
    property real opacityValue: isNewMessage ? 0 : 1
    property real yOffsetValue: isNewMessage ? 8 : 0

    Behavior on opacityValue { enabled: root.isNewMessage; NumberAnimation { duration: 300; easing.type: Easing.OutQuart } }
    Behavior on yOffsetValue { enabled: root.isNewMessage; NumberAnimation { duration: 300; easing.type: Easing.OutQuart } }

    Component.onCompleted: {
        if (isNewMessage) {
            opacityValue = 1
            yOffsetValue = 0
        }
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

            width: Math.min(innerText.implicitWidth + 32, parent.width * 0.75)
            height: innerText.implicitHeight + 28
            radius: 18

            // Apple Messages 风格：用户气泡尖角右下，AI 气泡尖角左下
            bottomLeftRadius: sender === "ai" ? 4 : 18
            bottomRightRadius: sender === "user" ? 4 : 18

            color: sender === "user"
                   ? (theme ? theme.userBubbleBg : "#AF52DE")
                   : (theme ? theme.aiBubbleBg : "#FFFFFF")

            border.color: sender === "ai"
                          ? (theme ? theme.aiBubbleBorder : Qt.rgba(0,0,0,0.08))
                          : "transparent"
            border.width: sender === "ai" ? 1 : 0

            Label {
                id: innerText
                anchors.fill: parent
                anchors.margins: 16

                text: root.message
                color: sender === "user"
                       ? (theme ? theme.userBubbleText : "#FFFFFF")
                       : (theme ? theme.aiBubbleText : "#1C1C1E")
                font.pixelSize: theme ? theme.fontSizeBody : 13
                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                antialiasing: true
                wrapMode: Text.Wrap
                lineHeight: 1.45
            }
        }

        // 工具调用卡片
        Rectangle {
            id: toolCard
            anchors.left: parent.left
            anchors.right: parent.right
            visible: root.toolName !== ""
            radius: theme ? theme.cornerRadiusMd : 10
            color: theme ? theme.toolBubbleBg : Qt.rgba(0,0,0,0.02)
            border.color: theme ? theme.toolBubbleBorder : Qt.rgba(0,0,0,0.06)
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

                // 头部（可点击展开）
                MouseArea {
                    height: 28
                    anchors.left: parent.left
                    anchors.right: parent.right
                    cursorShape: Qt.PointingHandCursor
                    onClicked: toolCard.toolExpanded = !toolCard.toolExpanded

                    Row {
                        anchors.left: parent.left
                        anchors.leftMargin: 8
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 6

                        // 展开/折叠箭头
                        Icon {
                            iconName: "chevron-right"
                            iconColor: theme ? theme.secondaryText : "#8E8E93"
                            size: 12
                            anchors.verticalCenter: parent.verticalCenter
                            rotation: toolCard.toolExpanded ? 90 : 0
                            Behavior on rotation { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                        }

                        // 工具图标
                        Icon {
                            iconName: "tools"
                            iconColor: theme ? theme.accentColor : "#AF52DE"
                            size: 14
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        // 工具名称
                        Label {
                            text: root.toolName
                            font.pixelSize: theme ? theme.fontSizeBody : 13
                            font.weight: theme ? theme.fontWeightSemibold : Font.DemiBold
                            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                            color: theme ? theme.textColor : "#1C1C1E"
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        // 结果预览
                        Label {
                            text: " · " + (root.toolResult || "").replace(/\n/g, ' ').substring(0, 50)
                            font.pixelSize: theme ? theme.fontSizeCaption : 11
                            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                            color: theme ? theme.secondaryText : "#8E8E93"
                            elide: Text.ElideRight
                            anchors.verticalCenter: parent.verticalCenter
                            visible: !toolCard.toolExpanded
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

                // 展开内容
                Text {
                    text: root.toolResult
                    font.pixelSize: theme ? theme.fontSizeCaption : 11
                    font.family: "SF Mono, Courier New, Consolas, monospace"
                    color: theme ? theme.secondaryText : "#8E8E93"
                    wrapMode: Text.Wrap
                    visible: toolCard.toolExpanded
                    leftPadding: 16
                    topPadding: 6
                    bottomPadding: 6
                    rightPadding: 8
                    width: parent.width
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
            color: Qt.rgba(1, 0.624, 0.039, 0.12)   // Apple Orange 12%
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
