# tools/trends_tool.py
from langchain_core.tools import tool
from typing import List, Dict
from pytrends.request import TrendReq
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import logger

@tool
def search_google_trends(keywords: List[str], timeframe: str = '2023-01-01 2025-10-21') -> Dict:
    """
    Google Trends에서 검색량 데이터를 수집합니다.
    
    Args:
        keywords: 검색할 키워드 리스트 (최대 5개)
        timeframe: 검색 기간
    
    Returns:
        키워드별 검색량 데이터
    """
    logger.info(f"📊 Google Trends 검색 시작 (키워드: {len(keywords)}개)")
    
    pytrends = TrendReq(hl='en-US', tz=360)
    trends_data = {}
    
    # Google Trends는 한 번에 최대 5개만 가능
    batch_size = 5
    
    for i in range(0, len(keywords), batch_size):
        batch = keywords[i:i+batch_size]
        
        try:
            logger.info(f"   배치 {i//batch_size + 1} 처리 중: {batch}")
            
            pytrends.build_payload(batch, timeframe=timeframe)
            data = pytrends.interest_over_time()
            
            if not data.empty:
                for keyword in batch:
                    if keyword in data.columns:
                        # 월별 평균으로 변환
                        monthly_data = data[keyword].resample('M').mean().to_dict()
                        trends_data[keyword] = {
                            str(k.date()): int(v) for k, v in monthly_data.items()
                        }
                        
                        avg_score = data[keyword].mean()
                        logger.info(f"   ✓ '{keyword}': 평균 {avg_score:.1f}")
            
            # Rate limit 방지
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"   ✗ 배치 검색 실패: {e}")
            # 실패해도 계속 진행
            for keyword in batch:
                trends_data[keyword] = {}
    
    logger.info(f"✅ Google Trends 수집 완료 ({len(trends_data)}개)")
    return trends_data