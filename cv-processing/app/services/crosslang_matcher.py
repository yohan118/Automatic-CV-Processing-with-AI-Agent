"""
Cross-Language Matcher (NEW in v5)
Scores CVs against job descriptions using the trilingual dictionary,
WITHOUT relying on machine translation for ranking.

How it works:
1. Scan the JD text (Kurdish Sorani) and find all dictionary terms present
2. Scan the CV text (any language) and find all dictionary terms present
3. For each JD term group found, check if the CV also has a term from the same group
4. The score = matched groups / total JD groups

This gives accurate cross-language matching because:
- "python" in an English CV matches "پایتۆن" in a Kurdish JD
- "بكالوريوس" in an Arabic CV matches "بەکالۆریۆس" in a Kurdish JD
- Technical terms like "React", "Docker" match regardless of language

The score is combined with the existing TF-IDF score for final ranking.
"""

import re
from typing import List, Dict, Set, Tuple
from app.services.trilingual_dict import (
    DICTIONARY, TermGroup, find_groups_for_term, get_all_groups
)


def _extract_words(text: str) -> List[str]:
    """
    Extract words from text, handling both Latin and Arabic script.
    Returns lowercase words.
    """
    if not text:
        return []
    
    # Split on whitespace and common separators
    # Keep multi-word terms by also checking bigrams and trigrams
    words = re.findall(r'[a-zA-Z0-9#+.]+|[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+', text)
    return [w.lower() for w in words if len(w) > 1]


def _find_matching_groups(text: str) -> Dict[int, Dict]:
    """
    Scan text and find all dictionary term groups that have a match.
    Returns dict of {group_index: {"term": matched_term, "group": TermGroup}}
    
    Checks single words, bigrams, and trigrams to catch multi-word terms
    like "machine learning", "بنکەی داتا", etc.
    """
    if not text:
        return {}
    
    found = {}
    words = _extract_words(text)
    text_lower = text.lower()
    
    # Check each dictionary group against the text
    for idx, group in enumerate(DICTIONARY):
        if idx in found:
            continue
            
        for term in group.all_terms:
            term_lower = term.lower()
            
            # For single-word terms, check word list
            if ' ' not in term_lower and '/' not in term_lower:
                if term_lower in words:
                    found[idx] = {"term": term, "group": group}
                    break
            else:
                # For multi-word terms, check if they appear in the text
                if term_lower in text_lower:
                    found[idx] = {"term": term, "group": group}
                    break
    
    return found


def calculate_crosslang_score(jd_text: str, cv_text: str) -> Tuple[float, List[Dict]]:
    """
    Calculate cross-language matching score between JD and CV.
    
    Args:
        jd_text: Job description text (typically Kurdish Sorani)
        cv_text: CV raw text (any language — English, Arabic, or Kurdish)
    
    Returns:
        (score, matched_details)
        - score: float 0.0 to 1.0
        - matched_details: list of matched term group info for display
    """
    # Find groups present in JD
    jd_groups = _find_matching_groups(jd_text)
    
    if not jd_groups:
        return 0.0, []
    
    # Find groups present in CV
    cv_groups = _find_matching_groups(cv_text)
    
    # Find intersection — groups present in BOTH
    matched_indices = set(jd_groups.keys()) & set(cv_groups.keys())
    
    if not matched_indices:
        return 0.0, []
    
    # Build match details for display
    matched_details = []
    for idx in matched_indices:
        jd_info = jd_groups[idx]
        cv_info = cv_groups[idx]
        group = jd_info["group"]
        
        matched_details.append({
            "keyword": jd_info["term"],  # The JD term (Kurdish)
            "cv_term": cv_info["term"],   # The CV term (whatever language)
            "category": group.category,
            "combined_score": 1.0,  # Full match — same concept
        })
    
    # Score = matched / total JD groups
    score = len(matched_indices) / len(jd_groups)
    
    # Cap at 1.0
    score = min(score, 1.0)
    
    # Sort matched details by category for clean display
    matched_details.sort(key=lambda x: x["category"])
    
    return score, matched_details


def calculate_v5_combined_score(
    tfidf_score: float,
    crosslang_score: float,
) -> float:
    """
    Calculate the final combined score for v5.
    
    Weights:
    - Cross-language dictionary match: 70% (deterministic, accurate)
    - TF-IDF on normalized text: 30% (catches terms not in dictionary)
    
    Cross-language gets higher weight because it's reliable and precise.
    TF-IDF still contributes because it catches domain-specific terms
    that might not be in our dictionary.
    """
    WEIGHT_CROSSLANG = 0.70
    WEIGHT_TFIDF = 0.30
    
    combined = (crosslang_score * WEIGHT_CROSSLANG) + (tfidf_score * WEIGHT_TFIDF)
    
    return min(combined, 1.0)


def get_dictionary_stats() -> Dict:
    """Return stats about the dictionary for the UI/API."""
    categories = {}
    for g in DICTIONARY:
        cat = g.category or "uncategorized"
        categories[cat] = categories.get(cat, 0) + 1
    
    total_terms = sum(len(g.all_terms) for g in DICTIONARY)
    
    return {
        "total_groups": len(DICTIONARY),
        "total_terms": total_terms,
        "categories": categories,
    }
