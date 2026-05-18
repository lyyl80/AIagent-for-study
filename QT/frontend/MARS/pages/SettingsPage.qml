import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root

    property var theme: null
    property var models: []

    color: theme ? theme.bgColor : "#f0f0f0"

    Component.onCompleted: {
        models = chatBridge.getModelOptions()
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0


        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 20

            Column {
                spacing: 16
                width: parent.width

                // 模型选择
                Label {
                    text: "模型选择"
                    font.pixelSize: 13
                    font.bold: true
                    font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                    color: theme ? theme.textColor : "#333"
                    antialiasing: true
                }
                ComboBox {
                    id: modelCombo
                    model: root.models
                    textRole: "label"
                    currentIndex: 0
                    width: 260
                    font.family: theme ? theme.defaultFontFamily : "Segoe UI"

                    onCurrentIndexChanged: {
                        if (currentIndex >= 0 && currentIndex < root.models.length) {
                            chatBridge.switchModel(root.models[currentIndex].key)
                        }
                    }

                    background: Rectangle {
                        radius: 6
                        color: theme ? theme.inputBg : "#fff"
                        border.color: theme ? theme.inputBorder : "#ccc"
                        border.width: 1
                    }

                    contentItem: Label {
                        text: modelCombo.displayText
                        font: modelCombo.font
                        color: theme ? theme.textColor : "#333"
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 10
                    }

                    delegate: ItemDelegate {
                        width: modelCombo.width
                        height: 32
                        highlighted: modelCombo.highlightedIndex === index
                        contentItem: Row {
                            spacing: 6
                            width: parent.width
                            Label {
                                text: modelData.label
                                font.pixelSize: 12
                                font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                                color: theme ? theme.textColor : "#333"
                                verticalAlignment: Text.AlignVCenter
                                elide: Text.ElideRight
                                width: parent.width - (delBtn.visible ? delBtn.width + 6 : 0)
                            }
                            Label {
                                id: delBtn
                                visible: modelData.category === "自定义模型"
                                text: "✕"
                                font.pixelSize: 11
                                color: theme ? theme.secondaryText : "#999"
                                antialiasing: true
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
                            radius: 4
                            color: highlighted
                                   ? (theme ? Qt.rgba(theme.textColor.r, theme.textColor.g, theme.textColor.b, 0.08) : "#e0e0e0")
                                   : "transparent"
                        }
                    }
                }

                // 自定义模型
                Label {
                    text: "自定义模型"
                    font.pixelSize: 13
                    font.bold: true
                    font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                    color: theme ? theme.textColor : "#333"
                    antialiasing: true
                }

                Row {
                    spacing: 8

                    Column {
                        spacing: 4
                        Label {
                            text: "显示名"
                            font.pixelSize: 10
                            font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                            color: theme ? theme.secondaryText : "#888"
                            antialiasing: true
                        }
                        TextField {
                            id: displayNameInput
                            width: 160
                            placeholderText: "如: GPT-4o"
                            font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                            font.pixelSize: 12
                            color: theme ? theme.textColor : "#333"
                            placeholderTextColor: theme ? theme.secondaryText : "#909090"
                            background: Rectangle {
                                radius: 6; color: theme ? theme.inputBg : "#fff"
                                border.color: theme ? theme.inputBorder : "#ccc"; border.width: 1
                            }
                        }
                    }

                    Column {
                        spacing: 4
                        Label {
                            text: "实际名"
                            font.pixelSize: 10
                            font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                            color: theme ? theme.secondaryText : "#888"
                            antialiasing: true
                        }
                        TextField {
                            id: modelKeyInput
                            width: 160
                            placeholderText: "如: gpt-4o"
                            font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                            font.pixelSize: 12
                            color: theme ? theme.textColor : "#333"
                            placeholderTextColor: theme ? theme.secondaryText : "#909090"
                            background: Rectangle {
                                radius: 6; color: theme ? theme.inputBg : "#fff"
                                border.color: theme ? theme.inputBorder : "#ccc"; border.width: 1
                            }
                        }
                    }

                    Column {
                        spacing: 4
                        Label {
                            text: "类型"
                            font.pixelSize: 10
                            font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                            color: theme ? theme.secondaryText : "#888"
                            antialiasing: true
                        }
                        ComboBox {
                            id: modelTypeCombo
                            model: ["local", "cloud"]
                            currentIndex: 0
                            width: 100
                            font.pixelSize: 12
                            font.family: theme ? theme.defaultFontFamily : "Segoe UI"

                            background: Rectangle {
                                radius: 6; color: theme ? theme.inputBg : "#fff"
                                border.color: theme ? theme.inputBorder : "#ccc"; border.width: 1
                            }

                            contentItem: Label {
                                text: modelTypeCombo.displayText
                                font: modelTypeCombo.font
                                color: theme ? theme.textColor : "#333"
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: 8
                            }

                            popup: Popup {
                                y: modelTypeCombo.height + 2
                                width: modelTypeCombo.width
                                implicitHeight: contentItem.implicitHeight
                                padding: 4
                                background: Rectangle {
                                    radius: 6
                                    color: theme ? theme.cardColor : "#fff"
                                    border.color: theme ? theme.inputBorder : "#ccc"
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

                    Button {
                        text: "添加"
                        flat: true
                        anchors.bottom: parent.bottom
                        enabled: displayNameInput.text.trim() !== "" && modelKeyInput.text.trim() !== ""
                        hoverEnabled: true
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
                        background: Rectangle {
                            radius: 6
                            color: theme ? theme.accentColor : "#7c3aed"
                            Behavior on color { ColorAnimation { duration: 120 } }
                            Rectangle {
                                anchors.fill: parent; radius: 6
                                color: !parent.parent.enabled ? (theme ? theme.dividerColor : "#555")
                                     : parent.parent.pressed ? Qt.rgba(0,0,0,0.25)
                                     : parent.parent.hovered ? Qt.rgba(1,1,1,0.2)
                                     : "transparent"
                                Behavior on color { ColorAnimation { duration: 120 } }
                            }
                        }
                        contentItem: Label {
                            anchors.centerIn: parent
                            text: parent.text
                            font.pixelSize: 13
                            font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                            color: "#fff"
                        }
                        scale: parent.pressed ? 0.95 : 1.0
                        Behavior on scale { NumberAnimation { duration: 80 } }
                    }
                }

                // API 环境变量
                Label {
                    text: "API 环境变量名"
                    font.pixelSize: 13
                    font.bold: true
                    font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                    color: theme ? theme.textColor : "#333"
                    antialiasing: true
                }
                TextField {
                    id: apiKeyField
                    width: 400
                    placeholderText: "DEEPSEEK_API_KEY"
                    font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                    color: theme ? theme.textColor : "#333"
                    placeholderTextColor: theme ? theme.secondaryText : "#909090"
                    onTextChanged: chatBridge.setApiEnvVarName(text)
                    Keys.onReturnPressed: apiKeyField.text = ""
                    background: Rectangle {
                        radius: 6
                        color: theme ? theme.inputBg : "#fff"
                        border.color: theme ? theme.inputBorder : "#ccc"
                        border.width: 1
                    }
                }

                Rectangle {
                    width: 400
                    height: hintText.implicitHeight + 16
                    radius: 6
                    color: Qt.rgba(theme ? theme.textColor.r : 0.5, theme ? theme.textColor.g : 0.5, theme ? theme.textColor.b : 0.5, 0.08)
                    Label {
                        id: hintText
                        anchors.fill: parent
                        anchors.margins: 8
                        text: "在系统环境变量中设置该名称对应的值，默认环境变量名为 DEEPSEEK_API_KEY"
                        font.pixelSize: 11
                        font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                        color: theme ? theme.secondaryText : "#888"
                        wrapMode: Text.Wrap
                        lineHeight: 1.4
                    }
                }

            }
        }
    }
}