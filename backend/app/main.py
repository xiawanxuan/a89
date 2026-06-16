import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routers import upload, repair, batch, history

app = FastAPI(title="古彝文手稿修复系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPAIR_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/repairs", StaticFiles(directory=settings.REPAIR_DIR), name="repairs")

app.include_router(upload.router, prefix="/api/upload", tags=["上传"])
app.include_router(repair.router, prefix="/api/repair", tags=["修复"])
app.include_router(batch.router, prefix="/api/batch", tags=["批量处理"])
app.include_router(history.router, prefix="/api/history", tags=["历史记录"])


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "古彝文手稿修复系统"}
