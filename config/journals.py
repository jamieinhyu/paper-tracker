# config/journals.py
# 핵심 타겟 저널 및 메타데이터

TARGET_JOURNALS = {
    "Tourism_Top3": {
        "description": "관광학 최상위 저널",
        "journals": [
            "Annals of Tourism Research",
            "Tourism Management", 
            "Journal of Travel Research"
        ]
    },
    "Tourism_Hospitality": {
        "description": "관광/호스피탈리티 Q1",
        "journals": [
            "Journal of Travel & Tourism Marketing",
            "Current Issues in Tourism",
            "Journal of Hospitality Marketing & Management",
            "Journal of Sustainable Tourism",
            "Asia Pacific Journal of Tourism Research",
            "Tourism Management Perspectives",
            "Journal of Hospitality and Tourism Management",
            "International Journal of Hospitality Management",
            "International Journal of Tourism Research",
            "Journal of Hospitality & Tourism Research",
            "International Journal of Contemporary Hospitality Management",
            "Journal of Hospitality and Tourism Technology",
            "Information Technology & Tourism"
        ]
    },
    "IS_Tech": {
        "description": "정보시스템/기술 Q1",
        "journals": [
            "International Journal of Information Management",
            "Information Systems Frontiers",
            "Information Systems Research",
            "Journal of Management Information Systems",
            "The Journal of Strategic Information Systems"
        ]
    },
    "Business_Psychology": {
        "description": "경영/심리/마케팅 Q1",
        "journals": [
            "Journal of Business Research",
            "Business Strategy and the Environment",
            "Computers in Human Behavior",
            "Journal of Retailing and Consumer Services",
            "Journal of Marketing"
        ]
    },
    "Urban_SmartCity": {
        "description": "스마트시티/도시계획 Q1",
        "journals": [
            "Sustainable Cities and Society",
            "Cities",
            "Computers, Environment and Urban Systems",
            "Journal of Transport Geography"
        ]
    }
}

# 확장 저널 (Track B) - HRI/Robotics 특화
EXTENDED_JOURNALS = {
    "HRI_Robotics": {
        "description": "HCI/로보틱스 Q1 (Physical AI 관련)",
        "journals": [
            "International Journal of Social Robotics",
            "ACM Transactions on Human-Robot Interaction",
            "IEEE Robotics and Automation Letters",
            "Human-Computer Interaction",
            "International Journal of Human-Computer Studies",
            "AI & Society",
            "Robotics and Autonomous Systems"
        ]
    },
    "Service_Experience": {
        "description": "서비스/경험 연구",
        "journals": [
            "Journal of Service Research",
            "Journal of Service Management",
            "Journal of Consumer Psychology"
        ]
    }
}

