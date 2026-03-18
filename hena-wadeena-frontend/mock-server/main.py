"""
Hena Wadeena — Mock API Server
================================
Returns dummy JSON for ALL services so the frontend can demo a full UX.

Run:  pip install -r requirements.txt && uvicorn main:app --port 8000 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth, tourism, market, logistics, investment
from routes import map as map_routes
from routes import guides, payments, notifications, search
from routes import ai as ai_routes

app = FastAPI(title="Hena Wadeena Mock API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Existing routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(tourism.router, prefix="/api/v1/tourism", tags=["Tourism"])
app.include_router(market.router, prefix="/api/v1/market", tags=["Market"])
app.include_router(logistics.router, prefix="/api/v1/logistics", tags=["Logistics"])
app.include_router(investment.router, prefix="/api/v1/investment", tags=["Investment"])

# New routes
app.include_router(map_routes.router, prefix="/api/v1/map", tags=["Map"])
app.include_router(guides.router, prefix="/api/v1/guides", tags=["Guides"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(ai_routes.router, prefix="/api/v1/ai", tags=["AI"])


@app.get("/health")
def health():
    return {"status": "healthy", "service": "mock-server"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
