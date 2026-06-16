import uuid

from fastapi import APIRouter, HTTPException

from app.database import async_session
from app.models import RepairTask, DamageRegion
from app.schemas import RepairRequest, RepairTaskOut, DamageRegionOut
from app.tasks.repair_tasks import repair_single_task, detect_damage_task

router = APIRouter()


@router.post("/start", response_model=dict)
async def start_repair(request: RepairRequest):
    async with async_session() as session:
        task = await session.get(RepairTask, request.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="修复任务不存在")
        if task.status not in ("pending",):
            raise HTTPException(status_code=400, detail=f"任务状态为{task.status}，无法启动修复")

        for region_data in request.regions:
            region = DamageRegion(
                task_id=task.id,
                x=region_data.x,
                y=region_data.y,
                width=region_data.width,
                height=region_data.height,
            )
            session.add(region)

        task.status = "queued"
        await session.commit()

    regions_list = [{"x": r.x, "y": r.y, "width": r.width, "height": r.height} for r in request.regions]
    repair_single_task.delay(str(request.task_id), regions_list)

    return {"task_id": str(request.task_id), "status": "queued", "message": "修复任务已提交"}


@router.post("/detect/{task_id}", response_model=list[DamageRegionOut])
async def detect_damage(task_id: uuid.UUID):
    async with async_session() as session:
        task = await session.get(RepairTask, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")

    result = detect_damage_task.delay(str(task_id))
    regions_data = result.get(timeout=30)

    async with async_session() as session:
        from sqlalchemy import select
        stmt = select(DamageRegion).where(DamageRegion.task_id == task_id)
        db_regions = (await session.execute(stmt)).scalars().all()
        return [DamageRegionOut.model_validate(r) for r in db_regions]


@router.get("/status/{task_id}", response_model=RepairTaskOut)
async def get_repair_status(task_id: uuid.UUID):
    async with async_session() as session:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        stmt = select(RepairTask).where(RepairTask.id == task_id).options(selectinload(RepairTask.regions))
        task = (await session.execute(stmt)).scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        return RepairTaskOut.model_validate(task)
