# nodes/rag_node.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.graph_state import GraphState
from tools.rag_tool import analyze_with_fixed_rag
from utils.logger import logger

def rag_analysis_node(state: GraphState) -> GraphState:
    """
    Agent: RAG 문서 분석 노드
    고정된 2개 PDF 문서를 기반으로 트렌드 인사이트 추출
    """
    logger.info("="*70)
    logger.info("📚 Agent: RAG 문서 분석 시작")
    logger.info("="*70)
    
    # 1. 쿼리 생성
    # 이미 수집된 tech_trends와 market_demands 기반으로 심층 질문 생성
    tech_trends = state.get("tech_trends", [])
    market_demands = state.get("market_demands", [])
    
    # 상위 5개 기술 키워드
    top_techs = [t["tech_name"] for t in tech_trends[:5]]
    
    # RAG 질문 생성
    query = f"""
다음 AI 기술들에 대해 2025-2030년 트렌드를 분석해주세요:
{', '.join(top_techs)}

다음 관점에서 분석해주세요:
1. 각 기술의 산업별 적용 사례와 성공 요인
2. 기업들이 직면한 주요 도전과제
3. 향후 5년 내 예상되는 주요 변화
4. 투자 및 시장 전망

구체적인 사례와 수치를 포함하여 답변해주세요.
"""
    
    logger.info(f"\n생성된 질문:\n{query}\n")
    
    # 2. RAG 분석 실행
    try:
        rag_result = analyze_with_fixed_rag.invoke({
            "query": query,
            "max_pages_per_doc": 35
        })
        
        # 3. 결과 검증
        if rag_result.get("error", False):
            logger.warning("⚠️ RAG 분석 중 오류 발생")
            logger.warning(f"   {rag_result.get('answer', '')}")
            
            # 오류 메시지 기록
            error_msg = f"RAG 분석 실패: {rag_result.get('answer', 'Unknown error')}"
            error_log = state.get("error_log", [])
            error_log.append(error_msg)
            
            return {
                "rag_analysis": rag_result,
                "error_log": error_log,
                "messages": [{
                    "role": "assistant",
                    "content": f"RAG 분석 중 오류 발생 (문서 확인 필요)"
                }],
                "current_step": "rag_failed"
            }
        
        # 4. 성공 시 결과 로깅
        logger.info("\n" + "="*70)
        logger.info("✅ RAG 분석 완료")
        logger.info("="*70)
        logger.info(f"\n📄 사용된 문서: {', '.join(rag_result['loaded_documents'])}")
        logger.info(f"📊 처리된 페이지: {rag_result['num_pages']}개")
        logger.info(f"📦 생성된 청크: {rag_result['num_chunks']}개")
        logger.info(f"\n💡 RAG 분석 결과 (처음 500자):\n")
        logger.info(rag_result['answer'][:500] + "...\n")
        
        if rag_result['sources']:
            logger.info("📚 주요 출처:")
            for i, source in enumerate(rag_result['sources'], 1):
                logger.info(f"   [{i}] {source['source']} (p.{source['page']})")
                logger.info(f"       {source['content'][:100]}...\n")
        
        return {
            "rag_analysis": rag_result,
            "messages": [{
                "role": "assistant",
                "content": f"RAG 분석 완료: {len(rag_result['answer'])}자 인사이트 생성"
            }],
            "step_rag": "completed"
        }
        
    except Exception as e:
        logger.error(f"❌ RAG 노드 실행 실패: {e}")
        
        error_log = state.get("error_log", [])
        error_log.append(f"RAG 노드 오류: {str(e)}")
        
        return {
            "rag_analysis": {
                "answer": f"RAG 분석 실패: {str(e)}",
                "sources": [],
                "error": True
            },
            "error_log": error_log,
            "current_step": "rag_failed"
        }