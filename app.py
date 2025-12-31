# app.py
# 학술 논문 검색 대시보드

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from config.journals import (
    TARGET_JOURNALS, EXTENDED_JOURNALS, JOURNAL_METADATA,
    get_all_target_journals, get_all_extended_journals, get_journal_metadata
)
from config.keywords import (
    KEYWORD_EXPANSIONS, RESEARCH_PRESETS, CONTEXT_KEYWORDS,
    expand_keywords, get_all_expanded_terms
)
from utils.search import search_and_filter, search_papers
from utils.export import to_csv, to_bibtex, get_summary_stats

st.set_page_config(page_title="📚 Research Paper Tracker", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main-header {font-size: 2rem; font-weight: bold; margin-bottom: 1rem;}
    .journal-badge {background-color: #1f77b4; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 4px;}
    .tier-badge {background-color: #2ca02c; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;}
</style>
""", unsafe_allow_html=True)

if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "search_executed" not in st.session_state:
    st.session_state.search_executed = False
if "raw_api_results" not in st.session_state:
    st.session_state.raw_api_results = []

keywords = []
selected_expansions = {}
search_keywords = []

with st.sidebar:
    st.markdown("## 🔍 검색 설정")
    st.markdown("### 검색 모드")
    search_mode = st.radio("검색 방식 선택", ["단순 검색", "스마트 확장"], index=1, help="스마트 확장: 유의어/관련어 포함 검색")
    
    st.markdown("---")
    st.markdown("### 키워드 입력")
    
    preset_option = st.selectbox("📌 저장된 연구 주제", ["직접 입력"] + list(RESEARCH_PRESETS.keys()), help="자주 사용하는 검색어 조합")
    
    if preset_option == "직접 입력":
        keyword_input = st.text_input("키워드 입력 (쉼표로 구분)", placeholder="예: Social Robot, Tourism, AI")
        keywords = [k.strip() for k in keyword_input.split(",") if k.strip()]
    else:
        preset_data = RESEARCH_PRESETS[preset_option]
        st.info(f"📝 {preset_data['description']}")
        keywords = preset_data["keywords"]
        st.write("**포함 키워드:**", ", ".join(keywords))
    
    if search_mode == "스마트 확장" and keywords:
        st.markdown("### 🔄 확장된 키워드")
        expanded = expand_keywords(keywords)
        for original, expansions in expanded.items():
            with st.expander(f"📍 {original}", expanded=True):
                selected = []
                for term in expansions:
                    if st.checkbox(term, value=True, key=f"exp_{original}_{term}"):
                        selected.append(term)
                selected_expansions[original] = selected
        for terms in selected_expansions.values():
            search_keywords.extend(terms)
        if search_keywords:
            st.markdown("**검색 쿼리 미리보기:**")
            st.code(" OR ".join(search_keywords[:5]) + ("..." if len(search_keywords) > 5 else ""))
    else:
        search_keywords = keywords.copy()
    
    st.markdown("---")
    st.markdown("### 📚 저널 필터")
    st.markdown("**[Track A] 핵심 저널**")
    selected_categories = {}
    for category, data in TARGET_JOURNALS.items():
        selected_categories[category] = st.checkbox(f"{data['description']} ({len(data['journals'])}개)", value=True, key=f"cat_{category}")
    
    st.markdown("**[Track B] 확장 저널**")
    include_extended = st.checkbox("리스트 외 Q1 저널 포함", value=False)
    
    st.markdown("---")
    st.markdown("### ⚙️ 필터 옵션")
    col1, col2 = st.columns(2)
    with col1:
        year_start = st.number_input("시작 연도", min_value=2000, max_value=2025, value=2015)
    with col2:
        year_end = st.number_input("종료 연도", min_value=2000, max_value=2025, value=2025)
    min_citations = st.slider("최소 인용수", 0, 100, 0)
    max_results = st.slider("최대 결과 수", 10, 200, 50)
    
    st.markdown("---")
    
    # 디버깅 모드 추가
    debug_mode = st.checkbox("🔧 디버깅 모드 (API 원본 결과 보기)", value=False)
    
    st.markdown("---")
    search_button = st.button("🔍 검색 시작", type="primary", use_container_width=True)

st.markdown('<p class="main-header">📚 Research Paper Tracker</p>', unsafe_allow_html=True)
st.markdown("Tourism & Physical AI 연구를 위한 논문 수집 대시보드")

if search_button:
    if not search_keywords:
        st.warning("⚠️ 검색할 키워드가 없습니다. 키워드를 입력하거나 프리셋을 선택해주세요.")
    else:
        with st.spinner("논문을 검색하는 중..."):
            try:
                target_journals = []
                for category, selected in selected_categories.items():
                    if selected:
                        target_journals.extend(TARGET_JOURNALS[category]["journals"])
                
                extended_journals = get_all_extended_journals() if include_extended else []
                
                st.info(f"🔍 검색 키워드: {', '.join(search_keywords[:5])}{'...' if len(search_keywords) > 5 else ''}")
                st.info(f"📚 타겟 저널 수: {len(target_journals)}개 | 📅 검색 기간: {year_start}-{year_end}")
                
                # API 원본 결과 저장 (디버깅용)
                query = " OR ".join(search_keywords)
                raw_papers = search_papers(
                    query=query,
                    year_start=int(year_start),
                    year_end=int(year_end),
                    min_citations=int(min_citations),
                    limit=int(max_results)
                )
                st.session_state.raw_api_results = raw_papers
                
                # 필터링된 결과
                results = search_and_filter(
                    keywords=search_keywords,
                    target_journals=target_journals,
                    extended_journals=extended_journals,
                    year_start=int(year_start),
                    year_end=int(year_end),
                    min_citations=int(min_citations),
                    include_extended=include_extended,
                    limit=int(max_results)
                )
                
                st.session_state.search_results = results
                st.session_state.search_executed = True
                
                # 디버깅 정보
                st.info(f"📊 API 원본 결과: {len(raw_papers)}개 → 필터링 후: {len(results)}개")
                
                if results:
                    st.success(f"✅ {len(results)}개의 논문을 찾았습니다!")
                else:
                    st.warning("⚠️ 필터링 후 결과가 없습니다. 아래 디버깅 모드를 켜서 API 원본 결과를 확인해보세요.")
            except Exception as e:
                st.error(f"❌ 검색 중 오류 발생: {str(e)}")
                st.session_state.search_results = []

# 디버깅 모드: API 원본 결과 표시
if debug_mode and st.session_state.raw_api_results:
    st.markdown("### 🔧 디버깅: API 원본 결과")
    st.markdown(f"**API가 반환한 논문 수:** {len(st.session_state.raw_api_results)}개")
    
    st.markdown("**저널(venue) 목록 (API 반환값):**")
    venues = [p.get("venue", "N/A") for p in st.session_state.raw_api_results[:20]]
    for i, v in enumerate(venues):
        st.text(f"{i+1}. {v}")
    
    with st.expander("📋 원본 데이터 샘플 (처음 3개)"):
        for i, paper in enumerate(st.session_state.raw_api_results[:3]):
            st.json({
                "title": paper.get("title"),
                "venue": paper.get("venue"),
                "year": paper.get("year"),
                "citationCount": paper.get("citationCount")
            })

results = st.session_state.search_results

if results:
    stats = get_summary_stats(results)
    st.markdown("### 📊 검색 결과 요약")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 논문 수", stats["total"])
    col2.metric("High Priority", stats["high_priority"])
    col3.metric("Medium Priority", stats["medium_priority"])
    col4.metric("평균 인용수", stats["avg_citations"])
    
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📄 논문 목록", "📈 시각화", "💾 내보내기"])
    
    with tab1:
        sort_option = st.selectbox("정렬 기준", ["우선순위 (기본)", "인용수 (높은 순)", "연도 (최신 순)", "연도 (오래된 순)"])
        sorted_results = results.copy()
        if sort_option == "인용수 (높은 순)":
            sorted_results.sort(key=lambda x: x["citations"], reverse=True)
        elif sort_option == "연도 (최신 순)":
            sorted_results.sort(key=lambda x: x["year"] or 0, reverse=True)
        elif sort_option == "연도 (오래된 순)":
            sorted_results.sort(key=lambda x: x["year"] or 9999)
        
        for paper in sorted_results:
            with st.expander(f"**{paper['title'][:80]}{'...' if len(paper['title']) > 80 else ''}** | {paper['year']} | Cited: {paper['citations']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**저자:** {paper['authors']}")
                    st.markdown(f"**저널:** {paper['venue']}")
                    journal_meta = get_journal_metadata(paper['venue'])
                    if journal_meta.get("IF"):
                        st.markdown(f"<span class='journal-badge'>IF: {journal_meta['IF']}</span><span class='tier-badge'>{journal_meta.get('tier', 'N/A')}</span>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"**Priority:** {paper['priority']}")
                    st.markdown(f"**Track:** {paper['track']}")
                st.markdown("**초록:**")
                st.markdown(paper['abstract'] if paper['abstract'] else "_초록 없음_")
                if paper['url']:
                    st.markdown(f"[📎 논문 링크]({paper['url']})")
                if paper['pdf_url']:
                    st.markdown(f"[📥 PDF 다운로드]({paper['pdf_url']})")
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📅 연도별 논문 수")
            year_data = [r["year"] for r in results if r["year"]]
            if year_data:
                year_counts = pd.Series(year_data).value_counts().sort_index()
                fig_year = px.bar(x=year_counts.index, y=year_counts.values, labels={"x": "연도", "y": "논문 수"})
                fig_year.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig_year, use_container_width=True)
        with col2:
            st.markdown("#### 🎯 Priority 분포")
            priority_data = [r["priority"] for r in results]
            if priority_data:
                priority_counts = pd.Series(priority_data).value_counts()
                fig_priority = px.pie(values=priority_counts.values, names=priority_counts.index)
                fig_priority.update_layout(height=300)
                st.plotly_chart(fig_priority, use_container_width=True)
        
        st.markdown("#### 👤 상위 인용 논문 Top 10")
        top_papers = sorted(results, key=lambda x: x["citations"], reverse=True)[:10]
        if top_papers:
            fig_top = px.bar(x=[p["citations"] for p in top_papers], y=[p["title"][:40] + "..." if len(p["title"]) > 40 else p["title"] for p in top_papers], orientation="h", labels={"x": "인용수", "y": "논문"})
            fig_top.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_top, use_container_width=True)
    
    with tab3:
        st.markdown("#### 💾 검색 결과 내보내기")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**CSV 형식**")
            csv_data = to_csv(results)
            st.download_button(label="📥 CSV 다운로드", data=csv_data, file_name=f"papers_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)
        with col2:
            st.markdown("**BibTeX 형식**")
            bibtex_data = to_bibtex(results)
            st.download_button(label="📥 BibTeX 다운로드", data=bibtex_data, file_name=f"papers_{datetime.now().strftime('%Y%m%d')}.bib", mime="text/plain", use_container_width=True)

else:
    if not st.session_state.search_executed:
        st.info("👈 왼쪽 사이드바에서 키워드와 필터를 설정한 후 '검색 시작' 버튼을 클릭하세요.")
    
    with st.expander("📖 사용 가이드", expanded=True):
        st.markdown("""
        ### 기능 소개
        **1. 검색 모드** - 단순 검색 / 스마트 확장 (유의어 포함)
        **2. 저널 필터** - Track A (핵심 저널) / Track B (확장 저널)
        **3. 결과 표시** - High/Medium/Low Priority
        **4. 내보내기** - CSV, BibTeX
        **5. 디버깅 모드** - API 원본 결과 확인 가능
        """)
    
    st.markdown("### 📌 저장된 연구 주제 프리셋")
    for name, data in RESEARCH_PRESETS.items():
        with st.expander(f"🔖 {name}"):
            st.markdown(f"**설명:** {data['description']}")
            st.markdown(f"**키워드:** {', '.join(data['keywords'])}")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>📚 Research Paper Tracker | Powered by Semantic Scholar API</div>", unsafe_allow_html=True)
