"""
Kurdish Sorani Spell Checker (NEW in v3)
Provides basic spell-checking and correction for Kurdish Sorani text.

Approach:
- Maintains a dictionary of common Kurdish words and technical terms
- Checks each word against the dictionary
- Suggests corrections using edit distance (Levenshtein)
- Handles common Kurdish character confusions

This is a rule-based approach suitable for a BSc project.
A production system would use a trained language model.
"""

import re
from typing import List, Tuple, Optional, Dict

# Common Kurdish Sorani words dictionary
# Organized by category for maintainability
KURDISH_DICTIONARY = set()

# Common verbs
KURDISH_DICTIONARY.update({
    "کردن", "کرد", "دەکات", "دەکەم", "دەکەن", "دەکەیت",
    "بوون", "بوو", "دەبێت", "بووە", "بووم", "نەبوو",
    "هاتن", "هات", "دێت", "دێم", "دێن", "دێیت",
    "چوون", "چوو", "دەچێت", "دەچم", "دەچن",
    "کارکردن", "کارکرد", "کاردەکات",
    "وتن", "وت", "دەڵێت", "دەڵێم",
    "زانین", "زانی", "دەزانێت", "دەزانم",
    "توانین", "توانی", "دەتوانێت", "دەتوانم",
    "دیتن", "دیت", "دەبینێت", "دەبینم",
    "خوێندن", "خوێند", "دەخوێنێت",
    "نووسین", "نووسی", "دەنووسێت",
    "گەڕان", "گەڕا", "دەگەڕێت",
    "دروستکردن", "دروستکرد", "دروستدەکات",
    "بەکارهێنان", "بەکارهێنا", "بەکاردەهێنێت",
    "بەڕێوەبردن", "بەڕێوەبرد", "بەڕێوەدەبات",
    "چارەسەرکردن", "چارەسەرکرد",
    "گەشەپێدان", "گەشەپێدا",
    "دیزاینکردن", "دیزاینکرد",
    "هەڵبژاردن", "هەڵبژارد",
    "پشتگیریکردن", "پشتگیریکرد",
    "تاقیکردنەوە", "تاقیکردەوە",
})

# Common nouns
KURDISH_DICTIONARY.update({
    "کار", "کارمەند", "کۆمپانیا", "شوێن", "شار", "وڵات",
    "زانکۆ", "خوێندنگا", "قوتابی", "مامۆستا", "بەڕێوەبەر",
    "پرۆژە", "بەرنامە", "سیستەم", "تەکنەلۆجیا", "کۆمپیوتەر",
    "داتا", "زانیاری", "زمان", "وشە", "دەق", "پەڕە",
    "تیم", "گروپ", "دەستە", "ئەندام", "سەرۆک",
    "ئەزموون", "شارەزایی", "لێهاتوویی", "توانا",
    "بڕوانامە", "بەکالۆریۆس", "ماستەر", "دکتۆرا",
    "خزمەتگوزاری", "بازاڕ", "فرۆشتن", "بەرهەم",
    "ماڵپەڕ", "ڕووکار", "بنکەی", "سێرڤەر", "تۆڕ",
    "ئینتەرنێت", "نەرمەکاڵا", "ڕەقەکاڵا", "ئامێر",
    "کتێبخانە", "چوارچێوە", "ئالگۆریزم", "فایل",
    "وێنە", "ڤیدیۆ", "دەنگ", "پەیام",
    "ئیمەیل", "ژمارە", "ناونیشان", "مۆبایل",
    "کێشە", "چارەسەر", "پلان", "ئامانج",
    "ڕاپۆرت", "ئەنجام", "شیکاری", "لێکۆڵینەوە",
    "وەسف", "پێویستی", "مەرج", "قەبارە",
    "کات", "ساڵ", "مانگ", "ڕۆژ", "هەفتە",
    "پارە", "بودجە", "موچە", "داهات",
    "ئاسایش", "پاراستن", "پاسوۆرد",
})

# Adjectives and adverbs
KURDISH_DICTIONARY.update({
    "باش", "خراپ", "زۆر", "کەم", "نوێ", "کۆن",
    "گەورە", "بچووک", "درێژ", "کورت", "بەرز", "نزم",
    "گرنگ", "سەرەکی", "تایبەت", "گشتی",
    "پێویست", "ئامادە", "تەواو", "نوێ",
    "هەموو", "هیچ", "چەند", "یەک",
    "باشتر", "باشترین", "زیاتر", "کەمتر",
    "پیشەیی", "تەکنیکی", "ئەکادیمی",
})

# Prepositions and conjunctions
KURDISH_DICTIONARY.update({
    "لە", "بۆ", "بە", "لەگەڵ", "تا", "هەتا",
    "کە", "ئەگەر", "یان", "و", "بەڵام", "چونکە",
    "بۆیە", "هەروەها", "لەسەر", "لەژێر",
    "لەنێوان", "لەپێش", "لەدوای", "لەبەر",
    "لەلایەن", "بەبێ", "وەک", "تەنها",
})

