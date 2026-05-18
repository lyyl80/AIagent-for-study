"""
Token使用跟踪模块

跟踪和统计LLM API调用的token消耗，支持单轮和累计统计。
提供简化的token估算函数用于本地计算。
"""
from core.runtime.types import TokenUsage


class UsageTracker:
    """
    Token使用跟踪器类
    
    记录每轮对话的token使用情况，维护累计统计数据。
    
    Attributes:
        latest (TokenUsage): 最近一轮的token使用量
        cumulative (TokenUsage): 所有轮次的累计token使用量
        turns (int): 已执行的对话轮数
    """
    
    def __init__(self):
        """初始化跟踪器，所有计数器归零"""
        self.latest: TokenUsage = TokenUsage()
        self.cumulative: TokenUsage = TokenUsage()
        self.turns: int = 0

    def add(self, usage: TokenUsage):
        """
        添加一轮的token使用数据
        
        Args:
            usage (TokenUsage): 本轮的token使用统计
        """
        self.latest = usage
        self.cumulative += usage
        self.turns += 1

    @property
    def cumulative_input_tokens(self) -> int:
        """
        获取累计输入token数
        
        Returns:
            int: 累计输入token数量
        """
        return self.cumulative.input_tokens

    def reset(self):
        """重置跟踪器状态（保留cumulative）"""
        self.latest = TokenUsage()
        self.turns = 0

    def summary(self) -> str:
        """
        生成使用统计摘要字符串
        
        Returns:
            str: 格式化的统计信息，包含本轮、累计token数和轮数
        """
        return (
            f"本轮: {self.latest.total}tokens  "
            f"累计: {self.cumulative.total}tokens, {self.turns}轮"
        )


def estimate_tokens(text: str) -> int:
    """
    估算文本的token数量
    
    采用简化算法：每个字符约等于0.5个token。
    这是一个粗略估计，实际token数取决于具体的tokenizer。
    
    Args:
        text (str): 要估算的文本
        
    Returns:
        int: 估算的token数量，至少为1
    """
    return max(1, len(text) // 2)
