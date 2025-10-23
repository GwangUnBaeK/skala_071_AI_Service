# tools/arxiv_tool.py
from langchain_core.tools import tool
from typing import List, Dict
import arxiv
from datetime import datetime, date
import sys
import os
import time  # ✅ 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from utils.logger import logger

@tool
def search_arxiv_papers(keywords: List[str], max_results: int = 200) -> List[Dict]:
    """
    arXiv에서 AI 관련 논문을 검색합니다.
    
    Args:
        keywords: 검색할 키워드 리스트
        max_results: 키워드당 최대 결과 수
    
    Returns:
        논문 정보 리스트
    """
    logger.info(f"📄 arXiv 논문 검색 시작 (키워드: {len(keywords)}개)")
    
    papers = []
    start_date = settings.ANALYSIS["date_range"]["start"]
    end_date = settings.ANALYSIS["date_range"]["end"]
    
    for idx, keyword in enumerate(keywords, 1):
        try:
            logger.info(f"   [{idx}/{len(keywords)}] 검색 중: '{keyword}'")
            
            # ✅ 한 번에 가져오기 (페이지네이션 제거)
            search = arxiv.Search(
                query=keyword,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            count = 0
            for result in search.results():
                pub_date = result.published.date()
                
                # 날짜 필터링
                if start_date <= pub_date <= end_date:
                    papers.append({
                        "id": result.entry_id,
                        "title": result.title,
                        "authors": [a.name for a in result.authors][:5],
                        "abstract": result.summary[:500],
                        "publish_date": pub_date.isoformat(),
                        "keywords": [keyword],
                        "url": result.entry_id
                    })
                    count += 1
            
            logger.info(f"      ✓ {count}개 수집")
            
            # ✅ Rate limit 방지 (키워드 간 대기)
            if idx < len(keywords):
                time.sleep(3)  # 3초 대기
            
        except Exception as e:
            logger.error(f"      ✗ '{keyword}' 검색 실패: {e}")
            continue
    
    logger.info(f"✅ arXiv 총 {len(papers)}개 논문 수집 완료\n")
    return papers