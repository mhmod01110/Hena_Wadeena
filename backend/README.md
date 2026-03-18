# Hena Wadeena Backend

## Overview
This backend is a FastAPI microservices platform for tourism, market, investment, guide booking, logistics, payments, notifications, search, analytics, AI assistant, media, and admin operations.

Services follow clean architecture boundaries:
- `controllers/`: HTTP transport and authorization gates
- `services/`: business rules
- `repositories/`: data access implementations
- `models/`: SQLAlchemy entities
- `schemas/`: request/response contracts
- `core/`: settings, DB sessions, dependency wiring

## Refactor Summary (Relational Normalization)
The backend was refactored to remove generic JSON blob persistence (`data`, `details`) from normal relational tables.

Normalized services:
- `admin-service`
- `map-service`
- `market-service`
- `investment-service`
- `guide-service`
- `notification-service`
- `search-service`
- `ai-service`
- `media-service`
- `payment-service`
- `analytics-service`

Examples of what changed:
- AI chat: now stored as explicit columns (`conversation_id`, `user_id`, `message`, `response`, `intent`)
- Payment transactions: explicit financial columns (`amount`, `balance_after`, `payment_method`, references)
- Media assets: explicit metadata columns (`owner_id`, `mime_type`, `size_bytes`, `url`)
- Admin moderation/audit/flags/announcements: explicit review, flag rollout, and audit detail fields
- Analytics events: explicit event dimensions (`event_type`, `actor_role`, `payment_method`, `search_query`, `results_count`, etc.)

API responses are built in the application layer from normalized fields; raw request payloads are no longer persisted as business blobs.

## Role and Permission Model
Implemented operational role boundaries:
- `super_admin`: full control, flags, audit log, unsuspend
- `admin`: user management, announcements, moderation review
- `reviewer`: moderation queue review
- `merchant`, `guide`, `investor`, `tourist`, `local_citizen`: domain-specific actions only

Key examples:
- Admin endpoints require `X-User-Role` in `{admin, super_admin}` or `{reviewer, admin, super_admin}` based on action
- Payment payouts require `guide|merchant|admin|super_admin`
- Search indexing requires `reviewer|admin|super_admin`

## Services and Ports
- Gateway: `8000`
- Auth: `8001`
- User: `8002`
- Map: `8003`
- Market: `8004`
- Guide: `8005`
- Investment: `8006`
- Payment: `8007`
- Notification: `8008`
- Search: `8009`
- AI: `8010`
- Admin: `8011`
- Analytics: `8012`
- Media: `8013`

## Databases
Each service owns its own MySQL schema:
- `hena_auth`, `hena_users`, `hena_map`, `hena_market`, `hena_guide`, `hena_investment`, `hena_payment`, `hena_notification`, `hena_search`, `hena_ai`, `hena_admin`, `hena_analytics`, `hena_media`

Creation script: `backend/init-db.sql`

## Setup and Run
```bash
cd backend
docker compose up -d --build
```

Health checks:
- `GET /health` on each service
- Gateway proxies `/api/v1/*`

## Migration Notes (Important)
This refactor changes table structures in multiple services.

If you have old local data created before this refactor, use one of these safe reset paths:

1. Recreate containers + DB volumes (recommended locally)
```bash
cd backend
docker compose down -v
docker compose up -d --build
```

2. Drop and recreate affected schemas manually, then restart services.

Without resetting schema state, services may fail due to old columns/tables not matching normalized models.

## Seed Data
Seed data is auto-created on first startup when service tables are empty.

Seed coverage includes:
- multiple admins and reviewers
- normal users across tourist/investor/guide/merchant/local citizen
- realistic domain records for listings, opportunities, guide bookings, wallet transactions, media assets, moderation queue, and analytics events

## Demo Credentials
Default seeded password for all users:
- `Pass@12345`

Admin accounts:
- `admin@hena.local`
- `ops.admin@hena.local`

Reviewer accounts:
- `reviewer@hena.local`
- `senior.reviewer@hena.local`

Other demo accounts:
- `guide@hena.local`
- `tourist@hena.local`
- `investor@hena.local`
- `merchant@hena.local`
- `citizen@hena.local`

## Notes
- User preferences in `user-service` still use JSON arrays for `preferred_areas` and `interests`; these are bounded preference lists, not generic business-object blobs.
- Frontend should call backend through gateway (`http://localhost:8000`) and include auth headers for protected routes.
