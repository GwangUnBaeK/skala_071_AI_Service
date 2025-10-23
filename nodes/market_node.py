# nodes/market_node.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.graph_state import GraphState
from tools.market_tool import search_market_reports
from utils.logger import logger
from config.settings import settings

B2B_MARKET_TEMPLATES = [
    {
        "demand_name": "SME automation",
        "problem_statement": "중소기업의 회계·인사·고객지원 업무를 AI로 자동화하여 비용을 절감",
        "industries": ["Manufacturing", "Finance", "Retail"],
        "search_keywords": ["SME automation AI", "enterprise RPA AI", "workflow automation AI"],
        "tam_usd": 12_000_000_000,  # $12B
        "cagr": 0.28,  # 28% CAGR
        "target_companies": 150_000,
        "regions": ["Global", "North America", "Europe", "Asia-Pacific"],
    },
    {
        "demand_name": "Contact center automation",
        "problem_statement": "고객 응대 업무를 AI Agent와 음성인식으로 자동화",
        "industries": ["Telecom", "Banking", "Insurance"],
        "search_keywords": ["contact center AI", "call center AI", "voicebot AI customer support"],
        "tam_usd": 8_000_000_000,  # $8B
        "cagr": 0.32,  # 32% CAGR
        "target_companies": 80_000,
        "regions": ["Global", "North America", "Asia-Pacific"],
    },
    {
        "demand_name": "Developer productivity",
        "problem_statement": "AI 코드 어시스턴트를 활용해 개발자 생산성을 향상",
        "industries": ["IT Services", "Software"],
        "search_keywords": ["developer productivity AI", "AI code assistant", "software engineering AI"],
        "tam_usd": 10_000_000_000,  # $10B
        "cagr": 0.35,  # 35% CAGR
        "target_companies": 200_000,
        "regions": ["Global"],
    },
    {
        "demand_name": "Privacy and sovereign AI",
        "problem_statement": "데이터 주권 보호를 위한 온프레미스 AI 솔루션 수요 확대",
        "industries": ["Public Sector", "Finance", "Healthcare"],
        "search_keywords": ["sovereign AI", "private LLM", "AI data governance"],
        "tam_usd": 6_000_000_000,  # $6B
        "cagr": 0.22,  # 22% CAGR
        "target_companies": 30_000,
        "regions": ["Europe", "Asia-Pacific", "Middle East"],
    },
    {
        "demand_name": "Manufacturing quality",
        "problem_statement": "생산 라인의 품질 검사를 AI 비전으로 자동화",
        "industries": ["Manufacturing", "Automotive"],
        "search_keywords": ["AI visual inspection", "smart factory AI", "industrial AI"],
        "tam_usd": 7_000_000_000,  # $7B
        "cagr": 0.26,  # 26% CAGR
        "target_companies": 50_000,
        "regions": ["Asia-Pacific", "North America", "Europe"],
    },
    {
        "demand_name": "Health diagnostics",
        "problem_statement": "의료영상 및 진단 AI로 의사 의사결정을 지원",
        "industries": ["Healthcare"],
        "search_keywords": ["medical imaging AI", "diagnostics AI", "healthcare AI platform"],
        "tam_usd": 9_000_000_000,  # $9B
        "cagr": 0.30,  # 30% CAGR
        "target_companies": 40_000,
        "regions": ["Global", "North America", "Europe"],
    },
    {
        "demand_name": "Personalized learning",
        "problem_statement": "AI 기반 학습자 맞춤형 교육 콘텐츠 제공",
        "industries": ["Education Tech"],
        "search_keywords": ["personalized learning AI", "adaptive education AI", "edtech AI"],
        "tam_usd": 5_000_000_000,  # $5B
        "cagr": 0.27,  # 27% CAGR
        "target_companies": 100_000,
        "regions": ["Global", "North America", "Asia-Pacific"],
    },
]


def market_analysis_node(state: GraphState) -> GraphState:
    """
    Agent 3: 시장 분석 (B2B 중심)
    - B2B_MARKET_TEMPLATES 기반 시장 기회 평가
    - Tavily API로 실시간 시장 리포트 검색
    - 시장 규모(TAM), 성장률(CAGR), 타겟 기업 수 포함
    """
    logger.info("=" * 70)
    logger.info("📈 Agent 3: 시장 분석 시작 (B2B 중심)")
    logger.info("=" * 70)

    keywords = state.get("keywords", []) or []
    keywords_lower = [str(k).lower() for k in keywords]
    error_log = state.get("error_log", [])
    results = []

    for domain in B2B_MARKET_TEMPLATES:
        demand = domain["demand_name"]
        search_terms = domain["search_keywords"]
        logger.info(f"\n🔍 시장 검색 → {demand}")

        # Tavily 검색
        try:
            tavily_reports = search_market_reports.invoke({
                "queries": search_terms,
                "max_results": settings.LIMITS.get("market_max_per_query", 5)
            })
        except Exception as e:
            msg = f"Tavily 검색 실패 ({demand}): {e}"
            logger.error(msg)
            error_log.append(msg)
            tavily_reports = []

        # 기회 점수 계산
        base_score = 50.0
        base_score += min(len(tavily_reports) * 8.0, 40.0)  # 리포트 수 기반

        # 키워드 매칭 보너스
        search_terms_text = " ".join(search_terms).lower()
        overlap = any(k in search_terms_text for k in keywords_lower)
        if overlap:
            base_score += 10.0

        final_score = round(min(base_score, 100.0), 1)

        # 상위 3개 리포트만 증거로 저장
        top_reports = tavily_reports[:3] if tavily_reports else []
        evidence_links = [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "source": r.get("source", ""),
                "published_date": r.get("published_date", "")
            }
            for r in top_reports
        ]

        # ✅ 결과 생성 (템플릿의 시장 데이터 포함)
        result = {
            "market_id": f"market_{len(results):03d}",
            "demand_name": domain["demand_name"],
            "opportunity_score": final_score,
            "industries": domain["industries"],
            "problem_statement": domain["problem_statement"],
            
            # ✅ 시장 데이터 (템플릿에서 가져옴)
            "tam_usd": domain["tam_usd"],
            "cagr": domain["cagr"],
            "target_companies": domain["target_companies"],
            "regions": domain["regions"],
            
            "evidence": {
                "reports": evidence_links,
                "search_terms": search_terms
            }
        }
        results.append(result)
        
        logger.info(f" → {demand:30s} | 기회점수 {final_score:5.1f} | 리포트 {len(evidence_links)} 건")

    # 점수 순으로 정렬
    results.sort(key=lambda x: x["opportunity_score"], reverse=True)

    logger.info("\n상위 3개 B2B 시장 기회:")
    for i, r in enumerate(results[:3], 1):
        logger.info(f" {i}. {r['demand_name']:30s} ({r['opportunity_score']}점)")

    logger.info("\n" + "=" * 70)
    logger.info("✅ Agent 3: 시장 분석 완료")
    logger.info("=" * 70 + "\n")

    return {
        "market_trends": results,
        "messages": [{
            "role": "assistant",
            "content": f"시장 분석 완료: {len(results)}개 도메인 평가"
        }],
        "step_market": "completed",
        "error_log": error_log
    }