# HENA WADEENA — Complete Zero-to-Hero Project Planning
## هنا وادينا | Full Engineering Blueprint
**Stack:** Python 3.12 · FastAPI · MongoDB · Qdrant · Redis  
**Version:** MVP (Minimal Working Demo)  
**Team:** Dev-X | Date: 2026-02-06

---

# PART 1 — ARCHITECTURE & FOUNDATIONS

## 1. Executive Summary

Hena Wadeena is a smart regional platform for New Valley (الوادي الجديد), Egypt — covering the cities of Al-Kharga, Al-Dakhla, Al-Farafra, Baris, and Balat. It serves four user types through a unified AI-powered web application.

**Core Value Propositions:**
- **Tourists:** Discover places, activities, accommodation, transport
- **Students:** Find housing, daily services, campus maps
- **Investors:** Browse verified investment opportunities, market intelligence
- **Local Citizens:** Access local services, announcements, daily needs

**AI Differentiator:** A RAG chatbot that answers natural-language queries using the platform's own verified knowledge base — in Arabic and English.

---

## 2. Full System Architecture

```
═══════════════════════════════════════════════════════════════════════
                         HENA WADEENA — MVP ARCHITECTURE
═══════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND LAYER                             │
│                                                                     │
│   ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────┐  │
│   │  Landing  │  │   Auth    │  │  Explorer │  │  AI Chat UI   │  │
│   │   Page    │  │  Pages    │  │  (Map +   │  │  (Chatbot     │  │
│   │           │  │           │  │  Lists)   │  │   Widget)     │  │
│   └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └──────┬────────┘  │
│         │              │              │               │            │
│   ┌─────┴──────────────┴──────────────┴───────────────┴──────────┐ │
│   │          Vanilla JS / Fetch API + HTML5 + Tailwind CSS        │ │
│   └──────────────────────────────────┬────────────────────────────┘ │
└─────────────────────────────────────┼─────────────────────────────-┘
                                      │ HTTPS / REST
┌─────────────────────────────────────▼────────────────────────────────┐
│                        NGINX (Reverse Proxy)                         │
│   - SSL Termination    - Static File Serving    - Rate Limiting      │
└─────────────────────────────────────┬────────────────────────────────┘
                                      │
┌─────────────────────────────────────▼────────────────────────────────┐
│                     FASTAPI APPLICATION (Single Process)             │
│                                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  /auth   │ │/listings │ │/guide    │ │/invest   │ │  /chat   │  │
│  │  Router  │ │  Router  │ │  Router  │ │  Router  │ │  Router  │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│       │            │            │            │            │         │
│  ┌────┴──────────────────────────────────────────────────┴──────┐   │
│  │                     MIDDLEWARE STACK                          │   │
│  │  CORSMiddleware · RequestLoggingMiddleware · RateLimitMiddle  │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  Auth    │ │ Listing  │ │  Guide   │ │ Invest   │ │  Chat    │  │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │ │ Service  │  │
│  │          │ │          │ │          │ │          │ │(RAG Core)│  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│       │            │            │            │            │         │
│  ┌────┴──────────────────────────────────────────────────┴──────┐   │
│  │  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │   │
│  │  │Search Svc  │  │Review Svc│  │ User Svc │  │File Svc  │   │   │
│  │  │            │  │          │  │          │  │(uploads) │   │   │
│  │  └────────────┘  └──────────┘  └──────────┘  └──────────┘   │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │             BACKGROUND TASKS (asyncio + APScheduler)          │   │
│  │  market_data_sync · index_rebuild · cleanup_sessions          │   │
│  └───────────────────────────────────────────────────────────────┘   │
└──────────┬───────────────────────┬──────────────────────┬────────────┘
           │                       │                      │
  ┌────────▼────────┐   ┌──────────▼──────┐   ┌──────────▼─────────┐
  │    MongoDB      │   │     Redis       │   │     Qdrant         │
  │  (persistence)  │   │   (cache +      │   │  (vector store     │
  │                 │   │    sessions)    │   │   for RAG)         │
  │  Collections:   │   │                 │   │                    │
  │  · users        │   │  Keys:          │   │  Collections:      │
  │  · listings     │   │  · listings:*   │   │  · hena_kb         │
  │  · tourist_guide│   │  · guide:*      │   │                    │
  │  · investments  │   │  · invest:*     │   │  Payloads:         │
  │  · reviews      │   │  · search:*     │   │  · source, area    │
  │  · chat_sessions│   │  · session:*    │   │  · title, content  │
  │  · kb_documents │   │  · ratelimit:*  │   │  · category        │
  │  · notifications│   │                 │   │                    │
  │  · file_refs    │   │                 │   │                    │
  └─────────────────┘   └─────────────────┘   └────────────────────┘
                                                         │
                                               ┌─────────▼──────────┐
                                               │    LLM API         │
                                               │  (OpenAI / Local)  │
                                               │  gpt-4o-mini       │
                                               └────────────────────┘
```

---

## 3. Technology Stack — Final Decisions

| Layer | Technology | Reason |
|-------|-----------|--------|
| Backend Framework | FastAPI 0.115 | Async, auto-docs, fast |
| Language | Python 3.12 | Team skill, rich ecosystem |
| Primary DB | MongoDB 7 (Motor async) | Flexible schema, easy to seed |
| Vector DB | Qdrant 1.9 | Best async Python client, free, local |
| Cache | Redis 7 | Simple, proven, great Python lib |
| Embeddings | `text-embedding-3-small` (OpenAI) OR `intfloat/multilingual-e5-small` (free) | Cost vs quality tradeoff |
| LLM | `gpt-4o-mini` OR `ollama/qwen2.5:7b` (free, Arabic support) | Cost vs quality |
| Frontend | Vanilla HTML5 + Tailwind CSS + Alpine.js | Zero build toolchain for demo |
| File Storage | Local disk (demo) → MinIO (later) | Simplicity first |
| Auth | JWT (python-jose) + bcrypt | Industry standard |
| Background | APScheduler (in-process) | No Celery complexity for MVP |
| Reverse Proxy | Nginx | SSL, static files, rate limiting |
| Containerization | Docker + Docker Compose | Single command start |

---

## 4. Complete Folder & File Structure

```
hena_wadeena/
│
├── app/                                    # Main application package
│   ├── __init__.py
│   ├── main.py                             # FastAPI app factory + lifespan
│   ├── config.py                           # All settings via pydantic-settings
│   ├── dependencies.py                     # All FastAPI Depends() functions
│   │
│   ├── api/                                # HTTP layer (thin routers only)
│   │   ├── __init__.py
│   │   ├── router.py                       # Master router that includes all
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                     # /auth/*
│   │   │   ├── users.py                    # /users/*
│   │   │   ├── listings.py                 # /listings/*
│   │   │   ├── guide.py                    # /guide/*
│   │   │   ├── investment.py               # /investment/*
│   │   │   ├── search.py                   # /search/*
│   │   │   ├── chat.py                     # /chat/*
│   │   │   ├── reviews.py                  # /reviews/*
│   │   │   ├── notifications.py            # /notifications/*
│   │   │   ├── files.py                    # /files/* (upload)
│   │   │   └── admin.py                    # /admin/* (protected)
│   │
│   ├── services/                           # Business logic (no HTTP concerns)
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── listing_service.py
│   │   ├── guide_service.py
│   │   ├── investment_service.py
│   │   ├── search_service.py
│   │   ├── chat_service.py                 # RAG orchestration
│   │   ├── review_service.py
│   │   ├── notification_service.py
│   │   └── file_service.py
│   │
│   ├── schemas/                            # Pydantic models (request + response)
│   │   ├── __init__.py
│   │   ├── common.py                       # Shared: PaginatedResponse, etc.
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── listing.py
│   │   ├── guide.py
│   │   ├── investment.py
│   │   ├── chat.py
│   │   ├── review.py
│   │   └── notification.py
│   │
│   ├── db/                                 # Database connection clients
│   │   ├── __init__.py
│   │   ├── mongo.py                        # Motor client + collection helpers
│   │   ├── qdrant.py                       # AsyncQdrantClient + setup
│   │   └── redis.py                        # Redis async client + helpers
│   │
│   ├── core/                               # Cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── security.py                     # JWT, password hashing
│   │   ├── embeddings.py                   # Text → vector abstraction
│   │   ├── exceptions.py                   # Custom exceptions + handlers
│   │   ├── logging.py                      # Structured logging setup
│   │   ├── pagination.py                   # Pagination helpers
│   │   └── constants.py                    # Enums, category lists, areas
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── logging_middleware.py           # Request/response logging
│   │   └── rate_limit.py                   # Redis-backed rate limiting
│   │
│   └── tasks/                              # Background tasks
│       ├── __init__.py
│       ├── scheduler.py                    # APScheduler setup
│       ├── index_rebuild.py                # Rebuild Qdrant index nightly
│       └── cleanup.py                      # Clean old sessions
│
├── frontend/                               # Static frontend
│   ├── index.html                          # Landing page
│   ├── login.html
│   ├── register.html
│   ├── explorer.html                       # Browse listings + map
│   ├── listing_detail.html
│   ├── guide.html                          # Tourist guide
│   ├── guide_detail.html
│   ├── investment.html                     # Investment board
│   ├── investment_detail.html
│   ├── chat.html                           # AI chatbot page
│   ├── profile.html                        # User profile
│   ├── dashboard.html                      # Role-based dashboard
│   ├── admin/
│   │   ├── index.html                      # Admin home
│   │   ├── listings.html                   # Manage listings
│   │   └── users.html                      # Manage users
│   ├── css/
│   │   └── app.css                         # Custom styles + Tailwind CDN
│   └── js/
│       ├── api.js                          # API client wrapper
│       ├── auth.js                         # Login/logout/token refresh
│       ├── map.js                          # Google Maps init
│       └── chat.js                         # Chatbot UI logic
│
├── rag/                                    # RAG pipeline scripts
│   ├── __init__.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── chunker.py                      # Text chunking strategies
│   │   ├── loader.py                       # Load docs from Mongo
│   │   └── pipeline.py                     # Full ingestion orchestration
│   └── evaluation/
│       └── eval.py                         # Basic retrieval quality check
│
├── seed/
│   ├── data/
│   │   ├── tourist_guide.json              # 25 attractions
│   │   ├── listings.json                   # 40 businesses
│   │   ├── investments.json                # 15 opportunities
│   │   └── general_knowledge.json          # 20 general text docs about the valley
│   ├── seed_mongo.py                       # Insert all JSON data
│   ├── seed_qdrant.py                      # Embed + upsert to Qdrant
│   └── seed_admin.py                       # Create admin user
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_security.py
│   │   ├── test_chunker.py
│   │   └── test_pagination.py
│   ├── integration/
│   │   ├── test_auth.py
│   │   ├── test_listings.py
│   │   ├── test_search.py
│   │   ├── test_chat.py
│   │   └── test_investment.py
│   └── fixtures/
│       └── sample_data.py
│
├── nginx/
│   ├── nginx.conf                          # Main nginx config
│   └── ssl/                               # Self-signed certs for local dev
│
├── scripts/
│   ├── start.sh                            # Start everything
│   ├── reset_db.sh                         # Drop + re-seed all data
│   └── health_check.sh                     # Verify all services
│
├── docker-compose.yml                      # All services
├── docker-compose.prod.yml                 # Production overrides
├── Dockerfile
├── requirements.txt
├── .env.example
├── .env                                    # Local (git-ignored)
├── .gitignore
├── pyproject.toml                          # Black, isort, pytest config
└── README.md
```

---

## 5. Core Constants & Enums

```python
# app/core/constants.py

from enum import Enum

class UserRole(str, Enum):
    TOURIST = "tourist"
    STUDENT = "student"
    INVESTOR = "investor"
    CITIZEN = "citizen"
    ADMIN = "admin"

class ListingCategory(str, Enum):
    PLACE = "place"
    ACCOMMODATION = "accommodation"
    RESTAURANT = "restaurant"
    SERVICE = "service"
    ACTIVITY = "activity"
    TRANSPORT = "transport"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    SHOPPING = "shopping"

class ListingSubCategory(str, Enum):
    # Accommodation
    HOTEL = "hotel"
    HOSTEL = "hostel"
    APARTMENT = "apartment"
    # Restaurants
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    FAST_FOOD = "fast_food"
    # Services
    PHARMACY = "pharmacy"
    BANK = "bank"
    GOVERNMENT = "government"
    GAS_STATION = "gas_station"
    CAR_RENTAL = "car_rental"
    # Education
    SCHOOL = "school"
    UNIVERSITY = "university"
    # Healthcare
    HOSPITAL = "hospital"
    CLINIC = "clinic"

class InvestmentSector(str, Enum):
    AGRICULTURE = "agriculture"
    TOURISM = "tourism"
    INDUSTRY = "industry"
    REAL_ESTATE = "real_estate"
    SERVICES = "services"
    TECHNOLOGY = "technology"
    ENERGY = "energy"

class GuideType(str, Enum):
    ATTRACTION = "attraction"
    HISTORICAL = "historical"
    NATURAL = "natural"
    FESTIVAL = "festival"
    ADVENTURE = "adventure"

class Area(str, Enum):
    KHARGA = "الخارجة"
    DAKHLA = "الداخلة"
    FARAFRA = "الفرافرة"
    BARIS = "باريس"
    BALAT = "بلاط"

AREA_COORDINATES = {
    "الخارجة": {"lat": 25.4397, "lng": 30.5490},
    "الداخلة": {"lat": 25.4895, "lng": 28.9818},
    "الفرافرة": {"lat": 27.0603, "lng": 27.9723},
    "باريس":   {"lat": 24.7006, "lng": 30.7058},
    "بلاط":   {"lat": 25.6055, "lng": 29.0620},
}
```
# PART 2 — COMPLETE DATA LAYER

## 6. MongoDB Collections — Complete Schemas

All collections live in DB: **`hena_wadeena`**

### 6.1 `users`
```python
{
    "_id": ObjectId,
    "name": str,                      # "Ahmed Hassan"
    "name_ar": str,                   # "أحمد حسن"
    "email": str,                     # unique, lowercase
    "hashed_password": str,
    "role": str,                      # UserRole enum
    "phone": str | None,
    "avatar_url": str | None,
    "bio": str | None,
    "preferences": {
        "areas_of_interest": [str],   # ["الخارجة", "الداخلة"]
        "categories": [str],          # ["accommodation", "restaurant"]
        "language": str               # "ar" | "en"
    },
    "is_active": bool,                # default True
    "is_verified": bool,              # email verified
    "last_login": datetime | None,
    "created_at": datetime,
    "updated_at": datetime
}
# Indexes:
# { "email": 1 }  unique
# { "role": 1 }
# { "is_active": 1 }
```

### 6.2 `listings`
```python
{
    "_id": ObjectId,
    "title": str,                     # English
    "title_ar": str,                  # Arabic (primary)
    "slug": str,                      # url-friendly, unique
    "description": str,
    "description_ar": str,
    "category": str,                  # ListingCategory enum
    "sub_category": str,              # ListingSubCategory enum
    "location": {
        "area": str,                  # Area enum
        "address": str,
        "address_ar": str,
        "coordinates": {
            "lat": float,
            "lng": float
        },
        "google_place_id": str | None
    },
    "contact": {
        "phone": str | None,
        "whatsapp": str | None,
        "email": str | None,
        "website": str | None,
        "facebook": str | None
    },
    "hours": {                        # opening hours
        "saturday":  {"open": "08:00", "close": "22:00", "closed": False},
        "sunday":    {"open": "08:00", "close": "22:00", "closed": False},
        "monday":    {"open": "08:00", "close": "22:00", "closed": False},
        "tuesday":   {"open": "08:00", "close": "22:00", "closed": False},
        "wednesday": {"open": "08:00", "close": "22:00", "closed": False},
        "thursday":  {"open": "08:00", "close": "22:00", "closed": False},
        "friday":    {"open": "14:00", "close": "22:00", "closed": False}
    },
    "price_range": str | None,        # "$" | "$$" | "$$$"
    "tags": [str],                    # ["wifi", "parking", "air_conditioning"]
    "images": [str],                  # list of file_refs IDs or URLs
    "thumbnail": str | None,          # primary image URL
    "amenities": [str],               # for accommodations
    "is_verified": bool,              # admin approved
    "is_active": bool,
    "is_featured": bool,              # promoted listing
    "created_by": ObjectId,           # ref users._id
    "created_at": datetime,
    "updated_at": datetime,
    "rating_avg": float,              # denormalized, updated on review
    "review_count": int,              # denormalized
    "view_count": int                 # simple analytics
}
# Indexes:
# { "category": 1, "location.area": 1, "is_active": 1 }
# { "sub_category": 1 }
# { "is_featured": 1, "created_at": -1 }
# { "slug": 1 }  unique
# { "tags": 1 }
# text index: { "title_ar": "text", "description_ar": "text", "tags": "text" }
```

