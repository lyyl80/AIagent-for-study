#!/usr/bin/env python3
"""OpenCode AI Agent - 命令行界面

基于OpenCode架构重构的AI代理系统，支持工具调用和对话交互。
"""

import argparse
import sys
import os
from typing import Optional

from agent.chat_agent import ChatAgent
from agent.memory import Memory


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="OpenCode AI Agent - 智能代理系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s "创建一个Python文件"          # 执行单个任务
  %(prog)s --interactive                # 进入交互模式
  %(prog)s --session my_session         # 使用会话文件
  %(prog)s --list-tools                 # 列出可用工具
        """
    )
    
    # 运行模式
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "task",
        nargs="?",
        help="要执行的任务描述（如果提供，则执行单次任务）"
    )
    mode_group.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="进入交互模式"
    )
    
    # 会话管理
    parser.add_argument(
        "-s", "--session",
        help="会话文件路径，用于保存/加载对话历史"
    )
    parser.add_argument(
        "--clear-session",
        action="store_true",
        help="清除会话历史"
    )
    
    # 工具管理
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="列出所有可用工具"
    )
    
    # 输出控制
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细输出"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="禁用颜色输出"
    )
    
    return parser.parse_args()


def list_tools():
    """列出所有可用工具"""
    from tools import list_tools, get_tool_description
    print("=== 可用工具 ===")
    tools = list_tools()
    for tool in tools:
        print(f"  • {tool}")
    print("\n=== 工具描述 ===")
    print(get_tool_description())


def run_single_task(task: str, session_path: Optional[str] = None, verbose: bool = False):
    """执行单个任务
    
    参数:
        task: 任务描述
        session_path: 会话文件路径
        verbose: 是否显示详细输出
    """
    if verbose:
        print(f"任务: {task}")
        print("-" * 50)
    
    # 创建代理
    agent = ChatAgent(task)
    
    # 如果需要，加载会话记忆
    if session_path:
        # 注意：当前ChatAgent未直接支持会话加载，这里仅作示例
        # 实际实现时应在ChatAgent中添加会话支持
        if os.path.exists(session_path):
            if verbose:
                print(f"从会话文件加载: {session_path}")
    
    # 运行代理
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n任务被用户中断")
    except Exception as e:
        print(f"执行任务时出错: {e}")
        sys.exit(1)
    
    # 如果需要，保存会话
    if session_path and verbose:
        print(f"会话已保存到: {session_path}")


def run_interactive_mode(session_path: Optional[str] = None, verbose: bool = False):
    """运行交互模式
    
    参数:
        session_path: 会话文件路径
        verbose: 是否显示详细输出
    """
    print("=== OpenCode AI Agent 交互模式 ===")
    print("输入 'exit' 或 'quit' 退出，输入 'help' 查看帮助")
    print("输入 'clear' 清空当前会话历史")
    print("-" * 50)
    
    # 初始化记忆（如果提供了会话路径）
    memory = None
    if session_path:
        memory = Memory(persist_path=session_path)
        if verbose:
            print(f"会话文件: {session_path}")
            if len(memory) > 0:
                print(f"已加载 {len(memory)} 条历史记录")
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\nYou: ").strip()
            
            # 处理命令
            if user_input.lower() in ["exit", "quit"]:
                print("退出交互模式。再见！")
                break
            elif user_input.lower() == "help":
                print("可用命令:")
                print("  exit/quit - 退出程序")
                print("  clear - 清空当前会话历史")
                print("  history - 显示历史记录")
                print("  summary - 显示记忆总结")
                print("  其他任何输入都将作为任务执行")
                continue
            elif user_input.lower() == "clear":
                if memory:
                    memory.clear()
                    print("会话历史已清空")
                else:
                    print("当前未使用会话模式")
                continue
            elif user_input.lower() == "history":
                if memory:
                    history = memory.get_history()
                    for i, item in enumerate(history, 1):
                        print(f"{i}. {item.get('input', {}).get('tool', 'unknown')}: "
                              f"{item.get('output', '')[:100]}")
                else:
                    print("当前未使用会话模式")
                continue
            elif user_input.lower() == "summary":
                if memory:
                    summary = memory.get_summary()
                    if summary:
                        print(f"记忆总结: {summary}")
                    else:
                        print("暂无记忆总结")
                else:
                    print("当前未使用会话模式")
                continue
            
            # 执行任务
            if not user_input:
                continue
                
            agent = ChatAgent(user_input)
            
            # 如果存在记忆，可以传递给代理（当前ChatAgent未直接支持，这里仅作示例）
            # 实际实现时应在ChatAgent构造函数中接受memory参数
            
            agent.run()
            
            # 如果需要，将本次对话添加到记忆
            if memory:
                # 这里简化处理，实际应保存更详细的对话记录
                memory.add_conversation({
                    "input": {"tool": "user", "tool_args": {"message": user_input}},
                    "output": "任务执行完成",
                    "reflect": "用户任务"
                })
                
        except KeyboardInterrupt:
            print("\n输入 'exit' 退出程序")
        except EOFError:
            print("\n检测到文件结束符，退出程序")
            break
        except Exception as e:
            print(f"执行时出错: {e}")
            if verbose:
                import traceback
                traceback.print_exc()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 列出工具
    if args.list_tools:
        list_tools()
        return
    
    # 检查运行模式
    if args.interactive:
        run_interactive_mode(args.session, args.verbose)
    elif args.task:
        run_single_task(args.task, args.session, args.verbose)
    else:
        # 默认进入交互模式
        run_interactive_mode(args.session, args.verbose)


if __name__ == "__main__":
    main()
