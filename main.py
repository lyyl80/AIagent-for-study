#!/usr/bin/env python3
""" AI Agent - 命令行界面
"""
import re
import argparse
import sys
import os
from typing import Optional
from agent.chat_agent import ChatAgent
from agent.memory import Memory ,generate_session_summary,create_session_filename
from datetime import datetime


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description=" AI Agent - 智能代理系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s --interactive                # 进入交互模式
  %(prog)s --session my_session         # 使用会话文件
  %(prog)s --list-tools                 # 列出可用工具
        """
    )
     
    # 运行模式
    mode_group = parser.add_mutually_exclusive_group()
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
        print(f"  * {tool}")
    print("\n=== 工具描述 ===")
    print(get_tool_description())
def run_interactive_mode( verbose: bool = False):
    """运行交互模式
    
    参数:
        session_path: 会话文件路径
        verbose: 是否显示详细输出
    """
    print("=== OpenCode AI Agent 交互模式 ===")
    print("输入 'exit' 或 'quit' 退出，输入 'help' 查看帮助")
    print("输入 'clear' 清空当前会话历史")
    print("输入 'list' 列出所有会话")
    print("输入 'load <会话文件名>' 加载指定会话")
    print("-" * 50)
    
    # 初始化记忆
    session_id = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    agent = ChatAgent(user_input="")  # 初始化一个默认的agent实例
    
    if verbose:
        print(f"会话ID: {session_id}")
        print(f"会话文件: {agent.history.filename}")
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\nYou: ").strip()
            # 使用同一个agent实例，不重新创建
            agent.user_input = user_input  # 更新任务
            
            if verbose:
                print(f"已加载 {len(agent.history.messages)} 条对话消息, {len(agent.history.history)} 条步骤记录")
            
            # 处理命令
            lower_input = user_input.lower()
            match lower_input:
                case "exit" | "quit":
                    agent.history.save()
                    print("退出交互模式。再见！")
                    break
                case "help":
                    print("可用命令:")
                    print("  exit/quit - 退出程序")
                    print("  clear - 清空当前会话历史")
                    print("  history - 显示步骤历史记录")
                    print("  messages - 显示对话消息")
                    print("  summary - 显示记忆总结")
                    print("  list - 列出所有会话")
                    print("  load <文件名> - 加载指定会话")
                    print("  其他任何输入都将作为任务执行")
                    continue
                case "clear":
                    agent.history.clear()
                    print("会话历史已清空")
                    continue
                case "history":
                    history = agent.history.get_history()
                    if history:
                        for i, item in enumerate(history, 1):
                            print(f"{i}. {item.get('input', {}).get('tool', 'unknown')}: "
                                  f"{item.get('output', '')[:100]}")
                    else:
                        print("暂无步骤历史记录")
                    continue
                case "list":
                    sessions = Memory.list_sessions()
                    if sessions:
                        print(f"找到 {len(sessions)} 个会话:")
                        for i, session in enumerate(sessions, 1):
                            filename = session.get("filename", "未知")
                            summary = session.get("summary", "无摘要")
                            created_time = session.get("created_time", "未知")
                            if len(summary) > 50:
                                summary = summary[:50] + "..."
                            print(f"{i}. {filename}: {summary} ({created_time[:19]})")
                    else:
                        print("暂无保存的会话")
                    continue
                
                case _ if user_input.lower().startswith("load "):
                    # 加载指定会话
                    filename = user_input[5:].strip()
                    try:
                        agent.history = Memory.load_session(filename)
                        print(f"已加载会话: {filename}")
                        if verbose:
                            print(f"会话ID: {agent.history.session_id}")
                            print(f"摘要: {agent.history.summary}")
                            print(f"消息数: {len(agent.history.messages)}")
                    except Exception as e:
                        print(f"加载会话失败: {e}")
                    continue
                
                case _:
                    # 执行任务
                    if not user_input:
                        continue
                    
                    # 添加用户消息到记忆
                    agent.history.add_message("user", user_input)
                    
                    # 执行任务
                    agent.run()
                    
                    # 将代理的历史记录合并到当前记忆
                    # 注意：ChatAgent有自己的Memory实例，这里只添加步骤历史记录
                    agent.history.add_conversation({
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
# 默认进入交互模式
    run_interactive_mode(verbose=args.verbose)


if __name__ == "__main__":
    main()