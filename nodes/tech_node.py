# nodes/tech_node.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.graph_state import GraphState
from collections import Counter
from utils.logger import logger

def calculate_maturity_score(paper_count: int, github_stars: int, num_repos: int) -> float:
    """기술 성숙도 점수 계산"""
    # 논문 대비 제품(GitHub) 비율
    product_ratio = min(num_repos / max(paper_count / 100, 1), 1.0)
    
    # GitHub 활동도
    github_score = min(github_stars / 100000, 1.0)
    
    # 성숙도 = 50% 제품화 + 50% GitHub 활동
    score = (0.5 * product_ratio + 0.5 * github_score) * 100
    return round(score, 1)

def tech_analysis_node(state: GraphState) -> GraphState:
    """
    Agent 2: 기술 트렌드 분석
    논문과 GitHub 데이터로 기술별 성숙도 계산
    """
    logger.info("="*70)
    logger.info("🔬 Agent 2: 기술 트렌드 분석 시작")
    logger.info("="*70)
    
    papers = state.get("papers", [])
    github_repos = state.get("github_repos", [])
    
    logger.info(f"\n입력 데이터:")
    logger.info(f"   - 논문: {len(papers)}개")
    logger.info(f"   - GitHub: {len(github_repos)}개\n")
    
    # 1. 키워드 빈도 분석
    all_keywords = []
    for paper in papers:
        all_keywords.extend(paper.get("keywords", []))
    
    keyword_counts = Counter(all_keywords)
    top_keywords = keyword_counts.most_common(20)
    
    logger.info(f"상위 20개 기술 키워드 추출 완료\n")
    
    # 2. 각 기술별 성숙도 계산
    tech_trends = []
    
    for keyword, count in top_keywords:
        # 관련 GitHub 저장소 찾기
        related_repos = [
            r for r in github_repos 
            if keyword.lower() in r["name"].lower() 
            or keyword.lower() in r.get("description", "").lower()
        ]
        
        total_stars = sum(r["stars"] for r in related_repos)
        
        # 성숙도 점수
        maturity_score = calculate_maturity_score(
            paper_count=count,
            github_stars=total_stars,
            num_repos=len(related_repos)
        )
        
        tech_trends.append({
            "tech_id": f"tech_{len(tech_trends):03d}",
            "tech_name": keyword,
            "maturity_score": maturity_score,
            "paper_count": count,
            "github_stars_total": total_stars,
            "num_repos": len(related_repos),
            "related_projects": [r["name"] for r in related_repos[:3]]
        })
        
        logger.info(f"   [{len(tech_trends):2d}] {keyword:30s} | "
                   f"성숙도: {maturity_score:5.1f} | "
                   f"논문: {count:4d} | "
                   f"Stars: {total_stars:7,d}")
    
    # 3. 성숙도 순으로 정렬
    tech_trends.sort(key=lambda x: x["maturity_score"], reverse=True)
    
    logger.info(f"\n상위 5개 기술 (성숙도 기준):")
    for i, tech in enumerate(tech_trends[:5], 1):
        logger.info(f"   {i}. {tech['tech_name']:30s} ({tech['maturity_score']}점)")
    
    logger.info("\n" + "="*70)
    logger.info("✅ Agent 2: 기술 분석 완료")
    logger.info("="*70)
    logger.info(f"   총 {len(tech_trends)}개 기술 트렌드 발굴")
    logger.info("="*70 + "\n")
    
    return {
        "tech_trends": tech_trends,
        "messages": [{
            "role": "assistant",
            "content": f"기술 분석 완료: {len(tech_trends)}개 트렌드 발굴"
        }],
        "current_step": "tech_analyzed"
    }