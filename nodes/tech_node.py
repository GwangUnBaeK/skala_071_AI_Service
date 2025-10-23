# nodes/tech_node.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.graph_state import GraphState
from collections import Counter
from utils.logger import logger

# -----------------------------
# 튜닝 가능한 기준값 (B2B 제품화 중심)
# -----------------------------
ELIGIBILITY_MIN_REPOS = 2        # 레포 수가 이 값 미만이고
ELIGIBILITY_MIN_STARS = 200      # 총 Stars도 이 값 미만이면 → 제외
PENALTY_MIN_REPOS = 3            # 레포 수가 이 값 미만이면 경미한 감점
PENALTY_MIN_STARS = 500          # 총 Stars가 이 값 미만이면 경미한 감점

def calculate_maturity_score(paper_count: int, github_stars: int, num_repos: int) -> float:
    """
    B2B 제품화 중심 성숙도 계산:
    - 제품화 비율(60%) + GitHub 활동(40%)
    - 제품화 비율: 레포 수 / (논문 수/80) → 상한 1.0
    - GitHub 활동: 총 Stars / 50,000 → 상한 1.0
    """
    # 제품화 비율 (논문 대비 구현 빈도)
    denom = max(paper_count / 80.0, 1.0)  # 더 엄격한 분모
    product_ratio = min(num_repos / denom, 1.0)

    # GitHub 활동
    github_score = min(github_stars / 50000.0, 1.0)

    score = (0.6 * product_ratio + 0.4 * github_score) * 100.0
    return round(score, 1)

def tech_analysis_node(state: GraphState) -> GraphState:
    """
    Agent 2: 기술 트렌드 분석 (개선판)
    - 논문 키워드 빈도 → 상위 후보 추출
    - GitHub와 매칭하여 '제품화 중심' 성숙도 계산
    - 최소 레포/스타 기준으로 '연구만 뜨거운' 키워드 제외/감점
    - 근거(evidence) 필드 추가
    """
    logger.info("="*70)
    logger.info("🔬 Agent 2: 기술 트렌드 분석 시작 (B2B 제품화 중심)")
    logger.info("="*70)

    papers = state.get("papers", [])
    github_repos = state.get("github_repos", [])

    logger.info(f"\n입력 데이터:")
    logger.info(f"   - 논문: {len(papers)}개")
    logger.info(f"   - GitHub: {len(github_repos)}개\n")

    # 1) 논문 키워드 빈도 분석
    all_keywords = []
    for paper in papers:
        all_keywords.extend(paper.get("keywords", []))

    keyword_counts = Counter([k for k in all_keywords if k])  # 빈 문자열 방지
    top_keywords = keyword_counts.most_common(20)  # 과도 확장 방지

    logger.info(f"상위 20개 기술 키워드 추출 완료\n")

    # 2) 키워드별 GitHub 매칭 및 성숙도 계산
    tech_trends = []

    for keyword, count in top_keywords:
        kw_lower = keyword.lower()

        # 관련 GitHub 저장소 찾기(이름/설명 매칭)
        related_repos = [
            r for r in github_repos
            if kw_lower in (r.get("name","").lower())
            or kw_lower in (r.get("description","").lower())
            or any(kw_lower == (k or "").lower() for k in r.get("keywords", []))
        ]

        total_stars = sum(int(r.get("stars", 0)) for r in related_repos)
        num_repos = len(related_repos)

        # 자격요건(eligibility) 체크: 레포·스타 모두 너무 적으면 제외
        if num_repos < ELIGIBILITY_MIN_REPOS and total_stars < ELIGIBILITY_MIN_STARS:
            # 연구만 뜨거운 키워드로 간주하여 스킵
            continue

        # 기본 성숙도 점수
        maturity_score = calculate_maturity_score(
            paper_count=count,
            github_stars=total_stars,
            num_repos=num_repos
        )

        # 경미한 패널티: 어느 한쪽만 부족할 때
        penalty_factor = 1.0
        if num_repos < PENALTY_MIN_REPOS:
            penalty_factor *= 0.90
        if total_stars < PENALTY_MIN_STARS:
            penalty_factor *= 0.92

        maturity_score = round(maturity_score * penalty_factor, 1)

        # 대표 프로젝트 3개 (stars desc)
        top_projects = sorted(
            related_repos,
            key=lambda x: int(x.get("stars", 0)),
            reverse=True
        )[:3]

        evidence_projects = [
            {
                "name": p.get("name", ""),
                "url": p.get("url", p.get("html_url", "")),
                "stars": int(p.get("stars", 0))
            }
            for p in top_projects
        ]

        tech_trends.append({
            "tech_id": f"tech_{len(tech_trends):03d}",
            "tech_name": keyword,
            "maturity_score": maturity_score,
            "paper_count": int(count),
            "github_stars_total": int(total_stars),
            "num_repos": int(num_repos),
            "related_projects": [p["name"] for p in evidence_projects],
            "evidence": {
                "maturity": {
                    "paper_count": int(count),
                    "repo_count": int(num_repos),
                    "stars_total": int(total_stars),
                    "penalty_applied": penalty_factor < 1.0
                },
                "projects": evidence_projects
            }
        })

        logger.info(
            f"   [{len(tech_trends):2d}] {keyword:30s} | "
            f"성숙도: {maturity_score:5.1f} | "
            f"논문: {count:4d} | "
            f"Repos: {num_repos:3d} | "
            f"Stars: {total_stars:7d}"
        )

    # 3) 성숙도 순으로 정렬
    tech_trends.sort(key=lambda x: x["maturity_score"], reverse=True)

    logger.info(f"\n상위 5개 기술 (성숙도 기준):")
    for i, tech in enumerate(tech_trends[:5], 1):
        logger.info(f"   {i}. {tech['tech_name']:30s} ({tech['maturity_score']}점)")

    logger.info("\n" + "="*70)
    logger.info("✅ Agent 2: 기술 분석 완료")
    logger.info("="*70)
    logger.info(f"   총 {len(tech_trends)}개 기술 트렌드 발굴 (자격요건 필터 적용)")
    logger.info("="*70 + "\n")

    return {
        "tech_trends": tech_trends,
        "messages": [{
            "role": "assistant",
            "content": f"기술 분석 완료: {len(tech_trends)}개 트렌드 발굴"
        }],
        "step_tech": "completed"
    }