### 6.3 `tourist_guide`
```python
{
    "_id": ObjectId,
    "name": str,
    "name_ar": str,
    "slug": str,
    "type": str,                      # GuideType enum
    "area": str,                      # Area enum
    "description": str,
    "description_ar": str,
    "history": str | None,            # historical background (long text)
    "history_ar": str | None,
    "best_season": str,               # "winter" | "summer" | "all_year" | "spring"
    "best_time_of_day": str | None,   # "morning" | "evening" | "any"
    "entry_fee": {
        "adults_egp": float,
        "children_egp": float,
        "foreigners_usd": float | None
    },
    "opening_hours": str,             # "7:00 AM - 5:00 PM daily"
    "duration_hours": float,          # recommended visit duration
    "difficulty": str | None,         # "easy"|"moderate"|"hard" for activities
    "tips": [str],                    # practical visitor tips
    "tips_ar": [str],
    "nearby": [str],                  # list of other guide slugs
    "coordinates": {
        "lat": float,
        "lng": float
    },
    "images": [str],
    "thumbnail": str | None,
    "is_active": bool,
    "is_featured": bool,
    "created_at": datetime,
    "updated_at": datetime,
    "rating_avg": float,
    "review_count": int,
    "view_count": int
}
# Indexes:
# { "area": 1, "type": 1, "is_active": 1 }
# { "is_featured": 1 }
# text index: { "name_ar": "text", "description_ar": "text" }
```

### 6.4 `investment_opportunities`
```python
{
    "_id": ObjectId,
    "title": str,
    "title_ar": str,
    "slug": str,
    "description": str,
    "description_ar": str,
    "sector": str,                    # InvestmentSector enum
    "area": str,
    "land_area_sqm": float | None,
    "investment_range": {
        "min_egp": float,
        "max_egp": float
    },
    "expected_return_pct": float | None,  # percentage 0-100
    "payback_period_years": float | None,
    "incentives": [str],              # "tax_exemption", "land_subsidy", etc.
    "incentives_ar": [str],
    "infrastructure": {               # available infrastructure
        "water": bool,
        "electricity": bool,
        "road_access": bool,
        "telecom": bool
    },
    "contact": {
        "entity": str,                # "GAFI" | "محافظة الوادي الجديد"
        "person": str | None,
        "phone": str | None,
        "email": str | None
    },
    "documents": [str],              # file_refs to PDFs/brochures
    "images": [str],
    "thumbnail": str | None,
    "status": str,                   # "available"|"under_review"|"taken"
    "source": str,                   # "GAFI"|"محافظة"|"private"
    "is_verified": bool,
    "is_featured": bool,
    "interest_count": int,            # # of users who expressed interest
    "created_at": datetime,
    "updated_at": datetime
}
# Indexes:
# { "sector": 1, "area": 1, "status": 1 }
# { "is_featured": 1 }
# { "investment_range.min_egp": 1, "investment_range.max_egp": 1 }
# text index: { "title_ar": "text", "description_ar": "text" }
```

### 6.5 `reviews`
```python
{
    "_id": ObjectId,
    "user_id": ObjectId,              # ref users._id
    "user_name": str,                 # denormalized for display
    "user_avatar": str | None,
    "target_type": str,               # "listing" | "guide"
    "target_id": ObjectId,            # ref listings._id or tourist_guide._id
    "rating": int,                    # 1-5
    "title": str | None,
    "body": str,
    "images": [str],                  # review photos
    "helpful_count": int,             # other users marked helpful
    "is_verified_visit": bool,        # future: check-in confirmation
    "is_active": bool,                # can be soft-deleted by admin
    "created_at": datetime,
    "updated_at": datetime
}
# Indexes:
# { "target_type": 1, "target_id": 1, "is_active": 1 }
# { "user_id": 1 }
# { "rating": 1 }
# Unique: { "user_id": 1, "target_id": 1 }  — one review per user per target
```

### 6.6 `chat_sessions`
```python
{
    "_id": ObjectId,
    "session_id": str,                # UUID, indexed
    "user_id": ObjectId | None,       # null for anonymous
    "messages": [
        {
            "role": str,              # "user" | "assistant" | "system"
            "content": str,
            "sources": [              # only on assistant messages
                {
                    "title": str,
                    "type": str,      # "guide"|"listing"|"investment"|"general"
                    "id": str | None,
                    "score": float
                }
            ],
            "timestamp": datetime
        }
    ],
    "area_context": str | None,       # active area filter
    "user_type_context": str | None,  # "tourist"|"investor" etc.
    "metadata": {
        "total_tokens": int,
        "message_count": int
    },
    "created_at": datetime,
    "updated_at": datetime,
    "expires_at": datetime            # TTL index, 30 days
}
# Indexes:
# { "session_id": 1 }  unique
# { "user_id": 1 }
# { "expires_at": 1 }  TTL index, expireAfterSeconds: 0
```

### 6.7 `kb_documents` (RAG Knowledge Base)
```python
{
    "_id": ObjectId,
    "source_type": str,               # "guide"|"listing"|"investment"|"general"
    "source_ref_id": ObjectId | None, # link back to source collection
    "chunk_index": int,               # which chunk of the source document
    "content": str,                   # the actual text chunk
    "content_ar": str | None,         # Arabic version if available
    "metadata": {
        "title": str,
        "area": str,
        "category": str,
        "source_name": str            # human-readable source
    },
    "qdrant_id": str,                 # UUID used in Qdrant
    "embedded_model": str,            # which embedding model was used
    "embedded_at": datetime,
    "content_hash": str               # MD5 of content for dedup
}
# Indexes:
# { "qdrant_id": 1 }  unique
# { "source_ref_id": 1 }
# { "content_hash": 1 }  for dedup detection
```

### 6.8 `notifications`
```python
{
    "_id": ObjectId,
    "user_id": ObjectId,
    "type": str,                      # "system"|"investment_update"|"review_reply"
    "title": str,
    "title_ar": str,
    "body": str,
    "body_ar": str,
    "data": dict,                     # flexible payload (link, ref_id etc.)
    "is_read": bool,
    "created_at": datetime
}
# Indexes:
# { "user_id": 1, "is_read": 1, "created_at": -1 }
```

### 6.9 `file_refs`
```python
{
    "_id": ObjectId,
    "original_name": str,
    "stored_name": str,               # UUID-based filename
    "file_path": str,                 # relative path on disk
    "url": str,                       # public URL
    "mime_type": str,
    "size_bytes": int,
    "category": str,                  # "listing_image"|"guide_image"|"document"
    "ref_id": ObjectId | None,        # associated entity
    "uploaded_by": ObjectId,
    "created_at": datetime
}
# Indexes:
# { "ref_id": 1 }
# { "uploaded_by": 1 }
```

### 6.10 `investment_interests`
```python
{
    "_id": ObjectId,
    "user_id": ObjectId,
    "investment_id": ObjectId,
    "message": str | None,           # optional message from investor
    "contact_email": str,
    "contact_phone": str | None,
    "status": str,                   # "pending"|"contacted"|"closed"
    "created_at": datetime
}
# Indexes:
# { "investment_id": 1 }
# { "user_id": 1 }
# Unique: { "user_id": 1, "investment_id": 1 }
```

---

## 7. MongoDB Index Creation Script

```python
# app/db/mongo.py

async def create_indexes(db):
    """Run once on startup to ensure all indexes exist."""

    # users
    await db.users.create_index("email", unique=True)
    await db.users.create_index("role")

    # listings
    await db.listings.create_index([("category", 1), ("location.area", 1), ("is_active", 1)])
    await db.listings.create_index("slug", unique=True)
    await db.listings.create_index("tags")
    await db.listings.create_index([("is_featured", 1), ("created_at", -1)])
    await db.listings.create_index(
        [("title_ar", "text"), ("description_ar", "text"), ("tags", "text")],
        default_language="arabic"
    )

    # tourist_guide
    await db.tourist_guide.create_index([("area", 1), ("type", 1), ("is_active", 1)])
    await db.tourist_guide.create_index("slug", unique=True)
    await db.tourist_guide.create_index(
        [("name_ar", "text"), ("description_ar", "text")],
        default_language="arabic"
    )

    # investment_opportunities
    await db.investment_opportunities.create_index([("sector", 1), ("area", 1), ("status", 1)])
    await db.investment_opportunities.create_index(
        [("investment_range.min_egp", 1), ("investment_range.max_egp", 1)]
    )
    await db.investment_opportunities.create_index(
        [("title_ar", "text"), ("description_ar", "text")],
        default_language="arabic"
    )

    # reviews
    await db.reviews.create_index([("target_type", 1), ("target_id", 1), ("is_active", 1)])
    await db.reviews.create_index([("user_id", 1), ("target_id", 1)], unique=True)

    # chat_sessions
    await db.chat_sessions.create_index("session_id", unique=True)
    await db.chat_sessions.create_index("expires_at", expireAfterSeconds=0)

    # kb_documents
    await db.kb_documents.create_index("qdrant_id", unique=True)
    await db.kb_documents.create_index("content_hash")

    # notifications
    await db.notifications.create_index([("user_id", 1), ("is_read", 1), ("created_at", -1)])

    # file_refs
    await db.file_refs.create_index("ref_id")

    print("[DB] All indexes created successfully")
```

---

## 8. Complete Pydantic Schemas

### 8.1 Common Schemas
```python
# app/schemas/common.py
from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    pages: int

    @classmethod
    def build(cls, items, total, page, limit):
        import math
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=math.ceil(total / limit) if limit else 1
        )

class SuccessResponse(BaseModel):
    message: str
    id: Optional[str] = None

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[List[ErrorDetail]] = None
```

### 8.2 Auth Schemas
```python
# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, field_validator
from app.core.constants import UserRole

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.TOURIST

    @field_validator("password")
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserBrief"

class RefreshRequest(BaseModel):
    refresh_token: str

class UserBrief(BaseModel):
    id: str
    name: str
    email: str
    role: str
    avatar_url: str | None = None
```

### 8.3 Listing Schemas
```python
# app/schemas/listing.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.core.constants import ListingCategory, ListingSubCategory, Area

class ContactInfo(BaseModel):
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None

class CoordinatesSchema(BaseModel):
    lat: float
    lng: float

class LocationSchema(BaseModel):
    area: Area
    address: str
    address_ar: Optional[str] = None
    coordinates: Optional[CoordinatesSchema] = None

class ListingCreate(BaseModel):
    title: str
    title_ar: str
    description: Optional[str] = ""
    description_ar: Optional[str] = ""
    category: ListingCategory
    sub_category: Optional[ListingSubCategory] = None
    location: LocationSchema
    contact: Optional[ContactInfo] = None
    tags: List[str] = []
    price_range: Optional[str] = None   # "$"|"$$"|"$$$"
    amenities: List[str] = []

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    title_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    sub_category: Optional[str] = None
    contact: Optional[ContactInfo] = None
    tags: Optional[List[str]] = None
    price_range: Optional[str] = None
    amenities: Optional[List[str]] = None
    is_active: Optional[bool] = None

class ListingResponse(BaseModel):
    id: str
    title: str
    title_ar: str
    description: Optional[str] = None
    description_ar: Optional[str] = None
    category: str
    sub_category: Optional[str] = None
    location: LocationSchema
    contact: Optional[ContactInfo] = None
    tags: List[str] = []
    thumbnail: Optional[str] = None
    images: List[str] = []
    price_range: Optional[str] = None
    amenities: List[str] = []
    rating_avg: float = 0.0
    review_count: int = 0
    is_verified: bool = False
    is_featured: bool = False
    created_at: datetime
    created_by: str

class ListingFilters(BaseModel):
    category: Optional[ListingCategory] = None
    sub_category: Optional[str] = None
    area: Optional[Area] = None
    tags: Optional[List[str]] = None
    min_rating: Optional[float] = None
    is_verified: Optional[bool] = None
    is_featured: Optional[bool] = None
    page: int = 1
    limit: int = 20
```

### 8.4 Chat Schemas
```python
# app/schemas/chat.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatSource(BaseModel):
    title: str
    type: str
    id: Optional[str] = None
    score: float

class ChatMessage(BaseModel):
    role: str
    content: str
    sources: List[ChatSource] = []
    timestamp: datetime

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    area_filter: Optional[str] = None
    user_type_context: Optional[str] = None  # "tourist"|"investor"|"student"

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    sources: List[ChatSource] = []
    tokens_used: int = 0

class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
    message_count: int
```

---

## 9. Qdrant Vector Store — Complete Design

### Collection: `hena_kb`

```python
# app/db/qdrant.py
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, HnswConfigDiff,
    PayloadSchemaType, OptimizersConfigDiff
)

COLLECTION_NAME = "hena_kb"
VECTOR_DIM = 1536    # text-embedding-3-small
# OR: 384 for intfloat/multilingual-e5-small (free, runs on CPU)

async def init_qdrant_collection(client: AsyncQdrantClient):
    collections = await client.get_collections()
    existing = [c.name for c in collections.collections]
    if COLLECTION_NAME not in existing:
        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_DIM,
                distance=Distance.COSINE
            ),
            hnsw_config=HnswConfigDiff(
                m=16,               # default, good for demo
                ef_construct=100    # default
            ),
            optimizers_config=OptimizersConfigDiff(
                indexing_threshold=20000  # start indexing after 20k vectors
            )
        )
        # Create payload indexes for fast filtering
        await client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="area",
            field_schema=PayloadSchemaType.KEYWORD
        )
        await client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="source_type",
            field_schema=PayloadSchemaType.KEYWORD
        )
        await client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="category",
            field_schema=PayloadSchemaType.KEYWORD
        )
        print(f"[Qdrant] Collection '{COLLECTION_NAME}' created")
    else:
        print(f"[Qdrant] Collection '{COLLECTION_NAME}' already exists")
```

### Point Structure (what gets stored):
```python
{
    "id": "uuid-string",              # same as kb_documents.qdrant_id in Mongo
    "vector": [0.023, -0.451, ...],   # 1536-dim float array
    "payload": {
        "mongo_id": "string",         # kb_documents._id
        "source_ref_id": "string",    # original listing/guide._id
        "source_type": "guide",       # "guide"|"listing"|"investment"|"general"
        "title": "قصر الداخلة",
        "area": "الداخلة",
        "category": "historical",
        "content_preview": "...",     # first 300 chars
        "language": "ar"              # "ar"|"en"
    }
}
```

---

## 10. Redis Cache — Complete Key Design

```python
# app/db/redis.py
import json
import redis.asyncio as aioredis
from app.config import settings

# Key patterns and TTLs
CACHE_KEYS = {
    # Listings
    "listings_list":    ("listings:list:{category}:{area}:{page}:{limit}", 300),
    "listing_detail":   ("listings:detail:{id}", 600),
    "listing_featured": ("listings:featured:{area}", 600),

    # Tourist Guide
    "guide_list":       ("guide:list:{area}:{type_filter}:{page}", 1800),
    "guide_detail":     ("guide:detail:{id}", 1800),
    "guide_areas":      ("guide:areas:summary", 3600),

    # Investment
    "invest_list":      ("invest:list:{sector}:{area}:{page}", 600),
    "invest_detail":    ("invest:detail:{id}", 600),

    # Search
    "search":           ("search:{query_hash}", 120),

    # User sessions (refresh tokens)
    "refresh_token":    ("auth:refresh:{user_id}", 604800),  # 7 days

    # Rate limiting
    "rate_limit":       ("ratelimit:{ip}:{endpoint}", 60),   # per minute

    # Notifications count
    "notif_count":      ("notif:unread:{user_id}", 60),
}

class CacheHelper:
    def __init__(self, client: aioredis.Redis):
        self.r = client

    async def get(self, key: str):
        val = await self.r.get(key)
        return json.loads(val) if val else None

    async def set(self, key: str, data, ttl: int):
        await self.r.setex(key, ttl, json.dumps(data, default=str))

    async def delete(self, key: str):
        await self.r.delete(key)

    async def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern. Use sparingly."""
        keys = await self.r.keys(pattern)
        if keys:
            await self.r.delete(*keys)

    async def get_or_set(self, key: str, ttl: int, fetch_fn):
        data = await self.get(key)
        if data is not None:
            return data
        data = await fetch_fn()
        if data is not None:
            await self.set(key, data, ttl)
        return data

    async def increment_rate(self, key: str, window: int = 60) -> int:
        """Increment rate counter, returns current count."""
        pipe = self.r.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        results = await pipe.execute()
        return results[0]
```
# PART 3 — COMPLETE API DESIGN & SERVICE LAYER

