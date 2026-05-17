from enum import IntEnum
from typing import Tuple


class PermissionMode(IntEnum):
    READ_ONLY = 0
    WORKSPACE_WRITE = 1
    DANGER_FULL = 2
    ALL = 3


TOOL_PERMISSIONS = {
    "read_file": PermissionMode.READ_ONLY,
    "web_search": PermissionMode.READ_ONLY,
    "web_content": PermissionMode.READ_ONLY,
    "shell": PermissionMode.DANGER_FULL,
    "write_file": PermissionMode.WORKSPACE_WRITE,
    "replace_content": PermissionMode.WORKSPACE_WRITE,
    "talk": PermissionMode.READ_ONLY,
    "finish": PermissionMode.READ_ONLY,
    "weather": PermissionMode.READ_ONLY,
    "speaking": PermissionMode.READ_ONLY,
}


class PermissionPolicy:
    def __init__(self, mode: PermissionMode = PermissionMode.DANGER_FULL):
        self.mode = mode

    def authorize(self, tool_name: str) -> Tuple[bool, str]:
        required = TOOL_PERMISSIONS.get(tool_name, PermissionMode.DANGER_FULL)
        if self.mode >= required:
            return True, ""
        return False, f"当前权限模式({self.mode.name})不允许使用 {tool_name}(需要{required.name})"

    def set_mode(self, mode: PermissionMode):
        self.mode = mode
