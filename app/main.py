from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import settings
from app.core.redis_client import redis_client
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Scalable API Platform...")
    await redis_client.ping()
    print("✅ Redis connected")
    yield
    await redis_client.close()
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-ready Task Manager API with JWT auth, Redis caching, and Celery background jobs.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=settings.ALLOWED_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
async def root():
    return {"service": settings.PROJECT_NAME, "version": settings.VERSION, "status": "healthy", "docs": "/docs"}


@app.get("/health", tags=["Health"])
async def health_check():
    redis_ok = await redis_client.ping()
    return {"status": "healthy", "redis": "connected" if redis_ok else "disconnected", "database": "connected"}
