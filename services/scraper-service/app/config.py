from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB: str
    RABBITMQ_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
