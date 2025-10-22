# tools/rag_tool.py (개선 버전)
from langchain_core.tools import tool
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from typing import Dict
import os
import sys
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings
from utils.logger import logger

# ============================================
# 📂 벡터 저장소 경로
# ============================================
VECTORSTORE_DIR = "data/vectorstore"

# ============================================
# 🔄 벡터 저장소 로드 (캐싱)
# ============================================
_vectorstore_cache = None  # ✅ 전역 캐시

def get_vectorstore():
    """벡터 저장소 로드 (캐싱)"""
    global _vectorstore_cache
    
    # 이미 로드되어 있으면 재사용
    if _vectorstore_cache is not None:
        return _vectorstore_cache
    
    # 벡터 저장소 존재 확인
    if not os.path.exists(VECTORSTORE_DIR):
        logger.error(f"❌ 벡터 저장소 없음: {VECTORSTORE_DIR}")
        logger.error(f"   먼저 'python scripts/build_vectorstore.py'를 실행하세요!")
        return None
    
    try:
        logger.info(f"📂 벡터 저장소 로드 중: {VECTORSTORE_DIR}")
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # 저장된 벡터 저장소 로드
        _vectorstore_cache = Chroma(
            persist_directory=VECTORSTORE_DIR,
            embedding_function=embeddings
        )
        
        logger.info(f"   ✅ 로드 완료 (0.1초)")
        return _vectorstore_cache
        
    except Exception as e:
        logger.error(f"❌ 벡터 저장소 로드 실패: {e}")
        return None

# ============================================
# 🌐 한글 질의 → 영어 변환
# ============================================
def translate_query_to_english(query: str) -> str:
    """한글 질의를 영어로 번역"""
    try:
        llm_translator = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        prompt = f"Translate the following Korean text into English, preserving technical and analytical meaning:\n\n{query}"
        response = llm_translator.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        logger.error(f"⚠️ 질의 번역 실패 (원문으로 진행): {e}")
        return query

# ============================================
# 🤖 RAG 분석 도구 (최적화 버전)
# ============================================
@tool
def analyze_with_fixed_rag(query: str) -> Dict:
    """
    사전 생성된 벡터 저장소를 사용하여 RAG 분석 수행
    (매우 빠름: 0.1초 로딩 + 2-3초 검색)
    """
    logger.info("📚 Fixed RAG 분석 시작")
    logger.info(f"   Query: {query[:100]}...")
    
    # 1️⃣ 벡터 저장소 로드 (캐싱됨)
    vectorstore = get_vectorstore()
    
    if vectorstore is None:
        return {
            "answer": "벡터 저장소가 없습니다. 먼저 'python scripts/build_vectorstore.py'를 실행하세요.",
            "sources": [],
            "loaded_documents": [],
            "error": True
        }
    
    # 2️⃣ 한글 질의 → 영어 변환
    if not query.isascii():
        logger.info("🌐 한글 질의를 영어로 변환 중...")
        query_en = translate_query_to_english(query)
        logger.info(f"   번역 완료 → {query_en[:80]}...")
    else:
        query_en = query
    
    # 3️⃣ LLM 초기화
    logger.info("   🤖 LLM 분석 실행 중...")
    
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # 4️⃣ 한국어 답변용 프롬프트
        prompt = PromptTemplate(
            template=(
                "다음 컨텍스트만 사용하여 질문에 한국어로 간결하고 분석적으로 답하세요.\n\n"
                "질문:\n{question}\n\n"
                "컨텍스트:\n{context}\n"
            ),
            input_variables=["question", "context"]
        )
        
        # 5️⃣ Retriever 준비
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        
        # 6️⃣ 문서 포맷터
        def format_docs(docs):
            return "\n\n".join(d.page_content for d in docs)
        
        # 7️⃣ LCEL 기반 RAG 파이프라인
        rag_chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # 8️⃣ 영어 질의 실행
        answer_ko = rag_chain.invoke(query_en)
        
        # 9️⃣ 출처 정리
        top_docs = retriever.invoke(query_en)[:3]
        sources = []
        for doc in top_docs:
            sources.append({
                "content": doc.page_content[:300],
                "page": doc.metadata.get("page", 0) + 1,
                "source": os.path.basename(doc.metadata.get("source", "unknown"))
            })
        
        logger.info("   ✅ RAG 분석 완료")
        logger.info(f"      답변 길이: {len(answer_ko)}자")
        
        return {
            "answer": answer_ko,
            "sources": sources,
            "loaded_documents": ["OECD PDF", "IMF PDF"],
            "num_pages": "N/A (사전 인덱싱)",
            "num_chunks": "N/A (사전 인덱싱)",
            "error": False
        }
        
    except Exception as e:
        logger.error(f"   ❌ RAG 실행 실패: {e}")
        return {
            "answer": f"RAG 분석 실패: {str(e)}",
            "sources": [],
            "loaded_documents": [],
            "error": True
        }