## 11. Complete API Endpoints

### Base URL: `/api/v1`

---

### 11.1 Auth `/api/v1/auth`

| # | Method | Path | Auth | Description | Response |
|---|--------|------|------|-------------|----------|
| 1 | POST | `/register` | None | Create account | `TokenResponse` |
| 2 | POST | `/login` | None | Email+password login | `TokenResponse` |
| 3 | POST | `/refresh` | Refresh token | Get new access token | `TokenResponse` |
| 4 | POST | `/logout` | Bearer | Invalidate refresh token | `SuccessResponse` |
| 5 | GET | `/me` | Bearer | Current user profile | `UserProfile` |
| 6 | PATCH | `/me` | Bearer | Update own profile | `UserProfile` |
| 7 | POST | `/change-password` | Bearer | Change password | `SuccessResponse` |

---

### 11.2 Listings `/api/v1/listings`

| # | Method | Path | Auth | Description | Response |
|---|--------|------|------|-------------|----------|
| 1 | GET | `/` | None | List all (filter+paginate) | `Paginated[ListingResponse]` |
| 2 | GET | `/{id}` | None | Get single listing detail | `ListingResponse` |
| 3 | GET | `/slug/{slug}` | None | Get by SEO slug | `ListingResponse` |
| 4 | GET | `/featured` | None | Get featured listings | `List[ListingResponse]` |
| 5 | GET | `/nearby` | None | Get listings near lat/lng | `List[ListingResponse]` |
| 6 | POST | `/` | Bearer | Create new listing | `SuccessResponse` |
| 7 | PUT | `/{id}` | Bearer (owner/admin) | Full update | `ListingResponse` |
| 8 | PATCH | `/{id}` | Bearer (owner/admin) | Partial update | `ListingResponse` |
| 9 | DELETE | `/{id}` | Bearer (owner/admin) | Soft delete | `SuccessResponse` |
| 10 | POST | `/{id}/images` | Bearer (owner/admin) | Upload images | `SuccessResponse` |
| 11 | GET | `/{id}/reviews` | None | Get listing reviews | `Paginated[ReviewResponse]` |
| 12 | POST | `/{id}/views` | None | Increment view count | `SuccessResponse` |

**GET / Query Parameters:**
```
?category=accommodation
&sub_category=hotel
&area=الداخلة
&tags=wifi,parking
&min_rating=3.5
&is_verified=true
&is_featured=true
&page=1
&limit=20
&sort=rating_avg|-1    (field|direction)
```

---

### 11.3 Tourist Guide `/api/v1/guide`

| # | Method | Path | Auth | Description | Response |
|---|--------|------|------|-------------|----------|
| 1 | GET | `/attractions` | None | List attractions (filter) | `Paginated[GuideResponse]` |
| 2 | GET | `/attractions/{id}` | None | Get attraction detail | `GuideResponse` |
| 3 | GET | `/attractions/slug/{slug}` | None | Get by slug | `GuideResponse` |
| 4 | GET | `/areas` | None | All areas with stats | `List[AreaSummary]` |
| 5 | GET | `/featured` | None | Featured attractions | `List[GuideResponse]` |
| 6 | GET | `/map-pins` | None | All coords for map | `List[MapPin]` |
| 7 | POST | `/attractions` | Bearer (admin) | Create attraction | `SuccessResponse` |
| 8 | PUT | `/attractions/{id}` | Bearer (admin) | Update | `GuideResponse` |
| 9 | GET | `/attractions/{id}/reviews` | None | Get reviews | `Paginated[ReviewResponse]` |

---

### 11.4 Investment `/api/v1/investment`

| # | Method | Path | Auth | Description | Response |
|---|--------|------|------|-------------|----------|
| 1 | GET | `/` | None | List opportunities | `Paginated[InvestmentResponse]` |
| 2 | GET | `/{id}` | None | Get detail | `InvestmentResponse` |
| 3 | GET | `/sectors` | None | Sector summary stats | `List[SectorStat]` |
| 4 | GET | `/featured` | None | Featured opportunities | `List[InvestmentResponse]` |
| 5 | POST | `/` | Bearer (admin) | Create opportunity | `SuccessResponse` |
| 6 | PUT | `/{id}` | Bearer (admin) | Update | `InvestmentResponse` |
| 7 | POST | `/{id}/interest` | Bearer | Express investment interest | `SuccessResponse` |
| 8 | GET | `/{id}/interests` | Bearer (admin) | View interested investors | `List[InterestResponse]` |
| 9 | GET | `/my-interests` | Bearer | My expressed interests | `List[InterestResponse]` |

**GET / Query Parameters:**
```
?sector=agriculture
&area=الداخلة
&min_investment=100000
&max_investment=5000000
&status=available
&page=1
&limit=20
```

---

### 11.5 Search `/api/v1/search`

| # | Method | Path | Auth | Description | Response |
|---|--------|------|------|-------------|----------|
| 1 | GET | `/` | None | Unified text search | `SearchResults` |
| 2 | GET | `/semantic` | None | Semantic (vector) search | `SearchResults` |
| 3 | GET | `/autocomplete` | None | Autocomplete suggestions | `List[str]` |
| 4 | GET | `/trending` | None | Trending search terms | `List[str]` |

**GET / Query Parameters:**
```
?q=فندق في الخارجة
&type=all              # all | listing | guide | investment
&area=الخارجة
&page=1
&limit=10
```

---

### 11.6 Chat `/api/v1/chat`

| # | Method | Path | Auth | Description | Response |
|---|--------|------|------|-------------|----------|
| 1 | POST | `/message` | Optional Bearer | Send message, get AI reply | `ChatResponse` |
| 2 | POST | `/session` | Optional Bearer | Start new session | `SessionCreated` |
| 3 | GET | `/session/{session_id}` | Optional Bearer | Get session history | `SessionHistory` |
| 4 | DELETE | `/session/{session_id}` | Bearer | Delete session | `SuccessResponse` |
| 5 | GET | `/sessions` | Bearer | List my sessions | `List[SessionBrief]` |
| 6 | GET | `/suggestions` | None | Starter prompts by user type | `List[str]` |

---

### 11.7 Reviews `/api/v1/reviews`

| # | Method | Path | Auth | Description | Response |
|---|--------|------|------|-------------|----------|
| 1 | POST | `/` | Bearer | Create review | `ReviewResponse` |
| 2 | PUT | `/{id}` | Bearer (owner) | Update review | `ReviewResponse` |
| 3 | DELETE | `/{id}` | Bearer (owner/admin) | Delete review | `SuccessResponse` |
| 4 | POST | `/{id}/helpful` | Bearer | Mark as helpful | `SuccessResponse` |
| 5 | GET | `/my-reviews` | Bearer | My reviews | `List[ReviewResponse]` |

---

### 11.8 Files `/api/v1/files`

| # | Method | Path | Auth | Description | Response |
|---|--------|------|------|-------------|----------|
| 1 | POST | `/upload` | Bearer | Upload file(s) | `List[FileResponse]` |
| 2 | DELETE | `/{id}` | Bearer (owner/admin) | Delete file | `SuccessResponse` |
| 3 | GET | `/{filename}` | None | Serve static file | Binary |

---

### 11.9 Notifications `/api/v1/notifications`

| # | Method | Path | Auth | Description | Response |
|---|--------|------|------|-------------|----------|
| 1 | GET | `/` | Bearer | My notifications | `Paginated[NotifResponse]` |
| 2 | PATCH | `/{id}/read` | Bearer | Mark read | `SuccessResponse` |
| 3 | PATCH | `/read-all` | Bearer | Mark all read | `SuccessResponse` |
| 4 | GET | `/count` | Bearer | Unread count | `{"count": int}` |

---

### 11.10 Admin `/api/v1/admin`

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 1 | GET | `/stats` | Bearer (admin) | Platform statistics |
| 2 | GET | `/listings` | Bearer (admin) | All listings + unverified |
| 3 | PATCH | `/listings/{id}/verify` | Bearer (admin) | Approve listing |
| 4 | GET | `/users` | Bearer (admin) | All users |
| 5 | PATCH | `/users/{id}/status` | Bearer (admin) | Activate/deactivate |
| 6 | POST | `/kb/rebuild` | Bearer (admin) | Trigger RAG index rebuild |
| 7 | GET | `/investment/interests` | Bearer (admin) | All expressed interests |

---

## 12. Service Layer — Complete Implementation

### 12.1 `main.py` — App Factory
```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db.mongo import init_mongo, get_db
from app.db.redis import init_redis
from app.db.qdrant import init_qdrant_client
from app.api.router import api_router
from app.core.exceptions import register_exception_handlers
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.tasks.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[App] Starting up...")
    app.state.mongo = await init_mongo()
    app.state.redis = await init_redis()
    app.state.qdrant = await init_qdrant_client()
    await start_scheduler(app)
    print("[App] All services connected")
    yield
    # Shutdown
    print("[App] Shutting down...")
    app.state.mongo.close()
    await app.state.redis.close()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Hena Wadeena API — هنا وادينا",
        description="Smart platform for New Valley, Egypt",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Routes
    app.include_router(api_router, prefix="/api/v1")

    # Static files (frontend)
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

    # Exception handlers
    register_exception_handlers(app)

    # Health check
    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "services": {
                "mongo": "ok",
                "redis": "ok",
                "qdrant": "ok"
            }
        }

    return app

app = create_app()
```

---

### 12.2 `listing_service.py` — Full Service
```python
# app/services/listing_service.py
import re
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.redis import CacheHelper
from app.schemas.listing import ListingCreate, ListingUpdate, ListingFilters
from app.core.exceptions import NotFoundError, ForbiddenError

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[\s]+', '-', text)
    text = re.sub(r'[^\w\-]', '', text)
    return text

class ListingService:
    def __init__(self, db: AsyncIOMotorDatabase, cache: CacheHelper):
        self.col = db["listings"]
        self.cache = cache

    async def get_list(self, filters: ListingFilters) -> dict:
        cache_key = (
            f"listings:list:{filters.category}:{filters.area}:"
            f"{filters.page}:{filters.limit}"
        )
        return await self.cache.get_or_set(
            cache_key, ttl=300,
            fetch_fn=lambda: self._fetch_list(filters)
        )

    async def _fetch_list(self, f: ListingFilters) -> dict:
        query = {"is_active": True}
        if f.category:       query["category"] = f.category.value
        if f.area:           query["location.area"] = f.area.value
        if f.sub_category:   query["sub_category"] = f.sub_category
        if f.is_verified is not None: query["is_verified"] = f.is_verified
        if f.is_featured is not None: query["is_featured"] = f.is_featured
        if f.min_rating:     query["rating_avg"] = {"$gte": f.min_rating}
        if f.tags:
            query["tags"] = {"$all": f.tags}

        skip = (f.page - 1) * f.limit
        total = await self.col.count_documents(query)
        cursor = (self.col.find(query)
                  .sort("is_featured", -1)
                  .skip(skip)
                  .limit(f.limit))
        items = await cursor.to_list(length=f.limit)
        return {
            "items": [self._serialize(d) for d in items],
            "total": total, "page": f.page, "limit": f.limit
        }

    async def get_by_id(self, listing_id: str) -> dict:
        cache_key = f"listings:detail:{listing_id}"
        return await self.cache.get_or_set(
            cache_key, ttl=600,
            fetch_fn=lambda: self._fetch_by_id(listing_id)
        )

    async def _fetch_by_id(self, listing_id: str) -> dict:
        doc = await self.col.find_one(
            {"_id": ObjectId(listing_id), "is_active": True}
        )
        if not doc:
            raise NotFoundError("Listing not found")
        return self._serialize(doc)

    async def create(self, data: ListingCreate, user_id: str) -> str:
        base_slug = slugify(data.title_ar or data.title)
        slug = await self._unique_slug(base_slug)
        doc = {
            **data.model_dump(),
            "slug": slug,
            "location": data.location.model_dump(),
            "contact": data.contact.model_dump() if data.contact else {},
            "created_by": ObjectId(user_id),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "is_verified": False,
            "is_featured": False,
            "rating_avg": 0.0,
            "review_count": 0,
            "view_count": 0,
            "images": [],
            "thumbnail": None
        }
        result = await self.col.insert_one(doc)
        await self._bust_list_cache(data.category.value, data.location.area.value)
        return str(result.inserted_id)

    async def update(self, listing_id: str, data: ListingUpdate, user_id: str, role: str) -> dict:
        doc = await self.col.find_one({"_id": ObjectId(listing_id)})
        if not doc:
            raise NotFoundError("Listing not found")
        if str(doc["created_by"]) != user_id and role != "admin":
            raise ForbiddenError("Not authorized to update this listing")
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        await self.col.update_one(
            {"_id": ObjectId(listing_id)},
            {"$set": update_data}
        )
        await self.cache.delete(f"listings:detail:{listing_id}")
        return await self._fetch_by_id(listing_id)

    async def soft_delete(self, listing_id: str, user_id: str, role: str):
        doc = await self.col.find_one({"_id": ObjectId(listing_id)})
        if not doc:
            raise NotFoundError("Listing not found")
        if str(doc["created_by"]) != user_id and role != "admin":
            raise ForbiddenError("Not authorized")
        await self.col.update_one(
            {"_id": ObjectId(listing_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        await self.cache.delete(f"listings:detail:{listing_id}")

    async def increment_views(self, listing_id: str):
        await self.col.update_one(
            {"_id": ObjectId(listing_id)},
            {"$inc": {"view_count": 1}}
        )

    async def update_rating(self, listing_id: str):
        """Recalculate average rating from reviews collection."""
        from app.db.mongo import get_db_instance
        db = get_db_instance()
        pipeline = [
            {"$match": {"target_id": ObjectId(listing_id), "target_type": "listing", "is_active": True}},
            {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}}
        ]
        result = await db["reviews"].aggregate(pipeline).to_list(length=1)
        if result:
            await self.col.update_one(
                {"_id": ObjectId(listing_id)},
                {"$set": {"rating_avg": round(result[0]["avg"], 1), "review_count": result[0]["count"]}}
            )

    async def _unique_slug(self, base: str) -> str:
        slug, counter = base, 0
        while await self.col.find_one({"slug": slug}):
            counter += 1
            slug = f"{base}-{counter}"
        return slug

    async def _bust_list_cache(self, category: str, area: str):
        await self.cache.delete_pattern(f"listings:list:{category}:{area}:*")
        await self.cache.delete_pattern(f"listings:list:None:{area}:*")
        await self.cache.delete_pattern(f"listings:list:{category}:None:*")

    def _serialize(self, doc: dict) -> dict:
        doc["id"] = str(doc.pop("_id"))
        doc["created_by"] = str(doc.get("created_by", ""))
        return doc
```

---

