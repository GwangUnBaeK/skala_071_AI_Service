# scripts/run_analysis.py
"""
CLI로 분석 실행
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from main import main
from config.settings import settings
from utils.logger import logger

def cli():
    parser = argparse.ArgumentParser(
        description="AI Trends 2025-2030 분석 시스템",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python scripts/run_analysis.py
  python scripts/run_analysis.py --keywords "AI coding" "AI video"
  python scripts/run_analysis.py --quick
        """
    )
    
    parser.add_argument(
        "--keywords",
        nargs="+",
        help="분석 키워드 (기본값: config/settings.py 사용)"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="빠른 모드 (데이터 수집 제한: 논문 50개, GitHub 20개)"
    )
    
    parser.add_argument(
        "--no-rag",
        action="store_true",
        help="RAG 분석 스킵"
    )
    
    args = parser.parse_args()
    
    # 키워드 오버라이드
    if args.keywords:
        logger.info(f"🔍 커스텀 키워드 사용: {args.keywords}")
        settings.ANALYSIS["keywords"] = args.keywords
    
    # 빠른 모드
    if args.quick:
        logger.info(f"⚡ 빠른 모드 활성화")
        settings.LIMITS["arxiv_max_per_keyword"] = 50
        settings.LIMITS["github_max_per_keyword"] = 20
    
    # RAG 스킵
    if args.no_rag:
        logger.info(f"⏭️  RAG 분석 스킵")
        # workflow_config에서 RAG 노드 제거
        from config import workflow_config
        if "rag_analyzer" in workflow_config.WORKFLOW_NODES:
            workflow_config.WORKFLOW_NODES.remove("rag_analyzer")
            # 엣지 재연결
            workflow_config.WORKFLOW_EDGES = [
                e for e in workflow_config.WORKFLOW_EDGES 
                if "rag_analyzer" not in e
            ]
            workflow_config.WORKFLOW_EDGES.append(("market_analyzer", "cross_analyzer"))
    
    # 실행
    main()

if __name__ == "__main__":
    cli()