import sys
sys.path.insert(0, '.')

# 测试场景1: 目录已存在时的智能处理
print("=== 场景1: 创建已存在的目录 ===")
from agent.chat_agent import ChatAgent

agent1 = ChatAgent("帮我创建一个文件夹叫做new在当前目录")
print("期望: agent应该检查new是文件还是目录，然后决定在内部操作或询问用户")
agent1.run()

print("\n=== 场景2: 在目录中创建文件 ===")
agent2 = ChatAgent("在new里面写一个python的代码,用于显示hello , world")
print("期望: agent应该在new目录下创建.py文件，而不是直接写入new文件")
agent2.run()

print("\n=== 场景3: 检查文件是否正确创建 ===")
agent3 = ChatAgent("查看new目录下有什么文件")
agent3.run()

# 检查实际创建的文件
import os
if os.path.exists("new"):
    print("\n=== 实际文件检查 ===")
    for root, dirs, files in os.walk("new"):
        for file in files:
            filepath = os.path.join(root, file)
            print(f"找到文件: {filepath}")
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    print(f"内容: {content}")
            except:
                print(f"无法读取文件: {filepath}")