# utils/search.py
# Semantic Scholar API를 활용한 논문 검색

import requests
import time
from typing import List, Dict, Optional
from datetime import datetime

# Semantic Scholar API 설정
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
RATE_LIMIT_DELAY = 1.0  # API 호출 간 딜레이 (초)

def search_papers(
    query: str,
    year_start: int = 2015,
    year_end: int = None,
    min_citations: int = 0,
    limit: int = 100,
    fields: List[str] = None
) -> List[Dict]:
    """
    Semantic Scholar API로 논문 검색
    
    Args:
        query: 검색 쿼리
        year_start: 시작 연도
        year_end: 종료 연도 (None이면 현재 연도)
        min_citations: 최소 인용수
        limit: 최대 결과 수
        fields: 반환할 필드 목록
        
    Returns:
        논문 정보 딕셔너리 리스트
    """
    if year_end is None:
        year_end = datetime.now().year
    
    if fields is None:
        fields = [
            "paperId", "title", "abstract", "year", "citationCount",
            "authors", "venue", "url", "openAccessPdf", "publicationTypes"
        ]
    
    url = f"{SEMANTIC_SCHOLAR_API}/paper/search"
    params = {
        "query": query,
        "year": f"{year_start}-{year_end}",
        "limit": min(limit, 100),  # API 최대 100개
        "fields": ",".join(fields)
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        papers = data.get("data", [])
        
        # 인용수 필터링
        if min_citations > 0:
            papers = [p for p in papers if (p.get("citationCount") or 0) >= min_citations]
        
        return papers
        
    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류: {e}")
        return []

def check_relevance(
    paper: Dict,
    keywords: List[str],
    target_journals: List[str],
    context_keywords: List[str] = None
) -> Optional[Dict]:
    """
    논문 관련성 검사 (Track A/B 로직)
    
    Args:
        paper: 논문 정보 딕셔너리
        keywords: 검색 키워드 리스트
        target_journals: 타겟 저널 리스트
        context_keywords: 맥락 키워드 리스트 (Track B용)
        
    Returns:
        관련성 정보 딕셔너리 또는 None
    """
    if context_keywords is None:
        context_keywords = [
            "tourism", "travel", "hospitality", "hotel", "tourist",
            "visitor", "destination", "leisure"
        ]
    
    venue = (paper.get("venue") or "").lower()
    title = (paper.get("title") or "").lower()
    abstract = (paper.get("abstract") or "").lower()
    text = f"{title} {abstract}"
    
    # 저널명 매칭 (부분 매칭)
    is_target = any(
        target.lower() in venue or venue in target.lower()
        for target in target_journals
    )
    
    keywords_lower = [k.lower() for k in keywords]
    has_keyword = any(k in text for k in keywords_lower)
    
    # Track A: 타겟 저널 (느슨한 매칭)
    if is_target and has_keyword:
        return {
            "priority": "High",
            "track": "Core Journal",
            "reason": "타겟 저널 + 키워드 매칭"
        }
    
    # Track B: 확장 저널 (엄격한 매칭)
    has_context = any(c in text for c in context_keywords)
    
    if has_context and has_keyword:
        return {
            "priority": "Medium",
            "track": "Discovery",
            "reason": "맥락 + 기술 키워드 동시 매칭"
        }
    
    return None

def format_authors(authors: List[Dict]) -> str:
    """저자 목록 포맷팅"""
    if not authors:
        return "Unknown"
    
    names = [a.get("name", "Unknown") for a in authors[:3]]
    result = ", ".join(names)
    
    if len(authors) > 3:
        result += f" et al. ({len(authors)} authors)"
    
    return result

def format_paper_for_display(paper: Dict, relevance: Dict = None) -> Dict:
    """논문 정보를 표시용으로 포맷팅"""
    return {
        "id": paper.get("paperId", ""),
        "title": paper.get("title", "No Title"),
        "authors": format_authors(paper.get("authors", [])),
        "year": paper.get("year", "N/A"),
        "venue": paper.get("venue", "Unknown"),
        "citations": paper.get("citationCount", 0),
        "abstract": paper.get("abstract", "No abstract available"),
        "url": paper.get("url", ""),
        "pdf_url": (paper.get("openAccessPdf") or {}).get("url", ""),
        "priority": relevance.get("priority", "Unknown") if relevance else "Unknown",
        "track": relevance.get("track", "Unknown") if relevance else "Unknown"
    }

def search_and_filter(
    keywords: List[str],
    target_journals: List[str],
    extended_journals: List[str] = None,
    year_start: int = 2015,
    year_end: int = None,
    min_citations: int = 0,
    include_extended: bool = False,
    limit: int = 100
) -> List[Dict]:
    """
    키워드로 검색하고 저널 필터링 적용
    
    Args:
        keywords: 검색 키워드
        target_journals: 타겟 저널 리스트
        extended_journals: 확장 저널 리스트
        year_start: 시작 연도
        year_end: 종료 연도
        min_citations: 최소 인용수
        include_extended: 확장 저널 포함 여부
        limit: 최대 결과 수
        
    Returns:
        필터링된 논문 리스트
    """
    # 검색 쿼리 생성
    query = " OR ".join(keywords)
    
    # API 검색
    papers = search_papers(
        query=query,
        year_start=year_start,
        year_end=year_end,
        min_citations=min_citations,
        limit=limit
    )
    
    # 저널 필터링 및 관련성 검사
    all_target = target_journals.copy()
    if include_extended and extended_journals:
        all_target.extend(extended_journals)
    
    results = []
    for paper in papers:
        relevance = check_relevance(paper, keywords, all_target)
        if relevance:
            formatted = format_paper_for_display(paper, relevance)
            results.append(formatted)
    
    # 우선순위 정렬: High > Medium, 그 다음 인용수
    priority_order = {"High": 0, "Medium": 1, "Unknown": 2}
    results.sort(key=lambda x: (priority_order.get(x["priority"], 2), -x["citations"]))
    
    return results
