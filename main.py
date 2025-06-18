from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from core.config import settings
from core.database import create_tables
from api.v1.endpoints.room_router import router as rooms_router
from api.v1.endpoints.auth_router import router as auth_router

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
    title=settings.app_name,
    description="Virtual meeting space with 3 type chat system",
    docs_url="/docs",
    lifespan=lifespan
)

app.include_router(rooms_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Welcome to The Gathering API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "rooms": "/api/v1/rooms",
            "room_health": "/api/v1/rooms/health/check"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/test")
def test_endpoint():
    return {"status": "FastAPI works!", "project": "The Gathering"}


if __name__ == "__main__":
    print("API Documentation: http://localhost:8000/docs")
    print("Room Endpoint: http://localhost:8000/api/v1/rooms")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )