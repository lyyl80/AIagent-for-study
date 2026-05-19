"""
AI Agent - 命令行界面主程序

本模块实现了基于命令行的交互式AI代理系统，提供以下功能：
- 交互式对话模式
- 会话管理（保存、加载、清空）
- 历史记录查看
- 工具调用执行
- 实时思考状态动画显示
"""
import sys
import os
import time
import threading
from datetime import datetime

# 将项目根目录添加到Python路径，确保可以正确导入core模块
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.llm.client import ApiClient
from core.runtime.conversation import ConversationRuntime, memory_to_runtime_messages
from core.runtime.permissions import PermissionPolicy, PermissionMode
from core.prompt.builder import SystemPromptBuilder
from core.tools import call_tool
from core.agent.memory import Memory


class Spinner:
    """
    旋转动画类 - 用于显示"Thinking"状态的视觉反馈
    
    在守护线程中运行，使用sys.stdout.write避免输出竞争，
    实现横杠旋转动画（|/-\\），提供清晰的处理状态提示。
    
    Attributes:
        message (str): 显示的消息文本
        _stop (threading.Event): 线程停止事件标志
        _thread (threading.Thread): 后台动画线程
    """
    
    def __init__(self, message="Thinking"):
        """
        初始化Spinner对象
        
        Args:
            message (str): 要显示的提示消息，默认为"Thinking"
        """
        self.message = message
        self._stop = threading.Event()
        self._thread = None

    def _spin(self):
        """
        旋转动画的核心逻辑（在后台线程中运行）
        
        持续循环显示旋转字符直到收到停止信号，
        使用回车符\\r实现原地刷新效果。
        """
        chars = "|/-\\"
        idx = 0
        while not self._stop.is_set():
            sys.stdout.write(f"\r{self.message} {chars[idx % len(chars)]}")
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1

    def start(self):
        """
        启动旋转动画线程
        
        如果线程未运行或已结束，则创建新的守护线程并启动。
        守护线程确保主程序退出时自动清理。
        """
        if self._thread is None or not self._thread.is_alive():
            self._stop.clear()
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()

    def stop(self):
        """
        停止旋转动画并清理输出
        
        设置停止事件，等待线程结束，然后清除屏幕上的动画显示。
        """
        if self._thread and self._thread.is_alive():
            self._stop.set()
            self._thread.join()
            sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
            sys.stdout.flush()


class ToolExecutor:
    """
    工具执行器类 - 负责调用和执行业务工具
    
    封装工具调用的异常处理，将执行结果转换为字符串格式，
    供ConversationRuntime使用。
    """
    
    def execute(self, tool_name: str, tool_input: dict) -> str:
        """
        执行指定的工具
        
        Args:
            tool_name (str): 工具名称
            tool_input (dict): 工具的输入参数字典
            
        Returns:
            str: 工具执行结果的字符串表示，或错误信息
        """
        try:
            return str(call_tool(tool_name, **tool_input))
        except Exception as e:
            return f"Error: {e}"


