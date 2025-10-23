# config/workflow_config.py
"""
Workflow 설정
노드 추가/삭제/순서 변경이 여기서 가능
"""

# 사용할 노드 목록
WORKFLOW_NODES = [
    "search_agent",
    "tech_analyzer_agent",
    "market_analyzer_agent",
    "rag_analyzer_agent",
    "cross_check_agent",
    "report_writer_agent"
]

# 엣지 연결 정의
WORKFLOW_EDGES = [
    # (from, to)
    ("START", "search_agent"),
    ("search_agent", "tech_analyzer_agent"),
    ("search_agent", "market_analyzer_agent"),
    ("tech_analyzer_agent", "rag_analyzer_agent"),
    ("market_analyzer_agent", "rag_analyzer_agent"),
    ("rag_analyzer_agent", "cross_check_agent"),
    ("cross_check_agent", "report_writer_agent"),
    ("report_writer_agent", "END"),
]

# 병렬 실행 노드 (문서화 목적)
PARALLEL_NODES = [
    ["tech_analyzer_agent", "market_analyzer_agent"]
]

# 선택적 노드 (조건부 실행)
OPTIONAL_NODES = {
    "rag_analyzer_agent": {
        "condition": "has_rag_documents",
        "skip_to": "cross_check_agent"
    }
}

# 체크포인트 설정
CHECKPOINT_CONFIG = {
    "enabled": True,  # False면 메모리만 사용
    "db_path": "outputs/checkpoints/workflow.db"
}