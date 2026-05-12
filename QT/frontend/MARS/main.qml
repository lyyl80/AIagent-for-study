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
            ColumnLayout {
                FluentCard {
                theme: window.theme
                cardTitle: "测试卡片"
                width: 300
                height: 200
                x: 100
                y: 100
                Label {
                    text: "卡片内容"
                    color: window.theme.textColor
                    anchors.centerIn: parent
                    }
                }
                FluentButton {
                    theme: window.theme
                    text: "测试按钮"
                    x: 420
                    y: 100
                        }
                FluentInfoBar {
                    id: testBar
                    theme: root.theme
                    Layout.fillWidth: true
                    Component.onCompleted: {
                        testBar.show("欢迎使用 MARS AI Agent", "success", 5000)
                    }
                }
            }
            Rectangle { color: theme.bgColor; Label { anchors.centerIn: parent; text: "会话"; color: theme.textColor } }
            Rectangle { color: theme.bgColor; Label { anchors.centerIn: parent; text: "工具"; color: theme.textColor } }
            Rectangle { color: theme.bgColor; Label { anchors.centerIn: parent; text: "设置"; color: theme.textColor } }
        }
    }

    
    
}