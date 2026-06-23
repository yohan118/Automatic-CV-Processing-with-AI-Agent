"""
Translation Service (v3 — improved Kurdish output)
Adds post-processing to fix common Google Translate issues with Kurdish Sorani:
- Technical terms that get mistranslated
- Transliteration of programming terms that should stay in Latin script
- Common phrase corrections
"""

from abc import ABC, abstractmethod
from typing import Optional
import re


class TranslatorInterface(ABC):
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str = "ckb") -> str:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


# Technical terms that should NOT be translated (keep as-is)
PRESERVE_TERMS = {
    "python", "javascript", "java", "c++", "c#", "php", "ruby", "swift",
    "kotlin", "go", "rust", "typescript", "sql", "nosql",
    "html", "css", "react", "angular", "vue", "node.js", "express",
    "django", "flask", "fastapi", "spring", "laravel",
    "mysql", "postgresql", "mongodb", "sqlite", "redis", "oracle",
    "docker", "kubernetes", "aws", "azure", "gcp",
    "git", "github", "gitlab", "bitbucket",
    "linux", "windows", "macos", "ubuntu",
    "tensorflow", "pytorch", "keras",
    "rest", "api", "graphql", "json", "xml",
    "figma", "photoshop", "illustrator",
    "agile", "scrum", "jira", "trello",
    "excel", "word", "powerpoint",
    "wifi", "bluetooth", "usb", "http", "https",
    "pdf", "docx", "csv",
    "bsc", "msc", "mba", "phd",
}

# Common corrections for Google Translate Kurdish output
KURDISH_CORRECTIONS = {
    "پایتۆن": "Python",
    "جاڤاسکریپت": "JavaScript",
    "ری‌ئەکت": "React",
    "ئانگولار": "Angular",
    "نۆد": "Node.js",
    "داکەر": "Docker",
    "لینوکس": "Linux",
    "ویندۆز": "Windows",
    "ئێکسێل": "Excel",
    "فایەرفۆکس": "Firefox",
    "گووگل": "Google",
    "مایکرۆسۆفت": "Microsoft",
    "ئەمازۆن": "Amazon",
}

# English to Kurdish technical vocabulary for better translations
EN_TO_CKB_TECHNICAL = {
    "computer science": "زانستی کۆمپیوتەر",
    "software engineer": "ئەندازیاری نەرمەکاڵا",
    "software engineering": "ئەندازیاری نەرمەکاڵا",
    "web developer": "گەشەپێدەری وێب",
    "web development": "گەشەپێدانی وێب",
    "frontend": "ڕووکاری پێشەوە",
    "backend": "لای سێرڤەر",
    "full stack": "تەواو پەشکۆ",
    "database": "بنکەی داتا",
    "machine learning": "فێربوونی مەکینە",
    "artificial intelligence": "زیرەکی دەستکرد",
    "data science": "زانستی داتا",
    "data analysis": "شیکاری داتا",
    "project management": "بەڕێوەبردنی پرۆژە",
    "team leader": "سەرۆکی تیم",
    "problem solving": "چارەسەرکردنی کێشە",
    "communication skills": "لێهاتوویی پەیوەندیکردن",
    "work experience": "ئەزموونی کار",
    "education": "خوێندن",
    "university": "زانکۆ",
    "bachelor": "بەکالۆریۆس",
    "master": "ماستەر",
    "diploma": "دیبلۆم",
    "certificate": "بڕوانامە",
    "skills": "لێهاتوویی",
    "programming": "پرۆگرامکردن",
    "programming language": "زمانی پرۆگرامکردن",
    "version control": "کۆنتڕۆڵی وەشان",
    "operating system": "سیستەمی کارپێکردن",
    "network": "تۆڕ",
    "security": "ئاسایش",
    "cloud computing": "هەورکۆمپیوتینگ",
    "mobile development": "گەشەپێدانی مۆبایل",
    "testing": "تاقیکردنەوە",
    "debugging": "هەڵەدۆزینەوە",
    "framework": "چوارچێوە",
    "library": "کتێبخانە",
    "algorithm": "ئالگۆریزم",
    "data structure": "پێکهاتەی داتا",
}

# Arabic to Kurdish technical vocabulary
AR_TO_CKB_TECHNICAL = {
    "علوم الحاسوب": "زانستی کۆمپیوتەر",
    "هندسة البرمجيات": "ئەندازیاری نەرمەکاڵا",
    "مطور ويب": "گەشەپێدەری وێب",
    "تطوير الويب": "گەشەپێدانی وێب",
    "قاعدة بيانات": "بنکەی داتا",
    "الذكاء الاصطناعي": "زیرەکی دەستکرد",
    "تعلم الآلة": "فێربوونی مەکینە",
    "تحليل البيانات": "شیکاری داتا",
    "إدارة المشاريع": "بەڕێوەبردنی پرۆژە",
    "خبرة عملية": "ئەزموونی کار",
    "التعليم": "خوێندن",
    "الجامعة": "زانکۆ",
    "بكالوريوس": "بەکالۆریۆس",
    "ماجستير": "ماستەر",
    "المهارات": "لێهاتوویی",
    "البرمجة": "پرۆگرامکردن",
    "لغة البرمجة": "زمانی پرۆگرامکردن",
    "تصميم": "دیزاین",
    "شبكة": "تۆڕ",
    "أمن المعلومات": "ئاسایشی زانیاری",
}


