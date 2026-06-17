"""
技能管理器

自动扫描标准目录发现 SKILL.md，支持按名称查找和按需加载。
"""
import os
from pathlib import Path


class SkillManager:
    """扫描、查找、加载技能"""

    SCAN_DIRS = [
        ".agents/skills",
        ".claude/skills",
        ".opencode/skills",
    ]

    GLOBAL_DIRS = [
        "~/.agents/skills",
        "~/.claude/skills",
        "~/.config/opencode/skills",
    ]

    def __init__(self):
        self._cache = None

    def _scan_dirs(self) -> list[Path]:
        dirs = []
        cwd = Path.cwd()
        for d in self.SCAN_DIRS:
            p = cwd / d
            if p.is_dir():
                dirs.append(p)
        for d in self.GLOBAL_DIRS:
            p = Path(d).expanduser()
            if p.is_dir():
                dirs.append(p)
        return dirs

    def scan(self) -> list[dict]:
        """扫描所有目录，返回 [{name, description, path}]"""
        if self._cache is not None:
            return self._cache
        skills = []
        seen = set()
        for base in self._scan_dirs():
            for entry in sorted(base.iterdir()):
                if not entry.is_dir():
                    continue
                skill_file = entry / "SKILL.md"
                if not skill_file.exists():
                    continue
                name = entry.name
                if name in seen:
                    continue
                seen.add(name)
                desc = self._read_description(skill_file)
                skills.append({
                    "name": name,
                    "description": desc,
                    "path": str(skill_file.resolve()),
                })
        self._cache = skills
        return skills

    def _read_description(self, path: Path) -> str:
        try:
            content = path.read_text("utf-8")
        except Exception:
            return ""
        if not content.startswith("---"):
            return ""
        end = content.find("---", 3)
        if end == -1:
            return ""
        frontmatter = content[3:end].strip()
        for line in frontmatter.splitlines():
            line = line.strip()
            if line.startswith("description:"):
                val = line[len("description:"):].strip().strip('"').strip("'")
                return val
        return ""

    def find(self, name: str) -> dict | None:
        """按名称查找技能"""
        for s in self.scan():
            if s["name"] == name:
                return s
        return None

    def load(self, name: str) -> str | None:
        """加载技能的完整 SKILL.md 内容"""
        skill = self.find(name)
        if skill is None:
            return None
        try:
            with open(skill["path"], "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None

    def clear_cache(self):
        self._cache = None
