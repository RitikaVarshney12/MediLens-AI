import logging
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.report import Report
from app.models.report_extraction import ReportExtraction
from app.services.medical_extractor import extract_medical_parameters
from app.services.ocr_service import OcrError, extract_text
from app.services.text_cleaning import clean_text

logger = logging.getLogger(__name__)


def _update_report_status(db, report_id: str, status_value: str) -> None:
    db.query(Report).filter(Report.id == report_id).update({"status": status_value})


def run_extraction_pipeline(report_id: str, content: bytes, file_type: str) -> None:
    """Runs as a FastAPI BackgroundTask. Opens its own DB session rather
    than reusing the request's session, which is torn down before
    background tasks run."""
    db = SessionLocal()

    try:
        extraction = ReportExtraction(
            report_id=report_id,
            ocr_status="processing",
            processing_started_at=datetime.now(timezone.utc),
        )
        db.add(extraction)
        _update_report_status(db, report_id, "processing")
        db.commit()
        db.refresh(extraction)

        try:
            raw_text = extract_text(content, file_type)
            cleaned_text = clean_text(raw_text)
            structured = extract_medical_parameters(cleaned_text)

            extraction.raw_text = cleaned_text
            extraction.structured_json = structured
            extraction.ocr_status = "completed"
            extraction.completed_at = datetime.now(timezone.utc)
            _update_report_status(db, report_id, "completed")

        except OcrError as exc:
            logger.error("OCR failed for report %s: %s", report_id, exc)
            extraction.ocr_status = "failed"
            extraction.completed_at = datetime.now(timezone.utc)
            _update_report_status(db, report_id, "failed")

        except Exception:  # noqa: BLE001 - must never let a background task crash silently
            logger.exception("Unexpected error extracting report %s", report_id)
            extraction.ocr_status = "failed"
            extraction.completed_at = datetime.now(timezone.utc)
            _update_report_status(db, report_id, "failed")

        db.commit()

    finally:
        db.close()