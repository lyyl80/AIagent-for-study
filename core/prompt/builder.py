"""
系统提示词构建器模块

动态生成AI代理的系统提示词，包含：
- 环境信息（平台、工作目录、时间）
- 设备信息（操作系统版本）
- 核心行为规则
- 工具使用指南
- 输出格式规范

确保Agent了解自身能力边界和操作约束。
"""
import os
import sys
from datetime import datetime


class SystemPromptBuilder:
    """
    系统提示词构建器类
    
    通过模块化方法构建完整的系统提示词，每个部分独立管理。
    支持动态注入运行时环境信息。
    
    Attributes:
        _sections (list[str]): 提示词的各个段落列表
    """
    
    def __init__(self):
        """初始化构建器，创建空的段落列表"""
        self._sections: list[str] = []

    def build(self) -> str:
        """
        构建完整的系统提示词
        
        按顺序添加所有段落，然后用换行符连接。
        
        Returns:
            str: 完整的系统提示词文本
        """
        self._sections = []
        self._add_intro()           # 角色介绍
        self._add_environment()     # 环境信息
        self._add_device_info()     # 设备信息
        self._add_rules()           # 核心规则
        self._add_tool_usage()      # 工具使用说明
        self._add_output_format()   # 输出格式要求
        return "\n".join(self._sections)

    def _add_intro(self):
        """添加角色介绍段落"""
        self._sections.append("你是 MARS AI Agent，能处理文件操作、代码分析、shell 命令和网络搜索任务。")

    def _add_environment(self):
        """添加运行时环境信息"""
        cwd = os.getcwd()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        platform = sys.platform
        self._sections.append(f"## 环境")
        self._sections.append(f"- 平台: {platform}")
        self._sections.append(f"- 工作目录: {cwd}")
        self._sections.append(f"- 当前时间: {now}")

    def _add_device_info(self):
        """添加设备详细信息"""
        import platform as plat
        self._sections.append(f"- 系统: {plat.system()} {plat.release()}")

    def _add_rules(self):
        """添加核心行为规则"""
        self._sections.append("## 核心规则")
        self._sections.append("1. 每一步以纯JSON返回: {\"action\":{\"tool\":\"tool_name\",\"tool_args\":{}}}")
        self._sections.append("2. 使用 tools 中提供的工具，参数必须准确")
        self._sections.append("3. 每次操作后验证结果，失败则分析原因调整策略")
        self._sections.append("4. 连续3次不同策略均失败 → 使用 finish")
        self._sections.append("5. 信息不足时用 talk 主动询问，绝不输出空工具名")
        self._sections.append("6. 绝不伪造运行结果，不假设未验证的文件内容")

    def _add_tool_usage(self):
        """添加工具使用指南"""
        self._sections.append("## 操作原则")
        self._sections.append("- 对话/回答问题 → talk, tool_args: {\"message\": \"...\"}")
        self._sections.append("- 文件读写 → read_file(path)/write_file(path,content)/replace_content(path,old,new)")
        self._sections.append("- 执行命令 → shell, tool_args: {\"command\": \"...\"}")
        self._sections.append("- 网络搜索 → web_search, tool_args: {\"query\": \"...\"}")
        self._sections.append("- 获取网页 → web_content, tool_args: {\"urls\": [\"...\"]}")
        self._sections.append("- 列出目录 → list_directory, grep_files 搜索文件内容")
        self._sections.append("- 文件管理 → create_directory/delete_path/copy_move/file_info")
        self._sections.append("- Python执行 → python_exec, tool_args: {\"code\": \"...\"}")
        self._sections.append("- 任务完成 → finish, tool_args: {\"response\": \"完成说明\"}")
        self._sections.append("- 执行失败连续3次 → 用 finish")

    def _add_output_format(self):
        """添加输出格式和完成条件"""
        self._sections.append("## 完成条件")
        self._sections.append("- 文件操作: 创建成功且内容验证后 finish")
        self._sections.append("- 信息查询: 提供完整回答后 finish")
        self._sections.append("- 失败: 尝试3种不同策略无法解决时 finish")
