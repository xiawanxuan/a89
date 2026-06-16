import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io

from app.config import settings
from app.utils.image_utils import save_upload_image, validate_image_size
from app.models import RepairTask
from app.database import async_session
from app.schemas import UploadResponse

router = APIRouter()


@router.post("/single", response_model=UploadResponse)
async def upload_single_image(file: UploadFile = File(...)):
    allowed_types = {"image/png", "image/jpeg", "image/bmp", "image/tiff"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的图像格式，请上传PNG/JPG/BMP/TIFF格式")

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图像文件过大，请控制在20MB以内")

    try:
        image = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="无法解析图像文件")

    if not validate_image_size(image):
        image.thumbnail((settings.MAX_IMAGE_SIZE, settings.MAX_IMAGE_SIZE), Image.LANCZOS)

    task_id_str, saved_path = save_upload_image(image, file.filename or "upload.png")

    async with async_session() as session:
        task = RepairTask(
            id=uuid.UUID(task_id_str),
            filename=file.filename or "upload.png",
            original_path=saved_path,
            status="pending",
        )
        session.add(task)
        await session.commit()

    return UploadResponse(
        task_id=uuid.UUID(task_id_str),
        filename=file.filename or "upload.png",
        original_path=saved_path,
    )


@router.post("/batch", response_model=dict)
async def upload_batch_zip(file: UploadFile = File(...)):
    if file.content_type not in {"application/zip", "application/x-zip-compressed"}:
        raise HTTPException(status_code=400, detail="请上传ZIP格式的压缩包")

    content = await file.read()
    if len(content) > 500 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="ZIP文件过大，请控制在500MB以内")

    from app.utils.image_utils import extract_zip_images, save_upload_image
    from app.models import BatchTask, BatchItem

    zip_path = os.path.join(settings.UPLOAD_DIR, f"batch_{uuid.uuid4()}.zip")
    with open(zip_path, "wb") as f:
        f.write(content)

    images = extract_zip_images(zip_path)
    if not images:
        os.remove(zip_path)
        raise HTTPException(status_code=400, detail="ZIP包中未找到有效图像文件")

    batch_id = uuid.uuid4()

    async with async_session() as session:
        batch = BatchTask(
            id=batch_id,
            total_count=len(images),
            status="pending",
        )
        session.add(batch)

        for basename, img in images:
            task_id_str, saved_path = save_upload_image(img, basename)
            task = RepairTask(
                id=uuid.UUID(task_id_str),
                filename=basename,
                original_path=saved_path,
                status="pending",
            )
            session.add(task)

            item = BatchItem(
                batch_id=batch_id,
                task_id=uuid.UUID(task_id_str),
                filename=basename,
                status="pending",
            )
            session.add(item)

        await session.commit()

    os.remove(zip_path)

    from app.tasks.repair_tasks import repair_batch_task
    repair_batch_task.delay(str(batch_id))

    return {"batch_id": str(batch_id), "total_count": len(images)}