### 12.3 `review_service.py`
```python
# app/services/review_service.py
from datetime import datetime
from bson import ObjectId
from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError

class ReviewService:
    def __init__(self, db, cache):
        self.col = db["reviews"]
        self.db = db
        self.cache = cache

    async def create(self, user_id, user_name, user_avatar, target_type, target_id,
                     rating, body, title=None) -> dict:
        # Check no duplicate
        existing = await self.col.find_one({
            "user_id": ObjectId(user_id),
            "target_id": ObjectId(target_id)
        })
        if existing:
            raise ConflictError("You already reviewed this item")

        doc = {
            "user_id": ObjectId(user_id),
            "user_name": user_name,
            "user_avatar": user_avatar,
            "target_type": target_type,
            "target_id": ObjectId(target_id),
            "rating": rating,
            "title": title,
            "body": body,
            "images": [],
            "helpful_count": 0,
            "is_active": True,
            "is_verified_visit": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.col.insert_one(doc)

        # Update rating on parent
        await self._update_parent_rating(target_type, target_id)

        doc["id"] = str(result.inserted_id)
        return doc

    async def get_for_target(self, target_type, target_id, page=1, limit=10) -> dict:
        query = {"target_type": target_type, "target_id": ObjectId(target_id), "is_active": True}
        skip = (page - 1) * limit
        total = await self.col.count_documents(query)
        cursor = self.col.find(query).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        return {"items": [self._serialize(r) for r in items], "total": total}

    async def _update_parent_rating(self, target_type: str, target_id: str):
        collection_map = {"listing": "listings", "guide": "tourist_guide"}
        col_name = collection_map.get(target_type)
        if not col_name:
            return
        pipeline = [
            {"$match": {"target_id": ObjectId(target_id), "target_type": target_type, "is_active": True}},
            {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}}
        ]
        result = await self.col.aggregate(pipeline).to_list(length=1)
        if result:
            await self.db[col_name].update_one(
                {"_id": ObjectId(target_id)},
                {"$set": {"rating_avg": round(result[0]["avg"], 1), "review_count": result[0]["count"]}}
            )

    def _serialize(self, doc):
        doc["id"] = str(doc.pop("_id"))
        doc["user_id"] = str(doc["user_id"])
        doc["target_id"] = str(doc["target_id"])
        return doc
```

---

### 12.4 `file_service.py`
```python
# app/services/file_service.py
import uuid
import os
import aiofiles
from fastapi import UploadFile
from datetime import datetime
from bson import ObjectId
from app.config import settings
from app.core.exceptions import ValidationError

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

class FileService:
    def __init__(self, db):
        self.col = db["file_refs"]

    async def upload(self, files: list[UploadFile], category: str,
                     ref_id: str | None, user_id: str) -> list[dict]:
        results = []
        for f in files:
            if f.content_type not in ALLOWED_TYPES:
                raise ValidationError(f"File type {f.content_type} not allowed")
            content = await f.read()
            if len(content) > MAX_SIZE_BYTES:
                raise ValidationError("File exceeds 5MB limit")

            ext = f.filename.split(".")[-1].lower()
            stored_name = f"{uuid.uuid4().hex}.{ext}"
            file_path = os.path.join(settings.upload_dir, category, stored_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            async with aiofiles.open(file_path, "wb") as out:
                await out.write(content)

            url = f"{settings.base_url}/api/v1/files/{category}/{stored_name}"
            doc = {
                "original_name": f.filename,
                "stored_name": stored_name,
                "file_path": file_path,
                "url": url,
                "mime_type": f.content_type,
                "size_bytes": len(content),
                "category": category,
                "ref_id": ObjectId(ref_id) if ref_id else None,
                "uploaded_by": ObjectId(user_id),
                "created_at": datetime.utcnow()
            }
            result = await self.col.insert_one(doc)
            results.append({"id": str(result.inserted_id), "url": url})
        return results
```

---

### 12.5 `notification_service.py`
```python
# app/services/notification_service.py
from datetime import datetime
from bson import ObjectId

class NotificationService:
    def __init__(self, db, cache):
        self.col = db["notifications"]
        self.cache = cache

    async def send(self, user_id: str, type_: str, title: str,
                   title_ar: str, body: str, body_ar: str, data: dict = None):
        doc = {
            "user_id": ObjectId(user_id),
            "type": type_,
            "title": title,
            "title_ar": title_ar,
            "body": body,
            "body_ar": body_ar,
            "data": data or {},
            "is_read": False,
            "created_at": datetime.utcnow()
        }
        await self.col.insert_one(doc)
        # Bust unread count cache
        await self.cache.delete(f"notif:unread:{user_id}")

    async def get_unread_count(self, user_id: str) -> int:
        cache_key = f"notif:unread:{user_id}"
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return cached
        count = await self.col.count_documents(
            {"user_id": ObjectId(user_id), "is_read": False}
        )
        await self.cache.set(cache_key, count, ttl=60)
        return count

    async def mark_all_read(self, user_id: str):
        await self.col.update_many(
            {"user_id": ObjectId(user_id), "is_read": False},
            {"$set": {"is_read": True}}
        )
        await self.cache.delete(f"notif:unread:{user_id}")
```

---

### 12.6 `search_service.py` — Unified Text + Semantic Search
```python
# app/services/search_service.py
import hashlib
from motor.motor_asyncio import AsyncIOMotorDatabase
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.db.redis import CacheHelper
from app.core.embeddings import embed_text

class SearchService:
    def __init__(self, db: AsyncIOMotorDatabase, qdrant: AsyncQdrantClient, cache: CacheHelper):
        self.db = db
        self.qdrant = qdrant
        self.cache = cache

    async def text_search(self, q: str, type_filter: str, area: str, page: int, limit: int) -> dict:
        qhash = hashlib.md5(f"text:{q}:{type_filter}:{area}:{page}".encode()).hexdigest()
        return await self.cache.get_or_set(
            f"search:{qhash}", ttl=120,
            fetch_fn=lambda: self._text_search(q, type_filter, area, page, limit)
        )

    async def _text_search(self, q, type_filter, area, page, limit) -> dict:
        results = []
        collections = {
            "listing": ("listings", ["title_ar", "description_ar", "tags"]),
            "guide":   ("tourist_guide", ["name_ar", "description_ar"]),
            "investment": ("investment_opportunities", ["title_ar", "description_ar"]),
        }
        targets = {k: v for k, v in collections.items()
                   if type_filter in ("all", k)}

        for dtype, (col_name, _) in targets.items():
            col = self.db[col_name]
            query = {"$text": {"$search": q}, "is_active": True}
            if area:
                query["$or"] = [{"location.area": area}, {"area": area}]
            cursor = col.find(
                query,
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(20)
            docs = await cursor.to_list(20)
            for doc in docs:
                results.append({
                    "type": dtype,
                    "id": str(doc["_id"]),
                    "title": doc.get("title_ar") or doc.get("name_ar", ""),
                    "description": (doc.get("description_ar") or "")[:150],
                    "area": doc.get("location", {}).get("area") or doc.get("area", ""),
                    "thumbnail": doc.get("thumbnail"),
                    "score": doc.get("score", 0)
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        skip = (page - 1) * limit
        paginated = results[skip:skip + limit]
        return {"query": q, "results": paginated, "total": len(results), "type": "text"}

    async def semantic_search(self, q: str, type_filter: str, area: str, limit: int = 10) -> dict:
        """Vector-based semantic search via Qdrant."""
        vector = await embed_text(q)
        qdrant_filter = None
        conditions = []
        if area:
            conditions.append(FieldCondition(key="area", match=MatchValue(value=area)))
        if type_filter != "all":
            conditions.append(FieldCondition(key="source_type", match=MatchValue(value=type_filter)))
        if conditions:
            qdrant_filter = Filter(must=conditions)

        hits = await self.qdrant.search(
            collection_name="hena_kb",
            query_vector=vector,
            limit=limit,
            query_filter=qdrant_filter,
            with_payload=True
        )
        results = [
            {
                "type": h.payload.get("source_type"),
                "id": h.payload.get("source_ref_id"),
                "title": h.payload.get("title", ""),
                "description": h.payload.get("content_preview", "")[:150],
                "area": h.payload.get("area", ""),
                "score": h.score
            }
            for h in hits
        ]
        return {"query": q, "results": results, "total": len(results), "type": "semantic"}

    async def autocomplete(self, q: str, limit: int = 5) -> list[str]:
        """Return title suggestions matching the prefix."""
        regex = {"$regex": f"^{q}", "$options": "i"}
        results = []
        for col_name in ["listings", "tourist_guide", "investment_opportunities"]:
            col = self.db[col_name]
            field = "name_ar" if col_name == "tourist_guide" else "title_ar"
            cursor = col.find({"is_active": True, field: regex}, {field: 1}).limit(3)
            docs = await cursor.to_list(3)
            results.extend([d.get(field, "") for d in docs])
        return results[:limit]
```
# PART 4 — COMPLETE RAG PIPELINE

## 13. RAG Architecture

```
╔══════════════════════════════════════════════════════════════════════╗
║                    RAG PIPELINE — HENA WADEENA                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   INGESTION PIPELINE (runs offline / on schedule)                   ║
║   ─────────────────────────────────────────────────────────────     ║
║                                                                      ║
║   MongoDB Collections                                                ║
║   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               ║
║   │ tourist_guide│ │  listings    │ │ investments  │               ║
║   └──────┬───────┘ └──────┬───────┘ └──────┬───────┘               ║
║          └────────────────┴────────────────┘                        ║
║                           │                                         ║
║                    ┌──────▼───────┐                                 ║
║                    │  Document    │  Raw text extracted from docs    ║
║                    │   Loader     │                                  ║
║                    └──────┬───────┘                                 ║
║                           │                                         ║
║                    ┌──────▼───────┐                                 ║
║                    │    Text      │  Split into 400-token chunks     ║
║                    │   Chunker    │  with 50-token overlap           ║
║                    └──────┬───────┘                                 ║
║                           │                                         ║
║                    ┌──────▼───────┐                                 ║
║                    │  Embedding   │  text-embedding-3-small          ║
║                    │   Model      │  OR multilingual-e5-small        ║
║                    └──────┬───────┘                                 ║
║                           │  (vector + payload)                     ║
║                    ┌──────▼───────┐                                 ║
║                    │    Qdrant    │  hena_kb collection              ║
║                    │   Upsert     │                                  ║
║                    └─────────────┘                                  ║
║                                                                      ║
║   RETRIEVAL PIPELINE (runs on every chat message)                   ║
║   ─────────────────────────────────────────────────────────────     ║
║                                                                      ║
║   User Message: "ما هي أفضل الأماكن في الداخلة؟"                   ║
║          │                                                           ║
║   ┌──────▼───────────────────────────────────────────────────────┐  ║
║   │  1. QUERY ANALYSIS                                            │  ║
║   │     · Detect language (ar/en)                                 │  ║
║   │     · Extract area intent → "الداخلة"                        │  ║
║   │     · Extract user type intent → "tourist"                    │  ║
║   │     · Build filter conditions for Qdrant                      │  ║
║   └──────┬───────────────────────────────────────────────────────┘  ║
║          │                                                           ║
║   ┌──────▼───────────────────────────────────────────────────────┐  ║
║   │  2. EMBEDDING                                                 │  ║
║   │     · embed(user_message) → 1536-dim vector                   │  ║
║   └──────┬───────────────────────────────────────────────────────┘  ║
║          │                                                           ║
║   ┌──────▼───────────────────────────────────────────────────────┐  ║
║   │  3. VECTOR SEARCH (Qdrant)                                    │  ║
║   │     · cosine similarity search                                │  ║
║   │     · filter: area="الداخلة"  (if detected)                  │  ║
║   │     · top_k = 5 chunks                                        │  ║
║   │     · score_threshold = 0.35                                  │  ║
║   └──────┬───────────────────────────────────────────────────────┘  ║
║          │  top-5 chunks with metadata                              ║
║   ┌──────▼───────────────────────────────────────────────────────┐  ║
║   │  4. CONTEXT ASSEMBLY                                          │  ║
║   │     · Fetch full content from MongoDB kb_documents            │  ║
║   │     · Deduplicate by source_ref_id                            │  ║
║   │     · Rank by: score × recency_boost                          │  ║
║   └──────┬───────────────────────────────────────────────────────┘  ║
║          │                                                           ║
║   ┌──────▼───────────────────────────────────────────────────────┐  ║
║   │  5. PROMPT CONSTRUCTION                                       │  ║
║   │     System: role + knowledge base context                     │  ║
║   │     History: last 4 turns (user+assistant)                    │  ║
║   │     User: current message                                     │  ║
║   └──────┬───────────────────────────────────────────────────────┘  ║
║          │                                                           ║
║   ┌──────▼───────────────────────────────────────────────────────┐  ║
║   │  6. LLM GENERATION                                            │  ║
║   │     · gpt-4o-mini (fast, cheap) OR qwen2.5:7b (free)         │  ║
║   │     · max_tokens=600, temperature=0.4                         │  ║
║   └──────┬───────────────────────────────────────────────────────┘  ║
║          │                                                           ║
║   ┌──────▼───────────────────────────────────────────────────────┐  ║
║   │  7. RESPONSE POST-PROCESSING                                  │  ║
║   │     · Attach source citations                                 │  ║
║   │     · Save message pair to MongoDB chat_sessions              │  ║
║   │     · Return to user with sources                             │  ║
║   └──────────────────────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 14. Chunking Strategy

```python
# rag/ingestion/chunker.py

