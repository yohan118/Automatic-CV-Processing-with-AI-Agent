"""
Structured CV Parser (NEW in v2)
Extracts structured information from CV text:
- Candidate name
- Email address
- Phone number
- Degree / Education level
- Skills list
- Work experience entries

This module works on the raw extracted text (before translation)
because structured patterns like emails and phone numbers are
language-independent.

For degree extraction, it handles English, Arabic, and Kurdish patterns
since the degree is one of the most important fields for HR screening.
"""

import re
import json
from typing import Optional, List, Dict


class CVParseResult:
    def __init__(self):
        self.name: Optional[str] = None
        self.email: Optional[str] = None
        self.phone: Optional[str] = None
        self.degree: Optional[str] = None
        self.degree_level: Optional[str] = None
        self.skills: List[str] = []
        self.experience: List[Dict] = []
        self.education: List[Dict] = []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "degree": self.degree,
            "degree_level": self.degree_level,
            "skills": self.skills,
            "experience": self.experience,
            "education": self.education,
        }

    def skills_to_json(self) -> str:
        return json.dumps(self.skills, ensure_ascii=False)

    def experience_to_json(self) -> str:
        return json.dumps(self.experience, ensure_ascii=False)

    def education_to_json(self) -> str:
        return json.dumps(self.education, ensure_ascii=False)


# Degree patterns for three languages
DEGREE_PATTERNS_EN = {
    "PhD": [
        r'(?i)\bph\.?d\.?\b', r'(?i)\bdoctor(?:ate)?\s+(?:of|in)\b',
        r'(?i)\bdoctoral\b',
    ],
    "Master": [
        r'(?i)\bm\.?sc\.?\b', r'(?i)\bm\.?a\.?\b',
        r'(?i)\bmaster(?:\'?s)?\s+(?:of|in|degree)\b',
        r'(?i)\bmaster(?:\'?s)?\b',
        r'(?i)\bmba\b',
    ],
    "Bachelor": [
        r'(?i)\bb\.?sc\.?\b', r'(?i)\bb\.?a\.?\b', r'(?i)\bb\.?eng\.?\b',
        r'(?i)\bbachelor(?:\'?s)?\s+(?:of|in|degree)\b',
        r'(?i)\bbachelor(?:\'?s)?\b',
        r'(?i)\bundergraduate\s+degree\b',
    ],
    "Diploma": [
        r'(?i)\bdiploma\b', r'(?i)\bhnd\b', r'(?i)\bhigher\s+national\s+diploma\b',
        r'(?i)\bassociate(?:\'?s)?\s+degree\b',
    ],
    "High School": [
        r'(?i)\bhigh\s+school\b', r'(?i)\bsecondary\s+school\b',
        r'(?i)\bGED\b',
    ],
}

DEGREE_PATTERNS_AR = {
    "PhD": [
        r'دکتوراه', r'دكتوراه', r'الدكتوراه', r'دکتۆرا',
    ],
    "Master": [
        r'ماجستير', r'ماجستیر', r'الماجستير', r'ماستەر',
    ],
    "Bachelor": [
        r'بكالوريوس', r'بکالوریوس', r'البكالوريوس', r'بەکالۆریۆس',
        r'ليسانس', r'لیسانس',
    ],
    "Diploma": [
        r'دبلوم', r'دیبلۆم', r'الدبلوم',
    ],
    "High School": [
        r'ثانوية', r'الثانوية', r'ئامادەیی', r'دبیرستان',
    ],
}

DEGREE_PATTERNS_CKB = {
    "PhD": [
        r'دکتۆرا', r'پی\s*ئێچ\s*دی',
    ],
    "Master": [
        r'ماستەر', r'ماجستێر',
    ],
    "Bachelor": [
        r'بەکالۆریۆس', r'بکالۆریۆس', r'بەکالۆریوس',
    ],
    "Diploma": [
        r'دیبلۆم', r'دبلۆم',
    ],
    "High School": [
        r'ئامادەیی', r'دوانزە', r'دبیرستان',
    ],
}

# The hierarchy from highest to lowest
DEGREE_HIERARCHY = ["PhD", "Master", "Bachelor", "Diploma", "High School"]

# Section header patterns to identify CV sections
SECTION_HEADERS = {
    "education": [
        r'(?i)education', r'(?i)academic', r'(?i)qualification',
        r'خوێندن', r'خوێندنی', r'زانکۆ', r'بڕوانامە',
        r'التعليم', r'المؤهلات', r'التحصيل',
    ],
    "experience": [
        r'(?i)experience', r'(?i)employment', r'(?i)work\s+history',
        r'ئەزموون', r'ئەزموونی\s+کار', r'کارکردن',
        r'الخبرة', r'الخبرات', r'خبرة',
    ],
    "skills": [
        r'(?i)skills?', r'(?i)competenc', r'(?i)expertise', r'(?i)technical',
        r'لێهاتوویی', r'تواناکان', r'شارەزایی',
        r'المهارات', r'مهارات',
    ],
}

