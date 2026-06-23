"""Authentication routes (v10) — Email+OTP signup, Google OAuth, SHA-256 password hashing."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import urllib.request
import urllib.parse

from app.models.database import get_db, User, OTPCode
from config import (
    GOOGLE_CLIENT_ID,
    SMTP_EMAIL, SMTP_APP_PASSWORD, SMTP_HOST, SMTP_PORT,
    OTP_EXPIRY_MINUTES,
)

router = APIRouter()


# ── Schemas ──────────────────────────────────────────

class SignUpRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    password_hash: str  # SHA-256 hash from frontend


class VerifyOTPRequest(BaseModel):
    email: str
    code: str


class LoginRequest(BaseModel):
    email: str
    password_hash: str  # SHA-256 hash from frontend


class GoogleAuthRequest(BaseModel):
    credential: str  # JWT token from Google


# ── Helpers ──────────────────────────────────────────

def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def require_user(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def _send_otp_email(to_email: str, code: str):
    """Send OTP verification code via Gmail SMTP."""
    msg = MIMEMultipart()
    msg['From'] = SMTP_EMAIL
    msg['To'] = to_email
    msg['Subject'] = f'Your Verification Code: {code}'

    body = f"""
    <html>
    <body style="font-family: -apple-system, sans-serif; padding: 20px;">
        <div style="max-width: 400px; margin: 0 auto; background: #f8fafb; border-radius: 12px; padding: 32px; border: 1px solid #e2e8f0;">
            <h2 style="color: #1e293b; margin-top: 0;">Email Verification</h2>
            <p style="color: #64748b; font-size: 14px;">Use the code below to verify your account on Automatic CV Processing:</p>
            <div style="background: #1b6b5a; color: white; font-size: 32px; font-weight: 700; letter-spacing: 8px; text-align: center; padding: 16px; border-radius: 8px; margin: 20px 0;">
                {code}
            </div>
            <p style="color: #94a3b8; font-size: 12px;">This code expires in {OTP_EXPIRY_MINUTES} minutes. If you did not request this, please ignore this email.</p>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        server.send_message(msg)


def _decode_google_jwt(token: str) -> dict:
    """Decode and verify Google ID token using Google's tokeninfo endpoint."""
    url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        # Verify audience matches our client ID
        if data.get("aud") != GOOGLE_CLIENT_ID:
            raise ValueError("Invalid audience")
        return data
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")


# ── SIGNUP: Step 1 — Send OTP ────────────────────────

@router.post("/auth/signup")
def signup(data: SignUpRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise HTTPException(status_code=400, detail="Invalid email format.")

    first_name = data.first_name.strip()
    last_name = data.last_name.strip()
    if not first_name or not last_name:
        raise HTTPException(status_code=400, detail="First and last name are required.")
    if len(data.password_hash) != 64:
        raise HTTPException(status_code=400, detail="Invalid password hash.")

    # Check if verified user already exists
    existing = db.query(User).filter(User.email == email, User.email_verified == True).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    # Remove any unverified user with same email (re-signup)
    unverified = db.query(User).filter(User.email == email, User.email_verified == False).first()
    if unverified:
        db.delete(unverified)
        db.commit()

    # Create unverified user
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        auth_provider="local",
        email_verified=False,
    )
    user.set_password(data.password_hash)
    db.add(user)
    db.commit()

    # Generate and send OTP
    otp = OTPCode.generate(email, OTP_EXPIRY_MINUTES)
    db.add(otp)
    db.commit()

    try:
        _send_otp_email(email, otp.code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send verification email: {str(e)}")

    return {
        "message": f"Verification code sent to {email}.",
        "email": email,
        "requires_verification": True,
    }


# ── SIGNUP: Step 2 — Verify OTP ──────────────────────

@router.post("/auth/verify-otp")
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    code = data.code.strip()

    # Find the latest unused OTP for this email
    otp = (
        db.query(OTPCode)
        .filter(OTPCode.email == email, OTPCode.used == False)
        .order_by(OTPCode.created_at.desc())
        .first()
    )

    if not otp or not otp.is_valid(code):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code.")

    # Mark OTP as used
    otp.used = True

    # Verify user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.email_verified = True
    db.commit()

    return {
        "message": "Email verified successfully! You can now sign in.",
        "verified": True,
    }


# ── SIGNUP: Resend OTP ───────────────────────────────

@router.post("/auth/resend-otp")
def resend_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()

    user = db.query(User).filter(User.email == email, User.email_verified == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="No pending verification for this email.")

    # Invalidate old OTPs
    db.query(OTPCode).filter(OTPCode.email == email, OTPCode.used == False).update({"used": True})

    otp = OTPCode.generate(email, OTP_EXPIRY_MINUTES)
    db.add(otp)
    db.commit()

    try:
        _send_otp_email(email, otp.code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resend: {str(e)}")

    return {"message": f"New code sent to {email}."}


# ── LOGIN: Email + Password ──────────────────────────

@router.post("/auth/login")
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if user.auth_provider == "google":
        raise HTTPException(status_code=400, detail="This account uses Google Sign-In. Please use the Google button.")

    if not user.email_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please check your inbox for the verification code.")

    if not user.check_password(data.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    request.session["user_id"] = user.id
    request.session["first_name"] = user.first_name

    return {
        "message": f"Welcome back, {user.first_name}!",
        "user_id": user.id,
        "first_name": user.first_name,
    }


# ── LOGIN: Google OAuth ──────────────────────────────

@router.post("/auth/google")
def google_auth(data: GoogleAuthRequest, request: Request, db: Session = Depends(get_db)):
    # Verify token with Google
    google_data = _decode_google_jwt(data.credential)

    email = google_data.get("email", "").lower()
    first_name = google_data.get("given_name", "User")
    last_name = google_data.get("family_name", "")
    email_verified = google_data.get("email_verified", "false") == "true"

    if not email or not email_verified:
        raise HTTPException(status_code=400, detail="Google account email is not verified.")

    # Find or create user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # First time — create account automatically
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            auth_provider="google",
            email_verified=True,  # Google already verified
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Set session
    request.session["user_id"] = user.id
    request.session["first_name"] = user.first_name

    return {
        "message": f"Welcome, {user.first_name}!",
        "user_id": user.id,
        "first_name": user.first_name,
    }


# ── LOGOUT ────────────────────────────────────────────

@router.post("/auth/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out successfully."}


# ── ME ────────────────────────────────────────────────

@router.get("/auth/me")
def get_me(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "auth_provider": user.auth_provider,
    }
