# app.py
# 학술 논문 검색 대시보드

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 로컬 모듈 import
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

# 페이지 설정
st.set_page_config(
    page_title="📚 Research Paper Tracker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .paper-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .high-priority {
        border-left-color: #2ca02c;
    }
    .medium-priority {
        border-left-color: #ff7f0e;
    }
    .stat-card {
        background-color: #e8f4f8;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .journal-badge {
        background-color: #1f77b4;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-right: 4px;
    }
    .tier-badge {
        background-color: #2ca02c;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "saved_presets" not in st.session_state:
    st.session_state.saved_presets = list(RESEARCH_PRESETS.keys())

# ========== 사이드바 ==========
with st.sidebar:
    st.markdown("## 🔍 검색 설정")
    
    # 검색 모드
    st.markdown("### 검색 모드")
    search_mode = st.radio(
        "검색 방식 선택",
        ["단순 검색", "스마트 확장"],
        index=1,
        help="스마트 확장: 유의어/관련어 포함 검색"
    )
    
    st.markdown("---")
    
    # 키워드 입력
    st.markdown("### 키워드 입력")
    
    # 프리셋 선택
    preset_option = st.selectbox(
        "📌 저장된 연구 주제",
        ["직접 입력"] + list(RESEARCH_PRESETS.keys()),
        help="자주 사용하는 검색어 조합"
    )
    
    # 키워드 입력/표시
    if preset_option == "직접 입력":
        keyword_input = st.text_input(
            "키워드 입력 (쉼표로 구분)",
            placeholder="예: Social Robot, Tourism, AI",
            help="여러 키워드는 쉼표로 구분"
        )
        keywords = [k.strip() for k in keyword_input.split(",") if k.strip()]
    else:
        preset_data = RESEARCH_PRESETS[preset_option]
        st.info(f"📝 {preset_data['description']}")
        keywords = preset_data["keywords"]
        st.write("**포함 키워드:**", ", ".join(keywords))
    
    # 키워드 확장 옵션
    if search_mode == "스마트 확장" and keywords:
        st.markdown("### 🔄 확장된 키워드")
        expanded = expand_keywords(keywords)
        
        selected_expansions = {}
        for original, expansions in expanded.items():
            with st.expander(f"📍 {original}", expanded=True):
                selected = []
                for term in expansions:
                    if st.checkbox(term, value=True, key=f"exp_{original}_{term}"):
                        selected.append(term)
                selected_expansions[original] = selected
        
        # 최종 검색어 미리보기
        all_selected = []
        for terms in selected_expansions.values():
            all_selected.extend(terms)
        
        if all_selected:
            st.markdown("**검색 쿼리 미리보기:**")
            st.code(" OR ".join(all_selected[:5]) + ("..." if len(all_selected) > 5 else ""))
    
    st.markdown("---")
    
    # 저널 필터
    st.markdown("### 📚 저널 필터")
    
    # Track A: 핵심 저널
    st.markdown("**[Track A] 핵심 저널** (느슨한 매칭)")
    selected_categories = {}
    for category, data in TARGET_JOURNALS.items():
        selected_categories[category] = st.checkbox(
            f"{data['description']} ({len(data['journals'])}개)",
            value=True,
            key=f"cat_{category}"
        )
    
    # Track B: 확장 저널
    st.markdown("**[Track B] 확장 저널** (엄격한 매칭)")
    include_extended = st.checkbox("리스트 외 Q1 저널 포함", value=False)
    
    if include_extended:
        for category, data in EXTENDED_JOURNALS.items():
            st.checkbox(
                f"{data['description']} ({len(data['journals'])}개)",
                value=True,
                key=f"ext_{category}"
            )
    
    st.markdown("---")
    
    # 필터 옵션
    st.markdown("### ⚙️ 필터 옵션")
    
    col1, col2 = st.columns(2)
    with col1:
        year_start = st.number_input("시작 연도", min_value=2000, max_value=2025, value=2015)
    with col2:
        year_end = st.number_input("종료 연도", min_value=2000, max_value=2025, value=2025)
    
    min_citations = st.slider("최소 인용수", 0, 100, 0)
    max_results = st.slider("최대 결과 수", 10, 200, 50)
    
    st.markdown("---")
    
    # 검색 버튼
    search_button = st.button("🔍 검색 시작", type="primary", use_container_width=True)

# ========== 메인 영역 ==========
st.markdown('<p class="main-header">📚 Research Paper Tracker</p>', unsafe_allow_html=True)
st.markdown("Tourism & Physical AI 연구를 위한 논문 수집 대시보드")

# 검색 실행
if search_button and keywords:
    with st.spinner("논문을 검색하는 중..."):
        # 선택된 카테고리의 저널 수집
        target_journals = []
        for category, selected in selected_categories.items():
            if selected:
                target_journals.extend(TARGET_JOURNALS[category]["journals"])
        
        extended_journals = []
        if include_extended:
            extended_journals = get_all_extended_journals()
        
        # 확장된 키워드 사용
        if search_mode == "스마트 확장":
            search_keywords = []
            for terms in selected_expansions.values():
                search_keywords.extend(terms)
        else:
            search_keywords = keywords
        
        # 검색 실행
        results = search_and_filter(
            keywords=search_keywords,
            target_journals=target_journals,
            extended_journals=extended_journals,
            year_start=year_start,
            year_end=year_end,
            min_citations=min_citations,
            include_extended=include_extended,
            limit=max_results
        )
        
        st.session_state.search_results = results

# 결과 표시
results = st.session_state.search_results

if results:
    # 요약 통계
    stats = get_summary_stats(results)
    
    st.markdown("### 📊 검색 결과 요약")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 논문 수", stats["total"])
    with col2:
        st.metric("High Priority", stats["high_priority"])
    with col3:
        st.metric("Medium Priority", stats["medium_priority"])
    with col4:
        st.metric("평균 인용수", stats["avg_citations"])
    
    st.markdown("---")
    
    # 탭으로 결과 표시
    tab1, tab2, tab3 = st.tabs(["📄 논문 목록", "📈 시각화", "💾 내보내기"])
    
    # ===== 논문 목록 탭 =====
    with tab1:
        # 정렬 옵션
        sort_option = st.selectbox(
            "정렬 기준",
            ["우선순위 (기본)", "인용수 (높은 순)", "연도 (최신 순)", "연도 (오래된 순)"]
        )
        
        sorted_results = results.copy()
        if sort_option == "인용수 (높은 순)":
            sorted_results.sort(key=lambda x: x["citations"], reverse=True)
        elif sort_option == "연도 (최신 순)":
            sorted_results.sort(key=lambda x: x["year"] or 0, reverse=True)
        elif sort_option == "연도 (오래된 순)":
            sorted_results.sort(key=lambda x: x["year"] or 9999)
        
        # 논문 카드 표시
        for i, paper in enumerate(sorted_results):
            priority_class = "high-priority" if paper["priority"] == "High" else "medium-priority"
            
            with st.expander(
                f"**{paper['title'][:80]}{'...' if len(paper['title']) > 80 else ''}** | "
                f"{paper['year']} | Cited: {paper['citations']}",
                expanded=False
            ):
                # 메타 정보
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**저자:** {paper['authors']}")
                    st.markdown(f"**저널:** {paper['venue']}")
                    
                    # 저널 메타데이터
                    journal_meta = get_journal_metadata(paper['venue'])
                    if journal_meta["IF"]:
                        st.markdown(
                            f"<span class='journal-badge'>IF: {journal_meta['IF']}</span>"
                            f"<span class='tier-badge'>{journal_meta['tier']}</span>",
                            unsafe_allow_html=True
                        )
                
                with col2:
                    st.markdown(f"**Priority:** {paper['priority']}")
                    st.markdown(f"**Track:** {paper['track']}")
                
                # 초록
                st.markdown("**초록:**")
                st.markdown(paper['abstract'] if paper['abstract'] else "_초록 없음_")
                
                # 링크
                if paper['url']:
                    st.markdown(f"[📎 논문 링크]({paper['url']})")
                if paper['pdf_url']:
                    st.markdown(f"[📥 PDF 다운로드]({paper['pdf_url']})")
    
    # ===== 시각화 탭 =====
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # 연도별 논문 수
            st.markdown("#### 📅 연도별 논문 수")
            year_counts = pd.DataFrame(results)["year"].value_counts().sort_index()
            fig_year = px.bar(
                x=year_counts.index,
                y=year_counts.values,
                labels={"x": "연도", "y": "논문 수"},
                color_discrete_sequence=["#1f77b4"]
            )
            fig_year.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig_year, use_container_width=True)
        
        with col2:
            # Priority 분포
            st.markdown("#### 🎯 Priority 분포")
            priority_counts = pd.DataFrame(results)["priority"].value_counts()
            fig_priority = px.pie(
                values=priority_counts.values,
                names=priority_counts.index,
                color_discrete_sequence=["#2ca02c", "#ff7f0e", "#d62728"]
            )
            fig_priority.update_layout(height=300)
            st.plotly_chart(fig_priority, use_container_width=True)
        
        # 상위 저자 (인용수 기준)
        st.markdown("#### 👤 상위 인용 논문 Top 10")
        top_papers = sorted(results, key=lambda x: x["citations"], reverse=True)[:10]
        
        fig_top = px.bar(
            x=[p["citations"] for p in top_papers],
            y=[p["title"][:40] + "..." for p in top_papers],
            orientation="h",
            labels={"x": "인용수", "y": "논문"},
            color_discrete_sequence=["#2ca02c"]
        )
        fig_top.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_top, use_container_width=True)
        
        # 저널별 분포
        st.markdown("#### 📚 저널별 분포")
        venue_counts = pd.DataFrame(results)["venue"].value_counts().head(10)
        fig_venue = px.bar(
            x=venue_counts.values,
            y=venue_counts.index,
            orientation="h",
            labels={"x": "논문 수", "y": "저널"},
            color_discrete_sequence=["#1f77b4"]
        )
        fig_venue.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_venue, use_container_width=True)
    
    # ===== 내보내기 탭 =====
    with tab3:
        st.markdown("#### 💾 검색 결과 내보내기")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**CSV 형식**")
            csv_data = to_csv(results)
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv_data,
                file_name=f"papers_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            st.markdown("**BibTeX 형식**")
            bibtex_data = to_bibtex(results)
            st.download_button(
                label="📥 BibTeX 다운로드",
                data=bibtex_data,
                file_name=f"papers_{datetime.now().strftime('%Y%m%d')}.bib",
                mime="text/plain",
                use_container_width=True
            )
        
        # 미리보기
        with st.expander("BibTeX 미리보기"):
            st.code(bibtex_data[:2000] + "..." if len(bibtex_data) > 2000 else bibtex_data)

