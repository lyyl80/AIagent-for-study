from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptTemplate:
    """
    提示模板类，用于定义提示字符串的格式和内容
    """
    name: str
    content: str
    description : Optional[str] = None


class TemplateManager:
    """
    模板管理器，用于管理和获取预定义的提示模板
    """
    
    def __init__(self):
        self.templates = {
            # 基础对话模板
            "basic_chat": PromptTemplate(
                name = "basic_chat",
                content = "请基于以下内容进行回复：{content}",
                description = "基础对话"
            ),
            
            # 系统指令模板
            "system_instruction": PromptTemplate(
                name = "system_instruction",
                content = "请基于以下内容进行回复：{content}",
                description = "系统指令"
            ),
            
            # 多轮对话模板
            "multi_turn_chat": PromptTemplate(
                name = "multi_turn_chat",
                content = "请基于以下内容进行回复：{content}",
                description = "多轮对话"
            ),
            
            # 总结模板
            "summarize": PromptTemplate(
                name = "summarize",
                content = "请基于以下内容进行总结：{content}",
                description = "总结"
            ),
            
            # 问题解答模板
            "question_answering": PromptTemplate(
                name = "question_answering",
                content = "问题: {question}\n"
                          "上下文: {context}\n\n"
                          "请基于提供的上下文回答问题，如果无法从上下文中找到答案，请说明无法确定答案。",
                description = "问题解答"
            ),
            
            # 分析模板
            "analysis": PromptTemplate(
                name = "analysis",
                content = "请分析以下内容:\n{content}\n\n"
                          "分析角度包括: {aspects}",
                description = "分析"
            )
        }
    
    def get_template(self, template_name):
        """
        获取指定名称的模板
        
        Args:
            template_name (str): 模板名称
            
        Returns:
            PromptTemplate: 对应的模板对象，如果不存在则返回None
        """
        return self.templates.get(template_name)
    
    def register_template(self, template_name, template):
        """
        注册新的提示模板
        
        Args:
            template_name (str): 模板名称
            template (PromptTemplate): 模板对象
        """
        self.templates[template_name] = template
    
    def format_from_name(self, template_name, **kwargs):
        """
        使用指定名称的模板并格式化
        
        Args:
            template_name (str): 模板名称
            **kwargs: 用于替换模板中占位符的键值对
            
        Returns:
            str: 格式化后的提示字符串
        """
        template = self.get_template(template_name)
        if template:
            return template.format(**kwargs)
        else:
            raise ValueError(f"模板 '{template_name}' 不存在")


# 全局模板管理器实例
template_manager = TemplateManager()


def get_template(template_name):
    """
    获取指定名称的提示模板
    
    Args:
        template_name (str): 模板名称
        
    Returns:
        PromptTemplate: 对应的模板对象
    """
    return template_manager.get_template(template_name)


def format_prompt(template_name, **kwargs):
    """
    使用指定名称的模板并格式化
    
    Args:
        template_name (str): 模板名称
        **kwargs: 用于替换模板中占位符的键值对
        
    Returns:
        str: 格式化后的提示字符串
    """
    return template_manager.format_from_name(template_name, **kwargs)