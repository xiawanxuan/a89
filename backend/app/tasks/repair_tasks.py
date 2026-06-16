import os
import uuid
from datetime import datetime

from celery import shared_task, group
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import torch

from app.config import settings
from app.models import RepairTask, DamageRegion, BatchTask, BatchItem
from app.utils.image_utils import load_image, save_repair_image, save_full_repair_image
from app.gan_model.inference import repair_region, detect_damage_regions, get_device


def _get_sync_session():
    engine = create_engine(settings.DATABASE_URL_SYNC)
    Session = sessionmaker(bind=engine)
    return Session()


@shared_task(bind=True, time_limit=settings.SINGLE_REPAIR_TIMEOUT * 2, soft_time_limit=settings.SINGLE_REPAIR_TIMEOUT)
def repair_single_task(self, task_id: str, regions: list[dict]):
    session = _get_sync_session()
    try:
        task = session.query(RepairTask).filter(RepairTask.id == uuid.UUID(task_id)).first()
        if not task:
            return {"status": "error", "message": "Task not found"}

        task.status = "processing"
        session.commit()

        image = load_image(task.original_path)
        current_image = image.copy()

        for idx, region_data in enumerate(regions):
            x, y, w, h = region_data["x"], region_data["y"], region_data["width"], region_data["height"]
            current_image = repair_region(current_image, x, y, w, h)

            region_record = DamageRegion(
                task_id=task.id,
                x=x, y=y, width=w, height=h,
                repaired_path=save_repair_image(current_image, str(task.id), idx),
            )
            session.add(region_record)

        full_repair_path = save_full_repair_image(current_image, str(task.id))
        task.repaired_path = full_repair_path
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        session.commit()

        del image, current_image
        device = get_device()
        if device.type == "cuda":
            torch.cuda.empty_cache()

        return {"status": "completed", "task_id": task_id, "repaired_path": full_repair_path}

    except Exception as e:
        session.rollback()
        task = session.query(RepairTask).filter(RepairTask.id == uuid.UUID(task_id)).first()
        if task:
            task.status = "failed"
            session.commit()
        return {"status": "failed", "task_id": task_id, "error": str(e)}
    finally:
        session.close()


@shared_task(bind=True)
def repair_batch_task(self, batch_id: str):
    session = _get_sync_session()
    try:
        batch = session.query(BatchTask).filter(BatchTask.id == uuid.UUID(batch_id)).first()
        if not batch:
            return {"status": "error", "message": "Batch not found"}

        batch.status = "processing"
        session.commit()

        items = session.query(BatchItem).filter(BatchItem.batch_id == batch.id).all()

        for item in items:
            try:
                if item.task_id:
                    task = session.query(RepairTask).filter(RepairTask.id == item.task_id).first()
                    if task and task.status == "pending":
                        image = load_image(task.original_path)
                        detected_regions = detect_damage_regions(image)

                        current_image = image.copy()
                        for idx, region_data in enumerate(detected_regions):
                            current_image = repair_region(
                                current_image,
                                region_data["x"], region_data["y"],
                                region_data["width"], region_data["height"],
                            )
                            region_record = DamageRegion(
                                task_id=task.id, **region_data,
                                repaired_path=save_repair_image(current_image, str(task.id), idx),
                            )
                            session.add(region_record)

                        task.repaired_path = save_full_repair_image(current_image, str(task.id))
                        task.status = "completed"
                        task.completed_at = datetime.utcnow()

                        item.status = "completed"
                        batch.completed_count += 1

                        del image, current_image, detected_regions
                        device = get_device()
                        if device.type == "cuda":
                            torch.cuda.empty_cache()
                else:
                    item.status = "skipped"

            except Exception:
                item.status = "failed"
                batch.failed_count += 1
                if item.task_id:
                    task = session.query(RepairTask).filter(RepairTask.id == item.task_id).first()
                    if task:
                        task.status = "failed"

            session.commit()
            self.update_state(
                state="PROGRESS",
                meta={
                    "batch_id": batch_id,
                    "completed": batch.completed_count,
                    "failed": batch.failed_count,
                    "total": batch.total_count,
                },
            )

        all_done = batch.completed_count + batch.failed_count >= batch.total_count
        if all_done:
            batch.status = "completed"
            batch.completed_at = datetime.utcnow()
            session.commit()

        return {
            "status": batch.status,
            "batch_id": batch_id,
            "completed": batch.completed_count,
            "failed": batch.failed_count,
            "total": batch.total_count,
        }

    except Exception as e:
        session.rollback()
        batch = session.query(BatchTask).filter(BatchTask.id == uuid.UUID(batch_id)).first()
        if batch:
            batch.status = "failed"
            session.commit()
        return {"status": "failed", "batch_id": batch_id, "error": str(e)}
    finally:
        session.close()


@shared_task
def detect_damage_task(task_id: str) -> list[dict]:
    session = _get_sync_session()
    try:
        task = session.query(RepairTask).filter(RepairTask.id == uuid.UUID(task_id)).first()
        if not task:
            return []

        image = load_image(task.original_path)
        regions = detect_damage_regions(image)

        for region_data in regions:
            region_record = DamageRegion(task_id=task.id, **region_data)
            session.add(region_record)
        session.commit()

        return regions
    finally:
        session.close()
