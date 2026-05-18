import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0

Rectangle {
    id: root

    property var theme: null
    property var tools: []

    color: theme ? theme.bgColor : "#f0f0f0"

    Component.onCompleted: {
        tools = chatBridge.getTools()
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Label {
                text: "\u{1F527} 可用工具"
                font.pixelSize: 20
                font.bold: true
                font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                color: theme ? theme.textColor : "#333"
                antialiasing: true
                Layout.fillWidth: true
            }

            Label {
                text: "共 " + root.tools.length + " 个"
                font.pixelSize: 12
                font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                color: theme ? theme.secondaryText : "#999"
                antialiasing: true
                Layout.alignment: Qt.AlignBottom
            }

            Button {
                id: enableAllBtn
                text: "全开"
                font.pixelSize: 12
                font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                flat: true
                antialiasing: true
                enabled: root.tools.some(function(t) { return !t.enabled })
                contentItem: Label {
                    text: parent.text
                    font: parent.font
                    color: parent.enabled
                           ? (parent.hovered
                              ? (theme ? theme.accentColor : "#4a9eff")
                              : (theme ? theme.secondaryText : "#666"))
                           : (theme ? Qt.rgba(theme.secondaryText.r, theme.secondaryText.g, theme.secondaryText.b, 0.35) : "#ccc")
                    antialiasing: true
                }
                background: Rectangle {
                    implicitWidth: 48
                    implicitHeight: 26
                    radius: 13
                    color: parent.enabled && parent.hovered
                           ? (theme ? theme.hoverColor : "#e0e0ec") : "transparent"
                    Behavior on color { ColorAnimation { duration: 120 } }
                }
                onClicked: {
                    for (var i = 0; i < root.tools.length; i++) {
                        chatBridge.setToolEnabled(root.tools[i].name, true)
                    }
                    root.tools = chatBridge.getTools()
                }
            }

            Button {
                id: disableAllBtn
                text: "全关"
                font.pixelSize: 12
                font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                flat: true
                antialiasing: true
                enabled: root.tools.some(function(t) { return t.enabled })
                contentItem: Label {
                    text: parent.text
                    font: parent.font
                    color: parent.enabled
                           ? (parent.hovered
                              ? (theme ? theme.accentColor : "#4a9eff")
                              : (theme ? theme.secondaryText : "#666"))
                           : (theme ? Qt.rgba(theme.secondaryText.r, theme.secondaryText.g, theme.secondaryText.b, 0.35) : "#ccc")
                    antialiasing: true
                }
                background: Rectangle {
                    implicitWidth: 48
                    implicitHeight: 26
                    radius: 13
                    color: parent.enabled && parent.hovered
                           ? (theme ? theme.hoverColor : "#e0e0ec") : "transparent"
                    Behavior on color { ColorAnimation { duration: 120 } }
                }
                onClicked: {
                    for (var i = 0; i < root.tools.length; i++) {
                        chatBridge.setToolEnabled(root.tools[i].name, false)
                    }
                    root.tools = chatBridge.getTools()
                }
            }
        }

        GridView {
            id: grid
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: root.tools

            property int cardWidth: 320
            property int cardHeight: 160
            property int cardGap: 12
            property int colCount: Math.max(1, Math.floor(width / (cardWidth + cardGap)))
            cellWidth: width / colCount
            cellHeight: cardHeight + cardGap

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
                width: 8
                contentItem: Rectangle {
                    radius: 4
                    color: theme ? theme.dividerColor : "#ccc"
                }
            }

            delegate: FluentCard {
                id: toolCard
                width: grid.cellWidth - grid.cardGap
                height: grid.cardHeight
                theme: root.theme
                cardTitle: modelData.name
                opacity: toolSwitch.checked ? 1.0 : 0.55

                Item {
                    id: toolSwitch
                    z: 1
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.topMargin: 12
                    anchors.rightMargin: 12
                    width: 36
                    height: 20

                    property bool checked: false

                    Component.onCompleted: {
                        checked = modelData.enabled
                    }

                    Rectangle {
                        anchors.fill: parent
                        radius: 10
                        color: toolSwitch.checked
                               ? (theme ? theme.accentColor : "#4a9eff")
                               : (theme ? Qt.rgba(theme.textColor.r, theme.textColor.g, theme.textColor.b, 0.15) : "#ccc")
                    }

                    Rectangle {
                        id: thumb
                        width: 16
                        height: 16
                        radius: 8
                        y: 2
                        x: toolSwitch.checked ? toolSwitch.width - width - 2 : 2
                        color: toolSwitch.checked ? "#fff" : (theme ? theme.textColor : "#555")
                        Behavior on x {
                            NumberAnimation { duration: 120; easing.type: Easing.OutQuad }
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

                Flickable {
                    anchors.fill: parent
                    anchors.margins: 14
                    anchors.topMargin: 0
                    contentHeight: contentColumn.height
                    clip: true
                    interactive: true

                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                        width: 4
                        contentItem: Rectangle {
                            radius: 2
                            color: theme ? theme.dividerColor : "#ccc"
                        }
                    }

                    Column {
                        id: contentColumn
                        width: parent.width
                        spacing: 6

                        Label {
                            width: parent.width
                            text: modelData.description
                            font.pixelSize: 12
                            font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                            color: theme ? theme.secondaryText : "#666"
                            wrapMode: Text.Wrap
                            lineHeight: 1.4
                            maximumLineCount: 3
                            elide: Text.ElideRight
                            antialiasing: true
                        }

                        Item { height: 4; width: 1 }

                        Row {
                            spacing: 6
                            visible: modelData.required_params !== ""

                            Rectangle {
                                height: requiredLabel.implicitHeight + 6
                                width: requiredLabel.implicitWidth + 12
                                radius: 4
                                color: Qt.rgba(0.8, 0.2, 0.2, 0.12)

                                Label {
                                    id: requiredLabel
                                    anchors.centerIn: parent
                                    text: modelData.required_params
                                    font.pixelSize: 11
                                    font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                                    color: "#cc3333"
                                    antialiasing: true
                                }
                            }
                        }

                        Row {
                            spacing: 6
                            visible: modelData.optional_params !== ""

                            Rectangle {
                                height: optionalLabel.implicitHeight + 6
                                width: optionalLabel.implicitWidth + 12
                                radius: 4
                                color: theme ? Qt.rgba(theme.textColor.r, theme.textColor.g, theme.textColor.b, 0.06) : Qt.rgba(0,0,0,0.04)

                                Label {
                                    id: optionalLabel
                                    anchors.centerIn: parent
                                    text: modelData.optional_params
                                    font.pixelSize: 11
                                    font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                                    color: theme ? theme.secondaryText : "#888"
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