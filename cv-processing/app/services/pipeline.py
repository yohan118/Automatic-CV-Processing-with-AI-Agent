from typing import Optional
import json
from app.services.text_extractor import extract_text
from app.services.language_detector import detect_language, get_language_name
from app.services.translator import translate_to_sorani
from app.services.text_normalizer import normalize_text
from app.services.keyword_extractor import extract_keywords, keywords_to_json
from app.services.matcher import calculate_similarity, get_similarity_label
from app.services.cv_parser import parse_cv, CVParseResult
from app.services.spell_checker import check_and_correct
from app.services.crosslang_matcher import (
    calculate_crosslang_score,
    calculate_v5_combined_score,
)
from app.services import claude_matcher


class PipelineResult:
    def __init__(self):
        self.raw_text: str = ""
        self.detected_language: str = ""
        self.language_name: str = ""
        self.translated_text: str = ""
        self.spell_checked_text: str = ""
        self.spell_corrections: list = []
        self.normalized_text: str = ""
        self.keywords_json: str = "[]"
        self.similarity_score: float = 0.0
        self.crosslang_score: float = 0.0
        self.claude_score: float = 0.0
        self.claude_summary: str = ""
        self.claude_matched_skills: list = []
        self.claude_missing_skills: list = []
        self.combined_score: float = 0.0
        self.matched_keywords_json: str = "[]"
        self.similarity_label: str = ""
        self.matching_method: str = "dictionary"
        self.status: str = "completed"
        self.error_message: Optional[str] = None
        self.parsed: Optional[CVParseResult] = None

    def to_dict(self) -> dict:
        parsed_dict = self.parsed.to_dict() if self.parsed else {}
        return {
            "raw_text_preview": self.raw_text[:500] + "..." if len(self.raw_text) > 500 else self.raw_text,
            "detected_language": self.detected_language,
            "language_name": self.language_name,
            "translated_text_preview": self.translated_text[:500] + "..." if len(self.translated_text) > 500 else self.translated_text,
            "spell_corrections": self.spell_corrections[:20],
            "similarity_score": round(self.similarity_score, 4),
            "crosslang_score": round(self.crosslang_score, 4),
            "claude_score": round(self.claude_score, 4),
            "claude_summary": self.claude_summary,
            "claude_matched_skills": self.claude_matched_skills,
            "claude_missing_skills": self.claude_missing_skills,
            "combined_score": round(self.combined_score, 4),
            "similarity_percentage": round(self.combined_score * 100, 2),
            "similarity_label": self.similarity_label,
            "matching_method": self.matching_method,
            "keywords_json": self.keywords_json,
            "matched_keywords_json": self.matched_keywords_json,
            "parsed": parsed_dict,
            "status": self.status,
            "error_message": self.error_message,
        }


def process_cv(file_path: str, jd_normalized_text: str, jd_original_text: str = "") -> PipelineResult:
    result = PipelineResult()

    try:
        print(f"  Step 1: Extracting text from {file_path}...")
        result.raw_text = extract_text(file_path)
        print(f"    Extracted {len(result.raw_text)} characters")

        print("  Step 2: Detecting language...")
        result.detected_language = detect_language(result.raw_text)
        result.language_name = get_language_name(result.detected_language)
        print(f"    Detected: {result.language_name}")

        print("  Step 3: Parsing structured CV data...")
        result.parsed = parse_cv(result.raw_text, result.detected_language)
        if result.parsed.name:
            print(f"    Name: {result.parsed.name}")
        if result.parsed.degree_level:
            print(f"    Degree: {result.parsed.degree_level}")
        if result.parsed.skills:
            print(f"    Skills: {len(result.parsed.skills)} found")

        jd_for_matching = jd_original_text or jd_normalized_text

        print("  Step 4: Cross-language dictionary matching...")
        crosslang_score, crosslang_matches = calculate_crosslang_score(
            jd_for_matching, result.raw_text
        )
        result.crosslang_score = crosslang_score
        result.matched_keywords_json = json.dumps(crosslang_matches, ensure_ascii=False)
        print(f"    Cross-language score: {crosslang_score:.4f} ({len(crosslang_matches)} term matches)")

        if claude_matcher.is_enabled():
            print("  Step 4b: Claude API semantic matching (Sonnet)...")
            claude_result = claude_matcher.score_match(jd_for_matching, result.raw_text)
            if claude_result is not None:
                result.claude_score = claude_result["score"]
                result.claude_summary = claude_result["summary"]
                result.claude_matched_skills = claude_result["matched_skills"]
                result.claude_missing_skills = claude_result["missing_skills"]
                result.matching_method = "claude_api"
                print(f"    Claude score: {result.claude_score:.4f}")
                print(f"    Summary: {result.claude_summary}")
            else:
                print("    Claude API returned no result, using dictionary matching")
        else:
            print("  Step 4b: Claude API disabled (no API key in config.py)")

        if result.detected_language == "ckb":
            print("  Step 5: Already in Kurdish, skipping translation")
            result.translated_text = result.raw_text
        else:
            print(f"  Step 5: Translating from {result.language_name} to Kurdish (display only)...")
            try:
                result.translated_text = translate_to_sorani(
                    result.raw_text, result.detected_language
                )
                print(f"    Translated {len(result.translated_text)} characters")
            except Exception as te:
                print(f"    Translation failed (non-critical): {te}")
                result.translated_text = result.raw_text

        print("  Step 6: Running Kurdish spell check...")
        spell_result = check_and_correct(result.translated_text)
        result.spell_checked_text = spell_result.corrected_text
        result.spell_corrections = spell_result.corrections

        print("  Step 7: Normalizing text...")
        result.normalized_text = normalize_text(result.spell_checked_text)

        print("  Step 8: Calculating TF-IDF similarity...")
        result.similarity_score = calculate_similarity(
            jd_normalized_text, result.normalized_text
        )
        print(f"    TF-IDF score: {result.similarity_score:.4f}")

        if result.matching_method == "claude_api":
            result.combined_score = result.claude_score * 0.8 + result.similarity_score * 0.2
            print(f"  Step 9: Combined score (Claude 80% + TF-IDF 20%)")
        else:
            result.combined_score = calculate_v5_combined_score(
                tfidf_score=result.similarity_score,
                crosslang_score=result.crosslang_score,
            )
            print(f"  Step 9: Combined score (Dictionary 70% + TF-IDF 30%)")

        result.similarity_label = get_similarity_label(result.combined_score)
        print(f"    Final: {result.combined_score:.4f} ({result.similarity_label})")

        cv_keywords = extract_keywords(result.normalized_text, top_n=30)
        result.keywords_json = keywords_to_json(cv_keywords)

        result.status = "completed"

    except Exception as e:
        result.status = "error"
        result.error_message = str(e)
        print(f"  Pipeline error: {e}")
        import traceback
        traceback.print_exc()

    return result
