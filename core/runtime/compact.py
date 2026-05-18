"""
会话压缩模块

当对话历史过长时，自动压缩早期消息以节省token。
保留最近的消息，将早期消息汇总为简短的系统提示。
"""
from typing import List
from core.runtime.types import ConversationMessage, MessageRole, TextBlock, ToolUse, TokenUsage
from core.runtime.usage import estimate_tokens


class SessionCompactor:
    """
    会话压缩器类
    
    监控token使用量，超过阈值时压缩历史消息。
    采用"摘要+保留最近"策略平衡上下文完整性和成本。
    
    Attributes:
        threshold (int): 触发压缩的token阈值，默认50000
        preserve_recent (int): 保留的最近消息数量，默认4条
    """
    
    def __init__(self, auto_threshold_tokens: int = 50000,
                 preserve_recent: int = 4):
        """
        初始化会话压缩器
        
        Args:
            auto_threshold_tokens (int): 自动压缩的token阈值
            preserve_recent (int): 保留的最近消息条数
        """
        self.threshold = auto_threshold_tokens
        self.preserve_recent = preserve_recent

    def should_compact(self, usage: TokenUsage) -> bool:
        """
        判断是否需要压缩
        
        Args:
            usage (TokenUsage): 当前token使用统计
            
        Returns:
            bool: 是否达到压缩阈值
        """
        return usage.input_tokens >= self.threshold

    def compact(self, messages: List[ConversationMessage]) -> List[ConversationMessage]:
        """
        执行会话压缩
        
        将早期消息替换为系统摘要消息，保留最近的preserve_recent条消息。
        
        Args:
            messages (List[ConversationMessage]): 原始消息列表
            
        Returns:
            List[ConversationMessage]: 压缩后的消息列表
        """
        # 消息太少时无需压缩
        if len(messages) <= self.preserve_recent:
            return messages

        # 分离要压缩和要保留的消息
        to_summarize = messages[:-self.preserve_recent]
        preserved = messages[-self.preserve_recent:]

        # 生成摘要并创建系统消息
        summary = self._generate_summary(to_summarize)
        summary_msg = ConversationMessage(
            role=MessageRole.SYSTEM,
            blocks=[TextBlock(text=f"<summary>\n{summary}\n</summary>")]
        )

        return [summary_msg] + preserved

    def _generate_summary(self, messages: List[ConversationMessage]) -> str:
        """
        生成消息摘要
        
        统计用户消息数、助手消息数和使用的工具类型，
        生成简洁的文本摘要（未来可扩展为LLM生成的智能摘要）。
        
        Args:
            messages (List[ConversationMessage]): 要摘要的消息列表
            
        Returns:
            str: 摘要文本
        """
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
