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
                }

                Row {
                    spacing: 8

                    TextField {
                        id: customModelInput
                        width: 200
                        placeholderText: "输入自定义模型名..."
                        font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                        color: theme ? theme.textColor : "#333"
                        placeholderTextColor: theme ? theme.secondaryText : "#909090"
                        background: Rectangle {
                            radius: 6
                            color: theme ? theme.inputBg : "#fff"
                            border.color: theme ? theme.inputBorder : "#ccc"
                            border.width: 1
                        }
                    }

                    Button {
                        text: "添加"
                        flat: true
                        enabled: customModelInput.text.trim() !== ""
                        hoverEnabled: true
                        onClicked: {
                            chatBridge.addCustomModel(customModelInput.text.trim())
                            customModelInput.text = ""
                            root.models = chatBridge.getModelOptions()
                        }
                        background: Rectangle {
                            radius: 6
                            color: {
                                if (!parent.enabled) return theme ? theme.dividerColor : "#555"
                                if (parent.pressed) return Qt.darker(theme ? theme.accentColor : "#7c3aed", 1.2)
                                if (parent.hovered) return Qt.lighter(theme ? theme.accentColor : "#7c3aed", 1.15)
                                return theme ? theme.accentColor : "#7c3aed"
                            }
                            Behavior on color { ColorAnimation { duration: 120 } }
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