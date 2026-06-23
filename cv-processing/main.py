"""
Automatic CV Processing System — v10.0.0
BSc Graduation Project

v10: Google OAuth + Email OTP verification + SHA-256 password encryption.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import os

from app.models.database import create_tables
from app.routers import auth_router, job_router, cv_router, results_router
from app.services.trilingual_dict import DICTIONARY
from config import GOOGLE_CLIENT_ID, SESSION_SECRET, SESSION_MAX_AGE


# ── App ──────────────────────────────────────────────
app = FastAPI(
    title="Automatic CV Processing System",
    description="BSc Graduation Project — v11 (Google OAuth + OTP + SHA-256)",
    version="12.0.0",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="cv_session",
    max_age=SESSION_MAX_AGE,
)

# ── Static files ─────────────────────────────────────
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "app", "templates")
STATIC_DIR = os.path.join(TEMPLATES_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ── Routers ──────────────────────────────────────────
app.include_router(auth_router.router, prefix="/api", tags=["Auth"])
app.include_router(job_router.router, prefix="/api", tags=["Jobs"])
app.include_router(cv_router.router, prefix="/api", tags=["CVs"])
app.include_router(results_router.router, prefix="/api", tags=["Results"])


# ── Pages ────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user_id = request.session.get("user_id")
    if user_id:
        return RedirectResponse(url="/", status_code=302)

    login_html = os.path.join(TEMPLATES_DIR, "login.html")
    with open(login_html, "r", encoding="utf-8") as f:
        html = f.read()

    # Inject Google Client ID
    html = html.replace("{{ google_client_id }}", GOOGLE_CLIENT_ID)

    return HTMLResponse(content=html)


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    user_id = request.session.get("user_id")
    first_name = request.session.get("first_name", "User")

    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    index_html = os.path.join(TEMPLATES_DIR, "index.html")
    with open(index_html, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{ user_first_name }}", first_name)

    return HTMLResponse(content=html)


# ── Startup ──────────────────────────────────────────

@app.on_event("startup")
def on_startup():
    create_tables()

    cats = {}
    for g in DICTIONARY:
        c = g.category or "other"
        cats[c] = cats.get(c, 0) + 1

    print("\n" + "=" * 60)
    print("  Automatic CV Processing System — v11.0.0")
    print("  Google OAuth | Email OTP | SHA-256 Encryption")
    print("=" * 60)
    print(f"  Dictionary: {len(DICTIONARY)} term groups")
    print(f"  Categories: {len(cats)}")
    print("-" * 60)

    # Config status
    google_ok = GOOGLE_CLIENT_ID and "YOUR_" not in GOOGLE_CLIENT_ID
    print(f"  Google OAuth:  {'Configured' if google_ok else 'NOT configured (update config.py)'}")

    from config import SMTP_EMAIL
    smtp_ok = SMTP_EMAIL and "your." not in SMTP_EMAIL
    print(f"  Email OTP:     {'Configured' if smtp_ok else 'NOT configured (update config.py)'}")

    print("=" * 60)
    print("  http://localhost:8000/login")
    print("=" * 60 + "\n")

    os.makedirs("uploads", exist_ok=True)
    os.makedirs("exports", exist_ok=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
