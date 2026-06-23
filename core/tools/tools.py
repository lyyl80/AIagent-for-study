"""
工具函数模块

提供AI代理可调用的各种实用工具，包括：
- 文件操作（读取、写入、替换、搜索）
- 目录管理（列出、创建、删除、复制/移动）
- Shell命令执行
- 网络请求（搜索、网页抓取）
- 实用功能（天气查询、语音合成、Python代码执行）

所有工具通过**kwargs接收参数，返回字符串格式的结果。
"""
import subprocess
import sys
import os
import platform
import shutil
import stat
import re
import hashlib
import time
import fnmatch
import json as _json_mod
from pathlib import Path
from typing import Any
import serial
import requests
from bs4 import BeautifulSoup
import chardet
import serial
import time
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


# ===================== 内部辅助函数 =====================

def _get_file_path(kwargs: dict) -> str:
    """从 kwargs 中提取文件路径，支持 file_path / path 两种键名"""
    path = kwargs.get("file_path") or kwargs.get("path")
    if not path:
        raise ValueError("缺少参数 file_path")
    return path


def _validate_file_isfile(path: str) -> None:
    """确认 path 是一个存在的文件，否则抛出异常"""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"文件不存在: {path}")


def _normalize_content(content: str) -> str:
    """标准化行尾符：\r\r\n → \n, \r\n → \n"""
    return content.replace('\r\r\n', '\n').replace('\r\n', '\n')


def _auto_encode(file_path: str) -> str:
    """
    自动检测文件编码并读取内容
    
    使用chardet库检测文件编码，支持多种编码格式（UTF-8、GBK等）。
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        str: 解码后的文件内容，解码失败时使用replace策略
    """
    with open(file_path, 'rb') as f:
        raw = f.read()
    if not raw:
        return ''
    result = chardet.detect(raw)
    encoding = result.get('encoding', 'utf-8') or 'utf-8'
    return raw.decode(encoding, errors='replace')


# ============================================================
# 文件操作工具
# ============================================================

def read_file_tool(**kwargs) -> str:
    """
    读取文件内容
    
    支持按行号范围读取、关键词搜索、大文件截断等功能。
    自动检测文件编码，限制最大文件大小为5MB。
    
    Args:
        file_path/path (str): 文件路径
        search (str, optional): 搜索关键词，返回包含该词的行
        start_line (int, optional): 起始行号，默认1
        end_line (int, optional): 结束行号
        max_lines (int, optional): 最大返回行数，默认500
        
    Returns:
        str: 文件内容或搜索结果，错误时返回错误信息
    """
    try:
        file_path = _get_file_path(kwargs)
        _validate_file_isfile(file_path)
    except (ValueError, FileNotFoundError) as e:
        return f"Error: {e}"

    try:
        # 检查文件大小限制
        if os.path.getsize(file_path) > 5 * 1024 * 1024:
            return f"Error: 文件过大 ({os.path.getsize(file_path) // 1024}KB)，超过 5MB 限制"

        content = _auto_encode(file_path)
        lines = content.splitlines(keepends=True)

        # 关键词搜索模式
        if "search" in kwargs:
            found = []
            for i, li in enumerate(lines, 1):
                if kwargs["search"] in li:
                    found.append(f"L{i}: {li.rstrip()}")
            return "\n".join(found) if found else f"未找到: '{kwargs['search']}'"

        # 按行号范围读取
        start = int(kwargs.get("start_line", 1))
        end = kwargs.get("end_line")
        if end is not None:
            end = int(end)
            if start < 1 or end < start or end > len(lines):
                return f"Error: 行号无效，文件共 {len(lines)} 行"
            return "".join(lines[start - 1:end])

        # 从指定行读到末尾
        if start > 1:
            return "".join(lines[start - 1:])

        # 限制返回行数
        max_lines = kwargs.get("max_lines", 500)
        if isinstance(max_lines, str):
            max_lines = int(max_lines)
        if len(lines) > max_lines:
            return "".join(lines[:max_lines]) + f"\n... (共 {len(lines)} 行，已截断前 {max_lines} 行)"
        return content

    except Exception as e:
        return f"Error: 读取文件失败: {e}"


