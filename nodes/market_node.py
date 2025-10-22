# nodes/market_node.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.graph_state import GraphState
from tools.market_tool import get_predefined_market_demands, search_market_reports
from utils.logger import logger

def calculate_opportunity_score(tam_usd: int, cagr: float, gov_support: bool) -> float:
    """시장 기회 점수 계산"""
    # TAM 점수 (최대 40점)
    tam_score = min(tam_usd / 1_000_000_000, 1.0) * 40
    
    # 성장률 점수 (최대 30점)
    growth_score = min(cagr / 0.5, 1.0) * 30
    
    # 정부 지원 (30점)
    gov_score = 30 if gov_support else 0
    
    return round(tam_score + growth_score + gov_score, 1)

def market_analysis_node(state: GraphState) -> GraphState:
    """
    Agent 3: 시장 수요 분석
    사전 정의된 시장 수요 + Tavily 검색으로 보강
    """
    logger.info("="*70)
    logger.info("📈 Agent 3: 시장 수요 분석 시작")
    logger.info("="*70)
    
    # 1. 사전 정의된 시장 수요 로드
    logger.info("\n1️⃣ 기본 시장 수요 템플릿 로드 중...")
    market_demands = get_predefined_market_demands.invoke({})
    logger.info(f"   ✅ {len(market_demands)}개 시장 수요 로드\n")
    
    # 2. 각 수요별 기회 점수 계산
    logger.info("2️⃣ 시장 기회 점수 계산 중...\n")
    
    for demand in market_demands:
        # 기회 점수 계산
        opportunity_score = calculate_opportunity_score(
            tam_usd=demand["tam_usd"],
            cagr=demand["cagr"],
            gov_support=demand["government_support"]
        )
        
        demand["opportunity_score"] = opportunity_score
        
        logger.info(f"   [{demand['demand_id']}] {demand['demand_name']:30s}")
        logger.info(f"      TAM: ${demand['tam_usd']:>12,} | "
                   f"성장률: {demand['cagr']*100:5.1f}% | "
                   f"정부지원: {'✓' if demand['government_support'] else '✗'} | "
                   f"점수: {opportunity_score:5.1f}")
    
    # 3. Tavily로 실제 시장 리포트 검색 (상위 3개만)
    logger.info(f"\n3️⃣ Tavily 시장 리포트 검색 중 (상위 3개 시장)...")
    
    top_markets = sorted(market_demands, key=lambda x: x["opportunity_score"], reverse=True)[:3]
    
    for market in top_markets:
        try:
            logger.info(f"\n   검색: {market['demand_name']}")
            
            # 검색 키워드로 Tavily 검색
            reports = search_market_reports.invoke({
                "queries": market["search_keywords"][:2],  # 키워드 2개만
                "max_results": 3
            })
            
            market["tavily_reports"] = reports
            logger.info(f"      → {len(reports)}개 리포트 발견")
            
            if reports:
                logger.info(f"      샘플: {reports[0]['title'][:60]}...")
            
        except Exception as e:
            logger.warning(f"      ✗ Tavily 검색 실패: {e}")
            market["tavily_reports"] = []
    
    # 4. 기회 점수 순으로 정렬
    market_demands.sort(key=lambda x: x["opportunity_score"], reverse=True)
    
    logger.info(f"\n상위 5개 시장 (기회 점수 기준):")
    for i, market in enumerate(market_demands[:5], 1):
        logger.info(f"   {i}. {market['demand_name']:30s} ({market['opportunity_score']}점)")
    
    logger.info("\n" + "="*70)
    logger.info("✅ Agent 3: 시장 분석 완료")
    logger.info("="*70)
    logger.info(f"   총 {len(market_demands)}개 시장 수요 분석")
    logger.info("="*70 + "\n")
    
    return {
        "market_demands": market_demands,
        "messages": [{
            "role": "assistant",
            "content": f"시장 분석 완료: {len(market_demands)}개 수요 분석"
        }],
        "step_market": "completed"
    }