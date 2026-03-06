# High Level Design (HLD) — Hena Wadeena Platform
**"الوادي.. أقرب مما تخيّل"**

---

## 1. Overview

Hena Wadeena is a web + chatbot platform serving the New Valley (Al-Wadi Al-Jadeed) region of Egypt. It connects tourists, students, investors, and local citizens with real estate listings, guided tours, investment opportunities, and AI-driven assistance.

The backend is built on a **Microservices Architecture** exposed through a central **API Gateway**, backed by a **polyglot persistence** strategy (MySQL, MongoDB, Redis, Elasticsearch), with asynchronous job processing via **Celery** and full observability via **Prometheus/Grafana**.

---

## 2. Architecture Layers

```
┌────────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                  │
│          Web App  │  Mobile App  │  AI Chatbot (Assistant)             │
└────────────────────────────┬───────────────────────────────────────────┘
                             │  HTTPS / WebSocket
┌────────────────────────────▼───────────────────────────────────────────┐
│                        API GATEWAY                                     │
│   Authentication · Authorization · Rate Limiting · Routing · Logging  │
└──┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────────┘
   │      │      │      │      │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
 Users  Maps  Market  Guide  Invest  Notif  Pay  Search  AI/ML
  Svc   Svc    Svc    Svc    Svc     Svc   Svc   Svc    Services
   │      │      │      │      │      │      │      │      │
   └──────┴──────┴──────┴──────┴──────┴──────┴──────┘      │
                             │                              │
                    ┌────────▼────────┐          ┌──────────▼──────────┐
                    │  Async Workers  │          │   RAG · Chatbot ·   │
                    │  (Celery Queue) │          │   Recommendation    │
                    └────────┬────────┘          └─────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │         DATA LAYER          │
              │  MySQL · MongoDB · Redis ·  │
              │       Elasticsearch         │
              └─────────────────────────────┘
```

---

## 3. API Gateway

The single entry-point for all client traffic.

| Responsibility       | Detail                                                                 |
|----------------------|------------------------------------------------------------------------|
| **Authentication**   | Validates JWT tokens / session tokens on every inbound request         |
| **Authorization**    | Enforces role-based access control (RBAC) before forwarding            |
| **Routing**          | Dispatches requests to the correct downstream microservice             |
| **Rate Limiting**    | Prevents abuse; protects services from DDoS spikes                     |
| **Error Handling**   | Returns standardised error responses (4xx / 5xx) to clients            |
| **Logging**          | Attaches a unique Request-ID to every call for distributed tracing     |

**Communication:** All downstream services are called over internal HTTP/REST. The gateway never exposes service URLs to clients.

---

## 4. Microservices

### 4.1 Users Service

**Responsibility:** Manages identity, authentication state, roles, and user profiles.

| Item              | Detail                                                                 |
|-------------------|------------------------------------------------------------------------|
| Endpoints         | Register, Login, Refresh Token, Get/Update Profile, Manage Roles       |
| Primary DB        | **MySQL** — structured user records, roles, sessions                   |
| Cache             | **Redis** — active sessions, JWT blocklist                             |
| Emits Events      | `user.created`, `user.role_changed`                                    |
| Consumes Events   | —                                                                      |

```
Users Service
    │── MySQL  (users, roles, auth_tokens)
    └── Redis  (session cache, token store)
```

---

### 4.2 Maps & Navigation Service

**Responsibility:** Provides interactive maps, routes, Points of Interest (POIs), and carpooling matchmaking within the New Valley.

| Item              | Detail                                                                    |
|-------------------|---------------------------------------------------------------------------|
| Endpoints         | Get POIs, Calculate Route, Get Carpooling Matches, List Transit Options   |
| External API      | **Google Maps API** (geo-coding, directions, distance matrix)             |
| Primary DB        | **MongoDB** — geo-tagged POIs, route history, carpooling requests         |
| Cache             | **Redis** — frequently requested routes, popular POI lists (TTL: 1 hr)   |
| Emits Events      | `route.requested`                                                         |
| Consumes Events   | `listing.created` (to pin new real estate on map)                         |

```
Maps Service
    │── MongoDB      (POIs, routes, carpooling records)
    │── Redis        (route cache, POI cache)
    └── Google Maps  (external geo API)
```

---

