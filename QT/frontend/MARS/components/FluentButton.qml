import QtQuick
import QtQuick.Controls

Button {
    id: root

    property var theme: null
    property string iconText: ""
    property int iconSize: 16
    property bool primary: true   // 主色填充 / 透明

    implicitHeight: 36
    implicitWidth: iconText !== "" ? 80 : 60
    padding: 0

    // 背景
    background: Rectangle {
        radius: 6
        color: {
            if (!enabled) return theme ? theme.dividerColor : "#ccc"
            if (root.down) return Qt.darker(bgColor, 1.15)
            if (root.hovered) return Qt.lighter(bgColor, 1.08)
            return bgColor
        }
        Behavior on color { ColorAnimation { duration: 100 } }

        readonly property color bgColor: primary
            ? (theme ? theme.accentColor : "#f18cb9")
            : "transparent"

        border.color: primary ? "transparent" : (theme ? theme.dividerColor : "#ccc")
        border.width: primary ? 0 : 1
    }

    // 内容
    contentItem: Item {
        Row {
            anchors.centerIn: parent
            spacing: 4

            Label {
                text: root.iconText
                font.pixelSize: root.iconSize
                visible: root.iconText !== ""
                color: primary ? "#ffffff" : (theme ? theme.textColor : "#333")
            }
            Label {
                text: root.text
                font.pixelSize: 13
                visible: root.text !== ""
                color: primary ? "#ffffff" : (theme ? theme.textColor : "#333")
            }
        }
    }

}