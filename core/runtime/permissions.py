"""
权限管理模块

定义工具调用的权限级别和授权策略，确保AI代理只能执行允许的操作。
支持四种权限模式：只读、工作区写入、危险操作、完全开放。
"""
from enum import IntEnum
from typing import Tuple


class PermissionMode(IntEnum):
    """
    权限模式枚举
    
    定义不同级别的工具调用权限，数值越大权限越高。
    
    Attributes:
        READ_ONLY (0): 只读权限，仅允许查询类工具
        WORKSPACE_WRITE (1): 工作区写入权限，允许修改文件
        DANGER_FULL (2): 危险操作权限，允许执行Shell命令等
        ALL (3): 完全开放权限（预留）
    """
    READ_ONLY = 0
    WORKSPACE_WRITE = 1
    DANGER_FULL = 2
    ALL = 3


# 工具权限映射表
# 将每个工具映射到所需的最低权限级别
TOOL_PERMISSIONS = {
    "read_file": PermissionMode.READ_ONLY,
    "web_search": PermissionMode.READ_ONLY,
    "web_content": PermissionMode.READ_ONLY,
    "shell": PermissionMode.DANGER_FULL,
    "write_file": PermissionMode.WORKSPACE_WRITE,
    "replace_content": PermissionMode.WORKSPACE_WRITE,
    "talk": PermissionMode.READ_ONLY,
    "finish": PermissionMode.READ_ONLY,
    "speaking": PermissionMode.READ_ONLY,
    "list_directory": PermissionMode.READ_ONLY,
    "grep_files": PermissionMode.READ_ONLY,
    "file_info": PermissionMode.READ_ONLY,
    "create_directory": PermissionMode.WORKSPACE_WRITE,
    "delete_path": PermissionMode.WORKSPACE_WRITE,
    "copy_move": PermissionMode.WORKSPACE_WRITE,
    "python_exec": PermissionMode.DANGER_FULL,
    "serial_send": PermissionMode.DANGER_FULL,
    "load_skill": PermissionMode.READ_ONLY,
}


class PermissionPolicy:
    """
    权限策略类
    
    根据当前权限模式判断是否允许执行特定工具。
    提供灵活的权限控制和错误提示。
    
    Attributes:
        mode (PermissionMode): 当前权限模式
    """
    
    def __init__(self, mode: PermissionMode = PermissionMode.DANGER_FULL):
        """
        初始化权限策略
        
        Args:
            mode (PermissionMode): 初始权限模式，默认DANGER_FULL
        """
        self.mode = mode

    def authorize(self, tool_name: str) -> Tuple[bool, str]:
        """
        检查工具调用是否被授权
        
        比较当前权限模式和工具所需权限，返回授权结果和错误消息。
        
        Args:
            tool_name (str): 要检查的工具名称
            
        Returns:
            Tuple[bool, str]: (是否授权, 错误消息)，授权成功时错误消息为空字符串
        """
        required = TOOL_PERMISSIONS.get(tool_name, PermissionMode.DANGER_FULL)
        if self.mode >= required:
            return True, ""
        return False, f"当前权限模式({self.mode.name})不允许使用 {tool_name}(需要{required.name})"

    def set_mode(self, mode: PermissionMode):
        """
        动态修改权限模式
        
        Args:
            mode (PermissionMode): 新的权限模式
        """
        self.mode = mode
