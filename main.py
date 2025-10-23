# main.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph.workflow import create_workflow, visualize_workflow
from config.settings import settings
from utils.logger import logger
from utils.visualizer import plot_trend_scores, plot_score_breakdown
from datetime import datetime

def main():
    """메인 실행 함수"""
    start_time = datetime.now()
    
    logger.info("="*70)
    logger.info("🚀 AI TRENDS 2025-2030 분석 시작")
    logger.info("="*70)
    logger.info(f"\n📅 실행 시각: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📊 분석 기간: {settings.ANALYSIS['date_range']['start']} ~ {settings.ANALYSIS['date_range']['end']}")
    logger.info(f"🔍 검색 키워드: {len(settings.ANALYSIS['keywords'])}개")
    logger.info(f"🎯 목표: Top {settings.ANALYSIS['num_trends']}개 트렌드 발굴\n")
    
    # 1. Workflow 생성
    app = create_workflow()
    
    # 2. 그래프 시각화
    visualize_workflow(app)
    
    # 3. 초기 상태 설정
    initial_state = {
        "user_query": "2025-2030 AI 트렌드 분석 및 Top 5 예측",
        "keywords": settings.ANALYSIS["keywords"],
        "messages": [],
        "error_log": [],
        # 모든 step 초기화
        "step_collector": None,
        "step_tech": None,
        "step_market": None,
        "step_rag": None,
        "step_cross": None,
        "step_report": None,
    }
    
    # 4. 실행 설정
    config = {
        "configurable": {
            "thread_id": f"ai-trends-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
    }
    
    # 5. 그래프 실행
    logger.info("\n" + "="*70)
    logger.info("▶️  전체 파이프라인 실행 시작")
    logger.info("="*70 + "\n")
    
    try:
        completed_steps = set()
        
        for event in app.stream(initial_state, config, stream_mode="values"):
            # 각 노드별 완료 상태 체크
            if event.get("step_collector") and "collector" not in completed_steps:
                logger.info("\n" + "="*70)
                logger.info("✅ Agent 1: 데이터 수집 완료")
                logger.info("="*70)
                completed_steps.add("collector")
            
            if event.get("step_tech") and "tech" not in completed_steps:
                logger.info("\n" + "="*70)
                logger.info("✅ Agent 2: 기술 분석 완료")
                logger.info("="*70)
                completed_steps.add("tech")
            
            if event.get("step_market") and "market" not in completed_steps:
                logger.info("\n" + "="*70)
                logger.info("✅ Agent 3: 시장 분석 완료")
                logger.info("="*70)
                completed_steps.add("market")
            
            if event.get("step_rag") and "rag" not in completed_steps:
                logger.info("\n" + "="*70)
                logger.info("✅ Agent 4: RAG 분석 완료")
                logger.info("="*70)
                completed_steps.add("rag")
            
            if event.get("step_cross") and "cross" not in completed_steps:
                logger.info("\n" + "="*70)
                logger.info("✅ Agent 5: 교차 분석 완료")
                logger.info("="*70)
                completed_steps.add("cross")
            
            if event.get("step_report") and "report" not in completed_steps:
                logger.info("\n" + "="*70)
                logger.info("✅ Agent 6: 보고서 생성 완료")
                logger.info("="*70)
                completed_steps.add("report")
        
        # 6. 최종 상태 확인
        final_state = app.get_state(config).values
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "="*70)
        logger.info("🎉 전체 분석 완료!")
        logger.info("="*70)
        
        # 실행 시간
        logger.info(f"\n⏱️  실행 시간: {duration:.1f}초 ({duration/60:.1f}분)")
        
        # 최종 보고서 확인
        if final_state.get("final_report"):
            logger.info(f"📄 보고서 길이: {len(final_state['final_report']):,}자")
            
            # 생성된 파일 찾기
            import glob
            md_files = glob.glob("outputs/reports/AI_TRENDS_*.md")
            pdf_files = glob.glob("outputs/reports/AI_TRENDS_*.pdf")
            
            if md_files:
                latest_md = max(md_files, key=os.path.getctime)
                logger.info(f"\n📝 생성된 파일:")
                logger.info(f"   - Markdown: {latest_md}")
                logger.info(f"     크기: {os.path.getsize(latest_md) / 1024:.1f} KB")
                
            if pdf_files:
                latest_pdf = max(pdf_files, key=os.path.getctime)
                logger.info(f"   - PDF: {latest_pdf}")
                logger.info(f"     크기: {os.path.getsize(latest_pdf) / 1024 / 1024:.1f} MB")
        
        # Top 5 트렌드 출력
        if final_state.get("top_5_trends"):
            logger.info(f"\n🏆 Top 5 AI 트렌드:")
            for trend in final_state["top_5_trends"]:
                logger.info(f"   {trend['rank']}. {trend['trend_keyword']} ({trend['final_score']:.1f}점)")
                logger.info(f"      - 기술: {trend['tech']['tech_name']} ({trend['tech']['maturity_score']:.1f})")
                logger.info(f"      - 시장: {trend['market']['demand_name']} ({trend['market']['opportunity_score']:.1f})")
            
            # ✅ 시각화 생성
            logger.info(f"\n📊 시각화 생성 중...")
            try:
                plot_trend_scores(final_state["top_5_trends"])
                plot_score_breakdown(final_state["top_5_trends"])
                logger.info("   ✓ 차트 생성 완료")
            except Exception as e:
                logger.warning(f"   ⚠️ 차트 생성 실패: {e}")
        
        # 수집된 데이터 통계
        logger.info(f"\n📊 수집 데이터 통계:")
        logger.info(f"   - 논문: {len(final_state.get('papers', []))}개")
        logger.info(f"   - GitHub: {len(final_state.get('github_repos', []))}개")
        logger.info(f"   - 기술 트렌드: {len(final_state.get('tech_trends', []))}개")
        logger.info(f"   - 시장 수요: {len(final_state.get('market_demands', []))}개")
        logger.info(f"   - RAG 분석: {'완료' if final_state.get('rag_analysis', {}).get('answer') else '없음'}")
        
        # 에러 로그 확인
        if final_state.get("error_log"):
            logger.info(f"\n⚠️  경고/오류 ({len(final_state['error_log'])}건):")
            for i, error in enumerate(final_state["error_log"][:5], 1):
                logger.info(f"   {i}. {error}")
            
            if len(final_state["error_log"]) > 5:
                logger.info(f"   ... 외 {len(final_state['error_log']) - 5}건")
        
        logger.info("\n" + "="*70)
        logger.info("✅ 프로그램 정상 종료")
        logger.info("="*70 + "\n")
        
        return True
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  사용자에 의해 중단됨")
        logger.info(f"   체크포인트 ID: {config['configurable']['thread_id']}")
        logger.info(f"   재개하려면: python scripts/resume_analysis.py --thread-id {config['configurable']['thread_id']}\n")
        return False
        
    except Exception as e:
        logger.error(f"\n❌ 실행 중 오류 발생: {e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)