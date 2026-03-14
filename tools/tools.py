import subprocess
import sys
import platform
import requests
from bs4 import BeautifulSoup


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
        timeout = kwargs.get("timeout", 30)
        cwd = kwargs.get("cwd")
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout,
            cwd=cwd
        )
        
        if result.returncode != 0:
            return f"Command failed with exit code {result.returncode}: {result.stderr}"
        
        # 截断过长输出
        if len(result.stdout) > 2000:
            return result.stdout[:2000] + "\n... (output truncated)"
        
        return result.stdout
        
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

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

def web_search_tool(**kwargs):
    """
    使用谷歌搜索
    :param query: 搜索查询字符串
    :return: 搜索结果
    """
    try:
        query = kwargs["query"]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        url = f"https://www.google.com/search?q={query}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 提取搜索结果标题和链接
        search_results = []
        for g in soup.find_all('div', class_='g'):
            anchor = g.find('a')
            if anchor and anchor.get('href'):
                link = anchor['href']
                title_elem = g.find('h3')
                title = title_elem.text if title_elem else "No title found"
                search_results.append({
                    "title": title,
                    "link": link
                })
        
        # 如果上面的方法没找到结果，尝试另一种选择器
        if not search_results:
            for r in soup.find_all('div', class_='r'):
                anchor = r.find('a')
                if anchor and anchor.get('href'):
                    link = anchor['href']
                    title_elem = r.find('h3')
                    title = title_elem.text if title_elem else "No title found"
                    search_results.append({
                        "title": title,
                        "link": link
                    })

        if search_results:
            result_str = ""
            for i, result in enumerate(search_results[:5], 1):  # 只返回前5个结果
                result_str += f"{i}. {result['title']}\n   Link: {result['link']}\n"
            return result_str.strip()
        else:
            return "未能找到搜索结果，请稍后再试。"
            
    except requests.RequestException as e:
        return f"网络请求错误: {str(e)}"
    except Exception as e:
        return f"搜索过程中发生错误: {str(e)}"


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