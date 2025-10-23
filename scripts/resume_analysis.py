# scripts/resume_analysis.py
"""
중단된 분석 재개
"""
# scripts/resume_analysis.py (계속)
"""
중단된 분석 재개
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from graph.workflow import create_workflow
from utils.logger import logger
from datetime import datetime

def resume_analysis(thread_id: str):
    """
    중단된 분석 재개
    
    Args:
        thread_id: 재개할 thread ID
    """
    logger.info("="*70)
    logger.info("🔄 분석 재개")
    logger.info("="*70)
    logger.info(f"\n📍 Thread ID: {thread_id}\n")
    
    # Workflow 생성
    app = create_workflow()
    
    # 설정
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    # 이전 상태 확인
    try:
        previous_state = app.get_state(config)
        
        if not previous_state or not previous_state.values:
            logger.error("❌ 이전 상태를 찾을 수 없습니다!")
            logger.error(f"   Thread ID '{thread_id}'가 올바른지 확인하세요.")
            return False
        
        logger.info("✅ 이전 상태 발견")
        logger.info(f"   마지막 업데이트: {previous_state.created_at}")
        
        # 완료된 단계 확인
        values = previous_state.values
        completed = []
        if values.get("step_collector"): completed.append("collector")
        if values.get("step_tech"): completed.append("tech")
        if values.get("step_market"): completed.append("market")
        if values.get("step_rag"): completed.append("rag")
        if values.get("step_cross"): completed.append("cross")
        if values.get("step_report"): completed.append("report")
        
        logger.info(f"   완료된 단계: {', '.join(completed) if completed else '없음'}")
        
        # 재개
        logger.info("\n▶️  분석 재개 중...\n")
        
        for event in app.stream(None, config, stream_mode="values"):
            # 진행 상황 출력
            if event.get("step_collector") and "collector" not in completed:
                logger.info("✅ Collector 완료")
                completed.append("collector")
            if event.get("step_tech") and "tech" not in completed:
                logger.info("✅ Tech Analyzer 완료")
                completed.append("tech")
            if event.get("step_market") and "market" not in completed:
                logger.info("✅ Market Analyzer 완료")
                completed.append("market")
            if event.get("step_rag") and "rag" not in completed:
                logger.info("✅ RAG Analyzer 완료")
                completed.append("rag")
            if event.get("step_cross") and "cross" not in completed:
                logger.info("✅ Cross Analyzer 완료")
                completed.append("cross")
            if event.get("step_report") and "report" not in completed:
                logger.info("✅ Report Writer 완료")
                completed.append("report")
        
        # 최종 상태
        final_state = app.get_state(config).values
        
        logger.info("\n" + "="*70)
        logger.info("🎉 분석 재개 완료!")
        logger.info("="*70)
        
        # Top 5 출력
        if final_state.get("top_5_trends"):
            logger.info(f"\n🏆 Top 5 AI 트렌드:")
            for trend in final_state["top_5_trends"]:
                logger.info(f"   {trend['rank']}. {trend['trend_keyword']} ({trend['final_score']:.1f}점)")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ 재개 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def cli():
    parser = argparse.ArgumentParser(description="중단된 분석 재개")
    
    parser.add_argument(
        "--thread-id",
        required=True,
        help="재개할 thread ID"
    )
    
    args = parser.parse_args()
    
    success = resume_analysis(args.thread_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    cli()