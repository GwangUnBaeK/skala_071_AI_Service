# scripts/build_vectorstore.py
"""
RAG 벡터 저장소 사전 생성
최초 1회만 실행하면 됩니다.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from utils.logger import logger
import shutil

# 문서 경로
FIXED_DOCUMENTS = [
    "data/rag_documents/20250128_GPAI_GenAI_FoW_report_final_VOECD.pdf",
    "data/rag_documents/wpiea2025076-print-pdf.pdf"
]

# 벡터 저장소 경로
VECTORSTORE_DIR = "data/vectorstore"

def build_vectorstore(max_pages_per_doc: int = 35):
    """벡터 저장소 생성"""
    
    logger.info("="*70)
    logger.info("🏗️  벡터 저장소 생성 시작")
    logger.info("="*70)
    
    # 기존 벡터 저장소 삭제 (재생성)
    if os.path.exists(VECTORSTORE_DIR):
        logger.info(f"\n🗑️  기존 벡터 저장소 삭제 중...")
        shutil.rmtree(VECTORSTORE_DIR)
        logger.info("   ✓ 삭제 완료")
    
    # 1. 문서 로드
    logger.info(f"\n1️⃣ 문서 로드 중...")
    all_documents = []
    loaded_docs = []
    
    for doc_path in FIXED_DOCUMENTS:
        if not os.path.exists(doc_path):
            logger.warning(f"   ⚠️ 문서 없음: {doc_path}")
            continue
        
        try:
            logger.info(f"   📄 {os.path.basename(doc_path)}")
            
            loader = PyMuPDFLoader(doc_path)
            pages = loader.load()
            
            if len(pages) > max_pages_per_doc:
                logger.info(f"      → {len(pages)}페이지 중 {max_pages_per_doc}페이지만 사용")
                pages = pages[:max_pages_per_doc]
            else:
                logger.info(f"      → {len(pages)}페이지 로드")
            
            all_documents.extend(pages)
            loaded_docs.append(os.path.basename(doc_path))
            
        except Exception as e:
            logger.error(f"   ✗ 로드 실패: {e}")
            continue
    
    if not all_documents:
        logger.error("\n❌ 로드된 문서 없음!")
        return False
    
    logger.info(f"\n   ✅ 총 {len(all_documents)}개 페이지 로드")
    logger.info(f"   📚 문서: {', '.join(loaded_docs)}")
    
    # 2. 텍스트 분할
    logger.info(f"\n2️⃣ 텍스트 분할 중...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    splits = text_splitter.split_documents(all_documents)
    
    logger.info(f"   ✅ {len(splits)}개 청크 생성")
    
    # 3. 임베딩 및 벡터 저장소 생성
    logger.info(f"\n3️⃣ 벡터 임베딩 및 저장소 생성 중...")
    logger.info(f"   (예상 시간: 1-3분)")
    
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # persist_directory로 저장
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=VECTORSTORE_DIR  # ✅ 디스크에 저장
        )
        
        logger.info(f"   ✅ 벡터 저장소 생성 완료")
        logger.info(f"   📂 저장 위치: {VECTORSTORE_DIR}")
        
        # 크기 확인
        dir_size = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, _, filenames in os.walk(VECTORSTORE_DIR)
            for filename in filenames
        ) / 1024 / 1024
        
        logger.info(f"   💾 저장소 크기: {dir_size:.1f} MB")
        
        logger.info("\n" + "="*70)
        logger.info("✅ 벡터 저장소 생성 완료!")
        logger.info("="*70)
        logger.info(f"\n이제 RAG 분석을 빠르게 실행할 수 있습니다.")
        logger.info(f"재생성이 필요하면 이 스크립트를 다시 실행하세요.\n")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ 벡터 저장소 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = build_vectorstore()
    sys.exit(0 if success else 1)