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

        Label {
            text: "\u{1F527} 可用工具"
            font.pixelSize: 20
            font.bold: true
            font.family: theme ? theme.defaultFontFamily : "Segoe UI"
            color: theme ? theme.textColor : "#333"
            antialiasing: true
        }

        Label {
            text: "共 " + root.tools.length + " 个工具"
            font.pixelSize: 12
            font.family: theme ? theme.defaultFontFamily : "Segoe UI"
            color: theme ? theme.secondaryText : "#999"
            antialiasing: true
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
                width: grid.cellWidth - grid.cardGap
                height: grid.cardHeight
                theme: root.theme
                cardTitle: modelData.name

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