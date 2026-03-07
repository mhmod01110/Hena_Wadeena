"""
Hena Wadeena — User Service
=============================
Clean Architecture: controllers → services → repositories → models

Run:  uvicorn main:app --port 8002 --reload
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import init_db
from controllers.user_controller import router as user_router
from controllers.internal_controller import router as internal_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print(f"✅ {settings.APP_NAME} started on port {settings.APP_PORT}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="User profile & identity service — Clean Architecture",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, tags=["Users"])
app.include_router(internal_router)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "user-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.APP_PORT, reload=True)
