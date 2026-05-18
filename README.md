# MARS AI Agent

基于 ConversationRuntime 架构的 AI 代理系统，支持命令行和 PySide6 QML 桌面客户端。LLM 自主规划、调用工具、验证结果，完成文件操作、代码分析、网络搜索等任务。

## 功能特性

- **双端运行**：CLI 交互模式 + PySide6 QML 桌面 GUI
- **ConversationRuntime**：单次 `run_turn()` 完成完整对话轮次，回调驱动
- **17 个工具**：文件读写、Shell、网络搜索、网页抓取、正则 grep、Python 执行、文件管理等
- **会话持久化**：JSON 自动保存，支持加载/删除/新建/列表
- **LLM 上下文继承**：加载会话自动重建完整对话历史传入 LLM
- **AI 回复持久化**：talk/finish 文本自动写入 Memory → JSON
- **工具卡片 UI**：可折叠的半透明工具调用面板
- **模型热切换**：`ApiClient.active_model` 类变量，运行时即时切换
- **权限控制**：4 级权限模式（READ_ONLY / WORKSPACE_WRITE / DANGER_FULL / ALL）
- **收敛检测**：连续 3 步相同工具+参数 → 自动 finish
- **会话压缩**：超过 50000 token 自动摘要压缩
- **亮暗主题**：按 `T` 切换，FluentTheme 配色
- **截断 JSON 修复**：LLM 响应超出 token 限制时自动提取文本

## 技术栈

- **语言**：Python 3.10+
- **桌面端**：PySide6 (Qt6 QML, `QT_QUICK_CONTROLS_STYLE=Basic`)
- **LLM**：DeepSeek API (OpenAI) / Ollama 本地模型
- **架构**：QThread 异步工作线程，QObject 信号桥接 Python↔QML
- **存储**：JSON 文件持久化
- **依赖**：openai, ollama, requests, beautifulsoup4, chardet, pyttsx3

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
main.py                    CLI 入口，ConversationRuntime + Memory 驱动
QT/
 ├── main.py               桌面入口，QML 引擎 + ChatBridge 桥接
 ├── backend/
 │   ├── chat_bridge.py    Python↔QML 桥接（QObject），所有信号/槽
 │   └── worker.py         ChatWorker (QThread)，创建 ConversationRuntime
 └── frontend/MARS/        QML 前端
     ├── main.qml          窗口 + 导航 + Connections 信号处理
     ├── FluentTheme.qml   亮暗主题色系统
     ├── qmldir            模块声明 (MARS 1.0)
     ├── components/       MessageBubble, InputBar, NavigationPanel
     └── pages/            ChatPage, ToolsPage, SettingsPage
core/
 ├── runtime/              运行时核心（新架构）
 │   ├── types.py          TextBlock, ToolUse, ConversationMessage 等类型
 │   ├── conversation.py   ConversationRuntime, memory_to_runtime_messages
 │   ├── permissions.py    权限策略（4 级模式）
 │   ├── usage.py          TokenUsage 追踪器
 │   └── compact.py        SessionCompactor（自动摘要压缩）
 ├── llm/
 │   ├── client.py         ApiClient (stream/parse_response) + ModelManager
 ├── agent/
 │   └── memory.py         Memory（JSON 持久化，history + messages 分离）
 ├── prompt/
 │   ├── builder.py        SystemPromptBuilder（动态环境/平台/日期）
 │   └── __init__.py
 ├── tools/
 │   ├── __init__.py       工具注册表 (TOOL_DEFINITIONS + TOOL_REGISTRY + call_tool)
 │   └── tools.py          17 个工具实现
 └── config/
     └── settings.py       配置项 (DEEP_SEEK_API_KEY, Debugmode, LLM_URL)
session/                   会话 JSON 持久化目录
```

## 架构

```
┌─────────────────────────────────────────────────────────┐
│ QML 界面  ←─── Qt Signals ───→  ChatBridge (QObject)    │
│ ChatPage      messageReceived     sendMessage(text)     │
│ ToolsPage     toolCalled          loadSession(f)        │
│ SettingsPage  sessionListUpdated  newSession()          │
└─────────────────────────────────────────────────────────┘
                        │
                        │ ChatWorker(text, api_client, memory)
                        ▼
