from dotenv import load_dotenv
import os
load_dotenv()
DEEP_SEEK_API_KEY = os.getenv("DEEP_SEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.ai")
LLM_URL = os.getenv("LLM_URL", "http://localhost:11434")
MODEL_ING = os.getenv("MODEL_ING", "gpt-oss:20b")  # 模型标识，需与LLM_MODEL一致

