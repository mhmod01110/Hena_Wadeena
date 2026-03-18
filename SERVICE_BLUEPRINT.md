# هنا وادينا — Hena Wadeena
## Full Service-Level Engineering Blueprint
> Controllers · Core · Interfaces · Repositories · Schemas · Services · ERDs · Business Logic · RBAC · Endpoints

**Stack:** Python 3.12 · FastAPI · PostgreSQL 16 · MongoDB 7 · Redis 7 · Meilisearch · Qdrant  
**Architecture:** Microservices · API Gateway (Kong) · RabbitMQ Event Bus · Celery Workers  
**Team:** Dev-X | Version: 1.0 | Date: 2026-02-06

---

## Table of Contents

1. [Global Conventions](#1-global-conventions)
2. [Roles & Permissions Matrix](#2-roles--permissions-matrix)
3. [Service 01 — auth-service](#3-service-01--auth-service)
4. [Service 02 — user-service](#4-service-02--user-service)
5. [Service 03 — map-service](#5-service-03--map-service)
6. [Service 04 — market-service](#6-service-04--market-service)
7. [Service 05 — guide-service](#7-service-05--guide-service)
8. [Service 06 — investment-service](#8-service-06--investment-service)
9. [Service 07 — payment-service](#9-service-07--payment-service)
10. [Service 08 — notification-service](#10-service-08--notification-service)
11. [Service 09 — search-service](#11-service-09--search-service)
12. [Service 10 — ai-service](#12-service-10--ai-service)
13. [Service 11 — media-service](#13-service-11--media-service)
14. [Service 12 — analytics-service](#14-service-12--analytics-service)
15. [Service 13 — admin-service](#15-service-13--admin-service)
16. [Inter-Service Event Catalog](#16-inter-service-event-catalog)

---

## 1. Global Conventions

### 1.1 Universal Folder Structure (per service)
```
{service-name}/
├── app/
│   ├── main.py                   # FastAPI factory + lifespan hooks
│   ├── config.py                 # pydantic-settings env config
│   ├── dependencies.py           # Shared Depends() callables
│   │
│   ├── api/                      # CONTROLLERS — thin HTTP layer only
│   │   └── v1/
│   │       ├── router.py         # Master sub-router
│   │       └── {resource}.py     # Route handlers (call service, return schema)
│   │
│   ├── core/                     # CORE — cross-cutting concerns
│   │   ├── security.py           # JWT encode/decode, password hashing
│   │   ├── exceptions.py         # Custom HTTP exceptions + handlers
│   │   ├── middleware.py         # Logging, CORS, rate-limit middleware
│   │   ├── events.py             # RabbitMQ publisher helpers
│   │   └── pagination.py         # Cursor / offset pagination helpers
│   │
│   ├── interfaces/               # INTERFACES — abstract base classes
│   │   ├── base_repository.py    # Generic CRUD interface (ABC)
│   │   └── base_service.py       # Generic service interface (ABC)
│   │
│   ├── repositories/             # REPOSITORIES — data-access objects
│   │   └── {entity}_repo.py      # Implements base_repository for entity
│   │
│   ├── schemas/                  # SCHEMAS — Pydantic v2 models
│   │   ├── requests/             # Inbound request bodies
│   │   ├── responses/            # Outbound response models
│   │   └── internal/             # DB documents / internal DTOs
│   │
│   ├── services/                 # SERVICES — business logic
│   │   └── {domain}_service.py   # Orchestrates repo + external calls
│   │
│   └── db/                       # DB clients (Postgres, Mongo, Redis)
│       ├── postgres.py
│       ├── mongo.py
│       └── redis.py
│
├── tests/
├── Dockerfile
├── requirements.txt
└── .env.example
```

### 1.2 Standard Response Envelope
```python
# All responses wrap data in:
{
  "success": true,
  "data": { ... },
  "meta": { "page": 1, "total": 100 },   # pagination only
  "error": null
}
```

### 1.3 Error Codes
| HTTP | Code | Meaning |
|------|------|---------|
| 400 | VALIDATION_ERROR | Bad request body |
| 401 | UNAUTHENTICATED | Missing / expired token |
| 403 | FORBIDDEN | Role not permitted |
| 404 | NOT_FOUND | Resource absent |
| 409 | CONFLICT | Duplicate key / state conflict |
| 422 | UNPROCESSABLE | Schema mismatch |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Unexpected server error |

### 1.4 JWT Payload (injected by Kong)
```json
{
  "sub": "user_uuid",
  "role": "tourist | student | investor | local_citizen | guide | merchant | admin | super_admin",
  "email": "user@email.com",
  "iat": 1234567890,
  "exp": 1234571490
}
```

---

## 2. Roles & Permissions Matrix

| Action | tourist | student | investor | local_citizen | guide | merchant | admin | super_admin |
|--------|:-------:|:-------:|:--------:|:-------------:|:-----:|:--------:|:-----:|:-----------:|
| Register / Login | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| View public listings | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Create listing | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| Create guide profile | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ |
| Book a guide | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ |
| Submit review | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| Browse investments | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ |
| Post investment opp. | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| Carpooling (post) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| Access payments | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| View analytics | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| Moderate content | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| Manage all users | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| System config | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |

---

## 3. Service 01 — auth-service

### 3.1 Responsibility
Handles all identity concerns: registration, login, JWT issuance, token refresh, OTP, OAuth2 (Google), password reset, and logout (token revocation in Redis).

### 3.2 Folder Structure
```
auth-service/app/
├── api/v1/
│   ├── auth.py             # /auth/* routes
│   └── otp.py              # /auth/otp/* routes
│
├── core/
│   ├── security.py         # JWT encode/decode, bcrypt hash/verify
│   ├── otp.py              # TOTP / SMS OTP generation
│   └── oauth.py            # Google OAuth2 token exchange
│
├── interfaces/
│   └── base_repository.py
│
├── repositories/
│   ├── user_repo.py        # Reads users table (read-only here)
│   ├── token_repo.py       # Redis: refresh token store + blocklist
│   └── otp_repo.py         # Redis: OTP codes with TTL
│
├── schemas/
│   ├── requests/
│   │   ├── register.py     # RegisterRequest
│   │   ├── login.py        # LoginRequest
│   │   ├── refresh.py      # RefreshRequest
│   │   ├── otp.py          # OTPRequest, OTPVerifyRequest
│   │   └── password.py     # ChangePasswordRequest, ResetPasswordRequest
│   └── responses/
│       ├── token.py        # TokenResponse (access + refresh)
│       └── auth_user.py    # AuthUserResponse (me)
│
└── services/
    └── auth_service.py     # All auth business logic
```

### 3.3 ERD (auth-service owns)
```
┌──────────────────────────────────────────────────────────────┐
│                        POSTGRESQL                            │
│                                                              │
│  ┌──────────────────────┐       ┌──────────────────────────┐ │
│  │       users          │       │      oauth_accounts      │ │
│  ├──────────────────────┤  1──* ├──────────────────────────┤ │
│  │ id          UUID PK  │──────▶│ id          UUID PK      │ │
│  │ email       VARCHAR  │       │ user_id     UUID FK      │ │
│  │ phone       VARCHAR  │       │ provider    VARCHAR       │ │
│  │ password_hash VARCHAR│       │ provider_uid VARCHAR      │ │
│  │ role        ENUM     │       │ access_token TEXT         │ │
│  │ is_active   BOOL     │       │ created_at  TIMESTAMPTZ   │ │
│  │ is_verified BOOL     │       └──────────────────────────┘ │
│  │ created_at  TIMESTAMPTZ│                                   │
│  │ updated_at  TIMESTAMPTZ│     ┌──────────────────────────┐ │
│  └──────────────────────┘       │  password_reset_tokens   │ │
│            │  1                 ├──────────────────────────┤ │
│            │                   │ id          UUID PK      │ │
│            │ *                 │ user_id     UUID FK      │ │
│            ▼                   │ token_hash  VARCHAR       │ │
│  ┌──────────────────────┐      │ expires_at  TIMESTAMPTZ   │ │
│  │      user_roles      │      │ used        BOOL          │ │
│  ├──────────────────────┤      └──────────────────────────┘ │
│  │ id          UUID PK  │                                    │
│  │ user_id     UUID FK  │                                    │
│  │ role        VARCHAR  │                                    │
│  │ assigned_by UUID FK  │                                    │
│  │ assigned_at TIMESTAMPTZ│                                  │
│  └──────────────────────┘                                    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                          REDIS                               │
│                                                              │
│  auth:refresh:{user_id}  →  {refresh_token}  TTL: 7d        │
│  auth:blocklist:{jti}    →  "1"              TTL: access exp │
│  auth:otp:{phone}        →  {code}           TTL: 5min       │
│  auth:reset:{token_hash} →  {user_id}        TTL: 1hr        │
└──────────────────────────────────────────────────────────────┘
```

### 3.4 Schemas

```python
# schemas/requests/register.py
class RegisterRequest(BaseModel):
    email: EmailStr
    phone: str = Field(pattern=r"^01[0-9]{9}$")
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=100)
    role: Literal["tourist","student","investor","local_citizen","guide","merchant"]
    preferred_language: Literal["ar","en"] = "ar"

# schemas/requests/login.py
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# schemas/responses/token.py
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int          # seconds

# schemas/responses/auth_user.py
class AuthUserResponse(BaseModel):
    id: UUID
    email: str
    phone: str
    full_name: str
    role: str
    is_verified: bool
    avatar_url: str | None
```

### 3.5 Repository Layer

```python
# repositories/token_repo.py
class TokenRepository:
    async def store_refresh(self, user_id: str, token: str, ttl: int) -> None
    async def get_refresh(self, user_id: str) -> str | None
    async def revoke_refresh(self, user_id: str) -> None
    async def blocklist_access(self, jti: str, ttl: int) -> None
    async def is_blocklisted(self, jti: str) -> bool

# repositories/otp_repo.py
class OTPRepository:
    async def store_otp(self, phone: str, code: str, ttl: int = 300) -> None
    async def get_otp(self, phone: str) -> str | None
    async def delete_otp(self, phone: str) -> None
```

### 3.6 Service Layer — Business Logic

```python
# services/auth_service.py
class AuthService:

    async def register(self, data: RegisterRequest) -> AuthUserResponse:
        """
        1. Validate email uniqueness → raise CONFLICT if exists
        2. Validate phone uniqueness
        3. Hash password with bcrypt (rounds=12)
        4. Create user record in PostgreSQL
        5. Emit: user.created → RabbitMQ
        6. Send OTP to phone for verification
        7. Return user profile (NOT token — verify first)
        """

    async def login(self, data: LoginRequest) -> TokenResponse:
        """
        1. Fetch user by email → raise NOT_FOUND / UNAUTHENTICATED
        2. Verify password hash → raise UNAUTHENTICATED if wrong
        3. Check is_active=True → raise 403 if suspended
        4. Generate access JWT (1hr) + refresh token (7d)
        5. Store refresh token in Redis
        6. Return TokenResponse
        """

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """
        1. Validate JWT signature on refresh token
        2. Check token exists in Redis (not revoked)
        3. Rotate: revoke old, issue new pair
        4. Return new TokenResponse
        """

    async def logout(self, access_token_jti: str, user_id: str) -> None:
        """
        1. Add jti to blocklist in Redis (TTL = remaining access token lifetime)
        2. Delete refresh token from Redis
        """

    async def verify_otp(self, phone: str, code: str) -> bool:
        """
        1. Retrieve OTP from Redis
        2. Compare → delete on success, raise 400 on failure
        3. Set user.is_verified = True in PostgreSQL
        """

    async def request_password_reset(self, email: str) -> None:
        """
        1. Check email exists → silent success even if not (prevents enumeration)
        2. Generate secure random token, hash it
        3. Store hash in password_reset_tokens table (TTL 1hr)
        4. Send reset link via notification-service
        """

    async def reset_password(self, token: str, new_password: str) -> None:
        """
        1. Hash incoming token, look up in DB
        2. Check not used + not expired → raise 400 if so
        3. Validate new password strength
        4. Update password_hash, mark token used
        5. Revoke all active refresh tokens for user
        """

    async def google_oauth(self, google_token: str) -> TokenResponse:
        """
        1. Exchange google_token with Google APIs
        2. Extract email, google_uid
        3. Upsert oauth_accounts record
        4. Create or fetch user
        5. Return standard TokenResponse
        """
```

### 3.7 Controller (Router Signatures)

```python
# api/v1/auth.py
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ── Public endpoints ────────────────────────────────────────────
@router.post("/register",        response_model=AuthUserResponse,  status_code=201)
async def register(body: RegisterRequest, svc: AuthService = Depends())

@router.post("/login",           response_model=TokenResponse)
async def login(body: LoginRequest, svc: AuthService = Depends())

@router.post("/refresh",         response_model=TokenResponse)
async def refresh(body: RefreshRequest, svc: AuthService = Depends())

@router.post("/logout",          status_code=204)
async def logout(current_user: JWTPayload = Depends(get_current_user), svc: AuthService = Depends())

@router.post("/otp/send",        status_code=202)
async def send_otp(body: SendOTPRequest, svc: AuthService = Depends())

@router.post("/otp/verify",      response_model=MessageResponse)
async def verify_otp(body: OTPVerifyRequest, svc: AuthService = Depends())

@router.post("/password/reset-request", status_code=202)
async def request_reset(body: ResetRequestBody, svc: AuthService = Depends())

@router.post("/password/reset",  status_code=204)
async def reset_password(body: ResetPasswordRequest, svc: AuthService = Depends())

@router.post("/oauth/google",    response_model=TokenResponse)
async def google_oauth(body: GoogleOAuthRequest, svc: AuthService = Depends())

# ── Authenticated endpoints ─────────────────────────────────────
@router.get("/me",               response_model=AuthUserResponse)
async def get_me(current_user: JWTPayload = Depends(get_current_user))

@router.patch("/me/password",    status_code=204)
async def change_password(
    body: ChangePasswordRequest,
    current_user: JWTPayload = Depends(get_current_user),
    svc: AuthService = Depends()
)

# ── Internal (service-to-service, no Kong auth) ─────────────────
@router.post("/internal/validate-token", response_model=JWTClaimsResponse)
async def validate_token(body: ValidateTokenRequest)
# Called by Kong / other services to verify tokens
```

### 3.8 RBAC Rules for auth-service
| Endpoint | Allowed Roles |
|----------|--------------|
| POST /register | Public (no token) |
| POST /login | Public |
| POST /refresh | Any authenticated |
| POST /logout | Any authenticated |
| GET /me | Any authenticated |
| PATCH /me/password | Any authenticated (own account only) |
| POST /otp/* | Public |
| POST /password/* | Public |
| POST /oauth/google | Public |
| POST /internal/* | Internal service token only |

---

## 4. Service 02 — user-service

### 4.1 Responsibility
Manages user profiles, preferences, KYC (investors/guides), avatar uploads, activity history, and role-specific data (guide bio, merchant shop info).

### 4.2 Folder Structure
```
user-service/app/
├── api/v1/
│   ├── users.py            # /users/* (profile management)
│   └── kyc.py              # /users/kyc/* (document verification)
│
├── core/
│   ├── exceptions.py
│   └── events.py           # Emits: profile.updated
│
├── interfaces/
│   └── base_repository.py
│
├── repositories/
│   ├── user_repo.py        # PostgreSQL users CRUD
│   ├── profile_repo.py     # Extended profile data
│   └── kyc_repo.py         # KYC documents
│
├── schemas/
│   ├── requests/
│   │   ├── update_profile.py
│   │   ├── update_preferences.py
│   │   └── kyc_submit.py
│   └── responses/
│       ├── user_profile.py
│       └── kyc_status.py
│
└── services/
    ├── user_service.py
    └── kyc_service.py
```

### 4.3 ERD

```
┌────────────────────────────────────────────────────────────────────┐
│                          POSTGRESQL                                │
│                                                                    │
│  ┌────────────────────────┐       ┌──────────────────────────────┐ │
│  │         users          │       │        user_profiles         │ │
│  ├────────────────────────┤  1──1 ├──────────────────────────────┤ │
│  │ id           UUID PK   │──────▶│ user_id        UUID PK/FK    │ │
│  │ email        VARCHAR   │       │ full_name       VARCHAR       │ │
│  │ phone        VARCHAR   │       │ bio             TEXT          │ │
│  │ role         ENUM      │       │ avatar_url      VARCHAR       │ │
│  │ is_active    BOOL      │       │ city            VARCHAR       │ │
│  │ is_verified  BOOL      │       │ date_of_birth   DATE          │ │
│  │ created_at   TIMESTAMPTZ       │ nationality     VARCHAR       │ │
│  └────────────────────────┘       │ preferred_lang  ENUM(ar,en)   │ │
│            │                      │ notification_prefs JSONB      │ │
│            │                      │ social_links    JSONB         │ │
│            │                      │ updated_at      TIMESTAMPTZ   │ │
│            │                      └──────────────────────────────┘ │
│            │                                                        │
│            │  ┌──────────────────────────────────────────────────┐ │
│            │  │              kyc_documents                       │ │
│            │  ├──────────────────────────────────────────────────┤ │
│            └─▶│ id              UUID PK                          │ │
│          1..* │ user_id         UUID FK                          │ │
│               │ document_type   ENUM(national_id,passport,       │ │
│               │                      trade_license,guide_cert)   │ │
│               │ document_url    VARCHAR (MinIO path)             │ │
│               │ status          ENUM(pending,approved,rejected)  │ │
│               │ reviewed_by     UUID FK → users.id               │ │
│               │ review_note     TEXT                             │ │
│               │ submitted_at    TIMESTAMPTZ                      │ │
│               │ reviewed_at     TIMESTAMPTZ                      │ │
│               └──────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌──────────────────────────┐    ┌──────────────────────────────┐  │
│  │     guide_profiles       │    │     merchant_profiles        │  │
│  ├──────────────────────────┤    ├──────────────────────────────┤  │
│  │ user_id     UUID PK/FK   │    │ user_id     UUID PK/FK       │  │
│  │ expertise   TEXT[]       │    │ business_name VARCHAR        │  │
│  │ languages   TEXT[]       │    │ category    VARCHAR          │  │
│  │ areas       TEXT[]       │    │ address     TEXT             │  │
│  │ hourly_rate NUMERIC      │    │ geo_lat     NUMERIC          │  │
│  │ is_available BOOL        │    │ geo_lng     NUMERIC          │  │
│  │ rating_avg  NUMERIC      │    │ is_verified BOOL             │  │
│  │ rating_count INTEGER     │    └──────────────────────────────┘  │
│  └──────────────────────────┘                                      │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                           MONGODB                                  │
│                                                                    │
│  Collection: activity_logs                                         │
│  {                                                                 │
│    _id: ObjectId,                                                  │
│    user_id: UUID,                                                  │
│    action: "view_listing" | "search" | "book_guide" | ...,         │
│    resource_type: "listing" | "guide" | "investment",              │
│    resource_id: string,                                            │
│    metadata: { query?, filters?, duration_ms? },                   │
│    ip_hash: string,                                                │
│    created_at: ISODate                                             │
│  }                                                                 │
└────────────────────────────────────────────────────────────────────┘
```

### 4.4 Schemas

```python
# schemas/requests/update_profile.py
class UpdateProfileRequest(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=100)
    bio: str | None = Field(None, max_length=1000)
    city: str | None
    date_of_birth: date | None
    preferred_language: Literal["ar","en"] | None
    notification_prefs: NotificationPreferences | None

class NotificationPreferences(BaseModel):
    email: bool = True
    sms: bool = True
    push: bool = True
    digest_daily: bool = False

# schemas/requests/kyc_submit.py
class KYCSubmitRequest(BaseModel):
    document_type: Literal["national_id","passport","trade_license","guide_cert"]
    document_url: str   # MinIO path from media-service
    document_back_url: str | None   # national ID back

# schemas/responses/user_profile.py
class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    phone: str
    role: str
    profile: ProfileDetail
    kyc_status: str | None     # null if role doesn't need KYC
    guide_profile: GuideProfileDetail | None
    merchant_profile: MerchantProfileDetail | None
```

### 4.5 Service Layer — Business Logic

```python
class UserService:

    async def get_profile(self, user_id: UUID) -> UserProfileResponse:
        """
        1. Fetch user + profile JOIN from PostgreSQL
        2. Conditionally fetch guide_profile or merchant_profile based on role
        3. Append latest kyc_status if role in [investor, guide, merchant]
        4. Return assembled UserProfileResponse
        """

    async def update_profile(self, user_id: UUID, data: UpdateProfileRequest) -> UserProfileResponse:
        """
        1. Patch only provided (non-None) fields
        2. Validate city is within New Valley known cities
        3. Update updated_at timestamp
        4. Emit: profile.updated → RabbitMQ (triggers search re-index if guide)
        5. Invalidate Redis cache: user:profile:{user_id}
        """

    async def submit_kyc(self, user_id: UUID, data: KYCSubmitRequest) -> KYCStatusResponse:
        """
        1. Check role requires KYC (investor, guide, merchant) → raise 403 otherwise
        2. Validate document_url is accessible in MinIO
        3. Check for existing pending doc of same type → raise 409 CONFLICT
        4. Insert kyc_documents record with status=pending
        5. Emit: kyc.submitted → admin-service queue
        6. Return KYCStatusResponse
        """

    async def log_activity(self, user_id: UUID, action: str, resource_type: str, resource_id: str, metadata: dict) -> None:
        """
        Fire-and-forget: insert to MongoDB activity_logs
        Called internally by other services via event or direct HTTP.
        """
```

### 4.6 Controller (Router Signatures)

```python
# api/v1/users.py
router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me",              response_model=UserProfileResponse)
async def get_my_profile(current_user: JWTPayload = Depends(get_current_user), svc: UserService = Depends())

@router.patch("/me",            response_model=UserProfileResponse)
async def update_my_profile(body: UpdateProfileRequest, current_user: JWTPayload = Depends(get_current_user), svc: UserService = Depends())

@router.get("/{user_id}",       response_model=PublicProfileResponse)
async def get_public_profile(user_id: UUID, svc: UserService = Depends())
# Returns limited public info (no email/phone for non-admin)

@router.post("/me/avatar",      response_model=AvatarResponse)
async def upload_avatar(file: UploadFile, current_user: JWTPayload = Depends(get_current_user), svc: UserService = Depends())

@router.get("/me/activity",     response_model=PaginatedResponse[ActivityLogItem])
async def get_my_activity(
    page: int = 1,
    limit: int = 20,
    action: str | None = None,
    current_user: JWTPayload = Depends(get_current_user),
    svc: UserService = Depends()
)

# ── KYC endpoints ───────────────────────────────────────────────
# api/v1/kyc.py
kyc_router = APIRouter(prefix="/users/kyc", tags=["KYC"])

@kyc_router.post("/submit",     response_model=KYCStatusResponse, status_code=201)
async def submit_kyc(body: KYCSubmitRequest, current_user: JWTPayload = Depends(get_current_user), svc: KYCService = Depends())

@kyc_router.get("/status",      response_model=KYCStatusResponse)
async def get_kyc_status(current_user: JWTPayload = Depends(get_current_user), svc: KYCService = Depends())

# ── Admin endpoints ─────────────────────────────────────────────
@router.get("/",                response_model=PaginatedResponse[UserProfileResponse])
async def list_users(
    role: str | None = None,
    is_active: bool | None = None,
    page: int = 1,
    limit: int = 50,
    current_user: JWTPayload = Depends(require_roles(["admin","super_admin"]))
)

@router.patch("/{user_id}/role", response_model=UserProfileResponse)
async def change_user_role(user_id: UUID, body: ChangeRoleRequest, current_user: JWTPayload = Depends(require_roles(["super_admin"])))

@router.patch("/{user_id}/suspend", status_code=204)
async def suspend_user(user_id: UUID, body: SuspendRequest, current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

@kyc_router.patch("/{kyc_id}/review", response_model=KYCStatusResponse)
async def review_kyc(kyc_id: UUID, body: KYCReviewRequest, current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))
```

### 4.7 RBAC Rules for user-service
| Endpoint | Allowed Roles |
|----------|--------------|
| GET /users/me | Any authenticated |
| PATCH /users/me | Any authenticated (own only) |
| GET /users/{id} | Public (limited data) |
| POST /users/me/avatar | Any authenticated |
| GET /users/me/activity | Any authenticated |
| POST /users/kyc/submit | investor, guide, merchant |
| GET /users/kyc/status | investor, guide, merchant |
| GET /users/ (list all) | admin, super_admin |
| PATCH /users/{id}/role | super_admin only |
| PATCH /users/{id}/suspend | admin, super_admin |
| PATCH /kyc/{id}/review | admin, super_admin |

---

## 5. Service 03 — map-service

### 5.1 Responsibility
Points of Interest (POI) management, route calculation (Google Maps proxy), carpooling (post ride, find match, join), live driver location via WebSocket, and area information.

### 5.2 Folder Structure
```
map-service/app/      # Node.js (Express) — real-time WebSocket
├── api/v1/
│   ├── poi.js          # /map/poi/*
│   ├── routes.js       # /map/routes/*
│   └── carpooling.js   # /map/carpooling/*
│
├── core/
│   ├── googlemaps.js   # Google Maps API wrapper
│   ├── websocket.js    # Soketi / Socket.io live location
│   └── geo.js          # Haversine distance, bounding box utils
│
├── interfaces/
│   └── BaseRepository.js
│
├── repositories/
│   ├── PoiRepository.js          # PostgreSQL + PostGIS
│   └── CarpoolRepository.js      # PostgreSQL
│
├── schemas/
│   ├── requests/
│   │   ├── CreatePoi.js
│   │   └── CreateCarpoolRide.js
│   └── responses/
│       ├── PoiResponse.js
│       └── CarpoolMatchResponse.js
│
└── services/
    ├── MapService.js
    └── CarpoolService.js
```

### 5.3 ERD

```
┌────────────────────────────────────────────────────────────────────┐
│               POSTGRESQL 16 + PostGIS                              │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    points_of_interest                        │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id             UUID PK                                       │  │
│  │ name_ar        VARCHAR                                       │  │
│  │ name_en        VARCHAR                                       │  │
│  │ category       ENUM(hotel,restaurant,attraction,hospital,    │  │
│  │                     university,petrol,pharmacy,government,   │  │
│  │                     mosque,market,transport)                 │  │
│  │ description    TEXT                                          │  │
│  │ location       GEOMETRY(Point, 4326) — PostGIS               │  │
│  │ address        TEXT                                          │  │
│  │ city           VARCHAR (Kharga|Dakhla|Farafra|Baris|Balat)   │  │
│  │ phone          VARCHAR                                       │  │
│  │ website        VARCHAR                                       │  │
│  │ opening_hours  JSONB  {"mon":"08:00-22:00", ...}             │  │
│  │ images         TEXT[]                                        │  │
│  │ rating_avg     NUMERIC(3,2)                                  │  │
│  │ rating_count   INTEGER                                       │  │
│  │ is_verified    BOOL                                          │  │
│  │ added_by       UUID FK → users.id                           │  │
│  │ created_at     TIMESTAMPTZ                                   │  │
│  │ updated_at     TIMESTAMPTZ                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────┐    ┌──────────────────────────────┐  │
│  │     carpool_rides        │    │    carpool_passengers         │  │
│  ├──────────────────────────┤    ├──────────────────────────────┤  │
│  │ id          UUID PK      │    │ id          UUID PK          │  │
│  │ driver_id   UUID FK      │    │ ride_id     UUID FK          │  │
│  │ origin      GEOMETRY     │    │ passenger_id UUID FK         │  │
│  │ origin_name VARCHAR      │    │ seats_booked INTEGER         │  │
│  │ destination GEOMETRY     │    │ status      ENUM(pending,    │  │
│  │ dest_name   VARCHAR      │    │              confirmed,      │  │
│  │ departure_at TIMESTAMPTZ │    │              cancelled)      │  │
│  │ seats_total INTEGER      │    │ joined_at   TIMESTAMPTZ      │  │
│  │ seats_avail  INTEGER     │    └──────────────────────────────┘  │
│  │ price_per_seat NUMERIC   │                                      │
│  │ status      ENUM(open,   │    ┌──────────────────────────────┐  │
│  │             full,        │    │      route_history           │  │
│  │             cancelled,   │    ├──────────────────────────────┤  │
│  │             completed)   │    │ id          UUID PK          │  │
│  │ notes       TEXT         │    │ user_id     UUID FK          │  │
│  │ created_at  TIMESTAMPTZ  │    │ origin      GEOMETRY         │  │
│  └──────────────────────────┘    │ destination GEOMETRY         │  │
│                                  │ distance_km NUMERIC          │  │
│                                  │ duration_min INTEGER         │  │
│                                  │ created_at  TIMESTAMPTZ      │  │
│                                  └──────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                           REDIS                                    │
│  map:poi:nearby:{lat}:{lng}:{radius}  →  JSON[]  TTL: 1hr          │
│  map:poi:{id}                         →  JSON    TTL: 24hr         │
│  map:route:{hash(origin+dest)}        →  JSON    TTL: 2hr          │
│  map:driver:location:{user_id}        →  {lat,lng} TTL: 30s        │
└────────────────────────────────────────────────────────────────────┘
```

### 5.4 Service Layer — Business Logic

```python
class MapService:

    async def get_nearby_pois(self, lat: float, lng: float, radius_km: float,
                               category: str | None, limit: int) -> list[PoiResponse]:
        """
        1. Check Redis cache key map:poi:nearby:{lat:.2f}:{lng:.2f}:{radius}:{cat}
        2. Cache MISS: Query PostGIS ST_DWithin(location, point, radius_meters)
        3. Order by ST_Distance ASC
        4. Store in Redis TTL 1hr
        5. Return PoiResponse list with distance_km calculated
        """

    async def create_poi(self, data: CreatePoiRequest, user_id: UUID, role: str) -> PoiResponse:
        """
        1. Only admin/super_admin can create verified POIs directly
        2. Other roles create unverified (is_verified=False, queued for review)
        3. Validate coordinates are within New Valley bounding box:
           lat: [23.5, 26.0], lng: [28.0, 31.0]
        4. Insert to PostgreSQL
        5. Emit: poi.created → search-service (index), notification-service (if nearby watchers)
        """

    async def calculate_route(self, origin: LatLng, destination: LatLng,
                               mode: str) -> RouteResponse:
        """
        1. Build cache key from hash(origin+dest+mode)
        2. Cache HIT: return cached route
        3. Cache MISS: call Google Maps Directions API
        4. Extract steps, distance, duration, polyline
        5. Log to route_history (async)
        6. Cache TTL 2hr
        """

class CarpoolService:

    async def post_ride(self, driver_id: UUID, data: CreateCarpoolRide) -> CarpoolRide:
        """
        1. Validate departure_at is in future (min 30min from now)
        2. Check driver has no overlapping ride in same time window
        3. Insert carpool_rides with seats_avail = seats_total
        4. Emit: carpool.posted → notification-service (alert nearby users)
        """

    async def find_rides(self, origin: LatLng, destination: LatLng,
                          departure_date: date) -> list[CarpoolMatchResponse]:
        """
        1. Query rides WHERE:
           - ST_DWithin(origin, user_origin, 5km)
           - departure_at::date = departure_date
           - seats_avail > 0
           - status = 'open'
        2. Order by proximity to user origin ASC
        3. Include driver public profile
        """

    async def join_ride(self, ride_id: UUID, passenger_id: UUID, seats: int) -> CarpoolPassenger:
        """
        1. Fetch ride, lock row (SELECT FOR UPDATE)
        2. Validate seats_avail >= seats requested
        3. Decrement seats_avail
        4. If seats_avail == 0: set status = 'full'
        5. Insert carpool_passengers record
        6. Emit: carpool.joined → driver notification
        """
```

### 5.5 Controller (Router Signatures)

```python
# api/v1/poi.py
poi_router = APIRouter(prefix="/map/poi", tags=["Map - POI"])

@poi_router.get("/nearby",        response_model=list[PoiResponse])
async def get_nearby(lat: float, lng: float, radius_km: float = 10.0,
                     category: PoiCategory | None = None, limit: int = 50)

@poi_router.get("/city/{city}",   response_model=PaginatedResponse[PoiResponse])
async def get_by_city(city: str, category: PoiCategory | None = None,
                      page: int = 1, limit: int = 20)

@poi_router.get("/{poi_id}",      response_model=PoiDetailResponse)
async def get_poi(poi_id: UUID)

@poi_router.post("/",             response_model=PoiResponse, status_code=201)
async def create_poi(body: CreatePoiRequest, current_user: JWTPayload = Depends(get_current_user))

@poi_router.patch("/{poi_id}",    response_model=PoiResponse)
async def update_poi(poi_id: UUID, body: UpdatePoiRequest,
                     current_user: JWTPayload = Depends(get_current_user))
# Business rule: creator OR admin can update

@poi_router.delete("/{poi_id}",   status_code=204)
async def delete_poi(poi_id: UUID, current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

# api/v1/routes.py
route_router = APIRouter(prefix="/map/routes", tags=["Map - Routes"])

@route_router.post("/calculate",  response_model=RouteResponse)
async def calculate_route(body: RouteRequest, current_user: JWTPayload = Depends(get_current_user))

@route_router.get("/history",     response_model=PaginatedResponse[RouteHistoryItem])
async def get_route_history(page: int = 1, limit: int = 20,
                             current_user: JWTPayload = Depends(get_current_user))

# api/v1/carpooling.py
carpool_router = APIRouter(prefix="/map/carpooling", tags=["Map - Carpooling"])

@carpool_router.post("/rides",        response_model=CarpoolRideResponse, status_code=201)
async def post_ride(body: CreateCarpoolRide, current_user: JWTPayload = Depends(get_current_user))

@carpool_router.get("/rides",         response_model=PaginatedResponse[CarpoolMatchResponse])
async def find_rides(origin_lat: float, origin_lng: float,
                     dest_lat: float, dest_lng: float,
                     departure_date: date)

@carpool_router.get("/rides/{ride_id}", response_model=CarpoolRideDetailResponse)
async def get_ride(ride_id: UUID)

@carpool_router.post("/rides/{ride_id}/join",   response_model=CarpoolPassengerResponse)
async def join_ride(ride_id: UUID, body: JoinRideRequest,
                    current_user: JWTPayload = Depends(get_current_user))

@carpool_router.post("/rides/{ride_id}/cancel", status_code=204)
async def cancel_ride(ride_id: UUID, current_user: JWTPayload = Depends(get_current_user))
# Driver cancels own ride OR passenger cancels own seat

@carpool_router.get("/rides/my",      response_model=PaginatedResponse[CarpoolRideResponse])
async def my_rides(role: Literal["driver","passenger"] = "driver",
                   current_user: JWTPayload = Depends(get_current_user))

# WebSocket endpoint (Soketi channel)
# Channel: presence-ride.{ride_id}  — live driver GPS updates
# Event published: driver.location  payload: {lat, lng, timestamp}
```

---

## 6. Service 04 — market-service

### 6.1 Responsibility
Real estate listings (buy/rent/land), commercial property, price index, B2B business directory, merchant shop management, and market analytics/trends.

### 6.2 Folder Structure
```
market-service/app/
├── api/v1/
│   ├── listings.py         # /market/listings/*
│   ├── market.py           # /market/index/* (price index, trends)
│   └── b2b.py              # /market/b2b/* (business directory)
│
├── core/
│   ├── slug.py             # Arabic-safe slug generation
│   └── events.py           # listing.created, price.updated events
│
├── interfaces/
│   └── base_repository.py
│
├── repositories/
│   ├── listing_repo.py     # PostgreSQL structured data
│   ├── listing_meta_repo.py # MongoDB flexible metadata
│   └── price_repo.py       # Price index reads/writes
│
├── schemas/
│   ├── requests/
│   │   ├── create_listing.py
│   │   ├── update_listing.py
│   │   └── b2b_inquiry.py
│   └── responses/
│       ├── listing.py
│       ├── price_index.py
│       └── b2b_business.py
│
└── services/
    ├── listing_service.py
    ├── price_service.py
    └── b2b_service.py
```

### 6.3 ERD

```
┌────────────────────────────────────────────────────────────────────┐
│                         POSTGRESQL                                 │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                         listings                             │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id              UUID PK                                      │  │
│  │ slug            VARCHAR UNIQUE                               │  │
│  │ owner_id        UUID FK → users.id                          │  │
│  │ listing_type    ENUM(sale,rent,land,commercial)              │  │
│  │ title_ar        VARCHAR                                      │  │
│  │ title_en        VARCHAR                                      │  │
│  │ description_ar  TEXT                                         │  │
│  │ description_en  TEXT                                         │  │
│  │ price           NUMERIC                                      │  │
│  │ price_unit      ENUM(total,per_sqm,per_month,per_year)       │  │
│  │ area_sqm        NUMERIC                                      │  │
│  │ bedrooms        SMALLINT                                     │  │
│  │ bathrooms       SMALLINT                                     │  │
│  │ geo_lat         NUMERIC                                      │  │
│  │ geo_lng         NUMERIC                                      │  │
│  │ city            VARCHAR                                      │  │
│  │ district        VARCHAR                                      │  │
│  │ address         TEXT                                         │  │
│  │ status          ENUM(draft,pending_review,active,            │  │
│  │                      sold,rented,archived)                   │  │
│  │ is_featured     BOOL                                         │  │
│  │ is_verified     BOOL                                         │  │
│  │ view_count      INTEGER  DEFAULT 0                           │  │
│  │ save_count      INTEGER  DEFAULT 0                           │  │
│  │ contact_count   INTEGER  DEFAULT 0                           │  │
│  │ expires_at      TIMESTAMPTZ                                  │  │
│  │ created_at      TIMESTAMPTZ                                  │  │
│  │ updated_at      TIMESTAMPTZ                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│           │                            │                            │
│           │  1..*                      │ 1..*                       │
│           ▼                            ▼                            │
│  ┌──────────────────┐        ┌──────────────────────┐              │
│  │  listing_images  │        │  listing_saved        │              │
│  ├──────────────────┤        ├──────────────────────┤              │
│  │ id     UUID PK   │        │ user_id   UUID FK     │              │
│  │ listing_id UUID  │        │ listing_id UUID FK    │              │
│  │ url    VARCHAR   │        │ saved_at  TIMESTAMPTZ │              │
│  │ is_cover BOOL    │        │ PRIMARY KEY(user,lst) │              │
│  │ sort_order INT   │        └──────────────────────┘              │
│  └──────────────────┘                                              │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     price_index                              │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id           UUID PK                                         │  │
│  │ city         VARCHAR                                         │  │
│  │ listing_type ENUM(sale,rent,land,commercial)                 │  │
│  │ avg_price    NUMERIC                                         │  │
│  │ min_price    NUMERIC                                         │  │
│  │ max_price    NUMERIC                                         │  │
│  │ avg_sqm_price NUMERIC                                        │  │
│  │ listing_count INTEGER                                        │  │
│  │ recorded_at  DATE                                            │  │
│  │ UNIQUE(city, listing_type, recorded_at)                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    b2b_businesses                            │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id           UUID PK                                         │  │
│  │ owner_id     UUID FK                                         │  │
│  │ name_ar      VARCHAR                                         │  │
│  │ name_en      VARCHAR                                         │  │
│  │ category     VARCHAR (agriculture|tourism|manufacturing|...) │  │
│  │ description  TEXT                                            │  │
│  │ phone        VARCHAR                                         │  │
│  │ email        VARCHAR                                         │  │
│  │ website      VARCHAR                                         │  │
│  │ geo_lat      NUMERIC                                         │  │
│  │ geo_lng      NUMERIC                                         │  │
│  │ city         VARCHAR                                         │  │
│  │ is_verified  BOOL                                            │  │
│  │ created_at   TIMESTAMPTZ                                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                          MONGODB                                   │
│  Collection: listing_metadata                                      │
│  {                                                                 │
│    listing_id: UUID,                                               │
│    amenities: ["wifi","parking","generator","water_tank",...],     │
│    features: { floor: int, facing: "east"|"west", ... },           │
│    neighborhood: { schools:[], hospitals:[], markets:[] },          │
│    price_history: [{ price, recorded_at }],                        │
│    documents: [{ type, url }],   // title deed, floor plan         │
│    virtual_tour_url: string                                        │
│  }                                                                 │
│                                                                    │
│  Collection: b2b_inquiries                                         │
│  {                                                                 │
│    _id: ObjectId,                                                  │
│    business_id: UUID,                                              │
│    from_user_id: UUID,                                             │
│    subject: string,                                                │
│    message: string,                                                │
│    contact_info: { name, phone, email },                           │
│    status: "new"|"read"|"replied",                                 │
│    created_at: ISODate                                             │
│  }                                                                 │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                           REDIS                                    │
│  market:listing:{id}          → JSON   TTL: 30min                  │
│  market:listings:list:{hash}  → JSON[] TTL: 10min                  │
│  market:price:{city}:{type}   → JSON   TTL: 30min                  │
│  market:featured              → JSON[] TTL: 1hr                    │
└────────────────────────────────────────────────────────────────────┘
```

### 6.4 Service Layer — Business Logic

```python
class ListingService:

    async def create_listing(self, owner_id: UUID, role: str,
                              data: CreateListingRequest) -> ListingResponse:
        """
        1. Validate role can create: investor, merchant, local_citizen, admin
        2. Validate geo coordinates in New Valley bounding box
        3. Generate Arabic-safe slug from title_ar
        4. Set initial status:
           - admin → 'active' directly
           - others → 'pending_review'
        5. Insert listing row + listing_metadata doc in MongoDB
        6. Upload images are pre-validated (MinIO URLs from media-service)
        7. Emit: listing.created → search-service, map-service, notification-service
        8. Return full ListingResponse
        """

    async def get_listing(self, listing_id: UUID, viewer_id: UUID | None) -> ListingDetailResponse:
        """
        1. Check Redis cache hit
        2. Fetch listing from PostgreSQL
        3. Fetch metadata from MongoDB
        4. Increment view_count async (fire-and-forget)
        5. If viewer_id: check listing_saved for is_saved flag
        6. Cache assembled response
        """

    async def list_listings(self, filters: ListingFilters,
                             page: int, limit: int) -> PaginatedResponse[ListingResponse]:
        """
        Filters: city, listing_type, min_price, max_price, min_area, bedrooms, is_featured
        1. Build cache key from filter hash
        2. Cache HIT: return early
        3. PostgreSQL query with dynamic WHERE clauses
        4. Cache result TTL 10min
        """

    async def update_listing(self, listing_id: UUID, owner_id: UUID,
                              role: str, data: UpdateListingRequest) -> ListingResponse:
        """
        1. Fetch listing, verify ownership (owner_id == requester) OR admin
        2. If status change to 'active': requires admin role
        3. If price changes: append to price_history in MongoDB
        4. Invalidate Redis caches
        5. Emit: listing.updated → search-service re-index
        """

    async def save_listing(self, listing_id: UUID, user_id: UUID) -> None:
        """
        UPSERT into listing_saved, increment save_count on listing
        """

class PriceService:

    async def get_price_index(self, city: str,
                               listing_type: str) -> PriceIndexResponse:
        """
        1. Cache check market:price:{city}:{type}
        2. Fetch latest price_index record
        3. Include 30-day trend (last 30 daily records)
        """

    async def refresh_price_index(self) -> None:
        """
        CELERY TASK — runs every 30 min
        1. Aggregate AVG/MIN/MAX price from active listings per (city, type)
        2. Upsert price_index record for today's date
        3. Invalidate all market:price:* cache keys
        4. Emit: price.updated → notification-service (alert investors)
        """
```

### 6.5 Controller (Router Signatures)

```python
# api/v1/listings.py
listings_router = APIRouter(prefix="/market/listings", tags=["Market - Listings"])

@listings_router.get("/",           response_model=PaginatedResponse[ListingResponse])
async def list_listings(
    city: str | None = None,
    listing_type: ListingType | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_area: float | None = None,
    bedrooms: int | None = None,
    is_featured: bool | None = None,
    sort_by: Literal["price_asc","price_desc","newest","area"] = "newest",
    page: int = 1, limit: int = 20
)

@listings_router.get("/featured",   response_model=list[ListingResponse])
async def get_featured(limit: int = 10)

@listings_router.get("/saved",      response_model=PaginatedResponse[ListingResponse])
async def get_saved_listings(page: int = 1, limit: int = 20,
                              current_user: JWTPayload = Depends(get_current_user))

@listings_router.get("/{listing_id}", response_model=ListingDetailResponse)
async def get_listing(listing_id: UUID, request: Request)

@listings_router.post("/",           response_model=ListingResponse, status_code=201)
async def create_listing(body: CreateListingRequest,
                          current_user: JWTPayload = Depends(get_current_user))
# Allowed: investor, merchant, local_citizen, admin, super_admin

@listings_router.patch("/{listing_id}", response_model=ListingResponse)
async def update_listing(listing_id: UUID, body: UpdateListingRequest,
                          current_user: JWTPayload = Depends(get_current_user))

@listings_router.delete("/{listing_id}", status_code=204)
async def delete_listing(listing_id: UUID,
                          current_user: JWTPayload = Depends(get_current_user))
# Soft delete: sets status='archived'

@listings_router.post("/{listing_id}/save", status_code=204)
async def save_listing(listing_id: UUID,
                        current_user: JWTPayload = Depends(get_current_user))

@listings_router.delete("/{listing_id}/save", status_code=204)
async def unsave_listing(listing_id: UUID,
                          current_user: JWTPayload = Depends(get_current_user))

@listings_router.patch("/{listing_id}/verify", response_model=ListingResponse)
async def verify_listing(listing_id: UUID,
                          current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

# api/v1/market.py
market_router = APIRouter(prefix="/market/index", tags=["Market - Price Index"])

@market_router.get("/prices",       response_model=PriceIndexResponse)
async def get_price_index(city: str, listing_type: ListingType)

@market_router.get("/trends",       response_model=PriceTrendResponse)
async def get_price_trends(city: str, listing_type: ListingType, days: int = 30)

# api/v1/b2b.py
b2b_router = APIRouter(prefix="/market/b2b", tags=["Market - B2B"])

@b2b_router.get("/",               response_model=PaginatedResponse[B2BBusinessResponse])
async def list_businesses(category: str | None = None, city: str | None = None,
                            page: int = 1, limit: int = 20)

@b2b_router.get("/{business_id}",  response_model=B2BBusinessDetailResponse)
async def get_business(business_id: UUID)

@b2b_router.post("/",              response_model=B2BBusinessResponse, status_code=201)
async def create_business(body: CreateB2BRequest,
                            current_user: JWTPayload = Depends(require_roles(["investor","merchant","admin","super_admin"])))

@b2b_router.post("/{business_id}/inquire", status_code=202)
async def send_inquiry(business_id: UUID, body: B2BInquiryRequest,
                        current_user: JWTPayload = Depends(get_current_user))
```

---

## 7. Service 05 — guide-service

### 7.1 Responsibility
Tourist guide profiles, availability calendars, tour package creation, booking workflow (request → confirm → complete → review), earnings ledger, and service provider directory (accommodation, restaurants, transport).

### 7.2 Folder Structure
```
guide-service/app/
├── api/v1/
│   ├── guides.py           # /guides/* (profiles, search)
│   ├── bookings.py         # /guides/bookings/*
│   ├── packages.py         # /guides/packages/*
│   └── providers.py        # /guides/providers/* (accommodation, etc.)
│
├── core/
│   ├── calendar.py         # Availability conflict detection
│   └── events.py
│
├── repositories/
│   ├── guide_repo.py       # PostgreSQL guide profiles + MongoDB extended
│   ├── booking_repo.py     # PostgreSQL bookings
│   ├── package_repo.py     # PostgreSQL tour packages
│   └── provider_repo.py    # MongoDB service providers
│
├── schemas/
│   ├── requests/
│   │   ├── create_package.py
│   │   ├── create_booking.py
│   │   └── create_provider.py
│   └── responses/
│       ├── guide_profile.py
│       ├── booking.py
│       └── provider.py
│
└── services/
    ├── guide_service.py
    ├── booking_service.py
    └── provider_service.py
```

### 7.3 ERD

```
┌────────────────────────────────────────────────────────────────────┐
│                         POSTGRESQL                                 │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     guide_profiles                           │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ user_id          UUID PK/FK → users.id                      │  │
│  │ headline_ar      VARCHAR                                     │  │
│  │ headline_en      VARCHAR                                     │  │
│  │ about_ar         TEXT                                        │  │
│  │ about_en         TEXT                                        │  │
│  │ expertise_areas  TEXT[]  (archaeology,nature,cultural,       │  │
│  │                           adventure,photography)             │  │
│  │ languages        TEXT[]  (ar,en,fr,de,...)                   │  │
│  │ operating_cities TEXT[]                                      │  │
│  │ hourly_rate_egp  NUMERIC                                     │  │
│  │ daily_rate_egp   NUMERIC                                     │  │
│  │ years_experience SMALLINT                                    │  │
│  │ is_available     BOOL                                        │  │
│  │ kyc_verified     BOOL                                        │  │
│  │ rating_avg       NUMERIC(3,2)                                │  │
│  │ rating_count     INTEGER                                     │  │
│  │ total_bookings   INTEGER                                     │  │
│  │ total_earnings   NUMERIC  DEFAULT 0                          │  │
│  │ updated_at       TIMESTAMPTZ                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│            │ 1                                                      │
│            │                                                        │
│            │ *        ┌──────────────────────────────────────────┐  │
│            ├─────────▶│              tour_packages               │  │
│            │          ├──────────────────────────────────────────┤  │
│            │          │ id            UUID PK                    │  │
│            │          │ guide_id      UUID FK                    │  │
│            │          │ title_ar      VARCHAR                    │  │
│            │          │ title_en      VARCHAR                    │  │
│            │          │ description   TEXT                       │  │
│            │          │ duration_hrs  NUMERIC                    │  │
│            │          │ price_egp     NUMERIC                    │  │
│            │          │ max_capacity  SMALLINT                   │  │
│            │          │ category      VARCHAR                    │  │
│            │          │ includes      TEXT[]                     │  │
│            │          │ locations     JSONB []{ name, lat, lng } │  │
│            │          │ images        TEXT[]                     │  │
│            │          │ is_active     BOOL                       │  │
│            │          │ created_at    TIMESTAMPTZ                │  │
│            │          └──────────────────────────────────────────┘  │
│            │                          │ 1..*                        │
│            │                          ▼                             │
│            │          ┌──────────────────────────────────────────┐  │
│            │          │              bookings                    │  │
│            │          ├──────────────────────────────────────────┤  │
│            │          │ id              UUID PK                  │  │
│            │          │ package_id      UUID FK (nullable)       │  │
│            │          │ guide_id        UUID FK                  │  │
│            │          │ tourist_id      UUID FK                  │  │
│            │          │ booking_date    DATE                     │  │
│            │          │ start_time      TIME                     │  │
│            │          │ duration_hrs    NUMERIC                  │  │
│            │          │ group_size      SMALLINT                 │  │
│            │          │ total_price_egp NUMERIC                  │  │
│            │          │ status          ENUM(pending,confirmed,  │  │
│            │          │                      in_progress,        │  │
│            │          │                      completed,          │  │
│            │          │                      cancelled_guide,    │  │
│            │          │                      cancelled_tourist,  │  │
│            │          │                      no_show)            │  │
│            │          │ payment_status  ENUM(unpaid,paid,        │  │
│            │          │                      refunded)           │  │
│            │          │ special_requests TEXT                    │  │
│            │          │ meeting_point   VARCHAR                  │  │
│            │          │ cancelled_reason TEXT                    │  │
│            │          │ created_at      TIMESTAMPTZ              │  │
│            │          │ updated_at      TIMESTAMPTZ              │  │
│            │          └──────────────────────────────────────────┘  │
│            │                                                        │
│            │ *                                                       │
│            ▼                                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              guide_availability                              │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id         UUID PK                                           │  │
│  │ guide_id   UUID FK                                           │  │
│  │ date       DATE                                              │  │
│  │ slot_start TIME                                              │  │
│  │ slot_end   TIME                                              │  │
│  │ is_blocked BOOL  (blocked manually vs auto from booking)     │  │
│  │ booking_id UUID FK (nullable, when blocked by booking)       │  │
│  │ UNIQUE(guide_id, date, slot_start)                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                          MONGODB                                   │
│  Collection: service_providers                                     │
│  {                                                                 │
│    _id: ObjectId,                                                  │
│    category: "hotel"|"hostel"|"restaurant"|"cafe"|"transport"      │
│              |"pharmacy"|"hospital",                               │
│    name_ar: string, name_en: string,                               │
│    description: string, address: string,                           │
│    geo: { lat, lng }, city: string,                                │
│    contact: { phone, email, whatsapp },                            │
│    amenities: string[],                                            │
│    price_range: "$"|"$$"|"$$$",                                    │
│    images: string[],                                               │
│    rating_avg: number, rating_count: number,                       │
│    is_verified: boolean, owner_id: UUID,                           │
│    created_at: ISODate                                             │
│  }                                                                 │
└────────────────────────────────────────────────────────────────────┘
```

### 7.4 Service Layer — Business Logic

```python
class BookingService:

    async def request_booking(self, tourist_id: UUID,
                               data: CreateBookingRequest) -> BookingResponse:
        """
        1. Fetch guide profile → validate is_available=True, kyc_verified=True
        2. Check availability: query guide_availability for requested date/time
           → raise 409 CONFLICT if slot blocked
        3. Calculate total_price:
           - If package: package.price_egp * group_size
           - If custom: guide.hourly_rate * duration_hrs * group_size
        4. Create booking with status='pending'
        5. Auto-block availability slots
        6. Emit: booking.requested → guide notification (24hr to confirm or auto-cancel)
        7. Return BookingResponse
        """

    async def confirm_booking(self, booking_id: UUID, guide_id: UUID) -> BookingResponse:
        """
        1. Fetch booking → validate status='pending', guide_id matches
        2. Update status='confirmed'
        3. Emit: booking.confirmed → tourist notification + payment-service (collect payment)
        """

    async def complete_booking(self, booking_id: UUID, guide_id: UUID) -> BookingResponse:
        """
        1. Validate status='in_progress', guide_id matches
        2. Update status='completed'
        3. Emit: booking.completed → payment-service (release escrow to guide)
        4. Emit: review.prompt → tourist notification (7-day window to review)
        5. Increment guide.total_bookings
        """

    async def cancel_booking(self, booking_id: UUID, actor_id: UUID, reason: str) -> None:
        """
        1. Fetch booking → determine if actor is guide or tourist
        2. Cancellation policy:
           - tourist cancels >24hr before: full refund
           - tourist cancels <24hr before: 50% refund
           - guide cancels: full refund + guide penalty (flag)
        3. Set appropriate status (cancelled_guide or cancelled_tourist)
        4. Unblock availability slots
        5. Emit: booking.cancelled → payment-service (refund), notification-service
        """
```

### 7.5 Controller (Router Signatures)

```python
# api/v1/guides.py
guides_router = APIRouter(prefix="/guides", tags=["Guides"])

@guides_router.get("/",              response_model=PaginatedResponse[GuideCardResponse])
async def list_guides(
    city: str | None = None,
    expertise: str | None = None,
    language: str | None = None,
    min_rate: float | None = None,
    max_rate: float | None = None,
    sort_by: Literal["rating","price_asc","price_desc","bookings"] = "rating",
    page: int = 1, limit: int = 20
)

@guides_router.get("/{guide_id}",    response_model=GuideDetailResponse)
async def get_guide(guide_id: UUID)

@guides_router.get("/{guide_id}/availability", response_model=AvailabilityResponse)
async def get_availability(guide_id: UUID, month: int, year: int)

@guides_router.patch("/me",          response_model=GuideDetailResponse)
async def update_guide_profile(body: UpdateGuideProfileRequest,
                                current_user: JWTPayload = Depends(require_roles(["guide"])))

# api/v1/packages.py
packages_router = APIRouter(prefix="/guides/packages", tags=["Guide Packages"])

@packages_router.get("/",           response_model=PaginatedResponse[PackageResponse])
async def list_packages(city: str | None = None, category: str | None = None)

@packages_router.post("/",          response_model=PackageResponse, status_code=201)
async def create_package(body: CreatePackageRequest,
                          current_user: JWTPayload = Depends(require_roles(["guide"])))

@packages_router.patch("/{pkg_id}", response_model=PackageResponse)
async def update_package(pkg_id: UUID, body: UpdatePackageRequest,
                          current_user: JWTPayload = Depends(require_roles(["guide"])))

@packages_router.delete("/{pkg_id}", status_code=204)
async def delete_package(pkg_id: UUID,
                          current_user: JWTPayload = Depends(require_roles(["guide"])))

# api/v1/bookings.py
bookings_router = APIRouter(prefix="/guides/bookings", tags=["Guide Bookings"])

@bookings_router.post("/",          response_model=BookingResponse, status_code=201)
async def request_booking(body: CreateBookingRequest,
                           current_user: JWTPayload = Depends(get_current_user))
# Any authenticated user can book a guide

@bookings_router.get("/my",         response_model=PaginatedResponse[BookingResponse])
async def my_bookings(
    role: Literal["tourist","guide"] = "tourist",
    status: BookingStatus | None = None,
    page: int = 1, limit: int = 20,
    current_user: JWTPayload = Depends(get_current_user)
)

@bookings_router.get("/{booking_id}", response_model=BookingDetailResponse)
async def get_booking(booking_id: UUID,
                      current_user: JWTPayload = Depends(get_current_user))

@bookings_router.patch("/{booking_id}/confirm", response_model=BookingResponse)
async def confirm_booking(booking_id: UUID,
                           current_user: JWTPayload = Depends(require_roles(["guide"])))

@bookings_router.patch("/{booking_id}/complete", response_model=BookingResponse)
async def complete_booking(booking_id: UUID,
                            current_user: JWTPayload = Depends(require_roles(["guide"])))

@bookings_router.patch("/{booking_id}/cancel", status_code=204)
async def cancel_booking(booking_id: UUID, body: CancelBookingRequest,
                          current_user: JWTPayload = Depends(get_current_user))

# api/v1/providers.py
providers_router = APIRouter(prefix="/guides/providers", tags=["Service Providers"])

@providers_router.get("/",          response_model=PaginatedResponse[ProviderResponse])
async def list_providers(city: str | None = None, category: ProviderCategory | None = None,
                          page: int = 1, limit: int = 20)

@providers_router.get("/{provider_id}", response_model=ProviderDetailResponse)
async def get_provider(provider_id: str)  # MongoDB ObjectId

@providers_router.post("/",         response_model=ProviderResponse, status_code=201)
async def create_provider(body: CreateProviderRequest,
                           current_user: JWTPayload = Depends(get_current_user))
```

---

## 8. Service 06 — investment-service

### 8.1 Responsibility
Investment opportunity listings (agriculture, tourism, manufacturing, renewable energy), Expression of Interest (EOI) submissions, due diligence document room, investor-founder matching, pipeline status tracking.

### 8.2 ERD

```
┌────────────────────────────────────────────────────────────────────┐
│                         POSTGRESQL                                 │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │               investment_opportunities                       │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id               UUID PK                                     │  │
│  │ owner_id         UUID FK → users.id (poster)                 │  │
│  │ title_ar         VARCHAR                                     │  │
│  │ title_en         VARCHAR                                     │  │
│  │ sector           ENUM(agriculture,tourism,renewable_energy,  │  │
│  │                       manufacturing,real_estate,technology,  │  │
│  │                       services,other)                        │  │
│  │ opportunity_type ENUM(project,land,partnership,franchise,    │  │
│  │                       startup)                               │  │
│  │ min_investment   NUMERIC  (EGP)                              │  │
│  │ max_investment   NUMERIC  (EGP)                              │  │
│  │ expected_roi     NUMERIC  (%)                                │  │
│  │ payback_period   VARCHAR  ("3-5 years")                      │  │
│  │ city             VARCHAR                                     │  │
│  │ land_area_feddan NUMERIC                                     │  │
│  │ status           ENUM(draft,pending_review,active,           │  │
│  │                       funded,closed,expired)                 │  │
│  │ is_verified      BOOL                                        │  │
│  │ deadline         TIMESTAMPTZ                                 │  │
│  │ view_count       INTEGER                                     │  │
│  │ interest_count   INTEGER                                     │  │
│  │ created_at       TIMESTAMPTZ                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│             │  1                                                    │
│             │  *                                                    │
│             ▼                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              investment_interests (EOI)                      │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id                UUID PK                                    │  │
│  │ opportunity_id    UUID FK                                    │  │
│  │ investor_id       UUID FK                                    │  │
│  │ investment_amount NUMERIC                                    │  │
│  │ message           TEXT                                       │  │
│  │ status            ENUM(submitted,under_review,               │  │
│  │                        meeting_scheduled,accepted,           │  │
│  │                        rejected,withdrawn)                   │  │
│  │ owner_notes       TEXT  (private to opportunity owner)       │  │
│  │ submitted_at      TIMESTAMPTZ                                │  │
│  │ updated_at        TIMESTAMPTZ                                │  │
│  │ UNIQUE(opportunity_id, investor_id)                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                          MONGODB                                   │
│  Collection: opportunity_details                                   │
│  {                                                                 │
│    opportunity_id: UUID,                                           │
│    description_ar: string, description_en: string,                │
│    executive_summary_url: string,   // PDF in MinIO               │
│    documents: [{ type, url, is_public }],                         │
│    images: string[],                                               │
│    team: [{ name, role, linkedin }],                               │
│    milestones: [{ title, target_date, status }],                   │
│    faqs: [{ question, answer }],                                   │
│    location_details: { address, geo, map_url },                    │
│    updated_at: ISODate                                             │
│  }                                                                 │
│                                                                    │
│  Collection: investor_watchlist                                    │
│  {                                                                 │
│    user_id: UUID,                                                  │
│    opportunity_ids: UUID[],                                        │
│    sectors: string[],                                              │
│    min_investment: number,                                         │
│    max_investment: number,                                         │
│    updated_at: ISODate                                             │
│  }                                                                 │
└────────────────────────────────────────────────────────────────────┘
```

### 8.3 Service Layer — Business Logic

```python
class InvestmentService:

    async def create_opportunity(self, owner_id: UUID, role: str,
                                  data: CreateOpportunityRequest) -> OpportunityResponse:
        """
        1. Validate role: investor, merchant → can post
        2. Create PostgreSQL record status='pending_review'
        3. Insert MongoDB opportunity_details doc
        4. Emit: opportunity.created → admin queue for review, search-service
        """

    async def express_interest(self, investor_id: UUID,
                                data: ExpressInterestRequest) -> InterestResponse:
        """
        1. Validate investor has completed KYC
        2. Validate opportunity status='active'
        3. Check no existing EOI (UNIQUE constraint) → raise 409
        4. Validate investment_amount >= opportunity.min_investment
        5. Insert investment_interests
        6. Increment interest_count on opportunity
        7. Emit: investment.interest → opportunity owner notification
        8. Emit: kyc_check.required → verify investor KYC docs attached
        """

    async def update_interest_status(self, opportunity_owner_id: UUID,
                                      interest_id: UUID, status: str, notes: str | None) -> InterestResponse:
        """
        Only opportunity owner can move through pipeline:
        submitted → under_review → meeting_scheduled → accepted|rejected
        """

    async def get_dashboard(self, investor_id: UUID) -> InvestorDashboard:
        """
        Returns:
        - Active EOIs with status breakdown
        - Watchlist opportunities with latest status
        - Recommended opportunities based on watchlist sectors
        """
```

### 8.4 Controller (Router Signatures)

```python
# api/v1/investment.py
invest_router = APIRouter(prefix="/investment", tags=["Investment"])

@invest_router.get("/",              response_model=PaginatedResponse[OpportunityCardResponse])
async def list_opportunities(
    sector: InvestmentSector | None = None,
    city: str | None = None,
    opportunity_type: OpportunityType | None = None,
    min_investment: float | None = None,
    max_investment: float | None = None,
    sort_by: Literal["newest","roi_desc","min_invest_asc"] = "newest",
    page: int = 1, limit: int = 20
)
# Public: tourist/student see limited info; investor sees full detail

@invest_router.get("/{opp_id}",      response_model=OpportunityDetailResponse)
async def get_opportunity(opp_id: UUID, request: Request)
# Full detail only for investor+ or admin

@invest_router.post("/",             response_model=OpportunityResponse, status_code=201)
async def create_opportunity(body: CreateOpportunityRequest,
                              current_user: JWTPayload = Depends(require_roles(["investor","merchant","admin","super_admin"])))

@invest_router.patch("/{opp_id}",    response_model=OpportunityResponse)
async def update_opportunity(opp_id: UUID, body: UpdateOpportunityRequest,
                              current_user: JWTPayload = Depends(get_current_user))

@invest_router.post("/{opp_id}/interest", response_model=InterestResponse, status_code=201)
async def express_interest(opp_id: UUID, body: ExpressInterestRequest,
                            current_user: JWTPayload = Depends(require_roles(["investor"])))

@invest_router.get("/interests/my",  response_model=PaginatedResponse[InterestResponse])
async def my_interests(status: InterestStatus | None = None,
                        current_user: JWTPayload = Depends(require_roles(["investor"])))

@invest_router.get("/{opp_id}/interests", response_model=PaginatedResponse[InterestResponse])
async def list_interests_for_opportunity(
    opp_id: UUID,
    status: InterestStatus | None = None,
    current_user: JWTPayload = Depends(get_current_user)
)
# Only opportunity owner or admin

@invest_router.patch("/interests/{interest_id}/status", response_model=InterestResponse)
async def update_interest_status(interest_id: UUID, body: UpdateInterestStatusRequest,
                                  current_user: JWTPayload = Depends(get_current_user))

@invest_router.get("/dashboard",     response_model=InvestorDashboard)
async def investor_dashboard(current_user: JWTPayload = Depends(require_roles(["investor"])))

@invest_router.post("/watchlist",    status_code=204)
async def update_watchlist(body: WatchlistRequest,
                            current_user: JWTPayload = Depends(require_roles(["investor"])))

@invest_router.patch("/{opp_id}/verify", response_model=OpportunityResponse)
async def verify_opportunity(opp_id: UUID,
                              current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))
```

---

## 9. Service 07 — payment-service

### 9.1 Responsibility
Wallet management, booking payment escrow, subscription billing (guide/merchant plans), payout processing (guide earnings), Paymob gateway integration, transaction history.

### 9.2 ERD

```
┌────────────────────────────────────────────────────────────────────┐
│                         POSTGRESQL                                 │
│                                                                    │
│  ┌──────────────────────────┐    ┌──────────────────────────────┐  │
│  │         wallets          │    │       transactions           │  │
│  ├──────────────────────────┤    ├──────────────────────────────┤  │
│  │ id       UUID PK         │    │ id           UUID PK         │  │
│  │ user_id  UUID FK UNIQUE  │    │ wallet_id    UUID FK         │  │
│  │ balance  NUMERIC(12,2)   │    │ type         ENUM(deposit,   │  │
│  │ currency VARCHAR(3)='EGP'│    │               withdrawal,    │  │
│  │ is_frozen BOOL           │    │               payment,       │  │
│  │ created_at TIMESTAMPTZ   │    │               refund,        │  │
│  │ updated_at TIMESTAMPTZ   │    │               payout,        │  │
│  └──────────────────────────┘    │               commission)    │  │
│                                  │ amount       NUMERIC(12,2)   │  │
│                                  │ balance_after NUMERIC(12,2)  │  │
│                                  │ reference_id  UUID           │  │
│                                  │ reference_type VARCHAR       │  │
│                                  │  (booking|subscription|      │  │
│                                  │   withdrawal|deposit)        │  │
│                                  │ description  TEXT            │  │
│                                  │ status       ENUM(pending,   │  │
│                                  │               completed,     │  │
│                                  │               failed,        │  │
│                                  │               reversed)      │  │
│                                  │ gateway_ref  VARCHAR         │  │
│                                  │ created_at   TIMESTAMPTZ     │  │
│                                  └──────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    booking_payments                          │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id              UUID PK                                      │  │
│  │ booking_id      UUID FK (guide-service booking)              │  │
│  │ tourist_wallet  UUID FK → wallets.id                         │  │
│  │ guide_wallet    UUID FK → wallets.id                         │  │
│  │ amount          NUMERIC(12,2)                                │  │
│  │ platform_fee    NUMERIC(12,2)  (10% commission)              │  │
│  │ guide_amount    NUMERIC(12,2)  (90%)                         │  │
│  │ escrow_status   ENUM(held,released,refunded)                 │  │
│  │ held_at         TIMESTAMPTZ                                  │  │
│  │ released_at     TIMESTAMPTZ                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    subscriptions                             │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id           UUID PK                                         │  │
│  │ user_id      UUID FK                                         │  │
│  │ plan         ENUM(free,guide_basic,guide_pro,                │  │
│  │                   merchant_basic,merchant_pro)               │  │
│  │ status       ENUM(active,cancelled,expired,trial)            │  │
│  │ price_egp    NUMERIC                                         │  │
│  │ billing_cycle ENUM(monthly,annual)                           │  │
│  │ starts_at    TIMESTAMPTZ                                     │  │
│  │ ends_at      TIMESTAMPTZ                                     │  │
│  │ auto_renew   BOOL                                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

### 9.3 Service Layer — Business Logic

```python
class PaymentService:

    async def hold_booking_payment(self, booking_id: UUID, tourist_id: UUID,
                                    amount: float) -> BookingPaymentResponse:
        """
        1. Fetch tourist wallet → validate balance >= amount
        2. Debit tourist wallet (transaction type=payment)
        3. Create booking_payment record status=held
        4. Emit: payment.held → guide-service (confirm booking can proceed)
        """

    async def release_booking_payment(self, booking_id: UUID) -> None:
        """
        Called on booking.completed event
        1. Fetch booking_payment record
        2. Calculate platform_fee = amount * 0.10
        3. guide_amount = amount - platform_fee
        4. Credit guide wallet (transaction type=payout)
        5. Update escrow_status='released'
        6. Emit: payment.released → notification-service
        """

    async def refund_booking(self, booking_id: UUID, refund_pct: float) -> None:
        """
        Called on booking.cancelled event
        refund_pct: 1.0 (full) or 0.5 (partial)
        1. Fetch booking_payment
        2. Calculate refund_amount = amount * refund_pct
        3. Credit tourist wallet (transaction type=refund)
        4. Update escrow_status='refunded' (or partial)
        """

    async def deposit(self, user_id: UUID, amount: float, gateway_ref: str) -> TransactionResponse:
        """
        Paymob webhook callback after successful payment
        1. Validate gateway_ref not already processed (idempotency)
        2. Credit user wallet
        3. Create transaction record
        """

    async def request_withdrawal(self, user_id: UUID, amount: float,
                                   bank_details: BankDetails) -> WithdrawalResponse:
        """
        1. Validate user role is guide or merchant
        2. Validate wallet balance >= amount
        3. Debit wallet (transaction type=withdrawal, status=pending)
        4. Queue async payout job via Celery
        5. Return pending status with estimated processing time
        """
```

### 9.4 Controller (Router Signatures)

```python
# api/v1/payments.py
payments_router = APIRouter(prefix="/payments", tags=["Payments"])

@payments_router.get("/wallet",              response_model=WalletResponse)
async def get_wallet(current_user: JWTPayload = Depends(get_current_user))

@payments_router.get("/transactions",        response_model=PaginatedResponse[TransactionResponse])
async def get_transactions(
    type: TransactionType | None = None,
    page: int = 1, limit: int = 20,
    current_user: JWTPayload = Depends(get_current_user)
)

@payments_router.post("/deposit/initiate",   response_model=PaymobOrderResponse)
async def initiate_deposit(body: DepositRequest,
                            current_user: JWTPayload = Depends(get_current_user))
# Returns Paymob payment key for frontend redirect

@payments_router.post("/deposit/webhook",    status_code=200)
async def paymob_webhook(payload: dict, x_hmac: str = Header(...))
# Paymob HMAC-verified callback — no auth token

@payments_router.post("/withdraw",           response_model=WithdrawalResponse, status_code=202)
async def request_withdrawal(body: WithdrawalRequest,
                              current_user: JWTPayload = Depends(require_roles(["guide","merchant"])))

@payments_router.get("/subscriptions/my",    response_model=SubscriptionResponse)
async def get_my_subscription(current_user: JWTPayload = Depends(get_current_user))

@payments_router.post("/subscriptions",      response_model=SubscriptionResponse)
async def subscribe(body: SubscribeRequest,
                    current_user: JWTPayload = Depends(require_roles(["guide","merchant"])))

@payments_router.delete("/subscriptions/my", status_code=204)
async def cancel_subscription(current_user: JWTPayload = Depends(get_current_user))

# ── Internal (called by other services) ──────────────────────────
@payments_router.post("/internal/hold",      response_model=BookingPaymentResponse)
async def hold_payment(body: HoldPaymentRequest)
# Called by guide-service on booking.confirmed

@payments_router.post("/internal/release",   status_code=204)
async def release_payment(body: ReleasePaymentRequest)
# Called on booking.completed event
```

---

## 10. Service 08 — notification-service

### 10.1 Responsibility
Multi-channel notifications: Push (FCM), In-app (stored), Email (Resend), SMS (Vonage). Notification preferences, broadcast campaigns, and read/unread management.

### 10.2 ERD

```
┌────────────────────────────────────────────────────────────────────┐
│                         POSTGRESQL                                 │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      notifications                           │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id            UUID PK                                        │  │
│  │ user_id       UUID FK                                        │  │
│  │ type          ENUM(booking_request,booking_confirmed,        │  │
│  │                    booking_completed,booking_cancelled,      │  │
│  │                    payment_received,payment_sent,            │  │
│  │                    review_prompt,kyc_update,                 │  │
│  │                    new_listing,price_alert,                  │  │
│  │                    investment_interest,system,               │  │
│  │                    welcome,general)                          │  │
│  │ title_ar      VARCHAR                                        │  │
│  │ title_en      VARCHAR                                        │  │
│  │ body_ar       TEXT                                           │  │
│  │ body_en       TEXT                                           │  │
│  │ action_url    VARCHAR  (deep-link)                           │  │
│  │ is_read       BOOL     DEFAULT FALSE                         │  │
│  │ read_at       TIMESTAMPTZ                                    │  │
│  │ channels_sent TEXT[]   (push,email,sms,in_app)               │  │
│  │ metadata      JSONB                                          │  │
│  │ created_at    TIMESTAMPTZ                                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  device_tokens                               │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id          UUID PK                                          │  │
│  │ user_id     UUID FK                                          │  │
│  │ fcm_token   VARCHAR                                          │  │
│  │ platform    ENUM(web,android,ios)                            │  │
│  │ device_name VARCHAR                                          │  │
│  │ last_seen   TIMESTAMPTZ                                      │  │
│  │ UNIQUE(user_id, fcm_token)                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                           REDIS                                    │
│  notif:unread_count:{user_id}  →  integer  TTL: invalidated on new  │
│  notif:prefs:{user_id}         →  JSON     TTL: 24hr               │
└────────────────────────────────────────────────────────────────────┘
```

### 10.3 Service Layer — Business Logic

```python
class NotificationService:

    async def send(self, user_id: UUID, notif_type: str,
                   context: dict, channels: list[str] | None = None) -> None:
        """
        1. Fetch user notification preferences from Redis/DB
        2. Determine channels to use (preference intersection with requested channels)
        3. Render templates (ar/en based on user.preferred_language):
           - title_ar/en, body_ar/en from Jinja2 templates indexed by notif_type
        4. Insert notification record (in_app always stored)
        5. Parallel execution:
           - push: If FCM token exists → send via firebase-admin
           - email: If pref enabled → queue to Resend via Celery task
           - sms: If pref enabled + phone verified → queue to Vonage via Celery
        6. Invalidate notif:unread_count:{user_id}
        """

    async def get_unread_count(self, user_id: UUID) -> int:
        """
        1. Check Redis cache notif:unread_count:{user_id}
        2. Cache MISS: COUNT WHERE user_id=user_id AND is_read=FALSE
        3. Cache result (invalidated on new notification)
        """

    async def mark_read(self, user_id: UUID,
                         notification_ids: list[UUID] | None = None) -> None:
        """
        If notification_ids is None: mark ALL unread as read
        Else: mark specific ones
        Invalidate Redis count cache
        """
```

### 10.4 Controller (Router Signatures)

```python
# api/v1/notifications.py
notif_router = APIRouter(prefix="/notifications", tags=["Notifications"])

@notif_router.get("/",                response_model=PaginatedResponse[NotificationResponse])
async def list_notifications(
    is_read: bool | None = None,
    type: NotificationType | None = None,
    page: int = 1, limit: int = 20,
    current_user: JWTPayload = Depends(get_current_user)
)

@notif_router.get("/unread-count",    response_model=UnreadCountResponse)
async def get_unread_count(current_user: JWTPayload = Depends(get_current_user))

@notif_router.patch("/mark-read",     status_code=204)
async def mark_read(body: MarkReadRequest,
                    current_user: JWTPayload = Depends(get_current_user))
# body.ids = null → mark all; body.ids = [uuid,...] → mark specific

@notif_router.delete("/{notif_id}",   status_code=204)
async def delete_notification(notif_id: UUID,
                               current_user: JWTPayload = Depends(get_current_user))

@notif_router.post("/device-token",   status_code=204)
async def register_device_token(body: DeviceTokenRequest,
                                 current_user: JWTPayload = Depends(get_current_user))

@notif_router.delete("/device-token/{fcm_token}", status_code=204)
async def unregister_device_token(fcm_token: str,
                                   current_user: JWTPayload = Depends(get_current_user))

@notif_router.get("/preferences",     response_model=NotifPreferencesResponse)
async def get_preferences(current_user: JWTPayload = Depends(get_current_user))

@notif_router.patch("/preferences",   response_model=NotifPreferencesResponse)
async def update_preferences(body: NotifPreferencesRequest,
                              current_user: JWTPayload = Depends(get_current_user))

# ── Internal (called by other services via RabbitMQ consumer) ────
@notif_router.post("/internal/send",  status_code=202)
async def internal_send(body: InternalSendRequest)
# Called by other services. Validates internal-only API key.

# ── Admin (broadcast campaigns) ──────────────────────────────────
@notif_router.post("/broadcast",      status_code=202)
async def broadcast(body: BroadcastRequest,
                    current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))
# Sends to all users OR filtered by role/city
```

---

## 11. Service 09 — search-service

### 11.1 Responsibility
Unified full-text search across all content types (listings, guides, POIs, investment opportunities, service providers), geo-search, faceted filters, autocomplete, and index synchronization from domain events.

### 11.2 Index Schema (Meilisearch)

```
┌────────────────────────────────────────────────────────────────────┐
│                        MEILISEARCH INDEXES                         │
│                                                                    │
│  Index: listings                                                   │
│  {                                                                 │
│    id, slug, title_ar, title_en, description_ar, description_en,  │
│    listing_type, price, area_sqm, bedrooms, city, district,        │
│    is_featured, is_verified, view_count, rating_avg,               │
│    geo: { lat, lng }  ← used for _geoRadius filter                 │
│  }                                                                 │
│  Filterable: listing_type, city, bedrooms, is_featured, price      │
│  Sortable: price, created_at, view_count                           │
│  Searchable: title_ar, title_en, description_ar, city, district    │
│                                                                    │
│  Index: guides                                                     │
│  {                                                                 │
│    id, full_name, headline_ar, headline_en, expertise_areas,       │
│    languages, operating_cities, hourly_rate, daily_rate,           │
│    rating_avg, rating_count, kyc_verified, is_available            │
│  }                                                                 │
│                                                                    │
│  Index: investments                                                │
│  {                                                                 │
│    id, title_ar, title_en, sector, opportunity_type,               │
│    min_investment, max_investment, expected_roi, city,             │
│    is_verified, deadline, status                                   │
│  }                                                                 │
│                                                                    │
│  Index: pois                                                       │
│  {                                                                 │
│    id, name_ar, name_en, category, city, description,              │
│    geo: { lat, lng }, rating_avg, is_verified                      │
│  }                                                                 │
│                                                                    │
│  Index: providers                                                  │
│  {                                                                 │
│    id, name_ar, name_en, category, city, description,              │
│    price_range, rating_avg, is_verified                            │
│  }                                                                 │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                    REDIS                                           │
│  search:autocomplete:{prefix}   → string[]   TTL: 1hr             │
│  search:results:{hash(query)}   → JSON       TTL: 5min            │
└────────────────────────────────────────────────────────────────────┘
```

### 11.3 Service Layer — Business Logic

```python
class SearchService:

    async def unified_search(self, query: str, content_types: list[str] | None,
                              filters: SearchFilters, page: int,
                              limit: int) -> UnifiedSearchResponse:
        """
        1. Check Redis cache by query hash
        2. Fan out parallel searches to requested Meilisearch indexes
        3. Merge results by relevance score
        4. Group by content_type for faceted display
        5. Cache TTL 5min
        6. Log search query async (for analytics)
        """

    async def geo_search(self, lat: float, lng: float, radius_km: float,
                          content_type: str, limit: int) -> list[SearchResult]:
        """
        Uses Meilisearch _geoRadius filter
        Ordered by _geoDistance ASC
        """

    async def autocomplete(self, prefix: str, limit: int = 8) -> list[str]:
        """
        1. Check Redis cache
        2. Meilisearch search with limit=8, attributesToRetrieve=['title_ar','title_en']
        3. Deduplicate and combine suggestions
        4. Cache TTL 1hr
        """

    # ── Index Sync (called via RabbitMQ consumers) ────────────────
    async def index_document(self, index: str, doc: dict) -> None
    async def update_document(self, index: str, doc_id: str, partial: dict) -> None
    async def delete_document(self, index: str, doc_id: str) -> None
```

### 11.4 Controller (Router Signatures)

```python
# api/v1/search.py
search_router = APIRouter(prefix="/search", tags=["Search"])

@search_router.get("/",              response_model=UnifiedSearchResponse)
async def unified_search(
    q: str = Query(min_length=1, max_length=200),
    types: list[str] = Query(default=["listings","guides","investments","pois"]),
    city: str | None = None,
    page: int = 1, limit: int = 20
)

@search_router.get("/listings",      response_model=SearchResultsResponse)
async def search_listings(
    q: str,
    city: str | None = None,
    listing_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str = "relevance",
    page: int = 1, limit: int = 20
)

@search_router.get("/guides",        response_model=SearchResultsResponse)
async def search_guides(
    q: str,
    city: str | None = None,
    language: str | None = None,
    expertise: str | None = None,
    page: int = 1, limit: int = 20
)

@search_router.get("/investments",   response_model=SearchResultsResponse)
async def search_investments(
    q: str,
    sector: str | None = None,
    city: str | None = None,
    page: int = 1, limit: int = 20
)

@search_router.get("/geo",           response_model=list[GeoSearchResult])
async def geo_search(
    lat: float, lng: float,
    radius_km: float = Query(default=10, le=50),
    type: Literal["pois","listings","providers"] = "pois",
    category: str | None = None,
    limit: int = Query(default=20, le=100)
)

@search_router.get("/autocomplete",  response_model=AutocompleteResponse)
async def autocomplete(q: str = Query(min_length=2, max_length=50), limit: int = 8)

# ── Internal (no auth, called by other services) ─────────────────
@search_router.post("/internal/index",  status_code=202)
async def index_document(body: IndexDocumentRequest)

@search_router.patch("/internal/index/{index}/{doc_id}", status_code=204)
async def update_document(index: str, doc_id: str, body: dict)

@search_router.delete("/internal/index/{index}/{doc_id}", status_code=204)
async def delete_document(index: str, doc_id: str)
```

---

## 12. Service 10 — ai-service

### 12.1 Responsibility
RAG chatbot assistant (Arabic + English), recommendation engine (guides, listings, investments), price prediction model, sentiment analysis on reviews, content moderation.

### 12.2 Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                          QDRANT (Vector Store)                     │
│                                                                    │
│  Collection: hena_knowledge_base                                   │
│  Vector size: 1536 (OpenAI text-embedding-3-small)                 │
│  Distance: Cosine                                                  │
│  Payload fields:                                                   │
│    source_type: "listing"|"guide"|"investment"|"faq"|"area_guide"  │
│    source_id:   UUID or MongoDB ObjectId                           │
│    title:       string                                             │
│    content:     string (chunk, max 512 tokens)                     │
│    category:    string                                             │
│    city:        string                                             │
│    language:    "ar"|"en"|"bilingual"                              │
│    updated_at:  ISO timestamp                                      │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                          MONGODB                                   │
│  Collection: chat_sessions                                         │
│  {                                                                 │
│    _id: ObjectId,                                                  │
│    session_id: UUID,                                               │
│    user_id: UUID | null,  // null for anonymous                    │
│    messages: [                                                     │
│      { role: "user"|"assistant", content: string,                  │
│        sources: [{title, url, snippet}],                           │
│        timestamp: ISODate }                                        │
│    ],                                                              │
│    language: "ar"|"en",                                            │
│    created_at: ISODate,                                            │
│    last_active: ISODate                                            │
│  }                                                                 │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                           REDIS                                    │
│  ai:session:{session_id}  →  recent_context JSON   TTL: 1hr       │
│  ai:recommendations:{user_id} → JSON                TTL: 30min    │
└────────────────────────────────────────────────────────────────────┘
```

### 12.3 Service Layer — Business Logic

```python
class ChatService:

    async def chat(self, session_id: str, user_message: str,
                   user_id: UUID | None, lang: str) -> ChatResponse:
        """
        RAG Pipeline:
        1. Load session history from Redis (last 10 turns)
        2. Embed user_message using text-embedding-3-small
        3. Qdrant query: top-5 chunks by cosine similarity
           - Filter by city if user location available
        4. Build system prompt:
           - Persona: friendly local expert for New Valley
           - Language instruction: respond in {lang}
           - Context: inject retrieved chunks
           - Conversation history: last 5 turns
        5. Call LLM (gpt-4o-mini / Ollama fallback)
        6. Extract cited sources from LLM response
        7. Append turn to MongoDB session
        8. Update Redis session cache
        9. Return ChatResponse with message + sources
        """

    async def get_suggestions(self, user_id: UUID | None) -> list[str]:
        """
        Returns 6 contextual suggested questions based on:
        - User role and activity history (if authenticated)
        - Current trending queries
        - Time of year (tourism season awareness)
        """

class RecommendationService:

    async def get_recommendations(self, user_id: UUID, content_type: str,
                                   limit: int = 10) -> list[RecommendationItem]:
        """
        Algorithm:
        1. Check Redis cache
        2. Fetch user activity_logs from MongoDB (last 30 days)
        3. Extract feature vector:
           - Preferred categories (from viewed items)
           - Price sensitivity (from viewed prices)
           - Location preference (from search history)
           - Time patterns (tourism season)
        4. Query Qdrant for similar content embeddings
        5. Apply collaborative filtering (users with similar profiles)
        6. Filter out already-seen items
        7. Cache and return
        """
```

### 12.4 Controller (Router Signatures)

```python
# api/v1/chat.py
chat_router = APIRouter(prefix="/chat", tags=["AI Chatbot"])

@chat_router.post("/",                response_model=ChatResponse)
async def chat(body: ChatRequest,
               current_user: JWTPayload | None = Depends(get_optional_user))
# Anonymous allowed but rate-limited more strictly

@chat_router.get("/sessions",         response_model=PaginatedResponse[SessionSummary])
async def list_sessions(page: int = 1, limit: int = 10,
                         current_user: JWTPayload = Depends(get_current_user))

@chat_router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(session_id: str,
                       current_user: JWTPayload = Depends(get_current_user))

@chat_router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str,
                          current_user: JWTPayload = Depends(get_current_user))

@chat_router.get("/suggestions",      response_model=SuggestionsResponse)
async def get_suggestions(current_user: JWTPayload | None = Depends(get_optional_user))

# api/v1/recommendations.py
rec_router = APIRouter(prefix="/recommendations", tags=["AI Recommendations"])

@rec_router.get("/listings",          response_model=list[ListingCardResponse])
async def recommend_listings(limit: int = 10,
                              current_user: JWTPayload = Depends(get_current_user))

@rec_router.get("/guides",            response_model=list[GuideCardResponse])
async def recommend_guides(limit: int = 10,
                            current_user: JWTPayload = Depends(get_current_user))

@rec_router.get("/investments",       response_model=list[OpportunityCardResponse])
async def recommend_investments(limit: int = 10,
                                 current_user: JWTPayload = Depends(require_roles(["investor"])))

# ── Admin: RAG Knowledge Base Management ─────────────────────────
@chat_router.post("/admin/ingest",    status_code=202)
async def ingest_documents(body: IngestRequest,
                            current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

@chat_router.post("/admin/reindex",   status_code=202)
async def full_reindex(current_user: JWTPayload = Depends(require_roles(["super_admin"])))
```

---

## 13. Service 11 — media-service

### 13.1 Responsibility
File upload (images, PDFs), image resizing/WebP conversion, virus scanning, CDN presigned URL generation (MinIO/S3), and file reference management.

### 13.2 ERD

```
┌────────────────────────────────────────────────────────────────────┐
│                          MONGODB                                   │
│  Collection: file_references                                       │
│  {                                                                 │
│    _id: ObjectId,                                                  │
│    file_id: UUID,                                                  │
│    uploader_id: UUID,                                              │
│    original_filename: string,                                      │
│    mime_type: string,                                              │
│    size_bytes: number,                                             │
│    bucket: "listings"|"guides"|"investments"|"kyc"|"avatars",      │
│    storage_path: string,       // MinIO object key                 │
│    cdn_url: string,            // Public or presigned URL          │
│    thumbnail_url: string | null,                                   │
│    webp_url: string | null,                                        │
│    is_public: boolean,                                             │
│    is_scanned: boolean,        // antivirus scan done             │
│    scan_result: "clean"|"threat"|"pending",                        │
│    entity_type: string | null, // "listing"|"guide"|...            │
│    entity_id: string | null,                                       │
│    uploaded_at: ISODate                                            │
│  }                                                                 │
└────────────────────────────────────────────────────────────────────┘
```

### 13.3 Service Layer — Business Logic

```python
class MediaService:

    async def upload(self, file: UploadFile, uploader_id: UUID,
                     bucket: str, entity_type: str | None,
                     entity_id: str | None) -> FileReference:
        """
        1. Validate MIME type: allowed = {image/jpeg, image/png, image/webp, application/pdf}
        2. Validate file size: images ≤ 10MB, PDFs ≤ 50MB
        3. Scan with ClamAV (async) → reject if threat
        4. Generate unique storage_path: {bucket}/{year}/{month}/{uuid}.{ext}
        5. Upload original to MinIO
        6. If image: generate thumbnail (320x240) + WebP conversion async (Celery)
        7. Insert file_references MongoDB doc
        8. Return FileReference with CDN URL
        """

    async def get_presigned_url(self, file_id: UUID, user_id: UUID,
                                 expiry_seconds: int = 3600) -> str:
        """
        For private files (e.g., KYC docs):
        1. Validate requester has permission (own file, or admin)
        2. Generate MinIO presigned GET URL with TTL
        """

    async def delete_file(self, file_id: UUID, requester_id: UUID, role: str) -> None:
        """
        1. Validate ownership or admin
        2. Delete from MinIO (original + thumbnail + webp)
        3. Soft-delete file_reference (mark deleted_at)
        4. Do NOT delete if file is referenced by active entity
        """
```

### 13.4 Controller (Router Signatures)

```python
# api/v1/files.py
media_router = APIRouter(prefix="/media", tags=["Media"])

@media_router.post("/upload",         response_model=FileReferenceResponse)
async def upload_file(
    file: UploadFile,
    bucket: Literal["listings","guides","investments","kyc","avatars"],
    entity_type: str | None = Form(None),
    entity_id: str | None = Form(None),
    current_user: JWTPayload = Depends(get_current_user)
)

@media_router.get("/{file_id}",       response_model=FileReferenceResponse)
async def get_file_info(file_id: UUID, current_user: JWTPayload = Depends(get_current_user))

@media_router.get("/{file_id}/url",   response_model=PresignedUrlResponse)
async def get_presigned_url(file_id: UUID, expiry: int = 3600,
                             current_user: JWTPayload = Depends(get_current_user))
# For private bucket files (KYC docs)

@media_router.delete("/{file_id}",    status_code=204)
async def delete_file(file_id: UUID, current_user: JWTPayload = Depends(get_current_user))

@media_router.get("/my",              response_model=PaginatedResponse[FileReferenceResponse])
async def my_files(bucket: str | None = None, page: int = 1, limit: int = 20,
                   current_user: JWTPayload = Depends(get_current_user))
```

---

## 14. Service 12 — analytics-service

### 14.1 Responsibility
Aggregated metrics, KPI dashboards (admin), user funnel analysis, content engagement (views, saves, clicks), market heatmaps, and CSV/Excel export.

### 14.2 Data Storage

```
┌────────────────────────────────────────────────────────────────────┐
│                     CLICKHOUSE (OLAP)                              │
│                                                                    │
│  Table: events                                                     │
│  (Append-only, ingested from RabbitMQ event stream)                │
│  {                                                                 │
│    event_id UUID,                                                  │
│    event_type VARCHAR,          // listing.viewed, search.done...  │
│    user_id UUID,                                                   │
│    user_role LowCardinality,                                       │
│    resource_type VARCHAR,                                          │
│    resource_id UUID,                                               │
│    city LowCardinality,                                            │
│    metadata String (JSON),                                         │
│    created_at DateTime                                             │
│  }                                                                 │
│  ENGINE = MergeTree() PARTITION BY toYYYYMM(created_at)            │
│  ORDER BY (event_type, created_at)                                 │
│                                                                    │
│  Table: daily_kpis  (materialized view aggregates)                 │
│  { date, metric, value, dimension_key, dimension_value }           │
└────────────────────────────────────────────────────────────────────┘
```

### 14.3 Controller (Router Signatures)

```python
# api/v1/analytics.py — All endpoints require admin or super_admin
analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"],
                              dependencies=[Depends(require_roles(["admin","super_admin"]))])

@analytics_router.get("/overview",        response_model=PlatformOverviewResponse)
async def platform_overview(date_from: date, date_to: date)
# Returns: total users, new registrations, active users, bookings, transactions

@analytics_router.get("/users",           response_model=UserAnalyticsResponse)
async def user_analytics(date_from: date, date_to: date,
                          group_by: Literal["day","week","month"] = "day")

@analytics_router.get("/listings",        response_model=ListingAnalyticsResponse)
async def listing_analytics(date_from: date, date_to: date, city: str | None = None)

@analytics_router.get("/bookings",        response_model=BookingAnalyticsResponse)
async def booking_analytics(date_from: date, date_to: date)

@analytics_router.get("/revenue",         response_model=RevenueAnalyticsResponse)
async def revenue_analytics(date_from: date, date_to: date,
                              group_by: Literal["day","week","month"] = "month")

@analytics_router.get("/search",          response_model=SearchAnalyticsResponse)
async def search_analytics(date_from: date, date_to: date, top_n: int = 20)
# Top queries, zero-result queries, search-to-conversion rate

@analytics_router.get("/market/heatmap",  response_model=MarketHeatmapResponse)
async def market_heatmap(listing_type: str, metric: Literal["price","views","listings"])

@analytics_router.get("/kpis",            response_model=KPIDashboardResponse)
async def kpi_dashboard()
# Pre-aggregated KPIs for admin home dashboard

@analytics_router.post("/export",         response_model=ExportJobResponse, status_code=202)
async def export_data(body: ExportRequest)
# Triggers async Celery job → emails CSV/XLSX when ready
```

---

## 15. Service 13 — admin-service

### 15.1 Responsibility
Content moderation queue, user management (ban/suspend/verify), feature flags, system configuration, platform-wide audit log, and announcement publishing.

### 15.2 ERD

```
┌────────────────────────────────────────────────────────────────────┐
│                         POSTGRESQL                                 │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     audit_log                                │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id           UUID PK                                         │  │
│  │ actor_id     UUID FK → users.id  (null if system)            │  │
│  │ action       VARCHAR  (user.suspended, listing.verified, ...) │  │
│  │ resource_type VARCHAR                                        │  │
│  │ resource_id  UUID                                            │  │
│  │ old_value    JSONB                                           │  │
│  │ new_value    JSONB                                           │  │
│  │ ip_address   VARCHAR                                         │  │
│  │ created_at   TIMESTAMPTZ                                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   moderation_queue                           │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id              UUID PK                                      │  │
│  │ resource_type   VARCHAR  (listing|guide|review|poi|          │  │
│  │                           investment|provider)               │  │
│  │ resource_id     UUID                                         │  │
│  │ reason          VARCHAR  (new_submission|user_report|        │  │
│  │                           auto_flag)                         │  │
│  │ reporter_id     UUID FK (null if system)                     │  │
│  │ status          ENUM(pending,approved,rejected,escalated)    │  │
│  │ reviewed_by     UUID FK → users.id                           │  │
│  │ review_note     TEXT                                         │  │
│  │ priority        ENUM(low,medium,high,critical)               │  │
│  │ created_at      TIMESTAMPTZ                                  │  │
│  │ reviewed_at     TIMESTAMPTZ                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   feature_flags                              │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id          UUID PK                                          │  │
│  │ flag_key    VARCHAR UNIQUE                                   │  │
│  │ is_enabled  BOOL                                             │  │
│  │ rollout_pct SMALLINT (0-100, for gradual rollout)            │  │
│  │ target_roles TEXT[]                                          │  │
│  │ description TEXT                                             │  │
│  │ updated_by  UUID FK                                          │  │
│  │ updated_at  TIMESTAMPTZ                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  announcements                               │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ id          UUID PK                                          │  │
│  │ title_ar    VARCHAR                                          │  │
│  │ title_en    VARCHAR                                          │  │
│  │ body_ar     TEXT                                             │  │
│  │ body_en     TEXT                                             │  │
│  │ target_roles TEXT[]  (null = all)                            │  │
│  │ target_cities TEXT[] (null = all)                            │  │
│  │ is_active   BOOL                                             │  │
│  │ publish_at  TIMESTAMPTZ                                      │  │
│  │ expires_at  TIMESTAMPTZ                                      │  │
│  │ created_by  UUID FK                                          │  │
│  │ created_at  TIMESTAMPTZ                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

### 15.3 Service Layer — Business Logic

```python
class ModerationService:

    async def review_item(self, queue_id: UUID, admin_id: UUID,
                           action: str, note: str | None) -> None:
        """
        action: 'approve' | 'reject' | 'escalate'
        1. Fetch moderation_queue record
        2. Update status + reviewed_by + reviewed_at
        3. If approve:
           - Call relevant service (market/guide/investment) to set is_verified=True
           - If listing: emit listing.verified → search-service re-index
        4. If reject:
           - Call relevant service to set status='rejected'
           - Emit: notification.send → resource owner with reason
        5. Write audit_log entry
        """

    async def report_content(self, reporter_id: UUID, resource_type: str,
                               resource_id: UUID, reason: str) -> None:
        """
        1. Check reporter hasn't already reported same resource (prevent spam)
        2. Insert moderation_queue record reason='user_report', priority='medium'
        3. If same resource has 3+ reports → escalate to priority='high'
        4. Notify admin team
        """
```

### 15.4 Controller (Router Signatures)

```python
# api/v1/admin.py
admin_router = APIRouter(prefix="/admin", tags=["Admin"])

# ── Moderation Queue ─────────────────────────────────────────────
@admin_router.get("/moderation",     response_model=PaginatedResponse[ModerationQueueItem])
async def list_moderation_queue(
    status: ModerationStatus | None = None,
    resource_type: str | None = None,
    priority: str | None = None,
    page: int = 1, limit: int = 50,
    current_user: JWTPayload = Depends(require_roles(["admin","super_admin"]))
)

@admin_router.get("/moderation/{queue_id}", response_model=ModerationQueueDetailItem)
async def get_moderation_item(queue_id: UUID,
                               current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

@admin_router.patch("/moderation/{queue_id}", response_model=ModerationQueueItem)
async def review_moderation_item(queue_id: UUID, body: ReviewModerationRequest,
                                  current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

# ── User Management ──────────────────────────────────────────────
@admin_router.get("/users",          response_model=PaginatedResponse[AdminUserResponse])
async def list_users(role: str | None = None, is_active: bool | None = None,
                      search: str | None = None, page: int = 1, limit: int = 50,
                      current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

@admin_router.get("/users/{user_id}", response_model=AdminUserDetailResponse)
async def get_user_detail(user_id: UUID,
                           current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

@admin_router.patch("/users/{user_id}/suspend", status_code=204)
async def suspend_user(user_id: UUID, body: SuspendUserRequest,
                        current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

@admin_router.patch("/users/{user_id}/unsuspend", status_code=204)
async def unsuspend_user(user_id: UUID,
                          current_user: JWTPayload = Depends(require_roles(["super_admin"])))

@admin_router.patch("/users/{user_id}/verify", status_code=204)
async def verify_user(user_id: UUID,
                       current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

# ── Feature Flags ────────────────────────────────────────────────
@admin_router.get("/flags",          response_model=list[FeatureFlagResponse])
async def list_feature_flags(current_user: JWTPayload = Depends(require_roles(["super_admin"])))

@admin_router.patch("/flags/{flag_key}", response_model=FeatureFlagResponse)
async def update_feature_flag(flag_key: str, body: UpdateFeatureFlagRequest,
                               current_user: JWTPayload = Depends(require_roles(["super_admin"])))

# ── Audit Log ────────────────────────────────────────────────────
@admin_router.get("/audit-log",      response_model=PaginatedResponse[AuditLogResponse])
async def get_audit_log(
    actor_id: UUID | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1, limit: int = 100,
    current_user: JWTPayload = Depends(require_roles(["super_admin"]))
)

# ── Announcements ────────────────────────────────────────────────
@admin_router.get("/announcements",  response_model=PaginatedResponse[AnnouncementResponse])
async def list_announcements(current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

@admin_router.post("/announcements", response_model=AnnouncementResponse, status_code=201)
async def create_announcement(body: CreateAnnouncementRequest,
                               current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

@admin_router.patch("/announcements/{ann_id}", response_model=AnnouncementResponse)
async def update_announcement(ann_id: UUID, body: UpdateAnnouncementRequest,
                               current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

@admin_router.delete("/announcements/{ann_id}", status_code=204)
async def delete_announcement(ann_id: UUID,
                               current_user: JWTPayload = Depends(require_roles(["admin","super_admin"])))

# ── Public: Report content (any authenticated user) ───────────────
@admin_router.post("/report",        status_code=202)
async def report_content(body: ReportContentRequest,
                          current_user: JWTPayload = Depends(get_current_user))

# ── Public: Get active announcements ─────────────────────────────
@admin_router.get("/announcements/active", response_model=list[AnnouncementResponse])
async def get_active_announcements(city: str | None = None)
# No auth required — returns current platform announcements
```

---

## 16. Inter-Service Event Catalog

### 16.1 RabbitMQ Exchange & Routing Keys

```
Exchange: platform.events  (type: topic, durable: true)

Routing Key Pattern: {service}.{entity}.{action}

┌────────────────────────────────────────────────────────────────────┐
│                      EVENT CATALOG                                 │
├───────────────────────────┬────────────────────┬───────────────────┤
│ Routing Key               │ Producer           │ Consumers         │
├───────────────────────────┼────────────────────┼───────────────────┤
│ auth.user.created         │ auth-service        │ notification(welcome)│
│                           │                    │ user-service(profile) │
│ auth.user.role_changed    │ auth-service        │ notification, admin   │
│ user.profile.updated      │ user-service        │ search-service        │
│ user.kyc.submitted        │ user-service        │ admin-service(queue)  │
│ user.kyc.approved         │ admin-service       │ notification, user    │
├───────────────────────────┼────────────────────┼───────────────────┤
│ market.listing.created    │ market-service      │ search, map, notif    │
│ market.listing.updated    │ market-service      │ search(re-index)      │
│ market.listing.verified   │ admin-service       │ search, notif(owner)  │
│ market.price.updated      │ market-service      │ notif(price alerts)   │
│ market.b2b.inquiry        │ market-service      │ notif(business owner) │
├───────────────────────────┼────────────────────┼───────────────────┤
│ guide.booking.requested   │ guide-service       │ notif(guide), payment │
│ guide.booking.confirmed   │ guide-service       │ notif(tourist), pay   │
│ guide.booking.completed   │ guide-service       │ payment(release),notif│
│ guide.booking.cancelled   │ guide-service       │ payment(refund), notif│
│ guide.review.submitted    │ guide-service       │ search(re-index),notif│
├───────────────────────────┼────────────────────┼───────────────────┤
│ invest.opportunity.created│ invest-service      │ search, notif(watchl) │
│ invest.opportunity.verified│ admin-service      │ search, notif(owner)  │
│ invest.interest.submitted │ invest-service      │ notif(opp owner)      │
│ invest.interest.accepted  │ invest-service      │ notif(investor)       │
├───────────────────────────┼────────────────────┼───────────────────┤
│ payment.booking.held      │ payment-service     │ guide(confirm ok)     │
│ payment.booking.released  │ payment-service     │ notif(guide paid)     │
│ payment.refund.processed  │ payment-service     │ notif(tourist)        │
├───────────────────────────┼────────────────────┼───────────────────┤
│ map.poi.created           │ map-service         │ search(index)         │
│ map.carpool.posted        │ map-service         │ notif(nearby users)   │
├───────────────────────────┼────────────────────┼───────────────────┤
│ admin.content.flagged     │ admin-service       │ notif(moderators)     │
│ admin.user.suspended      │ admin-service       │ auth(revoke tokens)   │
└───────────────────────────┴────────────────────┴───────────────────┘
```

### 16.2 Event Payload Standard

```python
# All events follow this envelope:
{
  "event_id": "uuid-v4",
  "routing_key": "market.listing.created",
  "version": "1.0",
  "occurred_at": "2026-02-06T10:30:00Z",
  "producer": "market-service",
  "correlation_id": "request-id from original HTTP call",
  "payload": {
    # Event-specific data
  }
}
```

### 16.3 Celery Async Jobs Reference

| Task Name | Service | Trigger | Schedule |
|-----------|---------|---------|----------|
| `refresh_price_index` | market-service | Cron | Every 30min |
| `reindex_search` | search-service | Event `*.updated` | On-event + nightly |
| `send_digest_email` | notification-service | Cron | Daily 08:00 |
| `process_withdrawal` | payment-service | Manual + Cron | Every 6hr |
| `embed_new_documents` | ai-service | Event `*.created` | On-event |
| `generate_daily_report` | analytics-service | Cron | Daily 00:00 |
| `cleanup_expired_sessions` | auth-service | Cron | Hourly |
| `convert_images_to_webp` | media-service | Event `media.uploaded` | On-event |
| `expire_old_listings` | market-service | Cron | Daily 00:00 |
| `send_booking_reminders` | guide-service | Cron | Every 15min |
| `auto_cancel_unconfirmed_bookings` | guide-service | Cron | Every 30min |
| `backup_databases` | infra | Cron | Nightly 02:00 |

---

## Summary: Complete Endpoint Count

| Service | Public | Authenticated | Role-Restricted | Admin-Only | Internal |
|---------|--------|--------------|-----------------|------------|----------|
| auth-service | 8 | 2 | 0 | 0 | 1 |
| user-service | 1 | 5 | 3 (KYC) | 4 | 0 |
| map-service | 4 | 9 | 0 | 2 | 0 |
| market-service | 4 | 8 | 3 | 2 | 0 |
| guide-service | 3 | 10 | 3 (guide-only) | 1 | 0 |
| investment-service | 1 | 8 | 4 (investor) | 2 | 0 |
| payment-service | 0 | 8 | 2 (guide/merchant) | 0 | 2 |
| notification-service | 0 | 7 | 0 | 2 | 1 |
| search-service | 7 | 0 | 0 | 0 | 3 |
| ai-service | 2 | 8 | 1 (investor) | 2 | 0 |
| media-service | 0 | 5 | 0 | 0 | 0 |
| analytics-service | 0 | 0 | 0 | 9 | 0 |
| admin-service | 2 | 1 | 0 | 12 | 0 |
| **Total** | **32** | **71** | **16** | **36** | **7** |

---

*Built by Dev-X for هنا وادينا · الوادي الجديد، الخارجة، مصر*  
*Blueprint Version 1.0 — 2026-02-06*