┌─────────────────────────────────────────────────────────┐
│ ChatWorker (QThread)                                     │
│   ConversationRuntime(messages=..., system_prompt=...)  │
│   ├─ run_turn(user_input, client, executor,             │
│   │           on_text, on_tool, on_save)                │
│   │                                                     │
│   │   for iteration in range(max_iterations):           │
│   │     request = ApiRequest(messages, system, tools)   │
│   │     blocks, usage = api_client.stream(request)       │
│   │     msg = ConversationMessage.assistant(blocks)     │
│   │                                                     │
│   │     if not tool_uses:   ← talk/finish              │
│   │       on_text(block)    → textChunk → QML 显示      │
│   │       on_save("assistant", block) → JSON 持久化     │
│   │       return                                        │
│   │                                                     │
│   │     for tool_use in tool_uses:  ← shell/read_file  │
│   │       result = executor.execute(name, input)        │
│   │       on_tool(name, input, result) → QML 工具卡片   │
│   │       on_save("tool", result, name, args) → JSON    │
│   └─────────────────────────────────────────────────────│
│                                                         │
│   ApiClient.stream(request)                              │
│   ├─ _format_messages(ConversationMessage → API dicts) │
│   ├─ _call_cloud / _call_local (OpenAI / Ollama)       │
│   └─ _parse_response(raw_text → TextBlock | ToolUse)   │
└─────────────────────────────────────────────────────────┘
```

**CLI 模式**：直接实例化 `ConversationRuntime` + `ApiClient`，`run_turn()` 驱动，回调输出到终端。

**GUI 模式**：
1. `ChatBridge` 暴露为 `contextProperty("chatBridge", bridge)`
2. QML 用户输入 → `chatBridge.sendMessage(text)` → 创建 `ChatWorker`
3. `ChatWorker.run()` 在 QThread 中创建 `ConversationRuntime`
4. 通过 3 个回调 (`on_text`, `on_tool`, `on_save`) 分别负责显示、工具调用、持久化
5. Qt 信号 (`textChunk`, `toolInvoked`, `messageReceived`) 推送到 QML

**LLM 上下文继承**：
- 加载会话时 `memory_to_runtime_messages(memory.history)` 将 JSON 条目转为 `ConversationMessage` 序列
- 预填入 `runtime.messages`，`run_turn()` 调用 `ApiRequest(messages=...)` 时 LLM 看到完整历史

## 数据模型

```
ConversationMessage         Memory (JSON 存储)
 ├─ role: USER               ├─ history: list[dict]
 │   └─ blocks: [TextBlock]  │   ├─ {"role":"user","content":"..."}
 ├─ role: ASSISTANT          │   ├─ {"input":{"tool":"shell","tool_args":"..."),"output":"..."}
 │   └─ blocks: [TextBlock]  │   └─ {"role":"assistant","content":"..."}
 │    或 [ToolUse]            └─ messages: list[dict]  (只有 user + assistant)
 └─ role: TOOL                  (用于会话摘要生成)
     └─ blocks: [ToolResult]
```

## 配置

`DEEPSEEK_API_KEY` 需设为系统环境变量（云端模型必需）。

`core/llm/client.py` 中 `ModelManager.available_models` 管理模型列表。GUI 设置页可动态添加/删除自定义模型。

## 使用

**CLI 命令**：
| 命令 | 功能 |
|------|------|
| `help` | 帮助 |
| `clear` | 清空当前会话 |
| `history` | 查看工具步骤记录 |
| `messages` | 查看对话消息 |
| `list` | 列出所有会话 |
| `load <文件名>` | 加载指定会话 |

**GUI 操作**：
- 输入框发送消息，Enter 发送，Shift+Enter 换行
- ☰ 按钮切换侧边栏（会话列表）
- 左侧导航栏切换页面（Chat / Tools / Settings）
- `T` 键切换暗色模式
- Settings 页：切换模型、管理自定义模型、配置 API Key

## 工具列表（17 个）

| 工具 | 功能 | 关键参数 |
|------|------|----------|
| `read_file` | 读取文件（自动编码检测） | file_path, search, start_line, max_lines |
| `write_file` | 写入文件（自动创建目录/备份） | file_path, content, append, backup |
| `replace_content` | 替换文件内容（正则支持） | file_path, old_content, new_content, regex, count |
| `shell` | 执行 PowerShell 命令 | command, timeout, cwd |
| `talk` | 与用户对话 | message |
| `finish` | 完成任务 | response |
| `web_search` | Bing 网络搜索 | query |
| `web_content` | 获取网页纯文本 | urls |
| `weather` | 查询天气 | city, detail |
| `speaking` | 文字转语音 | text, rate, volume |
| `list_directory` | 列出目录 | path, all, pattern |
| `create_directory` | 创建目录 | path |
| `delete_path` | 删除文件/目录 | path, recursive |
| `copy_move` | 复制/移动文件 | src, dst, action |
| `grep_files` | 正则搜索文件 | pattern, path, include |
| `file_info` | 文件详细信息 | path |
| `python_exec` | 执行 Python 代码 | code |

## 许可证

MIT
