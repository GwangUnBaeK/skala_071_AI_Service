# nodes/cross_node.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.graph_state import GraphState
from utils.scoring import calculate_final_score
from utils.logger import logger
from config.keywords import COMPETITION_MAP, TREND_KEYWORD_MAP

def estimate_competition(tech_name: str) -> float:
    """경쟁 강도 추정 (0~100)"""
    tech_lower = tech_name.lower()
    
    # COMPETITION_MAP에서 매칭
    for key, score in COMPETITION_MAP.items():
        if key.lower() in tech_lower:
            return score
    
    # 기본값
    return 50.0

def generate_trend_keyword(tech_name: str, market_name: str) -> str:
    """트렌드 키워드 생성"""
    tech_lower = tech_name.lower()
    market_lower = market_name.lower()
    
    # TREND_KEYWORD_MAP에서 매칭
    for (tech_key, market_key), keyword in TREND_KEYWORD_MAP.items():
        if tech_key in tech_lower and market_key in market_lower:
            return keyword
    
    # 매칭 안되면 조합
    return f"{tech_name} × {market_name}"

def cross_analysis_node(state: GraphState) -> GraphState:
    """
    Agent 4: 교차 분석 및 Top 5 선정
    기술 × 시장 매트릭스 생성 → 최종 점수 계산 → Top 5 선정
    """
    logger.info("="*70)
    logger.info("🎯 Agent 4: 교차 분석 시작 (기술 × 시장)")
    logger.info("="*70)
    
    tech_trends = state.get("tech_trends", [])
    market_demands = state.get("market_demands", [])
    rag_analysis = state.get("rag_analysis", {})
    
    logger.info(f"\n입력 데이터:")
    logger.info(f"   - 기술: {len(tech_trends)}개")
    logger.info(f"   - 시장: {len(market_demands)}개")
    logger.info(f"   - RAG 분석: {'완료' if rag_analysis.get('answer') else '없음'}\n")
    
    # 1. 상위 기술/시장만 사용 (계산 효율)
    top_techs = tech_trends[:10]  # 상위 10개 기술
    top_markets = market_demands[:10]  # 상위 10개 시장
    
    logger.info(f"교차 분석 범위: {len(top_techs)} 기술 × {len(top_markets)} 시장 = {len(top_techs) * len(top_markets)}개 조합\n")
    
    # 2. 기술 × 시장 매트릭스 생성
    trend_matrix = []
    
    for tech in top_techs:
        for market in top_markets:
            # 경쟁 강도 추정
            competition = estimate_competition(tech["tech_name"])
            
            # 최종 점수 계산
            final_score = calculate_final_score(
                tech_score=tech["maturity_score"],
                market_score=market["opportunity_score"],
                growth_rate=market["cagr"],
                competition=competition
            )
            
            # 적합도 필터링 (점수 50점 미만은 제외)
            if final_score < 50:
                continue
            
            trend_matrix.append({
                "tech": tech,
                "market": market,
                "competition": competition,
                "final_score": final_score
            })
    
    logger.info(f"생성된 조합: {len(trend_matrix)}개 (50점 이상)\n")
    
    # 3. 점수 순으로 정렬
    trend_matrix.sort(key=lambda x: x["final_score"], reverse=True)
    
    # 4. Top 5 선정
    top_5_trends = []
    
    for i, trend in enumerate(trend_matrix[:5], 1):
        # 트렌드 키워드 생성
        keyword = generate_trend_keyword(
            trend["tech"]["tech_name"],
            trend["market"]["demand_name"]
        )
        
        top_5_trends.append({
            "rank": i,
            "trend_keyword": keyword,
            "final_score": trend["final_score"],
            "tech": trend["tech"],
            "market": trend["market"],
            "competition": trend["competition"]
        })
        
        logger.info(f"[{i}위] {keyword}")
        logger.info(f"      최종 점수: {trend['final_score']:.1f}")
        logger.info(f"      기술: {trend['tech']['tech_name']} (성숙도 {trend['tech']['maturity_score']:.1f})")
        logger.info(f"      시장: {trend['market']['demand_name']} (기회 {trend['market']['opportunity_score']:.1f})")
        logger.info(f"      경쟁: {trend['competition']:.1f}\n")
    
    # 5. RAG 인사이트 통합 (있으면)
    if rag_analysis.get("answer"):
        logger.info("📚 RAG 분석 결과 통합 중...")
        for trend in top_5_trends:
            trend["rag_insight"] = {
                "answer": rag_analysis["answer"][:500],  # 500자만
                "sources": rag_analysis.get("sources", [])[:2]  # 상위 2개 출처
            }
        logger.info("   ✓ RAG 인사이트 추가 완료\n")
    
    logger.info("="*70)
    logger.info("✅ Agent 4: 교차 분석 완료")
    logger.info("="*70)
    logger.info(f"   Top 5 트렌드 선정 완료")
    logger.info("="*70 + "\n")
    
    return {
        "trend_matrix": trend_matrix,
        "top_5_trends": top_5_trends,
        "messages": [{
            "role": "assistant",
            "content": f"Top 5 트렌드 선정 완료"
        }],
        "step_cross": "completed"
    }