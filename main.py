from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from app.core.config import settings
from app.core.database import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown.
    """
    print("Starting...")
    create_tables()
    print("Database tables created")

    yield

    print("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Virtual meeting space with 3 type chat system",
    docs_url="/docs",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {"message": "Welcome to The Gathering!"}


@app.get("/test")
def test_endpoint():
    return {"status": "FastAPI works!", "project": "The Gathering"}


if __name__ == "__main__":
    print("API Documentation: http://localhost:8000/docs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )