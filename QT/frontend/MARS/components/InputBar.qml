import QtQuick
import QtQuick.Controls

/**
 * InputBar - 输入栏组件
 * 提供文本输入框和发送按钮，支持 Enter 发送、Shift+Enter 换行
 */
Rectangle {
    id: root

    // ====== 自定义属性 ======
    property var theme: null                    // 主题对象
    property bool isThinking: false             // AI 思考状态（禁用输入）
    signal sendMessage(string text)             // 发送消息信号：传递用户输入的文本

    height: theme ? theme.inputBarHeight : 56   // 高度：优先使用主题设置，默认 56px
    width: parent ? parent.width : 0            // 宽度：跟随父容器
    color: theme ? theme.cardColor : "#ffffff"  // 背景色：优先使用主题设置，默认白色

    // ====== 顶部分割线 ======
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1                               // 分割线高度 1px
        color: theme ? theme.dividerColor : "#ddd"  // 颜色：优先使用主题设置
    }

    // ====== 文本输入区域 ======
    TextArea {
        id: inputField
        anchors.fill: parent
        anchors.margins: 8                      // 内边距 8px
        
        placeholderText: root.isThinking ? "AI 正在思考，请稍等..." : "输入消息,Enter to send"  // 占位提示文本
        placeholderTextColor: theme ? theme.secondaryText: "#999"  // 占位符颜色
        color: theme ? theme.textColor : "#333" // 文字颜色
        font.pixelSize: 14                      // 字体大小 14px
        enabled: !root.isThinking               // AI 思考时禁用输入
        wrapMode: Text.Wrap                     // 自动换行

        // ====== 键盘事件处理 ======
        Keys.onPressed: function(event) {
            // Enter 键且未按下 Shift：发送消息
            if (event.key === Qt.Key_Return && !(event.modifiers & Qt.ShiftModifier)) {
                 event.accepted = true          // 标记事件已处理
                 doSend()                       // 调用发送函数
            }
            // Shift+Enter：保留默认换行行为
        }
    }

    // ====== 发送按钮 ======
    Button {
        id: sendBtn
        anchors.verticalCenter: parent.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: 8                  // 右边距 8px
        width: 40                               // 按钮宽度 40px
        height: 40                              // 按钮高度 40px
        enabled: !root.isThinking               // AI 思考时禁用按钮

        // 按钮背景
        background: Rectangle {
            radius: 8                           // 圆角半径 8px
            
            // 动态颜色：根据启用/悬停/按下状态变化
            color: parent.enabled
                   ? (parent.hovered
                      ? Qt.lighter(theme ? theme.accentColor : "#f18cb9", 1.1)  // 悬停时提亮 10%
                      : (theme ? theme.accentColor : "#f18cb9"))                // 默认强调色
                   : (theme ? theme.dividerColor : "#ccc")                      // 禁用时灰色
            Behavior on color { ColorAnimation { duration: 100 } }  // 颜色变化动画（100ms）
        }

        // 按钮内容（图标）
        contentItem: Item {
            Label {
                anchors.centerIn: parent
                text: root.isThinking ? "\u23F3" : "\u25B6"  // ⏳ 沙漏（思考中）/ ▶ 播放（可发送）
                color: "#ffffff"                // 白色图标
                font.pixelSize: 18              // 图标大小 18px
            }
        }

        onClicked: doSend()                     // 点击调用发送函数
    }

    // ====== 发送消息处理函数 ======
    function doSend() {
        var text = inputField.text.trim()       // 获取并去除首尾空格
        if(text === "") return                  // 空文本不发送
        
        sendMessage(text)                       // 发出发送信号
        inputField.text = ""                    // 清空输入框
    }
}