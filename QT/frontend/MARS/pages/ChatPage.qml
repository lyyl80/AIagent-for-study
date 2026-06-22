import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0
import "../components"

/**
 * ChatPage — Apple Messages 风格聊天页面
 * 常驻会话侧边栏（日期分组）、空状态欢迎页、细腻滚动条
 */
Rectangle {
    id: root

    property var theme: null
    property bool isThinking: false
    property bool sidebarVisible: true
    property var sessionList: []
    property var chatModel: ListModel {}
    property string currentSessionFilename: ""
    property string currentSessionName: ""

    color: theme ? theme.bgColor : "#F2F2F7"

    signal userMessage(string text)
    signal loadSession(string filename)
    signal refreshSessions()
    signal newSession()
    signal deleteSession(string filename)

    // ====== 日期格式化辅助 ======

    function formatDateStr(d) {
        var year = d.getFullYear()
        var month = ("0" + (d.getMonth() + 1)).slice(-2)
        var day = ("0" + d.getDate()).slice(-2)
        return year + "-" + month + "-" + day
    }

    function getDateGroup(createdTime) {
        if (!createdTime || createdTime === "未知") return "更早"

        var dateStr = createdTime.substring(0, 10)
        var now = new Date()
        var today = formatDateStr(now)
        var yesterday = formatDateStr(new Date(now.getTime() - 86400000))
        var weekAgo = formatDateStr(new Date(now.getTime() - 7 * 86400000))

        if (dateStr === today) return "今天"
        if (dateStr === yesterday) return "昨天"
        if (dateStr >= weekAgo) return "7天内"
        return "更早"
    }

    function getDisplayName(filename) {
        // 尝试提取时间戳后缀的摘要部分
        var match = filename.match(/^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_(.+)$/)
        if (match) return match[1]

        // 纯时间戳，格式化为友好显示
        var tsMatch = filename.match(/^(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})/)
        if (tsMatch) {
            return parseInt(tsMatch[2]) + "月" + parseInt(tsMatch[3]) + "日 " + tsMatch[4] + ":" + tsMatch[5]
        }
        return filename
    }

    function getDisplayTime(createdTime) {
        if (!createdTime || createdTime === "未知") return ""

        var timeMatch = createdTime.match(/T(\d{2}):(\d{2})/)
        var dateStr = createdTime.substring(0, 10)
        var now = new Date()
        var today = formatDateStr(now)
        var yesterday = formatDateStr(new Date(now.getTime() - 86400000))

        if (dateStr === today && timeMatch) return timeMatch[1] + ":" + timeMatch[2]
        if (dateStr === yesterday) return "昨天"
        return dateStr.substring(5).replace("-", "/")
    }

    // ====== 会话列表 Model（含日期分组字段）======

    ListModel { id: sessionListModel }

    onSessionListChanged: {
        sessionListModel.clear()
        for (var i = 0; i < sessionList.length; i++) {
            var s = sessionList[i]
            var fn = s.filename || "(无标题)"
            var ct = s.created_time || ""
            sessionListModel.append({
                filename: fn,
                created_time: ct,
                dateGroup: getDateGroup(ct),
                displayName: getDisplayName(fn),
                displayTime: getDisplayTime(ct)
            })
        }
    }

    // ====== 布局 ======

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // ====== 会话侧边栏 ======
        Rectangle {
            id: sessionSidebar
            visible: root.sidebarVisible
            color: theme ? theme.cardColor : "#FFFFFF"
            Layout.preferredWidth: 240
            Layout.fillHeight: true

            // 右侧分割线
            Rectangle {
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: 1
                color: theme ? theme.separatorColor : Qt.rgba(0,0,0,0.06)
            }

            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                // 侧边栏头
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 48
                    color: "transparent"

                    Row {
                        anchors.left: parent.left
                        anchors.leftMargin: 16
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 8

                        Button {
                            width: 28; height: 28; flat: true
                            onClicked: root.sidebarVisible = false
                            background: Rectangle {
                                radius: 6
                                color: parent.hovered ? (theme ? theme.hoverColor : Qt.rgba(0,0,0,0.04)) : "transparent"
                                Behavior on color { ColorAnimation { duration: 150 } }
                            }
                            contentItem: Icon {
                                iconName: "chevron-left"
                                iconColor: theme ? theme.accentColor : "#AF52DE"
                                size: 16
                            }
                        }

                        Label {
                            text: "会话"
                            font.pixelSize: theme ? theme.fontSizeTitle : 17
                            font.weight: theme ? theme.fontWeightSemibold : Font.DemiBold
                            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                            color: theme ? theme.textColor : "#1C1C1E"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    Button {
                        anchors.right: parent.right
                        anchors.rightMargin: 8
                        anchors.verticalCenter: parent.verticalCenter
                        width: 28; height: 28; flat: true
                        onClicked: chatBridge.refreshSessions()
                        background: Rectangle {
                            radius: 6
                            color: parent.hovered ? (theme ? theme.hoverColor : Qt.rgba(0,0,0,0.04)) : "transparent"
                            Behavior on color { ColorAnimation { duration: 150 } }
                        }
                        contentItem: Icon {
                            iconName: "refresh"
                            iconColor: theme ? theme.accentColor : "#AF52DE"
                            size: 16
                        }
                    }
                }

                // 会话列表（日期分组）
                ListView {
                    id: sessionListView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    Layout.topMargin: 4
                    model: sessionListModel
                    spacing: 2
                    clip: true

                    // 日期分组
                    section.property: "dateGroup"
                    section.criteria: ViewSection.FullString
                    section.delegate: Rectangle {
                        width: ListView.view ? ListView.view.width : 0
                        height: 28
                        color: "transparent"

                        Label {
                            anchors.left: parent.left
                            anchors.leftMargin: 8
                            anchors.verticalCenter: parent.verticalCenter
                            text: section
                            font.pixelSize: theme ? theme.fontSizeCaption : 11
                            font.weight: theme ? theme.fontWeightSemibold : Font.DemiBold
                            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                            color: theme ? theme.secondaryText : "#8E8E93"
                        }
                    }

                    // 空列表占位
                    Label {
                        anchors.centerIn: parent
                        text: "暂无会话"
                        font.pixelSize: theme ? theme.fontSizeBody : 13
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        color: theme ? theme.tertiaryText : "#C7C7CC"
                        visible: sessionListView.count === 0
                    }

                    delegate: Item {
                        width: sessionListView.width - 16
                        height: 44

                        property bool isActive: filename === root.currentSessionFilename

                        MouseArea {
                            id: hoverArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                root.currentSessionFilename = filename
                                root.currentSessionName = displayName
                                root.loadSession(filename)
                            }
                        }

                        Rectangle {
                            anchors.fill: parent
                            radius: 8
                            color: isActive
                                   ? Qt.rgba(0.686, 0.322, 0.871, 0.12)
                                   : (hoverArea.containsMouse
                                      ? (theme ? theme.hoverColor : Qt.rgba(0,0,0,0.04))
                                      : "transparent")
                            Behavior on color { ColorAnimation { duration: 150 } }
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
                                    text: displayName
                                    font.pixelSize: theme ? theme.fontSizeBody : 13
                                    font.weight: isActive
                                           ? (theme ? theme.fontWeightMedium : Font.Medium)
                                           : (theme ? theme.fontWeightRegular : Font.Normal)
                                    font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                    color: isActive
                                           ? (theme ? theme.accentColor : "#AF52DE")
                                           : (theme ? theme.textColor : "#1C1C1E")
                                    elide: Text.ElideRight
                                    width: parent.width
                                }

                                Label {
                                    text: displayTime
                                    font.pixelSize: theme ? theme.fontSizeCaption : 11
                                    font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                    color: theme ? theme.secondaryText : "#8E8E93"
                                }
                            }

                            // 删除按钮
                            Item {
                                Layout.alignment: Qt.AlignVCenter
                                width: 28; height: 28
                                property bool delHovered: false
                                visible: hoverArea.containsMouse || delHovered

                                Rectangle {
                                    anchors.centerIn: parent
                                    width: 24; height: 24; radius: 6
                                    color: parent.delHovered
                                           ? Qt.rgba(1, 0.231, 0.188, 0.12)
                                           : "transparent"
                                    Behavior on color { ColorAnimation { duration: 150 } }
                                }

                                Icon {
                                    anchors.centerIn: parent
                                    iconName: "trash"
                                    iconColor: parent.delHovered
                                               ? (theme ? theme.errorBg : "#FF3B30")
                                               : (theme ? theme.tertiaryText : "#C7C7CC")
                                    size: 14
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    hoverEnabled: true
                                    onEntered: parent.delHovered = true
                                    onExited: parent.delHovered = false
                                    onClicked: root.deleteSession(filename)
                                }
                            }
                        }
                    }

                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                        width: 4
                        contentItem: Rectangle {
                            radius: 2
                            color: theme ? theme.tertiaryText : "#C7C7CC"
                            opacity: 0.5
                        }
                    }
                }

                // 新建会话按钮
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 40
                    Layout.leftMargin: 12
                    Layout.rightMargin: 12
                    Layout.bottomMargin: 12
                    Layout.topMargin: 4
                    radius: 10
                    color: theme ? theme.accentColor : "#AF52DE"

                    property bool btnHovered: false
                    property bool btnPressed: false
                    scale: btnPressed ? 0.97 : 1.0
                    Behavior on scale {
                        SpringAnimation { spring: 4; damping: 0.4; mass: 0.5 }
                    }

                    Rectangle {
                        anchors.fill: parent
                        radius: parent.radius
                        color: parent.btnHovered ? Qt.rgba(1,1,1,0.12) : "transparent"
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }

                    Row {
                        anchors.centerIn: parent
                        spacing: 6

                        Icon {
                            iconName: "plus"
                            iconColor: "#FFFFFF"
                            size: 16
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Label {
                            text: "新建会话"
                            color: "#FFFFFF"
                            font.pixelSize: theme ? theme.fontSizeBody : 13
                            font.weight: theme ? theme.fontWeightMedium : Font.Medium
                            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                            antialiasing: true
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        hoverEnabled: true
                        onEntered: parent.btnHovered = true
                        onExited: parent.btnHovered = false
                        onPressed: parent.btnPressed = true
                        onReleased: parent.btnPressed = false
                        onClicked: {
                            root.currentSessionFilename = ""
                            root.currentSessionName = ""
                            root.newSession()
                        }
                    }
                }
            }
        }

        // ====== 聊天主区域 ======
        Column {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // 头栏
            Rectangle {
                width: parent.width
                height: 48
                color: theme ? theme.cardColor : "#FFFFFF"

                // 底部分割线
                Rectangle {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: 1
                    color: theme ? theme.separatorColor : Qt.rgba(0,0,0,0.06)
                }

                Row {
                    anchors.left: parent.left
                    anchors.leftMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8

                    // 菜单按钮（侧边栏隐藏时显示）
                    Item {
                        width: 32; height: 32
                        anchors.verticalCenter: parent.verticalCenter
                        visible: !root.sidebarVisible
                        property bool menuHovered: false

                        Rectangle {
                            anchors.fill: parent
                            radius: 8
                            color: parent.menuHovered
                                   ? (theme ? theme.hoverColor : Qt.rgba(0,0,0,0.04))
                                   : "transparent"
                            Behavior on color { ColorAnimation { duration: 150 } }
                        }

                        Icon {
                            anchors.centerIn: parent
                            iconName: "sidebar"
                            iconColor: theme ? theme.accentColor : "#AF52DE"
                            size: 18
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            hoverEnabled: true
                            onEntered: parent.menuHovered = true
                            onExited: parent.menuHovered = false
                            onClicked: root.sidebarVisible = !root.sidebarVisible
                        }
                    }

                    // 标题：显示当前会话名或 "MARS mini"
                    Label {
                        anchors.verticalCenter: parent.verticalCenter
                        text: root.currentSessionName || "MARS mini"
                        font.pixelSize: theme ? theme.fontSizeTitle : 17
                        font.weight: theme ? theme.fontWeightSemibold : Font.DemiBold
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        color: theme ? theme.textColor : "#1C1C1E"
                    }
                }
            }

            // 消息列表 + 空状态
            Item {
                id: messageArea
                width: parent.width
                height: parent.height - 48 - (theme ? theme.inputBarHeight : 64)

                ListView {
                    id: messageList
                    anchors.fill: parent
                    model: chatModel
                    clip: true
                    spacing: 8
                    cacheBuffer: 200
                    visible: chatModel.count > 0

                    onCountChanged: Qt.callLater(positionViewAtEnd)

                    delegate: MessageBubble {
                        width: messageList.width
                        theme: root.theme
                        sender: model.sender || "user"
                        message: model.message || ""
                        toolName: model.toolName || ""
                        toolResult: model.toolResult || ""
                        isNewMessage: index === messageList.count - 1
                    }

                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                        width: 6
                        background: Rectangle { color: "transparent" }
                        contentItem: Rectangle {
                            radius: 3
                            color: theme ? theme.tertiaryText : "#C7C7CC"
                            opacity: 0.5
                        }
                    }
                }

                // 空状态欢迎页
                Column {
                    anchors.centerIn: parent
                    visible: chatModel.count === 0
                    spacing: 16

                    // 应用 Logo
                    Rectangle {
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: 72; height: 72
                        radius: 16
                        color: theme ? theme.accentColor : "#AF52DE"

                        Label {
                            anchors.centerIn: parent
                            text: "M"
                            font.pixelSize: 36
                            font.weight: Font.Bold
                            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                            color: "#FFFFFF"
                        }
                    }

                    // 应用名
                    Label {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "MARS mini"
                        font.pixelSize: theme ? theme.fontSizeTitle : 17
                        font.weight: theme ? theme.fontWeightSemibold : Font.DemiBold
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        color: theme ? theme.textColor : "#1C1C1E"
                    }

                    // 引导提示
                    Label {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "在下方输入消息，开始一段新对话"
                        font.pixelSize: theme ? theme.fontSizeBody : 13
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        color: theme ? theme.secondaryText : "#8E8E93"
                    }
                }
            }

            // 输入栏
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
