import QtQuick

Item {
    id: root
    
    property string iconName: "circle"
    property color iconColor: "#ffffff"
    property real size: 24
    
    width: size
    height: size
    
    // Circle (filled)
    Rectangle {
        anchors.centerIn: parent
        width: size * 0.66
        height: size * 0.66
        radius: width / 2
        color: iconColor
        visible: iconName === "circle"
    }
    
    // Circle Outline
    Rectangle {
        anchors.centerIn: parent
        width: size * 0.66
        height: size * 0.66
        radius: width / 2
        color: "transparent"
        border.color: iconColor
        border.width: 2
        visible: iconName === "circle-outline"
    }
    
    // Square (filled)
    Rectangle {
        anchors.centerIn: parent
        width: size * 0.66
        height: size * 0.66
        radius: 2
        color: iconColor
        visible: iconName === "square"
    }
    
    // Square Outline
    Rectangle {
        anchors.centerIn: parent
        width: size * 0.66
        height: size * 0.66
        radius: 2
        color: "transparent"
        border.color: iconColor
        border.width: 2
        visible: iconName === "square-outline"
    }
    
    // Plus — 简约 + 号
    Item {
        anchors.centerIn: parent
        width: size; height: size
        visible: iconName === "plus"
        Rectangle { anchors.centerIn: parent; width: size * 0.5; height: 2; color: iconColor; radius: 1 }
        Rectangle { anchors.centerIn: parent; width: 2; height: size * 0.5; color: iconColor; radius: 1 }
    }

    // Minus — 简约 - 号
    Rectangle { anchors.centerIn: parent; width: size * 0.5; height: 2; color: iconColor; radius: 1; visible: iconName === "minus" }

    // Line
    Rectangle { anchors.centerIn: parent; width: size * 0.5; height: 2; color: iconColor; radius: 1; visible: iconName === "line" }

    // Cross — 简约 ×
    Item {
        anchors.centerIn: parent; width: size; height: size
        visible: iconName === "cross"
        Rectangle { anchors.centerIn: parent; width: size * 0.5; height: 2; color: iconColor; radius: 1; rotation: 45 }
        Rectangle { anchors.centerIn: parent; width: size * 0.5; height: 2; color: iconColor; radius: 1; rotation: -45 }
    }
    
    // Arrow Right — 简约 >
    Item {
        anchors.centerIn: parent; width: size; height: size
        visible: iconName === "arrow-right"
        Rectangle {
            anchors.centerIn: parent
            width: size * 0.45; height: size * 0.28; radius: size * 0.04
            color: iconColor; rotation: -45
            anchors.horizontalCenterOffset: size * 0.06
        }
        Rectangle {
            anchors.centerIn: parent
            width: size * 0.45; height: size * 0.28; radius: size * 0.04
            color: iconColor; rotation: 45
            anchors.horizontalCenterOffset: size * 0.06
        }
    }

    // Arrow Up — 简约 ^
    Item {
        anchors.centerIn: parent; width: size; height: size
        visible: iconName === "arrow-up"
        Rectangle { anchors.centerIn: parent; width: size * 0.4; height: 2; color: iconColor; radius: 1; rotation: 45; anchors.verticalCenterOffset: size * 0.1 }
        Rectangle { anchors.centerIn: parent; width: size * 0.4; height: 2; color: iconColor; radius: 1; rotation: -45; anchors.verticalCenterOffset: size * 0.1 }
    }

    // Arrow Left — 简约 <
    Item {
        anchors.centerIn: parent; width: size; height: size
        visible: iconName === "arrow-left"
        Rectangle { anchors.centerIn: parent; width: size * 0.4; height: 2; color: iconColor; radius: 1; rotation: 45; anchors.horizontalCenterOffset: -size * 0.1 }
        Rectangle { anchors.centerIn: parent; width: size * 0.4; height: 2; color: iconColor; radius: 1; rotation: -45; anchors.horizontalCenterOffset: -size * 0.1 }
    }

    // Hamburger Menu — 简约菜单
    Column {
        anchors.centerIn: parent
        spacing: 3
        visible: iconName === "hamburger"
        Rectangle { width: size * 0.55; height: 2; color: iconColor; radius: 1 }
        Rectangle { width: size * 0.55; height: 2; color: iconColor; radius: 1 }
        Rectangle { width: size * 0.55; height: 2; color: iconColor; radius: 1 }
    }

    // Corner Right — 会话列表 (三条递减横线)
    Item {
        anchors.centerIn: parent; width: size; height: size
        visible: iconName === "corner-right"
        Column {
            anchors.centerIn: parent; spacing: 3
            Rectangle { width: size * 0.6; height: 2; color: iconColor; radius: 1 }
            Rectangle { width: size * 0.45; height: 2; color: iconColor; radius: 1 }
            Rectangle { width: size * 0.3; height: 2; color: iconColor; radius: 1 }
        }
    }

    // Refresh — 循环箭头
    Item {
        anchors.centerIn: parent; width: size; height: size
        visible: iconName === "refresh"
        Rectangle {
            anchors.centerIn: parent
            width: size * 0.65; height: size * 0.65; radius: size * 0.325
            color: "transparent"; border.color: iconColor; border.width: 2
        }
        Rectangle {
            anchors.top: parent.top; anchors.right: parent.right
            width: 2; height: size * 0.32; color: iconColor
            anchors.topMargin: size * 0.04; anchors.rightMargin: size * 0.02
            rotation: -45
        }
    }
    
    // Chat (会话) — 简约对话气泡
    Item {
        anchors.centerIn: parent; width: size * 0.7; height: size * 0.6
        visible: iconName === "chat"
        Rectangle { anchors.fill: parent; radius: width * 0.25; color: "transparent"; border.color: iconColor; border.width: 2 }
        Rectangle { anchors.bottom: parent.bottom; anchors.left: parent.left; width: size * 0.15; height: 2; color: iconColor; rotation: -45; anchors.leftMargin: size * 0.05 }
    }

    // Tools (工具) — 简约网格
    Column {
        anchors.centerIn: parent; spacing: size * 0.12
        visible: iconName === "tools"
        Row { spacing: size * 0.12; Rectangle { width: size * 0.2; height: size * 0.2; radius: size * 0.05; color: iconColor } Rectangle { width: size * 0.2; height: size * 0.2; radius: size * 0.05; color: iconColor } }
        Row { spacing: size * 0.12; Rectangle { width: size * 0.2; height: size * 0.2; radius: size * 0.05; color: iconColor } Rectangle { width: size * 0.2; height: size * 0.2; radius: size * 0.05; color: iconColor } }
    }

    // Tools Outline (工具轮廓) — 缺右上、左下的八边形
    Item {
        anchors.centerIn: parent; width: size; height: size
        visible: iconName === "tools-outline"
        Rectangle { x: size * 0.22; y: 0; width: size * 0.56; height: size * 0.09; color: iconColor; radius: 1 }
        Rectangle { x: size * 0.22; y: size * 0.91; width: size * 0.56; height: size * 0.09; color: iconColor; radius: 1 }
        Rectangle { x: 0; y: size * 0.22; width: size * 0.09; height: size * 0.56; color: iconColor; radius: 1 }
        Rectangle { x: size * 0.91; y: size * 0.22; width: size * 0.09; height: size * 0.56; color: iconColor; radius: 1 }
        Rectangle {
            x: size * 0.01; y: size * 0.01
            width: size * 0.33; height: size * 0.09
            rotation: 45; color: iconColor; radius: 1
        }
        Rectangle {
            x: size * 0.66; y: size * 0.66
            width: size * 0.33; height: size * 0.09
            rotation: 45; color: iconColor; radius: 1
        }
    }

    // Settings (设置) — 简约齿轮
    Item {
        anchors.centerIn: parent; width: size; height: size
        visible: iconName === "settings"
        Rectangle { anchors.centerIn: parent; width: size * 0.44; height: size * 0.44; radius: size * 0.22; color: "transparent"; border.color: iconColor; border.width: 2 }
        Rectangle { anchors.centerIn: parent; width: size * 0.18; height: size * 0.18; radius: size * 0.09; color: iconColor }
        Rectangle { anchors.centerIn: parent; width: 2; height: size * 0.7; color: iconColor; rotation: 0 }
        Rectangle { anchors.centerIn: parent; width: 2; height: size * 0.7; color: iconColor; rotation: 45 }
        Rectangle { anchors.centerIn: parent; width: 2; height: size * 0.7; color: iconColor; rotation: -45 }
        Rectangle { anchors.centerIn: parent; width: 2; height: size * 0.7; color: iconColor; rotation: 90 }
    }
}
