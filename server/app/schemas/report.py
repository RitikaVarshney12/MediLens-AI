import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    file_name: str
    file_type: str
    file_size: int
    storage_path: str
    status: str
    uploaded_at: datetime


class UploadResponse(BaseModel):
    report: ReportOut
    message: str