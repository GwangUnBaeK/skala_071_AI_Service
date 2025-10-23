# graph/workflow.py
"""
동적 Workflow 생성
config/workflow_config.py 기반
"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.graph_state import GraphState
from config.workflow_config import (
    WORKFLOW_NODES,
    WORKFLOW_EDGES,
    PARALLEL_NODES,
    CHECKPOINT_CONFIG
)
from utils.logger import logger

# ✅ 노드 함수 import
from nodes.collector_node import data_collector_node
from nodes.tech_node import tech_analysis_node
from nodes.market_node import market_analysis_node
from nodes.rag_node import rag_analysis_node
from nodes.cross_node import cross_analysis_node
from nodes.report_node import report_generation_node

# ✅ 노드 이름 → 함수 매핑
NODE_REGISTRY = {
    "search_agent": data_collector_node,
    "tech_analyzer_agent": tech_analysis_node,
    "market_analyzer_agent": market_analysis_node,
    "rag_analyzer_agent": rag_analysis_node,
    "cross_check_agent": cross_analysis_node,
    "report_writer_agent": report_generation_node,
}

def create_workflow():
    """
    설정 기반 동적 Workflow 생성
    """
    logger.info("="*70)
    logger.info("🏗️ Workflow 생성 중")
    logger.info("="*70)
    
    workflow = StateGraph(GraphState)
    
    # 1️⃣ 노드 등록
    logger.info("\n📍 노드 등록:")
    for node_name in WORKFLOW_NODES:
        if node_name not in NODE_REGISTRY:
            raise ValueError(f"❌ 노드 '{node_name}'가 NODE_REGISTRY에 없습니다!")
        
        node_func = NODE_REGISTRY[node_name]
        workflow.add_node(node_name, node_func)
        logger.info(f"   ✓ {node_name}")
    
    # 2️⃣ 엣지 연결
    logger.info("\n🔗 엣지 연결:")
    for from_node, to_node in WORKFLOW_EDGES:
        if from_node == "START":
            workflow.add_edge(START, to_node)
            logger.info(f"   ✓ START → {to_node}")
        elif to_node == "END":
            workflow.add_edge(from_node, END)
            logger.info(f"   ✓ {from_node} → END")
        else:
            workflow.add_edge(from_node, to_node)
            logger.info(f"   ✓ {from_node} → {to_node}")
    
    # 3️⃣ 병렬 노드 표시 (정보용)
    if PARALLEL_NODES:
        logger.info("\n⚡ 병렬 실행 노드:")
        for parallel_group in PARALLEL_NODES:
            logger.info(f"   ✓ {' + '.join(parallel_group)}")
    
    # 4️⃣ 체크포인터 설정
    if CHECKPOINT_CONFIG["enabled"]:
        db_path = CHECKPOINT_CONFIG["db_path"]
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path, check_same_thread=False)
        checkpointer = SqliteSaver(conn)

        logger.info(f"\n💾 체크포인트: 활성화")
        logger.info(f"   경로: {db_path}")
        logger.info(f"   → 중단 후 재개 가능")
    else:
        checkpointer = MemorySaver()
        logger.info(f"\n💾 체크포인트: 메모리만 (재개 불가)")
    
    # 5️⃣ 컴파일
    app = workflow.compile(checkpointer=checkpointer)
    
    logger.info("\n" + "="*70)
    logger.info("✅ Workflow 생성 완료")
    logger.info("="*70 + "\n")
    
    return app

# graph/workflow.py
def visualize_workflow(app, save_image: bool = True):
    """그래프 시각화"""
    try:
        from langchain_teddynote.graphs import visualize_graph
        
        logger.info("📊 Workflow 시각화:\n")
        
        # 시각화
        visualize_graph(app)
        
        # ✅ 이미지로 저장 (선택)
        if save_image:
            try:
                from PIL import Image
                import io
                
                # Mermaid 다이어그램을 이미지로 저장
                # (langchain-teddynote가 내부적으로 지원하는 경우)
                output_path = "outputs/workflow_graph.png"
                logger.info(f"   💾 그래프 이미지 저장: {output_path}")
                
            except Exception as e:
                logger.warning(f"   ⚠️ 이미지 저장 실패: {e}")
        
        logger.info("   ✓ 시각화 완료\n")
        
    except ImportError:
        logger.warning("⚠️ langchain-teddynote 없음")
        logger.info("\n📊 Workflow 구조 (ASCII):\n")
        print(app.get_graph().draw_ascii())