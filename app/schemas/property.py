import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PropertyCreate(BaseModel):
    user_id: uuid.UUID | None = None
    address: str
    property_type: str
    improvement_basis: float | None = None


class ImageUpload(BaseModel):
    property_id: uuid.UUID
    image_url: str


class DetectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_id: int
    label: str
    confidence: float
    normalized_label: str | None = None


class ImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: uuid.UUID
    image_url: str
    uploaded_at: datetime
    detections: list[DetectionResponse] = []


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: uuid.UUID
    asset_name: str
    quantity: int
    asset_life: int


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: uuid.UUID
    report_url: str
    created_at: datetime


class PropertyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None
    address: str
    property_type: str
    improvement_basis: float | None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    images: list[ImageResponse] = []
    assets: list[AssetResponse] = []
    reports: list[ReportResponse] = []

