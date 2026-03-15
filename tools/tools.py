import subprocess
import sys
import platform
import requests
from bs4 import BeautifulSoup
import re
import chardet


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

def web_content_tool(**kwargs):
    """
    获取一个或多个指定网页的内容并拼接返回
    :param urls: 网页URL地址列表 (也接受单个url参数)
    :return: 所有网页内容拼接后的纯文本
    """
    try:
        # 支持单个URL或URL列表
        urls = kwargs.get("urls")
        if isinstance(urls, str):
            urls = [urls]
        elif not isinstance(urls, list):
            return "错误: 请提供一个URL字符串或URL列表"
        
        if not urls:
            return "错误: 未提供任何URL"
        
        all_content = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        for i, original_url in enumerate(urls, 1):
            try:
                # 直接使用传入的URL，不再处理百度跳转链接
                url = original_url
                
                # 发送请求获取网页内容
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # 尝试检测并设置正确的编码
                detected_encoding = chardet.detect(response.content)
                if detected_encoding and detected_encoding['encoding']:
                    # 使用检测到的编码重新解码内容
                    decoded_content = response.content.decode(detected_encoding['encoding'])
                else:
                    # 如果检测不到编码，尝试常用中文编码
                    try:
                        decoded_content = response.content.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            decoded_content = response.content.decode('gbk')
                        except UnicodeDecodeError:
                            decoded_content = response.content.decode('gb2312', errors='ignore')
                
                # 使用BeautifulSoup解析网页内容
                soup = BeautifulSoup(decoded_content, "html.parser")
                
                # 移除脚本和样式元素
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # 提取网页正文内容
                content_tags = ['main', 'article', '.content', '#content', 'div.content', '.post', '.entry', 'div.post', 'div.entry', '[role="main"]', '.main-content']
                content = None
                
                for tag in content_tags:
                    content = soup.select_one(tag)
                    if content:
                        break
                
                # 如果没有找到指定的内容区域，就使用body标签的内容
                if not content:
                    body = soup.find('body')
                    if body:
                        content = body
                    else:
                        content = soup
                
                # 获取文本内容并清理
                text = content.get_text()
                
                # 清理文本 - 去除多余的空白字符
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # 添加当前网页的序号和内容到总内容中
                all_content.append(f"\n--- 网页 {i} ({original_url}) -> ({url}) ---\n{text}\n--- 网页 {i} 结束 ---\n")
                
            except requests.RequestException as e:
                all_content.append(f"\n--- 网页 {i} ({original_url}) 请求失败 ---\n错误: {str(e)}\n--- 网页 {i} 结束 ---\n")
            except UnicodeDecodeError as e:
                all_content.append(f"\n--- 网页 {i} ({original_url}) 解码失败 ---\n错误: {str(e)}\n--- 网页 {i} 结束 ---\n")
            except Exception as e:
                all_content.append(f"\n--- 网页 {i} ({original_url}) 处理失败 ---\n错误: {str(e)}\n--- 网页 {i} 结束 ---\n")
        
        # 拼接所有内容
        final_content = ''.join(all_content)
        
        # 限制返回内容长度，防止输出过长
        max_length = 2000  # 增加最大长度以容纳多个网页内容
        if len(final_content) > max_length:
            final_content = final_content[:max_length] + "\n\n... (内容已截断)"
        
        return final_content
        
    except Exception as e:
        return f"获取网页内容时发生错误: {str(e)}"


def web_search_tool(**kwargs):
    """
    使用必应(Bing)搜索
    :param query: 搜索查询字符串
    :return: 搜索结果
    """
    try:
        query = kwargs["query"]
        # 使用更真实的浏览器头部信息
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        # 必应搜索URL
        url = f"https://www.bing.com/search?q={query}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 提取必应搜索结果标题和链接
        search_results = []
        
        # 尝试多种可能的选择器来获取搜索结果
        selectors = [
            'li.b_algo',           # 主要选择器 - 必应搜索结果容器
            'div.b_title',         # 标题选择器
            'ol#b_results li'      # 搜索结果列表项
        ]
        
        # 首先尝试主要选择器
        results = soup.select('li.b_algo')
        if results:
            for result in results:
                # 寻找标题元素
                title_elem = result.find('h2') or result.find('a')
                
                if title_elem:
                    # 获取标题文本
                    title = title_elem.get_text().strip()
                    link_elem = result.find('a', href=True)
                    link = link_elem.get('href', '') if link_elem else ''
                    
                    # 如果标题为空或链接为空，跳过此结果
                    if not title.strip() or not link.strip():
                        continue
                    
                    # 尝试获取摘要信息
                    desc_elem = result.find('p', {'class': 'b_paractl'})
                    if not desc_elem:
                        desc_elem = result.find('div', {'class': 'b_caption'})
                    if not desc_elem:
                        desc_elem = result.find('p')
                    
                    desc = desc_elem.get_text().strip() if desc_elem else ""
                    
                    search_results.append({
                        "title": title,
                        "link": link,
                        "desc": desc
                    })
        
        # 如果以上选择器都没找到结果，尝试更通用的方法
        if not search_results:
            # 在必应页面中寻找搜索结果
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                title = link.get_text().strip()
                
                # 检查是否是有效的搜索结果链接
                if title and len(title) > 2 and ('/search?' not in href and 'bing.com' not in href):
                    # 检查是否在搜索结果区域内
                    parent = link.find_parent()
                    if parent and ('b_algo' in parent.get('class', []) or 'b_result' in parent.get('class', [])):
                        desc = "可能的相关结果"
                        search_results.append({
                            "title": title,
                            "link": href,
                            "desc": desc
                        })
        
        if search_results:
            result_str = ""
            for i, result in enumerate(search_results[:5], 1):  # 只返回前5个结果
                result_str += f"{i}. {result['title']}\n   Link: {result['link']}\n   Description: {result['desc']}\n"
            return result_str.strip()
        else:
            return "未能找到搜索结果，请稍后再试。"
            
    except requests.RequestException as e:
        return f"网络请求错误: {str(e)}"
    except Exception as e:
        return f"搜索过程中发生错误: {str(e)}"

def fusion360_tool(**kwargs):
    """
    调用Fusion360工具
    :param kwargs: 工具参数
    :return: 工具执行结果
    """
    tool_name = kwargs.get("tool_name")
    params = kwargs.get("params")
    url = "http://127.0.0.1:8989"
    data = {
        "tool_name": tool_name,
        "params": params
    }
    response = requests.post(url, json=data)
    return response.json()
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