class DocumentChunker:
    """
    Strategy for MVP:
    - Max 400 tokens per chunk (≈ 300 Arabic words)
    - 50-token overlap between chunks (sliding window)
    - Never split mid-sentence
    - Prepend metadata header to each chunk for context
    """

    def __init__(self, max_tokens: int = 400, overlap: int = 50):
        self.max_tokens = max_tokens
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: dict) -> list[str]:
        """Split text into chunks, each prepended with metadata context."""
        sentences = self._split_sentences(text)
        chunks = []
        current_chunk = []
        current_len = 0

        for sentence in sentences:
            sentence_len = self._approx_tokens(sentence)
            if current_len + sentence_len > self.max_tokens and current_chunk:
                chunk_text = self._build_chunk(" ".join(current_chunk), metadata)
                chunks.append(chunk_text)
                # Overlap: keep last N tokens worth of sentences
                overlap_sentences = self._get_overlap(current_chunk)
                current_chunk = overlap_sentences + [sentence]
                current_len = sum(self._approx_tokens(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_len += sentence_len

        if current_chunk:
            chunks.append(self._build_chunk(" ".join(current_chunk), metadata))

        return chunks

    def _build_chunk(self, content: str, metadata: dict) -> str:
        """Prepend context header so each chunk is self-contained."""
        header_parts = []
        if metadata.get("title"):
            header_parts.append(f"العنوان: {metadata['title']}")
        if metadata.get("area"):
            header_parts.append(f"المنطقة: {metadata['area']}")
        if metadata.get("category"):
            header_parts.append(f"التصنيف: {metadata['category']}")
        header = " | ".join(header_parts)
        return f"{header}\n{content}" if header else content

    def _split_sentences(self, text: str) -> list[str]:
        """Split by Arabic and English sentence boundaries."""
        import re
        sentences = re.split(r'(?<=[.!؟\n])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _approx_tokens(self, text: str) -> int:
        """Rough estimate: 1 token ≈ 4 chars for Arabic."""
        return max(1, len(text) // 4)

    def _get_overlap(self, sentences: list[str]) -> list[str]:
        """Return the last few sentences for overlap."""
        overlap_tokens = 0
        overlap = []
        for s in reversed(sentences):
            overlap_tokens += self._approx_tokens(s)
            if overlap_tokens > self.overlap:
                break
            overlap.insert(0, s)
        return overlap
```

---

## 15. Complete Ingestion Pipeline

```python
# rag/ingestion/pipeline.py
import uuid
import hashlib
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct
from app.core.embeddings import embed_text
from rag.ingestion.chunker import DocumentChunker

class IngestionPipeline:
    def __init__(self, db: AsyncIOMotorDatabase, qdrant: AsyncQdrantClient):
        self.db = db
        self.qdrant = qdrant
        self.chunker = DocumentChunker(max_tokens=400, overlap=50)
        self.collection = "hena_kb"
        self.batch_size = 20  # upsert batch size

    async def run_full(self):
        """Ingest all collections into Qdrant."""
        print("[RAG] Starting full ingestion...")
        await self.ingest_tourist_guide()
        await self.ingest_listings()
        await self.ingest_investments()
        await self.ingest_general_docs()
        print("[RAG] Full ingestion complete")

    async def ingest_tourist_guide(self):
        print("[RAG] Ingesting tourist_guide...")
        async for doc in self.db["tourist_guide"].find({"is_active": True}):
            text = self._build_guide_text(doc)
            meta = {
                "title": doc.get("name_ar", ""),
                "area": doc.get("area", ""),
                "category": doc.get("type", ""),
                "source_type": "guide",
                "source_ref_id": str(doc["_id"])
            }
            await self._process_document(text, meta, str(doc["_id"]))
        print("[RAG] tourist_guide done")

    async def ingest_listings(self):
        print("[RAG] Ingesting listings...")
        async for doc in self.db["listings"].find({"is_active": True}):
            text = self._build_listing_text(doc)
            meta = {
                "title": doc.get("title_ar", ""),
                "area": doc.get("location", {}).get("area", ""),
                "category": doc.get("category", ""),
                "source_type": "listing",
                "source_ref_id": str(doc["_id"])
            }
            await self._process_document(text, meta, str(doc["_id"]))
        print("[RAG] listings done")

    async def ingest_investments(self):
        print("[RAG] Ingesting investments...")
        async for doc in self.db["investment_opportunities"].find({"status": "available"}):
            text = self._build_investment_text(doc)
            meta = {
                "title": doc.get("title_ar", ""),
                "area": doc.get("area", ""),
                "category": doc.get("sector", ""),
                "source_type": "investment",
                "source_ref_id": str(doc["_id"])
            }
            await self._process_document(text, meta, str(doc["_id"]))
        print("[RAG] investments done")

    async def ingest_general_docs(self):
        """Ingest static knowledge documents from JSON file."""
        import json, os
        path = "seed/data/general_knowledge.json"
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            docs = json.load(f)
        for doc in docs:
            meta = {
                "title": doc.get("title", ""),
                "area": doc.get("area", "عام"),
                "category": doc.get("category", "general"),
                "source_type": "general",
                "source_ref_id": None
            }
            await self._process_document(doc["content"], meta, None)

    async def _process_document(self, text: str, meta: dict, source_ref_id: str | None):
        """Chunk, embed, deduplicate, and upsert one document."""
        chunks = self.chunker.chunk_text(text, meta)
        points = []

        for i, chunk in enumerate(chunks):
            content_hash = hashlib.md5(chunk.encode()).hexdigest()
            # Skip if already ingested (by hash)
            existing = await self.db["kb_documents"].find_one({"content_hash": content_hash})
            if existing:
                continue

            vector = await embed_text(chunk)
            point_id = str(uuid.uuid4())

            point = PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    **meta,
                    "content_preview": chunk[:300],
                    "language": "ar",
                    "chunk_index": i
                }
            )
            points.append(point)

            # Save to MongoDB
            await self.db["kb_documents"].insert_one({
                "source_type": meta["source_type"],
                "source_ref_id": source_ref_id,
                "chunk_index": i,
                "content": chunk,
                "metadata": meta,
                "qdrant_id": point_id,
                "embedded_model": "text-embedding-3-small",
                "embedded_at": datetime.utcnow(),
                "content_hash": content_hash
            })

        # Upsert to Qdrant in batches
        for j in range(0, len(points), self.batch_size):
            batch = points[j:j + self.batch_size]
            if batch:
                await self.qdrant.upsert(collection_name=self.collection, points=batch)

    def _build_guide_text(self, doc: dict) -> str:
        parts = [
            doc.get("name_ar", ""),
            doc.get("description_ar", ""),
            doc.get("history_ar", "") or "",
            "نصائح: " + " ".join(doc.get("tips_ar", [])),
            f"أفضل موسم للزيارة: {doc.get('best_season', '')}",
            f"رسوم الدخول: {doc.get('entry_fee', {}).get('adults_egp', 0)} جنيه",
            f"ساعات العمل: {doc.get('opening_hours', '')}",
        ]
        return "\n".join(filter(None, parts))

    def _build_listing_text(self, doc: dict) -> str:
        location = doc.get("location", {})
        contact = doc.get("contact", {})
        parts = [
            doc.get("title_ar", ""),
            doc.get("description_ar", ""),
            f"العنوان: {location.get('address_ar', '')}",
            f"المنطقة: {location.get('area', '')}",
            f"التصنيف: {doc.get('sub_category', doc.get('category', ''))}",
            f"التواصل: هاتف {contact.get('phone', '')}",
            f"المميزات: {', '.join(doc.get('tags', []))}",
        ]
        return "\n".join(filter(None, parts))

    def _build_investment_text(self, doc: dict) -> str:
        inv_range = doc.get("investment_range", {})
        parts = [
            doc.get("title_ar", ""),
            doc.get("description_ar", ""),
            f"القطاع: {doc.get('sector', '')}",
            f"المنطقة: {doc.get('area', '')}",
            f"حجم الاستثمار: {inv_range.get('min_egp', 0):,} - {inv_range.get('max_egp', 0):,} جنيه",
            f"العائد المتوقع: {doc.get('expected_return_pct', 0)}%",
            f"المحفزات: {', '.join(doc.get('incentives_ar', []))}",
        ]
        return "\n".join(filter(None, parts))
```

---

## 16. Complete Chat Service (RAG Core)

```python
# app/services/chat_service.py
import uuid
from datetime import datetime, timedelta
from bson import ObjectId
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from openai import AsyncOpenAI
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.embeddings import embed_text
from app.config import settings

SYSTEM_PROMPT_TEMPLATE = """أنت مساعد ذكي متخصص في منطقة الوادي الجديد في مصر، وتخدم المستخدمين بمعلومات دقيقة عن:
- المناطق السياحية والتاريخية (الخارجة، الداخلة، الفرافرة، باريس، بلاط)
- الخدمات والأعمال والإقامة
- الفرص الاستثمارية والسوق المحلي
- المعلومات اليومية للمواطنين والطلاب

السياق المتاح من قاعدة البيانات:
───────────────────────────────────
{context}
───────────────────────────────────

تعليمات:
- أجب بنفس لغة السؤال (عربي أو إنجليزي)
- استند إلى السياق المتاح أولاً
- إذا لم تجد معلومة في السياق، قل ذلك بوضوح
- كن مختصراً ومفيداً
- عند ذكر أماكن أو خدمات، اذكر المنطقة دائماً
- لا تخترع أرقام هواتف أو عناوين"""

class ChatService:
    def __init__(self, db: AsyncIOMotorDatabase, qdrant: AsyncQdrantClient):
        self.db = db
        self.qdrant = qdrant
        self.sessions_col = db["chat_sessions"]
        self.kb_col = db["kb_documents"]
        self.llm = AsyncOpenAI(api_key=settings.openai_api_key)
        self.collection = "hena_kb"

    async def process(self, session_id: str | None, message: str,
                      area_filter: str | None, user_type: str | None,
                      user_id: str | None) -> dict:

        # 1. Get or create session
        session = await self._get_or_create_session(session_id, user_id)

        # 2. Retrieve context from Qdrant
        context_chunks = await self._retrieve(message, area_filter, user_type)

        # 3. Build prompt context string
        context_text = self._format_context(context_chunks)
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context_text)

        # 4. Build message history (last 8 messages = 4 turns)
        history = session.get("messages", [])[-8:]
        openai_messages = [{"role": "system", "content": system_prompt}]
        for h in history:
            if h["role"] in ("user", "assistant"):
                openai_messages.append({"role": h["role"], "content": h["content"]})
        openai_messages.append({"role": "user", "content": message})

        # 5. Call LLM
        completion = await self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            max_tokens=600,
            temperature=0.4
        )
        reply = completion.choices[0].message.content
        tokens = completion.usage.total_tokens

        # 6. Build source list for response
        sources = [
            {
                "title": c.payload.get("title", ""),
                "type": c.payload.get("source_type", ""),
                "id": c.payload.get("source_ref_id"),
                "area": c.payload.get("area", ""),
                "score": round(c.score, 3)
            }
            for c in context_chunks if c.score > 0.4
        ]

        # 7. Persist to MongoDB
        now = datetime.utcnow()
        await self.sessions_col.update_one(
            {"session_id": session["session_id"]},
            {
                "$push": {
                    "messages": {
                        "$each": [
                            {"role": "user", "content": message, "sources": [], "timestamp": now},
                            {"role": "assistant", "content": reply, "sources": sources, "timestamp": now}
                        ]
                    }
                },
                "$set": {
                    "updated_at": now,
                    "expires_at": now + timedelta(days=30)
                },
                "$inc": {
                    "metadata.total_tokens": tokens,
                    "metadata.message_count": 1
                }
            }
        )

        return {
            "session_id": session["session_id"],
            "reply": reply,
            "sources": sources,
            "tokens_used": tokens
        }

    async def _retrieve(self, query: str, area: str | None, user_type: str | None):
        """Embed query and search Qdrant."""
        vector = await embed_text(query)

        conditions = []
        if area:
            conditions.append(FieldCondition(key="area", match=MatchValue(value=area)))

        # User type hinting: bias towards relevant content types
        if user_type == "investor":
            conditions.append(
                FieldCondition(key="source_type", match=MatchValue(value="investment"))
            )

        qdrant_filter = Filter(must=conditions) if conditions else None

        results = await self.qdrant.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=6,
            query_filter=qdrant_filter,
            score_threshold=0.35,
            with_payload=True
        )

        # If filtered results are too few, retry without filter
        if len(results) < 2 and qdrant_filter:
            results = await self.qdrant.search(
                collection_name=self.collection,
                query_vector=vector,
                limit=5,
                score_threshold=0.35,
                with_payload=True
            )

        return results

    def _format_context(self, chunks) -> str:
        if not chunks:
            return "لا توجد معلومات متاحة في قاعدة البيانات لهذا الموضوع."
        parts = []
        seen_refs = set()
        for c in chunks:
            ref = c.payload.get("source_ref_id", "")
            if ref in seen_refs:
                continue
            seen_refs.add(ref)
            title = c.payload.get("title", "")
            area = c.payload.get("area", "")
            content = c.payload.get("content_preview", "")
            src_type = c.payload.get("source_type", "")
            label = {"guide": "🏛️ معلم سياحي", "listing": "🏪 خدمة",
                     "investment": "💼 فرصة استثمارية", "general": "ℹ️ معلومة"}.get(src_type, "")
            parts.append(f"{label} [{area}] {title}\n{content}")
        return "\n\n".join(parts)

    async def _get_or_create_session(self, session_id: str | None, user_id: str | None) -> dict:
        if session_id:
            session = await self.sessions_col.find_one({"session_id": session_id})
            if session:
                return session
        new_id = str(uuid.uuid4())
        now = datetime.utcnow()
        session = {
            "session_id": new_id,
            "user_id": ObjectId(user_id) if user_id else None,
            "messages": [],
            "area_context": None,
            "user_type_context": None,
            "metadata": {"total_tokens": 0, "message_count": 0},
            "created_at": now,
            "updated_at": now,
            "expires_at": now + timedelta(days=30)
        }
        await self.sessions_col.insert_one(session)
        return session

    async def get_suggestions(self, user_type: str = "tourist") -> list[str]:
        """Return starter prompt suggestions by user type."""
        suggestions = {
            "tourist": [
                "ما أجمل الأماكن السياحية في الداخلة؟",
                "كيف أصل من القاهرة إلى الخارجة؟",
                "ما أفضل فنادق الوادي الجديد؟",
                "ما تكلفة زيارة واحة الفرافرة؟",
            ],
            "investor": [
                "ما الفرص الاستثمارية المتاحة في الزراعة؟",
                "ما حوافز الاستثمار في الوادي الجديد؟",
                "ما القطاعات الأكثر ربحية للاستثمار؟",
                "كيف أتواصل مع جهاز الاستثمار؟",
            ],
            "student": [
                "ما المساكن الطلابية المتاحة في الخارجة؟",
                "أين أجد أرخص السكن في الوادي الجديد؟",
                "ما الخدمات اليومية المتاحة للطلاب؟",
            ],
            "citizen": [
                "ما أقرب مستشفى في منطقتي؟",
                "أين مراكز الخدمات الحكومية في الخارجة؟",
                "ما محلات السوبر ماركت في الداخلة؟",
            ]
        }
        return suggestions.get(user_type, suggestions["tourist"])
```

---

## 17. Embedding Abstraction

```python
# app/core/embeddings.py
"""
Two options:
  OPTION A: OpenAI (costs money, best quality for Arabic)
  OPTION B: Local model (free, good quality, runs on CPU)
Set EMBEDDING_PROVIDER in .env
"""
from app.config import settings

async def embed_text(text: str) -> list[float]:
    """Single entry point for all embedding operations."""
    text = text.strip().replace("\n", " ")[:6000]
    if settings.embedding_provider == "openai":
        return await _embed_openai(text)
    else:
        return await _embed_local(text)

async def _embed_openai(text: str) -> list[float]:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding  # dim=1536

def _embed_local_sync(text: str) -> list[float]:
    """Run in thread pool to avoid blocking event loop."""
    from sentence_transformers import SentenceTransformer
    import numpy as np
    # Load once (module-level singleton)
    global _local_model
    if "_local_model" not in globals():
        _local_model = SentenceTransformer("intfloat/multilingual-e5-small")
    # Prepend "query: " for e5 models
    embedding = _local_model.encode(f"query: {text}", normalize_embeddings=True)
    return embedding.tolist()  # dim=384

async def _embed_local(text: str) -> list[float]:
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _embed_local_sync, text)

# For ingestion (documents), use "passage: " prefix with e5 models
async def embed_document(text: str) -> list[float]:
    if settings.embedding_provider == "openai":
        return await _embed_openai(text)
    import asyncio
    loop = asyncio.get_event_loop()
    def _local_doc(t):
        global _local_model
        if "_local_model" not in globals():
            from sentence_transformers import SentenceTransformer
            _local_model = SentenceTransformer("intfloat/multilingual-e5-small")
        return _local_model.encode(f"passage: {t}", normalize_embeddings=True).tolist()
    return await loop.run_in_executor(None, _local_doc, text)
```

---

## 18. Background Tasks

```python
# app/tasks/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

async def start_scheduler(app):
    from app.tasks.index_rebuild import rebuild_index
    from app.tasks.cleanup import cleanup_sessions

    # Rebuild Qdrant index every night at 2 AM
    scheduler.add_job(
        lambda: rebuild_index(app.state.mongo, app.state.qdrant),
        trigger=CronTrigger(hour=2, minute=0),
        id="nightly_index_rebuild",
        replace_existing=True
    )

    # Clean expired sessions every 6 hours
    scheduler.add_job(
        lambda: cleanup_sessions(app.state.mongo),
        trigger=CronTrigger(hour="*/6"),
        id="session_cleanup",
        replace_existing=True
    )

    scheduler.start()
    print("[Scheduler] Background tasks started")


# app/tasks/index_rebuild.py
async def rebuild_index(db, qdrant):
    """Ingest any new/updated documents that aren't in Qdrant yet."""
    from rag.ingestion.pipeline import IngestionPipeline
    print("[Task] Starting incremental index rebuild...")
    pipeline = IngestionPipeline(db, qdrant)
    await pipeline.run_full()   # For MVP: full rebuild nightly
    print("[Task] Index rebuild complete")


# app/tasks/cleanup.py
from datetime import datetime
async def cleanup_sessions(db):
    """Remove expired sessions (belt-and-suspenders alongside TTL index)."""
    result = await db["chat_sessions"].delete_many(
        {"expires_at": {"$lt": datetime.utcnow()}}
    )
    print(f"[Task] Cleaned {result.deleted_count} expired sessions")
```
# PART 5 — FRONTEND, AUTH & SECURITY

## 19. Frontend Architecture

**Decision: Vanilla HTML + Tailwind CSS (CDN) + Alpine.js**

No build step. Every page is a standalone HTML file served by Nginx.
FastAPI also serves them via `StaticFiles` during development.

```
frontend/
├── index.html          Landing page — hero, features, areas map
├── login.html          Login form
├── register.html       Registration with role selection
├── explorer.html       Main browsing page — listings + filter sidebar + map
├── listing_detail.html Full listing with reviews, contact, map pin
├── guide.html          Tourist guide list — filter by area/type
├── guide_detail.html   Attraction detail with photo gallery, tips
├── investment.html     Investment opportunities board
├── investment_detail.html  Full opportunity + express interest form
├── chat.html           AI Chatbot full page
├── profile.html        User profile + my reviews + my interests
├── dashboard.html      Role-based home (different for tourist/investor/admin)
├── admin/
│   ├── index.html      Admin dashboard — stats
│   ├── listings.html   Manage all listings — verify/delete
│   └── users.html      Manage users
├── css/
│   └── app.css         Custom utilities
└── js/
    ├── api.js          All API calls (centralized)
    ├── auth.js         Token management, auto-refresh
    ├── map.js          Google Maps + pins rendering
    └── chat.js         Chatbot widget logic
