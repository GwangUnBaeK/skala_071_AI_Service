# state/graph_state.py
from typing import TypedDict, List, Dict, Annotated
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
   
    # 입력
    user_query: str
    keywords: List[str]
    
    # 메시지 (add_messages로 자동 누적)
    messages: Annotated[list, add_messages]
    
    # Agent 1: 데이터 수집
    papers: List[Dict]
    github_repos: List[Dict]
    google_trends: Dict
    
    # Agent 2: 기술 분석
    tech_trends: List[Dict]
    
    # Agent 3: 시장 분석
    market_demands: List[Dict]

    # RAG 분석 결과
    rag_analysis: Dict
    
    # Agent 4: 교차 분석
    trend_matrix: List[Dict]
    top_5_trends: List[Dict]
    
    # Agent 5: 보고서
    final_report: str
    
    # 메타데이터
    current_step: str
    error_log: List[str]