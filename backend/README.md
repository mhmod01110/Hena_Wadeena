# Hena Wadeena — Backend Microservices

## Architecture

```
backend/
├── gateway/           → API Gateway (port 8000) — routes, JWT, CORS
├── auth-service/      → Auth (port 8001) — login, register, JWT, OTP
├── user-service/      → Users (port 8002) — profiles, KYC, preferences
├── shared/            → Shared utilities (JWT, config, schemas)
├── docker-compose.yml → Orchestration
└── .env               → Configuration
```

## Quick Start

### Prerequisites
- Python 3.11+
- MySQL 8.0  
- Redis 7

### Option 1: Docker Compose (recommended)
```bash
cd backend
docker-compose up -d
```

### Option 2: Local Development
```bash
# 1. Create databases
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS hena_auth;"
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS hena_users;"

# 2. Install dependencies
cd auth-service && pip install -r requirements.txt && cd ..
cd user-service && pip install -r requirements.txt && cd ..
cd gateway && pip install -r requirements.txt && cd ..

# 3. Start services (each in a separate terminal)
cd user-service && uvicorn main:app --port 8002 --reload
cd auth-service && uvicorn main:app --port 8001 --reload
cd gateway && uvicorn main:app --port 8000 --reload
```

## API Endpoints

### Auth (`/api/v1/auth`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/register` | Create new user |
| POST | `/login` | Login with email/phone + password |
| POST | `/refresh` | Refresh access token |
| POST | `/logout` | Revoke refresh token |
| POST | `/otp/request` | Request OTP code |
| POST | `/otp/verify` | Verify OTP and get tokens |

### Users (`/api/v1/users`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/me` | Get current user profile |
| PUT | `/me` | Update profile |
| GET | `/me/preferences` | Get notification preferences |
| PUT | `/me/preferences` | Update preferences |
| POST | `/me/kyc` | Upload KYC document |
| GET | `/me/kyc` | Get KYC status |
| GET | `/{id}` | Get user by ID (admin) |

## Service Ports
| Service | Port |
|---------|------|
| Gateway | 8000 |
| Auth | 8001 |
| User | 8002 |
| Map | 8003 |
| Market | 8004 |
| Guide | 8005 |
| Investment | 8006 |
| Payment | 8007 |
| Notification | 8008 |
| Search | 8009 |
| AI | 8010 |

## Tech Stack
- **FastAPI** (Python) — async API framework
- **SQLAlchemy** (async) — ORM
- **MySQL** — primary database  
- **Redis** — caching, JWT blacklist
- **bcrypt** — password hashing
- **python-jose** — JWT tokens
