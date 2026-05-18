import subprocess
import sys
import os
import platform
import shutil
import stat
import re
import hashlib
from pathlib import Path
from typing import Any
import requests
from bs4 import BeautifulSoup
import chardet
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


def _auto_encode(file_path: str) -> str:
    """自动检测文件编码并读取"""
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
    """读取文件内容"""
    file_path = kwargs.get("file_path") or kwargs.get("path")
    if not file_path:
        return "Error: 缺少参数 file_path"
    if not os.path.isfile(file_path):
        return f"Error: 文件不存在: {file_path}"

    try:
        if os.path.getsize(file_path) > 5 * 1024 * 1024:
            return f"Error: 文件过大 ({os.path.getsize(file_path) // 1024}KB)，超过 5MB 限制"

        content = _auto_encode(file_path)
        lines = content.splitlines(keepends=True)

        if "search" in kwargs:
            found = []
            for i, li in enumerate(lines, 1):
                if kwargs["search"] in li:
                    found.append(f"L{i}: {li.rstrip()}")
            return "\n".join(found) if found else f"未找到: '{kwargs['search']}'"

        start = int(kwargs.get("start_line", 1))
        end = kwargs.get("end_line")
        if end is not None:
            end = int(end)
            if start < 1 or end < start or end > len(lines):
                return f"Error: 行号无效，文件共 {len(lines)} 行"
            return "".join(lines[start - 1:end])

        if start > 1:
            return "".join(lines[start - 1:])

        max_lines = kwargs.get("max_lines", 500)
        if isinstance(max_lines, str):
            max_lines = int(max_lines)
        if len(lines) > max_lines:
            return "".join(lines[:max_lines]) + f"\n... (共 {len(lines)} 行，已截断前 {max_lines} 行)"
        return content

    except Exception as e:
        return f"Error: 读取文件失败: {e}"


def write_file_tool(**kwargs) -> str:
    """写入文件内容"""
    file_path = kwargs.get("file_path") or kwargs.get("path")
    content = kwargs.get("content")
    if not file_path:
        return "Error: 缺少参数 file_path"
    if content is None:
        return "Error: 缺少参数 content"

    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)) or ".", exist_ok=True)

        if kwargs.get("append"):
            mode = 'a'
        else:
            mode = 'w'
            if kwargs.get("backup") and os.path.isfile(file_path):
                bak = file_path + ".bak"
                shutil.copy2(file_path, bak)

        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)

        size = os.path.getsize(file_path)
        return f"写入成功: {file_path} ({size} 字节)"
    except Exception as e:
        return f"Error: 写入文件失败: {e}"


def replace_content_tool(**kwargs) -> str:
    """替换文件内容（支持精确匹配、正则、计数）"""
    file_path = kwargs.get("file_path") or kwargs.get("path")
    old_val = kwargs.get("old_content", "")
    new_val = kwargs.get("new_content", "")
    if not file_path:
        return "Error: 缺少参数 file_path"

    try:
        if not os.path.isfile(file_path):
            return f"Error: 文件不存在: {file_path}"
        content = _auto_encode(file_path)
    except Exception as e:
        return f"Error: 读取文件失败: {e}"

    use_regex = kwargs.get("regex", False)
    count = int(kwargs.get("count", 0) or 0)

    if use_regex:
        try:
            new_content, n = re.subn(old_val, new_val, content, count=count if count > 0 else 0)
        except re.error as e:
            return f"Error: 正则表达式无效: {e}"
    else:
        if old_val not in content:
            return f"Error: 文件中未找到要替换的内容"
        if count > 1:
            new_content = content.replace(old_val, new_val, count)
            n = min(count, content.count(old_val))
        else:
            new_content = content.replace(old_val, new_val, 1)
            n = 1 if old_val in content else 0

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
    """列出目录内容（含文件大小、修改时间、类型）"""
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

        entries.sort(key=lambda e: ("[DIR]" not in e, e.lower()))
        header = f"[目录] {os.path.abspath(path)} ({len(entries)} 项)"
        return header + "\n" + "\n".join(entries) if entries else header + "\n  (空)"
    except Exception as e:
        return f"Error: 列出目录失败: {e}"


def create_directory(**kwargs) -> str:
    """创建目录"""
    path = kwargs.get("path", "")
    if not path:
        return "Error: 缺少参数 path"
    try:
        os.makedirs(path, exist_ok=True)
        return f"目录已创建: {os.path.abspath(path)}"
    except Exception as e:
        return f"Error: 创建目录失败: {e}"


def delete_path(**kwargs) -> str:
    """删除文件或目录"""
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
    """复制或移动文件/目录"""
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
    """在文件中搜索正则表达式"""
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

    if ignore_case and not (pattern.startswith('(?') and pattern.endswith(')')):
        compiled = re.compile(pattern, re.IGNORECASE)

    import fnmatch
    search_path = Path(path_spec)
    if not search_path.exists():
        return f"Error: 路径不存在: {path_spec}"

    files = search_path.rglob(include) if search_path.is_dir() else [search_path]
    for fp in files:
        if not fp.is_file():
            continue
        if exclude and fnmatch.fnmatch(fp.name, exclude):
            continue
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
    """获取文件/目录详细信息"""
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
    """执行 Shell 命令 (Windows PowerShell)"""
    command = kwargs.get("command", "")
    if not command:
        return "Error: 缺少参数 command"

    timeout = int(kwargs.get("timeout", 60))
    cwd = kwargs.get("cwd")
    input_str = kwargs.get("input")  # stdin

    try:
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
    """Bing 搜索"""
    query = kwargs.get("query", "")
    if not query:
        return "Error: 缺少参数 query"

    try:
        url = f"https://www.bing.com/search?q={requests.utils.quote(query)}&setlang=zh-cn"
        resp = requests.get(url, headers=_WEB_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []

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
    """获取网页纯文本内容"""
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
            for tag in soup(["script", "style", "nav", "footer", "header", "aside",
                             "noscript", "iframe", "form"]):
                tag.decompose()

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
    message = kwargs.get("message") or kwargs.get("content") or kwargs.get("text", "")
    return message or "(空消息)"


def finish_tool(**kwargs) -> str:
    return kwargs.get("response", "任务完成")


def weather_tool(**kwargs) -> str:
    """天气查询 (wttr.in)"""
    city = kwargs.get("city", "")
    if not city:
        return "Error: 缺少参数 city"
    try:
        fmt = "4" if kwargs.get("detail") else "3"
        url = f"https://wttr.in/{requests.utils.quote(city)}?format={fmt}&lang=zh"
        resp = requests.get(url, headers=_WEB_HEADERS, timeout=10)
        if resp.status_code == 200:
            text = resp.text.strip()
            if "Unknown" in text or "Sorry" in text:
                return f"找不到城市: {city}"
            return text
        return f"HTTP {resp.status_code}"
    except Exception as e:
        return f"Error: {e}"


def speaking_tool(**kwargs) -> str:
    """文字转语音"""
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
    """执行 Python 代码片段（隔离环境）"""
    code = kwargs.get("code", "")
    if not code:
        return "Error: 缺少参数 code"

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
        },
        "os": os, "sys": sys, "re": re, "json": __import__('json'),
        "datetime": __import__('datetime'), "math": __import__('math'),
        "Path": Path, "platform": platform,
    }

    import io as _io
    try:
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
