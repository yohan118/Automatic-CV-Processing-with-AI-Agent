"""
TF-IDF Matching Service (Pipeline Step 8)
Basic keyword matching using TF-IDF + Cosine Similarity.
Works alongside semantic_matcher.py which adds synonym understanding.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple


def calculate_similarity(jd_text: str, cv_text: str) -> float:
    if not jd_text or not cv_text:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            token_pattern=r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+'
                          r'|[a-zA-Z]+',
            min_df=1,
            max_features=1000,
        )

        tfidf_matrix = vectorizer.fit_transform([jd_text, cv_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

        return max(0.0, min(1.0, float(similarity[0][0])))

    except Exception as e:
        return 0.0


def rank_cvs(jd_text: str, cv_texts: List[Tuple[int, str]]) -> List[Tuple[int, float]]:
    if not jd_text or not cv_texts:
        return []

    try:
        corpus = [jd_text] + [text for _, text in cv_texts]
        cv_ids = [cv_id for cv_id, _ in cv_texts]

        vectorizer = TfidfVectorizer(
            token_pattern=r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+'
                          r'|[a-zA-Z]+',
            min_df=1,
            max_features=1000,
        )

        tfidf_matrix = vectorizer.fit_transform(corpus)
        jd_vector = tfidf_matrix[0:1]
        cv_vectors = tfidf_matrix[1:]

        similarities = cosine_similarity(jd_vector, cv_vectors).flatten()
        results = list(zip(cv_ids, [float(s) for s in similarities]))
        results.sort(key=lambda x: x[1], reverse=True)

        return results

    except Exception as e:
        return [(cv_id, 0.0) for cv_id, _ in cv_texts]


def get_similarity_label(score: float) -> str:
    if score >= 0.7:
        return "Excellent Match"
    elif score >= 0.5:
        return "Good Match"
    elif score >= 0.3:
        return "Fair Match"
    elif score >= 0.15:
        return "Weak Match"
    else:
        return "Poor Match"
