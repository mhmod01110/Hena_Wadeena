"""Hena Wadeena Media Service entrypoint."""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from controllers.media_asset_controller import router as entity_router
from core.config import settings
from core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print(f"Hena Wadeena Media Service started on port {settings.APP_PORT}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Hena Wadeena Media Service - Clean Architecture",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(entity_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": "media-service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.APP_PORT, reload=True)
