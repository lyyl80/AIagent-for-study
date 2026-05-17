from dotenv import load_dotenv
import os

load_dotenv()
DEEP_SEEK_API_KEY = os.environ.get("DEEP_SEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.ai")
LLM_URL = os.getenv("LLM_URL", "http://localhost:11434")
MODEL_ING = "deepseek-v4-flash"
_active_model = "deepseek-v4-flash"

def get_active_model() -> str:
    return _active_model

def set_active_model(key: str) -> None:
    global _active_model
    _active_model = key

Debugmode = False

