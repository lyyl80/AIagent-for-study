"""
配置管理模块

负责加载和管理应用程序的环境变量和全局配置。
使用python-dotenv从.env文件读取敏感信息（如API密钥）。
"""
from dotenv import load_dotenv
import os

# 加载环境变量（从项目根目录的.env文件）
load_dotenv()

# DeepSeek API配置
DEEP_SEEK_API_KEY = os.environ.get("DEEP_SEEK_API_KEY")  # DeepSeek API密钥
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.ai")  # DeepSeek API基础URL

# LLM服务配置
LLM_URL = os.getenv("LLM_URL", "http://localhost:11434")  # Ollama本地服务地址

# 默认模型配置
MODEL_ING = "deepseek-v4-flash"  # 正在使用的模型标识符
_active_model = "deepseek-v4-flash"  # 当前激活的模型（内部变量）


def get_active_model() -> str:
    """
    获取当前激活的模型标识符
    
    Returns:
        str: 激活的模型名称
    """
    return _active_model


def set_active_model(key: str) -> None:
    """
    设置当前激活的模型
    
    Args:
        key (str): 要激活的模型标识符
    """
    global _active_model
    _active_model = key


# 调试模式开关
Debugmode = False
