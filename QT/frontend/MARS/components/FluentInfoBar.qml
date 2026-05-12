import QtQuick
import QtQuick.Controls

Item{
    id: root

    property var theme: null
    property string infoText: ""
    property string infoType: "info" //info / success /warning /error
    property int displayDuration: 3000 //ms , 0 = 手动关闭

    visible : false
    height: visible ? 48 : 0
    clip: true

    signal dismissed()

    Behavior on height { NumberAnimation { duration: 200 }}

    Rectangle{
        anchors.fill : parent
        radius: 8
        color: {
             switch (infoType) {
                case "success": return theme ? theme.successBg : "#4CAF50"
                case "warning": return theme ? theme.warningBg : "#FF9800"
                case "error":   return theme ? theme.errorBg : "#F44336"
                default:        return theme ? theme.infoBg : "#2196F3"
                }
            }
        Row{
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            spacing: 8
            Label{
                anchors.verticalCenter: parent.verticalCenter
                text:{
                    switch (infoType) {
                        case "success": return "\u2713"   // ✓
                        case "warning": return "\u26A0"   // ⚠
                        case "error":   return "\u2716"   // ✖
                        default:        return "\u2139"   // ℹ
                    }
                }
                font.pixelSize: 16
                color: "#ffffff"
            }
            Label{
                anchors.verticalCenter: parent.verticalCenter
                text: infoText
                font.pixelSize: 13
                color: "#ffffff"

            }
        }
          Label {
            anchors.right: parent.right
            anchors.rightMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            text: "\u2716"
            color: "#ffffff"
            font.pixelSize: 14
            visible: displayDuration === 0

            MouseArea {
                anchors.fill: parent
                onClicked: dismiss()
            }
        }
    }
    function show(text , type ,duration) {
        infoText = text
        infoType = type || "info"
        displayDuration = duration || 3000
        visible = true

        if(displayDuration > 0){
            hideTimer.interval = displayDuration
            hideTimer.start()
        }
        
    }
    function dismiss() {
        hideTimer.stop()
        root.visible = false
        dismissed()
    }
    Timer{
        id: hideTimer
        onTriggered: dismiss()
    }
  
}