def run_interactive_mode(verbose=False):
    """
    运行交互式命令行模式
    
    主循环处理用户输入，支持多种命令：
    - exit/quit: 退出程序
    - clear: 清空当前会话
    - history: 查看工具执行历史
    - messages: 查看对话消息
    - list: 列出所有保存的会话
    - load <文件名>: 加载指定会话
    
    Args:
        verbose (bool): 是否显示详细的错误追踪信息
    """
    print("=== AI Agent 交互模式 ===")
    print("exit/quit 退出 | clear 清空 | history 步骤 | list 会话 | load <文件> 加载 | help 帮助")
    print("-" * 50)

    # 初始化记忆系统和运行时环境
    memory = Memory(user_input="")

    def _create_runtime():
        return ConversationRuntime(
            system_prompt=SystemPromptBuilder().build(),
            max_iterations=100,
            permission_policy=PermissionPolicy(PermissionMode.DANGER_FULL),
        )

    runtime = _create_runtime()

    def save_msg(role, content, tool_name="", tool_args=""):
        """
        保存消息到记忆系统
        
        根据角色类型（user/assistant/tool）将消息添加到记忆中，
        工具调用会记录输入参数和输出结果。
        
        Args:
            role (str): 消息角色（user/assistant/tool）
            content: 消息内容
            tool_name (str): 工具名称（仅tool角色使用）
            tool_args (str): 工具参数（仅tool角色使用）
        """
        if role == "user":
            memory.add_message("user", content)
        elif role == "assistant":
            text = content.text if hasattr(content, 'text') else str(content)
            memory.add_message("assistant", text)
        elif role == "tool":
            memory.add_conversation({
                "input": {"tool": tool_name, "tool_args": tool_args},
                "output": content,
            })

    # 创建LLM客户端实例
    client = ApiClient()

    # 主交互循环
    while True:
        try:
            raw = input("\nYou: ").strip()
            if not raw:
                continue
            lower = raw.lower()

            # 退出命令
            if lower in ("exit", "quit"):
                memory.save()
                print("再见！")
                break

            # 帮助命令
            if lower == "help":
                print("  exit/quit - 退出")
                print("  clear     - 清空当前会话")
                print("  history   - 显示工具步骤历史")
                print("  messages  - 显示对话消息")
                print("  list      - 列出所有会话")
                print("  load <文件名> - 加载指定会话")
                continue

            # 清空会话
            if lower == "clear":
                memory.clear()
                runtime = _create_runtime()
                print("会话已清空")
                continue

            # 查看工具执行历史
            if lower == "history":
                h = memory.get_history()
                if not h:
                    print("暂无步骤记录")
                else:
                    for i, item in enumerate(h, 1):
                        inp = item.get("input", {})
                        out = str(item.get("output_summary") or item.get("output", ""))
                        tag = inp.get("tool", "?")
                        if item.get("failed"):
                            tag += " (失败)"
                        if len(out) > 120:
                            out = out[:120] + "..."
                        print(f"{i}. [{tag}] {out}")
                continue

            # 查看对话消息
            if lower == "messages":
                msgs = memory.messages
                if not msgs:
                    print("暂无对话消息")
                else:
                    for i, m in enumerate(msgs, 1):
                        print(f"{i}. [{m.get('role', '?')}] {m.get('content', '')}")
                continue

            # 列出所有会话
            if lower == "list":
                sessions = Memory.list_sessions()
                if not sessions:
                    print("暂无保存的会话")
                else:
                    for i, s in enumerate(sessions, 1):
                        summary = (s.get("summary") or "")[:50]
                        print(f"{i}. {s['filename']}: {summary}")
                continue

            # 加载指定会话
            if lower.startswith("load "):
                filename = raw[5:].strip()
                try:
                    memory = Memory.load_session(filename)
                    runtime = _create_runtime()
                    runtime.messages = memory_to_runtime_messages(memory.history)
                    print(f"已加载会话: {filename}")
                except Exception as e:
                    print(f"加载失败: {e}")
                continue

            # 创建思考状态动画
            spinner = Spinner("Thinking")
            try:
                # 执行一轮对话
                runtime.run_turn(
                    raw, client, ToolExecutor(),
                    on_text=lambda block: print(
                        f"\nAI: {block.text if hasattr(block, 'text') else str(block)}",
                        end="", flush=True
                    ),
                    on_tool=lambda name, args, result, failed: (
                        print(f"\n[工具 {name}{' 失败' if failed else ''}] "
                              f"{str(result)[:200]}")
                    ),
                    on_save=save_msg,
                    on_think_begin=lambda: spinner.start(),
                    on_think_end=lambda: spinner.stop(),
                )
            finally:
                # 确保动画线程被正确停止
                spinner.stop()
            print()

        except KeyboardInterrupt:
            print("\n输入 'exit' 退出")
        except EOFError:
            break
        except Exception as e:
            print(f"错误: {e}")
            if verbose:
                import traceback
                traceback.print_exc()


def main():
    """
    程序入口函数
    
    启动交互式命令行模式。
    """
    run_interactive_mode()


if __name__ == "__main__":
    main()
