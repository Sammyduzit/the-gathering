import os

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://dev:password@localhost:5432/thegathering")

    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    APP_NAME = "The Gathering API"
    DEBUG = True


settings = Settings()
