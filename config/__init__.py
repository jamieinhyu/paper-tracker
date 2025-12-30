# config/__init__.py
from .journals import (
    TARGET_JOURNALS,
    EXTENDED_JOURNALS,
    JOURNAL_METADATA,
    get_all_target_journals,
    get_all_extended_journals,
    get_journal_metadata,
    is_target_journal
)

from .keywords import (
    KEYWORD_EXPANSIONS,
    RESEARCH_PRESETS,
    CONTEXT_KEYWORDS,
    expand_keywords,
    get_all_expanded_terms,
    build_search_query
)
