from typing import List
from core.runtime.types import ConversationMessage, MessageRole, TextBlock, ToolUse, TokenUsage
from core.runtime.usage import estimate_tokens


class SessionCompactor:
    def __init__(self, auto_threshold_tokens: int = 50000,
                 preserve_recent: int = 4):
        self.threshold = auto_threshold_tokens
        self.preserve_recent = preserve_recent

    def should_compact(self, usage: TokenUsage) -> bool:
        return usage.input_tokens >= self.threshold

    def compact(self, messages: List[ConversationMessage]) -> List[ConversationMessage]:
        if len(messages) <= self.preserve_recent:
            return messages

        to_summarize = messages[:-self.preserve_recent]
        preserved = messages[-self.preserve_recent:]

        summary = self._generate_summary(to_summarize)
        summary_msg = ConversationMessage(
            role=MessageRole.SYSTEM,
            blocks=[TextBlock(text=f"<summary>\n{summary}\n</summary>")]
        )

        return [summary_msg] + preserved

    def _generate_summary(self, messages: List[ConversationMessage]) -> str:
        user_msgs = 0
        assistant_msgs = 0
        tool_keys = set()

        for msg in messages:
            if msg.role == MessageRole.USER:
                user_msgs += 1
            elif msg.role == MessageRole.ASSISTANT:
                assistant_msgs += 1
                for block in msg.tool_uses:
                    tool_keys.add(block.name)

        return (
            f"压缩了 {user_msgs} 条用户消息, {assistant_msgs} 条助手消息, "
            f"涉及工具: {', '.join(sorted(tool_keys)) if tool_keys else '无'}"
        )
