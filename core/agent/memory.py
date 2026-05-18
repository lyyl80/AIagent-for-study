"""
记忆管理系统模块

基于OpenCode架构设计，提供会话的持久化存储和管理功能。
支持对话历史记录、会话摘要生成、文件命名和加载等功能。
"""
from typing import Dict, Any, List, Optional
import json
import os
import re
from datetime import datetime


def generate_session_summary(messages: List[Dict[str, Any]], max_length: int = 30) -> str:
    """
    生成会话摘要，用于文件名
    
    从用户消息中提取第一个问题作为会话摘要，清理特殊字符并限制长度，
    使文件名更具可读性。
    
    Args:
        messages (List[Dict[str, Any]]): 会话消息列表
        max_length (int): 摘要最大长度，默认30个字符
    
    Returns:
        str: 清理后的会话摘要字符串
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
    
    # 限制长度，避免在单词中间截断
    if len(cleaned_text) > max_length:
        # 按字符截取，确保不切分单词
        cleaned_text = cleaned_text[:max_length].rsplit(' ', 1)[0] + "..."
    
    # 移除多余空格
    cleaned_text = ' '.join(cleaned_text.split())
    
    return cleaned_text if cleaned_text else "会话"


def create_session_filename(session_id: str, messages: List[Dict[str, Any]]) -> str:
    """
    创建带摘要的会话文件名
    
    结合时间戳和用户输入的摘要生成安全的文件名，
    移除文件系统不允许的特殊字符。
    
    Args:
        session_id (str): 会话ID（通常为时间戳）
        messages (List[Dict[str, Any]]): 会话消息列表
    
    Returns:
        str: 完整的文件名（不含扩展名），格式为 "{session_id}_{summary}"
    """
    summary = generate_session_summary(messages)
    safe_summary = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', summary)
    return f"{session_id}_{safe_summary}" if safe_summary else session_id


class Memory:
    """
    记忆管理系统类
    
    负责管理AI代理的对话历史和会话数据，提供以下核心功能：
    - 短期记忆：维护最近的对话历史
    - 长期记忆：通过JSON文件持久化保存会话
    - 会话管理：支持创建、加载、列出和清空会话
    - 自动摘要：根据用户输入生成有意义的会话名称
    
    Attributes:
        history (List[Dict]): 步骤历史记录，包含工具调用等详细信息
        messages (List[Dict]): 对话消息列表，包含用户和AI的消息
        max_history (int): 最大历史记录条数，超出时自动裁剪
        user_input (str): 当前用户输入
        session_id (str): 会话唯一标识符（时间戳格式）
        filename (str): 会话文件名（含摘要）
        created_time (str): 会话创建时间的ISO格式字符串
        persist_path (str): 持久化文件的完整路径
    """
    
    def __init__(self, max_history: int = 100,  
                 session_id: Optional[str] = None, user_input: Optional[str] = None):
        """
        初始化记忆系统
        
        Args:
            max_history (int): 最大历史记录条数，默认100
            session_id (Optional[str]): 会话ID，如果为None则自动生成时间戳
            user_input (Optional[str]): 初始用户输入，用于生成会话摘要
        """
        self.history: List[Dict[str, Any]] = []  # 步骤历史记录
        self.messages: List[Dict[str, Any]] = []  # 对话消息列表
        self.max_history = max_history

        self.user_input = user_input
        
        # 生成会话ID（时间戳格式：YYYY-MM-DD_HH-MM-SS）
        self.session_id = session_id or datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # 创建初始消息列表用于生成文件名
        initial_messages = [{"role": "user", "content": user_input}] if user_input else []
        
        # 生成会话摘要和文件名
        self.filename = create_session_filename(self.session_id, initial_messages)
        self.created_time = datetime.now().isoformat()
        self.persist_path = f"session/{self.filename}.json"
        

    
    def add_conversation(self, conversation: Dict[str, Any]) -> None:
        """
        添加步骤历史记录
        
        记录工具调用的输入输出信息，对长输出进行摘要处理。
        超过最大历史记录数时自动裁剪旧记录，并触发持久化保存。
        
        Args:
            conversation (Dict[str, Any]): 包含工具调用信息的字典，应包含：
                - input: 工具输入参数
                - output: 工具执行结果
        """
        output = conversation.get("output", "")
        # 对长输出进行摘要，避免占用过多空间
        if isinstance(output, str) and len(output) > 1000:
            conversation["output_summary"] = output[:600] + f"\n... (全文 {len(output)} 字符)"
        else:
            conversation["output_summary"] = output

        self.history.append(conversation)

        # 超过最大记录数时，保留最近的记录
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        # 自动保存到文件
        if self.persist_path:
            self.save()

    def add_message(self, role: str, content: str) -> None:
        """
        添加对话消息到历史记录
        
        同时更新history和messages两个列表，保持数据一致性。
        
        Args:
            role (str): 消息角色，如"user"、"assistant"、"system"
            content (str): 消息内容
        """
        entry = {"role": role, "content": content}
        self.history.append(entry)
        self.messages.append(entry)
        if self.persist_path:
            self.save()
    
    def get_history(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取历史记录
        
        Args:
            n (Optional[int]): 返回最近n条记录，如果为None则返回全部
            
        Returns:
            List[Dict[str, Any]]: 历史记录列表
        """
        if n is None:
            return self.history
        return self.history[-n:]
    
    
    def clear(self) -> None:
        """
        清空所有历史记录
        
        清除history和messages列表，并更新持久化文件。
        """
        self.history.clear()
        self.messages.clear()
        if self.persist_path:
            self.save()

    
    def save(self) -> None:
        """
        保存记忆到JSON文件
        
        将会话数据序列化为JSON格式并写入文件。
        自动创建目录结构，处理可能的IO异常。
        """
        if not self.persist_path:
            return
        
        data = {
            "session_id": self.session_id,
            "filename": self.filename,
            "history": self.history,
            "messages": self.messages,
            "max_history": self.max_history,
            "created_time": self.created_time
        }
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记忆失败: {e}")
    
    def load(self) -> None:
        """
        从JSON文件加载记忆
        
        读取持久化的会话数据并恢复到内存中。
        支持新旧数据格式的兼容性处理。
        """
        if not self.persist_path or not os.path.exists(self.persist_path):
            return
        
        try:
            with open(self.persist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载新格式数据，保留原有值作为后备
            self.session_id = data.get("session_id", self.session_id)
            self.filename = data.get("filename", self.filename)
            self.created_time = data.get("created_time", self.created_time)
            self.history = data.get("history", self.history)
            self.messages = data.get("messages", [])
            self.max_history = data.get("max_history", self.max_history)
        except Exception as e:
            print(f"加载记忆失败: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将记忆对象转换为字典表示
        
        Returns:
            Dict[str, Any]: 包含所有会话数据的字典
        """
        return {
            "session_id": self.session_id,
            "filename": self.filename,
            "history": self.history,
            "messages": self.messages,
            "max_history": self.max_history,
            "created_time": self.created_time
        }
    
    @staticmethod
    def list_sessions() -> List[Dict[str, Any]]:
        """
        列出所有已保存的会话
        
        扫描session目录下的所有JSON文件，解析元数据并按创建时间排序。
        对损坏的文件提供降级处理，显示基本文件名信息。
        
        Returns:
            List[Dict[str, Any]]: 会话列表，按创建时间降序排列（新的在前）
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
        """
        加载指定会话
        
        从文件中读取会话数据并创建Memory实例。
        支持模糊匹配文件名，提高容错性。
        
        Args:
            filename (str): 会话文件名（不含扩展名）
        
        Returns:
            Memory: 加载的记忆实例
        
        Raises:
            FileNotFoundError: 当指定的会话文件不存在时
            Exception: 当加载过程出现其他错误时
        """
        session_path = f"session/{filename}.json"
        if not os.path.exists(session_path):
            # 如果找不到精确匹配，尝试按文件名前缀查找
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
            memory.persist_path = f"session/{memory.filename}.json"
            memory.created_time = session_data.get("created_time", memory.created_time)
            memory.history = session_data.get("history", [])
            memory.messages = session_data.get("messages", [])
            
            return memory
        except Exception as e:
            raise Exception(f"加载会话失败: {str(e)}")
    
    
    def __len__(self) -> int:
        """
        获取历史记录数量
        
        Returns:
            int: history列表的长度
        """
        return len(self.history)
    
    def __str__(self) -> str:
        """
        字符串表示
        
        Returns:
            str: 包含会话ID、消息数和历史数的格式化字符串
        """
        return f"Memory(session_id={self.session_id}, messages={len(self.messages)}, history={len(self.history)})"
