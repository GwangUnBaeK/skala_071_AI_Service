# config/settings.py
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """전역 설정"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # LangSmith (선택)
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
    
    # Analysis Configuration
    ANALYSIS = {
        "date_range": {
            "start": date(2023, 1, 1),
            "end": date(2025, 10, 21)
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
        "arxiv_max_per_keyword": 200,
        "github_max_per_keyword": 50,
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