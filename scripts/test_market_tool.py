# scripts/test_market_tool.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.market_tool import search_market_reports, get_predefined_market_demands
from utils.logger import logger

def test_tavily_search():
    """Tavily 검색 테스트"""
    logger.info("="*70)
    logger.info("🧪 Tavily API 시장 리포트 검색 테스트")
    logger.info("="*70)
    
    # 테스트 쿼리
    test_queries = [
        "AI automation market size 2025",
        "SME AI adoption statistics",
        "generative AI enterprise market"
    ]
    
    result = search_market_reports.invoke({
        "queries": test_queries,
        "max_results": 5
    })
    
    logger.info(f"\n총 {len(result)}개 결과 수집\n")
    
    # 결과 샘플 출력
    for i, item in enumerate(result[:3], 1):
        logger.info(f"[{i}] {item['title']}")
        logger.info(f"    출처: {item['source']}")
        logger.info(f"    점수: {item['score']:.2f}")
        logger.info(f"    내용: {item['content'][:100]}...")
        logger.info("")

def test_predefined_demands():
    """사전 정의된 시장 수요 테스트"""
    logger.info("="*70)
    logger.info("🧪 사전 정의 시장 수요 테스트")
    logger.info("="*70)
    
    result = get_predefined_market_demands.invoke({})
    
    logger.info(f"\n총 {len(result)}개 시장 수요\n")
    
    for i, item in enumerate(result[:3], 1):
        logger.info(f"[{i}] {item['demand_name']}")
        logger.info(f"    문제: {item['problem_statement']}")
        logger.info(f"    TAM: ${item['tam_usd']:,}")
        logger.info(f"    성장률: {item['cagr']*100:.0f}%")
        logger.info(f"    검색 키워드: {', '.join(item['search_keywords'][:2])}")
        logger.info("")

def main():
    """전체 테스트"""
    try:
        test_tavily_search()
        test_predefined_demands()
        
        logger.info("="*70)
        logger.info("✅ 모든 테스트 통과!")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()