### 4.3 Market / Real Estate Service

**Responsibility:** CRUD for real estate listings, B2B commercial opportunities, pricing, and market analytics.

| Item              | Detail                                                                       |
|-------------------|------------------------------------------------------------------------------|
| Endpoints         | List/Search Properties, Get Pricing, Submit Listing, B2B Enquiries           |
| Primary DB        | **MySQL** — structured listings, transactions, pricing records               |
| Document DB       | **MongoDB** — flexible listing metadata, media references, historical prices |
| Search Index      | **Elasticsearch** — full-text and geo-proximity search on listings           |
| Cache             | **Redis** — today's prices, hot listings (TTL: 10–30 min)                   |
| Async Jobs        | Price refresh (Celery cron), listing re-indexing                             |
| Emits Events      | `listing.created`, `listing.updated`, `price.updated`                        |
| Consumes Events   | —                                                                            |

```
Market Service
    │── MySQL           (listings, transactions, pricing)
    │── MongoDB         (listing metadata, media, history)
    │── Elasticsearch   (search index)
    │── Redis           (price cache, hot-listings cache)
    └── Celery          (scheduled price updates, re-indexing)
```

---

### 4.4 Guide Service

**Responsibility:** Curates tourist guides, service providers (accommodation, restaurants, transport), reviews, and AI-generated recommendations.

| Item              | Detail                                                                         |
|-------------------|--------------------------------------------------------------------------------|
| Endpoints         | Get Guides, List Service Providers, Submit Review, Get Recommendations         |
| Primary DB        | **MongoDB** — guide profiles, service provider records, reviews, media         |
| Search Index      | **Elasticsearch** — guide & provider search with autocomplete                  |
| Cache             | **Redis** — popular guides, active service-provider listings (TTL: 24 hr)      |
| AI Integration    | Calls **Recommendation Service** for personalised guide suggestions            |
| Emits Events      | `review.submitted`                                                             |
| Consumes Events   | `user.created` (personalise onboarding)                                        |

```
Guide Service
    │── MongoDB       (guides, providers, reviews)
    │── Elasticsearch (guide search index)
    │── Redis         (guide cache)
    └── AI/ML Svc    (recommendation calls)
```

---

### 4.5 Investment Service

**Responsibility:** Manages investment opportunity listings, investor profiles, B2B deal flows, and market data for institutional and individual investors.

| Item              | Detail                                                                          |
|-------------------|---------------------------------------------------------------------------------|
| Endpoints         | List Opportunities, Submit Interest, Get Market Data, B2B Negotiation Flows     |
| Primary DB        | **MySQL** — structured investment deals, financials, investor records           |
| Document DB       | **MongoDB** — flexible opportunity metadata, due-diligence documents            |
| Cache             | **Redis** — active opportunity snapshots (TTL: 30 min)                         |
| Async Jobs        | Daily market-data aggregation, portfolio summary reports (Celery cron)          |
| Emits Events      | `investment.interest_submitted`, `opportunity.published`                        |
| Consumes Events   | `user.role_changed` (grant investor portal access)                              |

```
Investment Service
    │── MySQL    (deals, investors, financials)
    │── MongoDB  (opportunity docs, metadata)
    │── Redis    (snapshot cache)
    └── Celery   (daily aggregation jobs)
```

---

### 4.6 Notifications Service

**Responsibility:** Dispatches emails, in-app push notifications, and SMS alerts to users for all platform events.

| Item              | Detail                                                                |
|-------------------|-----------------------------------------------------------------------|
| Endpoints         | Send Notification, Get Notification History, Mark as Read            |
| Primary DB        | **MongoDB** — notification logs, delivery status, preferences        |
| Cache             | **Redis** — unread counts per user (real-time badge updates)         |
| Transport         | SMTP (email), FCM/APNs (push), SMS gateway                          |
| Async Jobs        | Bulk digest emails, scheduled reminders (Celery)                     |
| Consumes Events   | `user.created`, `listing.updated`, `review.submitted`, `payment.confirmed`, `investment.interest_submitted` |
| Emits Events      | —                                                                    |

```
Notifications Service
    │── MongoDB  (notification logs, preferences)
    │── Redis    (unread count cache)
    └── Celery   (bulk email & scheduled alerts)
        └── External: SMTP · FCM/APNs · SMS Gateway
```

