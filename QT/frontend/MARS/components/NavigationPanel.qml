import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import MARS 1.0

Item {
    id: root

    property var theme: null
    property int currentIndex: 0
    signal itemClicked(int index)

    readonly property var navItems: [
        { icon: "chat", label: "对话" },
        { icon: "tools", label: "工具" },
        { icon: "settings", label: "设置" }
    ]

    width: theme ? theme.navWidth : 68

    Rectangle {
        anchors.fill: parent
        color: root.theme ? root.theme.navBg : "#252525"

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            Item {
                Layout.preferredHeight: 60
                Layout.fillWidth: true

                Rectangle {
                    anchors.centerIn: parent
                    width: 36
                    height: 36
                    radius: 8
                    color: root.theme ? root.theme.accentColor : "#7c3aed"

                    Label {
                        anchors.centerIn: parent
                        text: "M"
                        color: "#ffffff"
                        font.bold: true
                        font.pixelSize: 18
                    }
                }
            }

            Repeater {
                model: navItems
                delegate: navDelegate
            }

            Item { Layout.fillHeight: true }

            Item {
                Layout.preferredHeight: 56
                Layout.fillWidth: true

                Rectangle {
                    anchors.fill: parent
                    anchors.margins: 6
                    radius: 8
                    color: root.theme && themeToggleArea.containsMouse
                           ? (root.theme ? root.theme.navHoverBg : "transparent")
                           : "transparent"

                    Column {
                        anchors.centerIn: parent
                        spacing: 2

                        Icon {
                            anchors.horizontalCenter: parent.horizontalCenter
                            iconName: root.theme && root.theme.darkMode ? "circle-outline" : "circle"
                            iconColor: root.theme && root.theme.darkMode ? "#8a8a9a" : "#3a3a50"
                            size: 18
                        }

                        Label {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: root.theme && root.theme.darkMode ? "亮色" : "暗色"
                            font.pixelSize: 9
                            color: root.theme && root.theme.darkMode ? "#a0a0b0" : "#4a4a60"
                        }
                    }

                    MouseArea {
                        id: themeToggleArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor

                        onClicked: {
                            if (root.theme) root.theme.darkMode = !root.theme.darkMode
                        }
                    }
                }
            }
        }

        Item {
            Layout.preferredHeight: 12
        }
    }

    Component {
        id: navDelegate

        Item {
            Layout.preferredHeight: 56
            Layout.fillWidth: true

            property bool isActive: root.currentIndex === index
            property bool isHovered: false

            Rectangle {
                x: 0
                width: 3
                height: 20
                radius: 1.5
                y: parent.height / 2 - height / 2
                visible: isActive
                color: theme ? theme.navIndicator : "#7c3aed"
            }

            Rectangle {
                anchors.fill: parent
                anchors.margins: 6
                radius: 8
                color: {
                    if (isActive) return theme ? theme.navActiveBg : "#3a3a3a"
                    if (isHovered) return theme ? theme.navHoverBg : "transparent"
                    return "transparent"
                }
                Behavior on color { ColorAnimation { duration: 150 } }
            }

            Column {
                anchors.centerIn: parent
                spacing: 2

                Icon {
                    anchors.horizontalCenter: parent.horizontalCenter
                    iconName: modelData.icon
                    iconColor: isActive
                               ? (theme && theme.darkMode ? "#ffffff" : "#7c3aed")
                               : (theme && theme.darkMode ? "#8a8a9a" : "#2a2a40")
                    size: 20
                }

                Label {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: modelData.label
                    font.pixelSize: 9
                    font.family: theme ? theme.defaultFontFamily : "Segoe UI"
                    renderType: Text.NativeRendering
                    antialiasing: true
                    color: isActive
                           ? (theme && theme.darkMode ? "#ffffff" : "#7c3aed")
                           : (theme && theme.darkMode ? "#8a8a9a" : "#3a3a50")
                }
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                hoverEnabled: true

                onEntered: isHovered = true
                onExited: isHovered = false

                onClicked: {
                    currentIndex = index
                    itemClicked(index)
                }
            }
        }
    }
}
