"""
Keyword Extraction Service (Pipeline Step 7)
Uses TF-IDF to identify the most important words in a document.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Tuple
import json


def extract_keywords(text: str, top_n: int = 20) -> List[Tuple[str, float]]:
    if not text or not text.strip():
        return []

    segments = [s.strip() for s in text.split("\n") if s.strip()]

    if len(segments) < 2:
        words = text.split()
        chunk_size = max(5, len(words) // 5)
        segments = [
            " ".join(words[i:i + chunk_size])
            for i in range(0, len(words), chunk_size)
        ]

    if len(segments) < 2:
        words = text.split()
        total = len(words) if words else 1
        return [(w, 1.0 / total) for w in set(words)][:top_n]

    try:
        vectorizer = TfidfVectorizer(
            min_df=1,
            max_features=500,
            token_pattern=r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+'
                          r'|[a-zA-Z]+',
        )

        tfidf_matrix = vectorizer.fit_transform(segments)
        feature_names = vectorizer.get_feature_names_out()
        avg_scores = tfidf_matrix.mean(axis=0).A1

        word_scores = list(zip(feature_names, avg_scores))
        word_scores.sort(key=lambda x: x[1], reverse=True)

        return word_scores[:top_n]

    except Exception as e:
        words = list(set(text.split()))
        return [(w, 1.0) for w in words[:top_n]]


def find_matched_keywords(
    jd_keywords: List[Tuple[str, float]],
    cv_keywords: List[Tuple[str, float]]
) -> List[dict]:
    jd_dict = {word: score for word, score in jd_keywords}
    cv_dict = {word: score for word, score in cv_keywords}

    matched = []
    for word in jd_dict:
        if word in cv_dict:
            matched.append({
                "keyword": word,
                "jd_score": round(jd_dict[word], 4),
                "cv_score": round(cv_dict[word], 4),
                "combined_score": round((jd_dict[word] + cv_dict[word]) / 2, 4),
            })

    matched.sort(key=lambda x: x["combined_score"], reverse=True)
    return matched


def keywords_to_json(keywords: List[Tuple[str, float]]) -> str:
    return json.dumps(
        [{"keyword": k, "score": round(s, 4)} for k, s in keywords],
        ensure_ascii=False,
    )


def json_to_keywords(json_str: str) -> List[Tuple[str, float]]:
    if not json_str:
        return []
    try:
        data = json.loads(json_str)
        return [(item["keyword"], item["score"]) for item in data]
    except (json.JSONDecodeError, KeyError):
        return []
