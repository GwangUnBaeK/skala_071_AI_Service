# nodes/collector_node.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.graph_state import GraphState
from tools.arxiv_tool import search_arxiv_papers
from tools.github_tool import search_github_repos
from tools.trends_tool import search_google_trends
from utils.logger import logger
from config.settings import settings
from config.keywords import canonicalize_keywords


def data_collector_node(state: GraphState) -> GraphState:
    """
    Agent 1: 데이터 수집
    arXiv 논문, GitHub 저장소, Google Trends 데이터 수집
    (B2B Seed 기반 키워드 정규화 적용)
    """
    logger.info("="*70)
    logger.info("📊 Agent 1: 데이터 수집 시작")
    logger.info("="*70)

    # 0) 키워드 준비 (state 우선, 없으면 settings)
    raw_keywords = state.get("keywords", settings.ANALYSIS["keywords"])
    # 정규화 + 화이트리스트 필터
    keywords = canonicalize_keywords(raw_keywords)

    if not keywords:
        logger.error("❌ 유효한 키워드가 없습니다. (정규화/화이트리스트 결과 비어있음)")
        return {
            **state,
            "papers": [],
            "github_repos": [],
            "google_trends": {},
            "error_log": state.get("error_log", []) + ["collector: no valid keywords after normalization"],
            "messages": [{
                "role": "assistant",
                "content": "데이터 수집 실패: 유효 키워드 없음"
            }],
            "step_collector": "failed"
        }

    logger.info(f"\n검색 키워드: {keywords}\n")

    error_log = state.get("error_log", [])

    # 1) arXiv 논문 수집
    papers = []
    try:
        logger.info("1️⃣ arXiv 논문 검색 중...")
        papers = search_arxiv_papers.invoke({
            "keywords": keywords,
            "max_results": settings.LIMITS["arxiv_max_per_keyword"]
        })
        logger.info(f"   ✅ {len(papers)}개 논문 수집 완료\n")
    except Exception as e:
        error_msg = f"arXiv 수집 실패: {str(e)}"
        logger.error(f"   ❌ {error_msg}\n")
        error_log.append(error_msg)

    # 2) GitHub 저장소 수집
    github_repos = []
    try:
        logger.info("2️⃣ GitHub 저장소 검색 중...")
        github_repos = search_github_repos.invoke({
            "keywords": keywords,
            "min_stars": settings.LIMITS["github_min_stars"]
        })
        logger.info(f"   ✅ {len(github_repos)}개 저장소 수집 완료\n")
    except Exception as e:
        error_msg = f"GitHub 수집 실패: {str(e)}"
        logger.error(f"   ❌ {error_msg}\n")
        error_log.append(error_msg)

    # 3) Google Trends 수집 (정규화된 키워드만 대상으로)
    google_trends = {}
    try:
        logger.info("3️⃣ Google Trends 검색 중...")
        timeframe = f"{settings.ANALYSIS['date_range']['start']} {settings.ANALYSIS['date_range']['end']}"
        google_trends = search_google_trends.invoke({
            "keywords": keywords,
            "timeframe": timeframe
        })
        logger.info(f"   ✅ {len(google_trends)}개 키워드 트렌드 수집 완료\n")
    except Exception as e:
        error_msg = f"Google Trends 수집 실패: {str(e)}"
        logger.error(f"   ❌ {error_msg}\n")
        error_log.append(error_msg)

    # 4) 결과 요약
    logger.info("="*70)
    logger.info("✅ Agent 1: 데이터 수집 완료")
    logger.info("="*70)
    logger.info(f"   📄 논문: {len(papers)}개")
    logger.info(f"   🐙 GitHub: {len(github_repos)}개")
    logger.info(f"   📊 Trends: {len(google_trends)}개 키워드")
    logger.info("="*70 + "\n")

    return {
        "keywords": keywords,               # 정규화된 키워드로 덮어써서 이후 노드가 사용
        "papers": papers,
        "github_repos": github_repos,
        "google_trends": google_trends,
        "error_log": error_log,
        "messages": [{
            "role": "assistant",
            "content": f"데이터 수집 완료: 논문 {len(papers)}개, GitHub {len(github_repos)}개"
        }],
        "step_collector": "completed"
    }
