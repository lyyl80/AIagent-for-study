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
        Rectangle { anchors.centerIn: parent; width: size * 0.4; height: 2; color: iconColor; radius: 1; rotation: -45; anchors.horizontalCenterOffset: size * 0.1 }
        Rectangle { anchors.centerIn: parent; width: size * 0.4; height: 2; color: iconColor; radius: 1; rotation: 45; anchors.horizontalCenterOffset: size * 0.1 }
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

    // Hamburger Menu — 三条横线
    Column {
        anchors.centerIn: parent
        spacing: 3
        visible: iconName === "hamburger"
        Rectangle { width: size * 0.6; height: 2; color: iconColor; radius: 1 }
        Rectangle { width: size * 0.6; height: 2; color: iconColor; radius: 1 }
        Rectangle { width: size * 0.6; height: 2; color: iconColor; radius: 1 }
    }

    // Corner Right — 简约 > 箭头
    Item {
        anchors.centerIn: parent
        width: size; height: size
        visible: iconName === "corner-right"
        Rectangle {
            anchors.centerIn: parent
            width: size * 0.4; height: 2; color: iconColor; radius: 1
            rotation: -45; anchors.horizontalCenterOffset: size * 0.1
        }
        Rectangle {
            anchors.centerIn: parent
            width: size * 0.4; height: 2; color: iconColor; radius: 1
            rotation: 45; anchors.horizontalCenterOffset: size * 0.1
        }
    }

    // Refresh — 圆形箭头
    Item {
        anchors.centerIn: parent
        width: size; height: size
        visible: iconName === "refresh"
        Rectangle {
            anchors.centerIn: parent
            width: size * 0.6; height: size * 0.6; radius: size * 0.3
            color: "transparent"; border.color: iconColor; border.width: 2
        }
        Rectangle {
            anchors.top: parent.top; anchors.horizontalCenter: parent.horizontalCenter
            width: 2; height: size * 0.35; color: iconColor
            anchors.topMargin: size * 0.05
        }
        Rectangle {
            anchors.top: parent.top; anchors.horizontalCenter: parent.horizontalCenter
            width: 2; height: size * 0.22; color: iconColor; rotation: 45
            anchors.topMargin: size * 0.02
        }
    }
    
    // Chat (会话)
    Rectangle {
        anchors.centerIn: parent
        width: size * 0.6
        height: size * 0.6
        visible: iconName === "chat"
        
        color: "transparent"
        border.color: iconColor
        border.width: 2
        radius: width * 0.2
    }
    
    // Tools (工具)
    Rectangle {
        anchors.centerIn: parent
        width: size * 0.6
        height: size * 0.6
        visible: iconName === "tools"
        
        color: iconColor
        radius: width * 0.15
    }
    
    // Settings (设置)
    Item {
        anchors.centerIn: parent
        width: size
        height: size
        visible: iconName === "settings"
        
        Rectangle {
            anchors.centerIn: parent
            width: size * 0.5
            height: 2
            color: iconColor
        }
        
        Rectangle {
            anchors.centerIn: parent
            width: 2
            height: size * 0.5
            color: iconColor
        }
    }
}
