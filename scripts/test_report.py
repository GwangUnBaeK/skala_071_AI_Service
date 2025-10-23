# scripts/test_report.py
"""
리포트 생성 노드만 테스트 (PDF만 생성)
"""
import sys
import os
import warnings

# ✅ 모든 경고 숨기기
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

# ✅ GLib 경고 완전히 숨기기 (Windows)
if os.name == 'nt':
    import io
    sys.stderr = io.StringIO()  # stderr를 메모리로 리다이렉트

# 프로젝트 루트를 Python Path에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from nodes.report_node import report_generation_node
from config.settings import settings
from utils.logger import logger
from datetime import datetime

def create_mock_state():
    """테스트용 Mock State 생성"""
    
    top_5_trends = [
        {
            "rank": 1,
            "trend_keyword": "large language model × 의료 진단 보조",
            "final_score": 55.3,
            "tech": {
                "tech_name": "large language model",
                "maturity_score": 100.0,
                "paper_count": 100,
                "github_stars_total": 342435,
                "related_projects": ["NVIDIA-NeMo", "IBM/ibm-generative-ai", "lm-sys/FastChat"]
            },
            "market": {
                "demand_name": "의료 진단 보조",
                "problem_statement": "의료 영상 판독 및 진단의 정확성을 높이는 것",
                "opportunity_score": 88.0,
                "tam_usd": 700000000,
                "cagr": 0.52,
                "target_companies": 100000,
                "industries": ["healthcare"],
                "regions": ["글로벌"]
            },
            "competition": 90.0,
            "rag_insight": {
                "answer": "OECD 보고서에 따르면 AI 기반 의료 진단 시스템은 2030년까지 글로벌 헬스케어 시장의 핵심 기술로 자리잡을 것으로 예상됩니다."
            }
        },
        {
            "rank": 2,
            "trend_keyword": "large language model × 콘텐츠 크리에이터 지원",
            "final_score": 51.8,
            "tech": {
                "tech_name": "large language model",
                "maturity_score": 100.0,
                "paper_count": 100,
                "github_stars_total": 342435,
                "related_projects": ["OpenAI/gpt-4", "anthropic/claude"]
            },
            "market": {
                "demand_name": "콘텐츠 크리에이터 지원",
                "problem_statement": "콘텐츠 제작 비용과 시간 부담",
                "opportunity_score": 76.0,
                "tam_usd": 400000000,
                "cagr": 0.55,
                "target_companies": 2000000,
                "industries": ["media", "entertainment", "marketing"],
                "regions": ["글로벌"]
            },
            "competition": 90.0,
            "rag_insight": {
                "answer": "크리에이터 이코노미는 2030년까지 연평균 55% 성장할 것으로 전망됩니다."
            }
        },
        {
            "rank": 3,
            "trend_keyword": "generative AI × 의료 진단 보조",
            "final_score": 51.2,
            "tech": {
                "tech_name": "generative AI",
                "maturity_score": 80.7,
                "paper_count": 80,
                "github_stars_total": 61314,
                "related_projects": ["NVIDIA-NeMo", "andrewyng/aisuite"]
            },
            "market": {
                "demand_name": "의료 진단 보조",
                "problem_statement": "의료 영상 판독 및 진단의 정확성 향상",
                "opportunity_score": 88.0,
                "tam_usd": 700000000,
                "cagr": 0.52,
                "target_companies": 100000,
                "industries": ["healthcare"],
                "regions": ["글로벌"]
            },
            "competition": 85.0,
            "rag_insight": {
                "answer": "생성형 AI는 의료 영상 분석에서 90% 이상의 정확도를 달성하고 있습니다."
            }
        },
        {
            "rank": 4,
            "trend_keyword": "large language model × 중소기업 업무 자동화",
            "final_score": 51.1,
            "tech": {
                "tech_name": "large language model",
                "maturity_score": 100.0,
                "paper_count": 100,
                "github_stars_total": 342435,
                "related_projects": ["OpenAI/chatgpt", "Microsoft/copilot"]
            },
            "market": {
                "demand_name": "중소기업 업무 자동화",
                "problem_statement": "인건비 상승 및 채용난 심화",
                "opportunity_score": 78.8,
                "tam_usd": 500000000,
                "cagr": 0.48,
                "target_companies": 500000,
                "industries": ["제조", "소매", "서비스"],
                "regions": ["한국", "동남아시아"]
            },
            "competition": 90.0,
            "rag_insight": {
                "answer": "중소기업의 AI 도입률은 2025년 20%에서 2030년 60%로 증가할 전망입니다."
            }
        },
        {
            "rank": 5,
            "trend_keyword": "edge AI × 의료 진단 보조",
            "final_score": 50.8,
            "tech": {
                "tech_name": "edge AI",
                "maturity_score": 52.1,
                "paper_count": 100,
                "github_stars_total": 4227,
                "related_projects": ["sipeed/MaixPy-v1", "kaixxx/noScribe"]
            },
            "market": {
                "demand_name": "의료 진단 보조",
                "problem_statement": "실시간 데이터 처리 및 개인정보 보호",
                "opportunity_score": 88.0,
                "tam_usd": 700000000,
                "cagr": 0.52,
                "target_companies": 100000,
                "industries": ["healthcare"],
                "regions": ["글로벌"]
            },
            "competition": 40.0,
            "rag_insight": {
                "answer": "Edge AI는 의료 기기에서 실시간 진단을 가능하게 하여 응급 상황 대응 시간을 50% 단축합니다."
            }
        }
    ]
    
    papers = [
        {
            "id": "2510.18876",
            "title": "Grasp Any Region: Towards Precise, Contextual Pixel Understanding for Multimodal LLMs",
            "authors": ["Haochen Wang"],
            "abstract": "Recent advances...",
            "publish_date": "2025-10-21",
            "keywords": ["multimodal AI"],
            "url": "http://arxiv.org/abs/2510.18876v1"
        }
    ]
    
    github_repos = [
        {
            "full_name": "IBM/ibm-generative-ai",
            "html_url": "https://github.com/IBM/ibm-generative-ai",
            "stars": 21000,
            "description": "IBM Generative AI SDK"
        }
    ]
    
    keywords = ["generative AI", "large language model", "LLM agent", "multimodal AI", "edge AI", "AI automation"]
    
    return {
        "user_query": "2025-2030 AI 트렌드 분석",
        "keywords": keywords,
        "messages": [],
        "papers": papers,
        "github_repos": github_repos,
        "google_trends": {},
        "tech_trends": [],
        "market_demands": [],
        "rag_analysis": {},
        "trend_matrix": [],
        "top_5_trends": top_5_trends,
        "final_report": "",
        "error_log": [],
        "step_collector": "completed",
        "step_tech": "completed",
        "step_market": "completed",
        "step_rag": "completed",
        "step_cross": "completed",
        "step_report": None
    }