# Pronouns
KURDISH_DICTIONARY.update({
    "من", "تۆ", "ئەو", "ئێمە", "ئێوە", "ئەوان",
    "ئەم", "ئەوە", "ئەمە", "خۆ", "خۆم", "خۆت",
})

# Numbers in Kurdish
KURDISH_DICTIONARY.update({
    "یەک", "دوو", "سێ", "چوار", "پێنج",
    "شەش", "حەوت", "هەشت", "نۆ", "دە",
    "بیست", "سی", "چل", "پەنجا", "شەست",
    "حەفتا", "هەشتا", "نەوەد", "سەد", "هەزار",
})

# Common character confusion pairs in Kurdish
# When someone types the wrong character, we suggest the right one
CHAR_CONFUSIONS = {
    "ي": "ی",
    "ك": "ک",
    "ه": "ە",
    "ة": "ە",
    "ؤ": "و",
}


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    prev_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]


def _normalize_for_check(word: str) -> str:
    """Normalize a word for dictionary lookup."""
    for wrong, right in CHAR_CONFUSIONS.items():
        word = word.replace(wrong, right)
    return word


def _has_kurdish_chars(word: str) -> bool:
    """Check if a word contains Arabic/Kurdish script."""
    return bool(re.search(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]', word))


def _find_suggestions(word: str, max_distance: int = 2, max_results: int = 3) -> List[str]:
    """Find dictionary words within edit distance of the given word."""
    suggestions = []

    normalized = _normalize_for_check(word)
    if normalized in KURDISH_DICTIONARY:
        return [normalized]

    for dict_word in KURDISH_DICTIONARY:
        if abs(len(dict_word) - len(word)) > max_distance:
            continue

        dist = _levenshtein_distance(word, dict_word)
        if 0 < dist <= max_distance:
            suggestions.append((dict_word, dist))

    suggestions.sort(key=lambda x: x[1])
    return [s[0] for s in suggestions[:max_results]]


class SpellCheckResult:
    def __init__(self):
        self.original_text: str = ""
        self.corrected_text: str = ""
        self.corrections: List[Dict] = []
        self.total_words: int = 0
        self.misspelled_count: int = 0
        self.auto_corrected_count: int = 0

    def to_dict(self) -> dict:
        return {
            "original_text": self.original_text[:200],
            "corrected_text": self.corrected_text[:200],
            "total_words": self.total_words,
            "misspelled_count": self.misspelled_count,
            "auto_corrected_count": self.auto_corrected_count,
            "corrections": self.corrections[:30],
        }


def check_and_correct(text: str) -> SpellCheckResult:
    """
    Check Kurdish Sorani text for spelling errors and apply corrections.

    The checker:
    1. Splits text into words
    2. Skips non-Kurdish words (English terms, numbers)
    3. Normalizes common character confusions (ي -> ی, ك -> ک)
    4. Checks against the dictionary
    5. Suggests corrections using edit distance

    Auto-corrects when:
    - Only character normalization is needed (high confidence)
    - There is exactly one suggestion with distance 1

    Flags without correcting when:
    - Multiple suggestions exist
    - Edit distance is 2 or more
    """
    result = SpellCheckResult()
    result.original_text = text

    if not text or not text.strip():
        result.corrected_text = text
        return result

    words = text.split()
    result.total_words = len(words)
    corrected_words = []

    for word in words:
        clean = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]', '', word)

        if not clean or not _has_kurdish_chars(clean) or len(clean) <= 1:
            corrected_words.append(word)
            continue

        if clean in KURDISH_DICTIONARY:
            corrected_words.append(word)
            continue

        normalized = _normalize_for_check(clean)
        if normalized != clean and normalized in KURDISH_DICTIONARY:
            corrected_word = word
            for wrong, right in CHAR_CONFUSIONS.items():
                corrected_word = corrected_word.replace(wrong, right)

            corrected_words.append(corrected_word)
            result.auto_corrected_count += 1
            result.corrections.append({
                "original": clean,
                "corrected": normalized,
                "type": "character_normalization",
                "confidence": "high",
            })
            continue

        suggestions = _find_suggestions(clean, max_distance=1, max_results=3)

        if len(suggestions) == 1:
            corrected_word = word.replace(clean, suggestions[0])
            corrected_words.append(corrected_word)
            result.auto_corrected_count += 1
            result.misspelled_count += 1
            result.corrections.append({
                "original": clean,
                "corrected": suggestions[0],
                "type": "auto_corrected",
                "confidence": "medium",
            })
        elif len(suggestions) > 1:
            corrected_words.append(word)
            result.misspelled_count += 1
            result.corrections.append({
                "original": clean,
                "suggestions": suggestions,
                "type": "needs_review",
                "confidence": "low",
            })
        else:
            corrected_words.append(word)

    result.corrected_text = " ".join(corrected_words)
    return result
