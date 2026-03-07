"""
Hena Wadeena — API Gateway
===========================
Lightweight reverse-proxy with JWT validation.

Run:  uvicorn main:app --port 8000 --reload
"""

import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

from core.config import settings
from middleware.auth import JWTAuthMiddleware

# ── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description="API Gateway — Clean Architecture",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    JWTAuthMiddleware,
    secret_key=settings.JWT_SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM,
)

_http = httpx.AsyncClient(timeout=30.0)


@app.on_event("shutdown")
async def shutdown():
    await _http.aclose()


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "gateway"}


def _resolve(path: str):
    for prefix, url in settings.service_routes.items():
        if path.startswith(prefix):
            return url, path[len(prefix):] or "/"
    return None


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy(request: Request, path: str):
    full = f"/api/{path}"
    resolved = _resolve(full)
    if not resolved:
        raise HTTPException(404, f"No service for: {full}")

    svc_url, remaining = resolved
    target = f"{svc_url}{remaining}"
    if request.url.query:
        target += f"?{request.url.query}"

    headers = dict(request.headers)
    headers.pop("host", None)
    req_id = str(uuid.uuid4())
    headers["X-Request-Id"] = req_id

    if hasattr(request.state, "user_id"):
        headers["X-User-Id"] = request.state.user_id
        headers["X-User-Role"] = request.state.user_role

    body = await request.body()

    try:
        resp = await _http.request(method=request.method, url=target, headers=headers, content=body)
        ct = resp.headers.get("content-type", "")
        content = resp.json() if ct.startswith("application/json") else {"raw": resp.text}
        return JSONResponse(content=content, status_code=resp.status_code,
                            headers={"X-Request-Id": req_id, "X-Proxied-To": svc_url})
    except httpx.ConnectError:
        raise HTTPException(503, "Service unavailable")
    except httpx.TimeoutException:
        raise HTTPException(504, "Gateway timeout")
    except Exception as e:
        raise HTTPException(502, f"Bad gateway: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.APP_PORT, reload=True)
