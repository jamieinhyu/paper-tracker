# utils/search.py
# Semantic Scholar + OpenAlex API 통합 검색

import requests
from typing import List, Dict, Optional
from datetime import datetime

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
OPENALEX_API = "https://api.openalex.org"

# 저널명 약어 사전
JOURNAL_ALIASES = {
    "annals of tourism research": ["ann tour res", "annals tourism", "atr", "ann. tour. res"],
    "tourism management": ["tour manag", "tour manage", "tourism manage", "tour. manag"],
    "journal of travel research": ["j travel res", "jtr", "j. travel res.", "j travel research"],
    "journal of sustainable tourism": ["j sustain tour", "sustainable tourism", "j. sustain. tour"],
    "international journal of hospitality management": ["int j hosp manag", "ijhm", "int j hospitality", "int. j. hosp. manag"],
    "journal of hospitality and tourism research": ["j hosp tour res", "jhtr", "j. hosp. tour. res"],
    "journal of hospitality & tourism research": ["j hosp tour res", "jhtr"],
    "current issues in tourism": ["curr issues tour", "current issues tourism", "curr. issues tour"],
    "tourism management perspectives": ["tour manag perspect", "tourism manage persp"],
    "international journal of contemporary hospitality management": ["int j contemp hosp", "ijchm"],
    "journal of travel & tourism marketing": ["j travel tour mark", "jttm"],
    "journal of hospitality marketing & management": ["j hosp mark manage", "jhmm"],
    "asia pacific journal of tourism research": ["asia pac j tour", "apjtr"],
    "journal of hospitality and tourism management": ["j hosp tour manag", "jhtm"],
    "international journal of tourism research": ["int j tour res", "ijtr"],
    "journal of hospitality and tourism technology": ["j hosp tour tech", "jhtt"],
    "information technology & tourism": ["inf technol tour", "it&t", "itt"],
    "computers in human behavior": ["comput hum behav", "chb", "comput. hum. behav"],
    "international journal of information management": ["int j inf manag", "ijim"],
    "journal of business research": ["j bus res", "jbr", "j. bus. res"],
    "journal of retailing and consumer services": ["j retail consum serv", "jrcs"],
    "journal of marketing": ["j marketing", "j. marketing", "jm"],
    "information systems research": ["inf syst res", "isr"],
    "journal of service research": ["j serv res", "jsr"],
    "international journal of social robotics": ["int j soc robot", "ijsr"],
}

def normalize_venue(venue: str) -> str:
    if not venue:
        return ""
    normalized = venue.lower().strip()
    for char in [".", ",", ":", ";", "&"]:
        normalized = normalized.replace(char, " ")
    normalized = " ".join(normalized.split())
    return normalized

def match_journal(venue: str, target_journals: List[str]) -> bool:
    if not venue:
        return False
    
    venue_norm = normalize_venue(venue)
    
    for target in target_journals:
        target_norm = normalize_venue(target)
        
        # 1. 정확한 매칭
        if target_norm == venue_norm:
            return True
        
        # 2. 포함 관계
        if target_norm in venue_norm or venue_norm in target_norm:
            return True
        
        # 3. 핵심 단어 매칭 (2개 이상)
        target_words = set(target_norm.split())
        venue_words = set(venue_norm.split())
        common = target_words & venue_words
        important_words = common - {"of", "the", "and", "in", "for", "a", "an", "journal", "international"}
        if len(important_words) >= 2:
            return True
        
        # 4. 약어 매칭
        if target_norm in JOURNAL_ALIASES:
            for alias in JOURNAL_ALIASES[target_norm]:
                alias_norm = normalize_venue(alias)
                if alias_norm in venue_norm or venue_norm in alias_norm:
                    return True
    
    return False

# ==================== Semantic Scholar ====================

