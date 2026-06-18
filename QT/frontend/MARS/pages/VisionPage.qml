import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0
import "../components"

Rectangle {
    id: root

    property var theme: null

    color: theme ? theme.bgColor : "#1b1b1b"

    Rectangle {
        anchors.fill: parent
        color: theme ? theme.cardColor : "#2d2d2d"
        radius: theme ? theme.cardRadius : 12

        Image {
            id: cameraImage
            anchors.fill: parent
            anchors.margins: 4
            source: "image://camera/feed?" + visionBridge.frameCount
            fillMode: Image.PreserveAspectFit
            clip: true
            visible: visionBridge.connected
        }

        Label {
            anchors.centerIn: parent
            text: visionBridge.connected ? "等待视觉数据..." : "未连接 - 等待发送端..."
            font.pixelSize: 18
            color: theme ? theme.secondaryText : "#606060"
            visible: !cameraImage.visible || !visionBridge.connected
        }

        Rectangle {
            id: statusBadge
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.margins: 12
            height: 28
            width: statusRow.width + 16
            radius: 14
            color: visionBridge.connected
                   ? (theme && theme.darkMode ? "#4400cc00" : "#cc00cc00")
                   : (theme && theme.darkMode ? "#44cc0000" : "#cccc0000")

            Row {
                id: statusRow
                anchors.centerIn: parent
                spacing: 6

                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: 8
                    height: 8
                    radius: 4
                    color: visionBridge.connected ? "#00cc00" : "#cc0000"
                }

                Label {
                    text: visionBridge.connected ? "已连接" : "断开"
                    font.pixelSize: 11
                    font.bold: true
                    color: "#ffffff"
                }
            }
        }

        Rectangle {
            id: targetBadge
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 12
            height: 28
            width: targetRow.width + 16
            radius: 14
            visible: visionBridge.connected && visionBridge.targetCount > 0
            color: theme && theme.darkMode ? "#447c3aed" : "#cc7c3aed"

            Row {
                id: targetRow
                anchors.centerIn: parent
                spacing: 6

                Label {
                    text: "目标:"
                    font.pixelSize: 11
                    font.bold: true
                    color: "#ffffff"
                    anchors.verticalCenter: parent.verticalCenter
                }

                Label {
                    text: visionBridge.targetCount + " 个目标"
                    font.pixelSize: 11
                    font.bold: true
                    color: "#ffffff"
                }
            }
        }

        Rectangle {
            id: fpsBadge
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 12
            height: 24
            width: fpsLabel.width + 12
            radius: 12
            visible: visionBridge.connected
            color: theme && theme.darkMode ? "#44000000" : "#cc000000"

            Label {
                id: fpsLabel
                anchors.centerIn: parent
                text: "30 FPS"
                font.pixelSize: 10
                color: "#ffffff"
            }
        }
    }
}