def _preserve_technical_terms(text: str) -> tuple:
    """
    Before translation, replace technical terms with placeholders
    so they don't get mistranslated.
    Returns (modified_text, replacements_dict).
    """
    replacements = {}
    modified = text

    for term in sorted(PRESERVE_TERMS, key=len, reverse=True):
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        matches = pattern.findall(modified)
        if matches:
            placeholder = f"__TECH{len(replacements):03d}__"
            replacements[placeholder] = matches[0]
            modified = pattern.sub(placeholder, modified)

    return modified, replacements


def _restore_technical_terms(text: str, replacements: dict) -> str:
    """Restore technical terms after translation."""
    for placeholder, original in replacements.items():
        text = text.replace(placeholder, original)
    return text


def _pre_translate_terms(text: str, source_lang: str) -> str:
    """
    Replace known technical phrases with their Kurdish equivalents
    BEFORE sending to Google Translate for better accuracy.
    """
    vocab = {}
    if source_lang == "en":
        vocab = EN_TO_CKB_TECHNICAL
    elif source_lang == "ar":
        vocab = AR_TO_CKB_TECHNICAL

    for original, kurdish in sorted(vocab.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = re.compile(re.escape(original), re.IGNORECASE)
        text = pattern.sub(kurdish, text)

    return text


def _post_process_kurdish(text: str) -> str:
    """Fix common Google Translate mistakes in Kurdish output."""
    for wrong, correct in KURDISH_CORRECTIONS.items():
        text = text.replace(wrong, correct)
    return text


class GoogleTranslator(TranslatorInterface):
    LANG_MAP = {
        "en": "en",
        "ar": "ar",
        "ckb": "ckb",
    }

    def translate(self, text: str, source_lang: str, target_lang: str = "ckb") -> str:
        if not text or not text.strip():
            return text
        if source_lang == target_lang:
            return text

        src = self.LANG_MAP.get(source_lang, source_lang)
        tgt = self.LANG_MAP.get(target_lang, "ckb")

        try:
            from deep_translator import GoogleTranslator as GT

            # Step 1: Preserve technical terms
            processed_text, tech_replacements = _preserve_technical_terms(text)

            # Step 2: Pre-translate known phrases
            processed_text = _pre_translate_terms(processed_text, source_lang)

            # Step 3: Translate via Google
            chunks = self._split_text(processed_text, max_length=4500)
            translated_chunks = []

            for chunk in chunks:
                translator = GT(source=src, target=tgt)
                result = translator.translate(chunk)
                if result:
                    translated_chunks.append(result)

            translated = "\n".join(translated_chunks)

            # Step 4: Restore technical terms
            translated = _restore_technical_terms(translated, tech_replacements)

            # Step 5: Post-process Kurdish output
            translated = _post_process_kurdish(translated)

            return translated

        except ImportError:
            return StubTranslator().translate(text, source_lang, target_lang)
        except Exception as e:
            print(f"Translation error: {e}")
            return StubTranslator().translate(text, source_lang, target_lang)

    def _split_text(self, text: str, max_length: int = 4500) -> list:
        if len(text) <= max_length:
            return [text]

        chunks = []
        paragraphs = text.split("\n")
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) + 1 <= max_length:
                current_chunk += para + "\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                if len(para) > max_length:
                    sentences = para.replace(". ", ".\n").split("\n")
                    for sent in sentences:
                        chunks.append(sent.strip())
                else:
                    current_chunk = para + "\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text[:max_length]]

    def get_name(self) -> str:
        return "Google Translate (Enhanced)"


class StubTranslator(TranslatorInterface):
    def translate(self, text: str, source_lang: str, target_lang: str = "ckb") -> str:
        return f"[STUB: {source_lang} to {target_lang}]\n{text}"

    def get_name(self) -> str:
        return "Stub Translator"


_active_translator: Optional[TranslatorInterface] = None


def get_translator() -> TranslatorInterface:
    global _active_translator
    if _active_translator is None:
        try:
            from deep_translator import GoogleTranslator as GT
            _active_translator = GoogleTranslator()
        except ImportError:
            _active_translator = StubTranslator()
    return _active_translator


def set_translator(translator: TranslatorInterface):
    global _active_translator
    _active_translator = translator


def translate_to_sorani(text: str, source_lang: str) -> str:
    if source_lang == "ckb":
        return text
    translator = get_translator()
    return translator.translate(text, source_lang, "ckb")