```

---

### 19.1 `js/api.js` — Centralized API Client
```javascript
// frontend/js/api.js

const API_BASE = '/api/v1';

const Api = {
    // ─── Auth ───
    async register(data) {
        return request('POST', '/auth/register', data);
    },
    async login(email, password) {
        return request('POST', '/auth/login', { email, password });
    },
    async me() {
        return request('GET', '/auth/me', null, true);
    },
    async logout() {
        Auth.clear();
        window.location.href = '/login.html';
    },

    // ─── Listings ───
    async getListings(params = {}) {
        return request('GET', '/listings?' + new URLSearchParams(params));
    },
    async getListing(id) {
        return request('GET', `/listings/${id}`);
    },
    async createListing(data) {
        return request('POST', '/listings', data, true);
    },
    async getFeaturedListings(area = null) {
        const q = area ? `?area=${area}&is_featured=true` : '?is_featured=true';
        return request('GET', `/listings${q}`);
    },

    // ─── Guide ───
    async getAttractions(params = {}) {
        return request('GET', '/guide/attractions?' + new URLSearchParams(params));
    },
    async getAttraction(id) {
        return request('GET', `/guide/attractions/${id}`);
    },
    async getAreas() {
        return request('GET', '/guide/areas');
    },
    async getMapPins() {
        return request('GET', '/guide/map-pins');
    },

    // ─── Investment ───
    async getInvestments(params = {}) {
        return request('GET', '/investment?' + new URLSearchParams(params));
    },
    async getInvestment(id) {
        return request('GET', `/investment/${id}`);
    },
    async expressInterest(id, message, contact) {
        return request('POST', `/investment/${id}/interest`, { message, ...contact }, true);
    },

    // ─── Search ───
    async search(q, type = 'all', area = null) {
        const p = { q, type };
        if (area) p.area = area;
        return request('GET', '/search?' + new URLSearchParams(p));
    },
    async autocomplete(q) {
        return request('GET', `/search/autocomplete?q=${encodeURIComponent(q)}`);
    },

    // ─── Chat ───
    async sendMessage(sessionId, message, areaFilter, userType) {
        return request('POST', '/chat/message', {
            session_id: sessionId,
            message,
            area_filter: areaFilter || null,
            user_type_context: userType || null
        }, false);   // auth optional
    },
    async getChatSuggestions(userType = 'tourist') {
        return request('GET', `/chat/suggestions?user_type=${userType}`);
    },

    // ─── Reviews ───
    async createReview(targetType, targetId, rating, body, title) {
        return request('POST', '/reviews', {
            target_type: targetType,
            target_id: targetId,
            rating, body, title
        }, true);
    },
    async getReviews(targetType, targetId) {
        return request('GET', `/listings/${targetId}/reviews`);
    },

    // ─── Files ───
    async uploadImages(files, category, refId) {
        const form = new FormData();
        files.forEach(f => form.append('files', f));
        if (refId) form.append('ref_id', refId);
        return requestForm(`/files/upload?category=${category}`, form);
    },

    // ─── Notifications ───
    async getNotifications() {
        return request('GET', '/notifications', null, true);
    },
    async getUnreadCount() {
        return request('GET', '/notifications/count', null, true);
    },
    async markAllRead() {
        return request('PATCH', '/notifications/read-all', null, true);
    },
};

// ─── HTTP helpers ───

async function request(method, path, body = null, requireAuth = false) {
    const headers = { 'Content-Type': 'application/json' };
    const token = Auth.getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    else if (requireAuth) {
        Auth.clear();
        window.location.href = '/login.html';
        return;
    }
    const res = await fetch(API_BASE + path, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined
    });
    if (res.status === 401) {
        const refreshed = await Auth.refresh();
        if (refreshed) return request(method, path, body, requireAuth);
        Auth.clear();
        window.location.href = '/login.html';
        return;
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(err.error || err.detail || 'Request failed');
    }
    return res.json();
}

async function requestForm(path, form) {
    const headers = {};
    const token = Auth.getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(API_BASE + path, { method: 'POST', headers, body: form });
    if (!res.ok) throw new Error('Upload failed');
    return res.json();
}
```

---

### 19.2 `js/auth.js` — Token Management
```javascript
// frontend/js/auth.js

const Auth = {
    getToken() {
        return localStorage.getItem('access_token');
    },
    getUser() {
        const raw = localStorage.getItem('user');
        return raw ? JSON.parse(raw) : null;
    },
    save(tokenResponse) {
        localStorage.setItem('access_token', tokenResponse.access_token);
        localStorage.setItem('refresh_token', tokenResponse.refresh_token);
        localStorage.setItem('user', JSON.stringify(tokenResponse.user));
        // Schedule proactive refresh 5 minutes before expiry
        const msUntilRefresh = (tokenResponse.expires_in - 300) * 1000;
        setTimeout(() => Auth.refresh(), msUntilRefresh);
    },
    async refresh() {
        const rt = localStorage.getItem('refresh_token');
        if (!rt) return false;
        try {
            const res = await fetch('/api/v1/auth/refresh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: rt })
            });
            if (!res.ok) return false;
            const data = await res.json();
            Auth.save(data);
            return true;
        } catch {
            return false;
        }
    },
    clear() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },
    isLoggedIn() {
        return !!this.getToken();
    },
    hasRole(role) {
        const user = this.getUser();
        return user && (user.role === role || user.role === 'admin');
    },
    requireLogin() {
        if (!this.isLoggedIn()) {
            window.location.href = '/login.html?next=' + encodeURIComponent(window.location.pathname);
        }
    },
    requireRole(role) {
        this.requireLogin();
        if (!this.hasRole(role)) {
            window.location.href = '/index.html';
        }
    }
};
```

---

### 19.3 `js/chat.js` — Chatbot UI Logic
```javascript
// frontend/js/chat.js

const Chat = {
    sessionId: null,
    areaFilter: null,
    userType: null,

    async init() {
        this.sessionId = sessionStorage.getItem('chat_session_id');
        const user = Auth.getUser();
        this.userType = user?.role || 'tourist';

        // Load starter suggestions
        const suggestions = await Api.getChatSuggestions(this.userType);
        this.renderSuggestions(suggestions);

        // Bind send button
        document.getElementById('send-btn').addEventListener('click', () => this.send());
        document.getElementById('message-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.send();
            }
        });
    },

    async send() {
        const input = document.getElementById('message-input');
        const message = input.value.trim();
        if (!message) return;

        input.value = '';
        this.appendMessage('user', message);
        this.showTyping();

        try {
            const res = await Api.sendMessage(
                this.sessionId, message, this.areaFilter, this.userType
            );
            this.sessionId = res.session_id;
            sessionStorage.setItem('chat_session_id', this.sessionId);
            this.hideTyping();
            this.appendMessage('assistant', res.reply, res.sources);
        } catch (err) {
            this.hideTyping();
            this.appendMessage('assistant', '⚠️ حدث خطأ. حاول مرة أخرى.', []);
        }
    },

    appendMessage(role, content, sources = []) {
        const container = document.getElementById('chat-messages');
        const div = document.createElement('div');
        div.className = role === 'user'
            ? 'flex justify-end mb-3'
            : 'flex justify-start mb-3';

        const bubble = document.createElement('div');
        bubble.className = role === 'user'
            ? 'bg-emerald-600 text-white rounded-2xl rounded-tr-sm px-4 py-2 max-w-xs text-sm'
            : 'bg-white border rounded-2xl rounded-tl-sm px-4 py-3 max-w-sm text-sm shadow-sm';

        bubble.innerHTML = `<p>${content.replace(/\n/g, '<br>')}</p>`;

        if (role === 'assistant' && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'mt-2 pt-2 border-t text-xs text-gray-500';
            sourcesDiv.innerHTML = '<span>المصادر: </span>' +
                sources.slice(0, 3).map(s =>
                    `<span class="bg-gray-100 px-2 py-0.5 rounded mr-1">${s.title}</span>`
                ).join('');
            bubble.appendChild(sourcesDiv);
        }

        div.appendChild(bubble);
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    },

    showTyping() {
        const el = document.getElementById('typing-indicator');
        if (el) el.classList.remove('hidden');
    },
    hideTyping() {
        const el = document.getElementById('typing-indicator');
        if (el) el.classList.add('hidden');
    },

    renderSuggestions(suggestions) {
        const container = document.getElementById('suggestions');
        if (!container) return;
        container.innerHTML = suggestions.map(s =>
            `<button onclick="Chat.useSuggestion('${s}')"
              class="text-xs bg-white border rounded-full px-3 py-1 hover:bg-emerald-50 transition">
              ${s}
             </button>`
        ).join('');
    },

    useSuggestion(text) {
        document.getElementById('message-input').value = text;
        this.send();
    }
};

document.addEventListener('DOMContentLoaded', () => Chat.init());
```

---

### 19.4 `index.html` — Landing Page Structure
```html
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>هنا وادينا — بوابتك إلى الوادي الجديد</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="//unpkg.com/alpinejs" defer></script>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
  <style>body { font-family: 'Cairo', sans-serif; }</style>
</head>
<body class="bg-gray-50">

  <!-- Navbar -->
  <nav class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
      <div class="flex items-center gap-2">
        <img src="/static/img/logo.png" class="h-9" alt="هنا وادينا">
        <span class="font-bold text-emerald-700 text-xl">هنا وادينا</span>
      </div>
      <div class="hidden md:flex items-center gap-6 text-sm">
        <a href="/explorer.html" class="hover:text-emerald-600">استكشف</a>
        <a href="/guide.html" class="hover:text-emerald-600">السياحة</a>
        <a href="/investment.html" class="hover:text-emerald-600">الاستثمار</a>
        <a href="/chat.html" class="hover:text-emerald-600">المساعد الذكي</a>
      </div>
      <div x-data="{ user: null }" x-init="user = JSON.parse(localStorage.getItem('user'))">
        <div x-show="!user" class="flex gap-3">
          <a href="/login.html" class="text-sm text-gray-600 hover:text-emerald-600">دخول</a>
          <a href="/register.html"
             class="text-sm bg-emerald-600 text-white px-4 py-1.5 rounded-full hover:bg-emerald-700">
             تسجيل
          </a>
        </div>
        <div x-show="user" class="flex items-center gap-3">
          <a href="/dashboard.html" class="text-sm text-gray-700">
            <span x-text="user?.name"></span>
          </a>
          <button onclick="Auth.logout()"
            class="text-xs text-red-500 hover:text-red-700">خروج</button>
        </div>
      </div>
    </div>
  </nav>

  <!-- Hero -->
  <section class="relative bg-gradient-to-l from-emerald-700 to-emerald-900 text-white py-24">
    <div class="max-w-4xl mx-auto text-center px-4">
      <h1 class="text-5xl font-bold mb-4">الوادي.. أقرب مما تخيّل</h1>
      <p class="text-xl text-emerald-100 mb-10">
        اكتشف الوادي الجديد بذكاء — سياحة، استثمار، خدمات، وكل ما تحتاجه في مكان واحد
      </p>
      <!-- Search Bar -->
      <div class="flex items-center bg-white rounded-full px-4 py-2 max-w-xl mx-auto shadow-lg">
        <input type="text" id="hero-search"
          placeholder="ابحث عن فندق، مطعم، فرصة استثمارية..."
          class="flex-1 outline-none text-gray-700 text-sm"
          oninput="handleHeroSearch(this.value)">
        <button onclick="doHeroSearch()"
          class="bg-emerald-600 text-white px-5 py-2 rounded-full text-sm hover:bg-emerald-700">
          بحث
        </button>
      </div>
    </div>
  </section>

  <!-- Areas Grid -->
  <section class="max-w-7xl mx-auto px-4 py-16">
    <h2 class="text-2xl font-bold text-center mb-10 text-gray-800">اكتشف المناطق</h2>
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <!-- Each card links to explorer.html?area=... -->
      <a href="/explorer.html?area=الخارجة"
         class="bg-white rounded-2xl p-5 text-center shadow-sm hover:shadow-md transition border border-gray-100">
        <div class="text-3xl mb-2">🏙️</div>
        <p class="font-semibold text-gray-700">الخارجة</p>
        <p class="text-xs text-gray-400">العاصمة</p>
      </a>
      <a href="/explorer.html?area=الداخلة"
         class="bg-white rounded-2xl p-5 text-center shadow-sm hover:shadow-md transition border border-gray-100">
        <div class="text-3xl mb-2">🌴</div>
        <p class="font-semibold text-gray-700">الداخلة</p>
        <p class="text-xs text-gray-400">واحة السحر</p>
      </a>
      <a href="/explorer.html?area=الفرافرة"
         class="bg-white rounded-2xl p-5 text-center shadow-sm hover:shadow-md transition border border-gray-100">
        <div class="text-3xl mb-2">🏜️</div>
        <p class="font-semibold text-gray-700">الفرافرة</p>
        <p class="text-xs text-gray-400">الصحراء البيضاء</p>
      </a>
      <a href="/explorer.html?area=باريس"
         class="bg-white rounded-2xl p-5 text-center shadow-sm hover:shadow-md transition border border-gray-100">
        <div class="text-3xl mb-2">⛩️</div>
        <p class="font-semibold text-gray-700">باريس</p>
        <p class="text-xs text-gray-400">الجنوب النائم</p>
      </a>
      <a href="/explorer.html?area=بلاط"
         class="bg-white rounded-2xl p-5 text-center shadow-sm hover:shadow-md transition border border-gray-100">
        <div class="text-3xl mb-2">🏺</div>
        <p class="font-semibold text-gray-700">بلاط</p>
        <p class="text-xs text-gray-400">التاريخ الحي</p>
      </a>
    </div>
  </section>

  <!-- Feature Cards -->
  <section class="bg-white py-16">
    <div class="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="text-center p-6">
        <div class="text-4xl mb-3">🗺️</div>
        <h3 class="font-semibold mb-2">اكتشف الأماكن</h3>
        <p class="text-sm text-gray-500">فنادق، مطاعم، صيدليات، خدمات — كل شيء على الخريطة</p>
      </div>
      <div class="text-center p-6">
        <div class="text-4xl mb-3">🏛️</div>
        <h3 class="font-semibold mb-2">دليل سياحي</h3>
        <p class="text-sm text-gray-500">أبرز المعالم التاريخية والطبيعية مع نصائح الزيارة</p>
      </div>
      <div class="text-center p-6">
        <div class="text-4xl mb-3">💼</div>
        <h3 class="font-semibold mb-2">فرص استثمارية</h3>
        <p class="text-sm text-gray-500">فرص موثقة في الزراعة والسياحة والصناعة</p>
      </div>
      <div class="text-center p-6">
        <div class="text-4xl mb-3">🤖</div>
        <h3 class="font-semibold mb-2">مساعد ذكي</h3>
        <p class="text-sm text-gray-500">اسأل عن أي شيء في الوادي وستحصل على إجابة دقيقة</p>
      </div>
    </div>
  </section>

  <!-- Floating Chat Button -->
  <a href="/chat.html"
     class="fixed bottom-6 left-6 bg-emerald-600 text-white w-14 h-14 rounded-full
            flex items-center justify-center shadow-lg hover:bg-emerald-700 transition z-50">
    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863
           0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418
           4.03-8 9-8s9 3.582 9 8z"/>
    </svg>
  </a>

  <script src="/static/js/auth.js"></script>
  <script src="/static/js/api.js"></script>
  <script>
    async function doHeroSearch() {
        const q = document.getElementById('hero-search').value.trim();
        if (q) window.location.href = `/explorer.html?q=${encodeURIComponent(q)}`;
    }
  </script>