def write_file_tool(**kwargs) -> str:
    """
    写入文件内容
    
    支持追加模式和备份功能。自动创建父目录。
    
    Args:
        file_path/path (str): 文件路径
        content (str): 要写入的内容
        append (bool, optional): 是否追加模式，默认False（覆盖）
        backup (bool, optional): 覆盖前是否创建.bak备份文件
        
    Returns:
        str: 成功消息或错误信息
    """
    try:
        file_path = _get_file_path(kwargs)
    except ValueError as e:
        return f"Error: {e}"
    content = kwargs.get("content")
    if content is None:
        return "Error: 缺少参数 content"

    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)) or ".", exist_ok=True)

        if kwargs.get("append"):
            mode = 'a'
        else:
            mode = 'w'
            if kwargs.get("backup") and os.path.isfile(file_path):
                shutil.copy2(file_path, file_path + ".bak")

        with open(file_path, mode, encoding='utf-8') as f:
            f.write(_normalize_content(content))

        size = os.path.getsize(file_path)
        return f"写入成功: {file_path} ({size} 字节)"
    except Exception as e:
        return f"Error: 写入文件失败: {e}"


def replace_content_tool(**kwargs) -> str:
    """
    替换文件内容
    
    支持精确匹配和正则表达式替换，可控制替换次数。
    
    Args:
        file_path/path (str): 文件路径
        old_content (str): 要替换的旧内容或正则表达式
        new_content (str): 新内容
        regex (bool, optional): 是否使用正则表达式，默认False
        count (int, optional): 最大替换次数，0表示全部替换
        
    Returns:
        str: 替换结果统计或错误信息
    """
    try:
        file_path = _get_file_path(kwargs)
        _validate_file_isfile(file_path)
    except (ValueError, FileNotFoundError) as e:
        return f"Error: {e}"

    old_val = kwargs.get("old_content", "")
    new_val = kwargs.get("new_content", "")
    use_regex = kwargs.get("regex", False)
    count = int(kwargs.get("count", 0) or 0)

    try:
        content = _auto_encode(file_path)
    except Exception as e:
        return f"Error: 读取文件失败: {e}"

    content = _normalize_content(content)
    if not use_regex:
        old_val = old_val.replace('\r\r\n', '\n').replace('\r\n', '\n')

    if use_regex:
        try:
            new_content, n = re.subn(old_val, new_val, content, count=count if count > 0 else 0)
        except re.error as e:
            return f"Error: 正则表达式无效: {e}"
    else:
        if old_val not in content:
            return "Error: 文件中未找到要替换的内容"
        if count > 1:
            new_content = content.replace(old_val, new_val, count)
            n = min(count, content.count(old_val))
        else:
            new_content = content.replace(old_val, new_val, 1)
            n = 1

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return f"替换成功: {file_path} ({n} 处替换)"
    except Exception as e:
        return f"Error: 写入文件失败: {e}"


# ============================================================
# 目录 / 文件管理工具
# ============================================================

def list_directory(**kwargs) -> str:
    """
    列出目录内容
    
    显示文件名、大小、修改时间和类型（文件/目录）。
    支持隐藏文件过滤、正则匹配、递归列出等功能。
    
    Args:
        path (str): 目录路径，默认当前目录
        all (bool, optional): 是否显示隐藏文件（以.开头），默认False
        pattern (str, optional): 文件名正则过滤模式
        
    Returns:
        str: 格式化的目录列表或错误信息
    """
    path = kwargs.get("path", ".")
    if not os.path.isdir(path):
        return f"Error: 目录不存在: {path}"

    try:
        show_hidden = kwargs.get("all", False)
        pattern = kwargs.get("pattern")
        entries = []
        for name in os.listdir(path):
            if not show_hidden and name.startswith('.'):
                continue
            if pattern and not re.search(pattern, name):
                continue

            full = os.path.join(path, name)
            st = os.stat(full)
            size = st.st_size
            # 格式化文件大小
            if size >= 1024 * 1024:
                size_str = f"{size / (1024 * 1024):.1f}M"
            elif size >= 1024:
                size_str = f"{size / 1024:.1f}K"
            else:
                size_str = f"{size}B"
            import time
            mtime = time.strftime('%Y-%m-%d %H:%M', time.localtime(st.st_mtime))
            kind = "[DIR]" if os.path.isdir(full) else "[FILE]"
            entries.append(f"{kind} {name}  {size_str}  {mtime}")

        # 排序：目录在前，然后按名称字母序
        entries.sort(key=lambda e: ("[DIR]" not in e, e.lower()))
        header = f"[目录] {os.path.abspath(path)} ({len(entries)} 项)"
        return header + "\n" + "\n".join(entries) if entries else header + "\n  (空)"
    except Exception as e:
        return f"Error: 列出目录失败: {e}"


