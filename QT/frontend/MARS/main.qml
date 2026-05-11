import QtQuick
import QtQuick.Controls
import MARS 1.0

Window {
    id: root
    width:960
    height:640
    visible: true
    title: "MARS AI AGENT"
    readonly property var theme: FluentTheme {}

    Rectangle {
        anchors.fill: parent
        color: theme.bgColor

        Label {
            anchors.centerIn: parent
            text: "Hello MARS"
            font.pointSize: 24
            color: theme.textColor
        }
    }

    Shortcut {
        sequence: "T"
        onActivated: {
            root.theme.darkMode = !root.theme.darkMode
            console.log("darkMode toggled:", root.theme.darkMode)
        }
    }

    
    
}