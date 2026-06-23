"""Results, Ranking, and Export API routes (v7) — per-user isolation."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import json
import os

from app.models.database import get_db, JobDescription, CV, User
from app.routers.auth_router import require_user
from app.services.matcher import get_similarity_label
from app.services.export_service import export_to_pdf, export_to_excel
from app.services.crosslang_matcher import get_dictionary_stats

router = APIRouter()


def _get_user_job(job_id, user, db):
    job = db.query(JobDescription).filter(
        JobDescription.id == job_id,
        JobDescription.user_id == user.id,
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")
    return job


def _build_ranked_list(cvs):
    ranked = []
    for rank, cv in enumerate(cvs, start=1):
        score = cv.combined_score or 0.0

        try:
            matched_kw = json.loads(cv.matched_keywords) if cv.matched_keywords else []
        except json.JSONDecodeError:
            matched_kw = []

        try:
            extracted_kw = json.loads(cv.extracted_keywords) if cv.extracted_keywords else []
        except json.JSONDecodeError:
            extracted_kw = []

        try:
            skills = json.loads(cv.parsed_skills) if cv.parsed_skills else []
        except json.JSONDecodeError:
            skills = []

        try:
            claude_matched = json.loads(cv.claude_matched_skills) if cv.claude_matched_skills else []
        except json.JSONDecodeError:
            claude_matched = []

        try:
            claude_missing = json.loads(cv.claude_missing_skills) if cv.claude_missing_skills else []
        except json.JSONDecodeError:
            claude_missing = []

        ranked.append({
            "rank": rank,
            "cv_id": cv.id,
            "filename": cv.filename,
            "detected_language": cv.detected_language,
            "status": cv.status,
            "tfidf_score": round(cv.similarity_score or 0, 4),
            "crosslang_score": round(cv.crosslang_score or 0, 4),
            "claude_score": round(cv.claude_score or 0, 4),
            "claude_summary": cv.claude_summary or "",
            "claude_matched_skills": claude_matched,
            "claude_missing_skills": claude_missing,
            "matching_method": cv.matching_method or "dictionary",
            "combined_score": round(score, 4),
            "similarity_percentage": round(score * 100, 2),
            "similarity_label": get_similarity_label(score),
            "parsed_name": cv.parsed_name,
            "parsed_email": cv.parsed_email,
            "parsed_degree": cv.parsed_degree,
            "parsed_skills": skills,
            "matched_keywords": matched_kw[:15],
            "matched_keyword_count": len(matched_kw),
            "total_keywords": len(extracted_kw),
            "error_message": cv.error_message,
        })
    return ranked


def _build_summary(job, cvs):
    completed = [cv for cv in cvs if cv.status in ("completed", "cleaned")]
    errors = [cv for cv in cvs if cv.status == "error"]
    scores = [cv.combined_score for cv in completed if cv.combined_score is not None]
    return {
        "job_id": job.id,
        "job_title": job.title,
        "total_cvs": len(cvs),
        "completed": len(completed),
        "errors": len(errors),
        "average_score": round(sum(scores) / len(scores), 4) if scores else 0,
        "highest_score": round(max(scores), 4) if scores else 0,
        "lowest_score": round(min(scores), 4) if scores else 0,
    }


@router.get("/jobs/{job_id}/results")
def get_ranked_results(
    job_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    job = _get_user_job(job_id, user, db)
    cvs = (
        db.query(CV)
        .filter(CV.job_description_id == job_id, CV.user_id == user.id)
        .order_by(CV.combined_score.desc())
        .all()
    )
    return {
        "job_id": job.id,
        "job_title": job.title,
        "total_cvs": len(cvs),
        "ranked_cvs": _build_ranked_list(cvs),
    }


@router.get("/jobs/{job_id}/results/summary")
def get_results_summary(
    job_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    job = _get_user_job(job_id, user, db)
    cvs = db.query(CV).filter(CV.job_description_id == job_id, CV.user_id == user.id).all()
    return _build_summary(job, cvs)


@router.get("/dictionary/stats")
def dictionary_stats():
    return get_dictionary_stats()


@router.get("/jobs/{job_id}/export/pdf")
def export_results_pdf(
    job_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    job = _get_user_job(job_id, user, db)
    cvs = (
        db.query(CV)
        .filter(CV.job_description_id == job_id, CV.user_id == user.id)
        .order_by(CV.combined_score.desc())
        .all()
    )
    if not cvs:
        raise HTTPException(status_code=400, detail="No CVs to export.")

    ranked = _build_ranked_list(cvs)
    summary = _build_summary(job, cvs)

    try:
        filepath = export_to_pdf(job.title, ranked, summary)
        return FileResponse(path=filepath, filename=os.path.basename(filepath), media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")


@router.get("/jobs/{job_id}/export/excel")
def export_results_excel(
    job_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    job = _get_user_job(job_id, user, db)
    cvs = (
        db.query(CV)
        .filter(CV.job_description_id == job_id, CV.user_id == user.id)
        .order_by(CV.combined_score.desc())
        .all()
    )
    if not cvs:
        raise HTTPException(status_code=400, detail="No CVs to export.")

    ranked = _build_ranked_list(cvs)
    summary = _build_summary(job, cvs)

    try:
        filepath = export_to_excel(job.title, ranked, summary)
        return FileResponse(
            path=filepath, filename=os.path.basename(filepath),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel export failed: {str(e)}")


@router.post("/jobs/{job_id}/privacy-cleanup")
def privacy_cleanup(
    job_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """
    NFR-4 Privacy Compliance: Delete uploaded CV files and personal data.
    Preserves scores, rankings, and matched keywords for recruiter workflow.
    """
    job = _get_user_job(job_id, user, db)
    cvs = db.query(CV).filter(
        CV.job_description_id == job_id,
        CV.user_id == user.id,
    ).all()

    if not cvs:
        raise HTTPException(status_code=400, detail="No CVs to clean up.")

    files_deleted = 0
    for cv in cvs:
        # Delete physical file from disk
        if cv.file_path and os.path.exists(cv.file_path):
            try:
                os.remove(cv.file_path)
                files_deleted += 1
            except OSError:
                pass

        # Clear personal data from database
        cv.raw_text = None
        cv.translated_text = None
        cv.normalized_text = None
        cv.parsed_name = None
        cv.parsed_email = None
        cv.parsed_phone = None
        cv.parsed_experience = None
        cv.parsed_education = None
        cv.file_path = ""

        # Mark as cleaned
        cv.status = "cleaned"

    db.commit()

    return {
        "message": f"Privacy cleanup complete. {files_deleted} files deleted, personal data cleared from {len(cvs)} CVs.",
        "files_deleted": files_deleted,
        "cvs_cleaned": len(cvs),
    }
