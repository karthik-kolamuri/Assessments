import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_name = Column(String(255), nullable=False)
    issuer_name = Column(String(255), nullable=False)
    issue_date = Column(String(100), nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)  # PENDING, PROCESSING, COMPLETED, PARTIALLY_COMPLETED, FAILED
    total_count = Column(Integer, default=0, nullable=False)
    processed_count = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    failure_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    certificates = relationship("Certificate", back_populates="job", cascade="all, delete-orphan", order_by="Certificate.created_at")
    failures = relationship("JobFailure", back_populates="job", cascade="all, delete-orphan", order_by="JobFailure.failed_at")

    @property
    def progress_percentage(self) -> float:
        if self.total_count == 0:
            return 100.0 if self.status in ["COMPLETED", "PARTIALLY_COMPLETED"] else 0.0
        return round((self.processed_count / self.total_count) * 100.0, 2)


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    certificate_code = Column(String(64), unique=True, index=True, nullable=False)
    recipient_name = Column(String(255), nullable=False)
    recipient_email = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, default=0, nullable=False)
    verification_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    job = relationship("GenerationJob", back_populates="certificates")


class JobFailure(Base):
    __tablename__ = "job_failures"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_name = Column(String(255), nullable=True)
    recipient_email = Column(String(255), nullable=True)
    error_reason = Column(Text, nullable=False)
    failed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    job = relationship("GenerationJob", back_populates="failures")
