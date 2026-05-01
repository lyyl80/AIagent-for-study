from typing import Dict, Any, List, Optional
import json
import os
import re
from datetime import datetime


def generate_session_summary(messages: List[Dict[str, Any]], max_length: int = 30) -> str:
    """生成会话摘要，用于文件名
    
    Args:
        messages: 会话消息列表
        max_length: 摘要最大长度
    
    Returns:
        str: 会话摘要
    """
    if not messages:
        return ""
    
    # 提取用户的问题作为摘要
    user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
    
    if not user_messages:
        return "无用户输入"
    
    # 使用第一个用户问题作为基础
    first_question = user_messages[0].strip()
    
    # 清理文本：移除特殊字符，保留中文、英文、数字
    cleaned_text = re.sub(r'[^\u4e00-\u9fff\w\s]', '', first_question)
    
    # 限制长度
    if len(cleaned_text) > max_length:
        # 按字符截取，确保不切分单词
        cleaned_text = cleaned_text[:max_length].rsplit(' ', 1)[0] + "..."
    
    # 移除多余空格
    cleaned_text = ' '.join(cleaned_text.split())
    
    return cleaned_text if cleaned_text else "会话"


def create_session_filename(session_id: str, messages: List[Dict[str, Any]]) -> str:
    """创建带摘要的会话文件名
    
    Args:
        session_id: 会话ID（时间戳）
        messages: 会话消息列表
    
    Returns:
        str: 完整的文件名（不含扩展名）
    """
    summary = generate_session_summary(messages)
    # 确保文件名安全，移除可能引起问题的字符
    safe_summary = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', summary)
    return f"{session_id}_{safe_summary}"


class Memory:
    """记忆管理系统
    
    基于OpenCode架构设计，支持对话历史记录和记忆管理。
    提供短期记忆（最近对话）和长期记忆（总结）功能。
    """
    
    def __init__(self, max_history: int = 100,  
                 session_id: Optional[str] = None, user_input: Optional[str] = None):
        """初始化记忆系统
        
        参数:
            max_history: 最大历史记录条数
            user_input: 用户输入
            session_id: 会话ID，如果为None则自动生成
            messages: 初始消息列表，如果为None则为空列表
        """
        self.history: List[Dict[str, Any]] = []  # 步骤历史记录
        self.messages: List[Dict[str, Any]] = []  
        self.max_history = max_history

        self.user_input = user_input
        
        # 生成会话ID
        self.session_id = session_id or datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # 创建初始消息列表用于生成文件名
        initial_messages = [{"role": "user", "content": user_input}] if user_input else []
        
        # 生成会话摘要和文件名
        self.filename = create_session_filename(self.session_id, initial_messages)
        self.created_time = datetime.now().isoformat()
        self.persist_path = f"session/{self.filename}.json"
        

    
    def add_conversation(self, conversation: Dict[str, Any]) -> None:
        """添加步骤历史记录
        
        参数:
            conversation: 步骤记录字典，包含input、output、reflect等字段
        """
        self.history.append(conversation)
        
        # 限制历史记录长度
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # 自动保存
        if self.persist_path:
            self.save()
    
    def add_message(self, role: str, content: str) -> None:
        """添加对话消息
        
        参数:
            role: 角色（user/assistant）
            content: 消息内容
        """
        self.history.append({
            "role": role,
            "content": content
        })
        
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
    
    
    def clear(self) -> None:
        """清空历史记录和消息"""
        self.history.clear()
    
        
        if self.persist_path:
            self.save()

    
    def save(self) -> None:
        """保存记忆到文件"""
        if not self.persist_path:
            return
        
        data = {
            "session_id": self.session_id,
            "filename": self.filename,
            "history": self.history,  
            "max_history": self.max_history,
            "created_time": self.created_time
        }
        
        try:
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
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
            
            # 加载新格式数据
            self.session_id = data.get("session_id", self.session_id)
            self.filename = data.get("filename", self.filename)
            self.created_time = data.get("created_time", self.created_time)
            self.history = data.get("history", self.history)
            self.max_history = data.get("max_history", self.max_history)
        except Exception as e:
            print(f"加载记忆失败: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        返回:
            Dict[str, Any]: 记忆字典表示
        """
        return {
            "session_id": self.session_id,
            "filename": self.filename,
            "history": self.history,
            "max_history": self.max_history,
            "created_time": self.created_time
        }
    
    @staticmethod
    def list_sessions() -> List[Dict[str, Any]]:
        """列出所有已保存的会话
        
        返回:
            List[Dict[str, Any]]: 会话列表
        """
        sessions_list = []
        session_dir = "session"
        
        if os.path.exists(session_dir):
            for file_name in os.listdir(session_dir):
                if file_name.endswith(".json"):
                    try:
                        with open(f"{session_dir}/{file_name}", "r", encoding="utf-8") as f:
                            session_data = json.load(f)
                            if "filename" not in session_data:
                                session_data["filename"] = file_name[:-5]
                            sessions_list.append(session_data)
                    except Exception as e:
                        # 如果文件损坏，仍然显示基本文件名
                        sessions_list.append({
                            "filename": file_name[:-5],
                            "session_id": file_name[:-5].split('_')[0] if '_' in file_name else file_name[:-5],
                            "created_time": "未知"
                        })
        
        # 按创建时间排序（新的在前）
        sessions_list.sort(key=lambda x: x.get("created_time", ""), reverse=True)
        return sessions_list
    
    @staticmethod
    def load_session(filename: str) -> 'Memory':
        """加载指定会话
        
        参数:
            filename: 会话文件名（不含扩展名）
        
        返回:
            Memory: 加载的记忆实例
        """
        session_path = f"session/{filename}.json"
        if not os.path.exists(session_path):
            # 如果找不到，尝试按文件名查找（不带扩展名）
            for fname in os.listdir("session"):
                if fname.startswith(filename) and fname.endswith(".json"):
                    session_path = f"session/{fname}"
                    break
        
        if not os.path.exists(session_path):
            raise FileNotFoundError(f"会话文件 {filename} 不存在")
        
        try:
            with open(session_path, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            
            # 从加载的数据创建Memory实例
            memory = Memory(
                max_history=session_data.get("max_history", 100),
                session_id=session_data.get("session_id"),
            )
            
            # 手动设置其他属性（因为load方法不会在初始化时调用）
            memory.filename = session_data.get("filename", memory.filename)
            memory.created_time = session_data.get("created_time", memory.created_time)
            memory.history=session_data.get("history", [])
            
            return memory
        except Exception as e:
            raise Exception(f"加载会话失败: {str(e)}")
    
    
    def __len__(self) -> int:
        """获取历史记录数量"""
        return len(self.history)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Memory(session_id={self.session_id}, messages={len(self.messages)}, history={len(self.history)})"
