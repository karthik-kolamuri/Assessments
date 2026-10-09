import os
import csv
import io
import zipfile
import secrets
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from app.config import CERTIFICATES_DIR, TEMP_DIR, BASE_URL
from app.database import SessionLocal
from app.models import GenerationJob, Certificate, JobFailure
from app.schemas import RecipientInput, BulkJobCreateRequest
from app.generator import CertificateGenerator

logger = logging.getLogger("bulk_cert_generator")
logging.basicConfig(level=logging.INFO)

def generate_certificate_code() -> str:
    """Generates unique, user-friendly certificate identifier, e.g. CERT-2026-A8F29D"""
    year = datetime.now().year
    random_token = secrets.token_hex(4).upper()
    return f"CERT-{year}-{random_token}"

def create_bulk_job(db: Session, request: BulkJobCreateRequest) -> GenerationJob:
    """
    Initializes a new bulk certificate generation job in the database.
    """
    issue_date = request.issue_date or datetime.now().strftime("%B %d, %Y")
    
    job = GenerationJob(
        event_name=request.event_name.strip(),
        issuer_name=request.issuer_name.strip() if request.issuer_name else "AusIndia Education Initiative",
        issue_date=issue_date,
        status="PENDING",
        total_count=len(request.recipients),
        processed_count=0,
        success_count=0,
        failure_count=0
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def execute_background_generation(job_id: str, recipients_data: List[Dict[str, Any]]):
    """
    Asynchronously processes the list of recipients in the background.
    Guarantees isolated failure handling: failure on one recipient does not stop others.
    """
    db = SessionLocal()
    try:
        job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found in database for background processing.")
            return

        job.status = "PROCESSING"
        db.commit()

        for index, item in enumerate(recipients_data):
            recipient_name = item.get("name", "").strip() if item.get("name") else ""
            recipient_email = item.get("email", "").strip().lower() if item.get("email") else ""

            # 1. Validation check
            if not recipient_name or len(recipient_name) < 2:
                failure = JobFailure(
                    job_id=job.id,
                    recipient_name=recipient_name or "[Missing Name]",
                    recipient_email=recipient_email or "[Missing Email]",
                    error_reason="Recipient name is missing, empty, or shorter than 2 characters."
                )
                db.add(failure)
                job.failure_count += 1
                job.processed_count += 1
                db.commit()
                continue

            if not recipient_email or "@" not in recipient_email or "." not in recipient_email:
                failure = JobFailure(
                    job_id=job.id,
                    recipient_name=recipient_name,
                    recipient_email=recipient_email or "[Missing Email]",
                    error_reason=f"Invalid email address: '{recipient_email}'."
                )
                db.add(failure)
                job.failure_count += 1
                job.processed_count += 1
                db.commit()
                continue

            # 2. Certificate Generation with fault isolation
            try:
                cert_code = generate_certificate_code()
                
                # Render PDF
                file_path, file_name, file_size, vhash = CertificateGenerator.generate(
                    certificate_code=cert_code,
                    recipient_name=recipient_name,
                    recipient_email=recipient_email,
                    event_name=job.event_name,
                    issuer_name=job.issuer_name,
                    issue_date=job.issue_date
                )

                # Persist certificate record
                cert = Certificate(
                    job_id=job.id,
                    certificate_code=cert_code,
                    recipient_name=recipient_name,
                    recipient_email=recipient_email,
                    file_path=file_path,
                    file_name=file_name,
                    file_size_bytes=file_size,
                    verification_hash=vhash
                )
                db.add(cert)
                job.success_count += 1
                job.processed_count += 1
                db.commit()

            except Exception as e:
                db.rollback()
                logger.exception(f"Error generating certificate for {recipient_name} ({recipient_email}): {e}")
                failure = JobFailure(
                    job_id=job.id,
                    recipient_name=recipient_name,
                    recipient_email=recipient_email,
                    error_reason=f"Generation failed: {str(e)}"
                )
                db.add(failure)
                job.failure_count += 1
                job.processed_count += 1
                db.commit()

        # Finalize job status
        job.total_count = len(recipients_data)
        job.completed_at = datetime.now(timezone.utc)
        if job.failure_count > 0 and job.success_count > 0:
            job.status = "PARTIALLY_COMPLETED"
        elif job.success_count > 0 and job.failure_count == 0:
            job.status = "COMPLETED"
        else:
            job.status = "FAILED"

        db.commit()
        logger.info(f"Job {job_id} finished with status: {job.status} (Success: {job.success_count}, Failed: {job.failure_count})")

    except Exception as general_err:
        logger.exception(f"Unexpected fatal error in background job {job_id}: {general_err}")
        try:
            job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
            if job:
                job.status = "FAILED"
                job.completed_at = datetime.now(timezone.utc)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


def create_job_zip_archive(db: Session, job: GenerationJob) -> str:
    """
    Creates a zip archive containing all generated certificates and a manifest CSV.
    """
    zip_filename = f"Job_{job.id}_Certificates.zip"
    zip_path = TEMP_DIR / zip_filename

    # Query all successful certificates
    certificates = db.query(Certificate).filter(Certificate.job_id == job.id).all()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Add each PDF
        for cert in certificates:
            if os.path.exists(cert.file_path):
                zf.write(cert.file_path, arcname=f"certificates/{cert.file_name}")

        # 2. Add manifest.csv
        manifest_buffer = io.StringIO()
        writer = csv.writer(manifest_buffer)
        writer.writerow(["Certificate Code", "Recipient Name", "Recipient Email", "Event Name", "Issue Date", "Verification Hash", "File Name"])
        for cert in certificates:
            writer.writerow([
                cert.certificate_code,
                cert.recipient_name,
                cert.recipient_email,
                job.event_name,
                job.issue_date,
                cert.verification_hash,
                cert.file_name
            ])
        zf.writestr("manifest.csv", manifest_buffer.getvalue())

    return str(zip_path)
