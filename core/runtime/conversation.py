"""
对话运行时模块

实现AI代理的核心对话循环逻辑，包括：
- 消息历史管理
- API请求构建和发送
- 工具调用执行
- 权限检查
- 会话压缩
- 收敛检测（防止无限循环）

提供流式回调接口供UI层订阅事件。
"""
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
    """
    安全解析工具参数字符串
    
    尝试使用ast.literal_eval解析字符串为Python对象，失败时返回空字典。
    
    Args:
        args_raw: 原始参数（可能是字典或字符串）
        
    Returns:
        Dict: 解析后的参数字典
    """
    if isinstance(args_raw, dict):
        return args_raw
    try:
        return ast.literal_eval(args_raw)
    except (ValueError, SyntaxError):
        return {}


def memory_to_runtime_messages(history: list) -> List[ConversationMessage]:
    """
    将Memory.history转换为ConversationMessage列表
    
    处理两种格式的历史记录：
    1. 包含input/output的工具调用记录
    2. 简单的role/content消息记录
    
    保持时间顺序，正确区分用户消息、助手回复和工具结果。
    
    Args:
        history (list): Memory中的历史记录列表
        
    Returns:
        List[ConversationMessage]: 转换后的运行时消息列表
    """
    messages: List[ConversationMessage] = []
    for entry in history:
        if "input" in entry:
            # 工具调用格式
            tool = entry["input"].get("tool", "")
            args_raw = entry["input"].get("tool_args", {})
            output = entry.get("output", "")
            is_error = entry.get("failed", False) or (
                isinstance(output, str) and output.startswith("Error:")
            )

            # 特殊处理对话和完成工具
            if tool in ("talk", "finish"):
                messages.append(ConversationMessage.assistant([
                    TextBlock(text=output)
                ]))
            elif tool == "user":
                # 用户消息嵌入在工具调用中
                args = _safe_parse_args(args_raw)
                msg = args.get("message", output) if isinstance(args, dict) else str(args_raw)
                messages.append(ConversationMessage.user_text(msg or output))
            else:
                # 普通工具调用
                args = _safe_parse_args(args_raw)
                tool_id = f"tu_{hash(str(args_raw))}_p{len(messages)}"
                messages.append(ConversationMessage.assistant([
                    ToolUse(id=tool_id, name=tool, input=args)
                ]))
                messages.append(ConversationMessage.tool_result(
                    tool_id, output, is_error=is_error
                ))
        else:
            # 简单消息格式
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
    """
    对话运行时类
    
    管理单轮对话的完整生命周期，包括消息流转、工具调用、权限控制等。
    支持最大迭代次数限制以防止无限循环。
    
    Attributes:
        messages (List[ConversationMessage]): 对话消息历史
        system_prompt (str): 系统提示词
        max_iterations (int): 最大迭代次数，默认100
        usage_tracker (UsageTracker): Token使用跟踪器
        permission_policy (PermissionPolicy): 权限策略
        compactor (SessionCompactor): 会话压缩器
        allowed_tools (Optional[Set[str]]): 允许使用的工具集合，None表示全部允许
        _last_tool_steps (List[Tuple[str, str]]): 最近3步工具调用记录（用于收敛检测）
    """
    messages: List[ConversationMessage] = field(default_factory=list)
    system_prompt: str = ""
    max_iterations: int = 100
    usage_tracker: UsageTracker = field(default_factory=UsageTracker)
    permission_policy: PermissionPolicy = field(default_factory=PermissionPolicy)
    compactor: SessionCompactor = field(default_factory=SessionCompactor)
    allowed_tools: Optional[Set[str]] = None

    def __post_init__(self):
        """初始化后设置内部状态"""
        self._last_tool_steps: List[Tuple[str, str]] = []

    def run_turn(self, user_input: str, api_client, tool_executor,
                 on_text: Optional[Callable[[str], None]] = None,
                 on_tool: Optional[Callable[[str, Dict, str, bool], None]] = None,
                 on_save: Optional[Callable[[str, str], None]] = None,
                 on_think_begin: Optional[Callable[[], None]] = None,
                 on_think_end: Optional[Callable[[], None]] = None) -> TurnSummary:
        """
        执行一轮对话
        
        核心循环逻辑：
        1. 添加用户消息到历史
        2. 构建API请求并调用LLM
        3. 解析响应，执行工具调用
        4. 检查结果，判断是否收敛
        5. 必要时压缩会话历史
        
        Args:
            user_input (str): 用户输入文本
            api_client: LLM客户端实例
            tool_executor: 工具执行器实例
            on_text (Callable, optional): 文本输出回调
            on_tool (Callable, optional): 工具调用回调，参数(name, args, result, is_error)
            on_save (Callable, optional): 保存消息回调，参数(role, content, tool_name, tool_args)
            on_think_begin (Callable, optional): 思考开始回调（启动动画）
            on_think_end (Callable, optional): 思考结束回调（停止动画）
            
        Returns:
            TurnSummary: 本轮对话的执行摘要
        """
        # 添加用户消息
        self.messages.append(ConversationMessage.user_text(user_input))
        if on_save:
            on_save("user", user_input)
        total_usage = TokenUsage()

        # 主循环：最多max_iterations次迭代
        for iteration in range(1, self.max_iterations + 1):
            # 构建API请求
            request = ApiRequest(
                model=api_client.model,
                messages=self.messages,
                system=self.system_prompt,
                tools=api_client.get_tool_definitions() if self.allowed_tools is None else [
                    t for t in api_client.get_tool_definitions() if t.name in self.allowed_tools
                ],
            )

            # 调用LLM（带思考动画）
            if on_think_begin:
                on_think_begin()
            blocks, usage = api_client.stream(request)
            if on_think_end:
                on_think_end()
            total_usage += usage

            # 添加助手消息到历史
            msg = ConversationMessage.assistant(blocks, usage)
            self.messages.append(msg)

            # 检查是否有工具调用
            tool_uses = msg.tool_uses
            if not tool_uses:
                # 纯文本回复，任务完成
                for block in msg.text_blocks:
                    if block and on_text:
                        on_text(block)
                    if on_save:
                        on_save("assistant", block)
                return TurnSummary(usage=total_usage, iterations=iteration, finished=True)

            # 执行所有工具调用
            for tool_use in tool_uses:
                self.usage_tracker.add(usage)

                # 权限检查
                permitted, reason = self.permission_policy.authorize(tool_use.name)
                if not permitted:
                    result = f"权限拒绝: {reason}"
                    is_error = True
                else:
                    # 执行工具
                    result = tool_executor.execute(tool_use.name, tool_use.input)
                    is_error = isinstance(result, str) and result.startswith("Error:")

                # 添加工具结果到历史
                self.messages.append(ConversationMessage.tool_result(
                    tool_use.id, str(result), is_error=is_error
                ))
                if on_tool:
                    on_tool(tool_use.name, tool_use.input, str(result), is_error)
                if on_save:
                    on_save("tool", str(result), tool_use.name, str(tool_use.input))

            # 检查收敛条件（防止无限循环）
            if self._check_convergence(tool_uses):
                self._last_tool_steps = []
                return TurnSummary(usage=total_usage, iterations=iteration, finished=True)

            # 必要时压缩会话历史
            if self.compactor.should_compact(total_usage):
                self.messages = self.compactor.compact(self.messages)

        # 达到最大迭代次数
        return TurnSummary(usage=total_usage, iterations=self.max_iterations, finished=True)

    def _check_convergence(self, tool_uses: List[ToolUse]) -> bool:
        """
        检查是否陷入无限循环
        
        如果连续3次执行相同的工具调用（相同名称和参数），则认为已收敛，
        需要终止循环以避免资源浪费。
        
        Args:
            tool_uses (List[ToolUse]): 当前迭代的工具调用列表
            
        Returns:
            bool: 是否检测到收敛（应终止）
        """
        # 记录当前步骤
        for tu in tool_uses:
            key = (tu.name, str(sorted(tu.input.items())))
            self._last_tool_steps.append(key)
            if len(self._last_tool_steps) > 3:
                self._last_tool_steps.pop(0)

        # 检查最近3步是否完全相同
        if len(self._last_tool_steps) == 3 and len(set(self._last_tool_steps)) == 1:
            name = self._last_tool_steps[0][0]
            # talk和finish工具不算收敛
            if name not in ("talk", "finish"):
                return True
        return False

    def get_history_text(self, max_chars: int = 8000) -> str:
        """
        获取格式化的对话历史文本
        
        用于调试和展示，自动截断过长的工具输出。
        如果总长度超过限制，只显示最近的消息。
        
        Args:
            max_chars (int): 最大字符数，默认8000
            
        Returns:
            str: 格式化的对话历史文本
        """
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

        # 超出限制时，只显示最近的消息
        recent = []
        for line in reversed(lines):
            if len("\n".join([line] + recent)) > max_chars - 500:
                break
            recent.insert(0, line)
        return "(早期历史已省略)\n" + "\n".join(recent)
