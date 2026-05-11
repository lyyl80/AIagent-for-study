import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0

Window {
    id: root
    width:960
    height:640
    minimumWidth:800
    minimumHeight: 500
    visible: true
    title: "MARS AI AGENT"
    readonly property var theme: FluentTheme {}
    color: theme.bgColor

    Shortcut {
        sequence: "T"
        onActivated: {
            root.theme.darkMode = !root.theme.darkMode
            console.log("darkMode toggled:", root.theme.darkMode)
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0
       NavigationPanel{
          id: navPanel
          theme: root.theme
          Layout.fillHeight: true

          onItemClicked:function(index) {
            pageStack.currentIndex = index
            
          }
       }
       StackLayout {
            id: pageStack
            Layout.fillWidth: true
            Layout.fillHeight: true

            // 占位页面
            Rectangle {
                color: theme.bgColor
                Label {
                    anchors.centerIn: parent
                    text: "页面 " + (StackLayout.index + 1)
                    font.pixelSize: 20
                    color: theme.textColor
                }
            }
            Rectangle { color: theme.bgColor; Label { anchors.centerIn: parent; text: "会话"; color: theme.textColor } }
            Rectangle { color: theme.bgColor; Label { anchors.centerIn: parent; text: "工具"; color: theme.textColor } }
            Rectangle { color: theme.bgColor; Label { anchors.centerIn: parent; text: "设置"; color: theme.textColor } }
        }
    }

    
    
}