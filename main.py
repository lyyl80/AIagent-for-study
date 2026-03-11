#!/usr/bin/env python3
""" AI Agent - 命令行界面
"""
import re
import argparse
import sys
import os
from typing import Optional
from agent.chat_agent import ChatAgent
from agent.memory import Memory
from datetime import datetime


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description=" AI Agent - 智能代理系统",
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
def generate_session_summary(messages, max_length=30):
        """
        生成会话摘要，用于文件名
        
        Args:
            messages: 会话消息列表
            max_length: 摘要最大长度
        
        Returns:
            str: 会话摘要
        """
        if not messages:
            return "空会话"
        
        # 提取用户的问题作为摘要
        user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
        
        if not user_messages:
            return "无用户输入"
        
        # 使用第一个用户问题作为基础
        first_question = user_messages[0].strip()
        
        # 清理文本：移除特殊字符，保留中文、英文、数字
        cleaned_text = re.sub(r'[^\u4e00-\u9fff\w\s]', '', first_question)
        
        # 限制长度
        if len(cleaned_text) > max_length:
            # 按字符截取，确保不切分单词
            cleaned_text = cleaned_text[:max_length].rsplit(' ', 1)[0] + "..."
        
        # 移除多余空格
        cleaned_text = ' '.join(cleaned_text.split())
        
        return cleaned_text if cleaned_text else "会话"
    
def create_session_filename(session_id = datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), messages = [{"role": "user", "content": ""}]):
        """
        创建带摘要的会话文件名
        
        Args:
            session_id: 会话ID（时间戳）
            messages: 会话消息列表
        
        Returns:
            str: 完整的文件名（不含扩展名）
        """
        summary = generate_session_summary(messages)
        # 确保文件名安全，移除可能引起问题的字符
        safe_summary = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', summary)
        return f"{session_id}_{safe_summary}"
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
    memory = Memory(session_id=session_id)
    
    if verbose:
        print(f"会话ID: {session_id}")
        print(f"会话文件: {memory.filename}")
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\nYou: ").strip()
            
            if verbose:
                print(f"已加载 {len(memory.messages)} 条对话消息, {len(memory.history)} 条步骤记录")
            
            # 处理命令
            lower_input = user_input.lower()
            match lower_input:
                case "exit" | "quit":
                    memory.save()
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
                    memory.clear()
                    print("会话历史已清空")
                    continue
                case "history":
                    history = memory.get_history()
                    if history:
                        for i, item in enumerate(history, 1):
                            print(f"{i}. {item.get('input', {}).get('tool', 'unknown')}: "
                                  f"{item.get('output', '')[:100]}")
                    else:
                        print("暂无步骤历史记录")
                    continue
                case "messages":
                    messages = memory.get_messages()
                    if messages:
                        for i, msg in enumerate(messages, 1):
                            role = msg.get("role", "unknown")
                            content = msg.get("content", "")[:100]
                            print(f"{i}. [{role}]: {content}")
                    else:
                        print("暂无对话消息")
                    continue
                case "summary":
                    summary = memory.get_summary()
                    if summary:
                        print(f"记忆总结: {summary}")
                    else:
                        print("暂无记忆总结")
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
                        memory = Memory.load_session(filename)
                        print(f"已加载会话: {filename}")
                        if verbose:
                            print(f"会话ID: {memory.session_id}")
                            print(f"摘要: {memory.summary}")
                            print(f"消息数: {len(memory.messages)}")
                    except Exception as e:
                        print(f"加载会话失败: {e}")
                    continue
                
                case _:
                    # 执行任务
                    if not user_input:
                        continue
                    
                    # 添加用户消息到记忆
                    memory.add_message("user", user_input)
                    
                    # 执行任务
                    agent = ChatAgent(user_input)
                    agent.run()
                    
                    # 将代理的历史记录合并到当前记忆
                    # 注意：ChatAgent有自己的Memory实例，这里只添加步骤历史记录
                    # 对话消息已经在上面通过add_message添加了
                    
                    # 如果需要，添加步骤历史记录
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
# 默认进入交互模式
    run_interactive_mode(verbose=args.verbose)


if __name__ == "__main__":
    main()
