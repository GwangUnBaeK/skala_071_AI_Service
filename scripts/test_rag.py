# scripts/test_rag.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.rag_tool import analyze_with_fixed_rag
from utils.logger import logger

def test_fixed_rag():
    """Fixed RAG 테스트"""
    logger.info("="*70)
    logger.info("🧪 Fixed RAG 테스트")
    logger.info("="*70)
    
    # 테스트 질문
    test_query = """
    2025-2030년 AI 트렌드 중 다음을 분석해주세요:
    1. Generative AI의 산업별 적용 사례
    2. 기업이 직면한 주요 도전과제
    3. 투자 전망
    
    구체적인 수치와 사례를 포함해주세요.
    """
    
    try:
        result = analyze_with_fixed_rag.invoke({
            "query": test_query,
            "max_pages_per_doc": 35
        })
        
        if result.get("error", False):
            logger.error(f"\n❌ 테스트 실패: {result['answer']}")
            return
        
        logger.info("\n" + "="*70)
        logger.info("✅ 테스트 성공!")
        logger.info("="*70)
        logger.info(f"\n📄 사용 문서: {', '.join(result['loaded_documents'])}")
        logger.info(f"📊 페이지: {result['num_pages']}개")
        logger.info(f"📦 청크: {result['num_chunks']}개")
        logger.info(f"\n💡 답변:\n{result['answer']}\n")
        
        if result['sources']:
            logger.info("📚 출처:")
            for i, src in enumerate(result['sources'], 1):
                logger.info(f"[{i}] {src['source']} (p.{src['page']})")
        
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_rag()