# app.py
# 학술 논문 검색 대시보드 (Semantic Scholar + OpenAlex)

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from config.journals import (
    TARGET_JOURNALS, EXTENDED_JOURNALS,
    get_all_extended_journals, get_journal_metadata
)
from config.keywords import (
    KEYWORD_EXPANSIONS, RESEARCH_PRESETS,
    expand_keywords
)
from utils.search import search_and_filter
from utils.export import to_csv, to_bibtex, get_summary_stats

st.set_page_config(page_title="📚 Research Paper Tracker", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main-header {font-size: 2rem; font-weight: bold; margin-bottom: 1rem;}
    .journal-badge {background-color: #1f77b4; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 4px;}
    .tier-badge {background-color: #2ca02c; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;}
    .source-badge {background-color: #ff7f0e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-left: 4px;}
</style>
""", unsafe_allow_html=True)

if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "search_executed" not in st.session_state:
    st.session_state.search_executed = False

keywords = []
selected_expansions = {}
search_keywords = []

with st.sidebar:
    st.markdown("## 🔍 검색 설정")
    
    # 검색 소스 선택 (새로 추가!)
    st.markdown("### 📡 검색 소스")
    search_source = st.radio(
        "API 선택",
        ["both", "semantic", "openalex"],
        format_func=lambda x: {
            "both": "🔄 통합 검색 (추천)",
            "semantic": "📚 Semantic Scholar만",
            "openalex": "🌐 OpenAlex만"
        }[x],
        index=0,
        help="OpenAlex가 최신 논문 반영이 더 빠릅니다"
    )
    
    st.markdown("---")
    
    # 검색 모드
    st.markdown("### 검색 모드")
    search_mode = st.radio("검색 방식 선택", ["단순 검색", "스마트 확장"], index=0, help="스마트 확장: 유의어/관련어 포함 검색")
    
    st.markdown("---")
    st.markdown("### 키워드 입력")
    
    preset_option = st.selectbox("📌 저장된 연구 주제", ["직접 입력"] + list(RESEARCH_PRESETS.keys()))
    
    if preset_option == "직접 입력":
        keyword_input = st.text_input("키워드 입력 (쉼표로 구분)", placeholder="예: social media, tourism")
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
    else:
        search_keywords = keywords.copy()
    
    st.markdown("---")
    st.markdown("### 📚 저널 필터")
    st.markdown("**[Track A] 핵심 저널**")
    selected_categories = {}
    for category, data in TARGET_JOURNALS.items():
        selected_categories[category] = st.checkbox(
            f"{data['description']} ({len(data['journals'])}개)", 
            value=True, 
            key=f"cat_{category}"
        )
    
    st.markdown("**[Track B] 확장 저널**")
    include_extended = st.checkbox("리스트 외 Q1 저널 포함", value=False)
    
    st.markdown("---")
    st.markdown("### ⚙️ 필터 옵션")
    col1, col2 = st.columns(2)
    with col1:
        year_start = st.number_input("시작 연도", min_value=2000, max_value=2025, value=2015)
    with col2:
        year_end = st.number_input("종료 연도", min_value=2000, max_value=2026, value=2025)
    
    min_citations = st.slider("최소 인용수", 0, 100, 0)
    max_results = st.slider("최대 결과 수", 10, 300, 100)  # 기본값 100으로 증가
    
    st.markdown("---")
    search_button = st.button("🔍 검색 시작", type="primary", use_container_width=True)

# 메인 영역
st.markdown('<p class="main-header">📚 Research Paper Tracker</p>', unsafe_allow_html=True)
st.markdown("Tourism & Physical AI 연구를 위한 논문 수집 대시보드")

if search_button:
    if not search_keywords:
        st.warning("⚠️ 검색할 키워드가 없습니다.")
    else:
        with st.spinner("논문을 검색하는 중... (Semantic Scholar + OpenAlex)"):
            try:
                target_journals = []
                for category, selected in selected_categories.items():
                    if selected:
                        target_journals.extend(TARGET_JOURNALS[category]["journals"])
                
                extended_journals = get_all_extended_journals() if include_extended else []
                
                source_name = {"both": "통합", "semantic": "Semantic Scholar", "openalex": "OpenAlex"}[search_source]
                st.info(f"🔍 검색: {', '.join(search_keywords[:3])}{'...' if len(search_keywords) > 3 else ''} | 📡 {source_name} | 📅 {year_start}-{year_end}")
                
                results = search_and_filter(
                    keywords=search_keywords,
                    target_journals=target_journals,
                    extended_journals=extended_journals,
                    year_start=int(year_start),
                    year_end=int(year_end),
                    min_citations=int(min_citations),
                    include_extended=include_extended,
                    limit=int(max_results),
                    search_source=search_source
                )
                
                st.session_state.search_results = results
                st.session_state.search_executed = True
                
                if results:
                    # 소스별 통계
                    ss_count = len([r for r in results if r.get("source") == "Semantic Scholar"])
                    oa_count = len([r for r in results if r.get("source") == "OpenAlex"])
                    st.success(f"✅ {len(results)}개 논문 발견! (Semantic Scholar: {ss_count}개, OpenAlex: {oa_count}개)")
                else:
                    st.warning("⚠️ 검색 결과가 없습니다. 다른 키워드나 연도 범위를 시도해보세요.")
            except Exception as e:
                st.error(f"❌ 오류 발생: {str(e)}")
                st.session_state.search_results = []

results = st.session_state.search_results

if results:
    stats = get_summary_stats(results)
    st.markdown("### 📊 검색 결과 요약")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("총 논문 수", stats["total"])
    col2.metric("High Priority", stats["high_priority"])
    col3.metric("Medium Priority", stats["medium_priority"])
    col4.metric("Low Priority", stats.get("low_priority", 0))
    col5.metric("평균 인용수", stats["avg_citations"])
    
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📄 논문 목록", "📈 시각화", "💾 내보내기"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            sort_option = st.selectbox("정렬 기준", ["우선순위 (기본)", "인용수 (높은 순)", "연도 (최신 순)", "연도 (오래된 순)"])
        with col2:
            filter_priority = st.multiselect("Priority 필터", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
        
        sorted_results = [r for r in results if r["priority"] in filter_priority]
        
        if sort_option == "인용수 (높은 순)":
            sorted_results.sort(key=lambda x: x["citations"], reverse=True)
        elif sort_option == "연도 (최신 순)":
            sorted_results.sort(key=lambda x: x["year"] or 0, reverse=True)
        elif sort_option == "연도 (오래된 순)":
            sorted_results.sort(key=lambda x: x["year"] or 9999)
        
        st.markdown(f"**표시 중: {len(sorted_results)}개 논문**")
        
        for paper in sorted_results:
            priority_color = {"High": "🟢", "Medium": "🟡", "Low": "🔵"}.get(paper["priority"], "⚪")
            
            with st.expander(f"{priority_color} **{paper['title'][:80]}{'...' if len(paper['title']) > 80 else ''}** | {paper['year']} | Cited: {paper['citations']}", expanded=False):
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
                    st.markdown(f"<span class='source-badge'>{paper.get('source', 'N/A')}</span>", unsafe_allow_html=True)
                
                st.markdown("**초록:**")
                abstract_text = paper['abstract'] if paper['abstract'] and paper['abstract'] != "Abstract available" else "_초록 없음 (원문에서 확인)_"
                st.markdown(abstract_text)
                
                col1, col2 = st.columns(2)
                if paper['url']:
                    col1.markdown(f"[📎 논문 링크]({paper['url']})")
                if paper['pdf_url']:
                    col2.markdown(f"[📥 PDF 다운로드]({paper['pdf_url']})")
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📅 연도별 논문 수")
            year_data = [r["year"] for r in results if r["year"] and r["year"] != "N/A"]
            if year_data:
                year_counts = pd.Series(year_data).value_counts().sort_index()
                fig_year = px.bar(x=year_counts.index, y=year_counts.values, labels={"x": "연도", "y": "논문 수"})
                fig_year.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig_year, use_container_width=True)
        
        with col2:
            st.markdown("#### 🎯 Priority 분포")
            priority_counts = pd.Series([r["priority"] for r in results]).value_counts()
            fig_priority = px.pie(values=priority_counts.values, names=priority_counts.index, color=priority_counts.index, color_discrete_map={"High": "#2ca02c", "Medium": "#ff7f0e", "Low": "#1f77b4"})
            fig_priority.update_layout(height=300)
            st.plotly_chart(fig_priority, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📡 검색 소스 분포")
            source_counts = pd.Series([r.get("source", "Unknown") for r in results]).value_counts()
            fig_source = px.pie(values=source_counts.values, names=source_counts.index)
            fig_source.update_layout(height=300)
            st.plotly_chart(fig_source, use_container_width=True)
        
        with col2:
            st.markdown("#### 🏆 상위 인용 논문 Top 10")
            top_papers = sorted(results, key=lambda x: x["citations"], reverse=True)[:10]
            if top_papers:
                fig_top = px.bar(
                    x=[p["citations"] for p in top_papers],
                    y=[p["title"][:35] + "..." if len(p["title"]) > 35 else p["title"] for p in top_papers],
                    orientation="h", labels={"x": "인용수", "y": ""}
                )
                fig_top.update_layout(height=350, yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig_top, use_container_width=True)
        
        st.markdown("#### 📚 상위 저널 분포")
        venue_data = [r["venue"] for r in results if r["venue"] and r["venue"] not in ["Unknown", "", "N/A"]]
        if venue_data:
            venue_counts = pd.Series(venue_data).value_counts().head(15)
            fig_venue = px.bar(x=venue_counts.values, y=venue_counts.index, orientation="h", labels={"x": "논문 수", "y": ""})
            fig_venue.update_layout(height=450, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_venue, use_container_width=True)
    
    with tab3:
        st.markdown("#### 💾 검색 결과 내보내기")
        col1, col2 = st.columns(2)
        with col1:
            csv_data = to_csv(results)
            st.download_button(label="📥 CSV 다운로드", data=csv_data, file_name=f"papers_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)
        with col2:
            bibtex_data = to_bibtex(results)
            st.download_button(label="📥 BibTeX 다운로드", data=bibtex_data, file_name=f"papers_{datetime.now().strftime('%Y%m%d')}.bib", mime="text/plain", use_container_width=True)

else:
    if not st.session_state.search_executed:
        st.info("👈 왼쪽 사이드바에서 키워드와 필터를 설정한 후 '검색 시작' 버튼을 클릭하세요.")
    
    with st.expander("📖 사용 가이드", expanded=True):
        st.markdown("""
        ### 새로운 기능 ✨
        - **통합 검색**: Semantic Scholar + OpenAlex 동시 검색
        - **OpenAlex**: 최신 논문 (2025년 포함) 빠른 반영
        - **최대 300개** 논문까지 검색 가능
        
        ### 검색 소스 비교
        | 소스 | 장점 |
        |------|------|
        | Semantic Scholar | 인용 분석 우수, 초록 제공 |
        | OpenAlex | 최신 논문 빠름, 더 넓은 커버리지 |
        | 통합 검색 | 두 소스 장점 결합 (추천) |
        """)
    
    st.markdown("### 📌 저장된 연구 주제 프리셋")
    for name, data in RESEARCH_PRESETS.items():
        with st.expander(f"🔖 {name}"):
            st.markdown(f"**설명:** {data['description']}")
            st.markdown(f"**키워드:** {', '.join(data['keywords'])}")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>📚 Research Paper Tracker | Semantic Scholar + OpenAlex API</div>", unsafe_allow_html=True)
