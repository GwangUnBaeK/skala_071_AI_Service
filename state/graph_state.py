# state/graph_state.py
from typing import TypedDict, List, Dict, Annotated, Optional
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    user_query: str
    keywords: List[str]
    messages: Annotated[list, add_messages]
    
    # 데이터 수집
    papers: List[Dict]
    github_repos: List[Dict]
    google_trends: Dict
    
    # 분석 결과
    tech_trends: List[Dict]
    market_demands: List[Dict]
    
    # RAG 분석 결과
    rag_analysis: Dict
    
    # 최종 결과
    trend_matrix: List[Dict]
    top_5_trends: List[Dict]
    final_report: str
    
    # 메타데이터 - 각 노드별 독립 (병렬 안전)
    step_collector: Optional[str]
    step_tech: Optional[str]
    step_market: Optional[str]
    step_rag: Optional[str]
    step_cross: Optional[str]
    step_report: Optional[str]
    
    error_log: List[str]