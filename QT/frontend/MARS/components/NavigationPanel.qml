import QtQuick 
import QtQuick.Layouts
import QtQuick.Controls
import MARS 1.0

/**
 * NavigationPanel - 导航面板组件
 * 提供左侧垂直导航栏，包含Logo、导航项和主题切换按钮
 */
Item {
    id: root
    
    // ====== 对外接口属性 ======
    property var theme: null              // 主题对象，由父级传入
    property int currentIndex: 0          // 当前选中的导航项索引
    signal itemClicked(int index)         // 导航项点击信号，传递被点击项的索引

    // ========= 导航项数据模型 =========
    readonly property var navItems: [
        { icon: "\u{1F3E0}", label: "对话" },  // 🏠 首页/对话
        { icon: "\u{1F527}", label: "工具" },  // 🔧 工具配置
        { icon: "\u{2699}", label: "设置" }    // ⚙ 系统设置
    ]

    // 根据主题动态设置宽度，默认68像素
    width: theme ? theme.navWidth : 68

    // 背景容器
    Rectangle {
        anchors.fill: parent
        color: root.theme ? root.theme.navBg : "#fafafa"

        // 垂直布局容器
        ColumnLayout{
            anchors.fill: parent
            spacing: 0
            
            // ========== 顶部 Logo 区域 ==========
            Item{
                Layout.preferredHeight: 60
                Layout.fillWidth: true
                
                // Logo 图标容器
                Rectangle 
                    {
                        anchors.centerIn: parent
                        width: 36
                        height: 36
                        radius: 8
                        color: root.theme ? root.theme.accentColor : "#f18cb9"
                        
                        // Logo 文字 "M"
                        Label {
                            anchors.centerIn: parent
                            text: "M"
                            color: "#ffffff"
                            font.bold: true
                            font.pixelSize: 18
                        }
                    }
            }

            // ========== 导航项列表（使用 Repeater 动态生成）==========
            Repeater {
                model: navItems           // 数据源
                delegate: navDelegate     // 代理组件
            }

            // 弹性占位符，将底部内容推到底部
            Item { Layout.fillHeight: true }

            // ========== 底部主题切换按钮 ==========
            Item {
                Layout.preferredHeight: 56
                Layout.fillWidth: true

                // 主题切换按钮容器
                Rectangle {
                    anchors.fill: parent
                    anchors.margins: 6
                    radius: 8
                    
                    // 悬停时显示背景色
                    color: root.theme && themeToggleArea.containsMouse
                           ? (root.theme ? root.theme.navHoverBg : "transparent")
                           : "transparent"

                    // 图标和文字垂直排列
                    Column {
                        anchors.centerIn: parent
                        spacing: 2

                        // 主题图标（太阳/月亮）
                        Label {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: root.theme && root.theme.darkMode ? "\u{2600}" : "\u{1F319}"  // ☀ / 🌙
                            font.pixelSize: 18
                        }
                        
                        // 主题文字说明
                        Label {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: root.theme && root.theme.darkMode ? "亮色" : "暗色"
                            font.pixelSize: 9
                            color: root.theme ? root.theme.secondaryText : "#888"
                        }
                    }

                    // 鼠标交互区域
                    MouseArea {
                        id: themeToggleArea
                        anchors.fill: parent
                        hoverEnabled: true                          // 启用悬停检测
                        cursorShape: Qt.PointingHandCursor          // 手型光标
                        
                        // 点击切换深色/浅色模式
                        onClicked: {
                            if (root.theme) root.theme.darkMode = !root.theme.darkMode
                        }
                    }
                }
            }
        }
        
        // 底部留白间距
        Item {
            Layout.preferredHeight: 12
        }
    }

    // ========= 导航项代理组件定义 =========
    Component {
        id: navDelegate

        Item {
            Layout.preferredHeight: 56
            Layout.fillWidth: true

            // 判断当前项是否处于激活状态
            property bool isActive: root.currentIndex === index
            property bool isHovered: false      // 鼠标悬停状态

            // 选中指示器（左侧竖条）
            Rectangle {
                x: 0
                width: 3
                height: 20
                radius: 1.5
                y: parent.height / 2 - height / 2
                visible: isActive               // 仅在激活时显示
                color: theme ? theme.navIndicator : "#f18cb9"
            }

            // 背景矩形
            Rectangle {
                anchors.fill: parent
                anchors.margins: 6
                radius: 8
                
                // 根据状态动态设置背景色
                color: {
                    if (isActive) return theme ? theme.navActiveBg : "#e8e8e8"   // 激活状态
                    if (isHovered) return theme ? theme.navHoverBg : "transparent"  // 悬停状态
                    return "transparent"                                         // 默认状态
                }
                
                // 颜色变化动画效果
                Behavior on color { ColorAnimation { duration: 150 } }
            }

            // 图标和文字垂直居中显示
            Column {
                anchors.centerIn: parent
                spacing: 2

                // 导航图标（Emoji）
                Label {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: modelData.icon
                    font.pixelSize: 20
                }
                
                // 导航文字标签
                Label {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: modelData.label
                    font.pixelSize: 9
                    
                    // 根据激活状态设置文字颜色
                    color: isActive
                           ? (theme ? theme.navActiveText : "#2d2d2d")
                           : (theme ? theme.navText : "#888")
                }
            }

            // 鼠标交互区域
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor  // 手型光标
                hoverEnabled: true                  // 启用悬停检测
                
                // 鼠标进入时更新悬停状态
                onEntered: isHovered = true
                
                // 鼠标离开时更新悬停状态
                onExited: isHovered = false
                
                // 点击处理：更新内部状态并发出信号
                onClicked: {
                    currentIndex = index            // 更新当前选中索引
                    itemClicked(index)              // 发出点击信号通知父组件
                }
            }
        }
    }
}