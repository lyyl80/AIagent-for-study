import QtQuick
import QtQuick.Controls

/**
 * FluentCard — Apple 风格卡片容器
 * 柔和多层阴影、细腻边框、统一的圆角和间距
 */
Item {
    id: root

    property alias cardTitle: titleLabel.text
    property bool elevated: true
    property var theme: null
    property color cardBorder: "transparent"

    default property alias content: contentArea.data

    // 柔和阴影层（Apple 风格：多层叠加）
    Rectangle {
        id: shadowLayer2
        anchors.fill: cardSurface
        anchors.topMargin: 1
        radius: cardSurface.radius
        visible: elevated
        color: theme && theme.darkMode ? Qt.rgba(0,0,0,0.15) : Qt.rgba(0,0,0,0.02)
    }

    Rectangle {
        id: shadowLayer1
        anchors.fill: cardSurface
        anchors.topMargin: 2
        radius: cardSurface.radius
        visible: elevated
        color: theme && theme.darkMode ? Qt.rgba(0,0,0,0.2) : Qt.rgba(0,0,0,0.03)
    }

    // 卡片表面
    Rectangle {
        id: cardSurface
        anchors.fill: parent
        radius: theme ? theme.cornerRadiusMd : 10
        color: theme ? theme.cardColor : "#FFFFFF"
        border.color: root.cardBorder === "transparent"
                       ? (theme && !theme.darkMode ? Qt.rgba(0,0,0,0.04) : "transparent")
                       : root.cardBorder
        border.width: (root.cardBorder !== "transparent" || (theme && !theme.darkMode)) ? 1 : 0

        // 标题区域
        Label {
            id: titleLabel
            visible: text !== ""
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 20

            font.pixelSize: theme ? theme.fontSizeHeadline : 15
            font.weight: theme ? theme.fontWeightSemibold : Font.DemiBold
            font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
            color: theme ? theme.textColor : "#1C1C1E"
            antialiasing: true
        }

        // 内容区域
        Item {
            id: contentArea
            anchors.top: titleLabel.visible ? titleLabel.bottom : parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.topMargin: titleLabel.visible ? 12 : 0
        }
    }
}
