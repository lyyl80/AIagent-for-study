import subprocess
import sys


def read_file_tool(**kwargs):
    """
    读取文件内容
    :param file_path: 文件路径 (也接受 path 参数)
    :param start_line: 可选，开始行号 (1-based)
    :param end_line: 可选，结束行号 (1-based)
    :param search: 可选，搜索字符串，返回包含该字符串的行
    :return: 文件内容字符串或搜索结果
    """
    try:
        file_path = kwargs.get("file_path") or kwargs.get("path")
        start_line = kwargs.get("start_line")
        end_line = kwargs.get("end_line")
        search = kwargs.get("search")
        
        if not file_path:
            return "Error: Missing file path parameter (file_path or path)"
        
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        if search:
            # 搜索模式：返回包含搜索字符串的行及其行号
            result = []
            for i, line in enumerate(lines, 1):
                if search in line:
                    result.append(f"Line {i}: {line.rstrip()}")
            if result:
                return "\n".join(result)
            else:
                return f"No lines found containing: '{search}'"
        
        if start_line and end_line:
            # 行范围模式
            start_line = int(start_line)
            end_line = int(end_line)
            if start_line < 1 or end_line < start_line or end_line > len(lines):
                return f"Error: Invalid line range. File has {len(lines)} lines."
            selected_lines = lines[start_line-1:end_line]
            return "".join(selected_lines)
        
        # 默认：读取整个文件
        return "".join(lines)
    
    except FileNotFoundError:
        return f"Error: File not found: {file_path}"
    except Exception as e:
        print(e)
        return f"Error reading file: {str(e)}"

def write_file_tool(**kwargs):
   """
   写入文件内容
   :param file_path: 文件路径 (也接受 path 参数)
   :param content: 文件内容字符串
   :return: None
   """
   try:
    file_path = kwargs.get("file_path") or kwargs.get("path")
    content = kwargs["content"]
    if not file_path:
        return "Error: Missing file path parameter (file_path or path)"
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    return f"Successfully wrote to file: {file_path}"
   except Exception as e:
    print(e)
    return "Error writing file"

def run_shell(**kwargs):
    """
    执行shell命令
    :param command: shell命令字符串
    :param timeout: 可选，超时时间（秒），默认30秒
    :param cwd: 可选，工作目录
    :return: 命令输出结果
    """
    try:
        command = kwargs["command"]
        timeout = kwargs.get("timeout", 30)  # 默认30秒超时
        cwd = kwargs.get("cwd")
        
        # 使用subprocess.run，它可以更好地处理编码问题
        if sys.platform.startswith('win'):
            # 对于Windows，使用系统默认编码
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=False,  # 返回bytes，以便我们可以手动解码
                timeout=timeout,
                cwd=cwd
            )
            
            # 尝试多种编码方式
            try:
                # 尝试使用cp936 (GBK的超集) 解码Windows输出
                output = result.stdout.decode('cp936')
                error_output = result.stderr.decode('cp936')
            except UnicodeDecodeError:
                try:
                    # 如果失败，尝试UTF-8
                    output = result.stdout.decode('utf-8')
                    error_output = result.stderr.decode('utf-8')
                except UnicodeDecodeError:
                    # 最后尝试使用错误忽略方式
                    output = result.stdout.decode('utf-8', errors='replace')
                    error_output = result.stderr.decode('utf-8', errors='replace')
        else:
            # 对于Unix/Linux/macOS系统
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=False,
                timeout=timeout,
                cwd=cwd
            )
            output = result.stdout.decode('utf-8', errors='replace')
            error_output = result.stderr.decode('utf-8', errors='replace')

        # 检查命令是否成功执行
        if result.returncode != 0:
            # 如果错误信息包含"已经存在"，添加额外提示
            if "已经存在" in error_output or "already exists" in error_output.lower():
                error_output += " (目录/文件已存在，建议直接在该路径下操作，不要重复创建)"
            return f"Command failed with exit code {result.returncode}: {error_output}"

        # 截断过长输出，避免上下文溢出
        if len(output) > 2000:
            output = output[:2000] + "\n... (output truncated)"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {str(e)}"
    except UnicodeDecodeError as e:
        return f"Error decoding command output: {str(e)}"
    except Exception as e:
        return f"Unexpected error executing command: {str(e)}"

def talk_tool(**kwargs):
   """
   聊天
   :param message: 聊天内容 (也接受 text, content 参数)
   :return: 聊天结果
   """
   message = kwargs.get("message") or kwargs.get("content") or kwargs.get("text")
   if not message:
       return "错误: 缺少聊天内容参数 'message', 'content' 或 'text'"
   return message

def replace_content_tool(**kwargs):
    """
    替换文件中的现有内容
    :param file_path: 文件路径 (也接受 path 参数)
    :param old_content: 要替换的旧内容字符串
    :param new_content: 新的内容字符串
    :return: 操作结果
    """
    try:
        file_path = kwargs.get("file_path") or kwargs.get("path")
        old_content = kwargs.get("old_content")
        new_content = kwargs.get("new_content")
        
        if not file_path:
            return "Error: Missing file path parameter (file_path or path)"
        if old_content is None:
            return "Error: Missing old_content parameter"
        if new_content is None:
            return "Error: Missing new_content parameter"
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 检查旧内容是否存在
        if old_content not in content:
            return f"Error: Old content not found in file: {file_path}"
        
        # 替换内容
        new_file_content = content.replace(old_content, new_content, 1)  # 只替换第一次出现
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_file_content)
        
        return f"Successfully replaced content in file: {file_path}"
    
    except FileNotFoundError:
        return f"Error: File not found: {file_path}"
    except Exception as e:
        print(e)
        return f"Error replacing content in file: {str(e)}"


def finish_tool(**kwargs):
    """
    结束任务，可选地提供结语消息
    :param response: 可选，结语消息
    :return: 结束消息
    """
    response = kwargs.get("response")
    if response:
        return response
    return "任务完成"

    