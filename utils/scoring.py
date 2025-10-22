# utils/scoring.py
"""점수 계산 유틸리티"""

def calculate_maturity_score(paper_count: int, github_stars: int, num_products: int) -> float:
    """기술 성숙도 점수 (0~100)"""
    product_ratio = min(num_products / max(paper_count / 100, 1), 1.0)
    github_score = min(github_stars / 100000, 1.0)
    
    score = (0.5 * product_ratio + 0.5 * github_score) * 100
    return round(score, 1)

def calculate_opportunity_score(tam_usd: int, cagr: float, gov_support: bool) -> float:
    """시장 기회 점수 (0~100)"""
    tam_score = min(tam_usd / 1_000_000_000, 1.0) * 40
    growth_score = min(cagr / 0.5, 1.0) * 30
    gov_score = 30 if gov_support else 0
    
    return round(tam_score + growth_score + gov_score, 1)

def calculate_final_score(
    tech_score: float,
    market_score: float,
    growth_rate: float,
    competition: float
) -> float:
    """최종 트렌드 점수 (0~100)"""
    # 가중치
    w_tech = 0.25
    w_market = 0.35
    w_growth = 0.25
    w_comp = 0.15
    
    score = (
        w_tech * tech_score +
        w_market * market_score +
        w_growth * (growth_rate * 100) -
        w_comp * competition
    )
    
    return round(score, 1)