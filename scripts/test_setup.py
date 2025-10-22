# scripts/test_setup.py
import sys
sys.path.insert(0, '.')

from config.settings import settings
from utils.logger import logger

def test_setup():
    """환경 설정 테스트"""
    logger.info("="*50)
    logger.info("🧪 환경 설정 테스트")
    logger.info("="*50)
    
    # 1. API Key 확인
    logger.info("\n1️⃣ API Keys 확인:")
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
        logger.info("   ✅ OpenAI API Key 설정됨")
    else:
        logger.error("   ❌ OpenAI API Key 필요 (.env 파일 확인)")
    
    if settings.GITHUB_TOKEN:
        logger.info("   ✅ GitHub Token 설정됨")
    else:
        logger.info("   ⚠️  GitHub Token 없음 (선택사항)")
    
    # 2. 패키지 확인
    logger.info("\n2️⃣ 패키지 설치 확인:")
    
    packages = [
        ("arxiv", "arxiv"),
        ("PyGithub", "github"),
        ("pytrends", "pytrends.request"),
        ("langchain", "langchain"),
        ("langgraph", "langgraph.graph"),
        ("pandas", "pandas"),
    ]
    
    for name, import_path in packages:
        try:
            __import__(import_path)
            logger.info(f"   ✅ {name} 설치 완료")
        except ImportError:
            logger.error(f"   ❌ {name} 설치 필요")
    
    # 3. 설정 확인
    logger.info("\n3️⃣ 분석 설정:")
    logger.info(f"   - 기간: {settings.ANALYSIS['date_range']['start']} ~ {settings.ANALYSIS['date_range']['end']}")
    logger.info(f"   - 키워드: {len(settings.ANALYSIS['keywords'])}개")
    logger.info(f"   - Top 트렌드: {settings.ANALYSIS['num_trends']}개")
    
    logger.info("\n" + "="*50)
    logger.info("✅ 환경 설정 테스트 완료!")
    logger.info("="*50)

if __name__ == "__main__":
    test_setup()