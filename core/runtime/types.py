"""
运行时类型定义模块

定义AI代理运行时的核心数据结构，包括：
- 消息角色和类型枚举
- 内容块（文本、工具调用、工具结果）
- 对话消息结构
- Token使用统计
- API请求格式
- 助手事件和轮次摘要

使用dataclass提供简洁的数据结构定义。
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List, Optional


class MessageRole(str, Enum):
    """
    消息角色枚举
    
    定义对话中不同参与者的角色类型。
    """
    SYSTEM = "system"      # 系统提示
    USER = "user"          # 用户输入
    ASSISTANT = "assistant"  # AI助手回复
    TOOL = "tool"          # 工具执行结果


class ContentBlockType(str, Enum):
    """
    内容块类型枚举
    
    定义消息内容的不同类型。
    """
    TEXT = "text"           # 纯文本
    TOOL_USE = "tool_use"   # 工具调用
    TOOL_RESULT = "tool_result"  # 工具结果


@dataclass
class TextBlock:
    """
    文本内容块
    
    Attributes:
        text (str): 文本内容
    """
    text: str


@dataclass
class ToolUse:
    """
    工具调用内容块
    
    表示AI决定调用的工具及其参数。
    
    Attributes:
        id (str): 工具调用的唯一标识符
        name (str): 工具名称
        input (Dict[str, Any]): 工具的输入参数字典
    """
    id: str
    name: str
    input: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """
    工具执行结果内容块
    
    存储工具执行后的返回结果。
    
    Attributes:
        tool_use_id (str): 对应的工具调用ID
        content (str): 工具执行结果的字符串表示
        is_error (bool): 是否执行失败，默认False
    """
    tool_use_id: str
    content: str
    is_error: bool = False


# 内容块的联合类型
ContentBlock = TextBlock | ToolUse | ToolResult


@dataclass
class ConversationMessage:
    """
    对话消息类
    
    表示一轮完整的对话消息，包含角色、多个内容块和使用统计。
    支持多种内容类型的混合（文本+工具调用）。
    
    Attributes:
        role (MessageRole): 消息角色
        blocks (List[ContentBlock]): 内容块列表
        usage (Optional[TokenUsage]): Token使用统计
    """
    role: MessageRole
    blocks: List[ContentBlock] = field(default_factory=list)
    usage: Optional['TokenUsage'] = None

    @staticmethod
    def user_text(text: str) -> 'ConversationMessage':
        """
        创建用户文本消息的便捷方法
        
        Args:
            text (str): 用户输入的文本
            
        Returns:
            ConversationMessage: 用户消息对象
        """
        return ConversationMessage(role=MessageRole.USER, blocks=[TextBlock(text=text)])

    @staticmethod
    def assistant(blocks: List[ContentBlock], usage: Optional['TokenUsage'] = None) -> 'ConversationMessage':
        """
        创建助手消息的便捷方法
        
        Args:
            blocks (List[ContentBlock]): 内容块列表
            usage (Optional[TokenUsage]): Token使用统计
            
        Returns:
            ConversationMessage: 助手消息对象
        """
        return ConversationMessage(role=MessageRole.ASSISTANT, blocks=blocks, usage=usage)

    @staticmethod
    def tool_result(tool_use_id: str, content: str, is_error: bool = False) -> 'ConversationMessage':
        """
        创建工具结果消息的便捷方法
        
        Args:
            tool_use_id (str): 工具调用ID
            content (str): 工具执行结果
            is_error (bool): 是否为错误结果
            
        Returns:
            ConversationMessage: 工具结果消息对象
        """
        return ConversationMessage(
            role=MessageRole.TOOL,
            blocks=[ToolResult(tool_use_id=tool_use_id, content=str(content), is_error=is_error)]
        )

    @property
    def text_blocks(self) -> List[str]:
        """
        提取所有文本块的内容
        
        Returns:
            List[str]: 文本内容列表
        """
        return [b.text for b in self.blocks if isinstance(b, TextBlock)]

    @property
    def tool_uses(self) -> List[ToolUse]:
        """
        提取所有工具调用块
        
        Returns:
            List[ToolUse]: 工具调用列表
        """
        return [b for b in self.blocks if isinstance(b, ToolUse)]

    @property
    def tool_results(self) -> List[ToolResult]:
        """
        提取所有工具结果块
        
        Returns:
            List[ToolResult]: 工具结果列表
        """
        return [b for b in self.blocks if isinstance(b, ToolResult)]


@dataclass
class TokenUsage:
    """
    Token使用统计类
    
    跟踪API调用的token消耗，包括输入、输出和缓存相关统计。
    
    Attributes:
        input_tokens (int): 输入token数量
        output_tokens (int): 输出token数量
        cache_read_input_tokens (int): 从缓存读取的输入token数
        cache_creation_input_tokens (int): 创建缓存的输入token数
    """
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0

    def __add__(self, other: 'TokenUsage') -> 'TokenUsage':
        """
        累加两个TokenUsage对象
        
        Args:
            other (TokenUsage): 另一个TokenUsage对象
            
        Returns:
            TokenUsage: 累加后的新对象
        """
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cache_read_input_tokens=self.cache_read_input_tokens + other.cache_read_input_tokens,
            cache_creation_input_tokens=self.cache_creation_input_tokens + other.cache_creation_input_tokens,
        )

    @property
    def total(self) -> int:
        """
        计算总token数（输入+输出）
        
        Returns:
            int: 总token数量
        """
        return self.input_tokens + self.output_tokens


@dataclass
class ToolDefinition:
    """
    工具定义类
    
    描述一个可用工具的元数据，用于LLM理解工具功能。
    
    Attributes:
        name (str): 工具名称
        description (str): 工具功能描述
        input_schema (Dict[str, Any]): 输入参数的JSON Schema
    """
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class ApiRequest:
    """
    API请求类
    
    封装发送给LLM的完整请求信息。
    
    Attributes:
        model (str): 使用的模型标识符
        messages (List[ConversationMessage]): 对话历史消息
        system (str): 系统提示词
        max_tokens (int): 最大生成token数，默认4096
        tools (List[ToolDefinition]): 可用工具列表
    """
    model: str
    messages: List[ConversationMessage]
    system: str = ""
    max_tokens: int = 4096
    tools: List[ToolDefinition] = field(default_factory=list)


@dataclass
class AssistantEvent:
    """
    助手事件类
    
    表示流式响应中的事件类型（文本增量或工具调用）。
    
    Attributes:
        type (str): 事件类型
    """
    type: str

    @classmethod
    def text_delta(cls, text: str) -> 'AssistantEvent':
        """
        创建文本增量事件
        
        Args:
            text (str): 新增的文本内容
            
        Returns:
            AssistantEvent: 文本增量事件对象
        """
        return cls(type="text_delta", text=text)  # type: ignore

    @classmethod
    def tool_use(cls, id: str, name: str, input: Dict[str, Any]) -> 'AssistantEvent':
        """
        创建工具调用事件
        
        Args:
            id (str): 工具调用ID
            name (str): 工具名称
            input (Dict[str, Any]): 工具参数
            
        Returns:
            AssistantEvent: 工具调用事件对象
        """
        return cls(type="tool_use", id=id, name=name, input=input)  # type: ignore


@dataclass
class TurnSummary:
    """
    对话轮次摘要类
    
    汇总一轮对话的执行情况，包括消息、token使用和迭代次数。
    
    Attributes:
        assistant_messages (List[ConversationMessage]): 助手生成的消息列表
        usage (TokenUsage): 累计的token使用统计
        iterations (int): 迭代次数
        finished (bool): 任务是否已完成
    """
    assistant_messages: List[ConversationMessage] = field(default_factory=list)
    usage: TokenUsage = field(default_factory=TokenUsage)
    iterations: int = 0
    finished: bool = False