else:
    # 초기 상태 또는 결과 없음
    st.info("👈 왼쪽 사이드바에서 키워드와 필터를 설정한 후 '검색 시작' 버튼을 클릭하세요.")
    
    # 사용 가이드
    with st.expander("📖 사용 가이드", expanded=True):
        st.markdown("""
        ### 기능 소개
        
        **1. 검색 모드**
        - **단순 검색**: 입력한 키워드만 정확히 검색
        - **스마트 확장**: 유의어/관련어 포함 검색 (추천)
        
        **2. 저널 필터 (Track A/B)**
        - **Track A (핵심 저널)**: 관광/호스피탈리티 분야 Q1 저널
        - **Track B (확장 저널)**: HRI, Robotics 등 관련 분야 저널
        
        **3. 결과 표시**
        - **High Priority**: 타겟 저널 + 키워드 매칭
        - **Medium Priority**: 맥락 + 기술 키워드 동시 매칭
        
        **4. 내보내기**
        - CSV: Excel, Google Sheets 호환
        - BibTeX: Zotero, Mendeley 호환
        """)
    
    # 저장된 프리셋 표시
    st.markdown("### 📌 저장된 연구 주제 프리셋")
    for name, data in RESEARCH_PRESETS.items():
        with st.expander(f"🔖 {name}"):
            st.markdown(f"**설명:** {data['description']}")
            st.markdown(f"**키워드:** {', '.join(data['keywords'])}")

# 푸터
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "📚 Research Paper Tracker | Powered by Semantic Scholar API"
    "</div>",
    unsafe_allow_html=True
)
