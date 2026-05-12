import QtQuick
import QtQuick.Controls

Item {
    id: root

    property alias cardTitle: titleLabel.text
    property bool elevated: true
    property var theme: null

    default property alias content: contentArea.data

    // 阴影层（位于卡片表面下方，偏移 2px）
    Rectangle {
        id: shadowRect
        anchors.fill: cardSurface
        anchors.topMargin: 2
        anchors.leftMargin: 2
        radius: cardSurface.radius
        visible: elevated
        color: theme && theme.darkMode
               ? Qt.rgba(0, 0, 0, 0.3)
               : Qt.rgba(0, 0, 0, 0.1)
    }

    // 卡片表面
    Rectangle {
        id: cardSurface
        anchors.fill: parent
        radius: theme ? theme.cardRadius : 8
        color: theme ? theme.cardColor : "#ffffff"

        // 标题
        Label {
            id: titleLabel
            visible: text !== ""
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 16
            font.pixelSize: 14
            font.bold: true
            color: theme ? theme.textColor : "#333"
        }

        // 内容区（留给调用方填充）
        Item {
            id: contentArea
            anchors.top: titleLabel.visible ? titleLabel.bottom : parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.topMargin: titleLabel.visible ? 16 : 0
        }
    }
}
