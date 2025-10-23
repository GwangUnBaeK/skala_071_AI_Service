# nodes/cross_node.py
"""
Agent 4: 교차 분석 노드 (테마 기반)
- CLUSTER_RULES를 기반으로 기술×시장을 5대 테마로 그룹핑
- 테마별 종합 점수 계산
- Top 5 테마 선정
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.graph_state import GraphState
from utils.logger import logger
from config.keywords import CLUSTER_RULES, COMPETITION_MAP

def estimate_competition(tech_name: str, market_name: str = "") -> float:
    """
    경쟁 강도 추정 (0~100)
    - COMPETITION_MAP 기반
    - 기술명과 시장명 모두 고려
    """
    tech_lower = tech_name.lower()
    market_lower = market_name.lower()
    
    max_score = 50.0  # 기본값
    
    # 기술명 매칭
    for key, score in COMPETITION_MAP.items():
        if key.lower() in tech_lower:
            max_score = max(max_score, score)
    
    # 시장명 매칭 (추가 보너스)
    if "sme" in market_lower or "enterprise" in market_lower:
        max_score = min(max_score + 5, 100)
    
    return float(max_score)


def calculate_theme_score(
    avg_tech_score: float,
    avg_market_score: float,
    avg_cagr: float,
    competition: float
) -> float:
    """
    테마 종합 점수 계산
    
    가중치:
    - 기술 성숙도: 25%
    - 시장 기회: 35% (가장 중요)
    - 시장 성장률: 25%
    - 경쟁 강도: -15% (패널티)
    """
    score = (
        0.25 * avg_tech_score +
        0.35 * avg_market_score +
        0.25 * min(avg_cagr * 100 / 50, 100) +  # CAGR 50% 이상이면 만점
        -0.15 * competition
    )
    
    return round(max(score, 0), 1)


def cross_analysis_node(state: GraphState) -> GraphState:
    """
    Agent 4: 테마 기반 교차 분석
    - CLUSTER_RULES를 활용해 5대 테마 선정
    - 각 테마의 대표 기술×시장 조합 추출
    """
    logger.info("="*70)
    logger.info("🎯 Agent 4: 교차 분석 시작 (테마 기반)")
    logger.info("="*70)
    
    tech_trends = state.get("tech_trends", [])
    market_trends = state.get("market_trends", [])
    rag_analysis = state.get("rag_analysis", {})
    
    logger.info(f"\n입력 데이터:")
    logger.info(f"   - 기술: {len(tech_trends)}개")
    logger.info(f"   - 시장: {len(market_trends)}개")
    logger.info(f"   - RAG 분석: {'완료' if rag_analysis.get('answer') else '없음'}\n")
    
    if not tech_trends or not market_trends:
        logger.error("❌ 기술 또는 시장 데이터가 없습니다!")
        return {
            "top_5_trends": [],
            "step_cross": "failed"
        }
    
    # =================================================================
    # 1️⃣ 테마별 점수 계산
    # =================================================================
    logger.info("📊 테마별 데이터 매칭 중...\n")
    
    theme_scores = {}
    
    for theme_name, rules in CLUSTER_RULES.items():
        logger.info(f"🔍 [{theme_name}] 분석 중...")
        
        # ---------------------------------------------------------
        # A. 이 테마에 해당하는 기술들 찾기
        # ---------------------------------------------------------
        related_techs = []
        for tech in tech_trends:
            tech_name_lower = tech["tech_name"].lower()
            
            # CLUSTER_RULES의 tech 키워드와 매칭
            for seed in rules["tech"]:
                if seed.lower() in tech_name_lower:
                    related_techs.append(tech)
                    break  # 중복 방지
        
        # ---------------------------------------------------------
        # B. 이 테마에 해당하는 시장들 찾기
        # ---------------------------------------------------------
        related_markets = []
        for market in market_trends:
            market_name_lower = market["demand_name"].lower()
            
            # CLUSTER_RULES의 market 키워드와 매칭
            for seed in rules["market"]:
                if seed.lower() in market_name_lower:
                    related_markets.append(market)
                    break
        
        # ---------------------------------------------------------
        # C. 매칭 결과 확인
        # ---------------------------------------------------------
        if not related_techs:
            logger.warning(f"   ⚠️ 매칭된 기술 없음 → 스킵")
            continue
        
        if not related_markets:
            logger.warning(f"   ⚠️ 매칭된 시장 없음 → 스킵")
            continue
        
        logger.info(f"   ✓ 기술 {len(related_techs)}개 매칭")
        logger.info(f"   ✓ 시장 {len(related_markets)}개 매칭")
        
        # ---------------------------------------------------------
        # D. 평균 점수 계산
        # ---------------------------------------------------------
        avg_tech_score = sum(t["maturity_score"] for t in related_techs) / len(related_techs)
        avg_market_score = sum(m["opportunity_score"] for m in related_markets) / len(related_markets)
        
        # 시장 성장률 (CAGR) 평균
        avg_cagr = sum(m.get("cagr", 0.20) for m in related_markets) / len(related_markets)
        
        # 경쟁 강도 (대표 기술 기준)
        representative_tech = related_techs[0]["tech_name"]
        representative_market = related_markets[0]["demand_name"]
        competition = estimate_competition(representative_tech, representative_market)
        
        # 최종 점수
        final_score = calculate_theme_score(
            avg_tech_score=avg_tech_score,
            avg_market_score=avg_market_score,
            avg_cagr=avg_cagr,
            competition=competition
        )
        
        # ---------------------------------------------------------
        # E. 대표 조합 선정 (각 테마당 최고 점수 조합 1개)
        # ---------------------------------------------------------
        best_tech = max(related_techs, key=lambda x: x["maturity_score"])
        best_market = max(related_markets, key=lambda x: x["opportunity_score"])
        
        # ---------------------------------------------------------
        # F. 결과 저장
        # ---------------------------------------------------------
        theme_scores[theme_name] = {
            "final_score": final_score,
            "tech_score": round(avg_tech_score, 1),
            "market_score": round(avg_market_score, 1),
            "cagr": round(avg_cagr, 3),
            "competition": round(competition, 1),
            "tech": best_tech,  # 대표 기술 (전체 객체)
            "market": best_market,  # 대표 시장 (전체 객체)
            "evidence": {
                "tech_count": len(related_techs),
                "market_count": len(related_markets),
                "tech_examples": [t["tech_name"] for t in related_techs[:3]],
                "market_examples": [m["demand_name"] for m in related_markets[:3]],
                "all_techs": related_techs,
                "all_markets": related_markets
            }
        }
        
        logger.info(f"   → 최종 점수: {final_score:.1f}")
        logger.info(f"      (기술 {avg_tech_score:.1f} + 시장 {avg_market_score:.1f} + 성장 {avg_cagr*100:.0f}% - 경쟁 {competition:.1f})\n")
    
    # =================================================================
    # 2️⃣ Top 5 테마 선정
    # =================================================================
    logger.info("="*70)
    logger.info("🏆 Top 5 테마 선정")
    logger.info("="*70 + "\n")
    
    if not theme_scores:
        logger.error("❌ 매칭된 테마가 하나도 없습니다!")
        return {
            "top_5_trends": [],
            "step_cross": "failed"
        }
    
    top_5_trends = []
    
    for rank, (theme_name, data) in enumerate(
        sorted(theme_scores.items(), key=lambda x: x[1]["final_score"], reverse=True)[:5],
        start=1
    ):
        trend = {
            "rank": rank,
            "trend_keyword": theme_name,
            "final_score": data["final_score"],
            "tech": data["tech"],
            "market": data["market"],
            "competition": data["competition"],
            "cagr": data["cagr"],
            "evidence": data["evidence"]
        }
        
        top_5_trends.append(trend)
        
        # 로깅
        logger.info(f"[{rank}위] {theme_name}")
        logger.info(f"      최종 점수: {data['final_score']:.1f}/100")
        logger.info(f"      대표 기술: {data['tech']['tech_name']} (성숙도 {data['tech_score']:.1f})")
        logger.info(f"      대표 시장: {data['market']['demand_name']} (기회 {data['market_score']:.1f})")
        logger.info(f"      시장 성장률: {data['cagr']*100:.1f}% CAGR")
        logger.info(f"      경쟁 강도: {data['competition']:.1f}/100")
        logger.info(f"      근거:")
        logger.info(f"         - 기술 {data['evidence']['tech_count']}개: {', '.join(data['evidence']['tech_examples'])}")
        logger.info(f"         - 시장 {data['evidence']['market_count']}개: {', '.join(data['evidence']['market_examples'])}\n")
    
    # =================================================================
    # 3️⃣ RAG 인사이트 통합 (선택)
    # =================================================================
    if rag_analysis.get("answer"):
        logger.info("📚 RAG 인사이트 통합 중...")
        
        for trend in top_5_trends:
            trend["rag_insight"] = {
                "answer": rag_analysis["answer"][:500],  # 500자만
                "sources": rag_analysis.get("sources", [])[:2]  # 상위 2개 출처
            }
        
        logger.info("   ✓ 각 테마에 RAG 인사이트 추가 완료\n")
    
    # =================================================================
    # 4️⃣ 최종 요약
    # =================================================================
    logger.info("="*70)
    logger.info("✅ Agent 4: 교차 분석 완료")
    logger.info("="*70)
    logger.info(f"\n📊 분석 결과:")
    logger.info(f"   - 총 테마: {len(theme_scores)}개")
    logger.info(f"   - Top 5 선정 완료")
    logger.info(f"   - 평균 점수: {sum(t['final_score'] for t in top_5_trends) / 5:.1f}")
    logger.info("="*70 + "\n")
    
    return {
        "top_5_trends": top_5_trends,
        "all_theme_scores": theme_scores,  # 전체 테마 점수 (디버깅용)
        "messages": [{
            "role": "assistant",
            "content": f"Top 5 트렌드 선정 완료: {', '.join([t['trend_keyword'] for t in top_5_trends])}"
        }],
        "step_cross": "completed"
    }