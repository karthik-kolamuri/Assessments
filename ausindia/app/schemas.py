import re
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

class RecipientInput(BaseModel):
    name: str = Field(..., description="Full legal name of the recipient")
    email: str = Field(..., description="Valid email address of the recipient")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata such as grade, rank, etc.")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Recipient name cannot be empty or whitespace only.")
        if len(cleaned) < 2:
            raise ValueError("Recipient name must have at least 2 characters.")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if not re.match(EMAIL_REGEX, cleaned):
            raise ValueError(f"Invalid email address format: '{v}'")
        return cleaned


class BulkJobCreateRequest(BaseModel):
    event_name: str = Field(..., min_length=2, max_length=255, description="Name of the course, event, or workshop")
    issuer_name: Optional[str] = Field(default="AusIndia Education Initiative", max_length=255, description="Organization issuing certificate")
    issue_date: Optional[str] = Field(default=None, description="Formatted issue date (defaults to today)")
    recipients: List[RecipientInput] = Field(..., min_length=1, description="List of recipient items")


class JobCreateResponse(BaseModel):
    job_id: str
    status: str
    event_name: str
    total_recipients: int
    created_at: datetime
    status_url: str
    message: str


class CertificateItemResponse(BaseModel):
    certificate_id: str
    certificate_code: str
    recipient_name: str
    recipient_email: str
    file_name: str
    file_size_bytes: int
    verification_hash: str
    download_url: str
    created_at: datetime


class FailureItemResponse(BaseModel):
    recipient_name: Optional[str]
    recipient_email: Optional[str]
    error_reason: str
    failed_at: datetime


class JobDetailResponse(BaseModel):
    job_id: str
    status: str
    event_name: str
    issuer_name: str
    issue_date: str
    total_count: int
    processed_count: int
    success_count: int
    failure_count: int
    progress_percentage: float
    created_at: datetime
    completed_at: Optional[datetime]
    certificates: List[CertificateItemResponse]
    failures: List[FailureItemResponse]
    download_all_url: Optional[str]


class CertificateVerifyResponse(BaseModel):
    is_valid: bool
    certificate_code: str
    recipient_name: str
    recipient_email: str
    event_name: str
    issuer_name: str
    issue_date: str
    verification_hash: str
    issued_at: datetime
    download_url: str
    message: str


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    timestamp: datetime
