import QtQuick
import QtQuick.Controls

/**
 * FluentInfoBar - Fluent 风格信息提示条组件
 * 支持四种类型（info/success/warning/error），可自动或手动关闭
 */
Item{
    id: root

    // ====== 自定义属性 ======
    property var theme: null                    // 主题对象
    property string infoText: ""                // 提示文本内容
    property string infoType: "info"            // 提示类型：info / success / warning / error
    property int displayDuration: 3000          // 显示时长（毫秒），0 = 手动关闭

    visible : false                             // 默认隐藏
    height: visible ? 48 : 0                    // 可见时高度 48px，隐藏时 0px
    clip: true                                  // 裁剪超出边界的内容

    signal dismissed()                          // 关闭信号：通知父组件已关闭

    // 高度变化动画效果（200ms）
    Behavior on height { NumberAnimation { duration: 200 }}

    // ====== 背景矩形 ======
    Rectangle{
        anchors.fill : parent
        radius: 8                               // 圆角半径 8px
        
        // 根据类型动态设置背景色
        color: {
             switch (infoType) {
                case "success": return theme ? theme.successBg : "#4CAF50"   // 成功：绿色
                case "warning": return theme ? theme.warningBg : "#FF9800"   // 警告：橙色
                case "error":   return theme ? theme.errorBg : "#F44336"     // 错误：红色
                default:        return theme ? theme.infoBg : "#2196F3"      // 信息：蓝色（默认）
                }
            }
        
        // ====== 左侧图标和文字区域 ======
        Row{
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            spacing: 8                          // 图标与文字间距 8px
            
            // 类型图标（Unicode 符号）
            Label{
                anchors.verticalCenter: parent.verticalCenter
                text:{
                    switch (infoType) {
                        case "success": return "\u2713"   // ✓ 对勾
                        case "warning": return "\u26A0"   // ⚠ 警告
                        case "error":   return "\u2716"   // ✖ 叉号
                        default:        return "\u2139"   // ℹ 信息（默认）
                    }
                }
                font.pixelSize: 16              // 图标大小 16px
                color: "#ffffff"                // 白色图标
            }
            
            // 提示文本
            Label{
                anchors.verticalCenter: parent.verticalCenter
                text: infoText
                font.pixelSize: 13              // 字体大小 13px
                color: "#ffffff"                // 白色文字
            }
        }
        
        // ====== 右侧关闭按钮（仅手动关闭模式显示）======
        Label {
            anchors.right: parent.right
            anchors.rightMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            text: "\u2716"                      // ✖ 关闭图标
            color: "#ffffff"
            font.pixelSize: 14
            visible: displayDuration === 0      // 仅在手动关闭模式显示

            MouseArea {
                anchors.fill: parent
                onClicked: dismiss()            // 点击调用关闭函数
            }
        }
    }
    
    // ====== 公共方法 ======
    
    /**
     * 显示信息提示条
     * @param text - 提示文本内容
     * @param type - 提示类型（info/success/warning/error）
     * @param duration - 显示时长（毫秒），0 表示手动关闭
     */
    function show(text , type ,duration) {
        infoText = text                         // 设置提示文本
        infoType = type || "info"               // 设置类型，默认 info
        displayDuration = duration || 3000      // 设置时长，默认 3000ms
        visible = true                          // 显示提示条

        // 如果设置了自动关闭时长，启动定时器
        if(displayDuration > 0){
            hideTimer.interval = displayDuration
            hideTimer.start()
        }
    }
    
    /**
     * 手动关闭信息提示条
     */
    function dismiss() {
        hideTimer.stop()                        // 停止定时器
        root.visible = false                    // 隐藏提示条
        dismissed()                             // 发出关闭信号
    }
    
    // ====== 自动关闭定时器 ======
    Timer{
        id: hideTimer
        onTriggered: dismiss()                  // 定时到达后自动关闭
    }
}