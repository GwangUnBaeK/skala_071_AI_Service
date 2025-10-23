# config/settings.py
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """전역 설정"""
    
    # LLM 설정 
    LLM = {
        "model": "gpt-4o-mini",
        "temperature": 0
    }

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # LangSmith 
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
    
    # Analysis Configuration
    ANALYSIS = {
        "date_range": {
            "start": "2023-01-01",  # ✅ 문자열이어야 함
            "end": date.today().isoformat()  # ✅ 또는 이것도 문자열
        },
        "keywords": [
            "generative AI",
            "large language model",
            "LLM agent",
            "multimodal AI",
            "edge AI",
            "AI automation"
        ],
        "num_trends": 5
    }
    
    # Data Collection Limits
    LIMITS = {
        "arxiv_max_per_keyword": 100,
        "github_max_per_keyword": 30,
        "github_min_stars": 100,
        "tavily_max_results": 10
    }
    
    # Paths
    DATA_DIR = "data"
    RAW_DATA_DIR = "data/raw"
    PROCESSED_DATA_DIR = "data/processed"
    OUTPUT_DIR = "outputs"
    REPORTS_DIR = "outputs/reports"
    CHECKPOINTS_DIR = "outputs/checkpoints"

settings = Settings()