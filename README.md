# 📚 Research Paper Tracker

Tourism & Physical AI 연구를 위한 학술 논문 검색 대시보드

## 주요 기능

### 🔍 스마트 검색
- **키워드 확장**: 동의어/관련어 자동 확장 (예: AI → Artificial Intelligence, Machine Learning, ...)
- **연구 주제 프리셋**: 자주 사용하는 검색어 조합 저장

### 📚 저널 필터링 (Track A/B 시스템)
- **Track A (핵심 저널)**: 관광/호스피탈리티 분야 Q1 저널 30개
  - Tourism Top 3: ATR, TM, JTR
  - Tourism & Hospitality Q1
  - IS & Tech
  - Business & Psychology
  - Urban & Smart City
  
- **Track B (확장 저널)**: HRI/Robotics 분야 Q1 저널
  - 관광 맥락 + 기술 키워드 동시 매칭 시에만 수집

### 📊 시각화
- 연도별 논문 수 추이
- Priority 분포
- 상위 인용 논문 Top 10
- 저널별 분포

### 💾 내보내기
- CSV (Excel, Google Sheets 호환)
- BibTeX (Zotero, Mendeley 호환)

## 설치 방법

### 1. 로컬 설치

```bash
# 저장소 클론 또는 파일 다운로드
cd paper-tracker

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 앱 실행
streamlit run app.py
```

### 2. Streamlit Cloud 배포

1. GitHub에 저장소 생성
2. 모든 파일 업로드
3. [Streamlit Cloud](https://share.streamlit.io/) 접속
4. "New app" → GitHub 저장소 연결
5. Main file: `app.py` 설정
6. Deploy!

## 파일 구조

```
paper-tracker/
├── app.py                 # 메인 Streamlit 앱
├── requirements.txt       # 의존성 패키지
├── README.md             # 이 파일
├── config/
│   ├── __init__.py
│   ├── journals.py       # 저널 설정 및 메타데이터
│   └── keywords.py       # 키워드 확장 사전
└── utils/
    ├── __init__.py
    ├── search.py         # Semantic Scholar API 검색
    └── export.py         # CSV/BibTeX 내보내기
```

## 커스터마이징

### 저널 추가/수정
`config/journals.py` 파일에서:
- `TARGET_JOURNALS`: 핵심 저널 카테고리
- `EXTENDED_JOURNALS`: 확장 저널 카테고리
- `JOURNAL_METADATA`: 저널별 IF, CiteScore 등

### 키워드 확장 사전 수정
`config/keywords.py` 파일에서:
- `KEYWORD_EXPANSIONS`: 동의어/관련어 매핑
- `RESEARCH_PRESETS`: 연구 주제 프리셋

## API 정보

- **Semantic Scholar API**: 무료, 인증 불필요
- Rate Limit: 100 requests/5분 (인증 시 더 높음)
- [API 문서](https://api.semanticscholar.org/)

## 향후 개발 계획

- [ ] OpenAlex API 추가 지원
- [ ] Snowballing 기능 (인용/피인용 논문 탐색)
- [ ] 키워드 빈도 분석 (Word Cloud)
- [ ] 이메일/Slack 알림 기능
- [ ] 저널 Q등급 자동 업데이트 (Scimago 연동)

## 라이선스

MIT License