# Common tech skills to look for
TECH_SKILLS = {
    "python", "javascript", "java", "c++", "c#", "php", "ruby", "swift",
    "kotlin", "go", "rust", "typescript", "sql", "html", "css",
    "react", "angular", "vue", "node", "express", "django", "flask", "fastapi",
    "spring", "laravel", "rails",
    "mysql", "postgresql", "mongodb", "sqlite", "redis", "oracle",
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "gitlab",
    "linux", "windows", "macos",
    "tensorflow", "pytorch", "keras", "scikit-learn",
    "rest", "api", "graphql", "microservices",
    "figma", "photoshop", "illustrator", "indesign",
    "excel", "word", "powerpoint",
    "agile", "scrum", "jira",
}


def extract_email(text: str) -> Optional[str]:
    """Extract the first email address found in text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract the first phone number found in text."""
    patterns = [
        r'(?:\+964|0)\s*\d{3}[\s-]?\d{3}[\s-]?\d{4}',
        r'\d{4}[\s-]\d{3}[\s-]\d{4}',
        r'(?:\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}',
        r'\d{10,13}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return None


def extract_name(text: str) -> Optional[str]:
    """
    Extract candidate name from the beginning of the CV.
    The name is typically one of the first non-empty lines.
    We skip lines that look like headers, emails, or phone numbers.
    """
    lines = text.strip().split("\n")

    skip_patterns = [
        r'@',
        r'\d{4,}',
        r'(?i)(resume|curriculum|vitae|cv\b|contact|address|phone|email)',
        r'(?i)(experience|education|skill|summary|objective|profile)',
        r'^\s*[\-=_]{3,}',
    ]

    for line in lines[:10]:
        line = line.strip()
        if not line or len(line) < 2 or len(line) > 60:
            continue

        should_skip = False
        for pattern in skip_patterns:
            if re.search(pattern, line):
                should_skip = True
                break

        if should_skip:
            continue

        cleaned = re.sub(r'[|:,].*$', '', line).strip()
        if cleaned and 2 < len(cleaned) < 50:
            return cleaned

    return None


def extract_degree(text: str, language: str = "en") -> tuple:
    """
    Extract the highest degree mentioned in the CV.
    Returns (degree_description, degree_level).

    The degree level follows the hierarchy: PhD > Master > Bachelor > Diploma > High School
    """
    all_patterns = {}

    for level in DEGREE_HIERARCHY:
        patterns = []
        patterns.extend(DEGREE_PATTERNS_EN.get(level, []))
        patterns.extend(DEGREE_PATTERNS_AR.get(level, []))
        patterns.extend(DEGREE_PATTERNS_CKB.get(level, []))
        all_patterns[level] = patterns

    found_level = None
    found_context = None

    for level in DEGREE_HIERARCHY:
        for pattern in all_patterns[level]:
            match = re.search(pattern, text)
            if match:
                found_level = level

                start = max(0, match.start() - 80)
                end = min(len(text), match.end() + 80)
                context = text[start:end].strip()
                context = re.sub(r'\s+', ' ', context)

                line_start = text.rfind('\n', 0, match.start())
                line_end = text.find('\n', match.end())
                if line_end == -1:
                    line_end = min(len(text), match.end() + 120)
                found_context = text[line_start + 1:line_end].strip()

                return (found_context, found_level)

    return (None, None)


def extract_skills(text: str) -> List[str]:
    """
    Extract skills from CV text using two approaches:
    1. Look for a skills section and parse its content
    2. Scan entire text for known technical skills
    """
    found_skills = set()

    text_lower = text.lower()
    for skill in TECH_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill.capitalize() if len(skill) > 3 else skill.upper())

    return sorted(list(found_skills))


def extract_sections(text: str) -> Dict[str, str]:
    """
    Split CV text into sections based on common section headers.
    Returns dict with keys: education, experience, skills, and their text content.
    """
    sections = {}
    lines = text.split("\n")

    current_section = "header"
    section_text = []

    for line in lines:
        line_stripped = line.strip()
        detected_section = None

        for section_name, patterns in SECTION_HEADERS.items():
            for pattern in patterns:
                if re.search(pattern, line_stripped):
                    detected_section = section_name
                    break
            if detected_section:
                break

        if detected_section:
            if section_text:
                sections[current_section] = "\n".join(section_text).strip()
            current_section = detected_section
            section_text = []
        else:
            section_text.append(line)

    if section_text:
        sections[current_section] = "\n".join(section_text).strip()

    return sections


def parse_cv(raw_text: str, detected_language: str = "en") -> CVParseResult:
    """
    Main parsing function. Extracts all structured data from a CV.

    This runs on the raw extracted text (before translation) because
    patterns like email, phone, and degree keywords are language-specific
    and work better on the original text.
    """
    result = CVParseResult()

    result.email = extract_email(raw_text)
    result.phone = extract_phone(raw_text)
    result.name = extract_name(raw_text)

    degree_text, degree_level = extract_degree(raw_text, detected_language)
    result.degree = degree_text
    result.degree_level = degree_level

    result.skills = extract_skills(raw_text)

    sections = extract_sections(raw_text)
    if "education" in sections:
        result.education = [{"text": sections["education"]}]
    if "experience" in sections:
        result.experience = [{"text": sections["experience"]}]

    return result
