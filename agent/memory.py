class Memory:
    def __init__(self):
        self.history = []

    def add_conversation(self, conversation):
        self.history.append(conversation)

    def get_recent_conversations(self, limit=5):
        """返回最近的对话，格式化为字符串便于LLM理解"""
        recent = self.history[-limit:] if len(self.history) > limit else self.history
        if not recent:
            return "无历史步骤"
        
        formatted = []
        for i, conv in enumerate(recent, 1):
            tool = conv.get("input", {}).get("tool", "unknown")
            tool_args = conv.get("input", {}).get("tool_args", {})
            result = conv.get("output", "无结果")
            reflect = conv.get("reflect", "无反思")
            
            # 简化显示
            args_str = str(tool_args)[:100] + "..." if len(str(tool_args)) > 100 else str(tool_args)
            result_str = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            reflect_str = str(reflect)[:150] + "..." if len(str(reflect)) > 150 else str(reflect)
            
            formatted.append(f"步骤{i}: 工具={tool}, 参数={args_str}")
            formatted.append(f"     结果: {result_str}")
            formatted.append(f"     反思: {reflect_str}")
        
        return "\n".join(formatted)