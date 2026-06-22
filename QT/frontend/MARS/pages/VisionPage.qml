import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0
import "../components"

/**
 * VisionPage — 视觉数据页面
 * 显示摄像头画面，带连接状态指示和目标计数徽章
 */
Rectangle {
    id: root

    property var theme: null

    color: theme ? theme.bgColor : "#F2F2F7"

    Rectangle {
        anchors.fill: parent
        anchors.margins: 12
        color: theme ? theme.cardColor : "#FFFFFF"
        radius: theme ? theme.cornerRadiusMd : 10
        border.color: theme ? theme.separatorColor : Qt.rgba(0,0,0,0.06)
        border.width: 1
        clip: true

        Image {
            id: cameraImage
            anchors.fill: parent
            anchors.margins: 1
            source: visionBridge ? "image://camera/feed?" + visionBridge.frameCount : ""
            fillMode: Image.PreserveAspectFit
            clip: true
            visible: visionBridge && visionBridge.connected
        }

        // 空状态
        Column {
            anchors.centerIn: parent
            spacing: 12
            visible: !cameraImage.visible || !(visionBridge && visionBridge.connected)

            Icon {
                iconName: "camera"
                iconColor: theme ? theme.tertiaryText : "#C7C7CC"
                size: 48
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Label {
                text: visionBridge && visionBridge.connected ? "等待视觉数据..." : "未连接 - 等待发送端..."
                font.pixelSize: theme ? theme.fontSizeBody : 13
                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                color: theme ? theme.secondaryText : "#8E8E93"
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        // 状态徽章（药丸形）
        Rectangle {
            id: statusBadge
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.margins: 16
            height: 28
            width: statusRow.width + 20
            radius: 14
            color: visionBridge && visionBridge.connected
                   ? Qt.rgba(0.204, 0.780, 0.349, 0.15)
                   : Qt.rgba(1.0, 0.231, 0.188, 0.15)

            Row {
                id: statusRow
                anchors.centerIn: parent
                spacing: 6

                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: 8
                    height: 8
                    radius: 4
                    color: visionBridge && visionBridge.connected ? "#30D059" : "#FF3B30"

                    // 呼吸动画
                    SequentialAnimation on opacity {
                        loops: Animation.Infinite
                        NumberAnimation { from: 1; to: 0.4; duration: 1500 }
                        NumberAnimation { from: 0.4; to: 1; duration: 1500 }
                    }
                }

                Label {
                    text: visionBridge && visionBridge.connected ? "已连接" : "断开"
                    font.pixelSize: theme ? theme.fontSizeCaption : 11
                    font.weight: theme ? theme.fontWeightSemibold : Font.DemiBold
                    font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                    color: visionBridge && visionBridge.connected ? "#24A040" : "#FF3B30"
                }
            }
        }

        // 目标计数徽章
        Rectangle {
            id: targetBadge
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 16
            height: 28
            width: targetRow.width + 20
            radius: 14
            visible: visionBridge && visionBridge.connected && visionBridge.targetCount > 0
            color: Qt.rgba(0.686, 0.322, 0.870, 0.15)   // Accent 15%

            Row {
                id: targetRow
                anchors.centerIn: parent
                spacing: 6

                Label {
                    text: "目标"
                    font.pixelSize: theme ? theme.fontSizeCaption : 11
                    font.weight: theme ? theme.fontWeightMedium : Font.Medium
                    font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                    color: theme ? theme.accentColor : "#AF52DE"
                    anchors.verticalCenter: parent.verticalCenter
                }

                Label {
                    text: (visionBridge ? visionBridge.targetCount : 0) + " 个"
                    font.pixelSize: theme ? theme.fontSizeCaption : 11
                    font.weight: theme ? theme.fontWeightSemibold : Font.DemiBold
                    font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                    color: theme ? theme.accentColor : "#AF52DE"
                }
            }
        }

        // FPS 徽章
        Rectangle {
            id: fpsBadge
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 16
            height: 24
            width: fpsLabel.width + 16
            radius: 12
            visible: visionBridge && visionBridge.connected
            color: Qt.rgba(0, 0, 0, 0.5)

            Label {
                id: fpsLabel
                anchors.centerIn: parent
                text: "30 FPS"
                font.pixelSize: 10
                font.weight: theme ? theme.fontWeightMedium : Font.Medium
                font.family: theme ? theme.defaultFontFamily : "SF Pro Display"
                color: "#FFFFFF"
            }
        }
    }
}
