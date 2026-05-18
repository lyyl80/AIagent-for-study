from typing import Dict, Any, Optional, List, Set, Tuple, Callable
from dataclasses import dataclass, field
import ast
import time

from core.runtime.types import (
    ConversationMessage, MessageRole, TextBlock, ToolUse, ToolResult,
    ContentBlock, TokenUsage, AssistantEvent, TurnSummary,
    ApiRequest, ToolDefinition, ContentBlockType
)
from core.runtime.usage import UsageTracker
from core.runtime.permissions import PermissionPolicy
from core.runtime.compact import SessionCompactor


def _safe_parse_args(args_raw):
    if isinstance(args_raw, dict):
        return args_raw
    try:
        return ast.literal_eval(args_raw)
    except (ValueError, SyntaxError):
        return {}


def memory_to_runtime_messages(history: list) -> List[ConversationMessage]:
    """将 Memory.history 转换为 ConversationMessage 列表（保持时间顺序）"""
    messages: List[ConversationMessage] = []
    for entry in history:
        if "input" in entry:
            tool = entry["input"].get("tool", "")
            args_raw = entry["input"].get("tool_args", {})
            output = entry.get("output", "")
            is_error = entry.get("failed", False) or (
                isinstance(output, str) and output.startswith("Error:")
            )

            if tool in ("talk", "finish"):
                messages.append(ConversationMessage.assistant([
                    TextBlock(text=output)
                ]))
            elif tool == "user":
                args = _safe_parse_args(args_raw)
                msg = args.get("message", output) if isinstance(args, dict) else str(args_raw)
                messages.append(ConversationMessage.user_text(msg or output))
            else:
                args = _safe_parse_args(args_raw)
                tool_id = f"tu_{hash(str(args_raw))}_p{len(messages)}"
                messages.append(ConversationMessage.assistant([
                    ToolUse(id=tool_id, name=tool, input=args)
                ]))
                messages.append(ConversationMessage.tool_result(
                    tool_id, output, is_error=is_error
                ))
        else:
            role = entry.get("role", "")
            content = entry.get("content", "")
            if role == "user":
                messages.append(ConversationMessage.user_text(content))
            elif role == "assistant":
                messages.append(ConversationMessage.assistant([
                    TextBlock(text=content)
                ]))
    return messages


@dataclass
class ConversationRuntime:
    messages: List[ConversationMessage] = field(default_factory=list)
    system_prompt: str = ""
    max_iterations: int = 100
    usage_tracker: UsageTracker = field(default_factory=UsageTracker)
    permission_policy: PermissionPolicy = field(default_factory=PermissionPolicy)
    compactor: SessionCompactor = field(default_factory=SessionCompactor)
    allowed_tools: Optional[Set[str]] = None

    def __post_init__(self):
        self._last_tool_steps: List[Tuple[str, str]] = []

    def run_turn(self, user_input: str, api_client, tool_executor,
                 on_text: Optional[Callable[[str], None]] = None,
                 on_tool: Optional[Callable[[str, Dict, str, bool], None]] = None,
                 on_save: Optional[Callable[[str, str], None]] = None) -> TurnSummary:
        self.messages.append(ConversationMessage.user_text(user_input))
        if on_save:
            on_save("user", user_input)
        total_usage = TokenUsage()

        for iteration in range(1, self.max_iterations + 1):
            request = ApiRequest(
                model=api_client.model,
                messages=self.messages,
                system=self.system_prompt,
                tools=api_client.get_tool_definitions() if self.allowed_tools is None else [
                    t for t in api_client.get_tool_definitions() if t.name in self.allowed_tools
                ],
            )

            blocks, usage = api_client.stream(request)
            total_usage += usage

            msg = ConversationMessage.assistant(blocks, usage)
            self.messages.append(msg)

            tool_uses = msg.tool_uses
            if not tool_uses:
                for block in msg.text_blocks:
                    if block and on_text:
                        on_text(block)
                    if on_save:
                        on_save("assistant", block)
                return TurnSummary(usage=total_usage, iterations=iteration, finished=True)

            for tool_use in tool_uses:
                self.usage_tracker.add(usage)

                permitted, reason = self.permission_policy.authorize(tool_use.name)
                if not permitted:
                    result = f"权限拒绝: {reason}"
                    is_error = True
                else:
                    result = tool_executor.execute(tool_use.name, tool_use.input)
                    is_error = isinstance(result, str) and result.startswith("Error:")

                self.messages.append(ConversationMessage.tool_result(
                    tool_use.id, str(result), is_error=is_error
                ))
                if on_tool:
                    on_tool(tool_use.name, tool_use.input, str(result), is_error)
                if on_save:
                    on_save("tool", str(result), tool_use.name, str(tool_use.input))

            if self._check_convergence(tool_uses):
                self._last_tool_steps = []
                return TurnSummary(usage=total_usage, iterations=iteration, finished=True)

            if self.compactor.should_compact(total_usage):
                self.messages = self.compactor.compact(self.messages)

        return TurnSummary(usage=total_usage, iterations=self.max_iterations, finished=True)

    def _check_convergence(self, tool_uses: List[ToolUse]) -> bool:
        for tu in tool_uses:
            key = (tu.name, str(sorted(tu.input.items())))
            self._last_tool_steps.append(key)
            if len(self._last_tool_steps) > 3:
                self._last_tool_steps.pop(0)

        if len(self._last_tool_steps) == 3 and len(set(self._last_tool_steps)) == 1:
            name = self._last_tool_steps[0][0]
            if name not in ("talk", "finish"):
                return True
        return False

    def get_history_text(self, max_chars: int = 8000) -> str:
        lines = []
        for msg in self.messages:
            if msg.role == MessageRole.USER:
                for block in msg.text_blocks:
                    lines.append(f"用户: {block}")
            elif msg.role == MessageRole.ASSISTANT:
                for block in msg.blocks:
                    if isinstance(block, ToolUse):
                        lines.append(f"工具[{block.name}] {block.input}")
                    elif isinstance(block, TextBlock):
                        lines.append(f"AI: {block.text}")
            elif msg.role == MessageRole.TOOL:
                for block in msg.tool_results:
                    out = block.content
                    if len(out) > 600:
                        out = out[:600] + f"\n... (剩余 {len(out)-600} 字符)"
                    lines.append(f"  → {'失败: ' if block.is_error else ''}{out}")

        base = "\n".join(lines)
        if len(base) <= max_chars:
            return base

        recent = []
        for line in reversed(lines):
            if len("\n".join([line] + recent)) > max_chars - 500:
                break
            recent.insert(0, line)
        return "(早期历史已省略)\n" + "\n".join(recent)
