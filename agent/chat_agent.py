from llm import deep_seek_chat, local_chat
from agent import Memory
from prompt import format_prompt


class ChatAgent(Memory):
    def __init__(self, memory_size=10, use_template=False, default_template=None):
        super().__init__(memory_size)
        self.llm = local_chat
        self.deep_seek = deep_seek_chat
        self.use_template = use_template
        self.default_template = default_template or "basic_chat"
        self.memory = Memory(memory_size)

    def chat(self, message, template_name=None, model=None, **template_kwargs):
        # 使用记忆存储用户输入
        self.memory.add_conversation({"role": "user", "content": message})
        
        # 获取最近的对话历史
        recent_history = self.memory.get_recent_conversations()
        messages = [{"role": "user", "content": item["content"]} if item["role"] == "user" 
                    else {"role": "assistant", "content": item["content"]} for item in recent_history]
        
        # 确定使用的模板名称
        template_to_use = template_name or (self.default_template if self.use_template else None)
        
        # 使用llm或deepseek获取响应
        if model == "deepseek-reasoner":
            if self.use_template and template_to_use:
                response = self.deep_seek(messages, template_name=template_to_use, **template_kwargs)
            else:
                response = self.deep_seek(messages)
        elif model == "gemma3:12b(local)":
            if self.use_template and template_to_use:
                response = self.llm(messages, template_name=template_to_use, **template_kwargs)
            else:
                response = self.llm(messages)
            
        # 存储AI响应到记忆中
        self.memory.add_conversation({"role": "assistant", "content": response})
        
        return response