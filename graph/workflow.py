# graph/workflow.py 수정
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.graph_state import GraphState
from nodes.collector_node import data_collector_node
from nodes.tech_node import tech_analysis_node
from nodes.market_node import market_analysis_node
from nodes.rag_node import rag_analysis_node  # ✨ 추가
from nodes.cross_node import cross_analysis_node
from nodes.report_node import report_generation_node
from utils.logger import logger

def create_workflow():
    """
    LangGraph Workflow 생성
    """
    logger.info("🏗️ Workflow 생성 중...")
    
    # StateGraph 초기화
    workflow = StateGraph(GraphState)
    
    # 노드 추가
    workflow.add_node("collector", data_collector_node)
    workflow.add_node("tech_analyzer", tech_analysis_node)
    workflow.add_node("market_analyzer", market_analysis_node)
    workflow.add_node("rag_analyzer", rag_analysis_node)      # ✨ RAG 노드 추가
    workflow.add_node("cross_analyzer", cross_analysis_node)
    workflow.add_node("report_writer", report_generation_node)
    
    # 엣지 연결
    workflow.add_edge(START, "collector")
    
    # collector 이후 tech와 market이 병렬 실행
    workflow.add_edge("collector", "tech_analyzer")
    workflow.add_edge("collector", "market_analyzer")
    
    # tech와 market 완료 후 RAG 실행 ✨
    workflow.add_edge("tech_analyzer", "rag_analyzer")
    workflow.add_edge("market_analyzer", "rag_analyzer")
    
    # RAG 완료 후 cross 분석
    workflow.add_edge("rag_analyzer", "cross_analyzer")
    
    # cross 완료 후 보고서 작성
    workflow.add_edge("cross_analyzer", "report_writer")
    
    # 종료
    workflow.add_edge("report_writer", END)
    
    # 메모리 추가
    memory = MemorySaver()
    
    # 컴파일
    app = workflow.compile(checkpointer=memory)
    
    logger.info("✅ Workflow 생성 완료\n")
    return app

def visualize_workflow(app):
    """그래프 시각화"""
    try:
        from langchain_teddynote.graphs import visualize_graph
        visualize_graph(app)
    except ImportError:
        logger.info("\n📊 Workflow 구조 (ASCII):\n")
        print(app.get_graph().draw_ascii())
