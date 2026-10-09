import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'storage' / 'certificates.db'}")

# Storage paths
STORAGE_DIR = BASE_DIR / "storage"
CERTIFICATES_DIR = STORAGE_DIR / "certificates"
TEMP_DIR = STORAGE_DIR / "temp"

# Ensure directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
CERTIFICATES_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Application metadata
APP_NAME = "Bulk Certificate Generator API"
APP_VERSION = "1.0.0"
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
