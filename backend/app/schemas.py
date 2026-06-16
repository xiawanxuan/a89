import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DamageRegionCreate(BaseModel):
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)
    width: int = Field(..., gt=0)
    height: int = Field(..., gt=0)


class DamageRegionOut(BaseModel):
    id: uuid.UUID
    x: int
    y: int
    width: int
    height: int
    repaired_path: str | None = None

    class Config:
        from_attributes = True


class RepairTaskCreate(BaseModel):
    regions: list[DamageRegionCreate] = Field(..., min_length=1)


class RepairTaskOut(BaseModel):
    id: uuid.UUID
    filename: str
    original_path: str
    repaired_path: str | None = None
    quality_score: float | None = None
    selected_version_id: uuid.UUID | None = None
    status: str
    created_at: datetime
    completed_at: datetime | None = None
    regions: list[DamageRegionOut] = []
    versions: list["RepairVersionOut"] = []

    class Config:
        from_attributes = True


class RepairVersionOut(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    version_number: int
    repaired_path: str
    quality_score: float
    created_at: datetime
    is_selected: int

    class Config:
        from_attributes = True


class SelectVersionRequest(BaseModel):
    task_id: uuid.UUID
    version_id: uuid.UUID


RepairTaskOut.model_rebuild()


class BatchTaskOut(BaseModel):
    id: uuid.UUID
    total_count: int
    completed_count: int
    failed_count: int
    status: str
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class BatchItemOut(BaseModel):
    id: uuid.UUID
    batch_id: uuid.UUID
    task_id: uuid.UUID | None = None
    filename: str
    status: str

    class Config:
        from_attributes = True


class BatchTaskDetailOut(BatchTaskOut):
    items: list[BatchItemOut] = []


class UploadResponse(BaseModel):
    task_id: uuid.UUID
    filename: str
    original_path: str


class RepairRequest(BaseModel):
    task_id: uuid.UUID
    regions: list[DamageRegionCreate]


class BatchUploadResponse(BaseModel):
    batch_id: uuid.UUID
    total_count: int
