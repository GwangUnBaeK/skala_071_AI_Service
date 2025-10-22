# scripts/test_tools.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.arxiv_tool import search_arxiv_papers
from tools.github_tool import search_github_repos
from tools.trends_tool import search_google_trends
from tools.market_tool import get_market_demands
from utils.logger import logger

def test_arxiv():
    """arXiv 도구 테스트"""
    logger.info("\n" + "="*50)
    logger.info("TEST 1: arXiv Tool")
    logger.info("="*50)
    
    result = search_arxiv_papers.invoke({
        "keywords": ["generative AI"],
        "max_results": 10  # 테스트용 적은 수
    })
    
    logger.info(f"결과: {len(result)}개 논문")
    if result:
        logger.info(f"샘플: {result[0]['title'][:50]}...")

def test_github():
    """GitHub 도구 테스트"""
    logger.info("\n" + "="*50)
    logger.info("TEST 2: GitHub Tool")
    logger.info("="*50)
    
    result = search_github_repos.invoke({
        "keywords": ["LLM agent"],
        "min_stars": 1000  # 테스트용 높은 기준
    })
    
    logger.info(f"결과: {len(result)}개 저장소")
    if result:
        logger.info(f"샘플: {result[0]['name']} ({result[0]['stars']} stars)")

def test_trends():
    """Google Trends 도구 테스트"""
    logger.info("\n" + "="*50)
    logger.info("TEST 3: Google Trends Tool")
    logger.info("="*50)
    
    result = search_google_trends.invoke({
        "keywords": ["ChatGPT", "AI"],
        "timeframe": "2024-01-01 2025-10-21"
    })
    
    logger.info(f"결과: {len(result)}개 키워드")
    if result:
        for keyword, data in result.items():
            logger.info(f"  {keyword}: {len(data)}개 데이터 포인트")

def test_market():
    """Market 도구 테스트"""
    logger.info("\n" + "="*50)
    logger.info("TEST 4: Market Tool")
    logger.info("="*50)
    
    result = get_market_demands.invoke({})
    
    logger.info(f"결과: {len(result)}개 시장 수요")
    if result:
        logger.info(f"샘플: {result[0]['demand_name']}")
        logger.info(f"  TAM: ${result[0]['tam_usd']:,}")
        logger.info(f"  성장률: {result[0]['cagr']*100:.0f}%")

def main():
    """모든 도구 테스트"""
    logger.info("🧪 Tools 테스트 시작\n")
    
    try:
        test_arxiv()
        test_github()
        test_trends()
        test_market()
        
        logger.info("\n" + "="*50)
        logger.info("✅ 모든 테스트 통과!")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()