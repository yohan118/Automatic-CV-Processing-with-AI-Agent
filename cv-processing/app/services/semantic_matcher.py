"""
Semantic Matching Service (NEW in v2)
Adds meaning-based understanding on top of TF-IDF keyword matching.

The problem with plain TF-IDF:
- "programmer" and "developer" are treated as completely different words
- "built websites" and "web development" have zero similarity
- Technical synonyms are missed entirely

Our solution — Synonym-Enhanced Matching:
1. Build a synonym dictionary for common technical and Kurdish terms
2. Before matching, expand both JD and CV text with synonyms
3. Calculate similarity on the expanded text
4. Combine TF-IDF score with synonym-enhanced score

This approach is practical for a BSc project because:
- No external models or training data needed
- The synonym dictionary is transparent and explainable
- It measurably improves matching accuracy
- It can be extended by simply adding more synonyms
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict, Set
import re


# Technical synonym groups
# Each group contains words/phrases that mean the same thing
# When any word from a group appears, all words in the group are added
SYNONYM_GROUPS = [
    # Programming roles
    {"programmer", "developer", "coder", "engineer", "software engineer",
     "پرۆگرامەر", "گەشەپێدەر", "ئەندازیار"},

    # Web development
    {"web developer", "frontend developer", "web programmer", "web designer",
     "پرۆگرامەری وێب", "گەشەپێدەری وێب"},

    # Backend
    {"backend", "server-side", "backend developer",
     "باکئێند", "لای سێرڤەر"},

    # Database
    {"database", "db", "data storage", "data management",
     "داتابەیس", "بنکەی داتا", "بنکەداتا"},

    # Project management
    {"project management", "project manager", "team lead",
     "بەڕێوەبردنی پرۆژە", "سەرپەرشتیاری پرۆژە"},

    # Design
    {"design", "ui design", "ux design", "user interface", "graphic design",
     "دیزاین", "دیزاینکردن", "ڕووکاری بەکارهێنەر"},

    # Experience
    {"experience", "work experience", "professional experience",
     "ئەزموون", "ئەزموونی کار", "شارەزایی"},

    # Education
    {"education", "academic", "university", "college", "degree",
     "خوێندن", "زانکۆ", "بڕوانامە"},

    # Bachelor
    {"bachelor", "bsc", "ba", "undergraduate",
     "بەکالۆریۆس", "بکالۆریۆس"},

    # Master
    {"master", "msc", "ma", "graduate", "postgraduate",
     "ماستەر", "ماجستێر"},

    # Skills
    {"skills", "competencies", "abilities", "expertise",
     "لێهاتوویی", "تواناکان", "شارەزایی"},

    # Teamwork
    {"teamwork", "team player", "collaboration", "cooperative",
     "کارکردن بە تیم", "هاوکاری"},

    # Problem solving
    {"problem solving", "analytical", "troubleshooting", "debugging",
     "چارەسەرکردنی کێشە", "شیکاری"},

    # Communication
    {"communication", "interpersonal", "presentation",
     "پەیوەندی", "تێکەیشتن", "ئاخاوتن"},

    # Management
    {"management", "leadership", "supervision", "administration",
     "بەڕێوەبردن", "سەرکردایەتی", "سەرپەرشتی"},

    # Data / Analysis
    {"data analysis", "data science", "analytics", "reporting",
     "شیکاری داتا", "زانستی داتا"},

    # API
    {"api", "rest api", "restful", "web service", "web api",
     "ئەی پی ئای"},

    # Testing
    {"testing", "qa", "quality assurance", "unit testing",
     "تاقیکردنەوە", "دڵنیایی کوالیتی"},

    # Cloud
    {"cloud", "cloud computing", "aws", "azure", "gcp",
     "کلاود", "هەور"},

    # Mobile
    {"mobile development", "android", "ios", "mobile app",
     "گەشەپێدانی مۆبایل", "بەرنامەی مۆبایل"},

    # Machine learning
    {"machine learning", "artificial intelligence", "ai", "ml", "deep learning",
     "فێربوونی مەکینە", "زیرەکی دەستکرد"},

    # Security
    {"security", "cybersecurity", "information security",
     "ئاسایش", "پاراستنی زانیاری"},

    # Network
    {"networking", "network administration", "network engineer",
     "تۆڕ", "بەڕێوەبردنی تۆڕ"},

    # Operating systems
    {"operating system", "os", "system administration",
     "سیستەمی کارپێکردن"},

    # Version control
    {"version control", "git", "source control",
     "بەڕێوەبردنی کۆد", "کۆنتڕۆڵی وەشان"},
]


def _build_synonym_lookup() -> Dict[str, Set[str]]:
    """
    Build a lookup dictionary: word -> set of all its synonyms.
    This runs once and is cached for performance.
    """
    lookup = {}
    for group in SYNONYM_GROUPS:
        for word in group:
            word_lower = word.lower()
            if word_lower not in lookup:
                lookup[word_lower] = set()
            for synonym in group:
                if synonym.lower() != word_lower:
                    lookup[word_lower].add(synonym.lower())
    return lookup


# Build the lookup once at module load time
_SYNONYM_LOOKUP = _build_synonym_lookup()


def expand_with_synonyms(text: str) -> str:
    """
    Expand text by adding synonyms of recognized terms.

    For example, if text contains "programmer", this adds "developer"
    and "coder" to the text. This way, when TF-IDF compares the expanded
    JD against the expanded CV, words with similar meaning will match.
    """
    words = text.lower().split()
    expanded_words = list(words)

    # Single word synonyms
    for word in words:
        if word in _SYNONYM_LOOKUP:
            for synonym in _SYNONYM_LOOKUP[word]:
                if " " not in synonym:
                    expanded_words.append(synonym)

    # Two-word phrase synonyms
    for i in range(len(words) - 1):
        phrase = words[i] + " " + words[i + 1]
        if phrase in _SYNONYM_LOOKUP:
            for synonym in _SYNONYM_LOOKUP[phrase]:
                expanded_words.extend(synonym.split())

    return " ".join(expanded_words)


def calculate_semantic_similarity(jd_text: str, cv_text: str) -> float:
    """
    Calculate similarity using synonym-expanded texts.

    Steps:
    1. Expand both texts with synonyms
    2. Build TF-IDF vectors from expanded texts
    3. Calculate cosine similarity
    """
    if not jd_text or not cv_text:
        return 0.0

    try:
        expanded_jd = expand_with_synonyms(jd_text)
        expanded_cv = expand_with_synonyms(cv_text)

        vectorizer = TfidfVectorizer(
            token_pattern=r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+'
                          r'|[a-zA-Z]+',
            min_df=1,
            max_features=1500,
        )

        tfidf_matrix = vectorizer.fit_transform([expanded_jd, expanded_cv])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

        return max(0.0, min(1.0, float(similarity[0][0])))

    except Exception as e:
        print(f"Semantic similarity error: {e}")
        return 0.0


def calculate_combined_score(
    tfidf_score: float,
    semantic_score: float,
    tfidf_weight: float = 0.4,
    semantic_weight: float = 0.6,
) -> float:
    """
    Combine TF-IDF and semantic similarity scores.

    The semantic score gets higher weight because it captures meaning,
    not just exact word matches. The weights are configurable.

    Default: 40% TF-IDF + 60% Semantic = Combined Score
    """
    combined = (tfidf_score * tfidf_weight) + (semantic_score * semantic_weight)
    return max(0.0, min(1.0, combined))
