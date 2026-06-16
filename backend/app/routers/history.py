import uuid
from datetime import datetime

from fastapi import APIRouter, Query

from app.database import async_session
from app.models import RepairTask
from app.schemas import RepairTaskOut

router = APIRouter()


@router.get("/list", response_model=list[RepairTaskOut])
async def list_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with async_session() as session:
        stmt = select(RepairTask).options(selectinload(RepairTask.regions)).order_by(RepairTask.created_at.desc())

        if status:
            stmt = stmt.where(RepairTask.status == status)

        stmt = stmt.offset(skip).limit(limit)
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        return [RepairTaskOut.model_validate(t) for t in tasks]


@router.get("/detail/{task_id}", response_model=RepairTaskOut)
async def get_history_detail(task_id: uuid.UUID):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with async_session() as session:
        stmt = select(RepairTask).where(RepairTask.id == task_id).options(selectinload(RepairTask.regions))
        task = (await session.execute(stmt)).scalar_one_or_none()
        if not task:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="记录不存在")
        return RepairTaskOut.model_validate(task)


@router.delete("/{task_id}", response_model=dict)
async def delete_history(task_id: uuid.UUID):
    async with async_session() as session:
        task = await session.get(RepairTask, task_id)
        if not task:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="记录不存在")

        await session.delete(task)
        await session.commit()
        return {"message": "记录已删除"}
