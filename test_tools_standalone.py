"""
工具模块测试脚本
"""
from tools import call_tool, get_tool_description

if __name__ == "__main__":
    print("======测试计算器=====")
    print(call_tool("calculator", expression="2 + 3 * (4 - 1)"))
    
    print("======测试读取文件=====")
    print(call_tool("read_file", file_path="test.txt"))
    
    print("======测试写入文件=====")
    print(call_tool("write_file", file_path="test.txt", content="Hello, World!"))
    
    print("======测试新建文件=====")
    print(call_tool("write_file", file_path="test1.txt", content="Test content for new file"))
    
    print("======测试运行shell命令=====")
    # 注意：Windows系统使用dir命令，Linux/Mac使用ls命令
    import platform
    if platform.system() == "Windows":
        print(call_tool("shell", command="dir"))
    else:
        print(call_tool("shell", command="ls"))
        
    print("======测试获取工具描述=====")
    print(get_tool_description(""))