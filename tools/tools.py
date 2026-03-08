import subprocess
import sys

def calculator_tool(**kwargs):
   """
   计算数学表达式,仅仅支持+,-,*,/四则运算和括号。
   :param expression: 数学表达式字符串
   :return: 计算结果
   """
   try:
    expression = kwargs["expression"]
    eval(expression, {"__builtins__": None}, {})
    return f"计算结果: {eval(expression)}"
   except Exception as e:
    print(e)
   return "Invalid expression"

def read_file_tool(**kwargs):
    """
    读取文件内容
    :param file_path: 文件路径
    :return: 文件内容字符串
    """
    try:
        file_path = kwargs["file_path"]
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        print(e)
        return "Error reading file"

def write_file_tool(**kwargs):
   """
   写入文件内容
   :param file_path: 文件路径
   :param content: 文件内容字符串
   :return: None
   """
   try:
    file_path = kwargs["file_path"]
    content = kwargs["content"]
    with open(file_path, 'w') as file:
        file.write(content)
    return f"Successfully wrote to file: {file_path}"
   except Exception as e:
    print(e)
    return "Error writing file"

def run_shell(**kwargs):
    """
    执行shell命令
    :param command: shell命令字符串
    :return: 命令输出结果
    """
    try:
        command = kwargs["command"]
        
        # 使用subprocess.run，它可以更好地处理编码问题
        if sys.platform.startswith('win'):
            # 对于Windows，使用系统默认编码
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=False  # 返回bytes，以便我们可以手动解码
            )
            
            # 尝试多种编码方式
            try:
                # 尝试使用cp936 (GBK的超集) 解码Windows输出
                output = result.stdout.decode('cp936')
            except UnicodeDecodeError:
                try:
                    # 如果失败，尝试UTF-8
                    output = result.stdout.decode('utf-8')
                except UnicodeDecodeError:
                    # 最后尝试使用错误忽略方式
                    output = result.stdout.decode('utf-8', errors='replace')
        else:
            # 对于Unix/Linux/macOS系统
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=False
            )
            output = result.stdout.decode('utf-8')

        # 检查命令是否成功执行
        if result.returncode != 0:
            error_output = result.stderr.decode('cp936') if sys.platform.startswith('win') else result.stderr.decode('utf-8')
            return f"Command failed with exit code {result.returncode}: {error_output}"

        return output
        
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {str(e)}"
    except UnicodeDecodeError as e:
        return f"Error decoding command output: {str(e)}"
    except Exception as e:
        return f"Unexpected error executing command: {str(e)}"

def talk_tool(**kwargs):
   """
   聊天
   :param message: 聊天内容
   :return: 聊天结果
   """
   message = kwargs.get("message") or kwargs.get("content")
   if not message:
       return "错误: 缺少聊天内容参数 'message' 或 'content'"
   return f"你说: {message}"
   


    