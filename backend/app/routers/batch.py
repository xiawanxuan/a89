import uuid

from fastapi import APIRouter, HTTPException

from app.database import async_session
from app.models import BatchTask, BatchItem
from app.schemas import BatchTaskOut, BatchTaskDetailOut, BatchItemOut
from app.tasks.repair_tasks import repair_batch_task

router = APIRouter()


@router.get("/status/{batch_id}", response_model=BatchTaskDetailOut)
async def get_batch_status(batch_id: uuid.UUID):
    async with async_session() as session:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        stmt = select(BatchTask).where(BatchTask.id == batch_id).options(selectinload(BatchTask.items))
        batch = (await session.execute(stmt)).scalar_one_or_none()
        if not batch:
            raise HTTPException(status_code=404, detail="批量任务不存在")
        return BatchTaskDetailOut.model_validate(batch)


@router.get("/list", response_model=list[BatchTaskOut])
async def list_batch_tasks(skip: int = 0, limit: int = 20):
    async with async_session() as session:
        from sqlalchemy import select
        stmt = select(BatchTask).order_by(BatchTask.created_at.desc()).offset(skip).limit(limit)
        result = await session.execute(stmt)
        batches = result.scalars().all()
        return [BatchTaskOut.model_validate(b) for b in batches]


@router.post("/retry/{batch_id}", response_model=dict)
async def retry_batch(batch_id: uuid.UUID):
    async with async_session() as session:
        batch = await session.get(BatchTask, batch_id)
        if not batch:
            raise HTTPException(status_code=404, detail="批量任务不存在")

        batch.status = "pending"
        batch.completed_count = 0
        batch.failed_count = 0

        items = (await session.execute(
            select(BatchItem).where(BatchItem.batch_id == batch_id)
        )).scalars().all()

        for item in items:
            item.status = "pending"

        await session.commit()

    repair_batch_task.delay(str(batch_id))
    return {"batch_id": str(batch_id), "status": "queued"}


from sqlalchemy import select
