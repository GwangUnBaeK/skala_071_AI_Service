# tools/rag_tool.py

from langchain_core.tools import tool
from langchain_community.document_loaders import PyMuPDFLoader  # ✅ 빠르고 정확한 PDF 로더
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings          # ✅ 최신 경로
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate                # ✅ 최신 import
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from typing import Dict
import os
import sys
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings
from utils.logger import logger


# ============================================
# 📂 고정 문서 경로
# ============================================
FIXED_DOCUMENTS = [
    "data/rag_documents/20250128_GPAI_GenAI_FoW_report_final_VOECD.pdf",
    "data/rag_documents/wpiea2025076-print-pdf.pdf"
]


# ============================================
# 🌐 한글 질의 → 영어 변환
# ============================================
def translate_query_to_english(query: str) -> str:
    """한글 질의를 영어로 번역 (OpenAI LLM 사용)"""
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
# 🤖 RAG 분석 도구 (LangChain 1.x 호환)
# ============================================
@tool
def analyze_with_fixed_rag(query: str, max_pages_per_doc: int = 35) -> Dict:
    """
    고정된 PDF 문서 2개를 사용하여 RAG 분석을 수행합니다.
    (한글 질의 지원 + 영어 임베딩 + 한국어 출력)
    """
    logger.info("📚 Fixed RAG 분석 시작")
    logger.info(f"   Query: {query[:100]}...")

    all_documents = []
    loaded_docs = []

    # 1️⃣ 문서 로드
    for doc_path in FIXED_DOCUMENTS:
        if not os.path.exists(doc_path):
            logger.warning(f"   ⚠️ 문서 없음: {doc_path}")
            continue
        try:
            logger.info(f"   📄 로딩: {os.path.basename(doc_path)}")

            loader = PyMuPDFLoader(doc_path)
            pages = loader.load()

            if len(pages) > max_pages_per_doc:
                logger.info(f"      → {len(pages)}페이지 중 {max_pages_per_doc}페이지만 사용")
                pages = pages[:max_pages_per_doc]
            else:
                logger.info(f"      → {len(pages)}페이지 로드 완료")

            all_documents.extend(pages)
            loaded_docs.append(os.path.basename(doc_path))

        except Exception as e:
            logger.error(f"   ✗ {doc_path} 로드 실패: {e}")
            continue

    # 문서 없을 경우 종료
    if not all_documents:
        logger.error("   ❌ 로드된 문서 없음")
        return {
            "answer": "RAG 문서를 로드할 수 없습니다. data/rag_documents/ 폴더에 PDF 파일을 넣어주세요.",
            "sources": [],
            "loaded_documents": [],
            "error": True,
        }

    # 2️⃣ 텍스트 분할
    logger.info(f"   📝 {len(all_documents)}개 페이지 처리 중...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    splits = text_splitter.split_documents(all_documents)
    logger.info(f"      → {len(splits)}개 청크 생성")

    # 3️⃣ 임베딩 (Hugging Face 무료 모델)
    logger.info("   🔢 벡터 임베딩 중 (Hugging Face 모델 사용)...")
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"  # ✅ 영어 문서용
        )

        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings
        )

        logger.info("      → 임베딩 완료")

    except Exception as e:
        logger.error(f"   ❌ 임베딩 실패: {e}")
        return {
            "answer": f"벡터 임베딩 실패: {str(e)}",
            "sources": [],
            "loaded_documents": loaded_docs,
            "error": True,
        }

    # 4️⃣ 한글 질의 → 영어 변환
    if not query.isascii():
        logger.info("🌐 한글 질의를 영어로 변환 중...")
        query_en = translate_query_to_english(query)
        logger.info(f"   번역 완료 → {query_en[:120]}...")
    else:
        query_en = query

    # 5️⃣ LLM 초기화
    logger.info("   🤖 LLM 분석 실행 중 (OpenAI LLM 사용)...")
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # 6️⃣ 한국어 답변용 프롬프트
        prompt = PromptTemplate(
            template=(
                "다음 컨텍스트만 사용하여 질문에 한국어로 간결하고 분석적으로 답하세요.\n\n"
                "질문:\n{question}\n\n"
                "컨텍스트:\n{context}\n"
            ),
            input_variables=["question", "context"]
        )

        # 7️⃣ Retriever 준비
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        # 8️⃣ 문서 포맷터
        def format_docs(docs):
            return "\n\n".join(d.page_content for d in docs)

        # 9️⃣ LCEL 기반 RAG 파이프라인
        rag_chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough(),  # query_en 그대로 전달
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        # 10️⃣ 영어 질의 실행
        answer_ko = rag_chain.invoke(query_en)

        # 11️⃣ 출처 정리
        top_docs = retriever.invoke(query_en)[:3]
        sources = []
        for doc in top_docs:
            sources.append({
                "content": doc.page_content[:300],
                "page": doc.metadata.get("page", 0) + 1,
                "source": os.path.basename(doc.metadata.get("source", "unknown")),
            })

        logger.info("   ✅ RAG 분석 완료")
        logger.info(f"      답변 길이: {len(answer_ko)}자")

        return {
            "answer": answer_ko,
            "sources": sources,
            "loaded_documents": loaded_docs,
            "num_pages": len(all_documents),
            "num_chunks": len(splits),
            "error": False,
        }

    except Exception as e:
        logger.error(f"   ❌ RAG 실행 실패: {e}")
        return {
            "answer": f"RAG 분석 실패: {str(e)}",
            "sources": [],
            "loaded_documents": loaded_docs,
            "error": True,
        }
