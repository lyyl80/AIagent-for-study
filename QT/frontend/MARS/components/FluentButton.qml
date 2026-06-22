import QtQuick
import QtQuick.Controls

/**
 * FluentButton — Apple 风格按钮
 * 三种样式: primary(filled) / secondary(gray) / plain(text)
 * Spring 按压动画, 15px Medium 字体, 8px 圆角
 */
Button {
    id: root

    property var theme: null
    property string iconText: ""
    property int iconSize: 16
    property bool primary: true
    property string variant: "primary"  // "primary" | "secondary" | "plain"

    implicitHeight: theme ? theme.buttonHeight : 36
    implicitWidth: {
        var w = iconText !== "" ? 80 : 60
        if (text !== "") w = Math.max(w, 80)
        return w
    }
    padding: 0

    // 按压弹性缩放
    scale: pressed ? 0.96 : 1.0
    Behavior on scale {
        SpringAnimation { spring: 4; damping: 0.4; mass: 0.5 }
    }

    background: Rectangle {
        radius: theme ? theme.cornerRadiusSm : 8
        color: {
            if (!enabled) return theme ? theme.secondaryBg : "#E5E5EA"

            var v = root.variant
            if (v === "primary") {
                if (root.down) return theme ? theme.accentPressed : Qt.darker("#AF52DE", 1.1)
                if (root.hovered) return theme ? theme.accentHover : Qt.lighter("#AF52DE", 1.12)
                return theme ? theme.accentColor : "#AF52DE"
            }
            if (v === "secondary") {
                if (root.down) return theme ? Qt.darker(theme.secondaryBg, 1.1) : "#D1D1D6"
                if (root.hovered) return theme ? Qt.darker(theme.secondaryBg, 1.05) : "#E0E0E5"
                return theme ? theme.secondaryBg : "#E5E5EA"
            }
            // plain
            if (root.hovered) return theme ? theme.hoverColor : Qt.rgba(0,0,0,0.04)
            return "transparent"
        }

        Behavior on color { ColorAnimation { duration: 150 } }

        border.color: root.variant === "plain" && root.hovered
                      ? "transparent"
                      : "transparent"
        border.width: 0
    }

    contentItem: Item {
        Row {
            anchors.centerIn: parent
            spacing: 6

            Label {
                text: root.iconText
                font.pixelSize: root.iconSize
                visible: root.iconText !== ""
                color: {
                    var v = root.variant
                    if (v === "primary") return "#FFFFFF"
                    if (v === "secondary") return theme ? theme.textColor : "#1C1C1E"
                    return theme ? theme.accentColor : "#AF52DE"
                }
                verticalAlignment: Text.AlignVCenter
            }

            Label {
                text: root.text
                font.pixelSize: theme ? theme.fontSizeBody : 13
                font.weight: theme ? theme.fontWeightMedium : Font.Medium
                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                visible: root.text !== ""
                color: {
                    var v = root.variant
                    if (v === "primary") return "#FFFFFF"
                    if (v === "secondary") return theme ? theme.textColor : "#1C1C1E"
                    return theme ? theme.accentColor : "#AF52DE"
                }
                verticalAlignment: Text.AlignVCenter
            }
        }
    }
}
