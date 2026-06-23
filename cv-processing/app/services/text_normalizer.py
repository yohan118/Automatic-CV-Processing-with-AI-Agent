"""
Text Normalization Service (Pipeline Step 6)
Kurdish Sorani text normalization with expanded stopword list.
"""

import re
import unicodedata


SORANI_STOPWORDS = {
    "و", "لە", "بۆ", "بە", "لەگەڵ", "تا", "هەتا", "کە", "ئەگەر",
    "یان", "یا", "نە", "بەبێ", "وەک", "تەنها", "لەسەر", "لەژێر",
    "لەنێوان", "لەپێش", "لەدوای", "لەبەر", "لەلایەن",
    "ئەو", "ئەم", "ئێمە", "ئەوان", "من", "تۆ",
    "بوو", "هەیە", "نییە", "دەبێت", "بووە", "کرد", "دەکات",
    "هەموو", "هیچ", "چەند", "یەک", "هەر", "زۆر", "کەم",
    "ئەوەی", "ئەمە", "ئەوە", "خۆ",
    "بەڵام", "چونکە", "بۆیە", "هەروەها", "هەروەک",
    "دوو", "سێ", "چوار", "پێنج", "شەش", "حەوت", "هەشت", "نۆ", "دە",
    "ساڵ", "مانگ", "ڕۆژ", "کات", "ئێستا", "دوا", "پێش",
    "توانا", "پێویست", "دەتوانێت", "بتوانێت",
    "ئەنجام", "شت", "لای", "ناو", "سەر", "ژێر", "پشت",
    "دا", "ەوە", "ەکان", "ەکە", "یەک", "ێک",
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can",
    "in", "on", "at", "to", "for", "with", "by", "from", "of",
    "and", "or", "but", "not", "no", "if", "then", "than",
    "this", "that", "these", "those", "it", "its",
    "i", "you", "he", "she", "we", "they", "me", "him", "her", "us", "them",
}

CHAR_NORMALIZATION = {
    "ي": "ی",
    "ك": "ک",
    "\u0649": "ی",
    "ؤ": "وو",
    "أ": "ئ",
    "إ": "ئ",
    "آ": "ئا",
    "\u200C": "",
    "\u200D": "",
    "\u200F": "",
    "\u200E": "",
}

DIACRITICS_PATTERN = re.compile(
    r'[\u064B-\u065F\u0670\u06D6-\u06ED\u08D4-\u08E1\u08E3-\u08FF]'
)


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def normalize_kurdish_chars(text: str) -> str:
    for old_char, new_char in CHAR_NORMALIZATION.items():
        text = text.replace(old_char, new_char)
    return text


def remove_diacritics(text: str) -> str:
    return DIACRITICS_PATTERN.sub("", text)


def normalize_whitespace(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()


def remove_punctuation(text: str) -> str:
    cleaned = re.sub(
        r'[^\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF'
        r'a-zA-Z0-9\s]',
        ' ',
        text
    )
    return normalize_whitespace(cleaned)


def remove_stopwords(text: str) -> str:
    words = text.split()
    filtered = [word for word in words if word not in SORANI_STOPWORDS and len(word) > 1]
    return " ".join(filtered)


def normalize_text(text: str, remove_stops: bool = True) -> str:
    if not text:
        return ""

    text = normalize_unicode(text)
    text = normalize_kurdish_chars(text)
    text = remove_diacritics(text)
    text = remove_punctuation(text)
    text = normalize_whitespace(text)

    if remove_stops:
        text = remove_stopwords(text)

    text = text.lower()
    return text
