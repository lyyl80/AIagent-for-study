import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Rectangle{
    id: root

    property var theme: null
    property bool collapsed: false
    property var sessionList: []

    signal loadRequested(string filename)
    signal deleteRequested(string filename)
    signal newSessionRequested()
    signal refreshRequested()

    color: theme ? theme.cardColor : "#fff"
    clip: true


    ColumnLayout {
        anchors.fill: parent
        anchors.topMargin: 0
        spacing: 0

        // 标题栏
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 48
            color: "transparent"

            Rectangle {
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: 1
                color: theme ? theme.dividerColor : "#ddd"
            }

            Label {
                anchors.left: parent.left
                anchors.leftMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                text: "\u{1F4C2} 会话"
                font.pixelSize: 14
                font.bold: true
                color: theme ? theme.textColor : "#333"
            }

            Button {
                anchors.right: parent.right
                anchors.rightMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                text: "\u{27F2}"  // ⟲
                flat: true
                onClicked: root.refreshRequested()
                background: Rectangle {
                    radius: 4
                    color: parent.hovered ? (theme ? theme.navHoverBg : "#eee") : "transparent"
                }
                contentItem: Label {
                    anchors.centerIn: parent
                    text: parent.text
                    font.pixelSize: 14
                    color: theme ? theme.textColor : "#333"
                }
            }
        }

        // 会话列表
        ListView {
            id: sessionListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.leftMargin: 8
            Layout.rightMargin: 8
            Layout.topMargin: 8
            model: root.sessionList
            spacing: 4
            clip: true

            // 空状态提示
            Label {
                anchors.centerIn: parent
                text: "暂无会话"
                font.pixelSize: 13
                color: theme ? theme.secondaryText : "#999"
                visible: sessionListView.count === 0
            }

            delegate: Rectangle {
                width: sessionListView.width - 16
                height: 48
                radius: 6
                color: mouseArea.containsMouse
                       ? (theme ? theme.navHoverBg : "#eee")
                       : "transparent"

                Column {
                    anchors.left: parent.left
                    anchors.leftMargin: 12
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 2

                    Label {
                        text: modelData.filename || "(无标题)"
                        font.pixelSize: 12
                        font.bold: true
                        color: theme ? theme.textColor : "#333"
                        elide: Text.ElideRight
                        width: parent.parent.width - 60
                    }
                    Label {
                        text: (modelData.created_time || "").substring(0, 16)
                        font.pixelSize: 10
                        color: theme ? theme.secondaryText : "#999"
                    }
                }

                Button {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.rightMargin: 4
                    text: "\u{2716}"  // ✖
                    flat: true
                    visible: mouseArea.containsMouse
                    onClicked: root.deleteRequested(modelData.filename)
                    background: Rectangle {
                        radius: 4
                        color: parent.hovered ? "#ff444422" : "transparent"
                    }
                    contentItem: Label {
                        anchors.centerIn: parent
                        text: parent.text
                        font.pixelSize: 10
                        color: "#ff4444"
                    }
                }

                MouseArea {
                    id: mouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.loadRequested(modelData.filename)
                }
            }

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
                width: 4
                contentItem: Rectangle { radius: 2; color: theme ? theme.dividerColor : "#ccc" }
            }
        }

        // 新建会话按钮
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 44
            Layout.leftMargin: 8
            Layout.rightMargin: 8
            Layout.bottomMargin: 8
            radius: 6
            color: theme ? theme.accentColor : "#f18cb9"

            Label {
                anchors.centerIn: parent
                text: "\u{2795} 新建会话"
                color: "#fff"
                font.pixelSize: 13
                font.bold: true
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: root.newSessionRequested()
            }
        }
    }
}