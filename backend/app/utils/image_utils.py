import os
import uuid
from datetime import datetime

from PIL import Image

from app.config import settings


def save_upload_image(image: Image.Image, filename: str) -> tuple[str, str]:
    task_id = str(uuid.uuid4())
    ext = os.path.splitext(filename)[1] or ".png"
    saved_name = f"{task_id}{ext}"
    saved_path = os.path.join(settings.UPLOAD_DIR, saved_name)
    image.save(saved_path, quality=95)
    return task_id, saved_path


def save_repair_image(image: Image.Image, task_id: str, region_index: int = 0) -> str:
    ext = ".png"
    saved_name = f"{task_id}_repair_{region_index}{ext}"
    saved_path = os.path.join(settings.REPAIR_DIR, saved_name)
    image.save(saved_path, quality=95)
    return saved_path


def save_full_repair_image(image: Image.Image, task_id: str) -> str:
    saved_name = f"{task_id}_repaired.png"
    saved_path = os.path.join(settings.REPAIR_DIR, saved_name)
    image.save(saved_path, quality=95)
    return saved_path


def load_image(path: str) -> Image.Image:
    image = Image.open(path).convert("RGB")
    return image


def validate_image_size(image: Image.Image, max_size: int = None) -> bool:
    max_dim = max_size or settings.MAX_IMAGE_SIZE
    w, h = image.size
    return w <= max_dim and h <= max_dim


def extract_zip_images(zip_path: str) -> list[tuple[str, Image.Image]]:
    import zipfile
    results = []
    allowed_ext = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}

    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in sorted(zf.namelist()):
            ext = os.path.splitext(name)[1].lower()
            if ext in allowed_ext and not name.startswith("__MACOSX"):
                try:
                    with zf.open(name) as f:
                        image = Image.open(f).convert("RGB")
                        basename = os.path.basename(name)
                        results.append((basename, image))
                except Exception:
                    continue

    return results[:settings.MAX_BATCH_SIZE]