def create_directory(**kwargs) -> str:
    """
    创建目录
    
    递归创建所有父目录，如果已存在则不报错。
    
    Args:
        path (str): 要创建的目录路径
        
    Returns:
        str: 成功消息或错误信息
    """
    path = kwargs.get("path", "")
    if not path:
        return "Error: 缺少参数 path"
    try:
        os.makedirs(path, exist_ok=True)
        return f"目录已创建: {os.path.abspath(path)}"
    except Exception as e:
        return f"Error: 创建目录失败: {e}"


def delete_path(**kwargs) -> str:
    """
    删除文件或目录
    
    删除目录时需要显式设置recursive=true以防止误删。
    
    Args:
        path (str): 要删除的路径
        recursive (bool, optional): 是否递归删除非空目录
        
    Returns:
        str: 删除结果或错误信息
    """
    path = kwargs.get("path", "")
    if not path:
        return "Error: 缺少参数 path"
    try:
        if not os.path.exists(path):
            return f"Error: 路径不存在: {path}"
        if os.path.isdir(path):
            if not kwargs.get("recursive"):
                return f"Error: 目录非空，请设置 recursive=true: {path}"
            shutil.rmtree(path)
            return f"已递归删除目录: {path}"
        else:
            os.remove(path)
            return f"已删除文件: {path}"
    except Exception as e:
        return f"Error: 删除失败: {e}"


def copy_move(**kwargs) -> str:
    """
    复制或移动文件/目录
    
    自动创建目标路径的父目录，支持跨设备移动。
    
    Args:
        src (str): 源路径
        dst (str): 目标路径
        action (str, optional): 操作类型，"copy"或"move"，默认"copy"
        
    Returns:
        str: 操作结果或错误信息
    """
    src = kwargs.get("src", "")
    dst = kwargs.get("dst", "")
    action = kwargs.get("action", "copy")
    if not src or not dst:
        return "Error: 缺少 src 或 dst 参数"
    if not os.path.exists(src):
        return f"Error: 源路径不存在: {src}"

    try:
        os.makedirs(os.path.dirname(os.path.abspath(dst)) or ".", exist_ok=True)
        if action == "move":
            shutil.move(src, dst)
            return f"已移动: {src} -> {dst}"
        else:
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
            return f"已复制: {src} -> {dst}"
    except Exception as e:
        return f"Error: {'移动' if action == 'move' else '复制'}失败: {e}"


def grep_files(**kwargs) -> str:
    """
    在文件中搜索正则表达式
    
    递归搜索目录，支持文件类型过滤、大小限制、忽略大小写等选项。
    
    Args:
        pattern (str): 正则表达式模式
        path (str, optional): 搜索路径，默认当前目录
        include (str, optional): 文件名通配符模式，默认"*"
        exclude (str, optional): 排除的文件名模式
        ignore_case (bool, optional): 是否忽略大小写，默认True
        max_results (int, optional): 最大返回结果数，默认50
        
    Returns:
        str: 匹配的行列列表或错误信息
    """
    pattern = kwargs.get("pattern", "")
    path_spec = kwargs.get("path", ".")
    if not pattern:
        return "Error: 缺少参数 pattern"

    try:
        compiled = re.compile(pattern)
    except re.error as e:
        return f"Error: 正则表达式无效: {e}"

    results = []
    max_results = int(kwargs.get("max_results", 50))
    include = kwargs.get("include", "*")
    exclude = kwargs.get("exclude")
    ignore_case = kwargs.get("ignore_case", True)

    # 编译正则（可选忽略大小写）
    if ignore_case and not (pattern.startswith('(?') and pattern.endswith(')')):
        compiled = re.compile(pattern, re.IGNORECASE)

    import fnmatch
    search_path = Path(path_spec)
    if not search_path.exists():
        return f"Error: 路径不存在: {path_spec}"

    # 递归查找文件
    files = search_path.rglob(include) if search_path.is_dir() else [search_path]
    for fp in files:
        if not fp.is_file():
            continue
        if exclude and fnmatch.fnmatch(fp.name, exclude):
            continue
        # 跳过大于2MB的文件
        if fp.stat().st_size > 2 * 1024 * 1024:
            continue
        try:
            for i, line in enumerate(open(fp, 'r', encoding='utf-8', errors='replace'), 1):
                if compiled.search(line):
                    results.append(f"{fp}:{i}: {line.rstrip()[:200]}")
                    if len(results) >= max_results:
                        break
        except Exception:
            pass
        if len(results) >= max_results:
            break

    if not results:
        return f"未找到匹配 '{pattern}' 的结果"
    suffix = f"\n... (共 {len(results)} 条)" if len(results) == max_results else ""
    return f"找到 {len(results)} 条:\n" + "\n".join(results) + suffix


