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
    
    // Plus
    Item {
        anchors.centerIn: parent
        width: size
        height: size
        visible: iconName === "plus" || iconName === "plus-outline"
        
        Rectangle {
            anchors.centerIn: parent
            width: iconName === "plus" ? size * 0.6 : size * 0.7
            height: 2
            color: iconName === "plus" ? iconColor : "transparent"
            border.color: iconName === "plus-outline" ? iconColor : "transparent"
            border.width: iconName === "plus-outline" ? 2 : 0
        }
        
        Rectangle {
            anchors.centerIn: parent
            width: 2
            height: iconName === "plus" ? size * 0.6 : size * 0.7
            color: iconName === "plus" ? iconColor : "transparent"
            border.color: iconName === "plus-outline" ? iconColor : "transparent"
            border.width: iconName === "plus-outline" ? 2 : 0
        }
    }
    
    // Minus
    Rectangle {
        anchors.centerIn: parent
        width: size * 0.6
        height: 2
        color: iconColor
        visible: iconName === "minus"
    }
    
    // Line
    Rectangle {
        anchors.centerIn: parent
        width: size * 0.7
        height: 3
        color: iconColor
        visible: iconName === "line"
    }
    
    // Cross
    Item {
        anchors.centerIn: parent
        width: size
        height: size
        visible: iconName === "cross"
        
        Rectangle {
            anchors.centerIn: parent
            width: size * 0.6
            height: 2
            color: iconColor
            rotation: 45
        }
        
        Rectangle {
            anchors.centerIn: parent
            width: size * 0.6
            height: 2
            color: iconColor
            rotation: -45
        }
    }
    
    // Arrow Right
    Item {
        anchors.centerIn: parent
        width: size
        height: size
        visible: iconName === "arrow-right"
        
        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: size * 0.15
            width: size * 0.5
            height: 3
            color: iconColor
        }
        
        // Arrow head top
        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: size * 0.15
            width: size * 0.25
            height: 3
            color: iconColor
            rotation: -45
            anchors.topMargin: -size * 0.08
        }
        
        // Arrow head bottom
        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: size * 0.15
            width: size * 0.25
            height: 3
            color: iconColor
            rotation: 45
            anchors.bottomMargin: -size * 0.08
        }
    }
    
    // Arrow Up
    Item {
        anchors.centerIn: parent
        width: size
        height: size
        visible: iconName === "arrow-up"
        
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: size * 0.15
            width: 3
            height: size * 0.5
            color: iconColor
        }
        
        // Arrow head left
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: size * 0.15
            width: 3
            height: size * 0.25
            color: iconColor
            rotation: 45
            anchors.leftMargin: -size * 0.08
        }
        
        // Arrow head right
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: size * 0.15
            width: 3
            height: size * 0.25
            color: iconColor
            rotation: -45
            anchors.rightMargin: -size * 0.08
        }
    }
    
    // Arrow Left
    Item {
        anchors.centerIn: parent
        width: size
        height: size
        visible: iconName === "arrow-left"
        
        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: size * 0.15
            width: size * 0.5
            height: 2
            color: iconColor
        }
        
        // Arrow head using Rectangle
        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: size * 0.1
            width: size * 0.15
            height: size * 0.25
            color: iconColor
            rotation: -45
        }
    }
    
    // Hamburger Menu
    Column {
        anchors.centerIn: parent
        spacing: 4
        visible: iconName === "hamburger"
        
        Rectangle {
            width: size * 0.7
            height: 2
            color: iconColor
        }
        Rectangle {
            width: size * 0.7
            height: 2
            color: iconColor
        }
        Rectangle {
            width: size * 0.7
            height: 2
            color: iconColor
        }
    }
    
    // Corner Right
    Item {
        anchors.centerIn: parent
        width: size
        height: size
        visible: iconName === "corner-right"
        
        Rectangle {
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.leftMargin: size * 0.2
            width: 2
            height: size * 0.5
            color: iconColor
        }
        
        Rectangle {
            anchors.bottom: parent.bottom
            anchors.bottomMargin: size * 0.25
            anchors.left: parent.left
            width: size * 0.5
            height: 2
            color: iconColor
        }
        
        // Corner arrow
        Rectangle {
            anchors.bottom: parent.bottom
            anchors.bottomMargin: size * 0.25
            anchors.left: parent.left
            anchors.leftMargin: size * 0.5
            width: size * 0.15
            height: size * 0.15
            color: iconColor
            rotation: -45
        }
    }
    
    // Refresh
    Item {
        anchors.centerIn: parent
        width: size
        height: size
        visible: iconName === "refresh"
        
        Rectangle {
            anchors.fill: parent
            color: "transparent"
            border.color: iconColor
            border.width: 2
            radius: width / 2
        }
        
        Rectangle {
            anchors.top: parent.top
            anchors.left: parent.left
            width: size * 0.15
            height: 2
            color: iconColor
            rotation: -45
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
