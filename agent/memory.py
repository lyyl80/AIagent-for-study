from typing import Dict, Any, List, Optional
import json
import os


class Memory:
    """记忆管理系统
    
    基于OpenCode架构设计，支持对话历史记录和记忆管理。
    提供短期记忆（最近对话）和长期记忆（总结）功能。
    """
    
    def __init__(self, max_history: int = 100, persist_path: Optional[str] = None):
        """初始化记忆系统
        
        参数:
            max_history: 最大历史记录条数
            persist_path: 持久化存储路径，如果为None则不持久化
        """
        self.history: List[Dict[str, Any]] = []
        self.max_history = max_history
        self.persist_path = persist_path
        self.summary = ""
        
        # 如果存在持久化文件，加载历史记录
        if persist_path and os.path.exists(persist_path):
            self.load()
    
    def add_conversation(self, conversation: Dict[str, Any]) -> None:
        """添加对话记录
        
        参数:
            conversation: 对话记录字典，包含input、output、reflect等字段
        """
        self.history.append(conversation)
        
        # 限制历史记录长度
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # 自动保存
        if self.persist_path:
            self.save()
    
    def get_history(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取历史记录
        
        参数:
            n: 返回最近n条记录，如果为None则返回全部
            
        返回:
            List[Dict[str, Any]]: 历史记录列表
        """
        if n is None:
            return self.history
        return self.history[-n:]
    
    def get_recent_steps(self, steps: int = 3) -> List[Dict[str, Any]]:
        """获取最近的步骤（用于提示词构建）
        
        参数:
            steps: 步骤数量
            
        返回:
            List[Dict[str, Any]]: 最近的步骤记录
        """
        return self.get_history(steps)
    
    def clear(self) -> None:
        """清空历史记录"""
        self.history.clear()
        self.summary = ""
        
        if self.persist_path:
            self.save()
    
    def set_summary(self, summary: str) -> None:
        """设置记忆总结
        
        参数:
            summary: 总结文本
        """
        self.summary = summary
        
        if self.persist_path:
            self.save()
    
    def get_summary(self) -> str:
        """获取记忆总结
        
        返回:
            str: 总结文本
        """
        return self.summary
    
    def save(self) -> None:
        """保存记忆到文件"""
        if not self.persist_path:
            return
        
        data = {
            "history": self.history,
            "summary": self.summary,
            "max_history": self.max_history
        }
        
        try:
            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记忆失败: {e}")
    
    def load(self) -> None:
        """从文件加载记忆"""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return
        
        try:
            with open(self.persist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.history = data.get("history", [])
            self.summary = data.get("summary", "")
            self.max_history = data.get("max_history", 100)
        except Exception as e:
            print(f"加载记忆失败: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        返回:
            Dict[str, Any]: 记忆字典表示
        """
        return {
            "history": self.history,
            "summary": self.summary,
            "max_history": self.max_history
        }
    
    def __len__(self) -> int:
        """获取历史记录数量"""
        return len(self.history)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Memory(history={len(self.history)}, summary={len(self.summary)} chars)"