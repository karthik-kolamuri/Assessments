import os
import zipfile
import io
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db
from app.config import CERTIFICATES_DIR, TEMP_DIR

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Ensure database tables and storage directories are initialized."""
    init_db()
    CERTIFICATES_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    yield


def test_health_check():
    """Test system health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "version" in data


def test_create_generation_job_success():
    """Test submitting a valid certificate generation job."""
    payload = {
        "event_name": "AI & Cloud Engineering Summit 2026",
        "issuer_name": "AusIndia Education Initiative",
        "issue_date": "October 09, 2026",
        "recipients": [
            {"name": "Aarav Sharma", "email": "aarav.sharma@example.com"},
            {"name": "Priya Venkataraman", "email": "priya.v@example.com"}
        ]
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["total_recipients"] == 2
    assert "status_url" in data

    # Poll status until background task finishes
    job_id = data["job_id"]
    status_res = client.get(f"/api/v1/jobs/{job_id}")
    assert status_res.status_code == 200
    job_data = status_res.json()
    assert job_data["job_id"] == job_id
    assert job_data["total_count"] == 2


def test_input_validation_empty_recipients():
    """Test validation rejection when recipients list is empty."""
    payload = {
        "event_name": "Test Event",
        "recipients": []
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422  # Pydantic validation error


def test_input_validation_empty_name():
    """Test validation rejection when recipient name is whitespace or empty."""
    payload = {
        "event_name": "Test Event",
        "recipients": [
            {"name": "   ", "email": "valid@example.com"}
        ]
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422


def test_input_validation_invalid_email():
    """Test validation rejection when recipient email is malformed."""
    payload = {
        "event_name": "Test Event",
        "recipients": [
            {"name": "John Doe", "email": "not-a-valid-email"}
        ]
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422


def test_certificate_generation_and_job_progress():
    """Test end-to-end certificate generation, progress polling, and certificate output."""
    payload = {
        "event_name": "Python Backend Mastery",
        "issuer_name": "AusIndia Initiative",
        "issue_date": "October 09, 2026",
        "recipients": [
            {"name": "Karthik Kolamuri", "email": "karthik@example.com"},
            {"name": "Rohit Kulkarni", "email": "rohit@example.com"}
        ]
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 202
    job_id = response.json()["job_id"]

    # Poll status
    job_res = client.get(f"/api/v1/jobs/{job_id}")
    assert job_res.status_code == 200
    job_data = job_res.json()

    assert job_data["status"] == "COMPLETED"
    assert job_data["success_count"] == 2
    assert job_data["failure_count"] == 0
    assert job_data["progress_percentage"] == 100.0
    assert len(job_data["certificates"]) == 2

    # Check certificate details
    first_cert = job_data["certificates"][0]
    assert "certificate_code" in first_cert
    assert "download_url" in first_cert
    assert "verification_hash" in first_cert


def test_isolated_failure_handling():
    """
    Test handling an individual failure during generation.
    Submits a job through background execution where one recipient has invalid fields.
    Valid recipient must succeed; invalid recipient must be isolated and logged in failures list.
    """
    from app.service import create_bulk_job, execute_background_generation
    from app.database import SessionLocal
    from app.schemas import BulkJobCreateRequest, RecipientInput

    db = SessionLocal()
    req = BulkJobCreateRequest(
        event_name="Resilience & Fault Isolation Testing",
        issuer_name="AusIndia Testing Lab",
        issue_date="October 09, 2026",
        recipients=[
            RecipientInput(name="Valid User", email="valid.user@example.com"),
            RecipientInput(name="Another Valid", email="another.valid@example.com")
        ]
    )
    job = create_bulk_job(db, req)
    db.close()

    # Provide raw data with an intentionally corrupted item to test worker fault isolation
    recipients_data = [
        {"name": "Valid User", "email": "valid.user@example.com"},
        {"name": "Corrupted User", "email": "bad-email-no-domain"},  # Fails email validation
        {"name": "", "email": "empty.name@example.com"},             # Fails name validation
        {"name": "Another Valid", "email": "another.valid@example.com"}
    ]

    execute_background_generation(job.id, recipients_data)

    # Check job status
    status_res = client.get(f"/api/v1/jobs/{job.id}")
    assert status_res.status_code == 200
    data = status_res.json()

    assert data["status"] == "PARTIALLY_COMPLETED"
    assert data["success_count"] == 2
    assert data["failure_count"] == 2
    assert len(data["certificates"]) == 2
    assert len(data["failures"]) == 2

    # Verify failure reasons are clearly recorded
    reasons = [f["error_reason"] for f in data["failures"]]
    assert any("Invalid email" in r for r in reasons)
    assert any("name is missing" in r for r in reasons)


def test_download_individual_certificate():
    """Test downloading an individual generated certificate PDF."""
    payload = {
        "event_name": "Download Verification Event",
        "recipients": [{"name": "Download Test User", "email": "dl.test@example.com"}]
    }
    create_res = client.post("/api/v1/jobs", json=payload)
    job_id = create_res.json()["job_id"]

    job_data = client.get(f"/api/v1/jobs/{job_id}").json()
    cert_id = job_data["certificates"][0]["certificate_id"]

    dl_res = client.get(f"/api/v1/certificates/{cert_id}/download")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
    assert dl_res.content.startswith(b"%PDF")
    assert len(dl_res.content) > 1000


def test_download_all_zip_archive():
    """Test downloading all certificates for a job as a zip archive."""
    payload = {
        "event_name": "Batch Zip Event",
        "recipients": [
            {"name": "Participant One", "email": "p1@example.com"},
            {"name": "Participant Two", "email": "p2@example.com"}
        ]
    }
    create_res = client.post("/api/v1/jobs", json=payload)
    job_id = create_res.json()["job_id"]

    zip_res = client.get(f"/api/v1/jobs/{job_id}/download-all")
    assert zip_res.status_code == 200
    assert zip_res.headers["content-type"] == "application/zip"

    # Verify zip content
    with zipfile.ZipFile(io.BytesIO(zip_res.content)) as zf:
        namelist = zf.namelist()
        assert "manifest.csv" in namelist
        cert_files = [n for n in namelist if n.startswith("certificates/")]
        assert len(cert_files) == 2


def test_public_certificate_verification():
    """Test the public certificate verification endpoint."""
    payload = {
        "event_name": "Blockchain & Cryptography",
        "issuer_name": "AusIndia Institute",
        "issue_date": "October 09, 2026",
        "recipients": [{"name": "Satoshi Nakamoto", "email": "satoshi@example.com"}]
    }
    create_res = client.post("/api/v1/jobs", json=payload)
    job_id = create_res.json()["job_id"]
    job_data = client.get(f"/api/v1/jobs/{job_id}").json()
    cert_code = job_data["certificates"][0]["certificate_code"]

    # Verify valid code
    verify_res = client.get(f"/api/v1/certificates/verify/{cert_code}")
    assert verify_res.status_code == 200
    vdata = verify_res.json()
    assert vdata["is_valid"] is True
    assert vdata["certificate_code"] == cert_code
    assert vdata["recipient_name"] == "Satoshi Nakamoto"
    assert "verification_hash" in vdata

    # Verify invalid code returns 404
    bad_res = client.get("/api/v1/certificates/verify/NON-EXISTENT-CODE")
    assert bad_res.status_code == 404