def search_semantic_scholar(
    query: str,
    year_start: int = 2015,
    year_end: int = None,
    min_citations: int = 0,
    limit: int = 100
) -> List[Dict]:
    if year_end is None:
        year_end = datetime.now().year
    
    fields = "paperId,title,abstract,year,citationCount,authors,venue,url,openAccessPdf"
    all_papers = []
    offset = 0
    per_page = 100
    max_pages = min(3, (limit // per_page) + 1)
    
    for _ in range(max_pages):
        url = f"{SEMANTIC_SCHOLAR_API}/paper/search"
        params = {
            "query": query,
            "year": f"{year_start}-{year_end}",
            "limit": per_page,
            "offset": offset,
            "fields": fields
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            papers = response.json().get("data", [])
            if not papers:
                break
            all_papers.extend(papers)
            offset += per_page
            if len(all_papers) >= limit:
                break
        except:
            break
    
    # 표준 형식으로 변환
    results = []
    for p in all_papers:
        results.append({
            "id": p.get("paperId", ""),
            "title": p.get("title", ""),
            "abstract": p.get("abstract", ""),
            "year": p.get("year"),
            "citations": p.get("citationCount", 0) or 0,
            "authors": ", ".join([a.get("name", "") for a in (p.get("authors") or [])[:3]]),
            "venue": p.get("venue", ""),
            "url": p.get("url", ""),
            "pdf_url": (p.get("openAccessPdf") or {}).get("url", ""),
            "source": "Semantic Scholar"
        })
    
    if min_citations > 0:
        results = [r for r in results if r["citations"] >= min_citations]
    
    return results[:limit]

# ==================== OpenAlex ====================

def search_openalex(
    query: str,
    year_start: int = 2015,
    year_end: int = None,
    min_citations: int = 0,
    limit: int = 100
) -> List[Dict]:
    if year_end is None:
        year_end = datetime.now().year
    
    all_papers = []
    per_page = 100
    max_pages = min(3, (limit // per_page) + 1)
    cursor = "*"
    
    for _ in range(max_pages):
        url = f"{OPENALEX_API}/works"
        params = {
            "search": query,
            "filter": f"publication_year:{year_start}-{year_end}",
            "sort": "cited_by_count:desc",
            "per_page": per_page,
            "cursor": cursor
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            works = data.get("results", [])
            if not works:
                break
            all_papers.extend(works)
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor or len(all_papers) >= limit:
                break
        except:
            break
    
    # 표준 형식으로 변환
    results = []
    for w in all_papers:
        # 저자 추출
        authors = []
        for auth in (w.get("authorships") or [])[:3]:
            name = auth.get("author", {}).get("display_name", "")
            if name:
                authors.append(name)
        
        # 저널명 추출
        venue = ""
        primary_loc = w.get("primary_location") or {}
        source = primary_loc.get("source") or {}
        venue = source.get("display_name", "")
        
        # PDF URL
        pdf_url = ""
        if primary_loc.get("is_oa"):
            pdf_url = primary_loc.get("pdf_url", "") or ""
        
        results.append({
            "id": w.get("id", ""),
            "title": w.get("title", ""),
            "abstract": (w.get("abstract_inverted_index") and "Abstract available") or "",
            "year": w.get("publication_year"),
            "citations": w.get("cited_by_count", 0) or 0,
            "authors": ", ".join(authors),
            "venue": venue,
            "url": w.get("doi", "") or w.get("id", ""),
            "pdf_url": pdf_url,
            "source": "OpenAlex"
        })
    
    if min_citations > 0:
        results = [r for r in results if r["citations"] >= min_citations]
    
    return results[:limit]

# ==================== 통합 검색 ====================

def search_papers(query, year_start=2015, year_end=None, min_citations=0, limit=100):
    """기존 호환성을 위한 래퍼 함수"""
    return search_semantic_scholar(query, year_start, year_end, min_citations, limit)

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
            "ai", "artificial intelligence", "technology", "digital"
        ]
    
    venue = paper.get("venue", "")
    title = (paper.get("title") or "").lower()
    abstract = (paper.get("abstract") or "").lower()
    text = f"{title} {abstract}"
    
    is_target = match_journal(venue, target_journals)
    
    keywords_lower = [k.lower() for k in keywords]
    has_keyword = any(k in text for k in keywords_lower)
    
    if is_target and has_keyword:
        return {"priority": "High", "track": "Core Journal", "reason": "타겟 저널 + 키워드 매칭"}
    
    has_context = any(c in text for c in context_keywords)
    
    if has_context and has_keyword:
        return {"priority": "Medium", "track": "Discovery", "reason": "맥락 + 기술 키워드 동시 매칭"}
    
    if has_keyword and not strict_journal_filter:
        return {"priority": "Low", "track": "Keyword Match", "reason": "키워드 매칭"}
    
    return None

def format_paper_for_display(paper: Dict, relevance: Dict = None) -> Dict:
    authors = paper.get("authors", "")
    if isinstance(authors, list):
        authors = ", ".join([a.get("name", str(a)) for a in authors[:3]])
    
    return {
        "id": paper.get("id", ""),
        "title": paper.get("title", "No Title"),
        "authors": authors or "Unknown",
        "year": paper.get("year", "N/A"),
        "venue": paper.get("venue", "Unknown"),
        "citations": paper.get("citations", 0),
        "abstract": paper.get("abstract", "No abstract available"),
        "url": paper.get("url", ""),
        "pdf_url": paper.get("pdf_url", ""),
        "source": paper.get("source", "Unknown"),
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
    strict_journal_filter: bool = False,
    search_source: str = "both"
) -> List[Dict]:
    query = " OR ".join(keywords)
    search_limit = min(limit * 2, 200)
    
    all_papers = []
    
    # 검색 소스에 따라 API 호출
    if search_source in ["semantic", "both"]:
        ss_results = search_semantic_scholar(query, year_start, year_end, min_citations, search_limit)
        all_papers.extend(ss_results)
    
    if search_source in ["openalex", "both"]:
        oa_results = search_openalex(query, year_start, year_end, min_citations, search_limit)
        all_papers.extend(oa_results)
    
    # 중복 제거 (제목 기준)
    seen_titles = set()
    unique_papers = []
    for p in all_papers:
        title_key = (p.get("title") or "").lower().strip()[:50]
        if title_key and title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_papers.append(p)
    
    if not unique_papers:
        return []
    
    all_target = target_journals.copy()
    if include_extended and extended_journals:
        all_target.extend(extended_journals)
    
    results = []
    for paper in unique_papers:
        relevance = check_relevance(paper, keywords, all_target, strict_journal_filter=strict_journal_filter)
        if relevance:
            formatted = format_paper_for_display(paper, relevance)
            results.append(formatted)
    
    priority_order = {"High": 0, "Medium": 1, "Low": 2, "Unknown": 3}
    results.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["citations"]))
    
    return results[:limit]
