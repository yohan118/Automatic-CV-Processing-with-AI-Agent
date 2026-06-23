"""CV Upload, Processing, and Preview API routes (v7) — per-user isolation."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import os
import json
import fitz
import base64
from typing import List

from app.models.database import get_db, JobDescription, CV, User
from app.routers.auth_router import require_user
from app.services.pipeline import process_cv

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_file(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not supported.")
    return ext


def _get_user_job(job_id: int, user: User, db: Session):
    job = db.query(JobDescription).filter(
        JobDescription.id == job_id,
        JobDescription.user_id == user.id,
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")
    if not job.normalized_text:
        raise HTTPException(status_code=400, detail="Job description has no normalized text.")
    return job


@router.post("/jobs/{job_id}/cvs")
async def upload_cv(
    job_id: int,
    file: UploadFile = File(...),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    job = _get_user_job(job_id, user, db)
    validate_file(file.filename)

    safe_filename = f"u{user.id}_job{job_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File too large. Maximum 10 MB.")
            buffer.write(content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    db_cv = CV(
        job_description_id=job_id,
        user_id=user.id,
        filename=file.filename,
        file_path=file_path,
        status="processing",
    )
    db.add(db_cv)
    db.commit()
    db.refresh(db_cv)

    try:
        result = process_cv(
            file_path,
            jd_normalized_text=job.normalized_text,
            jd_original_text=job.original_text,
        )

        db_cv.raw_text = result.raw_text
        db_cv.detected_language = result.detected_language
        db_cv.translated_text = result.translated_text
        db_cv.normalized_text = result.normalized_text
        db_cv.extracted_keywords = result.keywords_json
        db_cv.similarity_score = result.similarity_score
        db_cv.crosslang_score = result.crosslang_score
        db_cv.combined_score = result.combined_score
        db_cv.claude_score = result.claude_score
        db_cv.claude_summary = result.claude_summary
        db_cv.claude_matched_skills = json.dumps(result.claude_matched_skills, ensure_ascii=False) if result.claude_matched_skills else None
        db_cv.claude_missing_skills = json.dumps(result.claude_missing_skills, ensure_ascii=False) if result.claude_missing_skills else None
        db_cv.matching_method = result.matching_method
        db_cv.matched_keywords = result.matched_keywords_json
        db_cv.status = result.status
        db_cv.error_message = result.error_message

        if result.parsed:
            db_cv.parsed_name = result.parsed.name
            db_cv.parsed_email = result.parsed.email
            db_cv.parsed_phone = result.parsed.phone
            db_cv.parsed_degree = result.parsed.degree
            db_cv.parsed_skills = result.parsed.skills_to_json()
            db_cv.parsed_experience = result.parsed.experience_to_json()
            db_cv.parsed_education = result.parsed.education_to_json()

        db.commit()
        db.refresh(db_cv)

        return {
            "id": db_cv.id,
            "filename": db_cv.filename,
            "status": db_cv.status,
            **result.to_dict(),
        }

    except Exception as e:
        db_cv.status = "error"
        db_cv.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/jobs/{job_id}/cvs/batch")
async def upload_multiple_cvs(
    job_id: int,
    files: List[UploadFile] = File(...),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    job = _get_user_job(job_id, user, db)

    results = []
    for file in files:
        try:
            validate_file(file.filename)
            safe_filename = f"u{user.id}_job{job_id}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, safe_filename)

            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            db_cv = CV(
                job_description_id=job_id,
                user_id=user.id,
                filename=file.filename,
                file_path=file_path,
                status="processing",
            )
            db.add(db_cv)
            db.commit()
            db.refresh(db_cv)

            result = process_cv(
                file_path,
                jd_normalized_text=job.normalized_text,
                jd_original_text=job.original_text,
            )

            db_cv.raw_text = result.raw_text
            db_cv.detected_language = result.detected_language
            db_cv.translated_text = result.translated_text
            db_cv.normalized_text = result.normalized_text
            db_cv.extracted_keywords = result.keywords_json
            db_cv.similarity_score = result.similarity_score
            db_cv.crosslang_score = result.crosslang_score
            db_cv.combined_score = result.combined_score
            db_cv.claude_score = result.claude_score
            db_cv.claude_summary = result.claude_summary
            db_cv.claude_matched_skills = json.dumps(result.claude_matched_skills, ensure_ascii=False) if result.claude_matched_skills else None
            db_cv.claude_missing_skills = json.dumps(result.claude_missing_skills, ensure_ascii=False) if result.claude_missing_skills else None
            db_cv.matching_method = result.matching_method
            db_cv.matched_keywords = result.matched_keywords_json
            db_cv.status = result.status
            db_cv.error_message = result.error_message

            if result.parsed:
                db_cv.parsed_name = result.parsed.name
                db_cv.parsed_email = result.parsed.email
                db_cv.parsed_phone = result.parsed.phone
                db_cv.parsed_degree = result.parsed.degree
                db_cv.parsed_skills = result.parsed.skills_to_json()
                db_cv.parsed_experience = result.parsed.experience_to_json()
                db_cv.parsed_education = result.parsed.education_to_json()

            db.commit()

            results.append({
                "id": db_cv.id,
                "filename": db_cv.filename,
                "status": result.status,
                "combined_score": round(result.combined_score, 4),
                "similarity_percentage": round(result.combined_score * 100, 2),
                "similarity_label": result.similarity_label,
                "detected_language": result.language_name,
                "degree": result.parsed.degree_level if result.parsed else None,
                "error": result.error_message,
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e),
            })

    return {"total": len(results), "results": results}


@router.get("/jobs/{job_id}/cvs/{cv_id}")
def get_cv_details(
    job_id: int, cv_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    cv = db.query(CV).filter(
        CV.id == cv_id,
        CV.job_description_id == job_id,
        CV.user_id == user.id,
    ).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")

    def safe_json(val):
        if not val:
            return []
        try:
            return json.loads(val)
        except:
            return []

    return {
        "id": cv.id,
        "filename": cv.filename,
        "status": cv.status,
        "detected_language": cv.detected_language,
        "raw_text": cv.raw_text,
        "translated_text": cv.translated_text,
        "normalized_text": cv.normalized_text,
        "similarity_score": round(cv.similarity_score, 4) if cv.similarity_score else 0,
        "crosslang_score": round(cv.crosslang_score, 4) if cv.crosslang_score else 0,
        "claude_score": round(cv.claude_score, 4) if cv.claude_score else 0,
        "claude_summary": cv.claude_summary or "",
        "claude_matched_skills": safe_json(cv.claude_matched_skills),
        "claude_missing_skills": safe_json(cv.claude_missing_skills),
        "matching_method": cv.matching_method or "dictionary",
        "combined_score": round(cv.combined_score, 4) if cv.combined_score else 0,
        "similarity_percentage": round((cv.combined_score or 0) * 100, 2),
        "extracted_keywords": safe_json(cv.extracted_keywords),
        "matched_keywords": safe_json(cv.matched_keywords),
        "parsed_name": cv.parsed_name,
        "parsed_email": cv.parsed_email,
        "parsed_phone": cv.parsed_phone,
        "parsed_degree": cv.parsed_degree,
        "parsed_skills": safe_json(cv.parsed_skills),
        "parsed_experience": safe_json(cv.parsed_experience),
        "parsed_education": safe_json(cv.parsed_education),
        "error_message": cv.error_message,
        "created_at": cv.created_at.isoformat() if cv.created_at else None,
    }


@router.get("/jobs/{job_id}/cvs/{cv_id}/preview")
def preview_cv(
    job_id: int, cv_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    cv = db.query(CV).filter(
        CV.id == cv_id,
        CV.job_description_id == job_id,
        CV.user_id == user.id,
    ).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")
    if not os.path.exists(cv.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk.")

    ext = os.path.splitext(cv.file_path)[1].lower()

    if ext == ".pdf":
        try:
            doc = fitz.open(cv.file_path)
            pages_html = []
            for page_num in range(min(len(doc), 10)):
                page = doc[page_num]
                mat = fitz.Matrix(1.5, 1.5)
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")
                b64 = base64.b64encode(img_bytes).decode()
                pages_html.append(
                    f'<div style="margin-bottom:12px;border:1px solid #e2e8f0;border-radius:4px;overflow:hidden;">'
                    f'<img src="data:image/png;base64,{b64}" style="width:100%;display:block;" /></div>'
                )
            doc.close()
            html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{cv.filename}</title>
            <style>body{{margin:0;padding:16px;background:#f5f6f8;font-family:sans-serif;}}
            h3{{color:#1e293b;margin-bottom:12px;}}</style></head>
            <body><h3>{cv.filename} ({len(pages_html)} pages)</h3>{''.join(pages_html)}</body></html>"""
            return HTMLResponse(content=html)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

    elif ext in (".docx", ".doc"):
        raw_text = cv.raw_text or "No text extracted."
        paragraphs = raw_text.split("\n")
        body = "".join(f"<p style='margin:4px 0;line-height:1.7;'>{p}</p>" for p in paragraphs if p.strip())
        has_rtl = any('\u0600' <= c <= '\u06FF' for c in raw_text[:500])
        direction = 'rtl' if has_rtl else 'ltr'
        html = f"""<!DOCTYPE html><html dir="{direction}"><head><meta charset="utf-8"><title>{cv.filename}</title>
        <style>body{{margin:0;padding:20px 24px;background:#fff;font-family:'Noto Sans Arabic',sans-serif;
        font-size:14px;color:#1e293b;}}h3{{margin-bottom:16px;}}</style></head>
        <body><h3>{cv.filename}</h3>{body}</body></html>"""
        return HTMLResponse(content=html)

    raise HTTPException(status_code=400, detail="Preview not supported for this file type.")


@router.delete("/jobs/{job_id}/cvs/{cv_id}")
def delete_cv(
    job_id: int, cv_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    cv = db.query(CV).filter(
        CV.id == cv_id,
        CV.job_description_id == job_id,
        CV.user_id == user.id,
    ).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")
    if os.path.exists(cv.file_path):
        os.remove(cv.file_path)
    db.delete(cv)
    db.commit()
    return {"message": f"CV '{cv.filename}' deleted."}
