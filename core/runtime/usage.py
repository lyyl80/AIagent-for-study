from core.runtime.types import TokenUsage


class UsageTracker:
    def __init__(self):
        self.latest: TokenUsage = TokenUsage()
        self.cumulative: TokenUsage = TokenUsage()
        self.turns: int = 0

    def add(self, usage: TokenUsage):
        self.latest = usage
        self.cumulative += usage
        self.turns += 1

    @property
    def cumulative_input_tokens(self) -> int:
        return self.cumulative.input_tokens

    def reset(self):
        self.latest = TokenUsage()
        self.turns = 0

    def summary(self) -> str:
        return (
            f"本轮: {self.latest.total}tokens  "
            f"累计: {self.cumulative.total}tokens, {self.turns}轮"
        )


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 2)
