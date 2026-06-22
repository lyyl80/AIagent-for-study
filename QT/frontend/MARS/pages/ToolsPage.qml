import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0
import "../components"

/**
 * ToolsPage — 工具管理页面
 * 圆角卡片网格，支持单个工具开关和批量操作
 */
Rectangle {
    id: root

    property var theme: null

    color: theme ? theme.bgColor : "#F2F2F7"

    ListModel { id: toolModel }

    function checkAllEnabled(val) {
        for (var i = 0; i < toolModel.count; i++)
            if (toolModel.get(i).enabled !== val) return false
        return toolModel.count > 0
    }

    function checkAnyEnabled() {
        for (var i = 0; i < toolModel.count; i++)
            if (toolModel.get(i).enabled) return true
        return false
    }

    function refreshTools() {
        toolModel.clear()
        var arr = chatBridge.getTools()
        for (var i = 0; i < arr.length; i++)
            toolModel.append(arr[i])
    }

    Component.onCompleted: refreshTools()

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
                    text: "共计 " + toolModel.count + " 个"
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
                        color: parent.hovered && !checkAllEnabled(true)
                               ? (theme ? theme.accentColor : "#AF52DE")
                               : (!checkAllEnabled(true)
                                  ? (theme ? theme.secondaryText : "#8E8E93")
                                  : (theme ? theme.tertiaryText : "#C7C7CC"))
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        hoverEnabled: true
                        enabled: !checkAllEnabled(true)
                        onEntered: parent.hovered = true
                        onExited: parent.hovered = false
                        onClicked: {
                            for (var i = 0; i < toolModel.count; i++) {
                                chatBridge.setToolEnabled(toolModel.get(i).name, true)
                            }
                            refreshTools()
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
                        color: parent.hovered && checkAnyEnabled()
                               ? (theme ? theme.accentColor : "#AF52DE")
                               : (checkAnyEnabled()
                                  ? (theme ? theme.secondaryText : "#8E8E93")
                                  : (theme ? theme.tertiaryText : "#C7C7CC"))
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        hoverEnabled: true
                        enabled: checkAnyEnabled()
                        onEntered: parent.hovered = true
                        onExited: parent.hovered = false
                        onClicked: {
                            for (var i = 0; i < toolModel.count; i++) {
                                chatBridge.setToolEnabled(toolModel.get(i).name, false)
                            }
                            refreshTools()
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
            model: toolModel

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
                cardTitle: model.name
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
                        checked = model.enabled
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
                            var newVal = !model.enabled
                            toolModel.setProperty(index, "enabled", newVal)
                            toolSwitch.checked = newVal
                            chatBridge.setToolEnabled(model.name, newVal)
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
                            text: model.description
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
                            visible: model.required_params !== ""

                            Rectangle {
                                height: requiredLabel.implicitHeight + 6
                                width: requiredLabel.implicitWidth + 12
                                radius: 4
                                color: Qt.rgba(1.0, 0.231, 0.188, 0.12)

                                Label {
                                    id: requiredLabel
                                    anchors.centerIn: parent
                                    text: model.required_params
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
                            visible: model.optional_params !== ""

                            Rectangle {
                                height: optionalLabel.implicitHeight + 6
                                width: optionalLabel.implicitWidth + 12
                                radius: 4
                                color: theme ? Qt.rgba(0, 0, 0, 0.04) : Qt.rgba(0,0,0,0.04)

                                Label {
                                    id: optionalLabel
                                    anchors.centerIn: parent
                                    text: model.optional_params
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
