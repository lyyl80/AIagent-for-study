# MARS AI Agent

模块化 AI 代理系统，支持命令行和 PySide6 QML 桌面客户端。基于思考-执行-反思循环驱动 LLM 自主完成文件操作、代码分析、网络搜索等任务。

## 功能特性

- **双端运行**：CLI 交互模式 + QML 桌面 GUI
- **思考-执行-反思循环**：LLM 自主规划、调用工具、验证结果
- **工具系统**：文件读写、Shell 命令、网络搜索、内容替换等
- **会话持久化**：对话历史自动保存，支持加载/删除
- **流式输出**：桌面端实时显示 LLM 响应
- **亮暗主题**：按 `T` 切换，支持主题色系统
- **流式输出**：桌面端实时显示 LLM 响应（实际尚未实现，计划中）

## 技术栈

- **语言**：Python 3.8+
- **桌面端**：PySide6 (Qt6 QML)
- **LLM**：DeepSeek API / OpenAI / Ollama
- **架构**：QThread 异步工作线程，QObject 桥接 Python↔QML
- **存储**：JSON 文件持久化

## 快速开始

```bash
pip install -r requirements.txt
```

**命令行模式**：
```bash
python main.py
```

**桌面客户端**：
```bash
python QT/main.py
```
按 `T` 切换亮/暗主题。

## 项目结构

```
main.py               CLI 入口，交互式对话
QT/
 ├── main.py          桌面客户端入口，启动 QML 引擎
 ├── backend/
 │   ├── chat_bridge.py   Python↔QML 桥接（QObject）
 │   └── worker.py        LLM 工作线程（QThread）
 └── frontend/MARS/       QML 前端
     ├── main.qml         窗口 + 导航布局
     ├── FluentTheme.qml  亮暗主题色
     ├── components/      UI 组件（气泡、输入栏、导航等）
     └── pages/           页面（聊天、工具、设置）
core/
 ├── agent/
 │   ├── chat_agent.py    思考-执行-反思主循环
 │   └── memory.py        会话持久化（JSON）
 ├── llm/client.py        LLM 模型管理
 ├── prompt/templates.py  提示词模板（精简版）
 ├── tools/               工具注册表 + 实现
 └── config/settings.py   配置项
```

## 架构

```
CLI:  用户输入 → ChatAgent.step() 循环 → Memory 持久化
GUI:  用户输入 → ChatBridge → ChatWorker(QThread) → ChatAgent.step()
         ↓                                       ↓
      QML 界面 ← 信号(textChunk/toolInvoked) ←──┘
```

**CLI 模式**：直接实例化 `ChatAgent`，`run()` 方法驱动循环。

**GUI 模式**：
1. `ChatBridge(QObject)` 暴露给 QML 上下文，接收用户输入
2. `ChatWorker(QThread)` 在后台运行 `ChatAgent.step()` 循环
3. 通过 Qt 信号（`textChunk`、`toolInvoked`）将结果推送到 QML
4. `Memory` 存储全部对话历史，支持跨会话加载

**记忆系统**：`Memory` 每步自动保存，`session_id` 区分会话。`get_history(n)` 返回最近 n 条记录供 LLM 上下文参考。

## 配置

创建 `.env` 文件：
```
DEEPSEEK_BASE_URL=https://api.deepseek.ai
LLM_URL=http://localhost:11434
```

`DEEP_SEEK_API_KEY` 需设为系统环境变量（因 `.env` 首行 `import os` 与 `python-dotenv` 冲突）。

修改 `core/config/settings.py` 可调整默认模型和调试模式。

## 使用

**CLI 命令**：
- `help` — 帮助
- `clear` — 清空历史
- `history` — 查看步骤记录
- `list` — 列出会话
- `load <文件名>` — 加载会话

**GUI 操作**：
- 输入框发送消息，Enter 发送，Shift+Enter 换行
- 左侧导航栏切换页面
- 底部主题按钮 / `T` 键切换暗色模式
- 🗑 清空当前对话

## 后续路线图

- [x] 基础聊天界面 + LLM 流式输出
- [x] 亮暗主题切换
- [x] 工具调用显示
- [ ] 会话侧边栏（ChatPage 内嵌，可折叠）
- [ ] 工具面板页（展示工具列表/详情）
- [ ] 设置页（模型选择、API Key、Debug 开关）
- [ ] 可折叠思考框（显示 LLM 推理过程）
- [ ] 消息流式逐 token 显示
- [ ] 会话加载后恢复消息列表
- [ ] 工具结果真实内容显示（非"执行完成"）

## 许可证

MIT
