import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
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
    property string searchText: ""
    property string editingFilename: ""
    property string editingText: ""
    property string pendingExportFilename: ""

    color: theme ? theme.bgColor : "#F2F2F7"

    signal userMessage(string text)
    signal loadSession(string filename)
    signal refreshSessions()
    signal newSession()
    signal deleteSession(string filename)
    signal regenerateMessage()
    signal renameSession(string filename, string newName)
    signal exportSession(string filename, string exportPath)

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

    function rebuildSessionModel() {
        sessionListModel.clear()
        var query = searchText.toLowerCase()
        for (var i = 0; i < sessionList.length; i++) {
            var s = sessionList[i]
            var fn = s.filename || "(无标题)"
            var ct = s.created_time || ""
            var dn = getDisplayName(fn)
            // 搜索过滤：匹配 displayName 或 filename
            if (query !== "" && dn.toLowerCase().indexOf(query) === -1 && fn.toLowerCase().indexOf(query) === -1)
                continue
            sessionListModel.append({
                filename: fn,
                created_time: ct,
                dateGroup: getDateGroup(ct),
                displayName: dn,
                displayTime: getDisplayTime(ct)
            })
        }
    }

    onSessionListChanged: rebuildSessionModel()
    onSearchTextChanged: rebuildSessionModel()

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

                // 搜索框
                Rectangle {
                    Layout.fillWidth: true
                    Layout.leftMargin: 12
                    Layout.rightMargin: 12
                    Layout.topMargin: 4
                    Layout.preferredHeight: 32
                    radius: 8
                    color: theme ? theme.inputBg : "#F2F2F7"
                    border.color: theme ? theme.inputBorder : Qt.rgba(0,0,0,0.08)
                    border.width: 1

                    Row {
                        anchors.left: parent.left
                        anchors.leftMargin: 8
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 6

                        Icon {
                            iconName: "search"
                            iconColor: theme ? theme.tertiaryText : "#C7C7CC"
                            size: 14
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        TextField {
                            id: searchField
                            width: sessionSidebar.width - 56
                            anchors.verticalCenter: parent.verticalCenter
                            placeholderText: "搜索会话"
                            placeholderTextColor: theme ? theme.tertiaryText : "#C7C7CC"
                            color: theme ? theme.textColor : "#1C1C1E"
                            font.pixelSize: theme ? theme.fontSizeBody : 13
                            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                            background: Item {}
                            selectByMouse: true

                            onTextChanged: root.searchText = text
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
                        id: sessionDelegate
                        width: sessionListView.width - 16
                        height: 44

                        property bool isActive: filename === root.currentSessionFilename
                        property bool isEditing: filename === root.editingFilename
                        property bool actionHovered: false

                        MouseArea {
                            id: hoverArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            enabled: !isEditing
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
                                   : (hoverArea.containsMouse || sessionDelegate.actionHovered
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
                                id: infoColumn
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignVCenter
                                spacing: 2
                                visible: !isEditing

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

                            // 内联重命名编辑框
                            TextField {
                                id: renameField
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignVCenter
                                visible: isEditing
                                text: root.editingText
                                color: theme ? theme.textColor : "#1C1C1E"
                                font.pixelSize: theme ? theme.fontSizeBody : 13
                                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                background: Rectangle {
                                    radius: 4
                                    color: theme ? theme.inputBg : "#F2F2F7"
                                    border.color: theme ? theme.accentColor : "#AF52DE"
                                    border.width: 1
                                }
                                selectByMouse: true
                                focus: visible

                                onTextChanged: root.editingText = text

                                onAccepted: {
                                    if (root.editingText.trim() !== "") {
                                        root.renameSession(filename, root.editingText.trim())
                                    }
                                    root.editingFilename = ""
                                }

                                Keys.onEscapePressed: {
                                    root.editingFilename = ""
                                }

                                Component.onCompleted: {
                                    if (visible) {
                                        text = root.editingText
                                        selectAll()
                                        forceActiveFocus()
                                    }
                                }
                            }

                            // 操作按钮组（hover 显示）
                            Row {
                                Layout.alignment: Qt.AlignVCenter
                                visible: (hoverArea.containsMouse || sessionDelegate.actionHovered) && !isEditing
                                spacing: 0

                                // 编辑/重命名按钮
                                Item {
                                    width: 24; height: 28
                                    property bool editHovered: false

                                    Rectangle {
                                        anchors.centerIn: parent
                                        width: 22; height: 22; radius: 5
                                        color: parent.editHovered
                                               ? (theme ? theme.hoverColor : Qt.rgba(0,0,0,0.06))
                                               : "transparent"
                                        Behavior on color { ColorAnimation { duration: 100 } }
                                    }

                                    Icon {
                                        anchors.centerIn: parent
                                        iconName: "edit"
                                        iconColor: parent.editHovered
                                                   ? (theme ? theme.accentColor : "#AF52DE")
                                                   : (theme ? theme.secondaryText : "#8E8E93")
                                        size: 13
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        hoverEnabled: true
                                        onEntered: { parent.editHovered = true; sessionDelegate.actionHovered = true }
                                        onExited: { parent.editHovered = false; sessionDelegate.actionHovered = false }
                                        onClicked: {
                                            root.editingFilename = filename
                                            root.editingText = displayName
                                        }
                                    }
                                }

                                // 导出按钮
                                Item {
                                    width: 24; height: 28
                                    property bool exportHovered: false

                                    Rectangle {
                                        anchors.centerIn: parent
                                        width: 22; height: 22; radius: 5
                                        color: parent.exportHovered
                                               ? (theme ? theme.hoverColor : Qt.rgba(0,0,0,0.06))
                                               : "transparent"
                                        Behavior on color { ColorAnimation { duration: 100 } }
                                    }

                                    Icon {
                                        anchors.centerIn: parent
                                        iconName: "arrow-down"
                                        iconColor: parent.exportHovered
                                                   ? (theme ? theme.accentColor : "#AF52DE")
                                                   : (theme ? theme.secondaryText : "#8E8E93")
                                        size: 13
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        hoverEnabled: true
                                        onEntered: { parent.exportHovered = true; sessionDelegate.actionHovered = true }
                                        onExited: { parent.exportHovered = false; sessionDelegate.actionHovered = false }
                                        onClicked: {
                                            root.pendingExportFilename = filename
                                            exportDialog.open()
                                        }
                                    }
                                }

                                // 删除按钮
                                Item {
                                    width: 24; height: 28
                                    property bool delHovered: false

                                    Rectangle {
                                        anchors.centerIn: parent
                                        width: 22; height: 22; radius: 5
                                        color: parent.delHovered
                                               ? Qt.rgba(1, 0.231, 0.188, 0.12)
                                               : "transparent"
                                        Behavior on color { ColorAnimation { duration: 100 } }
                                    }

                                    Icon {
                                        anchors.centerIn: parent
                                        iconName: "trash"
                                        iconColor: parent.delHovered
                                                   ? (theme ? theme.errorBg : "#FF3B30")
                                                   : (theme ? theme.secondaryText : "#8E8E93")
                                        size: 13
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        hoverEnabled: true
                                        onEntered: { parent.delHovered = true; sessionDelegate.actionHovered = true }
                                        onExited: { parent.delHovered = false; sessionDelegate.actionHovered = false }
                                        onClicked: root.deleteSession(filename)
                                    }
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

            // 头栏 — 仅标题文字，无背景遮挡
            Item {
                id: chatHeader
                height: 40
                width: parent.width

                Row {
                    id: titleRow
                    anchors.left: parent.left
                    anchors.leftMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8

                    // 菜单按钮（侧边栏隐藏时显示）
                    Item {
                        width: 28; height: 28
                        anchors.verticalCenter: parent.verticalCenter
                        visible: !root.sidebarVisible
                        property bool menuHovered: false

                        Rectangle {
                            anchors.fill: parent
                            radius: 6
                            color: parent.menuHovered
                                   ? (theme ? theme.hoverColor : Qt.rgba(0,0,0,0.04))
                                   : "transparent"
                            Behavior on color { ColorAnimation { duration: 150 } }
                        }

                        Icon {
                            anchors.centerIn: parent
                            iconName: "sidebar"
                            iconColor: theme ? theme.accentColor : "#AF52DE"
                            size: 16
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
                height: parent.height - chatHeader.height - inputBar.height

                ListView {
                    id: messageList
                    anchors.fill: parent
                    model: chatModel
                    clip: true
                    spacing: 8
                    cacheBuffer: 200
                    visible: chatModel.count > 0

                    onCountChanged: Qt.callLater(positionViewAtEnd)

                    // 打字指示器（AI 思考时显示在列表底部）
                    footer: Item {
                        width: messageList.width
                        height: root.isThinking ? 48 : 0
                        visible: root.isThinking

                        TypingIndicator {
                            anchors.left: parent.left
                            anchors.leftMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            theme: root.theme
                        }
                    }

                    delegate: MessageBubble {
                        width: messageList.width
                        theme: root.theme
                        sender: model.sender || "user"
                        message: model.message || ""
                        toolName: model.toolName || ""
                        toolResult: model.toolResult || ""
                        isNewMessage: index === messageList.count - 1

                        onCopyMessage: function(text) {
                            chatBridge.copyToClipboard(text)
                        }

                        onRegenerateMessage: {
                            root.regenerateMessage()
                        }
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

                // 滚动到底部按钮
                Rectangle {
                    id: scrollBottomBtn
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.rightMargin: 16
                    anchors.bottomMargin: 16
                    width: 36
                    height: 36
                    radius: 18
                    color: theme ? theme.cardColor : "#FFFFFF"
                    border.color: theme ? theme.separatorColor : Qt.rgba(0,0,0,0.08)
                    border.width: 1
                    visible: chatModel.count > 0 && !messageList.atYEnd

                    // 入场/退场动画
                    opacity: visible ? 1 : 0
                    scale: visible ? 1 : 0.5
                    Behavior on opacity { NumberAnimation { duration: 200; easing.type: Easing.OutQuart } }
                    Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutQuart } }

                    property bool hovered: false

                    Rectangle {
                        anchors.fill: parent
                        radius: parent.radius
                        color: scrollBottomBtn.hovered
                               ? (theme ? theme.hoverColor : Qt.rgba(0,0,0,0.04))
                               : "transparent"
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }

                    Icon {
                        anchors.centerIn: parent
                        iconName: "arrow-down"
                        iconColor: scrollBottomBtn.hovered
                                   ? (theme ? theme.accentColor : "#AF52DE")
                                   : (theme ? theme.secondaryText : "#8E8E93")
                        size: 18
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        hoverEnabled: true
                        onEntered: scrollBottomBtn.hovered = true
                        onExited: scrollBottomBtn.hovered = false
                        onClicked: {
                            scrollAnim.from = messageList.contentY
                            scrollAnim.to = messageList.contentHeight - messageList.height
                            scrollAnim.start()
                        }
                    }
                }

                // 滚动动画（放在按钮外部，避免按钮隐藏时动画被中断）
                NumberAnimation {
                    id: scrollAnim
                    target: messageList
                    property: "contentY"
                    duration: 350
                    easing.type: Easing.OutQuart
                    onStopped: {
                        // 确保到达底部
                        messageList.positionViewAtEnd()
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
                id: inputBar
                theme: root.theme
                isThinking: root.isThinking

                onSendMessage: function(text) {
                    root.userMessage(text)
                }
            }
        }
    }

    // 导出文件对话框
    FileDialog {
        id: exportDialog
        title: "导出会话"
        fileMode: FileDialog.SaveFile
        defaultSuffix: "txt"
        nameFilters: ["文本文件 (*.txt)", "所有文件 (*)"]

        onAccepted: {
            if (root.pendingExportFilename !== "") {
                root.exportSession(root.pendingExportFilename, currentFile.toString().replace("file:///", ""))
                root.pendingExportFilename = ""
            }
        }
    }
}
