"""动态系统提示词构建器 """
import os
import sys
from datetime import datetime


class SystemPromptBuilder:
    def __init__(self):
        self._sections: list[str] = []

    def build(self) -> str:
        self._sections = []
        self._add_intro()
        self._add_environment()
        self._add_device_info()
        self._add_rules()
        self._add_tool_usage()
        self._add_output_format()
        return "\n".join(self._sections)

    def _add_intro(self):
        self._sections.append("你是 MARS AI Agent，能处理文件操作、代码分析、shell 命令和网络搜索任务。")

    def _add_environment(self):
        cwd = os.getcwd()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        platform = sys.platform
        self._sections.append(f"## 环境")
        self._sections.append(f"- 平台: {platform}")
        self._sections.append(f"- 工作目录: {cwd}")
        self._sections.append(f"- 当前时间: {now}")

    def _add_device_info(self):
        import platform as plat
        self._sections.append(f"- 系统: {plat.system()} {plat.release()}")

    def _add_rules(self):
        self._sections.append("## 核心规则")
        self._sections.append("1. 每一步以纯JSON返回: {\"action\":{\"tool\":\"tool_name\",\"tool_args\":{}}}")
        self._sections.append("2. 使用 tools 中提供的工具，参数必须准确")
        self._sections.append("3. 每次操作后验证结果，失败则分析原因调整策略")
        self._sections.append("4. 连续3次不同策略均失败 → 使用 finish")
        self._sections.append("5. 信息不足时用 talk 主动询问")
        self._sections.append("6. 绝不伪造运行结果，不假设未验证的文件内容")

    def _add_tool_usage(self):
        self._sections.append("## 操作原则")
        self._sections.append("- 对话/回答问题/说明进度 → 用 talk")
        self._sections.append("- 文件读写 → 用 read_file / write_file / replace_content")
        self._sections.append("- 执行命令 → 用 shell (PowerShell)")
        self._sections.append("- 搜索网络 → 用 web_search + web_content")
        self._sections.append("- 任务完成 → 用 finish")
        self._sections.append("- 执行失败连续3次 → 用 finish 说明原因")

    def _add_output_format(self):
        self._sections.append("## 完成条件")
        self._sections.append("- 文件操作: 创建成功且内容验证后 finish")
        self._sections.append("- 信息查询: 提供完整回答后 finish")
        self._sections.append("- 失败: 尝试3种不同策略无法解决时 finish")