</body>
</html>
```

---

## 20. Auth & Security — Complete Implementation

### 20.1 Security Core
```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: str, role: str) -> str:
    expire = datetime.utcnow() + timedelta(seconds=settings.access_token_expire)
    return jwt.encode(
        {"sub": user_id, "role": role, "exp": expire, "type": "access"},
        settings.secret_key, algorithm="HS256"
    )

def create_refresh_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(seconds=settings.refresh_token_expire)
    return jwt.encode(
        {"sub": user_id, "exp": expire, "type": "refresh"},
        settings.secret_key, algorithm="HS256"
    )

def decode_token(token: str) -> dict:
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    return payload
```

### 20.2 FastAPI Dependencies
```python
# app/dependencies.py
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.security import decode_token
from app.db.redis import CacheHelper
from app.core.exceptions import UnauthorizedError, ForbiddenError

bearer_scheme = HTTPBearer(auto_error=False)

def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.mongo["hena_wadeena"]

def get_cache(request: Request) -> CacheHelper:
    return CacheHelper(request.app.state.redis)

def get_qdrant(request: Request):
    return request.app.state.qdrant

async def get_current_user_optional(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict | None:
    if not creds:
        return None
    try:
        payload = decode_token(creds.credentials)
        if payload.get("type") != "access":
            return None
        return {"user_id": payload["sub"], "role": payload["role"]}
    except Exception:
        return None

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> dict:
    if not creds:
        raise UnauthorizedError("Authentication required")
    try:
        payload = decode_token(creds.credentials)
        if payload.get("type") != "access":
            raise UnauthorizedError("Invalid token type")
        return {"user_id": payload["sub"], "role": payload["role"]}
    except Exception:
        raise UnauthorizedError("Invalid or expired token")

async def require_admin(user=Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise ForbiddenError("Admin access required")
    return user
```

### 20.3 Rate Limiting Middleware
```python
# app/middleware/rate_limit.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple Redis-backed rate limiter per IP."""

    LIMITS = {
        "/api/v1/chat/message": (20, 60),    # 20 req/min
        "/api/v1/auth/login":   (10, 60),    # 10 req/min
        "/api/v1/auth/register":(5, 60),     # 5 req/min
        "default":              (100, 60),   # 100 req/min
    }

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        path = request.url.path
        limit, window = self.LIMITS.get(path, self.LIMITS["default"])

        cache = CacheHelper(request.app.state.redis)
        key = f"ratelimit:{ip}:{path}"
        count = await cache.increment_rate(key, window)

        if count > limit:
            return Response(
                content='{"error":"Too many requests"}',
                status_code=429,
                media_type="application/json"
            )
        return await call_next(request)
```

### 20.4 Exception Handlers
```python
# app/core/exceptions.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class NotFoundError(AppError):
    def __init__(self, msg="Not found"):
        super().__init__(msg, 404)

class UnauthorizedError(AppError):
    def __init__(self, msg="Unauthorized"):
        super().__init__(msg, 401)

class ForbiddenError(AppError):
    def __init__(self, msg="Forbidden"):
        super().__init__(msg, 403)

class ConflictError(AppError):
    def __init__(self, msg="Conflict"):
        super().__init__(msg, 409)

class ValidationError(AppError):
    def __init__(self, msg="Validation error"):
        super().__init__(msg, 422)

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message}
        )

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
```
# PART 6 — SEED DATA, TESTING, INFRA & ROADMAP

## 21. Complete Seed Data

### 21.1 `seed/data/tourist_guide.json` (25 entries excerpt)
```json
[
  {
    "name": "Kharga Oasis", "name_ar": "واحة الخارجة",
    "slug": "kharga-oasis",
    "type": "attraction", "area": "الخارجة",
    "description_ar": "واحة الخارجة هي عاصمة محافظة الوادي الجديد، وتقع على بُعد 600 كم جنوب القاهرة. تتميز بمناخ صحراوي ومياه جوفية وفيرة وتاريخ ممتد آلاف السنين.",
    "history_ar": "كانت الخارجة محطة رئيسية على طريق القوافل القديم عبر الصحراء الغربية. تحتوي على آثار فرعونية ورومانية نادرة.",
    "best_season": "winter", "best_time_of_day": "morning",
    "entry_fee": {"adults_egp": 0, "children_egp": 0},
    "opening_hours": "على مدار اليوم",
    "duration_hours": 3.0,
    "tips_ar": ["الزيارة في الشتاء أفضل بسبب الطقس المعتدل", "احمل ماء كافياً دائماً"],
    "coordinates": {"lat": 25.4397, "lng": 30.5490},
    "is_active": true, "is_featured": true
  },
  {
    "name": "Hibis Temple", "name_ar": "معبد هيبس",
    "slug": "hibis-temple",
    "type": "historical", "area": "الخارجة",
    "description_ar": "معبد هيبس هو أقدم وأكمل المعابد المصرية المحفوظة من العصر المتأخر. بُني في عهد الملك أحمس الثاني ويعود إلى القرن السادس قبل الميلاد.",
    "best_season": "winter",
    "entry_fee": {"adults_egp": 30, "children_egp": 15, "foreigners_usd": 5},
    "opening_hours": "8:00 صباحاً - 5:00 مساءً",
    "duration_hours": 1.5,
    "tips_ar": ["احضر معك مرشداً لفهم النقوش", "التصوير مسموح مقابل رسوم إضافية"],
    "coordinates": {"lat": 25.4550, "lng": 30.5390},
    "is_active": true, "is_featured": true
  },
  {
    "name": "White Desert", "name_ar": "الصحراء البيضاء",
    "slug": "white-desert",
    "type": "natural", "area": "الفرافرة",
    "description_ar": "الصحراء البيضاء محمية طبيعية مذهلة تتميز بتكوينات صخرية كلسية بيضاء تشبه الجليد. من أجمل مناطق العالم للتخييم الليلي تحت النجوم.",
    "best_season": "winter", "best_time_of_day": "evening",
    "entry_fee": {"adults_egp": 40, "children_egp": 20, "foreigners_usd": 8},
    "opening_hours": "على مدار اليوم",
    "duration_hours": 6.0,
    "difficulty": "easy",
    "tips_ar": [
      "التخييم الليلي تجربة لا تُنسى",
      "لا تترك أي قمامة في المحمية",
      "احضر ملابس دافئة للليل",
      "يُفضل الحجز مع وكالة سفر"
    ],
    "coordinates": {"lat": 27.1400, "lng": 28.0000},
    "is_active": true, "is_featured": true
  },
  {
    "name": "Dakhla Old Town", "name_ar": "قصر الداخلة",
    "slug": "dakhla-old-town",
    "type": "historical", "area": "الداخلة",
    "description_ar": "قصر الداخلة مدينة عمرها أكثر من ألف عام، بُنيت من الطوب اللبن. شوارعها الضيقة وأزقتها التاريخية تنقلك إلى عصور سابقة.",
    "best_season": "winter",
    "entry_fee": {"adults_egp": 20, "children_egp": 10},
    "opening_hours": "8:00 - 17:00",
    "duration_hours": 2.0,
    "tips_ar": ["الزيارة في الصباح الباكر تجنباً للحر", "يوجد مرشدون محليون بأسعار معقولة"],
    "coordinates": {"lat": 25.4870, "lng": 29.0040},
    "is_active": true, "is_featured": true
  },
  {
    "name": "Ain Amoun Spring", "name_ar": "عين أمون",
    "slug": "ain-amoun",
    "type": "natural", "area": "الداخلة",
    "description_ar": "عين أمون ينبوع طبيعي دافئ يصل ماؤه أحياناً لـ 43 درجة مئوية، يُحاط بنخيل وارف ومروج خضراء. مثالي للاسترخاء والاستجمام.",
    "best_season": "winter",
    "entry_fee": {"adults_egp": 10, "children_egp": 5},
    "opening_hours": "7:00 - 18:00",
    "duration_hours": 1.5,
    "tips_ar": ["الماء دافئ في الشتاء وبارد في الصيف نسبياً", "احضر ملابس السباحة"],
    "coordinates": {"lat": 25.5030, "lng": 28.9990},
    "is_active": true
  }
]
```

### 21.2 `seed/data/listings.json` (40 entries excerpt)
```json
[
  {
    "title": "Safari Hotel Kharga", "title_ar": "فندق السفاري الخارجة",
    "slug": "safari-hotel-kharga",
    "description_ar": "فندق السفاري من أشهر فنادق الخارجة يقدم غرف مريحة بإطلالات صحراوية. يوفر خدمات الاستقبال على مدار الساعة ووجبات إفطار مصرية أصيلة.",
    "category": "accommodation", "sub_category": "hotel",
    "location": {
      "area": "الخارجة",
      "address": "شارع جمال عبد الناصر، الخارجة",
      "address_ar": "شارع جمال عبد الناصر، الخارجة",
      "coordinates": {"lat": 25.4410, "lng": 30.5500}
    },
    "contact": {"phone": "0922301111", "whatsapp": "0922301111"},
    "price_range": "$$",
    "tags": ["فطور مجاني", "مواقف سيارات", "تكييف", "واي فاي"],
    "amenities": ["مطعم", "استقبال 24 ساعة", "غسيل ملابس"],
    "is_active": true, "is_verified": true, "is_featured": true,
    "rating_avg": 4.2, "review_count": 18
  },
  {
    "title": "Al-Dakhla Inn", "title_ar": "نزل الداخلة",
    "slug": "al-dakhla-inn",
    "description_ar": "نزل هادئ وبأسعار مناسبة في قلب الداخلة. يناسب الطلاب والسياح بميزانية محدودة.",
    "category": "accommodation", "sub_category": "hostel",
    "location": {
      "area": "الداخلة",
      "address": "ميدان المحطة، الداخلة",
      "address_ar": "ميدان المحطة، الداخلة",
      "coordinates": {"lat": 25.4900, "lng": 28.9820}
    },
    "contact": {"phone": "0922401234"},
    "price_range": "$",
    "tags": ["أسعار مناسبة", "مطبخ مشترك", "واي فاي"],
    "is_active": true, "is_verified": true,
    "rating_avg": 3.8, "review_count": 7
  },
  {
    "title": "Oasis Restaurant", "title_ar": "مطعم الواحة",
    "slug": "oasis-restaurant-kharga",
    "description_ar": "مطعم شعبي يقدم أشهى الأكلات المصرية والمحلية. مشهور بالأرز المعمر والكبدة البلدي.",
    "category": "restaurant", "sub_category": "restaurant",
    "location": {
      "area": "الخارجة",
      "address": "شارع 23 يوليو، الخارجة",
      "address_ar": "شارع 23 يوليو، الخارجة",
      "coordinates": {"lat": 25.4380, "lng": 30.5460}
    },
    "contact": {"phone": "0922302222", "whatsapp": "0922302222"},
    "price_range": "$",
    "tags": ["أكل مصري", "أسعار معقولة", "توصيل"],
    "is_active": true, "is_verified": true,
    "rating_avg": 4.5, "review_count": 32
  },
  {
    "title": "Al-Nile Pharmacy", "title_ar": "صيدلية النيل",
    "slug": "al-nile-pharmacy-kharga",
    "description_ar": "صيدلية متكاملة في مركز الخارجة، تعمل 12 ساعة يومياً. توفر معظم الأدوية الشائعة ومستلزمات العلاج.",
    "category": "healthcare", "sub_category": "pharmacy",
    "location": {
      "area": "الخارجة",
      "address": "شارع الجمهورية، بجوار المحكمة",
      "address_ar": "شارع الجمهورية، بجوار المحكمة",
      "coordinates": {"lat": 25.4360, "lng": 30.5480}
    },
    "contact": {"phone": "0922305555"},
    "tags": ["دواء", "صيدلية", "مستلزمات طبية"],
    "hours": {
      "saturday":  {"open": "08:00", "close": "22:00", "closed": false},
      "friday":    {"open": "14:00", "close": "22:00", "closed": false}
    },
    "is_active": true, "is_verified": true,
    "rating_avg": 4.0, "review_count": 5
  }
]
```

### 21.3 `seed/data/investments.json`
```json
[
  {
    "title": "Olive Grove Investment", "title_ar": "مشروع زراعة الزيتون",
    "slug": "olive-grove-dakhla",
    "description_ar": "فرصة استثمارية في مجال زراعة الزيتون بالداخلة على مساحة 50 فدان. التربة مناسبة جداً والمياه الجوفية متوفرة. يُتوقع العائد بعد 5 سنوات.",
    "sector": "agriculture", "area": "الداخلة",
    "land_area_sqm": 210000,
    "investment_range": {"min_egp": 500000, "max_egp": 2000000},
    "expected_return_pct": 18.5,
    "payback_period_years": 6,
    "incentives_ar": ["إعفاء ضريبي 10 سنوات", "دعم مياه زراعية", "أرض بسعر رمزي"],
    "infrastructure": {"water": true, "electricity": true, "road_access": true, "telecom": false},
    "contact": {"entity": "مديرية الزراعة — الوادي الجديد", "phone": "0922399001"},
    "status": "available", "source": "محافظة",
    "is_verified": true, "is_featured": true, "interest_count": 4
  },
  {
    "title": "Desert Tourism Camp", "title_ar": "مخيم سياحي صحراوي",
    "slug": "desert-camp-farafra",
    "description_ar": "إنشاء مخيم سياحي متكامل بالقرب من الصحراء البيضاء في الفرافرة. تزايد الطلب السياحي على التجارب الصحراوية يجعل هذا المشروع واعداً.",
    "sector": "tourism", "area": "الفرافرة",
    "land_area_sqm": 50000,
    "investment_range": {"min_egp": 1500000, "max_egp": 5000000},
    "expected_return_pct": 22.0,
    "payback_period_years": 4,
    "incentives_ar": ["ترخيص سريع", "دعم ترويجي من وزارة السياحة", "إعفاء ضريبي 5 سنوات"],
    "infrastructure": {"water": false, "electricity": false, "road_access": true, "telecom": false},
    "contact": {"entity": "هيئة تنشيط السياحة", "phone": "0922399002"},
    "status": "available", "source": "GAFI",
    "is_verified": true, "is_featured": true, "interest_count": 9
  },
  {
    "title": "Date Packing Factory", "title_ar": "مصنع تعبئة وتغليف التمور",
    "slug": "date-factory-kharga",
    "description_ar": "مشروع مصنع لتعبئة وتصدير التمور من الخارجة. الوادي الجديد ينتج كميات كبيرة من التمور لكن تنقصه مرافق التصنيع المحلية.",
    "sector": "industry", "area": "الخارجة",
    "land_area_sqm": 5000,
    "investment_range": {"min_egp": 2000000, "max_egp": 8000000},
    "expected_return_pct": 25.0,
    "payback_period_years": 3,
    "incentives_ar": ["أرض صناعية مدعومة", "إعفاء جمركي على الآلات", "دعم التصدير"],
    "infrastructure": {"water": true, "electricity": true, "road_access": true, "telecom": true},
    "contact": {"entity": "الهيئة العامة للاستثمار — فرع الوادي الجديد", "phone": "0922399003"},
    "status": "available", "source": "GAFI",
    "is_verified": true, "is_featured": false, "interest_count": 6
  }
]
```

### 21.4 `seed/seed_mongo.py` — Full Script
```python
# seed/seed_mongo.py
"""
Usage: python seed/seed_mongo.py
Drops and re-seeds all collections with demo data.
"""
import asyncio, json, os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "hena_wadeena"

