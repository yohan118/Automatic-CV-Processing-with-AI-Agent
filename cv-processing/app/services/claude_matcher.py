import json
import re

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CLAUDE_TIMEOUT


_client = None


def is_enabled():
    return ANTHROPIC_AVAILABLE and bool(ANTHROPIC_API_KEY and ANTHROPIC_API_KEY.strip())


def _get_client():
    global _client
    if _client is None and is_enabled():
        _client = Anthropic(api_key=ANTHROPIC_API_KEY, timeout=CLAUDE_TIMEOUT)
    return _client


SYSTEM_PROMPT = """You are an expert recruiter assistant that evaluates how well a candidate's CV matches a job description. You analyze CVs and job descriptions in English, Arabic, or Kurdish Sorani.

Your task: Compare the given job description and CV, then return ONLY a JSON object with no extra text.

The JSON must have this exact structure:
{
  "score": <integer 0-100>,
  "summary": "<one short sentence explaining the match>",
  "matched_skills": ["<skill1>", "<skill2>", ...],
  "missing_skills": ["<skill1>", "<skill2>", ...]
}

Scoring guide:
- 90-100: Perfect match, all major requirements met
- 70-89: Strong match, most requirements met
- 50-69: Moderate match, some key requirements met
- 30-49: Weak match, few requirements met
- 0-29: Poor match, requirements not met

Be strict and realistic. Keep summary under 20 words. List 3-8 matched and missing skills max.
Return ONLY the JSON object. No markdown, no code fences, no explanations."""


def score_match(jd_text, cv_text):
    if not is_enabled():
        return None

    if not jd_text or not cv_text:
        return None

    client = _get_client()
    if client is None:
        return None

    jd_trimmed = jd_text[:3000]
    cv_trimmed = cv_text[:5000]

    user_message = f"""JOB DESCRIPTION:
{jd_trimmed}

---

CV:
{cv_trimmed}

---

Return the JSON object now."""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        if not response.content or len(response.content) == 0:
            return None

        raw_text = response.content[0].text.strip()
        return _parse_response(raw_text)

    except Exception as e:
        print(f"[Claude API error] {e}")
        return None


def _parse_response(raw_text):
    text = raw_text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)

    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if not json_match:
        return None

    try:
        data = json.loads(json_match.group(0))
    except json.JSONDecodeError:
        return None

    score_raw = data.get("score", 0)
    try:
        score = int(score_raw)
    except (ValueError, TypeError):
        score = 0

    score = max(0, min(100, score))

    return {
        "score": score / 100.0,
        "percentage": score,
        "summary": str(data.get("summary", ""))[:200],
        "matched_skills": list(data.get("matched_skills", []))[:10],
        "missing_skills": list(data.get("missing_skills", []))[:10],
    }
