# utils/export.py
# 검색 결과 내보내기 (CSV, BibTeX)

import csv
import io
from typing import List, Dict
from datetime import datetime

def to_csv(papers: List[Dict]) -> str:
    """
    논문 리스트를 CSV 문자열로 변환
    
    Args:
        papers: 논문 정보 딕셔너리 리스트
        
    Returns:
        CSV 형식 문자열
    """
    if not papers:
        return ""
    
    output = io.StringIO()
    fieldnames = [
        "title", "authors", "year", "venue", "citations",
        "priority", "track", "abstract", "url", "pdf_url"
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(papers)
    
    return output.getvalue()

def to_bibtex(papers: List[Dict]) -> str:
    """
    논문 리스트를 BibTeX 형식으로 변환
    
    Args:
        papers: 논문 정보 딕셔너리 리스트
        
    Returns:
        BibTeX 형식 문자열
    """
    if not papers:
        return ""
    
    bibtex_entries = []
    
    for i, paper in enumerate(papers):
        # 저자 첫 단어 + 연도로 키 생성
        first_author = paper.get("authors", "Unknown").split(",")[0].split()[-1]
        year = paper.get("year", "0000")
        key = f"{first_author}{year}_{i+1}"
        
        # 저자 포맷 (BibTeX 형식: "Last1, First1 and Last2, First2")
        authors = paper.get("authors", "Unknown")
        
        entry = f"""@article{{{key},
  title = {{{paper.get("title", "")}}},
  author = {{{authors}}},
  journal = {{{paper.get("venue", "")}}},
  year = {{{year}}},
  note = {{Citations: {paper.get("citations", 0)}}},
  url = {{{paper.get("url", "")}}}
}}"""
        bibtex_entries.append(entry)
    
    return "\n\n".join(bibtex_entries)

def generate_filename(prefix: str = "papers", extension: str = "csv") -> str:
    """타임스탬프가 포함된 파일명 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def get_summary_stats(papers: List[Dict]) -> Dict:
    """
    검색 결과 요약 통계
    
    Args:
        papers: 논문 정보 딕셔너리 리스트
        
    Returns:
        통계 정보 딕셔너리
    """
    if not papers:
        return {
            "total": 0,
            "high_priority": 0,
            "medium_priority": 0,
            "avg_citations": 0,
            "year_range": "N/A",
            "top_venues": []
        }
    
    high_priority = sum(1 for p in papers if p.get("priority") == "High")
    medium_priority = sum(1 for p in papers if p.get("priority") == "Medium")
    
    citations = [p.get("citations", 0) for p in papers]
    avg_citations = sum(citations) / len(citations) if citations else 0
    
    years = [p.get("year", 0) for p in papers if p.get("year")]
    year_range = f"{min(years)}-{max(years)}" if years else "N/A"
    
    # 상위 저널 집계
    venue_counts = {}
    for p in papers:
        venue = p.get("venue", "Unknown")
        venue_counts[venue] = venue_counts.get(venue, 0) + 1
    
    top_venues = sorted(venue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total": len(papers),
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "avg_citations": round(avg_citations, 1),
        "year_range": year_range,
        "top_venues": top_venues
    }
