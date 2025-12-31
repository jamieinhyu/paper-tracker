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
        "limit": min(limit, 100),
        "fields": ",".join(fields)
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        papers = data.get("data", [])
        
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
    context_keywords: List[str] = None,
    strict_journal_filter: bool = False
) -> Optional[Dict]:
    if context_keywords is None:
        context_keywords = [
            "tourism", "travel", "hospitality", "hotel", "tourist",
            "visitor", "destination", "leisure", "service", "robot",
            "ai", "artificial intelligence", "technology"
        ]
    
    venue = (paper.get("venue") or "").lower()
    title = (paper.get("title") or "").lower()
    abstract = (paper.get("abstract") or "").lower()
    text = f"{title} {abstract}"
    
    is_target = False
    if venue:
        for target in target_journals:
            target_lower = target.lower()
            if target_lower in venue or venue in target_lower:
                is_target = True
                break
            target_words = set(target_lower.split())
            venue_words = set(venue.split())
            common_words = target_words & venue_words
            if len(common_words) >= 2:
                is_target = True
                break
    
    keywords_lower = [k.lower() for k in keywords]
    has_keyword = any(k in text for k in keywords_lower)
    
    if is_target and has_keyword:
        return {
            "priority": "High",
            "track": "Core Journal",
            "reason": "타겟 저널 + 키워드 매칭"
        }
    
    has_context = any(c in text for c in context_keywords)
    
    if has_context and has_keyword:
        return {
            "priority": "Medium",
            "track": "Discovery",
            "reason": "맥락 + 기술 키워드 동시 매칭"
        }
    
    if has_keyword and not strict_journal_filter:
        return {
            "priority": "Low",
            "track": "Keyword Match",
            "reason": "키워드 매칭"
        }
    
    return None

def format_authors(authors: List[Dict]) -> str:
    if not authors:
        return "Unknown"
    
    names = [a.get("name", "Unknown") for a in authors[:3]]
    result = ", ".join(names)
    
    if len(authors) > 3:
        result += f" et al. ({len(authors)} authors)"
    
    return result

def format_paper_for_display(paper: Dict, relevance: Dict = None) -> Dict:
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
    limit: int = 100,
    strict_journal_filter: bool = False
) -> List[Dict]:
    query = " OR ".join(keywords)
    
    papers = search_papers(
        query=query,
        year_start=year_start,
        year_end=year_end,
        min_citations=min_citations,
        limit=limit
    )
    
    if not papers:
        return []
    
    all_target = target_journals.copy()
    if include_extended and extended_journals:
        all_target.extend(extended_journals)
    
    results = []
    for paper in papers:
        relevance = check_relevance(
            paper, 
            keywords, 
            all_target,
            strict_journal_filter=strict_journal_filter
        )
        if relevance:
            formatted = format_paper_for_display(paper, relevance)
            results.append(formatted)
    
    priority_order = {"High": 0, "Medium": 1, "Low": 2, "Unknown": 3}
    results.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["citations"]))
    
    return results
