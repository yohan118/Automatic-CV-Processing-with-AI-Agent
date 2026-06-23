"""
Language Detection Service (Pipeline Step 4)
Detects English, Arabic, or Kurdish Sorani with custom Kurdish character rules.
"""

from langdetect import detect, DetectorFactory
import re

DetectorFactory.seed = 0

KURDISH_SPECIFIC_CHARS = set("ڕڵێۆڤگپچژکە")

KURDISH_COMMON_WORDS = {
    "لە", "بۆ", "لەگەڵ", "بە", "دەکات", "ئەم", "ئەو",
    "هەبوو", "کردن", "هەیە", "نییە", "دەبێت", "ئێمە",
    "ئەوان", "کە", "چونکە", "بەڵام", "هەروەها", "دوای",
    "پێش", "زۆر", "کەم", "باش", "خراپ", "نوێ", "کۆن",
    "زانکۆ", "بەرنامە", "کار", "کارمەند", "تەکنەلۆجیا",
    "بەڕێوەبردن", "پرۆژە", "کۆمپیوتەر", "داتا",
}


def _count_kurdish_chars(text: str) -> int:
    return sum(1 for char in text if char in KURDISH_SPECIFIC_CHARS)


def _count_kurdish_words(text: str) -> int:
    words = text.split()
    return sum(1 for word in words if word in KURDISH_COMMON_WORDS)


def _has_arabic_script(text: str) -> bool:
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]')
    return bool(arabic_pattern.search(text))


def detect_language(text: str) -> str:
    if not text or not text.strip():
        return "unknown"

    sample = text[:3000]

    kurdish_char_count = _count_kurdish_chars(sample)
    kurdish_word_count = _count_kurdish_words(sample)

    if kurdish_char_count >= 5 or kurdish_word_count >= 3:
        return "ckb"

    try:
        detected = detect(sample)
    except Exception:
        detected = "unknown"

    if detected == "en":
        return "en"

    if detected in ("ar", "fa", "ur"):
        if kurdish_char_count >= 2 or kurdish_word_count >= 1:
            return "ckb"
        if detected == "ar":
            return "ar"
        else:
            return "ckb"

    if _has_arabic_script(sample):
        return "ckb"

    return "en"


def get_language_name(code: str) -> str:
    names = {
        "en": "English",
        "ar": "Arabic",
        "ckb": "Kurdish Sorani",
        "unknown": "Unknown",
    }
    return names.get(code, f"Unknown ({code})")
