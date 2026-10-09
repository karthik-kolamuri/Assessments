import os
import csv
import io
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import APP_NAME, APP_VERSION, BASE_DIR, BASE_URL, CERTIFICATES_DIR
from app.database import get_db, init_db
from app.models import GenerationJob, Certificate, JobFailure
from app.schemas import (
    BulkJobCreateRequest,
    JobCreateResponse,
    JobDetailResponse,
    CertificateItemResponse,
    FailureItemResponse,
    CertificateVerifyResponse,
    HealthResponse,
    RecipientInput
)
from app.service import create_bulk_job, execute_background_generation, create_job_zip_archive

# Initialize database tables
init_db()

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="High-performance, fault-tolerant Bulk Certificate Generation API with background processing and dynamic QR verification."
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = BASE_DIR / "app" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/api/v1/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """System health check endpoint."""
    return HealthResponse(
        status="HEALTHY",
        app_name=APP_NAME,
        version=APP_VERSION,
        timestamp=datetime.now(timezone.utc)
    )


@app.post("/api/v1/jobs", response_model=JobCreateResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Jobs"])
def create_generation_job(
    request: BulkJobCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Submits a bulk certificate generation job.
    Accepts a list of recipients and returns immediately with job tracking metadata.
    Generation runs asynchronously in the background.
    """
    if not request.recipients:
        raise HTTPException(status_code=400, detail="Recipients list cannot be empty.")

    # 1. Create job entry in DB
    job = create_bulk_job(db, request)

    # 2. Serialize recipient items for background worker
    recipients_data = [item.model_dump() for item in request.recipients]

    # 3. Queue asynchronous background processing
    background_tasks.add_task(execute_background_generation, job.id, recipients_data)

    status_url = f"{BASE_URL}/api/v1/jobs/{job.id}"
    return JobCreateResponse(
        job_id=job.id,
        status=job.status,
        event_name=job.event_name,
        total_recipients=job.total_count,
        created_at=job.created_at,
        status_url=status_url,
        message=f"Job accepted successfully. Processing {job.total_count} certificates in the background."
    )


@app.post("/api/v1/jobs/upload-csv", response_model=JobCreateResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Jobs"])
async def create_generation_job_from_csv(
    background_tasks: BackgroundTasks,
    event_name: str = Form(...),
    issuer_name: Optional[str] = Form("AusIndia Education Initiative"),
    issue_date: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Convenience endpoint to upload a CSV file containing recipients (`name`, `email`).
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a valid CSV file.")

    content = await file.read()
    decoded = content.decode("utf-8-sig", errors="ignore")
    reader = csv.DictReader(io.StringIO(decoded))

    recipients_list = []
    for row in reader:
        # Support flexible column headers
        name = row.get("name") or row.get("Name") or row.get("recipient_name") or ""
        email = row.get("email") or row.get("Email") or row.get("recipient_email") or ""
        recipients_list.append({"name": name.strip(), "email": email.strip()})

    if not recipients_list:
        raise HTTPException(status_code=400, detail="No valid recipient rows found in CSV.")

    # Build Pydantic request object
    validated_recipients = []
    for r in recipients_list:
        # Raw items will be safely validated with fault isolation in background
        validated_recipients.append(RecipientInput(name=r["name"] or "[Empty]", email=r["email"] or "invalid@email.com"))

    req = BulkJobCreateRequest(
        event_name=event_name,
        issuer_name=issuer_name,
        issue_date=issue_date,
        recipients=validated_recipients
    )

    job = create_bulk_job(db, req)
    background_tasks.add_task(execute_background_generation, job.id, recipients_list)

    return JobCreateResponse(
        job_id=job.id,
        status=job.status,
        event_name=job.event_name,
        total_recipients=job.total_count,
        created_at=job.created_at,
        status_url=f"{BASE_URL}/api/v1/jobs/{job.id}",
        message=f"CSV accepted. Processing {job.total_count} recipients in background."
    )


@app.get("/api/v1/jobs/{job_id}", response_model=JobDetailResponse, tags=["Jobs"])
def get_job_details(job_id: str, db: Session = Depends(get_db)):
    """
    Polls the status and progress of a certificate generation job.
    Returns counts, progress percentage, certificate links, and failure diagnostics.
    """
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Generation job '{job_id}' not found.")

    cert_responses = [
        CertificateItemResponse(
            certificate_id=c.id,
            certificate_code=c.certificate_code,
            recipient_name=c.recipient_name,
            recipient_email=c.recipient_email,
            file_name=c.file_name,
            file_size_bytes=c.file_size_bytes,
            verification_hash=c.verification_hash,
            download_url=f"{BASE_URL}/api/v1/certificates/{c.id}/download",
            created_at=c.created_at
        )
        for c in job.certificates
    ]

    failure_responses = [
        FailureItemResponse(
            recipient_name=f.recipient_name,
            recipient_email=f.recipient_email,
            error_reason=f.error_reason,
            failed_at=f.failed_at
        )
        for f in job.failures
    ]

    download_all = f"{BASE_URL}/api/v1/jobs/{job.id}/download-all" if job.success_count > 0 else None

    return JobDetailResponse(
        job_id=job.id,
        status=job.status,
        event_name=job.event_name,
        issuer_name=job.issuer_name,
        issue_date=job.issue_date,
        total_count=job.total_count,
        processed_count=job.processed_count,
        success_count=job.success_count,
        failure_count=job.failure_count,
        progress_percentage=job.progress_percentage,
        created_at=job.created_at,
        completed_at=job.completed_at,
        certificates=cert_responses,
        failures=failure_responses,
        download_all_url=download_all
    )


@app.get("/api/v1/certificates/{certificate_id}/download", tags=["Certificates"])
def download_certificate(certificate_id: str, db: Session = Depends(get_db)):
    """
    Downloads an individual certificate PDF file.
    """
    cert = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail=f"Certificate '{certificate_id}' not found.")

    if not os.path.exists(cert.file_path):
        raise HTTPException(status_code=404, detail="Certificate PDF file is missing from storage.")

    return FileResponse(
        path=cert.file_path,
        media_type="application/pdf",
        filename=cert.file_name,
        headers={"Content-Disposition": f'attachment; filename="{cert.file_name}"'}
    )


@app.get("/api/v1/jobs/{job_id}/download-all", tags=["Jobs"])
def download_all_certificates_zip(job_id: str, db: Session = Depends(get_db)):
    """
    Creates and streams a zip archive containing all generated certificate PDFs for a job.
    Includes a manifest.csv file.
    """
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    if job.success_count == 0:
        raise HTTPException(status_code=400, detail="Job has 0 successfully generated certificates.")

    zip_path = create_job_zip_archive(db, job)

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=f"Job_{job.id[:8]}_Certificates.zip",
        headers={"Content-Disposition": f'attachment; filename="Job_{job.id[:8]}_Certificates.zip"'}
    )


@app.get("/api/v1/certificates/verify/{certificate_code}", response_model=CertificateVerifyResponse, tags=["Verification"])
def verify_certificate(certificate_code: str, db: Session = Depends(get_db)):
    """
    Public verification endpoint to authenticate a certificate by code or scanned QR.
    """
    cert = db.query(Certificate).filter(Certificate.certificate_code == certificate_code).first()
    if not cert:
        raise HTTPException(
            status_code=404,
            detail=f"Certificate code '{certificate_code}' is not valid or was not issued by our system."
        )

    job = cert.job
    return CertificateVerifyResponse(
        is_valid=True,
        certificate_code=cert.certificate_code,
        recipient_name=cert.recipient_name,
        recipient_email=cert.recipient_email,
        event_name=job.event_name,
        issuer_name=job.issuer_name,
        issue_date=job.issue_date,
        verification_hash=cert.verification_hash,
        issued_at=cert.created_at,
        download_url=f"{BASE_URL}/api/v1/certificates/{cert.id}/download",
        message="Official Verified Certificate issued by AusIndia Education Initiative."
    )


@app.get("/", response_class=HTMLResponse, tags=["Web UI"])
@app.get("/dashboard", response_class=HTMLResponse, tags=["Web UI"])
def serve_dashboard():
    """Serves the interactive Bulk Certificate Generator Web Dashboard."""
    index_path = BASE_DIR / "app" / "static" / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h2>Welcome to Bulk Certificate Generator API. Visit <a href='/docs'>/docs</a> for Swagger API.</h2>")
