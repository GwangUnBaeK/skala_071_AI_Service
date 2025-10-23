# edges/routing.py
"""
조건부 라우팅 로직
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Literal
from state.graph_state import GraphState
from utils.logger import logger

def should_run_rag(state: GraphState) -> Literal["rag_analyzer", "cross_analyzer"]:
    """
    RAG 분석 실행 여부 결정
    
    Returns:
        "rag_analyzer": RAG 실행
        "cross_analyzer": RAG 스킵
    """
    # RAG 문서 확인
    import os
    rag_docs_dir = "data/rag_documents"
    vectorstore_dir = "data/vectorstore"
    
    # 벡터 저장소 존재 여부
    if not os.path.exists(vectorstore_dir):
        logger.warning("⚠️ 벡터 저장소 없음 → RAG 스킵")
        return "cross_analyzer"
    
    # RAG 문서 존재 여부
    if not os.path.exists(rag_docs_dir) or not os.listdir(rag_docs_dir):
        logger.warning("⚠️ RAG 문서 없음 → RAG 스킵")
        return "cross_analyzer"
    
    logger.info("✅ RAG 분석 실행")
    return "rag_analyzer"

def validate_data_quality(state: GraphState) -> Literal["tech_analyzer", "END"]:
    """
    데이터 품질 검증
    최소 데이터 요구사항 미충족 시 분석 중단
    
    Returns:
        "tech_analyzer": 분석 계속
        "END": 분석 중단
    """
    papers = state.get("papers", [])
    github_repos = state.get("github_repos", [])
    
    MIN_PAPERS = 50
    MIN_REPOS = 10
    
    if len(papers) < MIN_PAPERS:
        logger.error(f"❌ 논문 수 부족: {len(papers)}개 < {MIN_PAPERS}개 (최소)")
        logger.error("   분석 중단")
        return "END"
    
    if len(github_repos) < MIN_REPOS:
        logger.error(f"❌ GitHub 저장소 부족: {len(github_repos)}개 < {MIN_REPOS}개 (최소)")
        logger.error("   분석 중단")
        return "END"
    
    logger.info(f"✅ 데이터 품질 검증 통과 (논문 {len(papers)}개, GitHub {len(github_repos)}개)")
    return "tech_analyzer"