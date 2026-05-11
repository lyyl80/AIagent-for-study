# MARS AI Agent — QML 桌面客户端通关教程

> **目标**：从零开始，为 MARS 打造一个媲美 MRobot 质量级的 PySide6 QML 桌面客户端。
> **风格**：过关斩将，每一关都有明确的 Boss（目标）、技能点（知识）、装备（代码）、验收标准。
> **前置**：已成功运行 `python main.py`（CLI 模式）、已安装 `pip install -r requirements.txt`。

---

## 目录

1. [第零关：铸剑——环境准备](#第零关铸剑环境准备)
2. [第一关：开天辟地——QML 引擎跑通](#第一关开天辟地qml-引擎跑通)
3. [第二关：定海神针——全局主题系统](#第二关定海神针全局主题系统)
4. [第三关：龙门——导航面板](#第三关龙门导航面板)
5. [第四关：基石——UI 组件库](#第四关基石ui-组件库)
6. [第五关：初试锋芒——聊天页面布局](#第五关初试锋芒聊天页面布局)
7. [第六关：灵犀一指——Python ↔ QML 桥接](#第六关灵犀一指python--qml-桥接)
8. [第七关：内功心法——LLM 工作线程](#第七关内功心法llm-工作线程)
9. [第八关：百家争鸣——完整功能页](#第八关百家争鸣完整功能页)
10. [第九关：画龙点睛——动画与打磨](#第九关画龙点睛动画与打磨)
11. [最终 BOSS：自测清单](#最终-boss自测清单)

---

## 第零关：铸剑——环境准备

### Boss

安装 PySide6，验证 QML 引擎可用。

### 技能点

- `PySide6` 是 Qt6 的 Python 绑定，包含 `QML` 引擎
- `QtQuick.Controls` 是 QML 的标准控件库，版本 6.x
- `qmllint` / `qmlformat` 可选但推荐装

### 装备

```bash
pip install PySide6
```

验证：

```bash
python -c "from PySide6.QtQml import QQmlApplicationEngine; from PySide6.QtGui import QGuiApplication; print('OK')"
```

### 验收

控制台输出 `OK`。

### 顺便做：整理目录

确保 `QT/` 下结构如下（删除旧的空占位文件，新建目录）：

```
QT/
├── main.py                 # 我们一关一关写
├── backend/
│   ├── __init__.py
│   ├── chat_bridge.py      # 第六关写
│   ├── session_model.py    # 第八关写
│   └── worker.py           # 第七关写
├── frontend/
│   └── MARS/               # MARS QML 模块（qmldir 声明）
│       ├── qmldir              # 模块定义文件
│       ├── main.qml            # 第一关写
│       ├── FluentTheme.qml     # 第二关写
│       ├── components/
│       │   ├── NavigationPanel.qml  # 第三关写
│       │   ├── FluentCard.qml       # 第四关写
│       │   ├── FluentButton.qml     # 第四关写
│       │   ├── FluentInfoBar.qml    # 第四关写
│       │   ├── MessageBubble.qml    # 第五关写
│       │   └── InputBar.qml         # 第五关写
│       └── pages/
│           ├── ChatPage.qml         # 第五关写
│           ├── SessionsPage.qml     # 第八关写
│           ├── ToolsPage.qml        # 第八关写
│           └── SettingsPage.qml     # 第八关写
├── resources/
│   └── icons/                   # SVG 图标，可以先用 unicode 占位
└── QML_TUTORIAL.md          # ← 你现在看的这个（删掉也行）
```

```bash
# Windows PowerShell 执行
Remove-Item -LiteralPath "QT/Frontend" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "QT/backend", "QT/frontend/components", "QT/frontend/pages", "QT/resources/icons" -Force
New-Item -ItemType File -Path "QT/backend/__init__.py" -Force | Out-Null
```

---

## 第一关：开天辟地——QML 引擎跑通

### Boss

屏幕上出现一个空白窗口，标题 "MARS AI Agent"。

### 技能点

- `QGuiApplication` — Qt GUI 应用的必要对象
- `QQmlApplicationEngine` — 加载并运行 QML 文件
- QML `Window` 类型是最外层容器

### 装备

写入 `QT/main.py`：

```python
import sys
import os

# 强制将项目根目录加入 sys.path，让 core/ 可以被 import
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    app.setApplicationName("MARS AI Agent")
    app.setOrganizationName("MARS")

    engine = QQmlApplicationEngine()
    engine.load(os.path.join(os.path.dirname(__file__), "frontend", "main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
```

写入 `QT/frontend/main.qml`：

```qml
import QtQuick
import QtQuick.Controls

Window {
    width: 960
    height: 640
    visible: true
    title: "MARS AI Agent"

    // 先放个标签确认 QML 跑通了
    Label {
        anchors.centerIn: parent
        text: "Hello MARS!"
        font.pixelSize: 24
    }
}
```

### 验收

```bash
python QT/main.py
```

看到窗口弹出，居中显示 "Hello MARS!"。关掉它。

---

## 第二关：定海神针——全局主题系统

### Boss

建立一个全局主题对象，所有组件通过它取颜色，实现一键亮/暗切换。

### 技能点

- QML `QtObject` — 纯数据对象，不显示
- `property` — QML 的属性系统，支持绑定
- 亮暗双色板设计：背景色、卡片色、文字色、分割线色、悬停色
- QQmlApplicationEngine 的 `rootContext().setContextProperty()` — 把 Python 对象注入 QML 全局

### 装备

写入 `QT/frontend/FluentTheme.qml`：

```qml
import QtQuick

QtObject {
    id: theme

    // ====== 亮/暗切换 ======
    property bool darkMode: false

    // ====== 页面基础色 ======
    readonly property color bgColor:           darkMode ? "#1b1b1b" : "#f0f0f0"
    readonly property color cardColor:         darkMode ? "#2d2d2d" : "#ffffff"
    readonly property color textColor:         darkMode ? "#e0e0e0" : "#2d2d2d"
    readonly property color secondaryText:     darkMode ? "#909090" : "#666666"
    readonly property color dividerColor:      darkMode ? "#3d3d3d" : "#e0e0e0"
    readonly property color hoverColor:        darkMode ? "#3a3a3a" : "#e8e8e8"
    readonly property color inputBg:           darkMode ? "#3a3a3a" : "#ffffff"

    // ====== 主题色（accent）======
    property color accentColor: "#f18cb9"

    // ====== 导航栏 ======
    readonly property real navWidth: 68
    readonly property color navBg:            darkMode ? "#252525" : "#fafafa"
    readonly property color navText:          darkMode ? "#aaaaaa" : "#888888"
    readonly property color navActiveText:    darkMode ? "#ffffff" : "#2d2d2d"
    readonly property color navActiveBg:      darkMode ? "#3a3a3a" : "#e8e8e8"
    readonly property color navIndicator:     accentColor
    readonly property color navHoverBg:       darkMode ? "#303030" : "#f0f0f0"

    // ====== 卡片阴影 ======
    readonly property real cardRadius: 8
    readonly property real cardElevation: 4

    // ====== 消息气泡 ======
    readonly property color userBubbleBg:     accentColor
    readonly property color userBubbleText:   "#ffffff"
    readonly property color aiBubbleBg:       darkMode ? "#3a3a3a" : "#f0f0f0"
    readonly property color aiBubbleText:     darkMode ? "#e0e0e0" : "#2d2d2d"
    readonly property color toolBubbleBg:     darkMode ? "#2d2d2d" : "#fafafa"
    readonly property color toolBubbleBorder: dividerColor

    // ====== 输入栏 ======
    readonly property real inputBarHeight: 56
    readonly property color inputBorder:      darkMode ? "#555555" : "#cccccc"

    // ====== 信息栏 ======
    readonly property color infoBg:           "#2196F3"
    readonly property color successBg:        "#4CAF50"
    readonly property color warningBg:        "#FF9800"
    readonly property color errorBg:          "#F44336"
}
```

### 关键一步：QML 模块 + `qmldir`

QML 需要模块化才能跨文件引用类型。把 `main.qml`、`FluentTheme.qml`、`components/`、`pages/` 全部挪进 `frontend/MARS/`，创建 `qmldir` 声明为 `MARS` 模块。

写入 `QT/frontend/MARS/qmldir`：

```
module MARS
FluentTheme 1.0 FluentTheme.qml
NavigationPanel 1.0 components/NavigationPanel.qml
FluentCard 1.0 components/FluentCard.qml
FluentButton 1.0 components/FluentButton.qml
FluentInfoBar 1.0 components/FluentInfoBar.qml
MessageBubble 1.0 components/MessageBubble.qml
InputBar 1.0 components/InputBar.qml
ChatPage 1.0 pages/ChatPage.qml
SessionsPage 1.0 pages/SessionsPage.qml
ToolsPage 1.0 pages/ToolsPage.qml
SettingsPage 1.0 pages/SettingsPage.qml
```

同时在 `main.py` 注册导入路径、加载 `MARS/main.qml`：

```python
engine.addImportPath(os.path.join(os.path.dirname(__file__), "frontend"))
qml_path = os.path.join(os.path.dirname(__file__), "frontend", "MARS", "main.qml")
engine.load(QUrl.fromLocalFile(qml_path))
```

### 更新 main.qml

`QT/frontend/MARS/main.qml`：

```qml
import QtQuick
import QtQuick.Controls
import MARS 1.0

Window {
    id: window
    width: 960
    height: 640
    minimumWidth: 800
    minimumHeight: 500
    visible: true
    title: "MARS AI Agent"

    readonly property FluentTheme theme: FluentTheme {}

    Rectangle {
        anchors.fill: parent
        color: theme.bgColor

        Label {
            anchors.centerIn: parent
            text: "MARS AI Agent"
            font.pixelSize: 24
            color: theme.textColor
        }
    }

    Shortcut {
        sequence: "T"
        onActivated: theme.darkMode = !theme.darkMode
    }
}
```

### 验收

```bash
python QT/main.py
```

- 窗口出现，背景为主题基础色
- 按 `T` 键，窗口背景和卡片色同时切换亮/暗
- 所有颜色协调

---

## 第三关：龙门——导航面板

### Boss

左侧出现一个 68px 宽的导航栏，4 个导航项（对话/会话/工具/设置），底部有主题切换按钮。选中项高亮，hover 有背景变化。

### 技能点

- `ColumnLayout` / `Column` 纵向布局
- `Item` 配合 `Layout.fillHeight: true` 做弹性占位
- `MouseArea` 处理点击和悬停
- `Behavior on color` 实现背景色平滑过渡
- 选中指示器（左侧 3px 竖条）

### 装备

写入 `QT/frontend/components/NavigationPanel.qml`：

```qml
import QtQuick
import QtQuick.Layouts
import MARS 1.0

Item {
    id: root

    // ====== 对外接口 ======
    property var theme: null   // 由父级传入
    property int currentIndex: 0
    signal itemClicked(int index)

    // ====== 导航项数据 ======
    readonly property var navItems: [
        { icon: "\u{1F3E0}", label: "对话" },  // 🏠
        { icon: "\u{1F4C2}", label: "会话" },  // 📂
        { icon: "\u{1F527}", label: "工具" },  // 🔧
        { icon: "\u{2699}", label: "设置" }    // ⚙
    ]

    width: theme ? theme.navWidth : 68

    Rectangle {
        anchors.fill: parent
        color: theme ? theme.navBg : "#fafafa"

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            // 顶部 Logo 区
            Item {
                Layout.preferredHeight: 60
                Layout.fillWidth: true

                Rectangle {
                    anchors.centerIn: parent
                    width: 36
                    height: 36
                    radius: 8
                    color: theme ? theme.accentColor : "#f18cb9"
                    Label {
                        anchors.centerIn: parent
                        text: "M"
                        color: "#ffffff"
                        font.bold: true
                        font.pixelSize: 18
                    }
                }
            }

            // 导航项
            Repeater {
                model: navItems
                delegate: navDelegate
            }

            // 弹性占位
            Item { Layout.fillHeight: true }

            // 底部主题切换
            Item {
                Layout.preferredHeight: 56
                Layout.fillWidth: true

                Rectangle {
                    anchors.fill: parent
                    anchors.margins: 6
                    radius: 8
                    color: theme && themeToggleArea.containsMouse
                           ? (theme ? theme.navHoverBg : "transparent")
                           : "transparent"

                    Column {
                        anchors.centerIn: parent
                        spacing: 2

                        Label {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: theme && theme.darkMode ? "\u{2600}" : "\u{1F319}"  // ☀ / 🌙
                            font.pixelSize: 18
                        }
                        Label {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: theme && theme.darkMode ? "亮色" : "暗色"
                            font.pixelSize: 9
                            color: theme ? theme.secondaryText : "#888"
                        }
                    }

                    MouseArea {
                        id: themeToggleArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (theme) theme.darkMode = !theme.darkMode
                        }
                    }
                }
            }

            // 底部留白
            Item { Layout.preferredHeight: 12 }
        }
    }

    // ====== 导航项组件 ======
    Component {
        id: navDelegate

        Item {
            Layout.preferredHeight: 56
            Layout.fillWidth: true

            property bool isActive: currentIndex === index
            property bool isHovered: false

            // 选中指示器（左侧竖条）
            Rectangle {
                x: 0
                width: 3
                height: 20
                radius: 1.5
                y: parent.height / 2 - height / 2
                visible: isActive
                color: theme ? theme.navIndicator : "#f18cb9"
            }

            // 背景
            Rectangle {
                anchors.fill: parent
                anchors.margins: 6
                radius: 8
                color: {
                    if (isActive) return theme ? theme.navActiveBg : "#e8e8e8"
                    if (isHovered) return theme ? theme.navHoverBg : "transparent"
                    return "transparent"
                }
                Behavior on color { ColorAnimation { duration: 150 } }
            }

            // 图标 + 文字
            Column {
                anchors.centerIn: parent
                spacing: 2

                Label {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: modelData.icon
                    font.pixelSize: 20
                }
                Label {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: modelData.label
                    font.pixelSize: 9
                    color: isActive
                           ? (theme ? theme.navActiveText : "#2d2d2d")
                           : (theme ? theme.navText : "#888")
                }
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                hoverEnabled: true
                onEntered: isHovered = true
                onExited: isHovered = false
                onClicked: {
                    currentIndex = index
                    itemClicked(index)
                }
            }
        }
    }
}
```

### 在 main.qml 中使用导航面板

修改 `QT/frontend/MARS/main.qml`（添加 `QtQuick.Layouts`）：

```qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import MARS 1.0

Window {
    id: window
    width: 960
    height: 640
    minimumWidth: 800
    minimumHeight: 500
    visible: true
    title: "MARS AI Agent"

    readonly property FluentTheme theme: FluentTheme {}
    color: theme.bgColor

    Shortcut {
        sequence: "T"
        onActivated: theme.darkMode = !theme.darkMode
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // 左侧导航
        NavigationPanel {
            id: navPanel
            theme: window.theme
            Layout.fillHeight: true

            onItemClicked: function(index) {
                pageStack.currentIndex = index
            }
        }

        // 右侧页面区
        StackLayout {
            id: pageStack
            Layout.fillWidth: true
            Layout.fillHeight: true

            // 占位页面
            Rectangle {
                color: theme.bgColor
                Label {
                    anchors.centerIn: parent
                    text: "页面 " + (StackLayout.index + 1)
                    font.pixelSize: 20
                    color: theme.textColor
                }
            }
            Rectangle { color: theme.bgColor; Label { anchors.centerIn: parent; text: "会话"; color: theme.textColor } }
            Rectangle { color: theme.bgColor; Label { anchors.centerIn: parent; text: "工具"; color: theme.textColor } }
            Rectangle { color: theme.bgColor; Label { anchors.centerIn: parent; text: "设置"; color: theme.textColor } }
        }
    }
}
```

### 验收

```bash
python QT/main.py
```

- 左侧 68px 导航栏，4 项图标+文字
- 默认选中"对话"（指示器粉条）
- 鼠标悬停其他项，背景变色（动画平滑）
- 点击切换，指示器跟随
- 底部主题切换按钮，点击后全窗口切换亮/暗
- 右侧 4 个占位页面跟随导航切换

---

## 第四关：基石——UI 组件库

### Boss

做出 3 个可复用组件：`FluentCard`（圆角阴影卡片）、`FluentButton`（带图标和 hover 反馈的按钮）、`FluentInfoBar`（顶部滑入通知）。

### 技能点

- `DropShadow` — QML 中的投影效果
- `NumberAnimation` / `PropertyAnimation` — 属性动画
- `Timer` — 延时、周期性任务
- `OpacityMask` — 裁剪阴影到圆角

### 装备

**FluentCard.qml**：

```qml
import QtQuick

Rectangle {
    id: root

    property alias cardTitle: titleLabel.text
    property bool elevated: true

    // 接收外部主题
    property var theme: null

    radius: theme ? theme.cardRadius : 8
    color: theme ? theme.cardColor : "#ffffff"

    // 阴影
    layer.enabled: elevated
    layer.effect: Item {
        // 使用简单矩形投影（避免平台兼容问题）
        Rectangle {
            anchors.fill: parent
            anchors.margins: -4
            radius: parent.radius + 2
            color: "transparent"
            border.width: 0

            // 模拟阴影：半透明黑矩形偏移
            Rectangle {
                anchors.fill: parent
                anchors.margins: 2
                radius: parent.radius
                color: theme && theme.darkMode
                       ? Qt.rgba(0,0,0,0.3)
                       : Qt.rgba(0,0,0,0.08)
                y: 2
            }
        }
    }

    // 标题
    Label {
        id: titleLabel
        visible: text !== ""
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 16
        font.pixelSize: 14
        font.bold: true
        color: theme ? theme.textColor : "#333"
    }

    // 内容区（留给调用方填充）
    default property alias content: contentArea.data
    Item {
        id: contentArea
        anchors.top: titleLabel.visible ? titleLabel.bottom : parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: titleLabel.visible ? 0 : 0
    }
}
```

**FluentButton.qml**：

```qml
import QtQuick
import QtQuick.Controls

Button {
    id: root

    property var theme: null
    property string iconText: ""
    property int iconSize: 16
    property bool primary: true   // 主色填充 / 透明

    implicitHeight: 36
    implicitWidth: iconText !== "" ? 80 : 60

    // 背景
    background: Rectangle {
        radius: 6
        color: {
            if (!enabled) return theme ? theme.dividerColor : "#ccc"
            if (root.down) return Qt.darker(bgColor, 1.15)
            if (root.hovered) return Qt.lighter(bgColor, 1.08)
            return bgColor
        }
        Behavior on color { ColorAnimation { duration: 100 } }

        readonly property color bgColor: primary
            ? (theme ? theme.accentColor : "#f18cb9")
            : "transparent"

        border.color: primary ? "transparent" : (theme ? theme.dividerColor : "#ccc")
        border.width: primary ? 0 : 1
    }

    // 内容
    contentItem: Row {
        spacing: 4
        anchors.centerIn: parent

        Label {
            text: root.iconText
            font.pixelSize: root.iconSize
            visible: root.iconText !== ""
            color: primary ? "#ffffff" : (theme ? theme.textColor : "#333")
        }
        Label {
            text: root.text
            font.pixelSize: 13
            visible: root.text !== ""
            color: primary ? "#ffffff" : (theme ? theme.textColor : "#333")
        }
    }

    cursorShape: Qt.PointingHandCursor
}
```

**FluentInfoBar.qml**：

```qml
import QtQuick
import QtQuick.Controls

Item {
    id: root

    property var theme: null
    property string infoText: ""
    property string infoType: "info"    // info / success / warning / error
    property int displayDuration: 3000  // ms, 0 = 手动关闭

    visible: false
    height: visible ? 48 : 0
    clip: true

    signal dismissed()

    Behavior on height { NumberAnimation { duration: 200 } }

    Rectangle {
        anchors.fill: parent
        radius: 8
        color: {
            switch (infoType) {
                case "success": return theme ? theme.successBg : "#4CAF50"
                case "warning": return theme ? theme.warningBg : "#FF9800"
                case "error":   return theme ? theme.errorBg : "#F44336"
                default:        return theme ? theme.infoBg : "#2196F3"
            }
        }

        Row {
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            spacing: 8

            Label {
                anchors.verticalCenter: parent.verticalCenter
                text: {
                    switch (infoType) {
                        case "success": return "\u2713"   // ✓
                        case "warning": return "\u26A0"   // ⚠
                        case "error":   return "\u2716"   // ✖
                        default:        return "\u2139"   // ℹ
                    }
                }
                font.pixelSize: 16
                color: "#ffffff"
            }
            Label {
                anchors.verticalCenter: parent.verticalCenter
                text: infoText
                font.pixelSize: 13
                color: "#ffffff"
            }
        }

        // 关闭按钮
        Label {
            anchors.right: parent.right
            anchors.rightMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            text: "\u2716"
            color: "#ffffff"
            font.pixelSize: 14
            visible: displayDuration === 0

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: dismiss()
            }
        }
    }

    function show(text, type, duration) {
        infoText = text
        infoType = type || "info"
        displayDuration = duration || 3000
        visible = true

        if (displayDuration > 0) {
            hideTimer.interval = displayDuration
            hideTimer.start()
        }
    }

    function dismiss() {
        hideTimer.stop()
        root.visible = false
        dismissed()
    }

    Timer {
        id: hideTimer
        onTriggered: dismiss()
    }
}
```

### 验收

暂时无法单独测组件。在 main.qml 里临时添加一个测试卡片来验证：

```qml
// 在 main.qml 的 StackLayout 之前（或替换第一个页面）添加：
FluentCard {
    theme: window.theme
    cardTitle: "测试卡片"
    width: 300
    height: 200
    x: 100
    y: 100
    Label {
        text: "卡片内容"
        color: window.theme.textColor
        anchors.centerIn: parent
    }
}
FluentButton {
    theme: window.theme
    text: "测试按钮"
    x: 420
    y: 100
}
FluentInfoBar {
    id: testBar
    theme: window.theme
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.margins: 8
}
// 在 Component.onCompleted 里:
// testBar.show("信息栏测试", "success", 5000)
```

验证阴影、圆角、hover 变色、信息栏滑入效果。确认后删掉测试代码。

---

## 第五关：初试锋芒——聊天页面布局

### Boss

一个完整的聊天页面：顶部标题栏、中间消息列表（可滚动）、底部输入栏。消息气泡分用户/AI 两种样式。

### 技能点

- `ListView` — QML 中的虚拟列表（只渲染可见项）
- `ScrollBar.vertical` — 自定义滚动条
- `TextArea` — 多行输入框（支持 Shift+Enter 换行、Enter 发送）
- 动态布局：消息靠左（AI）/靠右（用户）

### 装备

**MessageBubble.qml**：

```qml
import QtQuick
import QtQuick.Controls

Rectangle {
    id: root

    property var theme: null
    property string sender: "user"    // user / ai
    property string message: ""
    property string toolName: ""
    property string toolResult: ""

    width: parent ? parent.width : 0
    implicitHeight: contentColumn.height + 24

    color: "transparent"

    Column {
        id: contentColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 16
        y: 12

        // 消息主体
        Rectangle {
            id: bubble
            anchors.left: sender === "ai" ? parent.left : undefined
            anchors.right: sender === "user" ? parent.right : undefined
            width: Math.min(innerText.implicitWidth + 32, parent.width * 0.75)
            radius: 12
            color: sender === "user"
                   ? (theme ? theme.userBubbleBg : "#f18cb9")
                   : (theme ? theme.aiBubbleBg : "#f0f0f0")

            Label {
                id: innerText
                anchors.margins: 16
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                text: root.message
                color: sender === "user"
                       ? (theme ? theme.userBubbleText : "#fff")
                       : (theme ? theme.aiBubbleText : "#333")
                font.pixelSize: 14
                wrapMode: Text.Wrap
            }

            // 工具调用信息（如有）
            Rectangle {
                anchors.top: innerText.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.margins: 12
                visible: root.toolName !== ""
                radius: 8
                color: theme ? theme.toolBubbleBg : "#fafafa"
                border.color: theme ? theme.toolBubbleBorder : "#ddd"
                border.width: 1

                Column {
                    anchors.margins: 10
                    anchors.fill: parent
                    spacing: 4

                    Label {
                        text: "\u{1F527} " + root.toolName
                        font.pixelSize: 12
                        font.bold: true
                        color: theme ? theme.textColor : "#333"
                    }
                    Label {
                        text: root.toolResult
                        font.pixelSize: 11
                        color: theme ? theme.secondaryText : "#666"
                        wrapMode: Text.Wrap
                        elide: Text.ElideRight
                        maximumLineCount: 3
                    }
                }
            }
        }

        // 发送者标签
        Label {
            anchors.left: sender === "ai" ? bubble.left : undefined
            anchors.right: sender === "user" ? bubble.right : undefined
            anchors.top: bubble.bottom
            anchors.topMargin: 4
            text: sender === "user" ? "你" : "MARS"
            font.pixelSize: 11
            color: theme ? theme.secondaryText : "#999"
        }
    }
}
```

**InputBar.qml**：

```qml
import QtQuick
import QtQuick.Controls

Rectangle {
    id: root

    property var theme: null
    property bool isThinking: false
    signal sendMessage(string text)

    height: theme ? theme.inputBarHeight : 56
    color: theme ? theme.cardColor : "#ffffff"

    // 上分割线
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        color: theme ? theme.dividerColor : "#ddd"
    }

    Row {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

        // 输入框
        Rectangle {
            id: inputBg
            height: parent.height - 4
            anchors.verticalCenter: parent.verticalCenter
            width: parent.width - sendBtn.width - 16
            radius: 8
            color: theme ? theme.inputBg : "#fff"
            border.color: inputField.activeFocus
                          ? (theme ? theme.accentColor : "#f18cb9")
                          : (theme ? theme.inputBorder : "#ccc")
            border.width: 1
            Behavior on border.color { ColorAnimation { duration: 150 } }

            TextArea {
                id: inputField
                anchors.fill: parent
                anchors.margins: 8
                placeholderText: root.isThinking ? "AI 思考中..." : "输入消息，Enter 发送..."
                placeholderTextColor: theme ? theme.secondaryText : "#999"
                color: theme ? theme.textColor : "#333"
                font.pixelSize: 14
                enabled: !root.isThinking
                wrapMode: TextArea.Wrap

                // Enter 发送，Shift+Enter 换行
                Keys.onPressed: function(event) {
                    if (event.key === Qt.Key_Return && !(event.modifiers & Qt.ShiftModifier)) {
                        event.accepted = true
                        doSend()
                    }
                }
            }
        }

        // 发送按钮
        Button {
            id: sendBtn
            anchors.verticalCenter: parent.verticalCenter
            width: 40
            height: 40
            enabled: !root.isThinking

            background: Rectangle {
                radius: 8
                color: parent.enabled
                       ? (parent.hovered
                          ? Qt.lighter(theme ? theme.accentColor : "#f18cb9", 1.1)
                          : (theme ? theme.accentColor : "#f18cb9"))
                       : (theme ? theme.dividerColor : "#ccc")
                Behavior on color { ColorAnimation { duration: 100 } }
            }

            contentItem: Label {
                anchors.centerIn: parent
                text: root.isThinking ? "\u23F3" : "\u25B6"  // ⏳ / ▶
                color: "#ffffff"
                font.pixelSize: 18
            }

            onClicked: doSend()
            cursorShape: Qt.PointingHandCursor
        }
    }

    function doSend() {
        var text = inputField.text.trim()
        if (text === "") return
        sendMessage(text)
        inputField.text = ""
    }
}
```

**ChatPage.qml**：

```qml
import QtQuick
import QtQuick.Controls

Rectangle {
    id: root

    property var theme: null
    property bool isThinking: false

    // 消息模型（由 Python 桥接填充）
    property var chatModel: []

    color: theme ? theme.bgColor : "#f0f0f0"

    // 信号
    signal userMessage(string text)

    Column {
        anchors.fill: parent
        spacing: 0

        // 顶部标题栏
        Rectangle {
            width: parent.width
            height: 48
            color: theme ? theme.cardColor : "#ffffff"
            // 底部分割线
            Rectangle {
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: 1
                color: theme ? theme.dividerColor : "#ddd"
            }

            Label {
                anchors.centerIn: parent
                text: "MARS AI 助手"
                font.pixelSize: 16
                font.bold: true
                color: theme ? theme.textColor : "#333"
            }

            // 清空按钮
            Label {
                anchors.right: parent.right
                anchors.rightMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                text: "\u{1F5D1}"  // 🗑
                font.pixelSize: 16
                visible: chatModel.length > 0

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: chatModel = []
                }
            }

            // 思考中指示
            Label {
                anchors.left: parent.left
                anchors.leftMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                text: isThinking ? "思考中..." : ""
                font.pixelSize: 12
                color: theme ? theme.accentColor : "#f18cb9"
                visible: isThinking
            }
        }

        // 消息列表
        ListView {
            id: messageList
            width: parent.width
            height: parent.height - 48 - (theme ? theme.inputBarHeight : 56)
            model: chatModel
            clip: true
            spacing: 4
            cacheBuffer: 200

            // 自动滚动到底部
            onCountChanged: {
                positionViewAtEnd()
            }

            delegate: MessageBubble {
                width: messageList.width
                theme: root.theme
                sender: modelData.sender || "user"
                message: modelData.message || ""
                toolName: modelData.toolName || ""
                toolResult: modelData.toolResult || ""
            }

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
                width: 8
                background: Rectangle { color: "transparent" }

                contentItem: Rectangle {
                    radius: 4
                    color: theme ? theme.dividerColor : "#ccc"
                }
            }
        }

        // 输入栏
        InputBar {
            theme: root.theme
            isThinking: root.isThinking
            onSendMessage: function(text) {
                root.userMessage(text)
            }
        }
    }
}
```

### 在 main.qml 中替换占位

修改 `main.qml`，将第一个 StackLayout 项替换为 ChatPage：

```qml
// 在 StackLayout 中
ChatPage {
    id: chatPage
    theme: window.theme
    Layout.fillWidth: true
    Layout.fillHeight: true

    onUserMessage: function(text) {
        // 暂时只显示在气泡里
        var msg = { sender: "user", message: text }
        chatPage.chatModel = chatPage.chatModel.concat([msg])

        // 模拟 AI 回复
        var aiMsg = { sender: "ai", message: "你说了: " + text }
        chatPage.chatModel = chatPage.chatModel.concat([aiMsg])
    }
}
```

### 验收

```bash
python QT/main.py
```

- 聊天页面：顶部标题栏、中间消息列表、底部输入栏
- 输入文字按 Enter，用户气泡出现在右侧（粉色），AI 回复气泡出现在左侧（灰色）
- Shift+Enter 换行
- 消息列表自动滚动到底部
- 按 🗑 清空消息

---

## 第六关：灵犀一指——Python ↔ QML 桥接

### Boss

在 Python 侧创建 `ChatBridge`（QObject 子类），注册到 QML context，使 QML 可以直接调用 Python 方法，Python 可以向 QML 发射信号。

### 技能点

- `QObject` 子类 + `@Slot()` 装饰器 — 暴露给 QML 的方法
- `Signal` — 从 Python 向 QML 发送事件
- `QmlContext.setContextProperty()` — 将 Python 对象注入 QML 全局命名空间
- `QVariant` / `QList` 在 Python ↔ QML 间的自动转换

### 装备

写入 `QT/backend/chat_bridge.py`：

```python
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtCore import QObject, Slot, Signal, Property
from core.agent.memory import Memory
from core.tools import call_tool, list_tools, get_tool_description


class ChatBridge(QObject):
    # ====== 向 QML 发射的信号 ======
    messageReceived = Signal(str, str)         # sender, text   (流式)
    toolCalled = Signal(str, str, str)         # toolName, args, result
    thinkingChanged = Signal(bool)             # is_thinking
    errorOccurred = Signal(str)                # error message
    sessionListUpdated = Signal(list)          # sessions

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_memory = Memory()
        self._is_thinking = False

    # ====== 属性 ======
    @Property(bool, notify=thinkingChanged)
    def isThinking(self):
        return self._is_thinking

    @isThinking.setter
    def isThinking(self, value):
        if self._is_thinking != value:
            self._is_thinking = value
            self.thinkingChanged.emit(value)

    # ====== QML 可调用的方法 ======

    @Slot(str)
    def sendMessage(self, text):
        """用户发送消息"""
        self._current_memory.add_message("user", text)
        # LLM 调用在 Worker 线程中进行，见第七关
        # 这里先直接回显
        self.messageReceived.emit("user", text)
        self.messageReceived.emit("ai", f"收到: {text} ({len(text)} 字符)")

    @Slot()
    def clearHistory(self):
        """清空当前会话"""
        self._current_memory.clear()

    @Slot(str)
    def loadSession(self, filename):
        """加载已保存的会话"""
        try:
            self._current_memory = Memory.load_session(filename)
        except Exception as e:
            self.errorOccurred.emit(f"加载会话失败: {e}")

    @Slot(str)
    def deleteSession(self, filename):
        """删除会话文件"""
        import os as _os
        session_path = _os.path.join("session", filename)
        if _os.path.exists(session_path):
            _os.remove(session_path)
        self.refreshSessions()

    @Slot()
    def refreshSessions(self):
        """刷新会话列表"""
        sessions = Memory.list_sessions()
        self.sessionListUpdated.emit(sessions)

    @Slot(result=str)
    def getToolDescriptions(self):
        """获取所有工具描述"""
        return get_tool_description()

    @Slot(result=list)
    def getToolNames(self):
        return list_tools()

    @Slot(str, str, result=str)
    def callToolDirectly(self, tool_name, args_json):
        """直接调用工具（用于工具面板测试）"""
        import json
        try:
            args = json.loads(args_json) if args_json else {}
            result = call_tool(tool_name, **args)
            return str(result)
        except Exception as e:
            return f"调用失败: {e}"
```

### 在 main.py 中注册桥接

修改 `QT/main.py`：

```python
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl
from backend.chat_bridge import ChatBridge

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    app.setApplicationName("MARS AI Agent")
    app.setOrganizationName("MARS")

    # 创建桥接对象
    bridge = ChatBridge()

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("chatBridge", bridge)

    qml_path = os.path.join(os.path.dirname(__file__), "frontend", "main.qml")
    engine.load(QUrl.fromLocalFile(qml_path))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
```

### 在 QML 中连接桥接

修改 `main.qml` 中的 ChatPage 连接：

```qml
ChatPage {
    id: chatPage
    theme: window.theme
    Layout.fillWidth: true
    Layout.fillHeight: true

    onUserMessage: function(text) {
        // 调用 Python 桥接
        chatBridge.sendMessage(text)
    }
}

// 连接桥接信号
Connections {
    target: chatBridge

    function onMessageReceived(sender, text) {
        chatPage.chatModel = chatPage.chatModel.concat([
            { sender: sender, message: text }
        ])
    }

    function onErrorOccurred(message) {
        chatPage.chatModel = chatPage.chatModel.concat([
            { sender: "ai", message: "\u26A0\uFE0F " + message }
        ])
    }

    function onThinkingChanged(isThinking) {
        chatPage.isThinking = isThinking
    }
}
```

### 验收

```bash
python QT/main.py
```

- 输入并发送消息，用户气泡出现
- Python 回显回复（"收到: xxx"）出现在 AI 气泡中
- 说明 Python → QML 信号通路通畅

---

## 第七关：内功心法——LLM 工作线程

### Boss

真正的 LLM 调用：在 `QThread` 中执行 `ChatAgent` 的 think-execute-reflect 循环，通过信号逐步把结果发回 QML，不阻塞 UI。

### 技能点

- `QThread` + `Signal` — 工作线程 + 跨线程信号
- `ChatAgent` 的核心循环（`step()` → `run()`）
- 流式输出：每次 LLM 返回 token 就 emit 一次
- 工具调用信息单独 emit

### 装备

写入 `QT/backend/worker.py`：

```python
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtCore import QThread, Signal
from core.agent.chat_agent import ChatAgent
from core.agent.memory import Memory


class ChatWorker(QThread):
    # ====== 向主线程（→QML）的信号 ======
    textChunk = Signal(str)                   # LLM 流式文本片段
    toolInvoked = Signal(str, str, str)       # toolName, args, result
    stepCompleted = Signal(int, int)          # current_step, total_steps
    finished = Signal()
    errorHappened = Signal(str)

    def __init__(self, user_input, memory=None, parent=None):
        super().__init__(parent)
        self.user_input = user_input
        self.memory = memory or Memory()

    def run(self):
        try:
            # 创建 agent（用我们的 memory）
            # ChatAgent 需要 model_manager 参数
            # 我们复用 settings.py 中的 MODEL_ING 和 Debugmode
            from core.config.settings import MODEL_ING, Debugmode

            agent = ChatAgent(user_input=self.user_input)
            # 替换 memory 为当前会话
            agent.history = self.memory

            # 注入信号回调
            # 注意：ChatAgent 默认没有回调机制，我们需要 hack
            # 方案：重写 agent.chat_agent 的几个方法

            # 最干净的方式：子类化 ChatAgent 或 monkey-patch
            self._run_agent(agent)

        except Exception as e:
            import traceback
            self.errorHappened.emit(f"Worker 错误: {e}\n{traceback.format_exc()}")
        finally:
            self.finished.emit()

    def _run_agent(self, agent):
        """运行 Agent 循环，发射信号"""
        max_steps = 100
        consecutive_failures = 0

        # 添加用户消息
        agent.history.add_message("user", self.user_input)

        for step in range(max_steps):
            self.stepCompleted.emit(step + 1, max_steps)

            # Think
            action = agent.think()
            tool_name = action.get("action", {}).get("tool", "")
            tool_args = action.get("action", {}).get("tool_args", {})

            if not tool_name:
                continue

            # 发射工具调用信息
            args_str = str(tool_args)
            self.toolInvoked.emit(tool_name, args_str, "执行中...")

            # Execute
            result = agent.execute({"action": {"tool": tool_name, "tool_args": tool_args}})
            result_str = str(result)[:200]  # 截断防止 QML 卡死

            # 发射工具结果
            self.toolInvoked.emit(tool_name, args_str, result_str)

            # 模拟流式输出（真正的流式需要修改 ModelManager）
            self.textChunk.emit(f"[步骤 {step+1}] 调用 {tool_name} → 完成\n")

            # Reflect
            agent.reflect(result, tool_name, tool_args)

            # 检查是否完成
            if tool_name == "finish":
                self.textChunk.emit("\n**任务完成**\n")
                break

            # 连续失败检测
            if agent._check_failure(result):
                consecutive_failures += 1
                if consecutive_failures >= 3:
                    self.textChunk.emit("\n连续失败次数过多，终止\n")
                    break
            else:
                consecutive_failures = 0
```

### 升级 ChatBridge 使用 Worker

修改 `QT/backend/chat_bridge.py`，添加 `_start_worker` 方法：

```python
from backend.worker import ChatWorker

class ChatBridge(QObject):
    # ...（已有信号不变）

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_memory = Memory()
        self._is_thinking = False
        self._worker = None

    # ...（已有方法）

    @Slot(str)
    def sendMessage(self, text):
        """用户发送消息 → 启动 Worker"""
        if self._worker and self._worker.isRunning():
            self.errorOccurred.emit("请等待当前任务完成")
            return

        self.isThinking = True
        self.messageReceived.emit("user", text)

        # 启动 Worker
        self._worker = ChatWorker(text, memory=self._current_memory)
        self._worker.textChunk.connect(self._on_text_chunk)
        self._worker.toolInvoked.connect(self._on_tool_invoked)
        self._worker.stepCompleted.connect(self._on_step_completed)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.errorHappened.connect(self._on_worker_error)
        self._worker.start()

    def _on_text_chunk(self, chunk):
        self.messageReceived.emit("ai", chunk)

    def _on_tool_invoked(self, tool_name, args, result):
        # 作为特殊消息发送给 QML
        self.toolInvoked.emit(tool_name, args, result)

    def _on_step_completed(self, current, total):
        pass  # 可用来更新进度

    def _on_worker_finished(self):
        self.isThinking = False
        self._worker = None

    def _on_worker_error(self, msg):
        self.errorOccurred.emit(msg)
        self.isThinking = False
        self._worker = None
```

### 在 QML 中接收 Worker 信号

修改 `main.qml` 中的 Connections：

```qml
Connections {
    target: chatBridge

    function onMessageReceived(sender, text) {
        chatPage.chatModel = chatPage.chatModel.concat([
            { sender: sender, message: text }
        ])
    }

    function onToolCalled(toolName, args, result) {
        chatPage.chatModel = chatPage.chatModel.concat([
            {
                sender: "ai",
                message: "\u{1F527} 工具: " + toolName,
                toolName: toolName,
                toolResult: result
            }
        ])
    }

    function onErrorOccurred(message) {
        chatPage.chatModel = chatPage.chatModel.concat([
            { sender: "ai", message: "\u26A0\uFE0F " + message }
        ])
    }

    function onThinkingChanged(isThinking) {
        chatPage.isThinking = isThinking
    }
}
```

### 验收前置条件

必须先在 `.env` 中配置好 `DEEPSEEK_API_KEY`（或确保本地 Ollama 可用），否则 Worker 会报错。

### 验收

```bash
python QT/main.py
```

- 输入消息后，聊天面板显示调用过程
- 工具调用卡片折叠显示
- 输入栏在 Worker 运行时禁用（显示"思考中..."）
- 任务完成后输入栏恢复正常

---

## 第八关：百家争鸣——完整功能页

### Boss

完成会话管理页、工具面板页、设置页三个功能页。导航栏 4 个页面全部可用。

### 技能点

- `QAbstractListModel` — 为 QML ListView 提供 Python 端数据模型（会话列表）
- QML `ListView` + `delegate` 绑定 Python 模型
- `SettingsPage` 读写 `settings.py`
- `ToolsPage` 展示工具列表

### 装备

#### 会话模型

写入 `QT/backend/session_model.py`：

```python
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Slot, Signal, QObject
from core.agent.memory import Memory
import os


class SessionListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._sessions = []
        self.refresh()

    # ====== 角色定义 ======
    def roleNames(self):
        return {
            Qt.UserRole + 1: b"filename",
            Qt.UserRole + 2: b"summary",
            Qt.UserRole + 3: b"created_time",
            Qt.UserRole + 4: b"message_count",
        }

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._sessions):
            return None
        s = self._sessions[index.row()]
        mapping = {
            Qt.UserRole + 1: s.get("filename", ""),
            Qt.UserRole + 2: s.get("summary", ""),
            Qt.UserRole + 3: s.get("created_time", "")[:19],
            Qt.UserRole + 4: s.get("message_count", 0),
        }
        return mapping.get(role)

    def rowCount(self, parent=QModelIndex()):
        return len(self._sessions)

    @Slot()
    def refresh(self):
        self.beginResetModel()
        self._sessions = Memory.list_sessions()
        self.endResetModel()

    @Slot(str)
    def deleteSession(self, filename):
        session_path = os.path.join("session", filename)
        if os.path.exists(session_path):
            os.remove(session_path)
        self.refresh()
```

在 `main.py` 中注册：

```python
from backend.session_model import SessionListModel

session_model = SessionListModel()
engine.rootContext().setContextProperty("sessionModel", session_model)
```

#### SessionsPage.qml

```qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root

    property var theme: null

    color: theme ? theme.bgColor : "#f0f0f0"

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 标题栏
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 48
            color: theme ? theme.cardColor : "#fff"

            Rectangle {
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: 1
                color: theme ? theme.dividerColor : "#ddd"
            }

            Label {
                anchors.left: parent.left
                anchors.leftMargin: 20
                anchors.verticalCenter: parent.verticalCenter
                text: "\u{1F4C2} 会话管理"
                font.pixelSize: 16
                font.bold: true
                color: theme ? theme.textColor : "#333"
            }

            Button {
                anchors.right: parent.right
                anchors.rightMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                text: "刷新"
                onClicked: sessionModel.refresh()
                background: Rectangle {
                    radius: 6
                    color: parent.hovered
                           ? Qt.lighter(theme ? theme.accentColor : "#f18cb9", 1.1)
                           : (theme ? theme.accentColor : "#f18cb9")
                }
                contentItem: Label {
                    anchors.centerIn: parent
                    text: parent.text
                    color: "#fff"
                    font.pixelSize: 13
                }
            }
        }

        // 会话列表
        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 16
            model: sessionModel
            spacing: 8
            clip: true

            delegate: Rectangle {
                width: ListView.view.width
                height: 80
                radius: theme ? theme.cardRadius : 8
                color: theme ? theme.cardColor : "#fff"

                // 阴影效果
                layer.enabled: true
                layer.effect: Item {
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: -2
                        radius: parent.radius + 1
                        color: Qt.rgba(0,0,0, theme && theme.darkMode ? 0.3 : 0.06)
                        y: 1
                    }
                }

                Column {
                    anchors.left: parent.left
                    anchors.leftMargin: 16
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 4

                    Label {
                        text: model.summary || "(无摘要)"
                        font.pixelSize: 14
                        font.bold: true
                        color: theme ? theme.textColor : "#333"
                        elide: Text.ElideRight
                        width: parent.parent.width - 180
                    }
                    Label {
                        text: model.created_time
                        font.pixelSize: 11
                        color: theme ? theme.secondaryText : "#999"
                    }
                    Label {
                        text: model.message_count + " 条消息"
                        font.pixelSize: 11
                        color: theme ? theme.secondaryText : "#999"
                    }
                }

                Row {
                    anchors.right: parent.right
                    anchors.rightMargin: 16
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8

                    Button {
                        text: "加载"
                        onClicked: chatBridge.loadSession(model.filename)
                        background: Rectangle {
                            radius: 6
                            color: parent.hovered
                                   ? Qt.lighter(theme ? theme.accentColor : "#f18cb9", 1.1)
                                   : (theme ? theme.accentColor : "#f18cb9")
                        }
                        contentItem: Label {
                            anchors.centerIn: parent
                            text: parent.text
                            color: "#fff"
                            font.pixelSize: 12
                        }
                    }

                    Button {
                        text: "\u{1F5D1}"
                        onClicked: sessionModel.deleteSession(model.filename)
                        background: Rectangle {
                            radius: 6
                            color: parent.hovered ? "#ff4444" : "transparent"
                            border.color: "#ff4444"
                            border.width: 1
                        }
                        contentItem: Label {
                            anchors.centerIn: parent
                            text: parent.text
                            font.pixelSize: 14
                        }
                    }
                }
            }

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
                width: 8
                contentItem: Rectangle {
                    radius: 4
                    color: theme ? theme.dividerColor : "#ccc"
                }
            }
        }
    }
}
```

#### ToolsPage.qml

```qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root

    property var theme: null

    color: theme ? theme.bgColor : "#f0f0f0"

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 48
            color: theme ? theme.cardColor : "#fff"
            Rectangle {
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: 1
                color: theme ? theme.dividerColor : "#ddd"
            }
            Label {
                anchors.left: parent.left
                anchors.leftMargin: 20
                anchors.verticalCenter: parent.verticalCenter
                text: "\u{1F527} 工具面板"
                font.pixelSize: 16
                font.bold: true
                color: theme ? theme.textColor : "#333"
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 16
            clip: true

            Column {
                spacing: 8
                width: parent.width

                Repeater {
                    model: chatBridge.getToolNames()

                    delegate: Rectangle {
                        width: parent.width
                        height: 60
                        radius: theme ? theme.cardRadius : 8
                        color: theme ? theme.cardColor : "#fff"

                        Row {
                            anchors.left: parent.left
                            anchors.leftMargin: 16
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 12

                            Label {
                                anchors.verticalCenter: parent.verticalCenter
                                text: "\u{1F4E6}"
                                font.pixelSize: 20
                            }
                            Column {
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 2
                                Label {
                                    text: modelData
                                    font.pixelSize: 14
                                    font.bold: true
                                    color: theme ? theme.textColor : "#333"
                                }
                                Label {
                                    text: "点击查看详情"
                                    font.pixelSize: 11
                                    color: theme ? theme.secondaryText : "#999"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
```

#### SettingsPage.qml

```qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root

    property var theme: null

    color: theme ? theme.bgColor : "#f0f0f0"

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 48
            color: theme ? theme.cardColor : "#fff"
            Rectangle {
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: 1
                color: theme ? theme.dividerColor : "#ddd"
            }
            Label {
                anchors.left: parent.left
                anchors.leftMargin: 20
                anchors.verticalCenter: parent.verticalCenter
                text: "\u2699\uFE0F 设置"
                font.pixelSize: 16
                font.bold: true
                color: theme ? theme.textColor : "#333"
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 20

            Column {
                spacing: 16
                width: parent.width

                // 模型选择
                Label {
                    text: "模型选择"
                    font.pixelSize: 13
                    font.bold: true
                    color: theme ? theme.textColor : "#333"
                }
                ComboBox {
                    id: modelCombo
                    model: ["deepseek-reasoner", "deepseek-chat", "本地 Ollama"]
                    currentIndex: 0
                    width: 260
                    background: Rectangle {
                        radius: 6
                        color: theme ? theme.inputBg : "#fff"
                        border.color: theme ? theme.inputBorder : "#ccc"
                        border.width: 1
                    }
                }

                // API Key
                Label {
                    text: "API Key"
                    font.pixelSize: 13
                    font.bold: true
                    color: theme ? theme.textColor : "#333"
                }
                TextField {
                    id: apiKeyField
                    width: 400
                    placeholderText: "sk-..."
                    echoMode: TextInput.Password
                    background: Rectangle {
                        radius: 6
                        color: theme ? theme.inputBg : "#fff"
                        border.color: theme ? theme.inputBorder : "#ccc"
                        border.width: 1
                    }
                }

                // Debug 模式
                Row {
                    spacing: 12
                    Label {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Debug 模式"
                        font.pixelSize: 13
                        font.bold: true
                        color: theme ? theme.textColor : "#333"
                    }
                    Switch {
                        id: debugSwitch
                        checked: false
                    }
                }

                // 主题切换
                Row {
                    spacing: 12
                    Label {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "主题"
                        font.pixelSize: 13
                        font.bold: true
                        color: theme ? theme.textColor : "#333"
                    }
                    Button {
                        text: theme && theme.darkMode ? "\u{2600} 亮色" : "\u{1F319} 暗色"
                        onClicked: theme.darkMode = !theme.darkMode
                        background: Rectangle {
                            radius: 6
                            color: parent.hovered
                                   ? Qt.lighter(theme ? theme.accentColor : "#f18cb9", 1.1)
                                   : (theme ? theme.accentColor : "#f18cb9")
                        }
                        contentItem: Label {
                            anchors.centerIn: parent
                            text: parent.text
                            color: "#fff"
                        }
                    }
                }
            }
        }
    }
}
```

### 注册页面到导航

在 `main.qml` 中将 StackLayout 的占位全部替换为真实页面：

```qml
StackLayout {
    id: pageStack
    Layout.fillWidth: true
    Layout.fillHeight: true
    currentIndex: navPanel.currentIndex

    ChatPage { id: chatPage; theme: window.theme; /* ...信号连接同上... */ }
    SessionsPage { theme: window.theme }
    ToolsPage { theme: window.theme }
    SettingsPage { theme: window.theme }
}
```

### 验收

- 4 个导航项全部指向真实页面
- 会话管理页列出 `session/` 目录下的 JSON 文件
- 工具面板展示所有注册的工具名
- 设置页可切换主题、输入 API Key 等
- 明/暗主题切换影响所有页面

---

## 第九关：画龙点睛——动画与打磨

### Boss

让 UI 交互有 MRobot 级别的丝滑感。

### 技能点

- `Behavior on ... { NumberAnimation { duration: 150; easing: Easing.OutCubic } }`
- `SequentialAnimation` + `PauseAnimation` — 序列动画
- `OpacityAnimator` / `ScaleAnimator` — 独立属性动画

### 装备

逐个打磨以下细节：

#### 1. 消息气泡出现动画

修改 `MessageBubble.qml`，包装在 `Item` 中加进入动画：

```qml
// 在 MessageBubble.qml 最外层 Item 加：
Item {
    // ...
    opacity: 0

    NumberAnimation on opacity {
        from: 0; to: 1
        duration: 200
        easing.type: Easing.OutCubic
    }

    // Y 方向滑入
    transform: Translate {
        id: slideIn
        y: 20
    }
    NumberAnimation on y {
        from: 20; to: 0
        duration: 250
        easing.type: Easing.OutCubic
    }
}
```

#### 2. 导航图标悬停缩放

在 `NavigationPanel.qml` 的 navDelegate 的图标 Label 上：

```qml
Label {
    // ...
    scale: isHovered ? 1.1 : 1.0
    Behavior on scale { NumberAnimation { duration: 100 } }
}
```

#### 3. 按钮点击反馈

在 `FluentButton.qml` 的 background Rectangle 上：

```qml
// 点击时略微缩小
property real normalScale: 1.0
property real pressedScale: 0.97

// 在根 Item 上：
scale: root.down ? pressedScale : normalScale
Behavior on scale { NumberAnimation { duration: 80 } }
```

#### 4. 页面切换过渡

给 `StackLayout` 的下级 Item 加：

```qml
// 对每个页面 Item：
OpacityAnimator {
    from: 0; to: 1
    duration: 150
    running: StackLayout.isCurrentItem
}
```

#### 5. 输入框 focus 光晕动画

`InputBar.qml` 中 border.color 已有 Behavior，再加微弱的阴影：

```qml
// inputBg 加:
layer.enabled: inputField.activeFocus
layer.effect: Item {
    Rectangle {
        anchors.fill: parent
        anchors.margins: -4
        radius: parent.radius + 2
        color: Qt.rgba(theme.accentColor.r, theme.accentColor.g, theme.accentColor.b, 0.15)
    }
}
Behavior on layer.enabled { NumberAnimation { duration: 150 } }
```

#### 6. InfoBar 滑入动画

已有 `Behavior on height`，再加 x 方向的滑入：

```qml
// 在 FluentInfoBar.qml 的根 Item 上：
NumberAnimation on opacity {
    from: 0; to: 1
    duration: 200
}
```

#### 7. 滚动条美化

统一滚动条样式（复制到每个需要的地方）：

```qml
ScrollBar.vertical: ScrollBar {
    policy: ScrollBar.AsNeeded
    width: 8
    background: Rectangle {
        color: "transparent"
    }
    contentItem: Rectangle {
        radius: 4
        color: theme ? theme.dividerColor : "#ccc"
        opacity: parent.hovered ? 0.8 : 0.4
        Behavior on opacity { NumberAnimation { duration: 150 } }
    }
}
```

### 验收

- 所有交互都有平滑的过渡动画
- 没有闪烁或卡顿
- 动画时长一致（150-250ms），风格统一
- 明暗主题切换平滑

---

## 最终 BOSS：自测清单

逐一检查，全部打 ✓ 才算通关：

### 基础功能

- [ ] `python QT/main.py` 启动成功，窗口显示
- [ ] 左侧导航栏 4 个页面切换正常
- [ ] 按 T 键切换亮/暗主题
- [ ] 底部主题按钮切换亮/暗

### 聊天页

- [ ] 输入文字按 Enter 发送
- [ ] Shift+Enter 换行
- [ ] 用户气泡粉色右对齐
- [ ] AI 气泡灰色左对齐
- [ ] LLM 回复流式显示（逐 token 出现）
- [ ] 工具调用卡片可折叠
- [ ] 思考中输入栏禁用
- [ ] 🗑 清空按钮可用
- [ ] 消息列表自动滚动到底部

### 会话管理

- [ ] 列出 `session/` 目录下的所有 .json
- [ ] 显示摘要、时间、消息数
- [ ] 点击"加载"加载会话到聊天页
- [ ] 点击"删除"删除文件并刷新列表

### 工具面板

- [ ] 展示所有已注册工具名
- [ ] 可点击查看工具详情

### 设置页

- [ ] 模型下拉可选
- [ ] API Key 输入（密文）
- [ ] Debug 模式开关
- [ ] 主题切换按钮

### 视觉质量

- [ ] 导航栏 hover 背景渐变
- [ ] 导航选中指示器粉条
- [ ] 卡片圆角 + 阴影
- [ ] 消息气泡出现动画
- [ ] 按钮 hover/down 反馈
- [ ] 滚动条悬停可见度变化
- [ ] 亮暗主题所有颜色协调

### 稳定性

- [ ] 连续快速发送不会崩溃
- [ ] Worker 运行时不能重复发送
- [ ] Worker 错误时输入栏恢复正常
- [ ] 内存不持续增长

---

## 附：常见问题

**Q: QML 报错 "module is not defined"**
A: 确保 `QT/frontend/MARS/qmldir` 文件存在且格式正确（第一行 `module MARS`），并在 `main.py` 中调用了 `engine.addImportPath("frontend/")`。QML 里用 `import MARS 1.0`。

**Q: Worker 启动了但 LLM 没响应**
A: 检查 `.env` 文件中的 API Key。可以先用 `python main.py`（CLI 模式）验证 LLM 连通性。

**Q: 属性绑定循环警告**
A: 检查是否有 `property a: b` 和 `property b: a` 相互依赖。用 `readonly property` 打断循环。

**Q: 窗口缩放时布局错乱**
A: 确保用 `Layout.fillWidth/Height` 或 `anchors.fill`，不要用绝对坐标（导航面板除外，它固定宽度）。

---

> **恭喜通关！** 🎉 你已为 MARS AI Agent 构建了一个功能完整、视觉精致的桌面客户端。
> 现在你可以回过头来：
> - 打磨细节（字体、间距、颜色微调）
> - 添加高级功能（会话搜索、工具调用历史、模型参数调节）
> - 打包分发（PyInstaller 参考 MRobot 的 MRobot.iss）
