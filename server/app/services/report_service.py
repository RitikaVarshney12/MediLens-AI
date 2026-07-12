import re
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.report import Report
from app.services.storage_service import StorageError, upload_file_to_storage

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
}
MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def sanitize_filename(filename: str) -> str:
    name = filename.strip().replace(" ", "_")
    name = re.sub(r"[^a-zA-Z0-9._-]", "", name)
    return name or "report"


def validate_upload(filename: str, content_type: str | None, size: int) -> str:
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Allowed types: PDF, JPG, JPEG, PNG.",
        )

    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file content type.",
        )

    if size == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty.")

    if size > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit.",
        )

    return extension


async def create_report(db: Session, user_id: str, file: UploadFile) -> Report:
    content = await file.read()
    size = len(content)

    extension = validate_upload(file.filename or "", file.content_type, size)
    safe_name = sanitize_filename(file.filename or "report")
    storage_path = f"{user_id}/{uuid.uuid4()}_{safe_name}"

    try:
        await upload_file_to_storage(storage_path, content, file.content_type or "")
    except StorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to upload file to storage.",
        ) from exc

    report = Report(
        user_id=user_id,
        file_name=safe_name,
        file_type=extension,
        file_size=size,
        storage_path=storage_path,
        status="uploaded",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return report