# 저널 메타데이터 (IF, CiteScore 등)
JOURNAL_METADATA = {
    "Annals of Tourism Research": {"IF": 7.8, "CiteScore": 16.2, "category": "Tourism", "tier": "Top3"},
    "Tourism Management": {"IF": 12.4, "CiteScore": 26.5, "category": "Tourism", "tier": "Top3"},
    "Journal of Travel Research": {"IF": 7.0, "CiteScore": None, "category": "Tourism", "tier": "Top3"},
    "Journal of Travel & Tourism Marketing": {"IF": 9.0, "CiteScore": 13.8, "category": "Tourism", "tier": "Q1"},
    "Current Issues in Tourism": {"IF": 4.6, "CiteScore": 15.5, "category": "Tourism", "tier": "Q1"},
    "Journal of Hospitality Marketing & Management": {"IF": 11.0, "CiteScore": 21.8, "category": "Hospitality", "tier": "Q1"},
    "Journal of Sustainable Tourism": {"IF": 7.8, "CiteScore": 20.4, "category": "Tourism", "tier": "Q1"},
    "Asia Pacific Journal of Tourism Research": {"IF": 3.3, "CiteScore": 7.2, "category": "Tourism", "tier": "Q1"},
    "Tourism Management Perspectives": {"IF": 6.9, "CiteScore": 14.9, "category": "Tourism", "tier": "Q1"},
    "Journal of Hospitality and Tourism Management": {"IF": 7.8, "CiteScore": 14.9, "category": "Tourism & Hospitality", "tier": "Q1"},
    "International Journal of Hospitality Management": {"IF": 8.3, "CiteScore": 20.7, "category": "Hospitality", "tier": "Q1"},
    "International Journal of Tourism Research": {"IF": 5.7, "CiteScore": 7.9, "category": "Tourism", "tier": "Q1"},
    "Journal of Hospitality & Tourism Research": {"IF": 5.3, "CiteScore": None, "category": "Tourism & Hospitality", "tier": "Q1"},
    "International Journal of Contemporary Hospitality Management": {"IF": 9.0, "CiteScore": 18.2, "category": "Hospitality", "tier": "Q1"},
    "Journal of Hospitality and Tourism Technology": {"IF": 6.9, "CiteScore": 10.3, "category": "Tourism & Hospitality", "tier": "Q1"},
    "Information Technology & Tourism": {"IF": 7.0, "CiteScore": None, "category": "Tourism", "tier": "Q1"},
    "International Journal of Information Management": {"IF": 27.0, "CiteScore": 54.9, "category": "Information", "tier": "Q1"},
    "Information Systems Frontiers": {"IF": 8.3, "CiteScore": 19.1, "category": "Information", "tier": "Q1"},
    "Information Systems Research": {"IF": 5.1, "CiteScore": None, "category": "Information", "tier": "Q1"},
    "Journal of Management Information Systems": {"IF": 6.2, "CiteScore": 11.3, "category": "Information", "tier": "Q1"},
    "The Journal of Strategic Information Systems": {"IF": 11.8, "CiteScore": 17.9, "category": "Information", "tier": "Q1"},
    "Journal of Business Research": {"IF": 9.8, "CiteScore": 25.3, "category": "Business", "tier": "Q1"},
    "Business Strategy and the Environment": {"IF": 13.3, "CiteScore": 23.7, "category": "Business", "tier": "Q1"},
    "Computers in Human Behavior": {"IF": 8.9, "CiteScore": 20.7, "category": "Psychology", "tier": "Q1"},
    "Journal of Retailing and Consumer Services": {"IF": 13.1, "CiteScore": 22.7, "category": "Business", "tier": "Q1"},
    "Journal of Marketing": {"IF": 10.4, "CiteScore": 28.0, "category": "Business", "tier": "Q1"},
    "Sustainable Cities and Society": {"IF": 12.0, "CiteScore": 22.4, "category": "Urban Planning", "tier": "Q1"},
    "Cities": {"IF": 6.6, "CiteScore": 10.9, "category": "Urban Planning", "tier": "Q1"},
    "Computers, Environment and Urban Systems": {"IF": 8.3, "CiteScore": 16.6, "category": "Urban Planning", "tier": "Q1"},
    "Journal of Transport Geography": {"IF": 6.3, "CiteScore": 11.2, "category": "Urban Planning", "tier": "Q1"},
    # Extended journals
    "International Journal of Social Robotics": {"IF": 4.7, "CiteScore": 8.5, "category": "HRI/Robotics", "tier": "Q1"},
    "Human-Computer Interaction": {"IF": 4.5, "CiteScore": 7.8, "category": "HCI", "tier": "Q1"},
    "International Journal of Human-Computer Studies": {"IF": 5.4, "CiteScore": 10.2, "category": "HCI", "tier": "Q1"},
    "AI & Society": {"IF": 3.2, "CiteScore": 5.8, "category": "AI", "tier": "Q1"},
}

def get_all_target_journals():
    """모든 타겟 저널 리스트 반환"""
    all_journals = []
    for category in TARGET_JOURNALS.values():
        all_journals.extend(category["journals"])
    return all_journals

def get_all_extended_journals():
    """모든 확장 저널 리스트 반환"""
    all_journals = []
    for category in EXTENDED_JOURNALS.values():
        all_journals.extend(category["journals"])
    return all_journals

def get_journal_metadata(journal_name):
    """저널 메타데이터 반환"""
    return JOURNAL_METADATA.get(journal_name, {"IF": None, "CiteScore": None, "category": "Unknown", "tier": "Unknown"})

def is_target_journal(journal_name):
    """타겟 저널 여부 확인"""
    return journal_name in get_all_target_journals()
