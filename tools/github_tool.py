# tools/github_tool.py
from langchain_core.tools import tool
from typing import List, Dict, Optional
from github import Github
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from utils.logger import logger

@tool
def search_github_repos(keywords: List[str], min_stars: int = 100) -> List[Dict]:
    """
    GitHub에서 인기 AI 저장소를 검색합니다.
    
    Args:
        keywords: 검색할 키워드 리스트
        min_stars: 최소 star 수
    
    Returns:
        저장소 정보 리스트
    """
    logger.info(f"🐙 GitHub 저장소 검색 시작 (키워드: {len(keywords)}개)")
    
    # GitHub 인증
    token = settings.GITHUB_TOKEN
    g = Github(token) if token else Github()
    
    repos = []
    seen_names = set()  # 중복 제거용
    
    for keyword in keywords:
        try:
            logger.info(f"   검색 중: '{keyword}'")
            
            # 검색 쿼리
            query = f"{keyword} language:python stars:>{min_stars}"
            results = g.search_repositories(query=query, sort="stars")
            
            count = 0
            for repo in results[:50]:  # 키워드당 최대 50개
                if repo.full_name not in seen_names:
                    repos.append({
                        "name": repo.full_name,
                        "description": repo.description or "",
                        "stars": repo.stargazers_count,
                        "forks": repo.forks_count,
                        "language": repo.language or "Unknown",
                        "url": repo.html_url,
                        "keywords": [keyword]
                    })
                    seen_names.add(repo.full_name)
                    count += 1
            
            logger.info(f"   ✓ '{keyword}': {count}개 수집")
            
        except Exception as e:
            logger.error(f"   ✗ '{keyword}' 검색 실패: {e}")
            continue
    
    logger.info(f"✅ GitHub 총 {len(repos)}개 저장소 수집 완료")
    return repos