import os
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(os.path.dirname(__file__), ".env")

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6000"
    BATCH_SIZE: int = 100
    PROCESSING_WORKERS: int = 10
    NUM_WORKERS: int = 3
    DB_PATH: str = "/Users/vinit.kumar/order-process-system/rdl.db"
    DB_ECHO_LOG: bool = True
    WORKER_PROCESSES: int = 1
    
    model_config = SettingsConfigDict(env_file=DOTENV)

settings = Settings()