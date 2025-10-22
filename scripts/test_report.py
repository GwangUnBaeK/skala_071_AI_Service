# scripts/test_report.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodes.report_node import report_generation_node
from utils.logger import logger

def test_report_generation():
    """보고서 생성 테스트"""
    
    # 테스트용 더미 데이터
    dummy_state = {
        "top_5_trends": [
            {
                "rank": 1,
                "trend_keyword": "AI 직원 시대",
                "final_score": 85.3,
                "tech": {
                    "tech_name": "LLM Agent",
                    "maturity_score": 75.0,
                    "paper_count": 450,
                    "github_stars_total": 250000,
                    "related_projects": ["langchain-ai/langchain", "microsoft/autogen"]
                },
                "market": {
                    "demand_name": "중소기업 업무 자동화",
                    "problem_statement": "중소기업 채용난 및 인건비 상승",
                    "opportunity_score": 92.0,
                    "tam_usd": 500_000_000,
                    "cagr": 0.48,
                    "target_companies": 500_000,
                    "industries": ["manufacturing", "retail"],
                    "regions": ["korea", "southeast_asia"],
                    "tavily_reports": []
                },
                "competition": 50.0,
                "rag_insight": {
                    "answer": "LLM Agent 기술은 2025년 현재 얼리어답터 단계입니다...",
                    "sources": []
                }
            }
        ],
        "rag_analysis": {
            "answer": "전문 문서 분석 결과...",
            "loaded_documents": ["AI_Trends_Report_2024.pdf"],
            "sources": []
        },
        "papers": [
            {
                "title": "Large Language Models are Few-Shot Learners",
                "authors": ["Tom Brown", "et al"],
                "publish_date": "2020-05-28",
                "url": "https://arxiv.org/abs/2005.14165"
            }
        ]
    }
    
    logger.info("🧪 보고서 생성 테스트 시작\n")
    
    try:
        result = report_generation_node(dummy_state)
        
        logger.info("\n✅ 테스트 성공!")
        logger.info(f"보고서 길이: {len(result['final_report']):,}자")
        
        # 생성된 파일 확인
        import glob
        reports = glob.glob("outputs/reports/AI_TRENDS_*.md")
        if reports:
            logger.info(f"생성된 파일: {len(reports)}개")
            
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_report_generation()