---

### 4.7 Payments Service

**Responsibility:** Processes financial transactions, manages payment gateway integrations, handles refunds and financial ledger entries.

| Item              | Detail                                                                       |
|-------------------|------------------------------------------------------------------------------|
| Endpoints         | Initiate Payment, Confirm Payment, Refund, Get Transaction History           |
| Primary DB        | **MySQL** — ACID-compliant transactions, ledger records, invoices            |
| Cache             | **Redis** — idempotency keys (prevent duplicate charges)                     |
| External APIs     | Payment gateway (e.g., Paymob / Fawry)                                       |
| Security          | Encrypted sensitive fields; PCI-DSS considerations                           |
| Emits Events      | `payment.confirmed`, `payment.failed`, `refund.issued`                       |
| Consumes Events   | `investment.interest_submitted`, `listing.booking_requested`                 |

```
Payments Service
    │── MySQL    (ledger, transactions, invoices)
    │── Redis    (idempotency keys)
    └── External Payment Gateway (Paymob / Fawry)
```

---

### 4.8 Search & Index Service

**Responsibility:** Provides unified full-text and geo-proximity search across all content types (listings, guides, providers, investment opportunities).

| Item              | Detail                                                                         |
|-------------------|--------------------------------------------------------------------------------|
| Endpoints         | Search (multi-entity), Autocomplete, Filter & Facet                            |
| Primary Store     | **Elasticsearch** — inverted indexes per content type                          |
| Cache             | **Redis** — top search results for popular queries (TTL: 15 min)              |
| Index Sources     | Consumes events from Market, Guide, and Investment services to keep indexes fresh |
| Async Jobs        | Periodic full re-index (Celery cron), incremental delta updates                |
| Consumes Events   | `listing.created/updated`, `review.submitted`, `opportunity.published`         |
| Emits Events      | —                                                                              |

```
Search Service
    │── Elasticsearch  (primary search index — listings, guides, providers, opportunities)
    │── Redis          (popular-query cache)
    └── Celery         (re-index jobs)
```

---

### 4.9 AI / ML Services

Three specialised AI sub-components share the same internal service boundary:

#### 4.9.1 Chatbot (AI Assistant)
- Handles natural-language queries from users inside the platform
- Routes to RAG or direct LLM response depending on query type
- **No persistent DB** — stateless per session; conversation history stored ephemerally in **Redis**

#### 4.9.2 RAG Service (Retrieval-Augmented Generation)
- Augments LLM responses with up-to-date, factual content from the platform
- Vector index stored in **Elasticsearch** (or a dedicated vector store)
- Source documents: guides, FAQs, listings, regulatory content

#### 4.9.3 Recommendation Service
- Suggests guides, listings, and investment opportunities based on user behaviour
- Reads user activity from **MongoDB** (event logs) and **Redis** (session signals)
- Outputs personalised ranked lists to Guide, Market, and Investment services

```
AI/ML Services
    │── Redis            (chat session context, TTL-bounded)
    │── Elasticsearch    (vector / document index for RAG)
    │── MongoDB          (user activity logs for recommendations)
    └── LLM API          (external: OpenAI / Anthropic / self-hosted)
```

---

## 5. Asynchronous Job Layer (Celery)

All time-consuming or background tasks are offloaded to a **Celery** task queue backed by **Redis** as the broker.

| Job                         | Triggered By              | Frequency         |
|-----------------------------|---------------------------|-------------------|
| Price refresh (Market)      | Cron schedule             | Every 10–30 min   |
| Re-index content (Search)   | Event: `*.updated`        | On-event + nightly|
| Send digest emails (Notif.) | Cron schedule             | Daily             |
| Generate reports (Invest.)  | Cron schedule             | Daily             |
| Data backup                 | Cron schedule             | Nightly           |
| Analytics aggregation       | Post-request async        | Per batch         |

```
Celery Workers
    │── Redis  (task broker & result backend)
    └── MySQL / MongoDB / Elasticsearch  (task targets)
```

---

## 6. Data Layer Summary

