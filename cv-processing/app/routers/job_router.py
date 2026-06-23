"""Job Description API routes (v7) — per-user isolation."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.database import get_db, JobDescription, CV
from app.routers.auth_router import require_user
from app.models.database import User
from app.services.text_normalizer import normalize_text
from app.services.keyword_extractor import extract_keywords, keywords_to_json

router = APIRouter()


class JobDescriptionCreate(BaseModel):
    title: str
    original_text: str


@router.post("/jobs")
def create_job(
    data: JobDescriptionCreate,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    if not data.title.strip():
        raise HTTPException(status_code=400, detail="Title is required.")
    if not data.original_text.strip():
        raise HTTPException(status_code=400, detail="Job description text is required.")

    normalized = normalize_text(data.original_text)
    keywords = extract_keywords(normalized, top_n=30)

    job = JobDescription(
        user_id=user.id,
        title=data.title.strip(),
        original_text=data.original_text.strip(),
        normalized_text=normalized,
        extracted_keywords=keywords_to_json(keywords),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "id": job.id,
        "title": job.title,
        "normalized_length": len(normalized),
        "keyword_count": len(keywords),
    }


@router.get("/jobs")
def list_jobs(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    jobs = (
        db.query(JobDescription)
        .filter(JobDescription.user_id == user.id)
        .order_by(JobDescription.created_at.desc())
        .all()
    )
    result = []
    for j in jobs:
        cv_count = db.query(CV).filter(CV.job_description_id == j.id, CV.user_id == user.id).count()
        result.append({
            "id": j.id,
            "title": j.title,
            "cv_count": cv_count,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        })
    return result


@router.get("/jobs/{job_id}")
def get_job(
    job_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    job = db.query(JobDescription).filter(
        JobDescription.id == job_id,
        JobDescription.user_id == user.id,
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")
    return {
        "id": job.id,
        "title": job.title,
        "original_text": job.original_text,
        "normalized_text": job.normalized_text,
    }


@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    job = db.query(JobDescription).filter(
        JobDescription.id == job_id,
        JobDescription.user_id == user.id,
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")

    import os
    cvs = db.query(CV).filter(CV.job_description_id == job_id, CV.user_id == user.id).all()
    for cv in cvs:
        if os.path.exists(cv.file_path):
            os.remove(cv.file_path)
        db.delete(cv)

    db.delete(job)
    db.commit()
    return {"message": f"Job '{job.title}' and {len(cvs)} CVs deleted."}
