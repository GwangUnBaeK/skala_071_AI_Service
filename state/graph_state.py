# state/graph_state.py
from typing import TypedDict, Optional, Annotated
from operator import add

class GraphState(TypedDict):
    """
    AI Trends 2025-2030 분석 그래프 상태
    
    messages, error_log는 Annotated[list, add]로 자동 병합됨
    """
    
    # ==========================================
    # 입력 데이터
    # ==========================================
    user_query: str                # 사용자 질의
    keywords: list                 # 검색 키워드 (정규화 후)
    
    # ==========================================
    # 수집 데이터 (Agent 1)
    # ==========================================
    papers: list                   # arXiv 논문 목록
    github_repos: list             # GitHub 저장소 목록
    google_trends: dict            # Google Trends 데이터
    
    # ==========================================
    # 분석 결과 (Agent 2, 3, 4)
    # ==========================================
    tech_trends: list              # 기술 트렌드 분석 결과
    market_trends: list            # 시장 수요 분석 결과
    rag_analysis: dict             # RAG 문서 분석 결과
    top_5_trends: list             # 최종 Top 5 트렌드
    all_theme_scores: Optional[dict]  # 전체 테마 점수 (디버깅용)
    
    # ==========================================
    # 최종 출력 (Agent 5)
    # ==========================================
    final_report: str              # 최종 보고서 (Markdown)
    
    # ==========================================
    # 누적 데이터 (자동 병합)
    # ==========================================
    messages: Annotated[list, add]      # 각 노드의 메시지 (자동 추가)
    error_log: Annotated[list, add]     # 에러 로그 (자동 추가)
    
    # ==========================================
    # 진행 상태 (각 노드별)
    # ==========================================
    step_collector: Optional[str]   # "completed" | "failed" | None
    step_tech: Optional[str]
    step_market: Optional[str]
    step_rag: Optional[str]
    step_cross: Optional[str]
    step_report: Optional[str]