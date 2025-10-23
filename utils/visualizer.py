# utils/visualizer.py
"""
결과 시각화 유틸리티
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import logger

# 한글 폰트 설정
def setup_korean_font():
    """한글 폰트 설정"""
    try:
        # Windows
        font_path = "C:/Windows/Fonts/malgun.ttf"
        if os.path.exists(font_path):
            font_name = fm.FontProperties(fname=font_path).get_name()
            plt.rc('font', family=font_name)
        else:
            # Mac/Linux
            plt.rc('font', family='AppleGothic')
        
        plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
    except:
        logger.warning("⚠️ 한글 폰트 설정 실패")

def plot_trend_scores(top_5_trends: list, output_path: str = "outputs/trend_scores.png"):
    """
    Top 5 트렌드 점수 막대 차트
    
    Args:
        top_5_trends: Top 5 트렌드 리스트
        output_path: 저장 경로
    """
    setup_korean_font()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    names = [t['trend_keyword'] for t in top_5_trends]
    scores = [t['final_score'] for t in top_5_trends]
    colors = ['#4CAF50', '#2196F3', '#FFC107', '#FF9800', '#9E9E9E']
    
    bars = ax.barh(names, scores, color=colors)
    
    # 값 표시
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                f'{scores[i]:.1f}점',
                ha='left', va='center', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('최종 점수', fontsize=12)
    ax.set_title('Top 5 AI 트렌드 (2025-2030)', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 100)
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    
    # 저장
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"📊 차트 저장: {output_path}")

def plot_score_breakdown(top_5_trends: list, output_path: str = "outputs/score_breakdown.png"):
    """
    점수 구성 요소 분해 (누적 막대 그래프)
    
    Args:
        top_5_trends: Top 5 트렌드 리스트
        output_path: 저장 경로
    """
    setup_korean_font()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    names = [t['trend_keyword'] for t in top_5_trends]
    
    # 점수 구성 요소
    tech_scores = [t['tech']['maturity_score'] * 0.25 for t in top_5_trends]
    market_scores = [t['market']['opportunity_score'] * 0.35 for t in top_5_trends]
    growth_scores = [t['market']['cagr'] * 100 * 0.25 for t in top_5_trends]
    comp_scores = [t['competition'] * 0.15 for t in top_5_trends]
    
    # 누적 막대 그래프
    ax.barh(names, tech_scores, label='기술 성숙도 (25%)', color='#4CAF50')
    ax.barh(names, market_scores, left=tech_scores, label='시장 기회 (35%)', color='#2196F3')
    
    left_sum = [tech_scores[i] + market_scores[i] for i in range(len(names))]
    ax.barh(names, growth_scores, left=left_sum, label='성장률 (25%)', color='#FFC107')
    
    # 경쟁 강도 (마이너스)
    total = [left_sum[i] + growth_scores[i] for i in range(len(names))]
    ax.barh(names, [-c for c in comp_scores], left=total, label='경쟁 강도 (-15%)', color='#F44336')
    
    ax.set_xlabel('점수 기여도', fontsize=12)
    ax.set_title('트렌드 점수 구성 요소', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"📊 차트 저장: {output_path}")

def plot_tech_market_heatmap(trend_matrix: list, output_path: str = "outputs/tech_market_heatmap.png"):
    """
    기술×시장 히트맵
    
    Args:
        trend_matrix: 전체 트렌드 매트릭스
        output_path: 저장 경로
    """
    import pandas as pd
    import seaborn as sns
    
    setup_korean_font()
    
    # 데이터 변환
    data = []
    for item in trend_matrix[:50]:  # 상위 50개만
        data.append({
            'tech': item['tech']['tech_name'],
            'market': item['market']['demand_name'][:15],  # 이름 제한
            'score': item['final_score']
        })
    
    df = pd.DataFrame(data)
    pivot = df.pivot_table(values='score', index='market', columns='tech', aggfunc='mean')
    
    # 히트맵
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax, cbar_kws={'label': '점수'})
    
    ax.set_title('기술 × 시장 매칭 점수', fontsize=14, fontweight='bold')
    ax.set_xlabel('기술', fontsize=12)
    ax.set_ylabel('시장', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"📊 차트 저장: {output_path}")