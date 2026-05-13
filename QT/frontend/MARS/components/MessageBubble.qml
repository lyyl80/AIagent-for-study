import QtQuick
import QtQuick.Controls

/**
 * MessageBubble - 消息气泡组件
 * 支持用户/AI 消息显示，以及工具调用结果展示
 */
Rectangle {
    id: root

    // ====== 自定义属性 ======
    property var theme: null                    // 主题对象
    property string sender: "user"              // 发送者：user（用户）/ ai（AI）
    property string message: ""                 // 消息文本内容
    property string toolName: ""                // 工具名称（可选，为空时不显示工具卡片）
    property string toolResult: ""              // 工具执行结果（可选）

    width: parent ? parent.width : 0            // 宽度：跟随父容器
    implicitHeight: contentColumn.height + 24   // 高度：根据内容自动计算，上下留白 24px
    color: "transparent"                        // 背景透明

    // ====== 内容列容器 ======
    Column {
        id: contentColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 16                     // 左右边距 16px
        y: 12                                   // 垂直偏移 12px
        spacing: 4                              // 子元素间距 4px

        // ====== 消息气泡 ======
        Rectangle {
            id: bubble
            
            // 动态对齐：用户消息右对齐，AI 消息左对齐
            anchors.left: sender === "ai" ? parent.left : undefined
            anchors.right: sender === "user" ? parent.right : undefined
            
            // 宽度：根据文本长度自适应，最大不超过父容器的 75%
            width: Math.min(innerText.implicitWidth + 32, parent.width * 0.75)
            height: innerText.implicitHeight + 32  // 高度：文本高度 + 上下内边距 32px
            radius: 12                          // 圆角半径 12px
            
            // 背景色：用户消息使用强调色，AI 消息使用浅色背景
            color: sender === "user"
                   ? (theme ? theme.userBubbleBg : "#f18cb9")     // 用户：粉色
                   : (theme ? theme.aiBubbleBg : "#f0f0f0")       // AI：浅灰色

            // 消息文本
            Label {
                id: innerText
                anchors.fill: parent
                anchors.margins: 16             // 内边距 16px
                
                text: root.message              // 绑定消息内容
                color: sender === "user"
                       ? (theme ? theme.userBubbleText : "#fff")  // 用户：白色文字
                       : (theme ? theme.aiBubbleText : "#333")    // AI：深色文字
                font.pixelSize: 14              // 字体大小 14px
                wrapMode: Text.Wrap             // 自动换行
            }
        }

        // ====== 工具调用卡片（仅在有工具名时显示）======
        Rectangle {
            id: toolCard
            anchors.left: parent.left
            anchors.right: parent.right
            visible: root.toolName !== ""       // 仅在工具名非空时显示
            radius: 8                           // 圆角半径 8px
            color: theme ? theme.toolBubbleBg : "#fafafa"           // 背景色：浅灰
            border.color: theme ? theme.toolBubbleBorder : "#ddd"   // 边框颜色
            border.width: 1                     // 边框宽度 1px
            height: visible ? toolInner.height + 20 : 0  // 动态高度

            // 工具信息列
            Column {
                id: toolInner
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 10             // 内边距 10px
                spacing: 4                      // 子元素间距 4px

                // 工具名称（带扳手图标）
                Label {
                    text: "\u{1F527} " + root.toolName  // 🔧 工具名
                    font.pixelSize: 12          // 字体大小 12px
                    font.bold: true             // 粗体显示
                    color: theme ? theme.textColor : "#333"
                }
                
                // 工具执行结果
                Label {
                    text: root.toolResult
                    font.pixelSize: 11          // 字体大小 11px
                    color: theme ? theme.secondaryText : "#666"  // 次要文字颜色
                    wrapMode: Text.Wrap         // 自动换行
                    elide: Text.ElideRight      // 超出省略号
                    maximumLineCount: 3         // 最多显示 3 行
                }
            }
        }

        // ====== 发送者标签 ======
        Label {
            // 动态对齐：与气泡保持一致
            anchors.left: sender === "ai" ? bubble.left : undefined
            anchors.right: sender === "user" ? bubble.right : undefined
            
            text: sender === "user" ? "你" : "MARS"  // 用户显示"你"，AI 显示"MARS"
            font.pixelSize: 11                  // 字体大小 11px
            color: theme ? theme.secondaryText : "#999"  // 次要文字颜色
        }
    }
}