def file_info(**kwargs) -> str:
    """
    获取文件/目录详细信息
    
    包括名称、路径、类型、大小、权限、MD5哈希值、时间戳等。
    
    Args:
        path (str): 文件或目录路径
        
    Returns:
        str: 格式化的文件信息或错误信息
    """
    path = kwargs.get("path", "")
    if not path or not os.path.exists(path):
        return f"Error: 路径不存在: {path}"

    try:
        st = os.stat(path)
        info = {
            "名称": os.path.basename(path),
            "完整路径": os.path.abspath(path),
            "类型": "目录" if os.path.isdir(path) else "文件",
            "大小": f"{st.st_size:,} 字节",
            "权限": oct(st.st_mode)[-3:],
        }
        # 计算文件MD5（仅对小文件）
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                info["MD5"] = hashlib.md5(f.read(65536)).hexdigest() if st.st_size < 10 * 1024 * 1024 else "(文件过大，跳过)"
        import time
        info["修改时间"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime))
        info["创建时间"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_ctime))
        return "\n".join(f"  {k}: {v}" for k, v in info.items())
    except Exception as e:
        return f"Error: 获取文件信息失败: {e}"


# ============================================================
# Shell 命令
# ============================================================

def run_shell(**kwargs) -> str:
    """
    执行 Shell 命令
    
    Windows下使用PowerShell，其他系统使用默认shell。
    支持超时控制、工作目录设置、stdin输入。
    
    Args:
        command (str): 要执行的命令
        timeout (int, optional): 超时秒数，默认60
        cwd (str, optional): 工作目录
        input (str, optional): stdin输入内容
        
    Returns:
        str: 命令输出或错误信息
    """
    command = kwargs.get("command", "")
    if not command:
        return "Error: 缺少参数 command"

    timeout = int(kwargs.get("timeout", 60))
    cwd = kwargs.get("cwd")
    input_str = kwargs.get("input")  # stdin

    try:
        # 根据操作系统选择shell
        if platform.system() == "Windows":
            proc = subprocess.Popen(
                ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                 "-Command", command],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=cwd, text=True, encoding='utf-8', errors='replace'
            )
        else:
            proc = subprocess.Popen(
                command, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=cwd, text=True, encoding='utf-8', errors='replace'
            )

        try:
            out, err = proc.communicate(input=input_str, timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            return f"命令超时 ({timeout}s)"

        if proc.returncode != 0:
            return f"退出码 {proc.returncode}: {err or out}"[:3000]

        # 截断过长输出
        if len(out) > 8000:
            out = out[:7000] + f"\n... (共 {len(out)} 字符，已截断)"

        return out or "(无输出)"
    except FileNotFoundError:
        return f"Error: powershell 未找到"
    except Exception as e:
        return f"Error: 执行命令失败: {e}"


# ============================================================
# 网络 / 搜索工具
# ============================================================

_WEB_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def web_search_tool(**kwargs) -> str:
    """
    Bing搜索引擎查询
    
    解析搜索结果页面，提取标题、链接和摘要。
    
    Args:
        query (str): 搜索关键词
        
    Returns:
        str: 格式化的搜索结果列表或错误信息
    """
    query = kwargs.get("query", "")
    if not query:
        return "Error: 缺少参数 query"

    try:
        url = f"https://www.bing.com/search?q={requests.utils.quote(query)}&setlang=zh-cn"
        resp = requests.get(url, headers=_WEB_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []

        # 提取标准搜索结果
        for li in soup.select("li.b_algo"):
            a = li.find("a", href=True)
            h2 = li.find("h2")
            p = li.find("p") or li.find("div", class_="b_caption")
            if a and h2:
                title = h2.get_text(strip=True)
                link = a["href"]
                desc = p.get_text(strip=True) if p else ""
                if title and not link.startswith("javascript:"):
                    results.append(f"{len(results) + 1}. {title}\n   {link}\n   {desc}")

        # 降级：尝试其他选择器
        if not results:
            for a_el in soup.select("h2 a, .b_title a"):
                href = a_el.get("href", "")
                title = a_el.get_text(strip=True)
                if title and href.startswith("http"):
                    results.append(f"{len(results) + 1}. {title}\n   {href}")

        if results:
            return "\n".join(results[:10])
        return f"搜索 '{query}' 未找到结果，请优化关键词"

    except requests.RequestException as e:
        return f"网络请求错误: {e}"
    except Exception as e:
        return f"搜索失败: {e}"


def web_content_tool(**kwargs) -> str:
    """
    获取网页纯文本内容
    
    移除脚本、样式、导航等无关元素，提取主要内容区域。
    支持多个URL批量处理。
    
    Args:
        urls (Union[str, List[str]]): URL或URL列表
        
    Returns:
        str: 提取的网页文本内容，每个URL用分隔线分开
    """
    urls = kwargs.get("urls")
    if isinstance(urls, str):
        urls = [urls]
    if not urls or not isinstance(urls, list):
        return "Error: 缺少参数 urls (URL 列表)"

    all_parts = []
    for i, url in enumerate(urls, 1):
        try:
            resp = requests.get(url, headers=_WEB_HEADERS, timeout=15, allow_redirects=True)
            resp.raise_for_status()
            if resp.apparent_encoding:
                resp.encoding = resp.apparent_encoding

            soup = BeautifulSoup(resp.text, "html.parser")
            # 移除无关标签
            for tag in soup(["script", "style", "nav", "footer", "header", "aside",
                             "noscript", "iframe", "form"]):
                tag.decompose()

            # 优先提取主要内容区域
            main = (soup.select_one("main, article, .content, #content, .post, .article, [role='main']")
                    or soup.body or soup)
            text = main.get_text(separator="\n")
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            cleaned = "\n".join(lines)[:3000]

            if len(lines) > 200:
                cleaned = cleaned[:2500] + f"\n... (共 {len(lines)} 行，已截断)"

            all_parts.append(f"=== 网页 {i}: {url} ===\n{cleaned}\n")
        except requests.RequestException as e:
            all_parts.append(f"=== 网页 {i}: {url} ===\nError: 请求失败: {e}\n")
        except Exception as e:
            all_parts.append(f"=== 网页 {i}: {url} ===\nError: {e}\n")

    total = "\n".join(all_parts)
    if len(total) > 10000:
        total = total[:9000] + "\n... (超出长度限制，已截断)"
    return total


# ============================================================
# 实用工具
# ============================================================

def talk_tool(**kwargs) -> str:
    """
    对话工具 - 返回用户消息
    
    用于Agent直接回复用户，不进行工具调用。
    
    Args:
        message/content/text (str): 要回复的消息
        
    Returns:
        str: 消息内容
    """
    message = kwargs.get("message") or kwargs.get("content") or kwargs.get("text", "")
    return message or "(空消息)"


def finish_tool(**kwargs) -> str:
    """
    完成任务工具
    
    标记任务已完成，返回最终结果。
    
    Args:
        response (str): 任务完成时的响应消息
        
    Returns:
        str: 完成消息，默认"任务完成"
    """
    return kwargs.get("response", "任务完成")


def speaking_tool(**kwargs) -> str:
    """
    文字转语音工具
    
    使用pyttsx3库进行本地TTS合成并播放。
    
    Args:
        text (str): 要朗读的文本
        rate (int, optional): 语速，默认150
        volume (float, optional): 音量（0.0-1.0），默认1.0
        
    Returns:
        str: 执行结果或错误信息
    """
    if pyttsx3 is None:
        return "Error: pyttsx3 未安装"

    text = kwargs.get("text", "")
    if not text:
        return "Error: 缺少参数 text"
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', kwargs.get("rate", 150))
        engine.setProperty('volume', kwargs.get("volume", 1.0))
        engine.say(text)
        engine.runAndWait()
        return "语音播放成功"
    except Exception as e:
        return f"Error: 语音播放失败: {e}"


def python_exec_tool(**kwargs) -> str:
    """
    执行 Python 代码片段
    
    在隔离的安全环境中执行代码，限制可用的内置函数和模块。
    捕获stdout输出作为返回值。
    
    Args:
        code (str): 要执行的Python代码
        
    Returns:
        str: 代码的输出结果或错误信息
    """
    code = kwargs.get("code", "")
    if not code:
        return "Error: 缺少参数 code"

    # 定义安全的命名空间，限制可用功能
    _real_builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
    safe_globals = {
        "__builtins__": {
            "print": print, "len": len, "range": range, "int": int, "float": float,
            "str": str, "bool": bool, "list": list, "dict": dict, "set": set,
            "tuple": tuple, "enumerate": enumerate, "zip": zip, "map": map,
            "filter": filter, "sorted": sorted, "reversed": reversed, "min": min,
            "max": max, "sum": sum, "abs": abs, "round": round, "hash": hash,
            "type": type, "isinstance": isinstance, "hasattr": hasattr,
            "getattr": getattr, "Exception": Exception, "ValueError": ValueError,
            "TypeError": TypeError, "KeyError": KeyError, "IndexError": IndexError,
            "open": open, "__import__": __import__,
            "__orig_import__": _real_builtins.get("__orig_import__", __import__),
        },
        "os": os, "sys": sys, "re": re, "json": __import__('json'),
        "datetime": __import__('datetime'), "math": __import__('math'),
        "Path": Path, "platform": platform,
    }

    import io as _io
    try:
        # 重定向stdout以捕获输出
        old_stdout = sys.stdout
        captured = _io.StringIO()
        sys.stdout = captured
        try:
            exec(code, safe_globals, {})
        finally:
            sys.stdout = old_stdout
        output = captured.getvalue()
        if output.strip():
            return output.strip()[:3000]
        return "(执行成功，无输出)"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"
    
def load_skill_tool(**kwargs) -> str:
    """
    加载技能(skill)完整内容

    按名称加载 SKILL.md 全文到对话中，帮助 AI 按标准流程执行任务。

    Args:
        name (str): 技能名称

    Returns:
        str: SKILL.md 完整内容或错误信息
    """
    from core.skills import SkillManager
    name = kwargs.get("name", "")
    if not name:
        return "Error: 缺少参数 name"
    mgr = SkillManager()
    skill = mgr.find(name)
    if skill is None:
        available = ", ".join(s["name"] for s in mgr.scan())
        return f"Error: 未找到 skill '{name}'\n可用技能: {available}"
    content = mgr.load(name)
    if content is None:
        return f"Error: 读取 skill '{name}' 失败"
    return content


def serial_send_tool(**kwargs) -> str:
    """
    串口发送工具
    
    Args:
        port (str): 串口名称
        baudrate (int): 波特率
        data (str): 要发送的数据
        encoding (str): 数据编码方式，可选"text"或"hex"
        timeout (float): 读取响应的超时时间
        read_response (bool): 是否读取响应数据
        
    Returns:
        str: 执行结果或错误信息
    """
    port = kwargs.get("port", "COM5") # 默认串口名称    
    baudrate = kwargs.get("baudrate", 115200)
    data = kwargs.get("data", "")
    if not data:
        return "Error: 缺少参数 data"
    encoding = kwargs.get("encoding", "text")
    timeout = float(kwargs.get("timeout", 1.0))
    read_response = kwargs.get("read_response", False)

    try:
        payload = bytes.fromhex(data) if encoding == "hex" else data.encode("utf-8")
    except ValueError as e:
        return f"Error: hex 格式错误: {e}"
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        ser.write(payload)
        result = f"已发送 {len(payload)} 字节到 {port}@{baudrate}"
        if read_response:
            # 机械臂响应较慢（约1s），持续读取直到超时无新数据
            response = b""
            deadline = time.time() + timeout
            ser.timeout = 0.2  # 每次 read 最多等 200ms
            while time.time() < deadline:
                try:
                    chunk = ser.read(1024)
                    if chunk:
                        response += chunk
                    elif response:
                        # 有数据后连续 200ms 无新数据 → 响应结束
                        break
                except:
                    break
            text = response.decode("utf-8", errors="replace").strip()
            if text:
                result += f"\n响应: {text}"
        ser.close()
        return result
    except serial.SerialException as e:
        return f"Error: 串口错误: {e}"


    



