import QtQuick
import QtQuick.Controls
import MARS 1.0

/**
 * TypingIndicator — Apple Messages 风格打字指示器
 * 三个交替缩放的圆点，表示 AI 正在思考
 */
Rectangle {
    id: root

    property var theme: null

    width: 48
    height: 32
    radius: 16
    color: theme ? theme.aiBubbleBg : "#FFFFFF"
    border.color: theme ? theme.aiBubbleBorder : Qt.rgba(0,0,0,0.08)
    border.width: 1

    Row {
        anchors.centerIn: parent
        spacing: 6

        Repeater {
            model: 3

            Rectangle {
                id: dot
                width: 8
                height: 8
                radius: 4
                color: theme ? theme.secondaryText : "#8E8E93"

                // 交替缩放动画
                SequentialAnimation on scale {
                    loops: Animation.Infinite

                    PauseAnimation { duration: index * 120 }

                    NumberAnimation {
                        target: dot
                        property: "scale"
                        from: 0.6
                        to: 1.0
                        duration: 300
                        easing.type: Easing.OutQuart
                    }

                    NumberAnimation {
                        target: dot
                        property: "scale"
                        from: 1.0
                        to: 0.6
                        duration: 300
                        easing.type: Easing.InQuart
                    }

                    PauseAnimation { duration: (2 - index) * 120 }
                }

                // 透明度同步动画
                opacity: scale
            }
        }
    }
}