| Database          | Role                                      | Used By                                          |
|-------------------|-------------------------------------------|--------------------------------------------------|
| **MySQL**         | Structured, ACID-safe relational data     | Users, Market, Investment, Payments              |
| **MongoDB**       | Flexible / document-oriented data         | Maps, Guide, Notifications, Market, Investment   |
| **Redis**         | Cache, sessions, pub/sub, job broker      | All services (shared)                            |
| **Elasticsearch** | Full-text search, geo search, vector index| Search, Market, Guide, RAG                       |

### Data Ownership Rules
- Each microservice **owns** its primary data store exclusively.
- Cross-service data access happens **only via service APIs or async events** — never direct DB cross-joins.
- Shared Redis is logically namespaced per service (e.g., `users:session:*`, `market:price:*`).

---

## 7. Inter-Service Communication

### 7.1 Synchronous (REST over HTTP)
Used for real-time, user-facing requests requiring an immediate response.

```
API Gateway → [Service A]  →  [Service B]
                              (e.g. Guide Svc calls AI/ML Svc for recommendations)
```

### 7.2 Asynchronous (Event-Driven via Message Queue)
Used for decoupled, non-blocking cross-service notifications.

```
Service A  →  Event Queue (Redis Pub/Sub or lightweight broker)  →  Service B
```

**Key Event Flows:**

```
Market Svc   ──── listing.created ────▶  Search Svc   (re-index)
                                    ──▶  Maps Svc     (pin on map)
                                    ──▶  Notif. Svc   (alert watchers)

Payments Svc ──── payment.confirmed ──▶  Notif. Svc   (receipt email)
                                    ──▶  Market Svc   (confirm booking)

Users Svc    ──── user.created ───────▶  Notif. Svc   (welcome email)
                                    ──▶  Guide Svc    (personalisation seed)

Invest. Svc  ──── opportunity.pub. ──▶  Search Svc   (re-index)
                                    ──▶  Notif. Svc   (alert investors)
```

---

## 8. Security Architecture

| Layer             | Mechanism                                                          |
|-------------------|--------------------------------------------------------------------|
| Transport         | HTTPS/TLS on all external and internal traffic                     |
| Authentication    | JWT (short-lived access token + refresh token rotation)            |
| Authorization     | RBAC enforced at API Gateway + within each service                 |
| Rate Limiting     | API Gateway enforces per-user and per-IP request quotas            |
| Input Validation  | Sanitisation against SQL injection and XSS at service layer        |
| Secrets           | Environment variables / secrets manager (no hard-coded credentials)|
| Data Encryption   | Sensitive fields (payment info, PII) encrypted at rest             |

---

## 9. Observability

| Tool           | Purpose                                                              |
|----------------|----------------------------------------------------------------------|
| **Prometheus** | Metrics collection — CPU, memory, request rate, error rate, latency |
| **Grafana**    | Real-time dashboards, alerting on threshold breaches                |
| **Structured Logging** | Each service emits JSON logs with Request-ID, timestamps, and severity |
| **Health Checks**      | `/health` endpoints on every service polled by a watchdog           |

---

## 10. Deployment Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Cloud / VPS Host                      │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Service  │  │ Service  │  │ Service  │  ...          │
│  │ Container│  │ Container│  │ Container│              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │               Data Tier                          │   │
│  │  MySQL  │  MongoDB  │  Redis  │  Elasticsearch   │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  CI/CD: GitHub Actions / GitLab CI                      │
└─────────────────────────────────────────────────────────┘
```

**CI/CD Pipeline:** Code commit → Build → Unit Tests → Integration Tests → Docker Image → Deploy to staging → Smoke test → Promote to production (zero-downtime rolling deploy).

---

## 11. Technology Stack Reference

| Layer                | Technology                          |
|----------------------|-------------------------------------|
| Frontend             | HTML / JS / CSS                     |
| Backend APIs         | Python (FastAPI) / Node.js / Java   |
| Relational DB        | MySQL                               |
| Document DB          | MongoDB                             |
| Cache / Broker       | Redis                               |
| Search & Vector      | Elasticsearch / Meilisearch         |
| Geo / Maps           | Google Maps API                     |
| AI / LLM             | LLM + RAG + Recommendation System  |
| Async Jobs           | Celery (Task Queue)                 |
| CI / CD              | GitHub Actions / GitLab CI          |
| Monitoring           | Prometheus + Grafana                |

---

*Document: Hena Wadeena — Backend HLD v1.0 | Team: Dev-X | Date: 2026-02-06*
