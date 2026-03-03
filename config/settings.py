from dotenv import load_dotenv
import os
load_dotenv()
DEEP_SEEK_API_KEY = os.getenv("DEEP_SEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.ai")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:12b")
LLM_URL = os.getenv("LLM_URL", "http://localhost:11434")
