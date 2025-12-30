# config/keywords.py
# 키워드 확장 사전 및 프리셋

# 동의어/관련어 사전 (규칙 기반 확장)
KEYWORD_EXPANSIONS = {
    # AI & Technology
    "AI": ["Artificial Intelligence", "Machine Learning", "Deep Learning", "Generative AI", "LLM", "Large Language Model"],
    "Physical AI": ["Embodied AI", "Embodied Artificial Intelligence", "Robotic AI", "Physical Intelligence"],
    "ChatGPT": ["GPT", "Large Language Model", "LLM", "Generative AI", "Conversational AI"],
    "Robot": ["Robotics", "Robotic", "Service Robot", "Social Robot", "Humanoid"],
    "Social Robot": ["Service Robot", "Companion Robot", "Hospitality Robot", "Robot Concierge"],
    
    # Social Media
    "SNS": ["Social Media", "Social Networking Sites", "Social Network"],
    "Social Media": ["Instagram", "TikTok", "YouTube", "Facebook", "Twitter", "Online Platform"],
    
    # Tourism & Hospitality
    "Tourism": ["Travel", "Tourist", "Traveler", "Destination", "Visitor"],
    "Hospitality": ["Hotel", "Accommodation", "Restaurant", "Service Industry"],
    "Smart Tourism": ["e-Tourism", "Digital Tourism", "ICT Tourism", "Technology Tourism"],
    "Tourist Experience": ["Visitor Experience", "Travel Experience", "Tourism Experience", "Customer Experience"],
    
    # HRI & Interaction
    "HRI": ["Human-Robot Interaction", "Human Robot Interaction", "Robot Interaction"],
    "HCI": ["Human-Computer Interaction", "Human Computer Interaction", "User Interaction"],
    
    # Experience & Psychology
    "UX": ["User Experience", "Customer Experience", "Experience Design"],
    "Satisfaction": ["Customer Satisfaction", "Tourist Satisfaction", "Service Satisfaction"],
    "Trust": ["Technology Trust", "Robot Trust", "AI Trust", "Human-Robot Trust"],
    "Acceptance": ["Technology Acceptance", "Robot Acceptance", "TAM", "UTAUT"],
    
    # Emerging Concepts
    "Phygital": ["Physical-Digital", "Hybrid Experience", "Blended Reality"],
    "Metaverse": ["Virtual World", "Virtual Reality", "VR Tourism", "Virtual Tourism"],
    "AR": ["Augmented Reality", "Mixed Reality", "XR"],
    "VR": ["Virtual Reality", "Immersive Technology", "Virtual Environment"],
}

# 연구 주제 프리셋
RESEARCH_PRESETS = {
    "Social Robots in Tourism": {
        "keywords": ["Social Robot", "Tourism", "Hospitality"],
        "description": "관광/호스피탈리티 분야의 소셜 로봇 연구"
    },
    "Physical AI & Hospitality": {
        "keywords": ["Physical AI", "Robot", "Hospitality", "Service"],
        "description": "호스피탈리티 산업에서의 Physical AI 적용"
    },
    "Smart Tourism Technology": {
        "keywords": ["Smart Tourism", "AI", "Digital", "Technology"],
        "description": "스마트 관광 기술 연구"
    },
    "Tourist Experience & Technology": {
        "keywords": ["Tourist Experience", "Technology", "Digital"],
        "description": "기술 매개 관광 경험 연구"
    },
    "Human-Robot Interaction in Service": {
        "keywords": ["HRI", "Service Robot", "Customer", "Experience"],
        "description": "서비스 분야 인간-로봇 상호작용"
    },
    "AI Acceptance in Tourism": {
        "keywords": ["AI", "Acceptance", "Tourism", "Trust"],
        "description": "관광 분야 AI 수용 연구"
    }
}

# 맥락 키워드 (Track B 엄격한 매칭용)
CONTEXT_KEYWORDS = [
    "tourism", "travel", "hospitality", "hotel", "tourist", 
    "traveler", "visitor", "destination", "leisure", "recreation",
    "vacation", "accommodation", "resort", "airline", "cruise"
]

def expand_keywords(keywords: list, include_original: bool = True) -> dict:
    """
    키워드 리스트를 확장하여 반환
    
    Args:
        keywords: 원본 키워드 리스트
        include_original: 원본 키워드 포함 여부
        
    Returns:
        {원본키워드: [확장키워드들]} 형태의 딕셔너리
    """
    expanded = {}
    for keyword in keywords:
        expansions = KEYWORD_EXPANSIONS.get(keyword, [])
        if include_original:
            expanded[keyword] = [keyword] + expansions
        else:
            expanded[keyword] = expansions
    return expanded

def get_all_expanded_terms(keywords: list) -> list:
    """모든 확장된 키워드를 flat 리스트로 반환"""
    expanded = expand_keywords(keywords)
    all_terms = []
    for terms in expanded.values():
        all_terms.extend(terms)
    return list(set(all_terms))

def build_search_query(keywords: list, use_expansion: bool = True) -> str:
    """
    검색 쿼리 문자열 생성
    
    Args:
        keywords: 원본 키워드 리스트
        use_expansion: 확장 사용 여부
        
    Returns:
        OR로 연결된 검색 쿼리 문자열
    """
    if use_expansion:
        all_terms = get_all_expanded_terms(keywords)
    else:
        all_terms = keywords
    
    return " OR ".join([f'"{term}"' for term in all_terms])
