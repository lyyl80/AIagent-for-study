import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0
import "../components"

/**
 * SettingsPage — CC Switch 风格设置页面
 * 卡片式分组布局、标题+副标题、圆角卡片
 * 每个 section 是独立的圆角卡片，视觉层次清晰
 *
 * 注意: ScrollView 内的 Column 必须显式绑定 width: scrollView.width
 * Column 不支持 leftPadding/rightPadding, 用 x + width 控制边距
 */
Rectangle {
    id: root

    property var theme: null
    property var models: []

    color: theme ? theme.bgColor : "#000000"

    Component.onCompleted: {
        models = chatBridge.getModelOptions()
    }

    // 外层滚动区域
    ScrollView {
        id: scrollView
        anchors.fill: parent
        clip: true

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
            width: 6
            contentItem: Rectangle {
                radius: 3
                color: theme ? theme.tertiaryText : "#C7C7CC"
                opacity: 0.4
            }
        }

        // 内容列 — 宽度显式绑定到 ScrollView 宽度
        Column {
            id: settingsColumn
            width: scrollView.width  // 关键修复: 显式绑定宽度
            spacing: theme ? theme.spacing4 : 16

            // 顶部留白
            Item { width: 1; height: 24 }

            // ====== 页面标题 ======
            Label {
                x: 32
                width: parent.width - 64
                text: "设置"
                font.pixelSize: theme ? theme.fontSizeLargeTitle : 28
                font.weight: theme ? theme.fontWeightBold : Font.Bold
                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                color: theme ? theme.textColor : "#FFFFFF"
            }

            // ====== 模型选择 ======
            Column {
                x: 32
                width: parent.width - 64
                spacing: 10

                // 标题
                Column {
                    width: parent.width
                    spacing: 4

                    Label {
                        text: "模型选择"
                        font.pixelSize: theme ? theme.fontSizeHeadline : 15
                        font.weight: theme ? theme.fontWeightSemibold : Font.DemiBold
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        color: theme ? theme.textColor : "#FFFFFF"
                    }

                    Label {
                        text: "选择 AI 对话使用的模型，切换后立即生效。"
                        font.pixelSize: theme ? theme.fontSizeCaption : 11
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        color: theme ? theme.secondaryText : "#8E8E93"
                        wrapMode: Text.Wrap
                        width: parent.width
                        lineHeight: 1.4
                    }
                }

                // 卡片容器
                Rectangle {
                    width: parent.width
                    height: modelCombo.height + 24
                    radius: 12
                    color: theme ? theme.cardColor : "#1C1C1E"
                    border.color: theme ? theme.separatorColor : "rgba(84,84,88,0.2)"
                    border.width: 1

                    // 微妙阴影（亮色模式）
                    Rectangle {
                        visible: theme && !theme.darkMode
                        anchors.fill: parent
                        radius: parent.radius
                        color: Qt.rgba(0, 0, 0, 0.03)
                        z: -1
                        anchors.topMargin: 2
                    }

                    // 模型下拉框
                    ComboBox {
                        id: modelCombo
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: 16
                        anchors.rightMargin: 16
                        height: 40
                        model: root.models
                        textRole: "label"
                        currentIndex: 0
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        font.pixelSize: theme ? theme.fontSizeBody : 13

                        onCurrentIndexChanged: {
                            if (currentIndex >= 0 && currentIndex < root.models.length) {
                                chatBridge.switchModel(root.models[currentIndex].key)
                            }
                        }

                        background: Rectangle {
                            radius: 10
                            color: theme ? theme.inputBg : "#1C1C1E"
                            border.color: modelCombo.popup.visible
                                          ? (theme ? theme.accentColor : "#AF52DE")
                                          : (theme ? theme.separatorColor : "rgba(84,84,88,0.3)")
                            border.width: 1
                            Behavior on border.color { ColorAnimation { duration: 150 } }
                        }

                        contentItem: Row {
                            spacing: 8
                            leftPadding: 14

                            Icon {
                                iconName: "chat"
                                iconColor: theme ? theme.accentColor : "#AF52DE"
                                size: 16
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Label {
                                text: modelCombo.displayText
                                font: modelCombo.font
                                color: theme ? theme.textColor : "#FFFFFF"
                                verticalAlignment: Text.AlignVCenter
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }

                        indicator: Item {
                            anchors.right: parent.right
                            anchors.rightMargin: 14
                            anchors.verticalCenter: parent.verticalCenter
                            width: 14
                            height: 14

                            Icon {
                                anchors.centerIn: parent
                                iconName: "chevron-right"
                                iconColor: theme ? theme.secondaryText : "#8E8E93"
                                size: 14
                                rotation: 90
                            }
                        }

                        delegate: ItemDelegate {
                            width: modelCombo.width
                            height: 38
                            highlighted: modelCombo.highlightedIndex === index

                            contentItem: Row {
                                spacing: 8
                                leftPadding: 14
                                width: parent.width

                                Rectangle {
                                    visible: modelCombo.currentIndex === index
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: 6
                                    height: 6
                                    radius: 3
                                    color: theme ? theme.accentColor : "#AF52DE"
                                }

                                Label {
                                    text: modelData.label
                                    font.pixelSize: theme ? theme.fontSizeBody : 13
                                    font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                    font.weight: modelCombo.currentIndex === index
                                                   ? (theme ? theme.fontWeightMedium : Font.Medium)
                                                   : (theme ? theme.fontWeightRegular : Font.Normal)
                                    color: modelCombo.currentIndex === index
                                           ? (theme ? theme.accentColor : "#AF52DE")
                                           : (theme ? theme.textColor : "#FFFFFF")
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                    width: parent.width - (delBtn.visible ? delBtn.width + 20 : 28)
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Label {
                                    id: delBtn
                                    visible: modelData.category === "自定义模型"
                                    text: "删除"
                                    font.pixelSize: theme ? theme.fontSizeCaption : 11
                                    font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                    color: theme ? theme.errorBg : "#FF3B30"
                                    verticalAlignment: Text.AlignVCenter
                                    anchors.verticalCenter: parent.verticalCenter
                                    rightPadding: 14

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            chatBridge.removeCustomModel(modelData.key)
                                            root.models = chatBridge.getModelOptions()
                                        }
                                    }
                                }
                            }

                            background: Rectangle {
                                radius: 6
                                color: highlighted
                                       ? (theme ? theme.hoverColor : "rgba(255,255,255,0.06)")
                                       : "transparent"
                                Behavior on color { ColorAnimation { duration: 100 } }
                            }
                        }

                        popup: Popup {
                            y: modelCombo.height + 4
                            width: modelCombo.width
                            implicitHeight: Math.min(contentItem.implicitHeight, 360)
                            padding: 6

                            background: Rectangle {
                                radius: 10
                                color: theme ? theme.cardColor : "#1C1C1E"
                                border.color: theme ? theme.separatorColor : "rgba(84,84,88,0.2)"
                                border.width: 1

                                Rectangle {
                                    anchors.fill: parent
                                    radius: parent.radius
                                    color: Qt.rgba(0, 0, 0, theme && theme.darkMode ? 0.4 : 0.08)
                                    z: -1
                                    anchors.topMargin: 3
                                }
                            }

                            contentItem: ListView {
                                clip: true
                                implicitHeight: contentHeight
                                model: modelCombo.delegateModel
                                currentIndex: modelCombo.highlightedIndex
                            }
                        }
                    }
                }
            }

            // ====== 自定义模型 ======
            Column {
                x: 32
                width: parent.width - 64
                spacing: 10

                // 标题
                Column {
                    width: parent.width
                    spacing: 4

                    Label {
                        text: "自定义模型"
                        font.pixelSize: theme ? theme.fontSizeHeadline : 15
                        font.weight: theme ? theme.fontWeightSemibold : Font.DemiBold
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        color: theme ? theme.textColor : "#FFFFFF"
                    }

                    Label {
                        text: "添加自定义 AI 模型，填写显示名称和对应的模型标识。"
                        font.pixelSize: theme ? theme.fontSizeCaption : 11
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        color: theme ? theme.secondaryText : "#8E8E93"
                        wrapMode: Text.Wrap
                        width: parent.width
                        lineHeight: 1.4
                    }
                }

                // 卡片容器
                Rectangle {
                    width: parent.width
                    height: inputRow.height + 24
                    radius: 12
                    color: theme ? theme.cardColor : "#1C1C1E"
                    border.color: theme ? theme.separatorColor : "rgba(84,84,88,0.2)"
                    border.width: 1

                    Rectangle {
                        visible: theme && !theme.darkMode
                        anchors.fill: parent
                        radius: parent.radius
                        color: Qt.rgba(0, 0, 0, 0.03)
                        z: -1
                        anchors.topMargin: 2
                    }

                    // 输入行
                    Row {
                        id: inputRow
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: 16
                        anchors.rightMargin: 16
                        spacing: 12

                        // 显示名
                        Column {
                            spacing: 6
                            width: (parent.width - 36) * 0.3

                            Label {
                                text: "显示名"
                                font.pixelSize: theme ? theme.fontSizeCaption : 11
                                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                color: theme ? theme.secondaryText : "#8E8E93"
                            }

                            TextField {
                                id: displayNameInput
                                width: parent.width
                                height: 38
                                placeholderText: "如: GPT-4o"
                                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                font.pixelSize: theme ? theme.fontSizeBody : 13
                                color: theme ? theme.textColor : "#FFFFFF"
                                placeholderTextColor: theme ? theme.tertiaryText : "#48484A"
                                selectByMouse: true
                                background: Rectangle {
                                    radius: 8
                                    color: theme ? theme.inputBg : "#1C1C1E"
                                    border.color: displayNameInput.activeFocus
                                                   ? (theme ? theme.accentColor : "#AF52DE")
                                                   : (theme ? theme.separatorColor : "rgba(84,84,88,0.3)")
                                    border.width: 1
                                    Behavior on border.color { ColorAnimation { duration: 150 } }
                                }
                                leftPadding: 12
                            }
                        }

                        // 模型标识
                        Column {
                            spacing: 6
                            width: (parent.width - 36) * 0.3

                            Label {
                                text: "模型标识"
                                font.pixelSize: theme ? theme.fontSizeCaption : 11
                                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                color: theme ? theme.secondaryText : "#8E8E93"
                            }

                            TextField {
                                id: modelKeyInput
                                width: parent.width
                                height: 38
                                placeholderText: "如: gpt-4o"
                                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                font.pixelSize: theme ? theme.fontSizeBody : 13
                                color: theme ? theme.textColor : "#FFFFFF"
                                placeholderTextColor: theme ? theme.tertiaryText : "#48484A"
                                selectByMouse: true
                                background: Rectangle {
                                    radius: 8
                                    color: theme ? theme.inputBg : "#1C1C1E"
                                    border.color: modelKeyInput.activeFocus
                                                   ? (theme ? theme.accentColor : "#AF52DE")
                                                   : (theme ? theme.separatorColor : "rgba(84,84,88,0.3)")
                                    border.width: 1
                                    Behavior on border.color { ColorAnimation { duration: 150 } }
                                }
                                leftPadding: 12
                            }
                        }

                        // 类型
                        Column {
                            spacing: 6
                            width: (parent.width - 36) * 0.2

                            Label {
                                text: "类型"
                                font.pixelSize: theme ? theme.fontSizeCaption : 11
                                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                color: theme ? theme.secondaryText : "#8E8E93"
                            }

                            ComboBox {
                                id: modelTypeCombo
                                model: ["local", "cloud"]
                                currentIndex: 0
                                width: parent.width
                                height: 38
                                font.pixelSize: theme ? theme.fontSizeBody : 13
                                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"

                                background: Rectangle {
                                    radius: 8
                                    color: theme ? theme.inputBg : "#1C1C1E"
                                    border.color: modelTypeCombo.popup.visible
                                                   ? (theme ? theme.accentColor : "#AF52DE")
                                                   : (theme ? theme.separatorColor : "rgba(84,84,88,0.3)")
                                    border.width: 1
                                }

                                contentItem: Label {
                                    text: modelTypeCombo.displayText
                                    font: modelTypeCombo.font
                                    color: theme ? theme.textColor : "#FFFFFF"
                                    verticalAlignment: Text.AlignVCenter
                                    leftPadding: 12
                                }

                                indicator: Item {
                                    anchors.right: parent.right
                                    anchors.rightMargin: 10
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: 12
                                    height: 12

                                    Icon {
                                        anchors.centerIn: parent
                                        iconName: "chevron-right"
                                        iconColor: theme ? theme.secondaryText : "#8E8E93"
                                        size: 12
                                        rotation: 90
                                    }
                                }

                                delegate: ItemDelegate {
                                    width: modelTypeCombo.width
                                    height: 34
                                    highlighted: modelTypeCombo.highlightedIndex === index
                                    contentItem: Label {
                                        text: modelData
                                        font.pixelSize: theme ? theme.fontSizeBody : 13
                                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                        color: modelTypeCombo.currentIndex === index
                                               ? (theme ? theme.accentColor : "#AF52DE")
                                               : (theme ? theme.textColor : "#FFFFFF")
                                        verticalAlignment: Text.AlignVCenter
                                        leftPadding: 12
                                    }
                                    background: Rectangle {
                                        radius: 6
                                        color: highlighted ? (theme ? theme.hoverColor : "rgba(255,255,255,0.06)") : "transparent"
                                    }
                                }

                                popup: Popup {
                                    y: modelTypeCombo.height + 4
                                    width: modelTypeCombo.width
                                    implicitHeight: contentItem.implicitHeight + 8
                                    padding: 4
                                    background: Rectangle {
                                        radius: 8
                                        color: theme ? theme.cardColor : "#1C1C1E"
                                        border.color: theme ? theme.separatorColor : "rgba(84,84,88,0.2)"
                                        border.width: 1
                                    }
                                    contentItem: ListView {
                                        clip: true
                                        implicitHeight: contentHeight
                                        model: modelTypeCombo.delegateModel
                                        currentIndex: modelTypeCombo.highlightedIndex
                                    }
                                }
                            }
                        }

                        // 添加按钮
                        Column {
                            spacing: 6
                            width: (parent.width - 36) * 0.2

                            // 占位标签（对齐用）
                            Label {
                                text: " "
                                font.pixelSize: theme ? theme.fontSizeCaption : 11
                            }

                            Item {
                                id: addBtn
                                width: parent.width
                                height: 38

                                property bool hovered: false
                                property bool pressed: false

                                scale: pressed ? 0.96 : 1.0
                                Behavior on scale {
                                    SpringAnimation { spring: 4; damping: 0.4; mass: 0.5 }
                                }

                                Rectangle {
                                    anchors.fill: parent
                                    radius: 8
                                    color: {
                                        var canAdd = displayNameInput.text.trim() !== "" && modelKeyInput.text.trim() !== ""
                                        if (!canAdd) return theme ? theme.secondaryBg : "#2C2C2E"
                                        if (addBtn.pressed) return theme ? theme.accentPressed : Qt.darker("#AF52DE", 1.1)
                                        if (addBtn.hovered) return theme ? theme.accentHover : Qt.lighter("#AF52DE", 1.12)
                                        return theme ? theme.accentColor : "#AF52DE"
                                    }
                                    Behavior on color { ColorAnimation { duration: 150 } }
                                }

                                Row {
                                    anchors.centerIn: parent
                                    spacing: 4

                                    Icon {
                                        iconName: "plus"
                                        iconColor: "#FFFFFF"
                                        size: 14
                                        anchors.verticalCenter: parent.verticalCenter
                                    }

                                    Label {
                                        text: "添加"
                                        font.pixelSize: theme ? theme.fontSizeBody : 13
                                        font.weight: theme ? theme.fontWeightMedium : Font.Medium
                                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                        color: "#FFFFFF"
                                        anchors.verticalCenter: parent.verticalCenter
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    hoverEnabled: true
                                    enabled: displayNameInput.text.trim() !== "" && modelKeyInput.text.trim() !== ""
                                    onEntered: parent.hovered = true
                                    onExited: parent.hovered = false
                                    onPressed: parent.pressed = true
                                    onReleased: parent.pressed = false
                                    onClicked: {
                                        chatBridge.addCustomModel(
                                            modelKeyInput.text.trim(),
                                            displayNameInput.text.trim(),
                                            modelTypeCombo.currentText
                                        )
                                        displayNameInput.text = ""
                                        modelKeyInput.text = ""
                                        root.models = chatBridge.getModelOptions()
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // ====== API 环境变量 ======
            Column {
                x: 32
                width: parent.width - 64
                spacing: 10

                // 标题
                Column {
                    width: parent.width
                    spacing: 4

                    Label {
                        text: "API 环境变量"
                        font.pixelSize: theme ? theme.fontSizeHeadline : 15
                        font.weight: theme ? theme.fontWeightSemibold : Font.DemiBold
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        color: theme ? theme.textColor : "#FFFFFF"
                    }

                    Label {
                        text: "设置存放 API 密钥的环境变量名称，应用从系统环境变量中读取对应的值。"
                        font.pixelSize: theme ? theme.fontSizeCaption : 11
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        color: theme ? theme.secondaryText : "#8E8E93"
                        wrapMode: Text.Wrap
                        width: parent.width
                        lineHeight: 1.4
                    }
                }

                // 卡片容器
                Rectangle {
                    width: parent.width
                    height: apiContent.height + 24
                    radius: 12
                    color: theme ? theme.cardColor : "#1C1C1E"
                    border.color: theme ? theme.separatorColor : "rgba(84,84,88,0.2)"
                    border.width: 1

                    Rectangle {
                        visible: theme && !theme.darkMode
                        anchors.fill: parent
                        radius: parent.radius
                        color: Qt.rgba(0, 0, 0, 0.03)
                        z: -1
                        anchors.topMargin: 2
                    }

                    // 卡片内容
                    Column {
                        id: apiContent
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.leftMargin: 16
                        anchors.rightMargin: 16
                        anchors.topMargin: 16
                        spacing: 10

                        // 输入框
                        TextField {
                            id: apiKeyField
                            width: parent.width
                            height: 38
                            placeholderText: "DEEPSEEK_API_KEY"
                            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                            font.pixelSize: theme ? theme.fontSizeBody : 13
                            color: theme ? theme.textColor : "#FFFFFF"
                            placeholderTextColor: theme ? theme.tertiaryText : "#48484A"
                            selectByMouse: true
                            onTextChanged: chatBridge.setApiEnvVarName(text)
                            Keys.onReturnPressed: apiKeyField.text = ""
                            background: Rectangle {
                                radius: 8
                                color: theme ? theme.inputBg : "#1C1C1E"
                                border.color: apiKeyField.activeFocus
                                               ? (theme ? theme.accentColor : "#AF52DE")
                                               : (theme ? theme.separatorColor : "rgba(84,84,88,0.3)")
                                border.width: 1
                                Behavior on border.color { ColorAnimation { duration: 150 } }
                            }
                            leftPadding: 12
                        }

                        // 提示框 — CC Switch 风格
                        Rectangle {
                            width: parent.width
                            height: noteText.implicitHeight + 16
                            radius: 8
                            color: theme && theme.darkMode
                                   ? Qt.rgba(0.486, 0.322, 0.870, 0.06)
                                   : Qt.rgba(0.686, 0.322, 0.870, 0.04)

                            // 左侧 accent 竖条
                            Rectangle {
                                anchors.left: parent.left
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                width: 3
                                radius: 1.5
                                color: theme ? theme.accentColor : "#AF52DE"
                                opacity: 0.6
                            }

                            Label {
                                id: noteText
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.leftMargin: 14
                                anchors.rightMargin: 8
                                anchors.topMargin: 8
                                text: "应用将从系统环境变量中读取该名称对应的值。默认环境变量名为 DEEPSEEK_API_KEY，请确保在系统环境变量中设置了对应的 API 密钥。"
                                font.pixelSize: theme ? theme.fontSizeCaption : 11
                                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                                color: theme ? theme.secondaryText : "#8E8E93"
                                wrapMode: Text.Wrap
                                lineHeight: 1.5
                            }
                        }
                    }
                }
            }

            // 底部留白
            Item { width: 1; height: 32 }
        }
    }
}
