from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List, Optional


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ContentBlockType(str, Enum):
    TEXT = "text"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"


@dataclass
class TextBlock:
    text: str


@dataclass
class ToolUse:
    id: str
    name: str
    input: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    tool_use_id: str
    content: str
    is_error: bool = False


ContentBlock = TextBlock | ToolUse | ToolResult


@dataclass
class ConversationMessage:
    role: MessageRole
    blocks: List[ContentBlock] = field(default_factory=list)
    usage: Optional['TokenUsage'] = None

    @staticmethod
    def user_text(text: str) -> 'ConversationMessage':
        return ConversationMessage(role=MessageRole.USER, blocks=[TextBlock(text=text)])

    @staticmethod
    def assistant(blocks: List[ContentBlock], usage: Optional['TokenUsage'] = None) -> 'ConversationMessage':
        return ConversationMessage(role=MessageRole.ASSISTANT, blocks=blocks, usage=usage)

    @staticmethod
    def tool_result(tool_use_id: str, content: str, is_error: bool = False) -> 'ConversationMessage':
        return ConversationMessage(
            role=MessageRole.TOOL,
            blocks=[ToolResult(tool_use_id=tool_use_id, content=str(content), is_error=is_error)]
        )

    @property
    def text_blocks(self) -> List[str]:
        return [b.text for b in self.blocks if isinstance(b, TextBlock)]

    @property
    def tool_uses(self) -> List[ToolUse]:
        return [b for b in self.blocks if isinstance(b, ToolUse)]

    @property
    def tool_results(self) -> List[ToolResult]:
        return [b for b in self.blocks if isinstance(b, ToolResult)]


@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0

    def __add__(self, other: 'TokenUsage') -> 'TokenUsage':
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cache_read_input_tokens=self.cache_read_input_tokens + other.cache_read_input_tokens,
            cache_creation_input_tokens=self.cache_creation_input_tokens + other.cache_creation_input_tokens,
        )

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class ApiRequest:
    model: str
    messages: List[ConversationMessage]
    system: str = ""
    max_tokens: int = 4096
    tools: List[ToolDefinition] = field(default_factory=list)


@dataclass
class AssistantEvent:
    type: str

    @classmethod
    def text_delta(cls, text: str) -> 'AssistantEvent':
        return cls(type="text_delta", text=text)  # type: ignore

    @classmethod
    def tool_use(cls, id: str, name: str, input: Dict[str, Any]) -> 'AssistantEvent':
        return cls(type="tool_use", id=id, name=name, input=input)  # type: ignore


@dataclass
class TurnSummary:
    assistant_messages: List[ConversationMessage] = field(default_factory=list)
    usage: TokenUsage = field(default_factory=TokenUsage)
    iterations: int = 0
    finished: bool = False
