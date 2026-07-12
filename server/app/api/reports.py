from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.schemas.report import ReportOut, UploadResponse
from app.services.report_service import create_report

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_report(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> UploadResponse:
    report = await create_report(db, user_id, file)
    return UploadResponse(
        report=ReportOut.model_validate(report),
        message="Report uploaded successfully.",
    )