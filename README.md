# هنا وادينا — Hena Wadeena
## Complete Software Architecture Plan
> Microservices · RBAC · Databases · Messaging · Notifications · AI/ML

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Technology Choices & Justification](#2-technology-choices--justification)
3. [Services Breakdown](#3-services-breakdown)
4. [Role-Based Access Control (RBAC)](#4-role-based-access-control-rbac)
5. [Role × Service Action Matrix](#5-role--service-action-matrix)
6. [Database Design per Service](#6-database-design-per-service)
7. [Event Bus & Inter-Service Messaging](#7-event-bus--inter-service-messaging)
8. [Notification System](#8-notification-system)
9. [API Gateway Layer](#9-api-gateway-layer)
10. [Auth & Identity Service](#10-auth--identity-service)
11. [AI/ML Services](#11-aiml-services)
12. [Search & Indexing Service](#12-search--indexing-service)
13. [Async Jobs & Background Processing](#13-async-jobs--background-processing)
14. [Frontend Architecture (React)](#14-frontend-architecture-react)
15. [Observability Stack](#15-observability-stack)
16. [CI/CD Pipeline](#16-cicd-pipeline)
17. [Full Architecture Diagram (Textual)](#17-full-architecture-diagram-textual)

---

## 1. System Overview

**Hena Wadeena** is a regional intelligence platform for the New Valley (الوادي الجديد), Egypt. It aggregates tourism, investment, real estate, transport, and local service data into a unified, AI-assisted experience.

### User Segments (Actors)

| Role | Arabic | Primary Need |
|---|---|---|
| `tourist` | سائح | Navigation, accommodation, guides, carpooling |
| `student` | طالب | Housing, daily services, affordability data |
| `investor` | مستثمر | Market prices, land opportunities, B2B matching |
| `local_citizen` | مواطن محلي | Local services, community, daily utility |
| `guide` | دليل سياحي | Profile management, booking reception, earnings |
| `merchant` | تاجر / صاحب نشاط | Business listing, product/service promotion |
| `admin` | مشرف | Platform moderation, data validation, analytics |
| `super_admin` | مدير النظام | Full system control, configuration, billing |

---

## 2. Technology Choices & Justification

### Core Stack Decision Table

| Layer | Technology | Why |
|---|---|---|
| **Frontend** | React + Vite + TailwindCSS | SPA, rich interactivity, component reuse across web/mobile-web |
| **Mobile** | React Native (Expo) | Code sharing with React web, reduced team context-switching |
| **API Gateway** | Kong (self-hosted) | Plugin ecosystem: auth, rate-limiting, routing, logging out of box |
| **Auth** | Keycloak | Open-source, OIDC/OAuth2, role mapping, Arabic UI support |
| **Primary Backend** | FastAPI (Python) | Async, fast, native Pydantic validation, AI/ML ecosystem compatibility |
| **Secondary Services** | Node.js (Express) | Real-time WebSocket heavy services (maps, chat) |
| **Message Broker** | RabbitMQ | Simpler than Kafka for this scale; reliable queues, dead-letter support |
| **Task Queue** | Celery + Redis | Python-native, Cron-like scheduling, integrates with FastAPI |
| **Primary DB** | PostgreSQL 16 | ACID, PostGIS for geo, JSONB for flexibility, mature |
| **Document DB** | MongoDB | Activity logs, guide profiles, content with variable schema |
| **Cache** | Redis 7 | Sessions, rate limiting, hot data (market prices) |
| **Search** | Meilisearch | Arabic-friendly tokenization, fast, simpler ops than Elasticsearch |
| **Object Storage** | MinIO (S3-compatible) | Self-hosted, images/documents/attachments |
| **Maps** | Google Maps API + OpenStreetMap (Leaflet fallback) | Official POI data + offline capability |
| **Email** | Resend | Simple REST API, high deliverability |
| **SMS** | Vonage / Twilio | Egyptian number support, OTP delivery |
| **Push Notifications** | Firebase Cloud Messaging (FCM) | Web + Android + iOS unified |
| **Realtime** | Soketi (Pusher-compatible, self-hosted) | WebSocket for live map updates, notifications |
| **Observability** | Prometheus + Grafana + Loki | Full metrics, logs, alerts stack |
| **CI/CD** | GitHub Actions + ArgoCD | GitOps model, Kubernetes deployment |
| **Container Orchestration** | Kubernetes (K3s) | Lightweight for regional deployment, cost-efficient |
| **AI / LLM** | OpenAI GPT-4o API + local Ollama fallback | Chatbot, RAG; fallback for offline/cost scenarios |
| **Vector DB** | Qdrant | RAG embeddings storage, Arabic text retrieval |
| **Embedding Model** | OpenAI `text-embedding-3-small` | Arabic support, cost-efficient |

---

## 3. Services Breakdown

The platform is decomposed into **9 core microservices** + **4 support services**.

```
Core Services:
  1.  auth-service            Identity, JWT, sessions, OAuth2
  2.  user-service            Profiles, preferences, KYC
  3.  map-service             Navigation, POI, carpooling
  4.  market-service          Real estate prices, B2B directory, land
  5.  guide-service           Tourist guides, bookings, reviews
  6.  investment-service      Opportunities, projects, applications
  7.  payment-service         Transactions, wallets, payouts
  8.  notification-service    Push, email, SMS, in-app alerts
  9.  search-service          Full-text, geo, faceted search

Support Services:
  10. ai-service              Chatbot (RAG), recommendations, analytics
  11. media-service           Upload, resize, CDN proxy (MinIO)
  12. analytics-service       Aggregated reporting, KPI dashboards
  13. admin-service           Moderation, config, audit log
```

### 3.1 Service Ownership Map

```
auth-service
  ├── JWT issuance & validation
  ├── OAuth2 (Google, Apple sign-in)
  ├── OTP (SMS via Vonage)
  ├── Password reset flows
  └── Keycloak integration bridge

user-service
  ├── Profile CRUD (all roles)
  ├── Role assignment
  ├── Preferences (language, notifications)
  ├── KYC document upload (investors/guides)
  └── Activity history

map-service
  ├── Points of Interest (POI) CRUD
  ├── Route calculation (Google Maps API proxy)
  ├── Carpooling: post ride, find ride, match
  ├── Live driver location (WebSocket via Soketi)
  └── Offline map tile caching

market-service
  ├── Real estate listings (buy/rent/land)
  ├── Price index by area + property type
  ├── Business directory (B2B)
  ├── Merchant shop management
  ├── Market analytics (price trends)
  └── Featured listing management

guide-service
  ├── Guide profile + availability calendar
  ├── Tour package creation
  ├── Booking workflow (request → confirm → complete)
  ├── Review & rating system
  └── Earnings ledger

investment-service
  ├── Opportunity listings (projects, land, ventures)
  ├── Application / Expression of Interest submission
  ├── Due diligence document room
  ├── Investor-founder matching
  └── Status tracking (pipeline)

payment-service
  ├── Wallet (deposit, balance, withdraw)
  ├── Booking payments (escrow → release)
  ├── Subscription billing (guide/merchant plans)
  ├── Payout processing (guide earnings)
  ├── Payment gateway integration (Paymob for Egypt)
  └── Transaction history & receipts

notification-service
  ├── Push (FCM)
  ├── In-app (stored, read/unread)
  ├── Email (Resend)
  ├── SMS (Vonage)
  ├── Notification preferences per user
  └── Broadcast / campaign management

search-service
  ├── Unified search across all content types
  ├── Geo-search (nearby POI, listings)
  ├── Faceted filters (price, category, location)
  ├── Autocomplete
  ├── Index sync (listens to domain events)
  └── Arabic + transliteration support

ai-service
  ├── Chatbot assistant (RAG over platform content)
  ├── Recommendation engine (guides, listings, POI)
  ├── Price prediction model
  ├── Sentiment analysis on reviews
  └── Content moderation (text/image)

media-service
  ├── Image/document upload (MinIO)
  ├── Image resizing & format conversion (WebP)
  ├── CDN URL generation (presigned)
  └── Virus scanning on upload

analytics-service
  ├── User funnel metrics
  ├── Content engagement (views, saves, clicks)
  ├── Market heatmaps
  ├── KPI dashboard data (for admin)
  └── Export (CSV/Excel)

admin-service
  ├── Content moderation queue
  ├── User ban / suspend / verify
  ├── Feature flags management
  ├── System configuration
  └── Full audit log
```

---

## 4. Role-Based Access Control (RBAC)

### 4.1 Role Hierarchy

```
super_admin
    └── admin
            ├── merchant
            ├── guide
            ├── investor
            ├── student
            └── tourist
                    └── local_citizen  (same permissions as tourist)
```

### 4.2 Role Definitions

```yaml
roles:
  tourist:
    description: Default role for all visitors / travelers
    requires_verification: false
    can_self_register: true

  student:
    description: Registered students seeking housing/services
    requires_verification: true   # student ID required
    can_self_register: true

  investor:
    description: Business/real-estate investors
    requires_verification: true   # national ID + business doc
    can_self_register: true
    has_wallet: true

  local_citizen:
    description: Residents of New Valley
    requires_verification: false
    can_self_register: true

  guide:
    description: Licensed local tour guides
    requires_verification: true   # license + ID
    can_self_register: true
    has_wallet: true            # receives payments

  merchant:
    description: Business owners with listings
    requires_verification: true   # commercial register
    can_self_register: true
    has_wallet: true

  admin:
    description: Platform operations team
    requires_verification: true
    assigned_by: super_admin

  super_admin:
    description: Full system control
    assigned_by: system_seed
```

### 4.3 Permission Taxonomy

Permissions follow the pattern: `resource:action`

```
Verbs:    read | create | update | delete | manage | publish | moderate
Resources: profile, listing, guide, booking, payment, review, investment,
           carpool, notification, report, config, user, media
```

---

## 5. Role × Service Action Matrix

### 5.1 User Service

| Action | tourist | student | investor | local | guide | merchant | admin |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Read own profile | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Update own profile | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Upload KYC documents | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| Read any user profile | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Ban / Suspend user | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Change user role | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Delete account (self) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### 5.2 Map Service

| Action | tourist | student | investor | local | guide | merchant | admin |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| View map & POIs | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Get directions | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Post carpool ride | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Join carpool ride | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Add POI (suggest) | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Approve POI | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Add merchant pin | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |

### 5.3 Market Service

| Action | tourist | student | investor | local | guide | merchant | admin |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Browse listings | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View price index | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View detailed analytics | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| Create listing | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Edit own listing | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Delete own listing | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Feature listing (pay) | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ |
| Moderate any listing | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Export price data | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |

### 5.4 Guide Service

| Action | tourist | student | investor | local | guide | merchant | admin |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Browse guides | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View guide profile | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Request booking | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage own bookings | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Create tour package | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Write review (post-trip) | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Reply to review | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Verify guide license | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

### 5.5 Investment Service

| Action | tourist | student | investor | local | guide | merchant | admin |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Browse opportunities | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ |
| View opportunity detail | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| Submit expression of interest | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ |
| Post opportunity | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| Upload due diligence docs | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| Approve opportunity listing | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| View full investor directory | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |

### 5.6 Payment Service

| Action | tourist | student | investor | local | guide | merchant | admin |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| View own wallet | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Top up wallet | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Pay for booking | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Pay for subscription | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ |
| Request payout | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| Approve payout | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| View all transactions | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Issue refund | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

### 5.7 Notification Service

| Action | tourist | student | investor | local | guide | merchant | admin |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Read own notifications | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Mark read / dismiss | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Update own preferences | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Send broadcast | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Send targeted campaign | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 6. Database Design per Service

### Design Principle
Each service owns its data. **No cross-service DB joins**. Data needed across services is replicated via events or fetched through APIs.

---

### 6.1 Auth Service → PostgreSQL

```sql
-- Sessions & tokens
CREATE TABLE refresh_tokens (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL,
  token_hash  TEXT NOT NULL UNIQUE,
  device_id   TEXT,
  ip_address  INET,
  expires_at  TIMESTAMPTZ NOT NULL,
  revoked_at  TIMESTAMPTZ,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- OTP codes
CREATE TABLE otp_codes (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  target      TEXT NOT NULL,         -- phone or email
  purpose     TEXT NOT NULL,         -- 'login' | 'reset' | 'verify'
  code_hash   TEXT NOT NULL,
  expires_at  TIMESTAMPTZ NOT NULL,
  used_at     TIMESTAMPTZ,
  attempts    SMALLINT DEFAULT 0
);

-- Audit log
CREATE TABLE auth_events (
  id         BIGSERIAL PRIMARY KEY,
  user_id    UUID,
  event_type TEXT NOT NULL,          -- 'login' | 'logout' | 'failed'
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Redis keys for auth:**
```
session:{user_id}            → JSON session data, TTL 24h
blacklist:token:{jti}        → "1", TTL = token expiry
otp:rate:{phone}             → counter, TTL 1h (rate limiting)
```

---

### 6.2 User Service → PostgreSQL

```sql
CREATE TABLE users (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email           TEXT UNIQUE,
  phone           TEXT UNIQUE,
  full_name       TEXT NOT NULL,
  display_name    TEXT,
  avatar_url      TEXT,
  role            TEXT NOT NULL DEFAULT 'tourist',
  status          TEXT NOT NULL DEFAULT 'active',  -- active|suspended|banned
  language        TEXT DEFAULT 'ar',               -- ar | en
  verified_at     TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_kyc (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
  doc_type      TEXT NOT NULL,    -- 'national_id' | 'student_id' | 'guide_license'
  doc_url       TEXT NOT NULL,    -- MinIO presigned path
  status        TEXT DEFAULT 'pending',  -- pending|approved|rejected
  reviewed_by   UUID,
  reviewed_at   TIMESTAMPTZ,
  rejection_reason TEXT
);

CREATE TABLE user_preferences (
  user_id              UUID PRIMARY KEY REFERENCES users(id),
  notify_push          BOOLEAN DEFAULT TRUE,
  notify_email         BOOLEAN DEFAULT TRUE,
  notify_sms           BOOLEAN DEFAULT FALSE,
  preferred_areas      TEXT[],    -- array of area slugs
  interests            TEXT[]     -- 'tourism' | 'investment' | 'real_estate'
);

CREATE TABLE saved_items (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES users(id),
  item_type   TEXT NOT NULL,    -- 'listing' | 'guide' | 'poi' | 'opportunity'
  item_id     UUID NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, item_type, item_id)
);
```

---

### 6.3 Map Service → PostgreSQL + PostGIS

```sql
-- Enable PostGIS
CREATE EXTENSION postgis;

CREATE TABLE points_of_interest (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name_ar      TEXT NOT NULL,
  name_en      TEXT,
  description  TEXT,
  category     TEXT NOT NULL,   -- 'hotel' | 'restaurant' | 'landmark' | 'government'
  location     GEOGRAPHY(POINT, 4326) NOT NULL,
  address      TEXT,
  phone        TEXT,
  website      TEXT,
  images       TEXT[],
  rating_avg   NUMERIC(3,2) DEFAULT 0,
  rating_count INT DEFAULT 0,
  status       TEXT DEFAULT 'pending',  -- pending | approved | rejected
  submitted_by UUID,
  approved_by  UUID,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Spatial index
CREATE INDEX poi_location_idx ON points_of_interest USING GIST(location);

CREATE TABLE carpool_rides (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  driver_id       UUID NOT NULL,
  origin          GEOGRAPHY(POINT, 4326) NOT NULL,
  destination     GEOGRAPHY(POINT, 4326) NOT NULL,
  origin_name     TEXT,
  destination_name TEXT,
  departure_time  TIMESTAMPTZ NOT NULL,
  seats_total     SMALLINT NOT NULL,
  seats_taken     SMALLINT DEFAULT 0,
  price_per_seat  NUMERIC(10,2),
  notes           TEXT,
  status          TEXT DEFAULT 'open',   -- open | full | cancelled | completed
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE carpool_passengers (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ride_id    UUID REFERENCES carpool_rides(id),
  user_id    UUID NOT NULL,
  seats      SMALLINT DEFAULT 1,
  status     TEXT DEFAULT 'pending',  -- pending | confirmed | cancelled
  joined_at  TIMESTAMPTZ DEFAULT NOW()
);
```

**Redis for live location:**
```
driver:location:{driver_id}    → {lat, lng, updated_at}, TTL 30s
active:rides                   → SET of active ride_ids
```

---

### 6.4 Market Service → PostgreSQL + MongoDB

**PostgreSQL** (structured, ACID listings):
```sql
CREATE TABLE listings (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id        UUID NOT NULL,
  listing_type    TEXT NOT NULL,    -- 'real_estate' | 'land' | 'business'
  transaction     TEXT NOT NULL,    -- 'sale' | 'rent'
  title_ar        TEXT NOT NULL,
  title_en        TEXT,
  description     TEXT,
  price           NUMERIC(14,2) NOT NULL,
  price_unit      TEXT DEFAULT 'EGP',
  area_sqm        NUMERIC(10,2),
  location        GEOGRAPHY(POINT, 4326),
  address         TEXT,
  city            TEXT DEFAULT 'الوادي الجديد',
  district        TEXT,
  images          TEXT[],
  features        JSONB,            -- {'rooms': 3, 'bathrooms': 2, 'floor': 1}
  status          TEXT DEFAULT 'draft',  -- draft|active|sold|suspended
  featured_until  TIMESTAMPTZ,
  views_count     INT DEFAULT 0,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX listings_location_idx ON listings USING GIST(location);
CREATE INDEX listings_status_idx ON listings(status);
CREATE INDEX listings_type_idx ON listings(listing_type, transaction);

-- Price index (aggregated)
CREATE TABLE price_snapshots (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  district     TEXT NOT NULL,
  listing_type TEXT NOT NULL,
  avg_price    NUMERIC(14,2),
  min_price    NUMERIC(14,2),
  max_price    NUMERIC(14,2),
  sample_count INT,
  snapshot_date DATE NOT NULL,
  UNIQUE(district, listing_type, snapshot_date)
);

CREATE TABLE business_directory (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id    UUID NOT NULL,
  name_ar     TEXT NOT NULL,
  name_en     TEXT,
  category    TEXT,
  description TEXT,
  location    GEOGRAPHY(POINT, 4326),
  phone       TEXT,
  website     TEXT,
  logo_url    TEXT,
  status      TEXT DEFAULT 'active',
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

**MongoDB** (activity logs, market events):
```javascript
// Collection: listing_views
{
  listing_id: "uuid",
  viewer_id: "uuid",        // null for anonymous
  ip: "1.2.3.4",
  viewed_at: ISODate(),
  source: "search | map | direct"
}

// Collection: price_history  
{
  listing_id: "uuid",
  price: 500000,
  changed_at: ISODate(),
  changed_by: "uuid"
}
```

---

### 6.5 Guide Service → PostgreSQL

```sql
CREATE TABLE guides (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID UNIQUE NOT NULL,
  bio_ar          TEXT,
  bio_en          TEXT,
  languages       TEXT[],            -- ['ar', 'en', 'fr']
  specialties     TEXT[],            -- ['history', 'desert', 'archaeology']
  license_number  TEXT UNIQUE,
  license_verified BOOLEAN DEFAULT FALSE,
  base_price      NUMERIC(10,2),
  currency        TEXT DEFAULT 'EGP',
  rating_avg      NUMERIC(3,2) DEFAULT 0,
  rating_count    INT DEFAULT 0,
  active          BOOLEAN DEFAULT TRUE
);

CREATE TABLE tour_packages (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  guide_id     UUID REFERENCES guides(id),
  title_ar     TEXT NOT NULL,
  title_en     TEXT,
  description  TEXT,
  duration_hrs NUMERIC(4,1),
  max_people   SMALLINT,
  price        NUMERIC(10,2) NOT NULL,
  includes     TEXT[],
  images       TEXT[],
  status       TEXT DEFAULT 'active'
);

CREATE TABLE bookings (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  package_id     UUID REFERENCES tour_packages(id),
  guide_id       UUID REFERENCES guides(id),
  tourist_id     UUID NOT NULL,
  booking_date   DATE NOT NULL,
  start_time     TIME NOT NULL,
  people_count   SMALLINT NOT NULL,
  total_price    NUMERIC(10,2) NOT NULL,
  status         TEXT DEFAULT 'pending',
  -- pending | confirmed | in_progress | completed | cancelled | refunded
  payment_ref    UUID,                     -- payment-service transaction ID
  notes          TEXT,
  cancelled_at   TIMESTAMPTZ,
  cancel_reason  TEXT,
  created_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE reviews (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id  UUID REFERENCES bookings(id) UNIQUE,
  guide_id    UUID REFERENCES guides(id),
  tourist_id  UUID NOT NULL,
  rating      SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  comment     TEXT,
  guide_reply TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE guide_availability (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  guide_id   UUID REFERENCES guides(id),
  date       DATE NOT NULL,
  is_blocked BOOLEAN DEFAULT FALSE,
  note       TEXT,
  UNIQUE(guide_id, date)
);
```

---

### 6.6 Investment Service → PostgreSQL + MongoDB

```sql
CREATE TABLE opportunities (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id         UUID NOT NULL,
  title_ar         TEXT NOT NULL,
  title_en         TEXT,
  description      TEXT,
  category         TEXT,    -- 'agriculture' | 'tourism' | 'real_estate' | 'industry'
  min_investment   NUMERIC(14,2),
  max_investment   NUMERIC(14,2),
  currency         TEXT DEFAULT 'EGP',
  location         GEOGRAPHY(POINT, 4326),
  district         TEXT,
  documents        TEXT[],     -- MinIO URLs for due diligence
  status           TEXT DEFAULT 'draft',  -- draft|review|active|closed
  expires_at       DATE,
  approved_by      UUID,
  approved_at      TIMESTAMPTZ,
  created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE investment_applications (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  opportunity_id    UUID REFERENCES opportunities(id),
  investor_id       UUID NOT NULL,
  amount_proposed   NUMERIC(14,2),
  message           TEXT,
  documents         TEXT[],
  status            TEXT DEFAULT 'pending',
  -- pending | reviewed | accepted | rejected | withdrawn
  created_at        TIMESTAMPTZ DEFAULT NOW()
);
```

**MongoDB** (document room, due diligence):
```javascript
// Collection: due_diligence_rooms
{
  opportunity_id: "uuid",
  investor_id: "uuid",
  documents: [
    { name: "Business Plan.pdf", url: "minio://...", uploaded_at: ISODate() }
  ],
  notes: "...",
  last_accessed: ISODate()
}
```

---

### 6.7 Payment Service → PostgreSQL

```sql
CREATE TABLE wallets (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID UNIQUE NOT NULL,
  balance      NUMERIC(14,2) DEFAULT 0.00,
  currency     TEXT DEFAULT 'EGP',
  updated_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE transactions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  wallet_id       UUID REFERENCES wallets(id),
  type            TEXT NOT NULL,
  -- 'topup' | 'booking_pay' | 'payout' | 'refund' | 'subscription' | 'escrow_hold' | 'escrow_release'
  amount          NUMERIC(14,2) NOT NULL,
  direction       TEXT NOT NULL,     -- 'credit' | 'debit'
  balance_after   NUMERIC(14,2) NOT NULL,
  reference_type  TEXT,              -- 'booking' | 'subscription' | 'topup'
  reference_id    UUID,
  gateway_ref     TEXT,              -- Paymob transaction ID
  status          TEXT DEFAULT 'pending',   -- pending|completed|failed|reversed
  description     TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE escrow (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  payer_id        UUID NOT NULL,
  payee_id        UUID NOT NULL,
  amount          NUMERIC(14,2) NOT NULL,
  reference_type  TEXT NOT NULL,    -- 'booking'
  reference_id    UUID NOT NULL,
  status          TEXT DEFAULT 'held',  -- held | released | refunded
  held_at         TIMESTAMPTZ DEFAULT NOW(),
  released_at     TIMESTAMPTZ
);

CREATE TABLE subscriptions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL,
  plan_type       TEXT NOT NULL,    -- 'guide_basic' | 'guide_pro' | 'merchant_featured'
  price           NUMERIC(10,2),
  status          TEXT DEFAULT 'active',
  current_period_start  DATE,
  current_period_end    DATE,
  cancelled_at    TIMESTAMPTZ
);

CREATE TABLE payout_requests (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL,
  amount          NUMERIC(14,2) NOT NULL,
  bank_account    TEXT,
  instapay_phone  TEXT,
  status          TEXT DEFAULT 'pending',    -- pending | approved | paid | rejected
  processed_by    UUID,
  processed_at    TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 6.8 Notification Service → PostgreSQL + Redis

```sql
CREATE TABLE notifications (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID NOT NULL,
  type         TEXT NOT NULL,
  -- 'booking_confirmed' | 'payment_received' | 'new_message' | 'system' | ...
  title_ar     TEXT,
  title_en     TEXT,
  body_ar      TEXT,
  body_en      TEXT,
  data         JSONB,           -- extra context (booking_id, amount, etc.)
  channel      TEXT[],         -- ['push', 'email', 'sms', 'in_app']
  read_at      TIMESTAMPTZ,
  sent_at      TIMESTAMPTZ,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX notif_user_unread_idx ON notifications(user_id, read_at)
  WHERE read_at IS NULL;

CREATE TABLE notification_campaigns (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title        TEXT,
  body_ar      TEXT,
  body_en      TEXT,
  target_roles TEXT[],         -- broadcast to specific roles
  channel      TEXT[],
  status       TEXT DEFAULT 'draft',
  scheduled_at TIMESTAMPTZ,
  sent_at      TIMESTAMPTZ,
  created_by   UUID
);
```

**Redis:**
```
unread_count:{user_id}         → integer, updated on write/read
device_tokens:{user_id}        → SET of FCM tokens
push:batch:queue               → list for batched FCM delivery
```

---

### 6.9 Search Service → Meilisearch

Meilisearch indexes (each a separate index):

```json
// Index: pois
{
  "uid": "pois",
  "primaryKey": "id",
  "searchableAttributes": ["name_ar", "name_en", "category", "address"],
  "filterableAttributes": ["category", "city", "district", "status"],
  "sortableAttributes": ["rating_avg", "created_at"],
  "rankingRules": ["words", "typo", "proximity", "attribute", "sort", "exactness"]
}

// Index: listings
{
  "uid": "listings",
  "primaryKey": "id",
  "searchableAttributes": ["title_ar", "title_en", "description", "district", "address"],
  "filterableAttributes": ["listing_type", "transaction", "district", "status", "price"],
  "sortableAttributes": ["price", "created_at", "views_count"],
  "pagination": { "maxTotalHits": 5000 }
}

// Index: guides
{
  "uid": "guides",
  "primaryKey": "id",
  "searchableAttributes": ["bio_ar", "bio_en", "specialties", "languages"],
  "filterableAttributes": ["languages", "specialties", "license_verified"],
  "sortableAttributes": ["rating_avg", "base_price"]
}

// Index: opportunities
{
  "uid": "opportunities",
  "primaryKey": "id",
  "searchableAttributes": ["title_ar", "title_en", "description", "category", "district"],
  "filterableAttributes": ["category", "district", "status", "min_investment", "max_investment"],
  "sortableAttributes": ["min_investment", "created_at"]
}
```

---

### 6.10 AI Service → Qdrant (Vector DB)

```python
# Qdrant collection for RAG
{
  "name": "platform_knowledge",
  "vectors": {
    "size": 1536,                    # OpenAI text-embedding-3-small
    "distance": "Cosine"
  },
  "payload_schema": {
    "source_type": "keyword",        # 'poi' | 'listing' | 'guide' | 'faq'
    "source_id": "keyword",
    "language": "keyword",           # 'ar' | 'en'
    "district": "keyword"
  }
}

# Each vector entry
{
  "id": "uuid",
  "vector": [0.01, 0.44, ...],      # embedding of the text
  "payload": {
    "source_type": "poi",
    "source_id": "poi-uuid",
    "text": "معبد هيبس في الخارجة...",
    "language": "ar",
    "district": "الخارجة",
    "updated_at": "2026-03-07"
  }
}
```

---

## 7. Event Bus & Inter-Service Messaging

### 7.1 Why RabbitMQ over Kafka

For Hena Wadeena's current scale (thousands → tens of thousands of users), RabbitMQ is preferred:
- Simpler operational overhead (no ZooKeeper/KRaft management)
- Native dead-letter queues for failed message handling
- Built-in management UI
- Per-message TTL and routing flexibility
- Sufficient throughput (up to ~50K msg/sec)

Kafka becomes relevant when daily events exceed ~10 million. This can be revisited at scale.

### 7.2 Exchange Topology

```
Exchanges (topic type):
  platform.users         → user lifecycle events
  platform.listings      → market listing events
  platform.bookings      → guide booking events
  platform.payments      → payment events
  platform.notifications → notification dispatch events
  platform.search        → index sync events (fan-out)
  platform.ai            → AI processing triggers

Queues per consumer:
  notification-service.users      ← platform.users (routing: user.*)
  search-service.listings         ← platform.listings (routing: listing.*)
  search-service.guides           ← platform.bookings (routing: guide.*)
  ai-service.embeddings           ← platform.search (routing: index.*)
  payment-service.bookings        ← platform.bookings (routing: booking.confirmed)
  analytics-service.all           ← all exchanges (fan-out binding)
```

### 7.3 Event Catalog

Every event follows this envelope:

```json
{
  "event_id": "uuid",
  "event_type": "booking.confirmed",
  "version": "1.0",
  "timestamp": "2026-03-07T10:00:00Z",
  "source_service": "guide-service",
  "correlation_id": "request-trace-id",
  "data": { ... }
}
```

**Full event list:**

```
USER EVENTS (platform.users)
  user.registered           → { user_id, role, email, phone }
  user.verified             → { user_id, verification_type }
  user.suspended            → { user_id, reason }
  user.deleted              → { user_id }
  user.role_changed         → { user_id, old_role, new_role }

MARKET EVENTS (platform.listings)
  listing.created           → { listing_id, owner_id, type, price, district }
  listing.updated           → { listing_id, changed_fields }
  listing.status_changed    → { listing_id, old_status, new_status }
  listing.view              → { listing_id, viewer_id }
  listing.saved             → { listing_id, user_id }

BOOKING EVENTS (platform.bookings)
  booking.requested         → { booking_id, guide_id, tourist_id, date, amount }
  booking.confirmed         → { booking_id, guide_id, tourist_id, amount }
  booking.cancelled         → { booking_id, initiator_id, reason }
  booking.completed         → { booking_id }
  review.submitted          → { review_id, guide_id, rating }

PAYMENT EVENTS (platform.payments)
  payment.completed         → { transaction_id, user_id, amount, reference_type, reference_id }
  payment.failed            → { transaction_id, user_id, reason }
  escrow.held               → { escrow_id, payer_id, payee_id, amount }
  escrow.released           → { escrow_id, payee_id, amount }
  payout.processed          → { payout_id, user_id, amount }
  wallet.topped_up          → { user_id, amount, new_balance }

NOTIFICATION EVENTS (platform.notifications)
  notification.send         → { user_id, type, channels, title_ar, body_ar, data }
  notification.broadcast    → { role_filter, type, channels, content }

SEARCH SYNC EVENTS (platform.search)
  index.listing.upsert      → { listing_id, data }
  index.listing.delete      → { listing_id }
  index.guide.upsert        → { guide_id, data }
  index.poi.upsert          → { poi_id, data }
  index.opportunity.upsert  → { opportunity_id, data }
```

### 7.4 Dead Letter Queue Strategy

```
For every queue:
  x-dead-letter-exchange: platform.dlx
  x-message-ttl: 30000          (30s before DLQ)
  x-max-retries: 3

DLQ processor:
  - Logs failed message with context
  - Alerts admin via notification-service
  - Stores in MongoDB for manual review
  - Supports replay with admin trigger
```

---

## 8. Notification System

### 8.1 Architecture

```
Domain Services
    │
    ├── emit event: notification.send → RabbitMQ
    │
    └── notification-service (consumer)
              │
              ├── Determine channels from user preferences
              ├── Render template (AR/EN based on user lang)
              │
              ├── push   → FCM (Firebase)
              ├── email  → Resend
              ├── sms    → Vonage
              └── in_app → store in PostgreSQL + push via Soketi WebSocket
```

### 8.2 Notification Types & Channels

| Event | Push | Email | SMS | In-App |
|---|:---:|:---:|:---:|:---:|
| Booking requested (guide) | ✅ | ✅ | ✅ | ✅ |
| Booking confirmed (tourist) | ✅ | ✅ | ✅ | ✅ |
| Booking cancelled | ✅ | ✅ | ✅ | ✅ |
| Payment received | ✅ | ✅ | ❌ | ✅ |
| OTP / Auth code | ❌ | ✅ | ✅ | ❌ |
| KYC approved/rejected | ✅ | ✅ | ❌ | ✅ |
| New review on guide | ✅ | ❌ | ❌ | ✅ |
| Listing featured | ✅ | ✅ | ❌ | ✅ |
| Payout processed | ✅ | ✅ | ✅ | ✅ |
| New investment application | ✅ | ✅ | ❌ | ✅ |
| Carpool match found | ✅ | ❌ | ✅ | ✅ |
| System broadcast | ✅ | ✅ | ❌ | ✅ |
| Weekly summary (digest) | ❌ | ✅ | ❌ | ❌ |

### 8.3 Template System

Templates stored in PostgreSQL with AR/EN variants:

```python
TEMPLATES = {
  "booking.confirmed": {
    "ar": {
      "push_title": "تم تأكيد حجزك ✅",
      "push_body": "رحلتك مع {guide_name} في {date} مؤكدة",
      "email_subject": "تأكيد حجز - هنا وادينا",
      "email_template": "booking_confirmed_ar.html",
      "sms": "تم تأكيد حجزك مع {guide_name} بتاريخ {date}. هنا وادينا"
    },
    "en": {
      "push_title": "Booking Confirmed ✅",
      "push_body": "Your trip with {guide_name} on {date} is confirmed",
      "email_subject": "Booking Confirmed - Hena Wadeena",
      "email_template": "booking_confirmed_en.html",
      "sms": "Your booking with {guide_name} on {date} is confirmed. Hena Wadeena"
    }
  }
}
```

### 8.4 Real-Time In-App (Soketi + React)

```
Server (notification-service)
  → publishes to Soketi channel: private-user.{user_id}
  → event: notification.new

React client (connected via pusher-js)
  → subscribes to private-user.{user_id}
  → receives notification payload
  → updates badge counter in state
  → shows toast alert
```

### 8.5 Digest & Campaign System

```python
# Celery beat task — runs every Sunday 10:00 AM Cairo time
@app.task
def send_weekly_digest():
    active_users = get_users_with_digest_enabled()
    for user in active_users:
        data = {
            "new_listings": get_new_listings_near(user.preferred_areas, days=7),
            "trending_guides": get_top_guides(limit=3),
            "market_summary": get_price_trends(user.preferred_areas)
        }
        notification_service.send_email(
            user_id=user.id,
            template="weekly_digest",
            context=data
        )
```

---

## 9. API Gateway Layer

### 9.1 Kong Configuration

```yaml
# kong.yml (declarative config)

services:
  - name: auth-service
    url: http://auth-service:8000
    routes:
      - name: auth-routes
        paths: ["/api/v1/auth"]
        strip_path: false

  - name: user-service
    url: http://user-service:8001
    routes:
      - name: user-routes
        paths: ["/api/v1/users"]

  - name: map-service
    url: http://map-service:8002
    routes:
      - name: map-routes
        paths: ["/api/v1/map", "/api/v1/carpool"]

  - name: market-service
    url: http://market-service:8003
    routes:
      - name: market-routes
        paths: ["/api/v1/market", "/api/v1/listings"]

  - name: guide-service
    url: http://guide-service:8004
    routes:
      - name: guide-routes
        paths: ["/api/v1/guides", "/api/v1/bookings"]

  - name: investment-service
    url: http://investment-service:8005
    routes:
      - name: investment-routes
        paths: ["/api/v1/investments"]

  - name: payment-service
    url: http://payment-service:8006
    routes:
      - name: payment-routes
        paths: ["/api/v1/payments", "/api/v1/wallet"]

  - name: notification-service
    url: http://notification-service:8007
    routes:
      - name: notification-routes
        paths: ["/api/v1/notifications"]

  - name: search-service
    url: http://search-service:8008
    routes:
      - name: search-routes
        paths: ["/api/v1/search"]

  - name: ai-service
    url: http://ai-service:8009
    routes:
      - name: ai-routes
        paths: ["/api/v1/ai"]

plugins:
  - name: jwt                         # JWT validation on all protected routes
  - name: rate-limiting
    config:
      minute: 100
      hour: 2000
      policy: redis
  - name: cors
    config:
      origins: ["https://hena-wadeena.com", "http://localhost:3000"]
      methods: [GET, POST, PUT, PATCH, DELETE, OPTIONS]
      headers: [Authorization, Content-Type, Accept-Language]
  - name: request-transformer
    config:
      add:
        headers:
          - "X-User-Id: $(jwt.claims.sub)"
          - "X-User-Role: $(jwt.claims.role)"
          - "X-Request-Id: $(uuid)"
  - name: prometheus                  # Expose metrics
  - name: http-log                    # Send logs to Loki
    config:
      http_endpoint: http://loki:3100/loki/api/v1/push
```

### 9.2 Rate Limits per Role

| Endpoint | tourist/student | investor/merchant | guide | admin |
|---|---|---|---|---|
| Search | 60/min | 120/min | 60/min | unlimited |
| Listing create | ❌ | 10/day | ❌ | unlimited |
| AI Chat | 20/day | 50/day | 30/day | unlimited |
| Map API | 200/min | 200/min | 200/min | unlimited |
| Auth OTP | 5/hour | 5/hour | 5/hour | 10/hour |

---

## 10. Auth & Identity Service

### 10.1 Token Strategy

```
Access Token:   JWT, RS256, TTL = 15 minutes
Refresh Token:  Opaque (stored hash in DB), TTL = 30 days
OTP:            6-digit, TTL = 5 minutes, max 3 attempts

JWT Payload:
{
  "sub":  "user-uuid",
  "role": "tourist",
  "lang": "ar",
  "jti":  "token-unique-id",
  "iat":  1741344000,
  "exp":  1741344900
}
```

### 10.2 Auth Flows

```
Standard Login:
  POST /auth/login {email/phone, password}
  → validate credentials
  → issue access_token + refresh_token
  → set HttpOnly cookie for refresh_token (web)
  → return access_token in response body (mobile)

OTP Login (phone):
  POST /auth/otp/request {phone}       → sends SMS via Vonage
  POST /auth/otp/verify  {phone, code} → issues tokens

Google OAuth2:
  GET /auth/google               → redirect to Google
  GET /auth/google/callback      → exchange code → tokens

Token Refresh:
  POST /auth/refresh {refresh_token}
  → validate refresh token (DB lookup, not blacklisted)
  → issue new access_token
  → rotate refresh_token (old one invalidated)

Logout:
  POST /auth/logout
  → blacklist current jti in Redis (TTL = remaining token TTL)
  → delete refresh token from DB
```

### 10.3 KYC Verification Flow

```
Student/Investor/Guide registers →
  1. Uploads ID doc via media-service
  2. user-service stores doc URL + status: 'pending'
  3. Admin sees pending KYC queue in admin-service
  4. Admin approves/rejects →
       notification-service sends result to user
       user-service updates status + role capabilities
```

---

## 11. AI/ML Services

### 11.1 Chatbot (RAG Architecture)

```
User message: "أين أقرب فندق في الخارجة؟"
        │
        ▼
Arabic language detection + preprocessing
        │
        ▼
Generate embedding via OpenAI text-embedding-3-small
        │
        ▼
Query Qdrant: top-5 similar chunks
  (filter: district='الخارجة', source_type='poi')
        │
        ▼
Build context prompt:
  System: "أنت مساعد منصة هنا وادينا..."
  Context: [retrieved chunks]
  User: "أين أقرب فندق في الخارجة؟"
        │
        ▼
GPT-4o → Arabic response
        │
        ▼
Return to user + store conversation in Redis (TTL 2h)
```

**Fallback strategy:**
```
GPT-4o (primary) → Ollama/llama3 (self-hosted fallback) → rule-based FAQ
```

### 11.2 Recommendation Engine

```python
# guide-service calls ai-service for recommendations

def get_guide_recommendations(user_id: str, limit: int = 5) -> list:
    user_profile = fetch_user_preferences(user_id)
    recent_views = fetch_recent_views(user_id, days=30)
    
    # Feature vector per guide
    features = build_guide_features()  # rating, specialties, language, price
    
    # Content-based: match user interests to guide specialties
    content_scores = cosine_similarity(user_profile_vector, features)
    
    # Collaborative: users like this user also booked...
    collab_scores = fetch_collab_scores(user_id)
    
    # Blend (70% content, 30% collab at low data, flip at high data)
    final_scores = 0.7 * content_scores + 0.3 * collab_scores
    
    return top_n(final_scores, limit)
```

### 11.3 Price Prediction Model

```python
# market-service calls ai-service for price estimates

Input features:
  - district (one-hot encoded)
  - property_type (real_estate | land | commercial)
  - area_sqm
  - floor (if applicable)
  - age_years
  - amenities_count
  - distance_to_center_km (PostGIS calculated)
  - month (seasonal factor)

Model: XGBoost (trained on historical listing data)
Output: { predicted_price: float, confidence_interval: [low, high] }

Retrain: Celery beat task, weekly, on new closed transactions
```

### 11.4 Content Moderation

```python
# Triggered on: listing creation, review submission, guide bio update

async def moderate_content(text: str, type: str) -> ModerationResult:
    # Arabic-aware moderation
    result = await openai.moderations.create(input=text)
    
    if result.flagged:
        return ModerationResult(
            approved=False,
            reason=result.categories,
            action="hold_for_review"
        )
    
    # Custom rules for Egyptian context (phone numbers in listings, etc.)
    custom_check = run_custom_rules(text, type)
    
    return ModerationResult(approved=not custom_check.flagged)
```

---

## 12. Search & Indexing Service

### 12.1 Index Sync Strategy

Search index is kept in sync via event consumption (eventual consistency):

```
Domain service writes to DB
    → publishes event: index.{entity}.upsert
    → RabbitMQ (fan-out)
    → search-service consumer
    → transforms data to search document
    → upserts into Meilisearch
```

**Bulk reindex job (Celery, nightly):**
```python
@app.task
def full_reindex():
    """Reconcile Meilisearch with primary DBs — catches missed events"""
    for service, fetcher in INDEX_SOURCES.items():
        documents = fetcher.get_all_active()
        meilisearch_client.index(service).add_documents_in_batches(
            documents, batch_size=500
        )
```

### 12.2 Geo Search

```python
# Listings near location
GET /api/v1/search/listings?
  lat=25.4435&lng=30.5585&radius_km=10
  &type=real_estate&transaction=rent
  &min_price=500&max_price=2000
  &sort=price:asc

# Meilisearch geo filter
{
  "filter": [
    "_geoRadius(25.4435, 30.5585, 10000)",  # 10km in meters
    "listing_type = 'real_estate'",
    "transaction = 'rent'",
    "price 500 TO 2000"
  ],
  "sort": ["price:asc"],
  "hitsPerPage": 20
}
```

### 12.3 Arabic Search Handling

Meilisearch with custom configuration for Arabic:

```json
{
  "index": "listings",
  "typoTolerance": {
    "enabled": true,
    "minWordSizeForTypos": { "oneTypo": 4, "twoTypos": 8 }
  },
  "synonyms": {
    "الخارجة": ["kharga", "el kharga"],
    "الداخلة": ["dakhla", "el dakhla"],
    "شقة": ["apartment", "flat", "شقق"],
    "أرض": ["land", "قطعة أرض"]
  },
  "stopWords": ["في", "من", "على", "إلى", "و", "أو", "the", "a", "an"]
}
```

---

## 13. Async Jobs & Background Processing

### 13.1 Celery Worker Architecture

```
Celery Workers (separate queues):
  ├── high_priority    → OTP delivery, payment callbacks, booking alerts
  ├── default          → email sends, index sync, AI requests
  ├── low_priority     → report generation, bulk exports
  └── scheduled        → cron jobs (digest, reindex, price snapshots)

Redis as broker + result backend
Flower (monitoring UI) for visibility
```

### 13.2 Scheduled Jobs (Cron)

| Job | Schedule | Description |
|---|---|---|
| `send_weekly_digest` | Sunday 10:00 | Email digest to opted-in users |
| `price_snapshot` | Daily 02:00 | Aggregate market prices per district |
| `full_reindex` | Daily 03:00 | Reconcile Meilisearch with primary DBs |
| `guide_rating_recalc` | Hourly | Recalculate guide avg rating from reviews |
| `expired_listings_cleanup` | Daily 01:00 | Mark expired listings as inactive |
| `carpool_cleanup` | Every 6h | Remove departed/cancelled rides |
| `wallet_reconcile` | Daily 04:00 | Verify wallet balances vs transactions |
| `payout_batch` | Sunday 12:00 | Process approved payout requests |
| `embedding_sync` | Every 4h | Sync new content to Qdrant vector DB |
| `db_backup` | Daily 00:00 | PostgreSQL + MongoDB dump to MinIO |

### 13.3 Key Async Task Implementations

```python
# booking.confirmed event → async: release escrow after tour completion

@app.task(bind=True, max_retries=3)
def release_escrow_after_booking(self, booking_id: str):
    try:
        booking = guide_service_client.get_booking(booking_id)
        if booking.status != 'completed':
            # Retry in 1 hour (auto-complete 24h after tour date)
            raise self.retry(countdown=3600)
        
        payment_service_client.release_escrow(
            escrow_id=booking.escrow_id,
            payee_id=booking.guide_id
        )
        notification_service_client.send(
            user_id=booking.guide_id,
            type='payout.received',
            data={'amount': booking.guide_earnings}
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
```

---

## 14. Frontend Architecture (React)

### 14.1 Project Structure

```
apps/
  web/                     # React web app (Vite + TailwindCSS)
  mobile/                  # React Native (Expo)

packages/
  api-client/              # Auto-generated from OpenAPI specs
  ui/                      # Shared component library
  hooks/                   # Shared React hooks
  types/                   # Shared TypeScript types
```

### 14.2 Web App Structure

```
src/
  ├── app/
  │   ├── routes/          # React Router v6 routes
  │   ├── layouts/         # MainLayout, AuthLayout, DashboardLayout
  │   └── providers/       # QueryClientProvider, AuthProvider, RTLProvider
  │
  ├── features/            # Feature-based modules
  │   ├── auth/            # Login, Register, OTP, OAuth
  │   ├── map/             # Interactive map, POI, carpool
  │   ├── market/          # Listings, price index, B2B directory
  │   ├── guides/          # Guide profiles, booking flow
  │   ├── investment/      # Opportunities, applications
  │   ├── payments/        # Wallet, transactions, checkout
  │   ├── notifications/   # Notification center, preferences
  │   ├── search/          # Global search, filters
  │   ├── ai-chat/         # Chatbot widget
  │   └── profile/         # User profile, settings, KYC
  │
  ├── shared/
  │   ├── components/      # Button, Input, Modal, Map, Card, etc.
  │   ├── hooks/           # useAuth, useNotifications, useSocket
  │   ├── store/           # Zustand global state
  │   └── utils/           # Arabic formatting, date helpers
  │
  └── i18n/
      ├── ar.json          # Arabic translations
      └── en.json          # English translations
```

### 14.3 State Management

```
Server state:   TanStack Query (React Query) — API data, caching, invalidation
Client state:   Zustand — auth, UI preferences, cart/draft state
Real-time:      pusher-js (Soketi) — live notifications, map updates
Forms:          React Hook Form + Zod validation
```

### 14.4 RTL / Arabic Support

```javascript
// tailwind.config.js
module.exports = {
  plugins: [require('tailwindcss-rtl')],
};

// App root
<html lang={lang} dir={lang === 'ar' ? 'rtl' : 'ltr'}>

// Font: IBM Plex Arabic (supports Arabic + Latin)
// Numerals: Eastern Arabic numerals when lang='ar'
```

### 14.5 Role-Aware UI Routing

```typescript
// Route guard
const GuardedRoute = ({ allowed_roles }: { allowed_roles: Role[] }) => {
  const { user } = useAuth();
  
  if (!user) return <Navigate to="/login" />;
  if (!allowed_roles.includes(user.role)) return <Navigate to="/403" />;
  
  return <Outlet />;
};

// Usage
<Route element={<GuardedRoute allowed_roles={['investor', 'admin']} />}>
  <Route path="/investments/manage" element={<InvestmentManage />} />
</Route>
```

---

## 15. Observability Stack

### 15.1 Stack Components

```
Metrics:  Prometheus (scrapes all services via /metrics)
Dashboards: Grafana (connected to Prometheus + Loki)
Logs:     Loki (log aggregation) + Promtail (log shipper)
Traces:   OpenTelemetry → Tempo (distributed tracing)
Alerts:   Alertmanager → PagerDuty / Telegram Bot
```

### 15.2 Key Dashboards

```
1. Platform Overview
   - Active users (last 5m, 1h, 24h)
   - Request rate per service
   - Error rate (p95, p99 latency)
   - Revenue (from payment-service metrics)

2. Service Health
   - Per-service: CPU, Memory, Requests/sec, Error%
   - DB connection pool usage
   - Redis hit ratio
   - RabbitMQ queue depths

3. Business KPIs
   - New registrations by role
   - Bookings created / completed / cancelled
   - Listings created by district
   - Search queries by category
   - AI chatbot usage / satisfaction rate
```

### 15.3 Alert Rules

```yaml
groups:
  - name: platform_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        annotations:
          summary: "Error rate > 5% on {{ $labels.service }}"

      - alert: PaymentServiceDown
        expr: up{job="payment-service"} == 0
        for: 30s
        severity: critical

      - alert: RabbitMQQueueDepth
        expr: rabbitmq_queue_messages > 1000
        for: 5m
        annotations:
          summary: "Queue {{ $labels.queue }} has {{ $value }} pending messages"

      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.85
        for: 5m
        annotations:
          summary: "Redis memory usage above 85%"
```

---

## 16. CI/CD Pipeline

### 16.1 Per-Service Pipeline (GitHub Actions)

```yaml
# .github/workflows/service.yml
name: Service CI/CD

on:
  push:
    paths: ['services/market-service/**']
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          cd services/market-service
          pip install -r requirements.txt
          pytest --cov=. --cov-report=xml

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build & push Docker image
        run: |
          IMAGE=ghcr.io/hena-wadeena/market-service:${{ github.sha }}
          docker build -t $IMAGE .
          docker push $IMAGE

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - name: Update staging manifest
        run: |
          yq -i '.spec.template.spec.containers[0].image = "ghcr.io/hena-wadeena/market-service:${{ github.sha }}"' \
            k8s/staging/market-service/deployment.yaml
          git commit -am "ci: bump market-service to ${{ github.sha }}"
          git push
      # ArgoCD detects the change and syncs automatically

  deploy-production:
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production    # requires manual approval
    runs-on: ubuntu-latest
    steps:
      - name: Canary deploy (5% traffic)
        run: kubectl apply -f k8s/prod/market-service/canary.yaml
      - name: Wait 10 minutes
        run: sleep 600
      - name: Check error rate
        run: ./scripts/check_canary_health.sh market-service
      - name: Full rollout
        run: kubectl apply -f k8s/prod/market-service/deployment.yaml
```

### 16.2 GitOps with ArgoCD

```yaml
# k8s/argocd/market-service-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: market-service
  namespace: argocd
spec:
  project: hena-wadeena
  source:
    repoURL: https://github.com/hena-wadeena/infra
    targetRevision: HEAD
    path: k8s/prod/market-service
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

---

## 17. Full Architecture Diagram (Textual)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                     │
│  React Web (Vite)    React Native (Expo)     AI Chatbot Widget      │
└──────────────┬──────────────────┬──────────────────┬───────────────┘
               │                  │                  │
               └──────────────────┴──────────────────┘
                                  │ HTTPS
                    ┌─────────────▼─────────────┐
                    │        Kong API Gateway    │
                    │  Auth · Rate Limit · CORS  │
                    │  Routing · Logging · RBAC  │
                    └──────────┬────────────────┘
                               │ injects X-User-Id, X-User-Role
              ┌────────────────┴────────────────────────┐
              │            CORE MICROSERVICES            │
              │                                         │
   ┌──────────▼──┐  ┌──────────▼──┐  ┌────────────▼──┐ │
   │ auth-service│  │ user-service│  │  map-service  │ │
   │ (FastAPI)   │  │ (FastAPI)   │  │  (Node.js)    │ │
   │ PostgreSQL  │  │ PostgreSQL  │  │ PG+PostGIS    │ │
   └─────────────┘  └─────────────┘  └───────────────┘ │
                                                        │
   ┌─────────────┐  ┌─────────────┐  ┌───────────────┐ │
   │market-service│ │guide-service│  │invest-service │ │
   │ (FastAPI)   │  │ (FastAPI)   │  │  (FastAPI)    │ │
   │ PG+MongoDB  │  │ PostgreSQL  │  │ PG+MongoDB    │ │
   └─────────────┘  └─────────────┘  └───────────────┘ │
                                                        │
   ┌─────────────┐  ┌─────────────┐  ┌───────────────┐ │
   │payment-svc  │  │notif-service│  │search-service │ │
   │ (FastAPI)   │  │  (FastAPI)  │  │  (FastAPI)    │ │
   │ PostgreSQL  │  │ PG + Redis  │  │ Meilisearch   │ │
   └──────┬──────┘  └──────┬──────┘  └───────────────┘ │
          │                │                             │
          └────────────────┴─────────────────────────────┘
                           │
                ┌──────────▼──────────┐
                │   RabbitMQ          │
                │  Event Bus          │
                │  platform.* topics  │
                └──────────┬──────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
┌────────▼──────┐  ┌───────▼──────┐  ┌──────▼────────┐
│  ai-service   │  │ analytics-svc│  │  admin-service │
│  (FastAPI)    │  │  (FastAPI)   │  │   (FastAPI)    │
│ Qdrant+OpenAI │  │  ClickHouse  │  │  PostgreSQL    │
└───────────────┘  └──────────────┘  └────────────────┘

            SHARED INFRASTRUCTURE
┌──────────────────────────────────────────────┐
│  Redis 7        PostgreSQL 16    MongoDB 7    │
│  MinIO          Meilisearch      Qdrant       │
│  Soketi         Prometheus       Grafana      │
│  Loki           Tempo            Alertmanager │
│  Celery Workers  RabbitMQ        Flower       │
└──────────────────────────────────────────────┘

            EXTERNAL INTEGRATIONS
┌──────────────────────────────────────────────┐
│  Google Maps API      Firebase FCM           │
│  Vonage (SMS/OTP)     Resend (Email)         │
│  Paymob (Payments)    OpenAI API             │
│  Keycloak (Identity)  Google OAuth2          │
└──────────────────────────────────────────────┘
```

---

## Technology Summary Reference

| Concern | Technology | Justification |
|---|---|---|
| Web Frontend | React 18 + Vite | Fast HMR, component ecosystem |
| Mobile | React Native + Expo | Shared codebase with web |
| Gateway | Kong | Auth, rate-limit, routing plugins |
| Auth | Keycloak + FastAPI bridge | OIDC, role mapping, enterprise-ready |
| Backend (main) | FastAPI (Python 3.12) | Async, type-safe, AI ecosystem |
| Backend (real-time) | Node.js + Express | WebSocket, event streaming |
| Relational DB | PostgreSQL 16 + PostGIS | ACID, geo queries, JSONB |
| Document DB | MongoDB 7 | Variable schema content, activity logs |
| Cache | Redis 7 | Sessions, hot data, pub/sub |
| Search | Meilisearch | Arabic-friendly, fast, simple ops |
| Vector DB | Qdrant | RAG embeddings, semantic search |
| Object Storage | MinIO | S3-compatible, self-hosted |
| Message Broker | RabbitMQ | Reliable queues, DLQ, routing |
| Task Queue | Celery + Redis | Python-native async jobs, cron |
| Real-time Push | Soketi (Pusher protocol) | WebSocket, self-hosted |
| Email | Resend | API-first, high deliverability |
| SMS / OTP | Vonage | Egypt coverage, competitive rates |
| Mobile Push | Firebase FCM | Unified iOS + Android + Web |
| Payments | Paymob | Egyptian market, InstaPay, cards |
| AI / LLM | OpenAI GPT-4o + Ollama | Arabic, RAG, fallback strategy |
| Orchestration | Kubernetes (K3s) | Cost-efficient, regional deployment |
| CI/CD | GitHub Actions + ArgoCD | GitOps, automated deploy |
| Observability | Prometheus + Grafana + Loki | Full stack: metrics, logs, alerts |
| Tracing | OpenTelemetry + Tempo | Distributed request tracing |

---

*Built by Dev-X for هنا وادينا · الوادي الجديد، الخارجة، مصر*
