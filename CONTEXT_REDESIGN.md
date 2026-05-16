# MARS AI Agent — 上下文处理系统重构通关教程

> **目标**：基于 [claw-code-main](D:\Python\Doc\claw-code-main) (Claude Code Rust 移植版) 架构，重构 AI Agent 的上下文处理系统。
> **风格**：过关斩将，每一关都有明确的 Boss（目标）、技能点（知识）、装备（代码）、验收标准。
> **前置**：已阅读过 `session/` 中的 Agent 运行日志，理解当前系统的行为缺陷。

---

## 目录

1. [第零关：铸剑——环境准备](#第零关铸剑环境准备)
2. [第一关：观局——认识循环与架构差异](#第一关观局认识循环与架构差异)
3. [第二关：立法——定义消息模型](#第二关立法定义消息模型)
4. [第三关：记账——Token 用量追踪](#第三关记账户头-用量追踪)
5. [第四关：瘦身——上下文压缩](#第四关瘦身上下文压缩)
6. [第五关：织网——提示词构建器](#第五关织网提示词构建器)
7. [第六关：引擎——运行时引擎](#第六关引擎运行时引擎)
8. [第七关：归档——会话持久化](#第七关归档会话持久化)
9. [第八关：融合——集成到现有系统](#第八关融合集成到现有系统)
10. [最终 BOSS：自测清单](#最终-boss自测清单)

---

## 第零关：铸剑——环境准备

### Boss

理解当前系统的问题根源，确认目标架构。

### 技能点

- 当前 `ChatAgent` 的 `think→execute→reflect` 循环每步产生 1~2 次 LLM 调用
- `reflect()` 的结果写入 `history` 但**永不进入下次 prompt**（见 `chat_agent.py` 的 `_format_history()`）
- 历史格式混用 `{input,output,reflect,failed}` 和 `{role,content}` 两种结构
- `_format_history(max_chars=6000)` 直接丢弃超长消息，无摘要替代
- 社区标准做法（claw-code）：事件驱动循环、结构化消息、自动压缩

### 装备

```
# 确认当前文件结构
core/
├── agent/
│   ├── chat_agent.py    # 要改造的目标
│   └── memory.py        # 旧格式兼容层
├── prompt/
│   └── templates.py     # 4 个硬编码 f-string
├── llm/
│   └── client.py        # 返回 token 数但未被使用
└── tools/
    ├── __init__.py      # TOOL_REGISTRY 纯文本描述
    └── tools.py         # 工具实现

# 重构后目标结构
core/
├── context/             # [新] 消息模型 + 压缩 + 持久化
│   ├── models.py
│   ├── session.py
│   ├── compaction.py
│   ├── history.py
│   └── transcript.py
├── prompt/
│   ├── builder.py       # [改] SystemPromptBuilder
│   └── sections.py      # [新] 各节模板
└── runtime/             # [新] 引擎 + 用量追踪
    ├── engine.py
    └── usage_tracker.py
```

### 验收

- 能口述当前系统 5 个以上问题
- 能用一句话说清 claw-code 的核心循环和当前循环的区别

---

## 第一关：观局——认识循环与架构差异

### Boss

对比分析当前 `think→execute→reflect` 与 claw-code `run_turn` 的核心差异，明确要改什么。

### 技能点

**当前循环流程**：
```
用户输入 → step()
  ┌──────────┐    ┌───────────┐
  │ think()  │───→│ execute() │──┐
  │ (LLM  1) │    │ (调一个  ) │  │
  └──────────┘    └───────────┘  │
                    ┌─────────────┘
                    ▼
         ┌─────────┴──────┐
         │ reflect()      │ ← 条件: 失败/关键工具/每5步
         │ (LLM  2)       │
         │ 结果→但不用    │
         └────────────────┘
```

**Claw-Code 循环**：
```
用户输入 → run_turn()
  ┌──────────────────────────────┐
  │ 1. api_client.stream()       │
  │    → TextDelta / ToolUse[]   │ ← 可多个工具
  │    → Usage / MessageStop     │
  │ 2. 追加 assistant 消息       │
  │ 3. 无 ToolUse → 退出         │
  │ 4. 遍历 ToolUse[]:           │
  │    权限检查 → pre-hook       │
  │    → 执行 → post-hook        │
  │    → 追加 ToolResult         │
  │ 5. maybe_auto_compact()      │
  └──────────────────────────────┘
```

### 装备

**四大决策**：

| 决策 | 当前 | 改进后 |
|------|------|--------|
| 去掉 reflect() | 每步 2 次 LLM 调用，reflect 结果浪费 | 工具结果自然流入下轮推理，隐式反射 |
| 批量工具调用 | 每次只能调一个工具 | 单次返回多个 ToolUse blocks |
| 结构化消息 | 扁平 dict，无法关联 tool_use→result | `tool_use_id` 精确匹配 |
| 权限 + 钩子 | 无安全边界 | PermissionMode + Pre/Post 钩子 |

### 验收

- 能画出两个循环的对比图
- 能说出为什么当前 `reflect()` 是浪费（答案：结果存了但 _format_history 不输出）
- 理解 "隐式反射" 的含义

---

## 第二关：立法——定义消息模型

### Boss

创建类型化消息模型，替代当前的扁平 dict 历史格式。

### 技能点

- `Enum` 定义角色和内容块类型
- `@dataclass` 定义不可变/半不可变数据结构
- `ContentBlock` 的三种变体：Text / ToolUse / ToolResult
- `tool_use_id` 是关联工具调用和结果的关键

### 装备

写入 `core/context/models.py`：

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ContentBlockType(Enum):
    TEXT = "text"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"


@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class ContentBlock:
    type: ContentBlockType
    text: str = ""
    tool_use_id: str = ""
    tool_name: str = ""
    tool_input: str = ""
    tool_output: str = ""
    is_error: bool = False


@dataclass
class ConversationMessage:
    role: MessageRole
    blocks: list[ContentBlock] = field(default_factory=list)
    usage: Optional[TokenUsage] = None


@dataclass
class Session:
    version: int = 2
    messages: list[ConversationMessage] = field(default_factory=list)
```

### 验收

```python
# 运行以下验证
from core.context.models import *

msg = ConversationMessage(
    role=MessageRole.ASSISTANT,
    blocks=[
        ContentBlock(type=ContentBlockType.TEXT, text="我来查一下"),
        ContentBlock(type=ContentBlockType.TOOL_USE, tool_use_id="t1",
                     tool_name="shell", tool_input='{"command":"echo hi"}'),
    ]
)
assert msg.role == MessageRole.ASSISTANT
assert len(msg.blocks) == 2
assert msg.blocks[1].tool_name == "shell"
print("消息模型 OK")
```

---

## 第三关：记账——Token 用量追踪

### Boss

记录每轮对话消耗的 token 数，为自动压缩提供触发条件。

### 技能点

- 累积用量 vs 单次用量
- `UsageTracker` 从 Session 中恢复历史用量
- 触发的关键是 `cumulative.input_tokens >= threshold`

### 装备

写入 `core/runtime/usage_tracker.py`：

```python
from dataclasses import dataclass, field
from core.context.models import TokenUsage, Session


@dataclass
class UsageTracker:
    turns: int = 0
    cumulative: TokenUsage = field(default_factory=TokenUsage)

    @classmethod
    def from_session(cls, session: Session) -> "UsageTracker":
        tracker = cls()
        for msg in session.messages:
            if msg.usage:
                tracker.record(msg.usage)
        return tracker

    def record(self, usage: TokenUsage) -> None:
        self.turns += 1
        self.cumulative.input_tokens += usage.input_tokens
        self.cumulative.output_tokens += usage.output_tokens
        self.cumulative.cache_creation_input_tokens += usage.cache_creation_input_tokens
        self.cumulative.cache_read_input_tokens += usage.cache_read_input_tokens

    def should_auto_compact(self, threshold: int = 200_000) -> bool:
        return self.cumulative.input_tokens >= threshold
```

### 验收

```python
tracker = UsageTracker()
tracker.record(TokenUsage(input_tokens=100, output_tokens=20))
tracker.record(TokenUsage(input_tokens=200, output_tokens=40))
assert tracker.cumulative.input_tokens == 300
assert tracker.cumulative.output_tokens == 60
assert not tracker.should_auto_compact(1000)
assert tracker.should_auto_compact(200)
print("用量追踪 OK")
```

---

## 第四关：瘦身——上下文压缩

### Boss

实现智能上下文压缩：丢弃旧消息时生成结构化摘要，而不是直接丢弃。

### 技能点

- `compact_session()` 把 `preserve_recent_messages` 之前的消息替换为一条 `System` 消息
- 摘要包含：统计、工具列表、最近用户请求、待办工作、关键文件、时间线
- 自动压缩：每轮交互后检查累积 token 是否超阈值

### 装备

写入 `core/context/compaction.py`：

```python
from dataclasses import dataclass, field
from core.context.models import *


@dataclass
class CompactionConfig:
    preserve_recent_messages: int = 6
    max_estimated_tokens: int = 10_000
    auto_compact_input_threshold: int = 200_000


@dataclass
class CompactionResult:
    summary: str
    formatted_summary: str
    compacted_session: Session
    removed_message_count: int


def estimate_tokens(session: Session) -> int:
    total = 0
    for msg in session.messages:
        for block in msg.blocks:
            text = ""
            if block.type == ContentBlockType.TEXT:
                text = block.text
            elif block.type == ContentBlockType.TOOL_USE:
                text = block.tool_name + block.tool_input
            elif block.type == ContentBlockType.TOOL_RESULT:
                text = block.tool_name + block.tool_output
            total += len(text) // 4 + 1
    return total


def should_compact(session: Session, config: CompactionConfig) -> bool:
    return (len(session.messages) > config.preserve_recent_messages
            and estimate_tokens(session) >= config.max_estimated_tokens)


def compact_session(session: Session, config: CompactionConfig) -> CompactionResult:
    if not should_compact(session, config):
        return CompactionResult(
            summary="", formatted_summary="",
            compacted_session=session, removed_message_count=0
        )

    keep_from = len(session.messages) - config.preserve_recent_messages
    removed = session.messages[:keep_from]
    preserved = session.messages[keep_from:]

    summary_lines = [
        "<summary>",
        "Conversation summary:",
        f"- Scope: {len(removed)} earlier messages compacted.",
    ]

    tools_used = set()
    for msg in removed:
        for block in msg.blocks:
            if block.type in (ContentBlockType.TOOL_USE, ContentBlockType.TOOL_RESULT):
                tools_used.add(block.tool_name)
    if tools_used:
        summary_lines.append(f"- Tools used: {', '.join(sorted(tools_used))}.")

    user_requests = [
        b.text for msg in removed if msg.role == MessageRole.USER
        for b in msg.blocks if b.type == ContentBlockType.TEXT
    ][-3:]
    if user_requests:
        summary_lines.append("- Recent user requests:")
        for req in user_requests:
            summary_lines.append(f"  - {req[:160]}")

    key_files = set()
    for msg in removed:
        for block in msg.blocks:
            for token in block.text.split():
                if "/" in token and "." in token:
                    key_files.add(token.strip(",:;\"'`"))
    if key_files:
        summary_lines.append(f"- Key files: {', '.join(list(key_files)[:8])}.")
    summary_lines.append("</summary>")

    summary = "\n".join(summary_lines)
    continuation = (
        f"Previous conversation context compressed.\n\n{summary}\n\n"
        "Continue without acknowledging this summary."
    )
    compacted_messages = [
        ConversationMessage(role=MessageRole.SYSTEM,
                            blocks=[ContentBlock(type=ContentBlockType.TEXT,
                                                  text=continuation)])
    ]
    compacted_messages.extend(preserved)

    return CompactionResult(
        summary=summary,
        formatted_summary=summary,
        compacted_session=Session(version=session.version, messages=compacted_messages),
        removed_message_count=len(removed),
    )
```

### 验收

```python
session = Session(messages=[
    ConversationMessage(role=MessageRole.USER,
        blocks=[ContentBlock(type=ContentBlockType.TEXT, text="帮我查天气")]),
    ConversationMessage(role=MessageRole.ASSISTANT,
        blocks=[ContentBlock(type=ContentBlockType.TEXT, text="好的")]),
    ConversationMessage(role=MessageRole.USER,
        blocks=[ContentBlock(type=ContentBlockType.TEXT, text="再查一下")]),
])

result = compact_session(session, CompactionConfig(
    preserve_recent_messages=1, max_estimated_tokens=1
))
assert result.removed_message_count == 2
assert result.compacted_session.messages[0].role == MessageRole.SYSTEM
print("压缩 OK")
```

---

## 第五关：织网——提示词构建器

### Boss

用组合式 Builder 替代 4 个硬编码 f-string，支持动态注入项目上下文、git 状态、指令文件。

### 技能点

- `SystemPromptBuilder` 以节为单位构建提示词
- 指令文件发现：从 CWD 向上搜索 `CLAUDE.md` → `CLAUDE.local.md` → `.claude/CLAUDE.md` → `.claude/instructions.md`
- 去重依据：内容 hash
- 预算限制：总 12K 字符，单文件最多 4K 字符
- `__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__` 标记静态/动态边界

### 装备

写入 `core/prompt/sections.py`：

```python
SYSTEM_PROMPT_DYNAMIC_BOUNDARY = "__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__"

INTRO_SECTION = """\
你是 MARS AI Agent，能处理文件操作、代码分析、shell命令和网络搜索任务。
使用 instructions 和 tools 中提供的工具完成用户请求。\
"""

SYSTEM_RULES_SECTION = """\
## 核心规则
1. 使用 tools 描述中提供的工具，参数必须准确完整
2. 每次操作后验证结果，失败则分析原因调整策略
3. 当前运行在 Windows 环境，shell 命令优先用 PowerShell
4. 绝不伪造运行结果，不假设未验证的文件内容\
"""

TASK_GUIDELINES_SECTION = """\
## 做事准则
- 修改代码前先读取相关部分
- 不添加推测性的抽象层或不相关清理
- 不创建任务不需要的文件
- 如果方法失败，诊断后再切换策略
- 如实报告结果：如果验证失败或未运行，要明确说明\
"""
```

写入 `core/prompt/builder.py`：

```python
from pathlib import Path
from typing import Optional
from core.prompt.sections import *

@dataclass
class ContextFile:
    path: Path
    content: str

@dataclass
class ProjectContext:
    cwd: Path
    current_date: str
    git_status: Optional[str] = None
    git_diff: Optional[str] = None
    instruction_files: list[ContextFile] = field(default_factory=list)


class SystemPromptBuilder:
    sections: list[str] = field(default_factory=list)

    def add_intro(self) -> "SystemPromptBuilder":
        self.sections.append(INTRO_SECTION); return self

    def add_system_rules(self) -> "SystemPromptBuilder":
        self.sections.append(SYSTEM_RULES_SECTION); return self

    def add_task_guidelines(self) -> "SystemPromptBuilder":
        self.sections.append(TASK_GUIDELINES_SECTION); return self

    def add_dynamic_boundary(self) -> "SystemPromptBuilder":
        self.sections.append(SYSTEM_PROMPT_DYNAMIC_BOUNDARY); return self

    def add_environment(self, cwd: str, date: str, os_name: str = "windows",
                        os_version: str = "") -> "SystemPromptBuilder":
        self.sections.append("\n".join([
            "# Environment",
            f"- Working directory: {cwd}",
            f"- Date: {date}",
            f"- Platform: {os_name} {os_version}",
        ]))
        return self

    def add_project_context(self, project: ProjectContext) -> "SystemPromptBuilder":
        lines = ["# Project context", f"- Working directory: {project.cwd}"]
        if project.git_status:
            lines.append(f"\nGit status:\n{project.git_status}")
        if project.git_diff:
            lines.append(f"\nGit diff:\n{project.git_diff}")
        self.sections.append("\n".join(lines))
        return self

    def add_instruction_files(self, files: list[ContextFile]) -> "SystemPromptBuilder":
        if not files:
            return self
        lines = ["# Instructions"]
        remaining = 12_000
        for f in files:
            if remaining <= 0:
                lines.append("[Additional instruction content omitted]")
                break
            content = f.content[:min(4000, remaining)]
            lines.append(f"## {f.path.name}\n{content}")
            remaining -= len(content)
        self.sections.append("\n".join(lines))
        return self

    def build(self) -> list[str]:
        return self.sections

    def render(self) -> str:
        return "\n\n".join(self.sections)
```

### 验收

```python
prompt = (SystemPromptBuilder()
    .add_intro()
    .add_system_rules()
    .add_dynamic_boundary()
    .add_environment(cwd="/home/project", date="2026-05-16")
    .render())
assert "MARS AI Agent" in prompt
assert "__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__" in prompt
assert "2026-05-16" in prompt
print("提示词构建器 OK")
```

---

## 第六关：引擎——运行时引擎

### Boss

实现 `ConversationRuntime`，管理一轮对话的完整生命周期：API 调用 → 工具执行 → 权限检查 → 钩子 → 自动压缩。

### 技能点

- 事件驱动循环：`api_client.stream()` 返回事件流，解析为 `AssistantEvent`
- 一个 assistant 消息可包含多个 `ToolUse` blocks → 批量执行
- 权限模型：每个工具声明 `PermissionMode`，运行时检查当前模式
- Hook 系统：PreToolUse / PostToolUse，可拦截或修改工具行为
- 自动压缩：每轮结束后检查累积 token 阈值

### 装备

写入 `core/runtime/engine.py`：

```python
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum, auto
from core.context.models import *
from core.context.compaction import *
from core.runtime.usage_tracker import UsageTracker


class PermissionMode(Enum):
    READ_ONLY = auto()
    WORKSPACE_WRITE = auto()
    DANGER_FULL_ACCESS = auto()
    ALLOW = auto()


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict
    required_permission: PermissionMode = PermissionMode.DANGER_FULL_ACCESS
    execute_fn: Optional[Callable] = None


@dataclass
class TurnSummary:
    assistant_messages: list[ConversationMessage]
    tool_results: list[ConversationMessage]
    iterations: int
    usage: TokenUsage
    auto_compaction: Optional[CompactionResult] = None


class ConversationRuntime:
    def __init__(self, session: Session, system_prompt: list[str],
                 tools: dict[str, ToolSpec],
                 permission_mode: PermissionMode = PermissionMode.WORKSPACE_WRITE,
                 compaction_config: Optional[CompactionConfig] = None):
        self.session = session
        self.system_prompt = system_prompt
        self.tools = tools
        self.permission_mode = permission_mode
        self.usage_tracker = UsageTracker.from_session(session)
        self.max_iterations = 20
        self.compaction_config = compaction_config or CompactionConfig()
        self.pre_hooks: list[Callable] = []
        self.post_hooks: list[Callable] = []

    def add_pre_hook(self, hook: Callable) -> None:
        self.pre_hooks.append(hook)

    def add_post_hook(self, hook: Callable) -> None:
        self.post_hooks.append(hook)

    def check_permission(self, tool_name: str) -> bool:
        spec = self.tools.get(tool_name)
        if not spec:
            return False
        required = spec.required_permission
        if self.permission_mode == PermissionMode.ALLOW:
            return True
        if required == PermissionMode.READ_ONLY:
            return True
        if required == PermissionMode.WORKSPACE_WRITE:
            return self.permission_mode in (
                PermissionMode.WORKSPACE_WRITE, PermissionMode.DANGER_FULL_ACCESS)
        if required == PermissionMode.DANGER_FULL_ACCESS:
            return self.permission_mode == PermissionMode.DANGER_FULL_ACCESS
        return False

    def run_turn(self, user_input: str,
                 api_stream: Callable) -> TurnSummary:
        self.session.messages.append(
            ConversationMessage(role=MessageRole.USER,
                blocks=[ContentBlock(type=ContentBlockType.TEXT, text=user_input)]))

        assistant_msgs = []
        tool_results = []
        iterations = 0

        while iterations < self.max_iterations:
            iterations += 1

            # 1. Call API → get events
            events = api_stream(self.system_prompt, self.session.messages)

            # 2. Parse assistant message
            text_parts = []
            tool_uses = []
            usage = None
            for event in events:
                if event["type"] == "text":
                    text_parts.append(event["delta"])
                elif event["type"] == "tool_use":
                    tool_uses.append(event)
                elif event["type"] == "usage":
                    usage = TokenUsage(**event["data"])
                elif event["type"] == "stop":
                    break

            blocks = []
            if text_parts:
                blocks.append(ContentBlock(
                    type=ContentBlockType.TEXT,
                    text="".join(text_parts)))
            for tu in tool_uses:
                blocks.append(ContentBlock(
                    type=ContentBlockType.TOOL_USE,
                    tool_use_id=tu["id"],
                    tool_name=tu["name"],
                    tool_input=tu["input"]))

            msg = ConversationMessage(
                role=MessageRole.ASSISTANT, blocks=blocks, usage=usage)
            if usage:
                self.usage_tracker.record(usage)
            self.session.messages.append(msg)
            assistant_msgs.append(msg)

            if not tool_uses:
                break

            # 4. Execute each tool
            for tu in tool_uses:
                tid, tname, tinput = tu["id"], tu["name"], tu["input"]

                # Permission
                if not self.check_permission(tname):
                    result_msg = ConversationMessage.tool_result(
                        tid, tname, f"Permission denied for {tname}", True)
                    self.session.messages.append(result_msg)
                    tool_results.append(result_msg)
                    continue

                # Pre-hooks
                hook_denied = False
                for hook in self.pre_hooks:
                    r = hook(tname, tinput)
                    if r is False:
                        result_msg = ConversationMessage.tool_result(
                            tid, tname, f"Pre-hook denied {tname}", True)
                        self.session.messages.append(result_msg)
                        tool_results.append(result_msg)
                        hook_denied = True
                        break
                if hook_denied:
                    continue

                # Execute
                spec = self.tools.get(tname)
                is_error = False
                output = ""
                if spec and spec.execute_fn:
                    try:
                        output = str(spec.execute_fn(**eval(tinput)))
                    except Exception as e:
                        output = str(e)
                        is_error = True
                else:
                    output = f"No handler for {tname}"
                    is_error = True

                # Post-hooks
                for hook in self.post_hooks:
                    hook(tname, tinput, output, is_error)

                result_msg = ConversationMessage(
                    role=MessageRole.TOOL,
                    blocks=[ContentBlock(
                        type=ContentBlockType.TOOL_RESULT,
                        tool_use_id=tid, tool_name=tname,
                        tool_output=output, is_error=is_error)])
                self.session.messages.append(result_msg)
                tool_results.append(result_msg)

        # Auto-compaction
        auto_comp = None
        if self.usage_tracker.should_auto_compact(
                self.compaction_config.auto_compact_input_threshold):
            r = compact_session(self.session, self.compaction_config)
            if r.removed_message_count > 0:
                self.session = r.compacted_session
                auto_comp = r

        return TurnSummary(
            assistant_messages=assistant_msgs,
            tool_results=tool_results,
            iterations=iterations,
            usage=self.usage_tracker.cumulative,
            auto_compaction=auto_comp)
```

### 验收

```python
# 这个不能独立运行（需要 mock API），但可以验证导入
from core.runtime.engine import ConversationRuntime, PermissionMode, ToolSpec
assert ConversationRuntime is not None
print("引擎模块导入 OK")
```

---

## 第七关：归档——会话持久化

### Boss

实现版本化会话 JSON 持久化，支持旧格式迁移。

### 技能点

- 版本号控制格式演进
- `save_session()` / `load_session()` 对称序列化
- `migrate_v1_to_v2()` 将旧 `{input,output,reflect}` 格式转为新 `MessageRole` 格式

### 装备

写入 `core/context/session.py`：

```python
import json
from pathlib import Path
from core.context.models import *


def message_to_dict(msg: ConversationMessage) -> dict:
    d = {"role": msg.role.value, "blocks": []}
    for b in msg.blocks:
        bd = {"type": b.type.value}
        if b.type == ContentBlockType.TEXT:
            bd["text"] = b.text
        elif b.type == ContentBlockType.TOOL_USE:
            bd.update(tool_use_id=b.tool_use_id, tool_name=b.tool_name,
                      tool_input=b.tool_input)
        elif b.type == ContentBlockType.TOOL_RESULT:
            bd.update(tool_use_id=b.tool_use_id, tool_name=b.tool_name,
                      tool_output=b.tool_output, is_error=b.is_error)
        d["blocks"].append(bd)
    if msg.usage:
        d["usage"] = {"input_tokens": msg.usage.input_tokens,
                      "output_tokens": msg.usage.output_tokens}
    return d


def message_from_dict(d: dict) -> ConversationMessage:
    role = MessageRole(d["role"])
    blocks = []
    for bd in d["blocks"]:
        bt = ContentBlockType(bd["type"])
        kwargs = {"type": bt}
        if bt == ContentBlockType.TEXT:
            kwargs["text"] = bd.get("text", "")
        elif bt == ContentBlockType.TOOL_USE:
            kwargs.update(tool_use_id=bd["tool_use_id"],
                          tool_name=bd["tool_name"],
                          tool_input=bd["tool_input"])
        elif bt == ContentBlockType.TOOL_RESULT:
            kwargs.update(tool_use_id=bd["tool_use_id"],
                          tool_name=bd["tool_name"],
                          tool_output=bd.get("tool_output", ""),
                          is_error=bd.get("is_error", False))
        blocks.append(ContentBlock(**kwargs))
    usage = None
    if "usage" in d:
        usage = TokenUsage(**d["usage"])
    return ConversationMessage(role=role, blocks=blocks, usage=usage)


def save_session(session: Session, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "version": session.version,
        "messages": [message_to_dict(m) for m in session.messages],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def load_session(path: Path) -> Session:
    data = json.loads(path.read_text(encoding="utf-8"))
    version = data.get("version", 1)
    if version == 1:
        return migrate_v1_to_v2(data)
    return Session(
        version=version,
        messages=[message_from_dict(m) for m in data["messages"]],
    )


def migrate_v1_to_v2(old: dict) -> Session:
    """旧格式: {"history": [{"role":"user","content":"..."},
                            {"input":...,"output":...,"reflect":...,"failed":F}]}"""
    messages = []
    for entry in old.get("history", []):
        if "role" in entry and entry["role"] == "user":
            messages.append(ConversationMessage(
                role=MessageRole.USER,
                blocks=[ContentBlock(type=ContentBlockType.TEXT,
                                      text=entry.get("content", ""))]))
        elif "input" in entry:
            inp = entry["input"]
            tool = inp.get("tool", "")
            args = inp.get("tool_args", {})
            out = entry.get("output", "")
            failed = entry.get("failed", False)
            if tool in ("talk", "finish"):
                messages.append(ConversationMessage(
                    role=MessageRole.ASSISTANT,
                    blocks=[ContentBlock(type=ContentBlockType.TEXT, text=out)]))
            else:
                messages.append(ConversationMessage(
                    role=MessageRole.ASSISTANT,
                    blocks=[ContentBlock(type=ContentBlockType.TOOL_USE,
                                          tool_name=tool,
                                          tool_input=str(args))]))
                messages.append(ConversationMessage(
                    role=MessageRole.TOOL,
                    blocks=[ContentBlock(type=ContentBlockType.TOOL_RESULT,
                                          tool_name=tool,
                                          tool_output=out,
                                          is_error=failed)]))
    return Session(version=2, messages=messages)
```

### 验收

```python
from pathlib import Path
import tempfile

session = Session(messages=[
    ConversationMessage(role=MessageRole.USER,
        blocks=[ContentBlock(type=ContentBlockType.TEXT, text="hello")])
])
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "test.json"
    save_session(session, p)
    loaded = load_session(p)
    assert loaded.version == 2
    assert loaded.messages[0].role == MessageRole.USER
    assert loaded.messages[0].blocks[0].text == "hello"
print("会话持久化 OK")
```

---

## 第八关：融合——集成到现有系统

### Boss

将新模块集成到 `ChatAgent` 和 `main.py`，保持向后兼容。

### 技能点

- `ChatAgent` 作为适配层：新代码走 `ConversationRuntime`，旧接口保持可用
- `Memory` 类标记为 `@deprecated`，内部委托给 `Session`
- `main.py` 双模式：无参数继续用旧行为，传 `--v2` 启用新引擎
- 旧 session 文件自动迁移

### 装备

`ChatAgent` 改造要点：

```python
class ChatAgent:
    def __init__(self, user_input=None, memory=None, callbacks=None,
                 use_v2=False):    # ← 新增 use_v2 开关
        if use_v2:
            self._runtime = ConversationRuntime(
                session=Session(),
                system_prompt=["你是 MARS AI Agent..."],
                tools=build_tool_specs(),
            )
        else:
            # 保持旧行为
            ...

    def run(self):
        if hasattr(self, "_runtime"):
            summary = self._runtime.run_turn(
                user_input=self.user_input,
                api_stream=self._build_api_stream(),
            )
            return summary
        # 旧循环
        ...
```

`main.py` 改造：

```python
def run_interactive_mode(verbose=False, use_v2=False):
    agent = ChatAgent(user_input="", use_v2=use_v2)
    while True:
        user_input = input("\nYou: ").strip()
        agent.user_input = user_input
        if use_v2:
            agent.run()  # 走新引擎 v2
        else:
            agent.run()  # 旧兼容模式
```

### 验收

- 旧 session 文件可加载（自动迁移）
- `ChatAgent(callbacks=...)` 可在 CLI 和 GUI 间切换输出
- `use_v2=True` 时走新引擎，`use_v2=False` 时行为不变

---

## 最终 BOSS：自测清单

用这个清单确认所有关卡都通过了：

### 第零关：问题理解
- [ ] 能列举当前系统至少 5 个问题
- [ ] 能用一句话说明重构目标和方向

### 第一关：循环对比
- [ ] 理解为什么当前 `reflect()` 是浪费
- [ ] 理解 claw-code 的单 API 调用 + 多工具执行模式

### 第二关：消息模型
- [ ] `core/context/models.py` 创建完成
- [ ] 能构造 `ConversationMessage` 并访问其字段
- [ ] 理解 `tool_use_id` 的作用

### 第三关：用量追踪
- [ ] `core/runtime/usage_tracker.py` 创建完成
- [ ] 能从 Session 恢复历史用量
- [ ] 能根据阈值判断是否触发压缩

### 第四关：上下文压缩
- [ ] `core/context/compaction.py` 创建完成
- [ ] 压缩后 System 消息包含结构化摘要
- [ ] 压缩前后 token 数减少

### 第五关：提示词构建器
- [ ] `core/prompt/builder.py` + `sections.py` 创建完成
- [ ] 能组合不同节生成提示词
- [ ] 支持注入环境信息

### 第六关：运行时引擎
- [ ] `core/runtime/engine.py` 创建完成
- [ ] `run_turn()` 的循环逻辑正确
- [ ] 权限检查和钩子机制可用

### 第七关：会话持久化
- [ ] `core/context/session.py` 创建完成
- [ ] 新格式存 → 读回 → 数据一致
- [ ] 旧 `session/*.json` 可迁移为 v2 格式

### 第八关：系统集成
- [ ] CLI `python main.py` 正常运行（兼容模式）
- [ ] 旧 session 文件加载不报错
- [ ] GUI Worker 通过 callbacks 使用新引擎

---

## 参考来源

| 文件 | 内容 |
|------|------|
| `claw-code-main/rust/crates/runtime/src/session.rs` | 消息模型（MessageRole, ContentBlock, Session） |
| `claw-code-main/rust/crates/runtime/src/conversation.rs` | 运行时引擎（ConversationRuntime, run_turn） |
| `claw-code-main/rust/crates/runtime/src/compact.rs` | 上下文压缩（CompactionConfig, compact_session） |
| `claw-code-main/rust/crates/runtime/src/prompt.rs` | 提示词构建器（SystemPromptBuilder, ProjectContext） |
| `claw-code-main/rust/crates/runtime/src/usage.rs` | Token 用量追踪（UsageTracker） |
| `claw-code-main/rust/crates/runtime/src/hooks.rs` | Pre/Post ToolUse 钩子系统（HookRunner） |
| `claw-code-main/rust/crates/runtime/src/permissions.rs` | 权限模型（PermissionPolicy, PermissionMode） |
| `claw-code-main/rust/crates/tools/src/lib.rs` | 工具定义（ToolSpec, input_schema JSON Schema） |