def main():
    """리포트 생성 테스트"""
    # ✅ stderr 복원 (logger 출력을 위해)
    sys.stderr = sys.__stderr__
    
    logger.info("="*70)
    logger.info("🧪 리포트 생성 테스트 (PDF만)")
    logger.info("="*70)
    
    logger.info("\n1️⃣ Mock State 생성 중...")
    mock_state = create_mock_state()
    logger.info(f"   ✓ Top 5 트렌드: {len(mock_state['top_5_trends'])}개")
    
    logger.info("\n2️⃣ PDF 생성 실행...")
    start_time = datetime.now()
    
    try:
        result = report_generation_node(mock_state)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "="*70)
        logger.info("✅ 완료!")
        logger.info("="*70)
        logger.info(f"\n⏱️  실행 시간: {duration:.1f}초 ({duration/60:.1f}분)")
        
        # PDF 파일 확인
        import glob
        pdf_files = glob.glob("outputs/reports/AI_TRENDS_*.pdf")
        
        if pdf_files:
            latest_pdf = max(pdf_files, key=os.path.getctime)
            logger.info(f"\n📄 생성된 PDF:")
            logger.info(f"   {latest_pdf}")
            logger.info(f"   크기: {os.path.getsize(latest_pdf) / 1024 / 1024:.1f} MB\n")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)