import QtQuick
import QtQuick.Controls

/**
 * FluentCard - Fluent 风格卡片组件
 * 提供带阴影效果的容器，支持标题和自定义内容区域
 */
Item {
    id: root

    // ====== 自定义属性 ======
    property alias cardTitle: titleLabel.text  // 卡片标题（直接绑定到内部 Label）
    property bool elevated: true               // 是否显示阴影效果
    property var theme: null                   // 主题对象

    default property alias content: contentArea.data  // 默认属性：允许子元素直接添加到内容区

    // ====== 阴影层（位于卡片表面下方，偏移 2px）======
    Rectangle {
        id: shadowRect
        anchors.fill: cardSurface                    // 填充卡片表面
        anchors.topMargin: 2                         // 向下偏移 2px
        anchors.leftMargin: 2                        // 向右偏移 2px
        radius: cardSurface.radius                   // 与卡片相同的圆角
        visible: elevated                            // 仅在启用阴影时显示
        
        // 阴影颜色：深色模式更透明，浅色模式更深
        color: theme && theme.darkMode
               ? Qt.rgba(0, 0, 0, 0.3)               // 深色模式：30% 透明度黑色
               : Qt.rgba(0, 0, 0, 0.1)               // 浅色模式：10% 透明度黑色
    }

    // ====== 卡片表面 ======
    Rectangle {
        id: cardSurface
        anchors.fill: parent                         // 填充整个组件
        radius: theme ? theme.cardRadius : 8         // 圆角半径：优先使用主题设置，默认 8px
        color: theme ? theme.cardColor : "#ffffff"   // 背景色：优先使用主题设置，默认白色

        // ====== 标题区域 ======
        Label {
            id: titleLabel
            visible: text !== ""                     // 仅在有标题文本时显示
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 16                      // 内边距 16px
            
            font.pixelSize: 14                       // 字体大小 14px
            font.bold: true                          // 粗体显示
            font.family: theme ? theme.defaultFontFamily : "Segoe UI"
            color: theme ? theme.textColor : "#333"  // 文字颜色：优先使用主题设置
            antialiasing: true
        }

        // ====== 内容区域（留给调用方填充）======
        Item {
            id: contentArea
            // 动态定位：如果标题可见则在标题下方，否则在顶部
            anchors.top: titleLabel.visible ? titleLabel.bottom : parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.topMargin: titleLabel.visible ? 16 : 0  // 有标题时上边距 16px
        }
    }
}