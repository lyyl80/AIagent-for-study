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
                    color: theme ? theme.textColor : "#333"
                }
                ComboBox {
                    id: modelCombo
                    model: root.models
                    textRole: "label"
                    currentIndex: 0
                    width: 260
                    
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
                }

                Row {
                    spacing: 8

                    TextField {
                        id: customModelInput
                        width: 200
                        placeholderText: "输入自定义模型名..."
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
                        onClicked: {
                            chatBridge.addCustomModel(customModelInput.text.trim())
                            customModelInput.text = ""
                            root.models = chatBridge.getModelOptions()
                        }
                        background: Rectangle {
                            radius: 6
                            color: parent.enabled ? (theme ? theme.accentColor : "#f18cb9") : "#ccc"
                        }
                        contentItem: Label {
                            anchors.centerIn: parent
                            text: parent.text
                            font.pixelSize: 13
                            color: "#fff"
                        }
                    }
                }

                // API Key
                Label {
                    text: "API Key"
                    font.pixelSize: 13
                    font.bold: true
                    color: theme ? theme.textColor : "#333"
                }
                TextField {
                    id: apiKeyField
                    width: 400
                    placeholderText: "sk-..."
                    echoMode: TextInput.Password
                    background: Rectangle {
                        radius: 6
                        color: theme ? theme.inputBg : "#fff"
                        border.color: theme ? theme.inputBorder : "#ccc"
                        border.width: 1
                    }
                }

            }
        }
    }
}