import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel


class Property(BaseModel):
    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    address: Mapped[str] = mapped_column(String(length=255), nullable=False)
    property_type: Mapped[str] = mapped_column(String(length=50), nullable=False)
    improvement_basis: Mapped[float | None] = mapped_column(Float, nullable=True)

    images: Mapped[list["Image"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    assets: Mapped[list["Asset"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    reports: Mapped[list["Report"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Image(BaseModel):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_url: Mapped[str] = mapped_column(String(length=500), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    property: Mapped[Property] = relationship(back_populates="images")
    detections: Mapped[list["Detection"]] = relationship(
        back_populates="image",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Detection(BaseModel):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    image_id: Mapped[int] = mapped_column(
        ForeignKey("images.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(length=100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    normalized_label: Mapped[str | None] = mapped_column(String(length=100), nullable=True)

    image: Mapped[Image] = relationship(back_populates="detections")


class Asset(BaseModel):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    asset_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    asset_life: Mapped[int] = mapped_column(nullable=False, doc="Asset life in years")

    property: Mapped[Property] = relationship(back_populates="assets")


class Report(BaseModel):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    report_url: Mapped[str] = mapped_column(String(length=500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    property: Mapped[Property] = relationship(back_populates="reports")

