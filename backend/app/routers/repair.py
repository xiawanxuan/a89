import uuid

from fastapi import APIRouter, HTTPException

from app.database import async_session
from app.models import RepairTask, DamageRegion, RepairVersion
from app.schemas import RepairRequest, RepairTaskOut, DamageRegionOut, RepairVersionOut, SelectVersionRequest
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


@router.post("/retry/{task_id}", response_model=dict)
async def retry_repair(task_id: uuid.UUID):
    async with async_session() as session:
        task = await session.get(RepairTask, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="修复任务不存在")
        if task.status not in ("completed", "failed"):
            raise HTTPException(status_code=400, detail=f"任务状态为{task.status}，无法重新修复")

        from sqlalchemy import select
        regions_stmt = select(DamageRegion).where(DamageRegion.task_id == task_id)
        regions = (await session.execute(regions_stmt)).scalars().all()
        if not regions:
            raise HTTPException(status_code=400, detail="未找到破损区域，请先框选区域")

        task.status = "queued"
        await session.commit()

    regions_list = [{"x": r.x, "y": r.y, "width": r.width, "height": r.height} for r in regions]
    repair_single_task.delay(str(task_id), regions_list)

    return {"task_id": str(task_id), "status": "queued", "message": "重新修复任务已提交"}


@router.post("/select-version", response_model=dict)
async def select_version(request: SelectVersionRequest):
    async with async_session() as session:
        task = await session.get(RepairTask, request.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="修复任务不存在")

        from sqlalchemy import select
        stmt = select(RepairVersion).where(
            RepairVersion.task_id == request.task_id,
            RepairVersion.id == request.version_id,
        )
        version = (await session.execute(stmt)).scalar_one_or_none()
        if not version:
            raise HTTPException(status_code=404, detail="修复版本不存在")

        all_stmt = select(RepairVersion).where(RepairVersion.task_id == request.task_id)
        all_versions = (await session.execute(all_stmt)).scalars().all()
        for v in all_versions:
            v.is_selected = 1 if v.id == request.version_id else 0

        task.selected_version_id = request.version_id
        task.repaired_path = version.repaired_path
        task.quality_score = version.quality_score

        await session.commit()

    return {"message": "版本已选中", "version_id": str(request.version_id)}


@router.get("/versions/{task_id}", response_model=list[RepairVersionOut])
async def list_versions(task_id: uuid.UUID):
    async with async_session() as session:
        from sqlalchemy import select

        stmt = select(RepairVersion).where(
            RepairVersion.task_id == task_id
        ).order_by(RepairVersion.version_number.desc())
        versions = (await session.execute(stmt)).scalars().all()
        return [RepairVersionOut.model_validate(v) for v in versions]


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

        stmt = select(RepairTask).where(RepairTask.id == task_id).options(
            selectinload(RepairTask.regions),
            selectinload(RepairTask.versions),
        )
        task = (await session.execute(stmt)).scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")

        task.versions.sort(key=lambda v: v.version_number, reverse=True)
        return RepairTaskOut.model_validate(task)
