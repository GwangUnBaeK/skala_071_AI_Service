# tools/market_tool.py
from langchain_core.tools import tool
from typing import List, Dict
from tavily import TavilyClient
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from utils.logger import logger

@tool
def search_market_reports(queries: List[str], max_results: int = 10) -> List[Dict]:
    """
    Tavily API를 사용하여 AI 시장 리포트 및 뉴스를 검색합니다.
    
    Args:
        queries: 검색할 쿼리 리스트
        max_results: 쿼리당 최대 결과 수
    
    Returns:
        시장 리포트 및 뉴스 정보 리스트
    """
    logger.info(f"📊 시장 리포트 검색 시작 (쿼리: {len(queries)}개)")
    
    # Tavily 클라이언트 초기화
    tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
    
    all_results = []
    
    for query in queries:
        try:
            logger.info(f"   검색 중: '{query}'")
            
            # Tavily 검색 (심층 검색 모드)
            response = tavily.search(
                query=query,
                search_depth="advanced",  # 심층 검색
                max_results=max_results,
                include_domains=[
                    "mckinsey.com",
                    "gartner.com", 
                    "idc.com",
                    "forrester.com",
                    "statista.com",
                    "techcrunch.com",
                    "venturebeat.com",
                    "cbinsights.com"
                ]  # 신뢰할 수 있는 출처만
            )
            
            count = 0
            for result in response.get('results', []):
                all_results.append({
                    "query": query,
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "content": result.get('content', ''),
                    "score": result.get('score', 0),
                    "published_date": result.get('published_date', ''),
                    "source": result.get('url', '').split('/')[2] if result.get('url') else ''
                })
                count += 1
            
            logger.info(f"   ✓ '{query}': {count}개 수집")
            
        except Exception as e:
            logger.error(f"   ✗ '{query}' 검색 실패: {e}")
            continue
    
    logger.info(f"✅ 총 {len(all_results)}개 시장 리포트 수집 완료")
    return all_results


@tool  
def get_predefined_market_demands() -> List[Dict]:
    """
    사전 정의된 주요 시장 수요 데이터를 반환합니다.
    (Tavily 검색 결과와 함께 사용)
    
    Returns:
        시장 수요 정보 리스트
    """
    logger.info("📈 사전 정의된 시장 수요 데이터 로드 중...")
    
    # 기본 시장 수요 템플릿
    market_demands = [
        {
            "demand_id": "market_001",
            "demand_name": "중소기업 업무 자동화",
            "problem_statement": "중소기업 채용난 심화 및 인건비 상승",
            "tam_usd": 500_000_000,
            "cagr": 0.48,
            "government_support": True,
            "target_companies": 500_000,
            "regions": ["korea", "southeast_asia"],
            "industries": ["manufacturing", "retail", "services"],
            "search_keywords": [
                "SME AI automation market",
                "small business AI adoption",
                "AI workforce automation SME"
            ]
        },
        {
            "demand_id": "market_002",
            "demand_name": "다국어 커뮤니케이션",
            "problem_statement": "글로벌 비즈니스 언어 장벽",
            "tam_usd": 300_000_000,
            "cagr": 0.35,
            "government_support": False,
            "target_companies": 1_000_000,
            "regions": ["global"],
            "industries": ["travel", "education", "commerce"],
            "search_keywords": [
                "AI translation market size",
                "real-time translation business",
                "multilingual AI market"
            ]
        },
        {
            "demand_id": "market_003",
            "demand_name": "콘텐츠 크리에이터 지원",
            "problem_statement": "1인 창작자 제작 비용 및 시간 부담",
            "tam_usd": 400_000_000,
            "cagr": 0.55,
            "government_support": True,
            "target_companies": 2_000_000,
            "regions": ["global"],
            "industries": ["media", "entertainment", "marketing"],
            "search_keywords": [
                "AI content creation market",
                "creator economy AI tools",
                "generative AI for creators"
            ]
        },
        {
            "demand_id": "market_004",
            "demand_name": "개인정보 보호 AI",
            "problem_statement": "클라우드 AI 보안 및 프라이버시 우려",
            "tam_usd": 250_000_000,
            "cagr": 0.42,
            "government_support": True,
            "target_companies": 300_000,
            "regions": ["global"],
            "industries": ["finance", "healthcare", "government"],
            "search_keywords": [
                "private AI market",
                "on-premise LLM enterprise",
                "edge AI privacy"
            ]
        },
        {
            "demand_id": "market_005",
            "demand_name": "제조업 품질 관리",
            "problem_statement": "불량률 감소 및 검사 자동화 필요",
            "tam_usd": 600_000_000,
            "cagr": 0.38,
            "government_support": True,
            "target_companies": 200_000,
            "regions": ["korea", "southeast_asia"],
            "industries": ["manufacturing"],
            "search_keywords": [
                "AI quality inspection manufacturing",
                "computer vision quality control",
                "AI manufacturing defect detection"
            ]
        },
        {
            "demand_id": "market_006",
            "demand_name": "교육 개인화",
            "problem_statement": "학생별 맞춤 교육 수요 증가",
            "tam_usd": 350_000_000,
            "cagr": 0.45,
            "government_support": True,
            "target_companies": 500_000,
            "regions": ["global"],
            "industries": ["education"],
            "search_keywords": [
                "AI personalized learning market",
                "adaptive learning AI",
                "AI education technology"
            ]
        },
        {
            "demand_id": "market_007",
            "demand_name": "고객 서비스 자동화",
            "problem_statement": "24/7 고객 응대 인력 부족",
            "tam_usd": 450_000_000,
            "cagr": 0.50,
            "government_support": False,
            "target_companies": 800_000,
            "regions": ["global"],
            "industries": ["retail", "finance", "telecom"],
            "search_keywords": [
                "AI customer service market",
                "chatbot enterprise market size",
                "AI contact center automation"
            ]
        },
        {
            "demand_id": "market_008",
            "demand_name": "개발자 생산성 향상",
            "problem_statement": "소프트웨어 개발 속도 및 품질 요구 증가",
            "tam_usd": 550_000_000,
            "cagr": 0.60,
            "government_support": False,
            "target_companies": 1_500_000,
            "regions": ["global"],
            "industries": ["tech", "software"],
            "search_keywords": [
                "AI code generation market",
                "GitHub Copilot adoption",
                "AI developer tools market"
            ]
        },
        {
            "demand_id": "market_009",
            "demand_name": "의료 진단 보조",
            "problem_statement": "의료 영상 판독 및 진단 정확도 향상 필요",
            "tam_usd": 700_000_000,
            "cagr": 0.52,
            "government_support": True,
            "target_companies": 100_000,
            "regions": ["global"],
            "industries": ["healthcare"],
            "search_keywords": [
                "AI medical imaging market",
                "AI healthcare diagnosis",
                "AI radiology market size"
            ]
        },
        {
            "demand_id": "market_010",
            "demand_name": "마케팅 콘텐츠 자동 생성",
            "problem_statement": "마케팅 콘텐츠 제작 비용 및 속도",
            "tam_usd": 400_000_000,
            "cagr": 0.58,
            "government_support": False,
            "target_companies": 1_000_000,
            "regions": ["global"],
            "industries": ["marketing", "advertising"],
            "search_keywords": [
                "AI marketing content generation",
                "generative AI advertising",
                "AI copywriting market"
            ]
        }
    ]
    
    logger.info(f"✅ {len(market_demands)}개 시장 수요 템플릿 로드 완료")
    return market_demands