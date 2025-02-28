from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6000"
    BATCH_SIZE: int = 100
    PROCESSING_WORKERS: int = 10
    NUM_WORKERS: int = 3
    DB_PATH: str = "/Users/vinit.kumar/Desktop/python-play/order_processing_system/rdl.db"
    DB_ECHO_LOG: bool = True
    WORKER_PROCESSES: int = 1
    
    class Config:
        env_file = ".env"

settings = Settings()