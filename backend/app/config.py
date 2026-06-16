import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://yiman:yiman123@localhost:5432/yiman_repair"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://yiman:yiman123@localhost:5432/yiman_repair"
    CELERY_BROKER_URL: str = "amqp://yiman:yiman123@localhost:5672//"

    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    REPAIR_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "repairs")
    MODEL_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "gan_repair.pth")

    MAX_IMAGE_SIZE: int = 2000
    MAX_BATCH_SIZE: int = 50
    SINGLE_REPAIR_TIMEOUT: int = 10
    BATCH_REPAIR_TIMEOUT: int = 480

    GPU_DEVICE: str = "cuda:0"

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        extra = "ignore"


settings = Settings()
