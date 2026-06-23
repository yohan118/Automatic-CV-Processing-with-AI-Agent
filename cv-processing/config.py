"""
Configuration — reads all secrets from environment variables.
Never hardcode secrets here. Set them in Render's Environment dashboard.
"""
import os

# ── Google OAuth 2.0 ──────────────────────────────────
GOOGLE_CLIENT_ID     = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

# ── Email OTP (Gmail SMTP) ────────────────────────────
SMTP_EMAIL        = os.environ.get("SMTP_EMAIL", "")
SMTP_APP_PASSWORD = os.environ.get("SMTP_APP_PASSWORD", "")
SMTP_HOST         = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT         = int(os.environ.get("SMTP_PORT", "587"))

# ── OTP Settings ──────────────────────────────────────
OTP_EXPIRY_MINUTES = 5
OTP_LENGTH         = 6

# ── Session ───────────────────────────────────────────
SESSION_SECRET  = os.environ.get("SESSION_SECRET", "change-me-in-production")
SESSION_MAX_AGE = 86400  # 24 hours

# ── Claude API (Anthropic) ────────────────────────────
ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL       = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
CLAUDE_MAX_TOKENS  = 1024
CLAUDE_TIMEOUT     = 30
