# Microservices Architecture: Design Decision and Low-Level Implementation

## 1. When Do We Decide to Use Microservices?

Microservices are chosen when the system has:

Typical indicators:

-   Many independent features/modules
-   Multiple development teams
-   Need for independent deployment
-   High scalability requirements
-   Different components require different scaling patterns

Example platform modules:

-   Marketplace
-   Transportation
-   Housing
-   AI assistant
-   Authentication

These naturally separate into services.

------------------------------------------------------------------------

# 2. Domain Decomposition (Domain Driven Design)

Microservices usually start with **Domain Driven Design (DDD)**.

You identify **Bounded Contexts**.

Example:

  Domain            Service
  ----------------- -------------------
  User management   Auth Service
  Marketplace       Product Service
  Transport         Transport Service
  Housing           Property Service
  AI assistant      AI Service
  Payments          Payment Service

Each bounded context becomes a microservice.

------------------------------------------------------------------------

# 3. Service Ownership Rule

Each microservice must own:

1.  Its database
2.  Its business logic
3.  Its APIs
4.  Its data models

Example:

    Auth Service
        owns:
            users table
            login logic
            authentication APIs

Other services **must not access its database directly**.

Communication happens through APIs.

------------------------------------------------------------------------

# 4. Low-Level Service Structure

Each microservice is an independent application.

Example folder structure:

    auth-service
    │
    ├── app
    │   ├── api
    │   │   ├── routes.py
    │   │
    │   ├── services
    │   │   ├── auth_service.py
    │   │
    │   ├── models
    │   │   ├── user.py
    │   │
    │   ├── repository
    │   │   ├── user_repo.py
    │   │
    │   └── main.py
    │
    ├── Dockerfile
    ├── requirements.txt

Other services:

    transport-service
    marketplace-service
    ai-service

Each runs independently.

------------------------------------------------------------------------

# 5. API Communication Between Services

Services communicate using:

## Option 1 (Most common): REST APIs

Example:

    GET /users/{id}

Python example:

``` python
import requests

user = requests.get(
    "http://auth-service:8000/users/123"
)
```

------------------------------------------------------------------------

## Option 2: gRPC

Used for faster internal communication.

------------------------------------------------------------------------

## Option 3: Event Messaging

Using tools like:

-   Kafka
-   RabbitMQ

Example:

    UserCreated Event

Other services subscribe.

------------------------------------------------------------------------

# 6. API Gateway Layer

Instead of frontend calling services directly:

    Frontend
       |
    API Gateway
       |
    Microservices

Example:

    React App
       |
    Nginx / Kong / Traefik
       |
    auth-service
    transport-service
    marketplace-service

Gateway responsibilities:

-   Authentication
-   Routing
-   Rate limiting
-   Logging

------------------------------------------------------------------------

# 7. Independent Databases

Each service has its own database schema.

Example:

    Auth DB
       users

    Transport DB
       trips
       drivers

    Marketplace DB
       products
       orders

This avoids tight coupling.

------------------------------------------------------------------------

# 8. Data Consistency Strategy

Since databases are separate, we use **event-driven consistency**.

Example:

    OrderCreated
       |
    publish event
       |
    Inventory Service

Tools:

-   Kafka
-   RabbitMQ
-   Redis Streams

------------------------------------------------------------------------

# 9. Containerization

Each microservice becomes a Docker container.

Example Dockerfile:

    FROM python:3.11

    WORKDIR /app

    COPY . .

    RUN pip install -r requirements.txt

    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

------------------------------------------------------------------------

# 10. Running Services Together

Using Docker Compose:

    version: "3"

    services:

      auth-service:
        build: ./auth-service
        ports:
          - "8001:8000"

      transport-service:
        build: ./transport-service
        ports:
          - "8002:8000"

      marketplace-service:
        build: ./marketplace-service
        ports:
          - "8003:8000"

      postgres:
        image: postgres

------------------------------------------------------------------------

# 11. Service Discovery

When services scale dynamically, they must discover each other.

Options:

-   Kubernetes DNS
-   Consul
-   etcd

Example:

    http://auth-service.default.svc.cluster.local

------------------------------------------------------------------------

# 12. Observability

Critical for microservices.

## Logging

ELK Stack:

-   Elasticsearch
-   Logstash
-   Kibana

## Metrics

Prometheus

## Distributed Tracing

-   Jaeger
-   OpenTelemetry

Example trace:

    User Request
       |
    Gateway
       |
    Auth Service
       |
    Marketplace Service

------------------------------------------------------------------------

# 13. CI/CD Pipeline

Each microservice has its own pipeline.

Example:

    Git push
       |
    CI pipeline
       |
    Build Docker image
       |
    Run tests
       |
    Push to registry
       |
    Deploy to Kubernetes

------------------------------------------------------------------------

# 14. Deployment Layer

Most common: **Kubernetes**

    Cluster
       |
    Pods
       |
    Containers

Example deployment:

    auth-service (3 replicas)
    transport-service (5 replicas)
    ai-service (2 replicas)

------------------------------------------------------------------------

# 15. Important Microservice Patterns

## API Gateway Pattern

Single entry point for clients.

## Saga Pattern

Used for distributed transactions.

Example:

    Booking trip
       |
    Payment
       |
    Seat reservation

If payment fails → rollback.

## Circuit Breaker

Prevents cascading failures.

Libraries:

-   Resilience4j
-   Hystrix

------------------------------------------------------------------------

# 16. Typical Production Architecture

    Users
      |
    Cloud Load Balancer
      |
    API Gateway
      |
    -------------------------
    | auth-service          |
    | transport-service     |
    | marketplace-service   |
    | housing-service       |
    | ai-service            |
    -------------------------
      |
    Message Broker (Kafka)
      |
    Databases
      |
    Monitoring Stack

------------------------------------------------------------------------

# 17. Common Beginner Mistakes

1.  Splitting services too early
2.  Sharing database between services
3.  Too many network calls
4.  No observability
5.  Ignoring distributed transactions

------------------------------------------------------------------------

# 18. Practical Advice

Most successful systems start with:

**Modular Monolith → Microservices**

Example:

    single codebase
    modules separated

Later split into services when scaling is needed.

------------------------------------------------------------------------

# 19. Real Companies Using Microservices

-   Netflix
-   Amazon
-   Uber
-   Spotify

These companies operate **hundreds or thousands of microservices**.

------------------------------------------------------------------------

# Conclusion

Microservices architecture requires careful design in:

-   Domain boundaries
-   API communication
-   Independent data ownership
-   Containerization
-   Observability
-   Deployment pipelines

When implemented correctly, it allows systems to scale independently,
deploy faster, and support large development teams efficiently.
