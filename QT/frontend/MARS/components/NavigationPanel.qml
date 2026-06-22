import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import MARS 1.0
import "../components"

/**
 * NavigationPanel — 导航侧边栏
 * 图标+文字导航，支持页面切换和深色/亮色模式切换
 */
Item {
    id: root

    property var theme: null
    property int currentIndex: 0
    signal itemClicked(int index)

    readonly property var navItems: [
        { icon: "chat", label: "对话" },
        { icon: "camera", label: "视觉" },
        { icon: "tools-outline", label: "工具" },
        { icon: "settings", label: "设置" }
    ]

    width: theme ? theme.navWidth : 72

    Rectangle {
        anchors.fill: parent
        color: root.theme ? root.theme.navBg : "rgba(242,242,247,0.85)"

        // 右侧细分割线
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

            // Logo
            Item {
                Layout.preferredHeight: 60
                Layout.fillWidth: true

                Rectangle {
                    anchors.centerIn: parent
                    width: 36
                    height: 36
                    radius: 10
                    color: root.theme ? root.theme.accentColor : "#AF52DE"

                    // 微妙渐变感
                    Rectangle {
                        anchors.fill: parent
                        radius: parent.radius
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: Qt.lighter(root.theme ? root.theme.accentColor : "#AF52DE", 1.1) }
                            GradientStop { position: 1.0; color: Qt.darker(root.theme ? root.theme.accentColor : "#AF52DE", 1.05) }
                        }
                    }

                    Label {
                        anchors.centerIn: parent
                        text: "M"
                        color: "#FFFFFF"
                        font.bold: true
                        font.pixelSize: 18
                        font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                        z: 1
                    }
                }
            }

            // 导航项
            Repeater {
                model: navItems
                delegate: navDelegate
            }

            Item { Layout.fillHeight: true }

            // 暗色/亮色切换
            Item {
                Layout.preferredHeight: 56
                Layout.fillWidth: true

                Rectangle {
                    anchors.fill: parent
                    anchors.margins: 6
                    radius: 10
                    color: themeToggleArea.containsMouse
                           ? (root.theme ? root.theme.navHoverBg : "transparent")
                           : "transparent"
                    Behavior on color { ColorAnimation { duration: 200 } }

                    Column {
                        anchors.centerIn: parent
                        spacing: 3

                        Icon {
                            anchors.horizontalCenter: parent.horizontalCenter
                            iconName: root.theme && root.theme.darkMode ? "sun" : "moon"
                            iconColor: root.theme && root.theme.darkMode ? "#98989F" : "#8E8E93"
                            size: 20
                        }

                        Label {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: root.theme && root.theme.darkMode ? "亮色" : "暗色"
                            font.pixelSize: 9
                            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                            color: root.theme && root.theme.darkMode ? "#98989F" : "#8E8E93"
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
    }

    Component {
        id: navDelegate

        Item {
            Layout.preferredHeight: 56
            Layout.fillWidth: true

            property bool isActive: root.currentIndex === index
            property bool isHovered: false

            // 选中背景
            Rectangle {
                anchors.fill: parent
                anchors.margins: 6
                radius: 10
                color: {
                    if (isActive) return theme ? theme.navActiveBg : Qt.rgba(0.686, 0.322, 0.870, 0.12)
                    if (isHovered) return theme ? theme.navHoverBg : Qt.rgba(0,0,0,0.03)
                    return "transparent"
                }
                Behavior on color { ColorAnimation { duration: 200 } }
            }

            Column {
                anchors.centerIn: parent
                spacing: 3

                Icon {
                    anchors.horizontalCenter: parent.horizontalCenter
                    iconName: modelData.icon
                    iconColor: isActive
                               ? (theme ? theme.accentColor : "#AF52DE")
                               : (theme ? theme.navText : "#8E8E93")
                    size: 22
                }

                Label {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: modelData.label
                    font.pixelSize: 10
                    font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                    font.weight: isActive ? (theme ? theme.fontWeightSemibold : Font.DemiBold) : (theme ? theme.fontWeightRegular : Font.Normal)
                    antialiasing: true
                    color: isActive
                           ? (theme ? theme.accentColor : "#AF52DE")
                           : (theme ? theme.navText : "#8E8E93")
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
