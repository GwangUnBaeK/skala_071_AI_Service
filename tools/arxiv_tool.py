# tools/arxiv_tool.py
"""
arXiv 논문 검색 도구
"""
from langchain_core.tools import tool
from typing import List, Dict
import arxiv
from datetime import datetime
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from utils.logger import logger

@tool
def search_arxiv_papers(keywords: List[str], max_results: int = 100) -> List[Dict]:
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
    
    # ✅ 날짜를 date 객체로 변환
    start_date = datetime.strptime(settings.ANALYSIS["date_range"]["start"], "%Y-%m-%d").date()
    end_date = datetime.strptime(settings.ANALYSIS["date_range"]["end"], "%Y-%m-%d").date()
    
    for idx, keyword in enumerate(keywords, 1):
        try:
            logger.info(f"   [{idx}/{len(keywords)}] 검색 중: '{keyword}'")
            
            # ✅ 검색 설정
            search = arxiv.Search(
                query=keyword,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            count = 0
            keyword_papers = []
            
            # ✅ 결과 순회 (에러 핸들링 추가)
            try:
                for result in search.results():
                    try:
                        pub_date = result.published.date()
                        
                        # 날짜 필터링
                        if pub_date < start_date or pub_date > end_date:
                            continue
                        
                        # 논문 정보 저장
                        keyword_papers.append({
                            "id": result.entry_id.split('/')[-1],  # arXiv ID만 추출
                            "title": result.title.strip(),
                            "authors": [a.name for a in result.authors][:5],
                            "abstract": result.summary.strip()[:500],
                            "publish_date": pub_date.isoformat(),
                            "keywords": [keyword],
                            "url": result.entry_id,
                            "categories": result.categories if hasattr(result, 'categories') else []
                        })
                        count += 1
                        
                        # ✅ 최대 개수 도달 시 중단
                        if count >= max_results:
                            break
                            
                    except Exception as e:
                        # 개별 논문 처리 실패는 건너뛰기
                        continue
                
            except StopIteration:
                # 더 이상 결과 없음
                pass
            except arxiv.UnexpectedEmptyPageError:
                # 빈 페이지 에러 (무시)
                logger.warning(f"      ⚠️ 더 이상 결과 없음")
            except Exception as e:
                logger.warning(f"      ⚠️ 검색 중 예외: {e}")
            
            # 수집된 논문 추가
            papers.extend(keyword_papers)
            logger.info(f"      ✓ {count}개 수집")
            
            # ✅ Rate limit 방지 (키워드 간 대기)
            if idx < len(keywords):
                time.sleep(3)  # 3초 대기
            
        except Exception as e:
            logger.error(f"      ✗ '{keyword}' 검색 실패: {e}")
            continue
    
    # ✅ 중복 제거 (같은 논문이 여러 키워드에서 나올 수 있음)
    unique_papers = {}
    for paper in papers:
        paper_id = paper["id"]
        if paper_id not in unique_papers:
            unique_papers[paper_id] = paper
        else:
            # 키워드 병합
            existing_keywords = unique_papers[paper_id]["keywords"]
            new_keywords = paper["keywords"]
            unique_papers[paper_id]["keywords"] = list(set(existing_keywords + new_keywords))
    
    final_papers = list(unique_papers.values())
    
    logger.info(f"✅ arXiv 총 {len(final_papers)}개 논문 수집 완료 (중복 제거 후)\n")
    
    return final_papers