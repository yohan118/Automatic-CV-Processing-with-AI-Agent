"""Database models (v10) — User auth with OTP verification & Google OAuth."""

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timedelta
import hashlib
import secrets
import random

DATABASE_URL = "sqlite:///cv_processor.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=True)
    salt = Column(String(64), nullable=True)
    auth_provider = Column(String(20), default="local")
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password_sha256: str):
        """
        Receives SHA-256 hash from frontend.
        Adds server-side salt and re-hashes (double hash).
        Password is NEVER transmitted or stored in plain text.
        """
        self.salt = secrets.token_hex(32)
        self.password_hash = hashlib.sha256(
            (password_sha256 + self.salt).encode()
        ).hexdigest()

    def check_password(self, password_sha256: str) -> bool:
        """Verify: SHA256(client_hash + server_salt) == stored_hash."""
        test_hash = hashlib.sha256(
            (password_sha256 + self.salt).encode()
        ).hexdigest()
        return test_hash == self.password_hash


class OTPCode(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    code = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

    @staticmethod
    def generate(email: str, expiry_minutes: int = 5):
        code = str(random.randint(100000, 999999))
        return OTPCode(
            email=email.lower().strip(),
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes),
        )

    def is_valid(self, code: str) -> bool:
        return (
            self.code == code
            and not self.used
            and datetime.utcnow() < self.expires_at
        )


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    original_text = Column(Text, nullable=False)
    normalized_text = Column(Text)
    extracted_keywords = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class CV(Base):
    __tablename__ = "cvs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_description_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")

    raw_text = Column(Text)
    detected_language = Column(String(10))
    translated_text = Column(Text)
    normalized_text = Column(Text)

    extracted_keywords = Column(Text)
    matched_keywords = Column(Text)

    similarity_score = Column(Float, default=0.0)
    crosslang_score = Column(Float, default=0.0)
    claude_score = Column(Float, default=0.0)
    claude_summary = Column(Text)
    claude_matched_skills = Column(Text)
    claude_missing_skills = Column(Text)
    matching_method = Column(String(20), default="dictionary")
    combined_score = Column(Float, default=0.0)

    parsed_name = Column(String(255))
    parsed_email = Column(String(255))
    parsed_phone = Column(String(100))
    parsed_degree = Column(String(500))
    parsed_skills = Column(Text)
    parsed_experience = Column(Text)
    parsed_education = Column(Text)

    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
