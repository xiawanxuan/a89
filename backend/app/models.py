import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Float, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RepairTask(Base):
    __tablename__ = "repair_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(256), nullable=False)
    original_path: Mapped[str] = mapped_column(Text, nullable=False)
    repaired_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    regions: Mapped[list["DamageRegion"]] = relationship(back_populates="task", cascade="all, delete-orphan")


class DamageRegion(Base):
    __tablename__ = "damage_regions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repair_tasks.id"), nullable=False)
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    repaired_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    task: Mapped["RepairTask"] = mapped_column(back_populates="regions")


class BatchTask(Base):
    __tablename__ = "batch_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    total_count: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    items: Mapped[list["BatchItem"]] = relationship(back_populates="batch_task", cascade="all, delete-orphan")


class BatchItem(Base):
    __tablename__ = "batch_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("batch_tasks.id"), nullable=False)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repair_tasks.id"), nullable=True)
    filename: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending")

    batch_task: Mapped["BatchTask"] = mapped_column(back_populates="items")
