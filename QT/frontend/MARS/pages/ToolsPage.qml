import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0
import "../components"

/**
 * ToolsPage — Apple 设置风格工具页面
 * 圆角卡片网格、Apple Toggle 开关
 */
Rectangle {
    id: root

    property var theme: null
    property var tools: []

    color: theme ? theme.bgColor : "#F2F2F7"

    Component.onCompleted: {
        tools = chatBridge.getTools()
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16

        // 头栏
        Rectangle {
            Layout.fillWidth: true
            height: 44
            radius: theme ? theme.cornerRadiusMd : 10
            color: theme ? theme.cardColor : "#FFFFFF"
            border.color: theme ? theme.separatorColor : Qt.rgba(0,0,0,0.06)
            border.width: 1

            Row {
                anchors.left: parent.left
                anchors.leftMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                spacing: 8

                Icon {
                    anchors.verticalCenter: parent.verticalCenter
                    iconName: "tools-outline"
                    iconColor: theme ? theme.accentColor : "#AF52DE"
                    size: 20
                }

                Label {
                    text: "工具"
                    font.pixelSize: theme ? theme.fontSizeHeadline : 15
                    font.weight: theme ? theme.fontWeightSemibold : Font.DemiBold
                    font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                    color: theme ? theme.textColor : "#1C1C1E"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            Row {
                anchors.right: parent.right
                anchors.rightMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                spacing: 4

                Label {
                    text: "共计 " + root.tools.length + " 个"
                    font.pixelSize: theme ? theme.fontSizeCaption : 11
                    font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                    color: theme ? theme.secondaryText : "#8E8E93"
                    anchors.verticalCenter: parent.verticalCenter
                }

                // 全开按钮
                Item {
                    width: 48
                    height: 28
                    anchors.verticalCenter: parent.verticalCenter

                    property bool hovered: false

                    Rectangle {
                        anchors.fill: parent
                        radius: 8
                        color: parent.hovered ? (theme ? theme.hoverColor : Qt.rgba(0,0,0,0.04)) : "transparent"
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }

                    Label {
                        anchors.centerIn: parent
                        text: "全开"
                        font.pixelSize: theme ? theme.fontSizeCaption : 11
                        font.weight: theme ? theme.fontWeightMedium : Font.Medium
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        color: parent.hovered && root.tools.some(function(t) { return !t.enabled })
                               ? (theme ? theme.accentColor : "#AF52DE")
                               : (root.tools.some(function(t) { return !t.enabled })
                                  ? (theme ? theme.secondaryText : "#8E8E93")
                                  : (theme ? theme.tertiaryText : "#C7C7CC"))
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        hoverEnabled: true
                        enabled: root.tools.some(function(t) { return !t.enabled })
                        onEntered: parent.hovered = true
                        onExited: parent.hovered = false
                        onClicked: {
                            for (var i = 0; i < root.tools.length; i++) {
                                chatBridge.setToolEnabled(root.tools[i].name, true)
                            }
                            root.tools = chatBridge.getTools()
                        }
                    }
                }

                // 全关按钮
                Item {
                    width: 48
                    height: 28
                    anchors.verticalCenter: parent.verticalCenter

                    property bool hovered: false

                    Rectangle {
                        anchors.fill: parent
                        radius: 8
                        color: parent.hovered ? (theme ? theme.hoverColor : Qt.rgba(0,0,0,0.04)) : "transparent"
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }

                    Label {
                        anchors.centerIn: parent
                        text: "全关"
                        font.pixelSize: theme ? theme.fontSizeCaption : 11
                        font.weight: theme ? theme.fontWeightMedium : Font.Medium
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        color: parent.hovered && root.tools.some(function(t) { return t.enabled })
                               ? (theme ? theme.accentColor : "#AF52DE")
                               : (root.tools.some(function(t) { return t.enabled })
                                  ? (theme ? theme.secondaryText : "#8E8E93")
                                  : (theme ? theme.tertiaryText : "#C7C7CC"))
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        hoverEnabled: true
                        enabled: root.tools.some(function(t) { return t.enabled })
                        onEntered: parent.hovered = true
                        onExited: parent.hovered = false
                        onClicked: {
                            for (var i = 0; i < root.tools.length; i++) {
                                chatBridge.setToolEnabled(root.tools[i].name, false)
                            }
                            root.tools = chatBridge.getTools()
                        }
                    }
                }
            }
        }

        // 工具卡片网格
        GridView {
            id: grid
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: root.tools

            property int cardWidth: 320
            property int cardHeight: 168
            property int cardGap: 12
            property int colCount: Math.max(1, Math.floor(width / (cardWidth + cardGap)))
            cellWidth: width / colCount
            cellHeight: cardHeight + cardGap

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
                width: 6
                contentItem: Rectangle {
                    radius: 3
                    color: theme ? theme.tertiaryText : "#C7C7CC"
                    opacity: 0.5
                }
            }

            delegate: FluentCard {
                id: toolCard
                width: grid.cellWidth - grid.cardGap
                height: grid.cardHeight
                theme: root.theme
                cardTitle: modelData.name
                cardBorder: theme ? theme.separatorColor : Qt.rgba(0,0,0,0.06)
                opacity: toolSwitch.checked ? 1.0 : 0.6

                // Apple Toggle 开关
                Item {
                    id: toolSwitch
                    z: 1
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.topMargin: 14
                    anchors.rightMargin: 14
                    width: 36
                    height: 22

                    property bool checked: false

                    Component.onCompleted: {
                        checked = modelData.enabled
                    }

                    // 背景轨道
                    Rectangle {
                        anchors.fill: parent
                        radius: 11
                        color: toolSwitch.checked
                               ? (theme ? theme.accentColor : "#34C759")
                               : (theme && theme.darkMode ? "#39393C" : "#E9E9EA")
                        Behavior on color { ColorAnimation { duration: 200 } }
                    }

                    // 滑块（Spring 动画）
                    Rectangle {
                        id: thumb
                        width: 18
                        height: 18
                        radius: 9
                        y: 2
                        x: toolSwitch.checked ? parent.width - width - 2 : 2
                        color: "#FFFFFF"

                        // 阴影
                        Rectangle {
                            anchors.fill: parent
                            anchors.topMargin: 1
                            radius: parent.radius
                            color: Qt.rgba(0, 0, 0, 0.1)
                            z: -1
                        }

                        Behavior on x {
                            SpringAnimation { spring: 5; damping: 0.5; mass: 0.3 }
                        }
                    }

                    TapHandler {
                        onTapped: {
                            toolSwitch.checked = !toolSwitch.checked
                            chatBridge.setToolEnabled(modelData.name, toolSwitch.checked)
                            modelData.enabled = toolSwitch.checked
                        }
                    }
                }

                // 描述内容
                Flickable {
                    anchors.fill: parent
                    anchors.margins: 16
                    anchors.topMargin: 0
                    contentHeight: contentColumn.height
                    clip: true
                    interactive: true

                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                        width: 4
                        contentItem: Rectangle {
                            radius: 2
                            color: theme ? theme.tertiaryText : "#C7C7CC"
                            opacity: 0.5
                        }
                    }

                    Column {
                        id: contentColumn
                        width: parent.width
                        spacing: 8

                        Label {
                            width: parent.width
                            text: modelData.description
                            font.pixelSize: theme ? theme.fontSizeBody : 13
                            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                            color: theme ? theme.secondaryText : "#8E8E93"
                            wrapMode: Text.Wrap
                            lineHeight: 1.45
                            maximumLineCount: 3
                            elide: Text.ElideRight
                            antialiasing: true
                        }

                        Item { height: 4; width: 1 }

                        // 必需参数标签
                        Row {
                            spacing: 6
                            visible: modelData.required_params !== ""

                            Rectangle {
                                height: requiredLabel.implicitHeight + 6
                                width: requiredLabel.implicitWidth + 12
                                radius: 4
                                color: Qt.rgba(1.0, 0.231, 0.188, 0.12)

                                Label {
                                    id: requiredLabel
                                    anchors.centerIn: parent
                                    text: modelData.required_params
                                    font.pixelSize: theme ? theme.fontSizeCaption : 11
                                    font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                    color: "#FF3B30"
                                    antialiasing: true
                                }
                            }
                        }

                        // 可选参数标签
                        Row {
                            spacing: 6
                            visible: modelData.optional_params !== ""

                            Rectangle {
                                height: optionalLabel.implicitHeight + 6
                                width: optionalLabel.implicitWidth + 12
                                radius: 4
                                color: theme ? Qt.rgba(0, 0, 0, 0.04) : Qt.rgba(0,0,0,0.04)

                                Label {
                                    id: optionalLabel
                                    anchors.centerIn: parent
                                    text: modelData.optional_params
                                    font.pixelSize: theme ? theme.fontSizeCaption : 11
                                    font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                    color: theme ? theme.secondaryText : "#8E8E93"
                                    antialiasing: true
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
