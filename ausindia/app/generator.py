import os
import io
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

import qrcode
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from app.config import CERTIFICATES_DIR, BASE_URL

class CertificateGenerator:
    """
    Renders professional, vector-grade A4 landscape certificate PDFs
    with dynamic QR verification codes, cryptographic hashes, and ornamental borders.
    """

    WIDTH, HEIGHT = landscape(A4)  # 841.89 x 595.27 points

    @classmethod
    def generate(
        cls,
        certificate_code: str,
        recipient_name: str,
        recipient_email: str,
        event_name: str,
        issuer_name: str,
        issue_date: str
    ) -> Tuple[str, str, int, str]:
        """
        Generates certificate PDF and returns (file_path, file_name, file_size_bytes, verification_hash).
        """
        # Calculate verification hash
        hash_payload = f"{certificate_code}|{recipient_name}|{recipient_email}|{event_name}|{issue_date}".encode("utf-8")
        verification_hash = hashlib.sha256(hash_payload).hexdigest()

        file_name = f"Certificate_{certificate_code}.pdf"
        file_path = CERTIFICATES_DIR / file_name

        # Create canvas
        c = canvas.Canvas(str(file_path), pagesize=landscape(A4))
        c.setTitle(f"Certificate of Completion - {recipient_name}")
        c.setAuthor(issuer_name)
        c.setSubject(event_name)

        # 1. Subtle warm background
        c.setFillColor(colors.HexColor("#fbfaf7"))
        c.rect(0, 0, cls.WIDTH, cls.HEIGHT, fill=True, stroke=False)

        # 2. Outer decorative borders
        # Deep navy outer border
        c.setStrokeColor(colors.HexColor("#0f172a"))
        c.setLineWidth(4)
        c.rect(20, 20, cls.WIDTH - 40, cls.HEIGHT - 40, fill=False, stroke=True)

        # Gold inner border
        c.setStrokeColor(colors.HexColor("#d97706"))
        c.setLineWidth(1.5)
        c.rect(26, 26, cls.WIDTH - 52, cls.HEIGHT - 52, fill=False, stroke=True)

        # Corner corner ornaments
        cls._draw_corner_ornaments(c, 26, 26, cls.WIDTH - 52, cls.HEIGHT - 52)

        # 3. Header Ribbon / Organization Name
        c.setFillColor(colors.HexColor("#d97706"))
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(cls.WIDTH / 2.0, cls.HEIGHT - 75, issuer_name.upper())

        # 4. Certificate Title
        c.setFillColor(colors.HexColor("#0f172a"))
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(cls.WIDTH / 2.0, cls.HEIGHT - 115, "CERTIFICATE OF ACHIEVEMENT")

        # Small decorative divider under title
        c.setStrokeColor(colors.HexColor("#d97706"))
        c.setLineWidth(2)
        c.line(cls.WIDTH / 2.0 - 90, cls.HEIGHT - 128, cls.WIDTH / 2.0 + 90, cls.HEIGHT - 128)

        # 5. Presentation line
        c.setFillColor(colors.HexColor("#64748b"))
        c.setFont("Helvetica", 12)
        c.drawCentredString(cls.WIDTH / 2.0, cls.HEIGHT - 165, "THIS IS PROUDLY PRESENTED TO")

        # 6. Recipient Name (Prominent Hero Element)
        c.setFillColor(colors.HexColor("#0f172a"))
        c.setFont("Helvetica-Bold", 32)
        c.drawCentredString(cls.WIDTH / 2.0, cls.HEIGHT - 215, recipient_name)

        # Underline for name
        name_width = c.stringWidth(recipient_name, "Helvetica-Bold", 32)
        line_padding = 24
        c.setStrokeColor(colors.HexColor("#d97706"))
        c.setLineWidth(1)
        c.line(
            cls.WIDTH / 2.0 - (name_width / 2.0 + line_padding),
            cls.HEIGHT - 225,
            cls.WIDTH / 2.0 + (name_width / 2.0 + line_padding),
            cls.HEIGHT - 225
        )

        # 7. Citation Body
        c.setFillColor(colors.HexColor("#475569"))
        c.setFont("Helvetica", 12)
        c.drawCentredString(
            cls.WIDTH / 2.0,
            cls.HEIGHT - 265,
            "for successfully completing the course curriculum and demonstrating verified excellence in"
        )

        # 8. Course / Event Title
        c.setFillColor(colors.HexColor("#1e3a8a"))
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(cls.WIDTH / 2.0, cls.HEIGHT - 305, event_name)

        # 9. Bottom Section: Signatures, Seal & Security QR Code
        # Left signature block
        sign_y = 120
        c.setStrokeColor(colors.HexColor("#94a3b8"))
        c.setLineWidth(1)
        c.line(90, sign_y, 250, sign_y)

        c.setFillColor(colors.HexColor("#0f172a"))
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(170, sign_y - 18, "AUTHORIZED SIGNATURE")
        c.setFillColor(colors.HexColor("#64748b"))
        c.setFont("Helvetica", 9)
        c.drawCentredString(170, sign_y - 32, f"Director, {issuer_name}")

        # Date block
        c.setFillColor(colors.HexColor("#0f172a"))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(90, sign_y - 58, "ISSUE DATE:")
        c.setFillColor(colors.HexColor("#475569"))
        c.setFont("Helvetica", 10)
        c.drawString(170, sign_y - 58, issue_date)

        # Center: Golden Medallion / Seal
        cls._draw_gold_seal(c, cls.WIDTH / 2.0, sign_y - 15)

        # Right block: Dynamic QR Code & Security Verification
        verify_url = f"{BASE_URL}/api/v1/certificates/verify/{certificate_code}"
        cls._draw_qr_code(c, verify_url, cls.WIDTH - 210, sign_y - 35, size=65)

        # Certificate ID and security hash
        c.setFillColor(colors.HexColor("#0f172a"))
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(cls.WIDTH - 225, sign_y - 48, f"ID: {certificate_code}")
        c.setFillColor(colors.HexColor("#94a3b8"))
        c.setFont("Helvetica", 6.5)
        c.drawString(cls.WIDTH - 225, sign_y - 58, f"HASH: {verification_hash[:20]}...")
        c.drawString(cls.WIDTH - 225, sign_y - 68, "Scan QR to verify tamper-proof status")

        # Save PDF
        c.showPage()
        c.save()

        file_size_bytes = os.path.getsize(file_path)
        return str(file_path), file_name, file_size_bytes, verification_hash

    @classmethod
    def _draw_corner_ornaments(cls, c: canvas.Canvas, x: float, y: float, w: float, h: float):
        """Draws classic geometric corner flourishes."""
        ornament_size = 18
        c.setStrokeColor(colors.HexColor("#d97706"))
        c.setLineWidth(1.5)

        # Bottom-Left
        c.line(x, y + ornament_size, x + ornament_size, y)
        # Top-Left
        c.line(x, y + h - ornament_size, x + ornament_size, y + h)
        # Bottom-Right
        c.line(x + w - ornament_size, y, x + w, y + ornament_size)
        # Top-Right
        c.line(x + w - ornament_size, y + h, x + w, y + h - ornament_size)

    @classmethod
    def _draw_gold_seal(cls, c: canvas.Canvas, cx: float, cy: float):
        """Draws vector gold excellence seal in center."""
        # Outer gold circle
        c.setFillColor(colors.HexColor("#d97706"))
        c.circle(cx, cy, 32, fill=True, stroke=False)
        # Inner white ring
        c.setStrokeColor(colors.white)
        c.setLineWidth(1)
        c.circle(cx, cy, 28, fill=False, stroke=True)
        # Inner deep navy core
        c.setFillColor(colors.HexColor("#0f172a"))
        c.circle(cx, cy, 26, fill=True, stroke=False)
        # Seal Star & Text
        c.setFillColor(colors.HexColor("#f59e0b"))
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(cx, cy - 4, "★")
        c.setFont("Helvetica-Bold", 6.5)
        c.drawCentredString(cx, cy + 12, "OFFICIAL")
        c.drawCentredString(cx, cy - 18, "SEAL")

    @classmethod
    def _draw_qr_code(cls, c: canvas.Canvas, data: str, x: float, y: float, size: float = 65):
        """Generates dynamic QR code and stamps directly onto canvas."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=4,
            border=1
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0f172a", back_color="white")

        temp_buffer = io.BytesIO()
        img.save(temp_buffer, format="PNG")
        temp_buffer.seek(0)

        from reportlab.lib.utils import ImageReader
        image_reader = ImageReader(temp_buffer)
        c.drawImage(image_reader, x, y, width=size, height=size)
