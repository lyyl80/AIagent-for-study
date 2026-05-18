"""AI Agent - 命令行界面"""
import sys
import os
import time
import threading
from datetime import datetime

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
    def __init__(self, message="Thinking"):
        self.message = message
        self._stop = threading.Event()
        self._thread = None

    def _spin(self):
        chars = "|/-\\"
        idx = 0
        while not self._stop.is_set():
            sys.stdout.write(f"\r{self.message} {chars[idx % len(chars)]}")
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._stop.clear()
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()

    def stop(self):
        if self._thread and self._thread.is_alive():
            self._stop.set()
            self._thread.join()
            sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
            sys.stdout.flush()


class ToolExecutor:
    def execute(self, tool_name: str, tool_input: dict) -> str:
        try:
            return str(call_tool(tool_name, **tool_input))
        except Exception as e:
            return f"Error: {e}"


def run_interactive_mode(verbose=False):
    print("=== AI Agent 交互模式 ===")
    print("exit/quit 退出 | clear 清空 | history 步骤 | list 会话 | load <文件> 加载 | help 帮助")
    print("-" * 50)

    memory = Memory(user_input="")
    runtime = ConversationRuntime(
        system_prompt=SystemPromptBuilder().build(),
        max_iterations=100,
        permission_policy=PermissionPolicy(PermissionMode.DANGER_FULL),
    )

    def _new_runtime():
        return ConversationRuntime(
            system_prompt=SystemPromptBuilder().build(),
            max_iterations=100,
            permission_policy=PermissionPolicy(PermissionMode.DANGER_FULL),
        )

    def save_msg(role, content, tool_name="", tool_args=""):
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

    client = ApiClient()

    while True:
        try:
            raw = input("\nYou: ").strip()
            if not raw:
                continue
            lower = raw.lower()

            if lower in ("exit", "quit"):
                memory.save()
                print("再见！")
                break

            if lower == "help":
                print("  exit/quit - 退出")
                print("  clear     - 清空当前会话")
                print("  history   - 显示工具步骤历史")
                print("  messages  - 显示对话消息")
                print("  list      - 列出所有会话")
                print("  load <文件名> - 加载指定会话")
                continue

            if lower == "clear":
                memory.clear()
                runtime = _new_runtime()
                print("会话已清空")
                continue

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

            if lower == "messages":
                msgs = memory.messages
                if not msgs:
                    print("暂无对话消息")
                else:
                    for i, m in enumerate(msgs, 1):
                        print(f"{i}. [{m.get('role', '?')}] {m.get('content', '')}")
                continue

            if lower == "list":
                sessions = Memory.list_sessions()
                if not sessions:
                    print("暂无保存的会话")
                else:
                    for i, s in enumerate(sessions, 1):
                        summary = (s.get("summary") or "")[:50]
                        print(f"{i}. {s['filename']}: {summary}")
                continue

            if lower.startswith("load "):
                filename = raw[5:].strip()
                try:
                    memory = Memory.load_session(filename)
                    runtime = _new_runtime()
                    runtime.messages = memory_to_runtime_messages(memory.history)
                    print(f"已加载会话: {filename}")
                except Exception as e:
                    print(f"加载失败: {e}")
                continue

            spinner = Spinner("Thinking")
            try:
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
    run_interactive_mode()


if __name__ == "__main__":
    main()
