from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:123456%40@localhost:3306/event_db"

    SECRET_KEY: str = "event_secret_key"
    ALGORITHM: str = "HS256"
    EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
