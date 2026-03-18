"""Local API endpoints used when domain microservices are not available yet.

This keeps the frontend fully integrated against one production-shaped gateway
while auth/user services continue to run as dedicated services.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1")


def _ok(data: Any, **extra: Any) -> dict[str, Any]:
    return {"success": True, "data": data, **extra}


from fastapi import Request
from importlib import import_module
from pathlib import Path
import sys

from core.config import settings
from shared.utils.jwt import create_access_token, create_refresh_token_value

# Reuse mock-server datasets so gateway data stays in sync with frontend mock data.
MOCK_ROUTES: dict[str, Any] = {}
try:
    root = Path(__file__).resolve().parents[2]
    mock_server_dir = root / "hena-wadeena-frontend" / "mock-server"
    if mock_server_dir.exists():
        sys.path.insert(0, str(mock_server_dir))
        for name in ["tourism", "market", "logistics", "investment", "guides", "payments", "notifications", "search", "ai", "map"]:
            MOCK_ROUTES[name] = import_module(f"routes.{name}")
except Exception:
    MOCK_ROUTES = {}


def _mock_attr(module_name: str, attr_name: str, default: Any):
    module = MOCK_ROUTES.get(module_name)
    if not module:
        return default
    return getattr(module, attr_name, default)


# Auth + user fallback store
AUTH_USERS: dict[str, dict[str, Any]] = {}
REFRESH_INDEX: dict[str, str] = {}


def _make_auth_payload(user: dict[str, Any]) -> dict[str, Any]:
    access_token = create_access_token(
        user_id=user["id"],
        role=user.get("role", "tourist"),
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    refresh_token = create_refresh_token_value()
    REFRESH_INDEX[refresh_token] = user["id"]

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user["id"],
            "email": user.get("email"),
            "phone": user.get("phone"),
            "full_name": user["full_name"],
            "display_name": user.get("display_name"),
            "avatar_url": user.get("avatar_url"),
            "city": user.get("city"),
            "organization": user.get("organization"),
            "role": user.get("role", "tourist"),
            "status": user.get("status", "active"),
            "language": user.get("language", "ar"),
            "verified_at": user.get("verified_at"),
            "created_at": user["created_at"],
        },
    }


def _find_user(email: Optional[str], phone: Optional[str]) -> Optional[dict[str, Any]]:
    for user in AUTH_USERS.values():
        if email and user.get("email") == email:
            return user
        if phone and user.get("phone") == phone:
            return user
    return None


class RegisterAuthRequest(BaseModel):
    email: str
    phone: str
    full_name: str
    password: str = Field(min_length=6, max_length=128)
    role: str = "tourist"
    city: Optional[str] = None
    organization: Optional[str] = None
    documents: list[dict[str, Any]] = Field(default_factory=list)


class LoginAuthRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str


class RefreshAuthRequest(BaseModel):
    refresh_token: str


@router.post("/auth/register", status_code=201)
async def fallback_register(body: RegisterAuthRequest):
    if _find_user(body.email, body.phone):
        raise HTTPException(status_code=409, detail="User with this email or phone already exists")

    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    user = {
        "id": user_id,
        "email": body.email,
        "phone": body.phone,
        "full_name": body.full_name,
        "display_name": None,
        "avatar_url": None,
        "city": body.city,
        "organization": body.organization,
        "role": body.role,
        "status": "active",
        "language": "ar",
        "verified_at": None,
        "created_at": now,
        "password": body.password,
        "kyc": [
            {
                "id": str(uuid.uuid4()),
                "doc_type": d.get("doc_type", "document"),
                "doc_url": f"client-upload://{d.get('file_name', 'document')}",
                "status": "pending",
            }
            for d in body.documents
        ],
    }
    AUTH_USERS[user_id] = user
    return {"success": True, "message": "Account created successfully", "data": _make_auth_payload(user)}


@router.post("/auth/login")
async def fallback_login(body: LoginAuthRequest):
    if not body.email and not body.phone:
        raise HTTPException(status_code=400, detail="Email or phone is required")

    user = _find_user(body.email, body.phone)
    if not user or user.get("password") != body.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"success": True, "message": "Login successful", "data": _make_auth_payload(user)}


@router.post("/auth/refresh")
async def fallback_refresh(body: RefreshAuthRequest):
    user_id = REFRESH_INDEX.get(body.refresh_token)
    if not user_id or user_id not in AUTH_USERS:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = AUTH_USERS[user_id]
    return {"success": True, "message": "Token refreshed", "data": _make_auth_payload(user)}


@router.get("/auth/me")
async def fallback_auth_me(request: Request):
    user_id = getattr(request.state, "user_id", None)
    if not user_id or user_id not in AUTH_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    user = AUTH_USERS[user_id]
    return {
        "id": user["id"],
        "email": user.get("email"),
        "phone": user.get("phone"),
        "full_name": user["full_name"],
        "display_name": user.get("display_name"),
        "avatar_url": user.get("avatar_url"),
        "city": user.get("city"),
        "organization": user.get("organization"),
        "role": user.get("role", "tourist"),
        "status": user.get("status", "active"),
        "language": user.get("language", "ar"),
        "verified_at": user.get("verified_at"),
        "created_at": user.get("created_at"),
    }


@router.post("/auth/logout")
async def fallback_logout(body: RefreshAuthRequest):
    REFRESH_INDEX.pop(body.refresh_token, None)
    return {"success": True, "message": "Logged out successfully"}


@router.get("/users/me")
async def fallback_user_me(request: Request):
    return await fallback_auth_me(request)


class UpdateUserMeRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    organization: Optional[str] = None
    language: Optional[str] = Field(default=None, pattern="^(ar|en)$")


@router.put("/users/me")
async def fallback_update_user_me(body: UpdateUserMeRequest, request: Request):
    user_id = getattr(request.state, "user_id", None)
    if not user_id or user_id not in AUTH_USERS:
        raise HTTPException(status_code=404, detail="User not found")

    user = AUTH_USERS[user_id]
    updates = body.model_dump(exclude_unset=True)

    if "email" in updates and updates["email"]:
        other = _find_user(updates["email"], None)
        if other and other["id"] != user_id:
            raise HTTPException(status_code=409, detail="User with this email already exists")

    if "phone" in updates and updates["phone"]:
        other = _find_user(None, updates["phone"])
        if other and other["id"] != user_id:
            raise HTTPException(status_code=409, detail="User with this phone already exists")

    user.update(updates)

    return {
        "id": user["id"],
        "email": user.get("email"),
        "phone": user.get("phone"),
        "full_name": user["full_name"],
        "display_name": user.get("display_name"),
        "avatar_url": user.get("avatar_url"),
        "city": user.get("city"),
        "organization": user.get("organization"),
        "role": user.get("role", "tourist"),
        "status": user.get("status", "active"),
        "language": user.get("language", "ar"),
        "verified_at": user.get("verified_at"),
        "created_at": user.get("created_at"),
    }


@router.get("/users/me/kyc")
async def fallback_user_kyc(request: Request):
    user_id = getattr(request.state, "user_id", None)
    if not user_id or user_id not in AUTH_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    return AUTH_USERS[user_id].get("kyc", [])

# Tourism
ATTRACTIONS: list[dict[str, Any]] = [
    {
        "id": 1,
        "title": "Kharga Oasis",
        "description": "Historic oasis with landmarks and desert tours",
        "long_description": "Kharga is a major destination with heritage sites, palm groves, and nearby hot springs.",
        "image": "https://images.unsplash.com/photo-1539768942893-daf53e448371?w=800",
        "images": [
            "https://images.unsplash.com/photo-1539768942893-daf53e448371?w=800",
            "https://images.unsplash.com/photo-1568322445389-f64ac2515020?w=800",
        ],
        "rating": 4.8,
        "reviews_count": 240,
        "duration": "Full day",
        "type": "historical",
        "location": "Kharga, New Valley",
        "coordinates": {"lat": 25.441, "lng": 30.5534},
        "featured": True,
        "opening_hours": "08:00 - 17:00",
        "ticket_price": 80,
        "highlights": ["Hibis Temple", "Bagawat", "Museum"],
    },
    {
        "id": 2,
        "title": "White Desert",
        "description": "Iconic white rock formations and stargazing camps",
        "image": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800",
        "rating": 4.9,
        "reviews_count": 560,
        "duration": "2-3 days",
        "type": "nature",
        "location": "Farafra, New Valley",
        "coordinates": {"lat": 27.2956, "lng": 28.0567},
        "featured": True,
    },
    {
        "id": 3,
        "title": "Dakhla Old Village",
        "description": "Traditional mud-brick village and cultural heritage",
        "image": "https://images.unsplash.com/photo-1568322445389-f64ac2515020?w=800",
        "rating": 4.5,
        "reviews_count": 150,
        "duration": "3 hours",
        "type": "culture",
        "location": "Dakhla, New Valley",
        "coordinates": {"lat": 25.4888, "lng": 29.0},
        "featured": False,
    },
]

TOURISM_GUIDES: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Ahmed El Sayed",
        "languages": ["Arabic", "English"],
        "specialties": ["Desert safari", "Heritage tours"],
        "rating": 4.9,
        "reviews": 87,
        "price_per_day": 800,
        "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200",
        "bio": "Certified local guide with 10+ years experience.",
        "available": True,
    },
    {
        "id": 2,
        "name": "Fatma Hassan",
        "languages": ["Arabic", "English", "French"],
        "specialties": ["Wellness trips", "Oasis tours"],
        "rating": 4.7,
        "reviews": 45,
        "price_per_day": 650,
        "image": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=200",
        "bio": "Wellness-focused guide for oasis experiences.",
        "available": True,
    },
]

ACCOMMODATIONS: list[dict[str, Any]] = [
    {
        "id": 1,
        "title": "Kharga Furnished Apartment",
        "type": "apartment",
        "price": 1500,
        "price_unit": "month",
        "rooms": 2,
        "location": "Kharga Center",
        "amenities": ["AC", "Wi-Fi", "Kitchen"],
        "for_students": True,
        "image": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400",
        "rating": 4.3,
    },
    {
        "id": 2,
        "title": "Oasis Hotel",
        "type": "hotel",
        "price": 350,
        "price_unit": "night",
        "rooms": 1,
        "location": "Kharga Main Street",
        "amenities": ["AC", "Breakfast", "Pool"],
        "for_students": False,
        "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400",
        "rating": 4.5,
    },
]


ATTRACTIONS = _mock_attr("tourism", "ATTRACTIONS", ATTRACTIONS)
TOURISM_GUIDES = _mock_attr("tourism", "GUIDES", TOURISM_GUIDES)
ACCOMMODATIONS = _mock_attr("tourism", "ACCOMMODATIONS", ACCOMMODATIONS)

@router.get("/tourism/attractions")
async def get_attractions():
    return _ok(ATTRACTIONS)


@router.get("/tourism/attractions/featured")
async def get_featured_attractions():
    return _ok([a for a in ATTRACTIONS if a.get("featured")])


@router.get("/tourism/attractions/{attraction_id}")
async def get_attraction(attraction_id: int):
    attraction = next((a for a in ATTRACTIONS if a["id"] == attraction_id), None)
    if not attraction:
        raise HTTPException(status_code=404, detail="Attraction not found")
    return _ok(attraction)


@router.get("/tourism/guides")
async def get_tourism_guides():
    return _ok(TOURISM_GUIDES)


@router.get("/tourism/accommodations")
async def get_accommodations():
    return _ok(ACCOMMODATIONS)


# Market
PRICE_ITEMS: list[dict[str, Any]] = [
    {"id": 1, "name": "Wheat", "price": 1250, "change": 2.5, "unit": "ton", "category": "grain"},
    {"id": 2, "name": "Siwi Dates", "price": 45, "change": -1.2, "unit": "kg", "category": "fruit"},
    {"id": 3, "name": "Olives", "price": 28, "change": 0.0, "unit": "kg", "category": "fruit"},
    {"id": 4, "name": "Potatoes", "price": 8, "change": 0.7, "unit": "kg", "category": "vegetable"},
]

SUPPLIERS: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Green Valley Farms",
        "specialties": ["Dates", "Olives", "Grapes"],
        "city": "Kharga",
        "rating": 4.8,
        "reviews": 124,
        "verified": True,
        "description": "Integrated farm supplying premium crops.",
        "phone": "01012345678",
        "email": "info@green-valley.example",
        "image": "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=400",
        "products": [{"name": "Premium Dates", "price": 55, "unit": "kg"}],
    },
    {
        "id": 2,
        "name": "Golden Palm Co",
        "specialties": ["Dates"],
        "city": "Dakhla",
        "rating": 4.6,
        "reviews": 89,
        "verified": True,
        "description": "Date producer for local and export channels.",
        "phone": "01098765432",
        "email": "sales@golden-palm.example",
        "image": "https://images.unsplash.com/photo-1523741543316-beb7fc7023d8?w=400",
    },
]


PRICE_ITEMS = _mock_attr("market", "PRICE_DATA", PRICE_ITEMS)
SUPPLIERS = _mock_attr("market", "SUPPLIERS", SUPPLIERS)

@router.get("/market/prices")
async def get_market_prices():
    return _ok(PRICE_ITEMS)


@router.get("/market/suppliers")
async def get_suppliers():
    return _ok(SUPPLIERS)


@router.get("/market/suppliers/{supplier_id}")
async def get_supplier(supplier_id: int):
    supplier = next((s for s in SUPPLIERS if s["id"] == supplier_id), None)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return _ok(supplier)


# Logistics
TRANSPORT_ROUTES: list[dict[str, Any]] = [
    {
        "id": 1,
        "from": "Kharga",
        "to": "Dakhla",
        "type": "bus",
        "duration": "3 hours",
        "price": 80,
        "departures": ["06:00", "10:00", "14:00", "18:00"],
        "operator": "West Delta",
    },
    {
        "id": 2,
        "from": "Kharga",
        "to": "Assiut",
        "type": "bus",
        "duration": "4 hours",
        "price": 120,
        "departures": ["07:00", "15:00"],
        "operator": "Valley Transit",
    },
]

STATIONS: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Kharga Central Station",
        "city": "Kharga",
        "routes": 8,
        "address": "El Gomhoria St, Kharga",
        "phone": "092-7921234",
        "facilities": ["Waiting hall", "Cafe", "Parking"],
        "operating_hours": "05:00-22:00",
    },
    {
        "id": 2,
        "name": "Dakhla Station",
        "city": "Dakhla",
        "routes": 5,
        "address": "Mut, Dakhla",
        "phone": "092-7851234",
        "facilities": ["Waiting hall"],
        "operating_hours": "06:00-20:00",
    },
]

CARPOOLS: list[dict[str, Any]] = [
    {
        "id": 1,
        "from": "Kharga",
        "to": "Assiut",
        "date": "2026-03-15",
        "time": "07:00",
        "seats": 2,
        "price": 100,
        "driver": "Khaled Mahmoud",
        "rating": 4.8,
        "car_model": "Toyota Corolla",
    },
    {
        "id": 2,
        "from": "Dakhla",
        "to": "Assiut",
        "date": "2026-03-16",
        "time": "06:00",
        "seats": 3,
        "price": 120,
        "driver": "Mahmoud Ali",
        "rating": 4.5,
        "car_model": "Hyundai Elantra",
    },
]


TRANSPORT_ROUTES = _mock_attr("logistics", "ROUTES", TRANSPORT_ROUTES)
STATIONS = _mock_attr("logistics", "STATIONS", STATIONS)
CARPOOLS = _mock_attr("logistics", "CARPOOLS", CARPOOLS)

@router.get("/logistics/routes")
async def get_routes():
    return _ok(TRANSPORT_ROUTES)


@router.get("/logistics/stations")
async def get_stations():
    return _ok(STATIONS)


@router.get("/logistics/stations/{station_id}")
async def get_station(station_id: int):
    station = next((s for s in STATIONS if s["id"] == station_id), None)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return _ok(station)


@router.get("/logistics/carpools")
async def get_carpools():
    return _ok(CARPOOLS)


# Investment
OPPORTUNITIES: list[dict[str, Any]] = [
    {
        "id": 1,
        "title": "Integrated Farm Project",
        "category": "Agriculture",
        "location": "Dakhla",
        "investment": "5-10M EGP",
        "min_investment": 5_000_000,
        "max_investment": 10_000_000,
        "roi": "18-22%",
        "status": "available",
        "description": "100-acre farm for dates and olives with modern irrigation.",
    },
    {
        "id": 2,
        "title": "Eco Tourism Compound",
        "category": "Tourism",
        "location": "Farafra",
        "investment": "15-25M EGP",
        "min_investment": 15_000_000,
        "max_investment": 25_000_000,
        "roi": "20-25%",
        "status": "available",
        "description": "Eco-lodge and desert camp package near White Desert.",
    },
]

STARTUPS: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Oasis Tech",
        "sector": "AgriTech",
        "stage": "growth",
        "location": "Kharga",
        "team": 8,
        "description": "Farm optimization platform with AI forecasting.",
        "funding_needed": "2M EGP",
    },
    {
        "id": 2,
        "name": "Dates Online",
        "sector": "E-commerce",
        "stage": "growth",
        "location": "Kharga",
        "team": 12,
        "description": "Marketplace for New Valley date products.",
        "funding_needed": "3M EGP",
    },
]


OPPORTUNITIES = _mock_attr("investment", "OPPORTUNITIES", OPPORTUNITIES)
STARTUPS = _mock_attr("investment", "STARTUPS", STARTUPS)

@router.get("/investment/opportunities")
async def get_opportunities():
    return _ok(OPPORTUNITIES)


@router.get("/investment/opportunities/{opportunity_id}")
async def get_opportunity(opportunity_id: int):
    opportunity = next((o for o in OPPORTUNITIES if o["id"] == opportunity_id), None)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return _ok(opportunity)


@router.get("/investment/startups")
async def get_startups():
    return _ok(STARTUPS)


# Guides + bookings
GUIDES: list[dict[str, Any]] = [
    {
        "id": 1,
        "user_id": "g1",
        "name": "Ahmed El Sayed",
        "bio_ar": "Certified guide for desert and heritage tours.",
        "languages": ["Arabic", "English"],
        "specialties": ["Desert safari", "Heritage tours"],
        "license_number": "GD-2020-001",
        "license_verified": True,
        "base_price": 800,
        "rating_avg": 4.9,
        "rating_count": 87,
        "active": True,
        "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200",
    },
    {
        "id": 2,
        "user_id": "g2",
        "name": "Fatma Hassan",
        "bio_ar": "Specialized in oasis and wellness tourism.",
        "languages": ["Arabic", "English", "French"],
        "specialties": ["Wellness", "Oasis tours"],
        "license_number": "GD-2021-015",
        "license_verified": True,
        "base_price": 650,
        "rating_avg": 4.7,
        "rating_count": 45,
        "active": True,
        "image": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=200",
    },
]

PACKAGES: list[dict[str, Any]] = [
    {
        "id": 1,
        "guide_id": 1,
        "title_ar": "White Desert Safari (3 days)",
        "description": "Camping and safari package with guide support.",
        "duration_hrs": 72,
        "max_people": 8,
        "price": 3500,
        "includes": ["Transport", "Meals", "Camp", "Guide"],
        "images": ["https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=600"],
        "status": "active",
    },
    {
        "id": 2,
        "guide_id": 1,
        "title_ar": "Kharga Heritage Day Tour",
        "description": "Temple and heritage attractions day trip.",
        "duration_hrs": 8,
        "max_people": 12,
        "price": 800,
        "includes": ["Transport", "Tickets", "Guide"],
        "images": ["https://images.unsplash.com/photo-1539768942893-daf53e448371?w=600"],
        "status": "active",
    },
]

REVIEWS: list[dict[str, Any]] = [
    {
        "id": "rv-001",
        "guide_id": 1,
        "tourist_id": "t1",
        "tourist_name": "Sara Ahmed",
        "rating": 5,
        "comment": "Amazing guide and great trip organization.",
        "guide_reply": "Thanks a lot, glad you enjoyed!",
        "created_at": "2026-03-01",
    }
]

BOOKINGS: list[dict[str, Any]] = [
    {
        "id": "bk-001",
        "package_id": 1,
        "guide_id": 1,
        "guide_name": "Ahmed El Sayed",
        "tourist_id": "demo-user",
        "package_title": "White Desert Safari (3 days)",
        "booking_date": "2026-03-15",
        "start_time": "07:00",
        "people_count": 2,
        "total_price": 7000,
        "status": "confirmed",
        "created_at": "2026-03-07T10:00:00",
    }
]


GUIDES = _mock_attr("guides", "GUIDES", GUIDES)
PACKAGES = _mock_attr("guides", "PACKAGES", PACKAGES)
REVIEWS = _mock_attr("guides", "REVIEWS", REVIEWS)
BOOKINGS = _mock_attr("guides", "BOOKINGS", BOOKINGS)

class BookingCreate(BaseModel):
    package_id: int
    guide_id: int
    booking_date: str
    start_time: str = "08:00"
    people_count: int = Field(default=1, ge=1, le=20)
    notes: Optional[str] = None


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=2, max_length=2000)


@router.get("/guides")
async def list_guides():
    return _ok(GUIDES)


@router.get("/guides/{guide_id}")
async def get_guide(guide_id: int):
    guide = next((g for g in GUIDES if g["id"] == guide_id), None)
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    return _ok(guide)


@router.get("/guides/{guide_id}/packages")
async def get_guide_packages(guide_id: int):
    return _ok([p for p in PACKAGES if p["guide_id"] == guide_id])


@router.get("/guides/{guide_id}/reviews")
async def get_guide_reviews(guide_id: int):
    return _ok([r for r in REVIEWS if r["guide_id"] == guide_id])


@router.post("/guides/{guide_id}/reviews", status_code=201)
async def create_review(guide_id: int, body: ReviewCreate):
    if not any(g["id"] == guide_id for g in GUIDES):
        raise HTTPException(status_code=404, detail="Guide not found")

    review = {
        "id": f"rv-{len(REVIEWS) + 1:03d}",
        "guide_id": guide_id,
        "tourist_id": "current-user",
        "tourist_name": "You",
        "rating": body.rating,
        "comment": body.comment,
        "guide_reply": None,
        "created_at": datetime.now(timezone.utc).date().isoformat(),
    }
    REVIEWS.append(review)
    return _ok(review)


@router.post("/guides/bookings", status_code=201)
async def create_booking(body: BookingCreate):
    guide = next((g for g in GUIDES if g["id"] == body.guide_id), None)
    package = next((p for p in PACKAGES if p["id"] == body.package_id), None)
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    if package["guide_id"] != body.guide_id:
        raise HTTPException(status_code=400, detail="Package does not belong to selected guide")

    booking = {
        "id": f"bk-{len(BOOKINGS) + 1:03d}",
        "package_id": body.package_id,
        "guide_id": body.guide_id,
        "guide_name": guide["name"],
        "tourist_id": "current-user",
        "package_title": package["title_ar"],
        "booking_date": body.booking_date,
        "start_time": body.start_time,
        "people_count": body.people_count,
        "total_price": package["price"] * body.people_count,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    BOOKINGS.append(booking)
    return {"success": True, "message": "Booking created successfully", "data": booking}


@router.get("/guides/bookings/my")
async def my_bookings():
    return _ok(BOOKINGS)


# Payments
WALLET = {
    "id": "w-001",
    "user_id": "demo-user",
    "balance": 2500.0,
    "currency": "EGP",
}

TRANSACTIONS: list[dict[str, Any]] = [
    {
        "id": "tx-001",
        "type": "topup",
        "amount": 5000,
        "direction": "credit",
        "balance_after": 5000,
        "description": "Wallet top-up",
        "status": "completed",
        "created_at": "2026-03-01T10:00:00",
    },
    {
        "id": "tx-002",
        "type": "booking_pay",
        "amount": 2500,
        "direction": "debit",
        "balance_after": 2500,
        "description": "Guide booking payment",
        "status": "completed",
        "created_at": "2026-03-05T14:30:00",
    },
]


WALLET = _mock_attr("payments", "WALLET", WALLET)
TRANSACTIONS = _mock_attr("payments", "TRANSACTIONS", TRANSACTIONS)

class TopupRequest(BaseModel):
    amount: float = Field(gt=0)
    method: str = "visa"


@router.get("/payments/wallet")
async def get_wallet():
    return _ok({**WALLET, "recent_transactions": TRANSACTIONS[:3]})


@router.post("/payments/wallet/topup")
async def topup_wallet(body: TopupRequest):
    WALLET["balance"] += body.amount
    tx = {
        "id": f"tx-{len(TRANSACTIONS) + 1:03d}",
        "type": "topup",
        "amount": body.amount,
        "direction": "credit",
        "balance_after": WALLET["balance"],
        "description": f"Wallet top-up ({body.method})",
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    TRANSACTIONS.insert(0, tx)
    return {
        "success": True,
        "message": f"Top-up successful: {body.amount:.0f} EGP",
        "data": {"new_balance": WALLET["balance"]},
    }


@router.get("/payments/transactions")
async def get_transactions():
    return _ok(TRANSACTIONS)


# Notifications
NOTIFICATIONS: list[dict[str, Any]] = [
    {
        "id": "n-001",
        "type": "booking_confirmed",
        "title_ar": "Booking confirmed",
        "body_ar": "Your guide booking has been confirmed.",
        "data": {"booking_id": "bk-001"},
        "channel": ["push", "in_app"],
        "read_at": None,
        "created_at": "2026-03-07T10:30:00",
    },
    {
        "id": "n-002",
        "type": "payment_received",
        "title_ar": "Payment completed",
        "body_ar": "Payment was deducted from your wallet successfully.",
        "data": {"transaction_id": "tx-002"},
        "channel": ["push", "email", "in_app"],
        "read_at": None,
        "created_at": "2026-03-05T14:30:00",
    },
]


NOTIFICATIONS = _mock_attr("notifications", "NOTIFICATIONS", NOTIFICATIONS)

@router.get("/notifications")
async def get_notifications():
    return _ok(NOTIFICATIONS)


@router.get("/notifications/unread-count")
async def get_unread_count():
    count = sum(1 for n in NOTIFICATIONS if n["read_at"] is None)
    return _ok({"count": count})


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    notification = next((n for n in NOTIFICATIONS if n["id"] == notification_id), None)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification["read_at"] = datetime.now(timezone.utc).isoformat()
    return {"success": True}


# Search
SEARCH_INDEX: list[dict[str, str]] = [
    {
        "id": "att-1",
        "type": "attraction",
        "title": "Kharga Oasis",
        "description": "Historic attractions and oasis experience",
        "location": "Kharga",
        "url": "/tourism/attraction/1",
    },
    {
        "id": "guide-1",
        "type": "guide",
        "title": "Ahmed El Sayed",
        "description": "Desert safari guide",
        "location": "Kharga",
        "url": "/guides/1",
    },
    {
        "id": "sup-1",
        "type": "supplier",
        "title": "Green Valley Farms",
        "description": "Dates and olives supplier",
        "location": "Kharga",
        "url": "/marketplace/supplier/1",
    },
    {
        "id": "inv-1",
        "type": "investment",
        "title": "Integrated Farm Project",
        "description": "100-acre date/olive project",
        "location": "Dakhla",
        "url": "/investment/opportunity/1",
    },
]


SEARCH_INDEX = _mock_attr("search", "SEARCH_INDEX", SEARCH_INDEX)

@router.get("/search")
async def search(q: str = "", type: Optional[str] = None):
    query = q.strip().lower()
    results = SEARCH_INDEX

    if query:
        results = [
            item
            for item in results
            if query in item["title"].lower() or query in item["description"].lower()
        ]

    if type:
        results = [item for item in results if item["type"] == type]

    return {"success": True, "data": results, "total": len(results), "query": q}


# AI
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: Optional[str] = None


AI_RESPONSES = _mock_attr("ai", "RESPONSES", {})
AI_DEFAULT_RESPONSE = _mock_attr("ai", "DEFAULT_RESPONSE", "I can help with tourism, guides, logistics, market prices, and investments.")

@router.post("/ai/chat")
async def ai_chat(body: ChatRequest):
    conv_id = body.conversation_id or f"conv-{uuid.uuid4().hex[:8]}"
    text = body.message.lower().strip()

    response = AI_DEFAULT_RESPONSE
    for keyword, reply in AI_RESPONSES.items():
        if keyword in text:
            response = reply
            break

    return _ok({"response": response, "conversation_id": conv_id, "sources": []})


# Map
POIS: list[dict[str, Any]] = [
    {
        "id": 1,
        "name_ar": "Hibis Temple",
        "name_en": "Hibis Temple",
        "category": "landmark",
        "description": "Historic temple in Kharga oasis.",
        "address": "Kharga, New Valley",
        "lat": 25.451,
        "lng": 30.5434,
        "phone": "092-7921111",
        "rating_avg": 4.8,
        "rating_count": 234,
        "images": ["https://images.unsplash.com/photo-1539768942893-daf53e448371?w=400"],
        "status": "approved",
    },
    {
        "id": 2,
        "name_ar": "Kharga General Hospital",
        "name_en": "Kharga General Hospital",
        "category": "government",
        "description": "Main public hospital in Kharga.",
        "address": "El Gomhoria St, Kharga",
        "lat": 25.44,
        "lng": 30.55,
        "phone": "092-7922222",
        "rating_avg": 3.6,
        "rating_count": 90,
        "images": [],
        "status": "approved",
    },
]

CARPOOL_RIDES: list[dict[str, Any]] = [
    {
        "id": 1,
        "driver_id": "d1",
        "driver_name": "Khaled Mahmoud",
        "origin_name": "Kharga",
        "destination_name": "Assiut",
        "origin": {"lat": 25.441, "lng": 30.5534},
        "destination": {"lat": 27.1809, "lng": 31.1837},
        "departure_time": "2026-03-15T07:00:00",
        "seats_total": 4,
        "seats_taken": 1,
        "price_per_seat": 100,
        "notes": "Air conditioned car",
        "status": "open",
        "car_model": "Toyota Corolla",
        "rating": 4.8,
    }
]


class CreateRideRequest(BaseModel):
    origin_name: str = Field(min_length=2, max_length=120)
    destination_name: str = Field(min_length=2, max_length=120)
    departure_time: str
    seats_total: int = Field(ge=1, le=8)
    price_per_seat: float = Field(gt=0)
    notes: Optional[str] = Field(default=None, max_length=500)


POIS = _mock_attr("map", "POIS", POIS)
CARPOOL_RIDES = _mock_attr("map", "CARPOOL_RIDES", CARPOOL_RIDES)

@router.get("/map/pois")
async def get_pois(category: Optional[str] = None):
    if not category:
        return _ok(POIS)
    return _ok([p for p in POIS if p["category"] == category])


@router.get("/map/pois/{poi_id}")
async def get_poi(poi_id: int):
    poi = next((p for p in POIS if p["id"] == poi_id), None)
    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")
    return _ok(poi)


@router.get("/map/carpool/rides")
async def get_map_carpool_rides():
    return _ok(CARPOOL_RIDES)


@router.post("/map/carpool/rides", status_code=201)
async def create_map_carpool_ride(body: CreateRideRequest):
    new_ride = {
        "id": len(CARPOOL_RIDES) + 1,
        "driver_id": "current-user",
        "driver_name": "You",
        "origin_name": body.origin_name,
        "destination_name": body.destination_name,
        "origin": {"lat": 25.441, "lng": 30.5534},
        "destination": {"lat": 27.1809, "lng": 31.1837},
        "departure_time": body.departure_time,
        "seats_total": body.seats_total,
        "seats_taken": 0,
        "price_per_seat": body.price_per_seat,
        "notes": body.notes,
        "status": "open",
    }
    CARPOOL_RIDES.append(new_ride)
    return _ok(new_ride)