async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    print("⚠️  Dropping existing data...")
    await db["tourist_guide"].drop()
    await db["listings"].drop()
    await db["investment_opportunities"].drop()
    await db["kb_documents"].drop()

    print("📦 Seeding tourist_guide...")
    with open("seed/data/tourist_guide.json", encoding="utf-8") as f:
        guides = json.load(f)
    for g in guides:
        g["created_at"] = datetime.utcnow()
        g["updated_at"] = datetime.utcnow()
        g.setdefault("review_count", 0)
        g.setdefault("rating_avg", 0.0)
        g.setdefault("view_count", 0)
        g.setdefault("images", [])
        g.setdefault("thumbnail", None)
    await db["tourist_guide"].insert_many(guides)
    print(f"  ✅ {len(guides)} attractions inserted")

    print("📦 Seeding listings...")
    with open("seed/data/listings.json", encoding="utf-8") as f:
        listings = json.load(f)
    for l in listings:
        l["created_at"] = datetime.utcnow()
        l["updated_at"] = datetime.utcnow()
        l.setdefault("view_count", 0)
        l.setdefault("images", [])
        l.setdefault("thumbnail", None)
        l.setdefault("is_active", True)
        l.setdefault("created_by", ObjectId())  # placeholder admin
    await db["listings"].insert_many(listings)
    print(f"  ✅ {len(listings)} listings inserted")

    print("📦 Seeding investments...")
    with open("seed/data/investments.json", encoding="utf-8") as f:
        investments = json.load(f)
    for i in investments:
        i["created_at"] = datetime.utcnow()
        i["updated_at"] = datetime.utcnow()
    await db["investment_opportunities"].insert_many(investments)
    print(f"  ✅ {len(investments)} opportunities inserted")

    # Create indexes
    print("🗂️  Creating indexes...")
    from app.db.mongo import create_indexes
    await create_indexes(db)

    print("\n✅ Seed complete!")
    client.close()

asyncio.run(main())
```

### 21.5 `seed/seed_admin.py`
```python
# seed/seed_admin.py
import asyncio, os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.security import hash_password

async def main():
    client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
    db = client["hena_wadeena"]
    email = "admin@henawadeena.com"
    existing = await db["users"].find_one({"email": email})
    if existing:
        print(f"Admin already exists: {email}")
        return
    await db["users"].insert_one({
        "name": "Admin",
        "name_ar": "المدير",
        "email": email,
        "hashed_password": hash_password("Admin@2026!"),
        "role": "admin",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    print(f"✅ Admin created: {email} / Admin@2026!")
    client.close()

asyncio.run(main())
```

---

## 22. Testing Strategy

### 22.1 `tests/conftest.py`
```python
import pytest, pytest_asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient
from unittest.mock import AsyncMock, MagicMock
from app.main import create_app

@pytest_asyncio.fixture(scope="session")
async def app():
    application = create_app()
    # Inject mocked services
    application.state.mongo = AsyncIOMotorClient("mongodb://localhost:27017")
    application.state.redis = AsyncMock()
    application.state.qdrant = AsyncMock()
    yield application

@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as c:
        yield c

@pytest_asyncio.fixture
async def admin_headers(client):
    # Register + login as admin
    await client.post("/api/v1/auth/register", json={
        "name": "Test Admin", "email": "testadmin@test.com",
        "password": "Admin1234!", "role": "admin"
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "testadmin@test.com", "password": "Admin1234!"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def user_headers(client):
    await client.post("/api/v1/auth/register", json={
        "name": "Test User", "email": "testuser@test.com",
        "password": "User1234!", "role": "tourist"
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "testuser@test.com", "password": "User1234!"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### 22.2 Test Cases
```python
# tests/integration/test_auth.py
class TestAuth:
    async def test_register_success(self, client): ...
    async def test_register_duplicate_email(self, client): ...
    async def test_login_success(self, client): ...
    async def test_login_wrong_password(self, client): ...
    async def test_get_me_authenticated(self, client, user_headers): ...
    async def test_get_me_unauthenticated(self, client): ...
    async def test_token_refresh(self, client, user_headers): ...
    async def test_short_password_rejected(self, client): ...

# tests/integration/test_listings.py
class TestListings:
    async def test_get_listings(self, client): ...
    async def test_get_listings_filter_by_area(self, client): ...
    async def test_get_listings_filter_by_category(self, client): ...
    async def test_get_listing_by_id(self, client): ...
    async def test_create_listing_authenticated(self, client, user_headers): ...
    async def test_create_listing_unauthenticated(self, client): ...
    async def test_update_own_listing(self, client, user_headers): ...
    async def test_update_others_listing_forbidden(self, client, user_headers): ...
    async def test_delete_own_listing(self, client, user_headers): ...
    async def test_cache_hit_on_second_request(self, client): ...

# tests/integration/test_chat.py
class TestChat:
    async def test_chat_returns_reply(self, client): ...
    async def test_chat_creates_session(self, client): ...
    async def test_chat_continues_session(self, client): ...
    async def test_get_suggestions(self, client): ...
    async def test_chat_with_area_filter(self, client): ...

# tests/unit/test_chunker.py
class TestChunker:
    def test_chunk_long_text(self): ...
    def test_chunk_short_text_no_split(self): ...
    def test_chunk_respects_max_tokens(self): ...
    def test_chunk_overlap(self): ...
    def test_metadata_header_prepended(self): ...
```

---

## 23. Configuration (`app/config.py`)

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    app_name: str = "Hena Wadeena"
    app_env: str = "development"
    debug: bool = True
    base_url: str = "http://localhost:8000"

    # MongoDB
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "hena_wadeena"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"

    # JWT
    secret_key: str = "change-me-in-production-please!"
    access_token_expire: int = 3600          # 1 hour
    refresh_token_expire: int = 604800       # 7 days

    # Embeddings
    embedding_provider: str = "openai"       # "openai" or "local"
    openai_api_key: str = ""
    vector_dim: int = 1536                   # 384 for local model

    # File Storage
    upload_dir: str = "./uploads"
    max_upload_mb: int = 5

    # Maps
    google_maps_api_key: str = ""

    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://hena-wadeena.lovable.app"
    ]

    # Rate Limits
    rate_limit_per_minute: int = 100

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 24. Docker & Infrastructure

### 24.1 `docker-compose.yml`
```yaml
version: "3.9"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: hena_api
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      - MONGO_URL=mongodb://mongo:27017
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      mongo:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_started
    volumes:
      - ./uploads:/app/uploads
      - .:/app                         # hot reload in dev
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  mongo:
    image: mongo:7
    container_name: hena_mongo
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: hena_redis
    ports:
      - "6379:6379"
    command: redis-server --save "" --appendonly no --loglevel warning
    healthcheck:
      test: redis-cli ping
      interval: 5s
      timeout: 3s
      retries: 5

  qdrant:
    image: qdrant/qdrant:v1.9.0
    container_name: hena_qdrant
    ports:
      - "6333:6333"
      - "6334:6334"          # gRPC (optional)
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__STORAGE__STORAGE_PATH=/qdrant/storage

  nginx:
    image: nginx:alpine
    container_name: hena_nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend:/var/www/frontend:ro
    depends_on:
      - api

volumes:
  mongo_data:
  qdrant_data:
```

### 24.2 `nginx/nginx.conf`
```nginx
events { worker_connections 1024; }

http {
    include mime.types;
    server_tokens off;

    upstream api_backend {
        server api:8000;
    }

    server {
        listen 80;
        server_name localhost;

        # Gzip
        gzip on;
        gzip_types text/html text/css application/javascript application/json;

        # Static frontend files
        root /var/www/frontend;
        index index.html;

        # Frontend routes (SPA-style fallback)
        location / {
            try_files $uri $uri.html $uri/ =404;
        }

        # API proxy
        location /api/ {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # FastAPI docs
        location /docs {
            proxy_pass http://api_backend/docs;
        }
        location /redoc {
            proxy_pass http://api_backend/redoc;
        }

        # Uploaded files
        location /uploads/ {
            alias /app/uploads/;
            add_header Cache-Control "public, max-age=86400";
        }
    }
}
```

### 24.3 `Dockerfile`
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 25. `requirements.txt`

```
# Core
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.9

# Database
motor==3.5.0
pymongo==4.8.0

# Redis
redis[asyncio]==5.0.0

# Qdrant
qdrant-client==1.10.0

# Auth
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Config
pydantic==2.8.0
pydantic-settings==2.4.0
python-dotenv==1.0.1

# LLM & Embeddings (OpenAI path)
openai==1.45.0

# Local embeddings (optional, comment out if using OpenAI only)
# sentence-transformers==3.1.0

# Background tasks
apscheduler==3.10.4

# File handling
aiofiles==24.1.0
Pillow==10.4.0

# HTTP client
httpx==0.27.0

# Testing
pytest==8.3.0
pytest-asyncio==0.23.0
pytest-cov==5.0.0

# Code quality
black==24.8.0
isort==5.13.0
```

---

## 26. `.env.example`

```ini
# ─── App ───
APP_ENV=development
DEBUG=true
BASE_URL=http://localhost:8000

# ─── MongoDB ───
MONGO_URL=mongodb://localhost:27017
MONGO_DB=hena_wadeena

# ─── Redis ───
REDIS_URL=redis://localhost:6379/0

# ─── Qdrant ───
QDRANT_URL=http://localhost:6333

# ─── JWT ───
SECRET_KEY=change-this-to-a-64-char-random-string-before-deploying
ACCESS_TOKEN_EXPIRE=3600
REFRESH_TOKEN_EXPIRE=604800

# ─── LLM / Embeddings ───
# Option A: OpenAI (recommended for Arabic quality)
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Option B: Free local model (set VECTOR_DIM=384, no API key needed)
# EMBEDDING_PROVIDER=local
# VECTOR_DIM=384

# ─── Maps ───
GOOGLE_MAPS_API_KEY=AIza...

# ─── Files ───
UPLOAD_DIR=./uploads
MAX_UPLOAD_MB=5

# ─── CORS ───
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

---

## 27. Implementation Roadmap

### Sprint 0 — Environment (Day 1)
- [ ] Create repo + folder structure exactly as specified
- [ ] `docker compose up -d` → all 4 services healthy
- [ ] `GET /health` returns `{"mongo":"ok","redis":"ok","qdrant":"ok"}`
- [ ] `.env` configured
- [ ] Index creation runs on startup

**Exit criteria:** `curl http://localhost:8000/health` is green.

---

### Sprint 1 — Auth + Users (Days 2-3)
- [ ] `users` collection + indexes
- [ ] `POST /auth/register` with bcrypt
- [ ] `POST /auth/login` → JWT pair
- [ ] `POST /auth/refresh` → new access token
- [ ] `POST /auth/logout` → invalidate in Redis
- [ ] `GET /auth/me`
- [ ] `PATCH /auth/me` — update profile
- [ ] `POST /auth/change-password`
- [ ] All auth tests pass

**Exit criteria:** Full login lifecycle works. Expired token returns 401.

---

### Sprint 2 — Listings (Days 3-5)
- [ ] `listings` collection + all indexes including text index
- [ ] All 12 listing endpoints implemented
- [ ] Redis caching on list + detail
- [ ] Cache invalidation on write/delete
- [ ] File upload for listing images
- [ ] Slug generation
- [ ] Admin verify endpoint
- [ ] All listing tests pass

**Exit criteria:** Create, read, update, delete, filter, cache all working.

---

### Sprint 3 — Tourist Guide + Investment (Days 5-7)
- [ ] `tourist_guide` collection + indexes
- [ ] All guide endpoints
- [ ] Map pins endpoint (returns coordinates list)
- [ ] `investment_opportunities` collection + indexes
- [ ] All investment endpoints
- [ ] Express interest endpoint + notification trigger
- [ ] `investment_interests` collection
- [ ] Seed data loaded (25 guide + 15 investments)

**Exit criteria:** Browsing all areas, full guide detail, investment board functional.

---

### Sprint 4 — Reviews + Notifications (Days 7-8)
- [ ] `reviews` collection + unique constraint
- [ ] Create / update / delete review
- [ ] Rating recalculation on parent entity
- [ ] `notifications` collection
- [ ] `NotificationService` — send on interest expressed
- [ ] Unread count endpoint
- [ ] Mark all read

**Exit criteria:** Review a listing → parent rating updates. Express interest → notification created.

---

### Sprint 5 — Search (Day 8-9)
- [ ] MongoDB text search on all 3 collections
- [ ] Cross-collection unified results
- [ ] Redis cache for search results
- [ ] Semantic search via Qdrant (requires Sprint 6 to run first)
- [ ] Autocomplete endpoint

**Exit criteria:** Search "فندق" returns listings. Search "زراعة" returns investments.

---

### Sprint 6 — RAG Pipeline + Chat (Days 9-11)
- [ ] Qdrant collection initialized on startup
- [ ] `DocumentChunker` — splits and prepends metadata headers
- [ ] `IngestionPipeline` — processes all collections
- [ ] `seed/seed_qdrant.py` run successfully
- [ ] `embed_text()` function working (OpenAI or local)
- [ ] `ChatService` — full RAG with retrieval + prompt + generation
- [ ] All chat endpoints
- [ ] Session persistence in MongoDB
- [ ] Sources attached to responses
- [ ] Chat suggestions endpoint

**Exit criteria:** Ask "ما أفضل مطعم في الخارجة؟" → coherent Arabic reply citing "مطعم الواحة" from seed data.

---

### Sprint 7 — Frontend (Days 11-14)
- [ ] `index.html` — landing page with search + areas grid
- [ ] `login.html` + `register.html`
- [ ] `explorer.html` — listings browser with filters + map integration
- [ ] `listing_detail.html` — full detail + reviews + contact
- [ ] `guide.html` + `guide_detail.html`
- [ ] `investment.html` + `investment_detail.html` + interest form
- [ ] `chat.html` — full chatbot UI
- [ ] `profile.html`
- [ ] `dashboard.html` — role-based home
- [ ] `admin/index.html` — basic stats
- [ ] `js/api.js` + `js/auth.js` + `js/chat.js` + `js/map.js`
- [ ] Nginx serving frontend + proxying API

**Exit criteria:** End-to-end flow: visit site → register → browse listings → chat with AI → express investment interest.

---

### Sprint 8 — Polish & Demo Prep (Day 14-15)
- [ ] Load full seed data (40 listings, 25 guide, 15 investments)
- [ ] Run `seed_qdrant.py` to embed everything
- [ ] Error handling on all routes
- [ ] Input validation edge cases
- [ ] Rate limiting active
- [ ] Admin panel shows stats
- [ ] `README.md` with quickstart
- [ ] Demo walkthrough script prepared

**Exit criteria:** Live demo of complete flow without errors.

---

## 28. Known Gaps (Post-MVP)

| Feature | Gap | When to Add |
|---------|-----|-------------|
| Email notifications | SMTP not configured | After MVP, add SendGrid |
| Mobile app | No React Native | Phase 2 |
| Payments | No Stripe | When subscription model confirmed |
| Real-time carpooling | Carpooling routes stubbed | Phase 2 |
| WebSocket chat | Polling only (request/response) | Phase 2 |
| Advanced monitoring | No Grafana/Prometheus | After first users |
| Multi-tenant admin | Single admin role | Phase 2 |
| PWA support | No service worker | Phase 2 |
| Social features | No user feed | Phase 3 |
| Analytics dashboard | No usage graphs | Phase 2 |
| Production HTTPS | Self-signed only | Before public launch |

---

## 29. Quick Start — 4 Commands

```bash
# 1. Setup
git clone <repo> && cd hena_wadeena
cp .env.example .env
# Edit .env: set OPENAI_API_KEY (or switch to local)

# 2. Start all services
docker compose up -d

# 3. Install Python deps and seed
pip install -r requirements.txt
python seed/seed_mongo.py
python seed/seed_admin.py
python seed/seed_qdrant.py   # takes 2-5 min depending on embedding provider

# 4. Start API
uvicorn app.main:app --reload

# Open:
# API Docs:  http://localhost:8000/docs
# Frontend:  http://localhost:80      (via nginx)
# Qdrant UI: http://localhost:6333/dashboard
```

---

## 30. Security Checklist

- [ ] `SECRET_KEY` is 64+ random chars in production
- [ ] Passwords hashed with bcrypt (never stored plain)
- [ ] JWT access token short-lived (1hr)
- [ ] Refresh token stored in Redis (revocable)
- [ ] Rate limiting on auth and chat endpoints
- [ ] File upload validates MIME type and max size
- [ ] MongoDB queries use parameterized values (no injection)
- [ ] CORS whitelist only known origins
- [ ] Admin endpoints protected by role check
- [ ] Soft deletes (no hard data loss)
- [ ] Error messages don't leak internal state
- [ ] `DEBUG=false` in production

---

*Prepared for Team Dev-X | Hena Wadeena Project | 2026-02-06*
*Full blueprint: 30 sections, zero-to-hero MVP delivery in 15 days.*
