# utils/export.py
# 검색 결과 내보내기 기능

import csv
import io
from typing import List, Dict

def to_csv(papers: List[Dict]) -> str:
    """논문 목록을 CSV 형식으로 변환"""
    if not papers:
        return ""
    
    output = io.StringIO()
    fieldnames = ["title", "authors", "year", "venue", "citations", "priority", "track", "source", "url", "abstract"]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    
    for paper in papers:
        writer.writerow({
            "title": paper.get("title", ""),
            "authors": paper.get("authors", ""),
            "year": paper.get("year", ""),
            "venue": paper.get("venue", ""),
            "citations": paper.get("citations", 0),
            "priority": paper.get("priority", ""),
            "track": paper.get("track", ""),
            "source": paper.get("source", ""),
            "url": paper.get("url", ""),
            "abstract": (paper.get("abstract", "") or "")[:500]
        })
    
    return output.getvalue()

def to_bibtex(papers: List[Dict]) -> str:
    """논문 목록을 BibTeX 형식으로 변환"""
    if not papers:
        return ""
    
    entries = []
    for i, paper in enumerate(papers):
        # BibTeX 키 생성
        first_author = (paper.get("authors", "") or "Unknown").split(",")[0].split()[-1] if paper.get("authors") else "Unknown"
        year = paper.get("year", "0000") or "0000"
        key = f"{first_author}{year}_{i}"
        key = "".join(c for c in key if c.isalnum() or c == "_")
        
        # BibTeX 엔트리 생성
        entry = f"@article{{{key},\n"
        entry += f"  title = {{{paper.get('title', 'No Title')}}},\n"
        entry += f"  author = {{{paper.get('authors', 'Unknown')}}},\n"
        entry += f"  year = {{{year}}},\n"
        entry += f"  journal = {{{paper.get('venue', 'Unknown')}}},\n"
        
        if paper.get("url"):
            entry += f"  url = {{{paper.get('url')}}},\n"
        
        if paper.get("citations"):
            entry += f"  note = {{Cited by {paper.get('citations')}}},\n"
        
        entry += "}\n"
        entries.append(entry)
    
    return "\n".join(entries)

def get_summary_stats(papers: List[Dict]) -> Dict:
    """검색 결과 요약 통계"""
    if not papers:
        return {
            "total": 0,
            "high_priority": 0,
            "medium_priority": 0,
            "low_priority": 0,
            "avg_citations": 0,
            "year_range": "N/A",
            "top_journals": []
        }
    
    priorities = [p.get("priority", "Unknown") for p in papers]
    citations = [p.get("citations", 0) or 0 for p in papers]
    years = [p.get("year") for p in papers if p.get("year") and p.get("year") != "N/A"]
    venues = [p.get("venue") for p in papers if p.get("venue") and p.get("venue") not in ["Unknown", "", "N/A"]]
    
    # 상위 저널
    venue_counts = {}
    for v in venues:
        venue_counts[v] = venue_counts.get(v, 0) + 1
    top_journals = sorted(venue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total": len(papers),
        "high_priority": priorities.count("High"),
        "medium_priority": priorities.count("Medium"),
        "low_priority": priorities.count("Low"),
        "avg_citations": round(sum(citations) / len(citations), 1) if citations else 0,
        "year_range": f"{min(years)}-{max(years)}" if years else "N/A",
        "top_journals": top_journals
    }
