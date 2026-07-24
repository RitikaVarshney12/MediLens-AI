from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.schemas.report import ReportOut, UploadResponse
from app.services.extraction_service import run_extraction_pipeline
from app.services.report_service import create_report

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> UploadResponse:
    report = await create_report(db, user_id, file)

    # create_report() already consumed the stream; rewind to hand the same
    # bytes to the background OCR task without re-uploading or re-validating.
    await file.seek(0)
    content = await file.read()
    background_tasks.add_task(run_extraction_pipeline, str(report.id), content, report.file_type)

    return UploadResponse(
        report=ReportOut.model_validate(report),
        message="Report uploaded successfully. OCR processing started.",
    )