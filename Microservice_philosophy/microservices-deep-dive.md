# Microservices: Complete Deep-Dive Reference
> A comprehensive guide covering every layer — from decomposition philosophy to infrastructure wiring

---

## Table of Contents

1. [What Is a Microservice, Really?](#1-what-is-a-microservice-really)
2. [Service Decomposition](#2-service-decomposition)
3. [Inter-Service Communication](#3-inter-service-communication)
4. [API Gateway & Edge Layer](#4-api-gateway--edge-layer)
5. [Routing & Load Balancing](#5-routing--load-balancing)
6. [Service Discovery](#6-service-discovery)
7. [Data Architecture & Databases](#7-data-architecture--databases)
8. [Distributed Transactions & Consistency](#8-distributed-transactions--consistency)
9. [Event-Driven Architecture & Messaging](#9-event-driven-architecture--messaging)
10. [Orchestration & Container Management](#10-orchestration--container-management)
11. [Service Mesh](#11-service-mesh)
12. [Resilience Patterns](#12-resilience-patterns)
13. [Security](#13-security)
14. [Observability: Logging, Metrics, Tracing](#14-observability-logging-metrics-tracing)
15. [CI/CD for Microservices](#15-cicd-for-microservices)
16. [Configuration Management](#16-configuration-management)
17. [Testing Strategies](#17-testing-strategies)
18. [Anti-Patterns & Pitfalls](#18-anti-patterns--pitfalls)
19. [Decision Framework](#19-decision-framework)

---

## 1. What Is a Microservice, Really?

A microservice is a **small, independently deployable unit** that:

- Owns a single bounded domain
- Has its **own database** (no shared data stores)
- Communicates over the **network** (HTTP, gRPC, messaging)
- Can be **deployed, scaled, and failed independently**

### The CAP Theorem Foundation

Every distributed system must choose trade-offs between:

| Property | Meaning |
|---|---|
| **Consistency** | Every read receives the most recent write |
| **Availability** | Every request receives a response (not guaranteed to be latest) |
| **Partition Tolerance** | System continues operating despite network splits |

In microservices, **network partitions are a given**, so you always choose between **CP** (consistent but may reject requests) or **AP** (always responds but may return stale data). Most microservice systems lean AP and embrace **eventual consistency**.

### Monolith vs Microservices Trade-offs

| Dimension | Monolith | Microservices |
|---|---|---|
| Deployment | One unit | Many independent units |
| Scaling | Scale everything | Scale per service |
| Failure blast radius | Total outage risk | Isolated failures |
| Data transactions | ACID, simple | Distributed, complex |
| Development speed (small team) | Fast | Slow (infra overhead) |
| Development speed (large team) | Slow (coupling) | Fast (independent teams) |
| Observability | Easy | Requires dedicated tooling |
| Latency | In-process calls (nanoseconds) | Network calls (milliseconds) |

---

## 2. Service Decomposition

The most consequential decision in microservices. Get this wrong and you end up with a **distributed monolith** — the worst of both worlds.

### 2.1 Domain-Driven Design (DDD)

DDD gives the most principled approach to decomposition.

**Strategic DDD Concepts:**

```
Bounded Context:
  A boundary within which a particular domain model applies.
  The same word "Order" means different things in:
    - Sales context: a customer's purchase request
    - Warehouse context: a picking/packing unit
    - Accounting context: an invoice record
  Each context = a service candidate.

Ubiquitous Language:
  Every team uses the same terms within their bounded context.
  No translation layer — the code uses the same words as the business.

Context Map:
  How bounded contexts relate to each other.
  Patterns: Shared Kernel, Customer-Supplier, Anticorruption Layer, Open Host
```

**Example Domain Model:**

```
E-Commerce Domain
├── Catalog Context       → CatalogService       (products, categories, search)
├── Order Context         → OrderService          (cart, checkout, order lifecycle)
├── Payment Context       → PaymentService        (charging, refunds, invoices)
├── Inventory Context     → InventoryService      (stock levels, reservations)
├── Shipping Context      → ShippingService       (carriers, tracking, delivery)
├── User Context          → UserService           (accounts, auth, profiles)
└── Notification Context  → NotificationService   (email, SMS, push)
```

### 2.2 Decomposition Patterns

**By Business Capability**
Split along what the business *does*, not technical layers.

```
❌ Bad (technical split):
  DataAccessService  → all DB queries
  BusinessLogicService → all rules
  PresentationService  → all rendering

✅ Good (capability split):
  OrderService    → everything about orders
  PaymentService  → everything about payments
```

**By Subdomain**
- **Core subdomain** — your competitive advantage → invest heavily, own fully
- **Supporting subdomain** — necessary but not differentiating → build internally but simpler
- **Generic subdomain** — commodity → buy or use SaaS (email, auth, payments)

**By Volatility**
Separate things that change at different rates:

```
Stable (change rarely):        → AuthService, UserService
Moderate (change monthly):     → OrderService, ProductService
High (change weekly/daily):    → RecommendationService, PricingService, PromoService
```

**Strangler Fig Pattern** (Migration from Monolith)

```
Phase 1: Put a proxy in front of the monolith
         Client → Proxy → Monolith (everything)

Phase 2: Extract first service (e.g., NotificationService)
         Client → Proxy → NotificationService  ← new traffic for /notifications
                       → Monolith              ← everything else

Phase 3: Repeat until monolith is dead
```

### 2.3 Right-Sizing Services

**Too small (nanoservices):** Every function is a service. Massive overhead, chatty network calls, impossible to trace.

**Too large (mini-monolith):** Services have too many responsibilities, teams step on each other.

**Right size heuristics:**
- Can one team (5–8 people) fully own it?
- Can it be rewritten in 2 weeks if needed?
- Does it have a single reason to change?
- Does it have a clean API contract with the outside world?

---

## 3. Inter-Service Communication

### 3.1 Communication Styles

```
Synchronous (request/response):
  Caller waits for a response before continuing.
  Direct dependency at runtime.

Asynchronous (fire and forget / event-driven):
  Caller sends a message and continues.
  No runtime dependency on the receiver.
```

### 3.2 Synchronous: REST over HTTP

```http
POST /orders HTTP/1.1
Host: order-service
Content-Type: application/json
Authorization: Bearer <jwt>

{
  "user_id": "u_123",
  "items": [{"product_id": "p_456", "qty": 2}]
}

--- Response ---
HTTP/1.1 201 Created
Location: /orders/o_789

{
  "order_id": "o_789",
  "status": "pending",
  "created_at": "2026-03-07T10:00:00Z"
}
```

**REST Design Principles for Microservices:**
- Use nouns for resources, not verbs (`/orders` not `/createOrder`)
- Use standard HTTP verbs (GET, POST, PUT, PATCH, DELETE)
- Return appropriate status codes (201 Created, 400 Bad Request, 404 Not Found, 503 Unavailable)
- Version your APIs (`/v1/orders`) — never break clients silently
- Use HATEOAS for discoverability (optional but helpful)

### 3.3 Synchronous: gRPC

gRPC uses **Protocol Buffers (Protobuf)** — binary serialization, strongly typed contracts.

**Service Definition (.proto file):**

```protobuf
syntax = "proto3";
package order;

service OrderService {
  rpc CreateOrder (CreateOrderRequest) returns (CreateOrderResponse);
  rpc GetOrder    (GetOrderRequest)    returns (Order);
  rpc ListOrders  (ListOrdersRequest)  returns (stream Order);  // server streaming
}

message CreateOrderRequest {
  string user_id = 1;
  repeated OrderItem items = 2;
}

message OrderItem {
  string product_id = 1;
  int32  quantity   = 2;
}

message CreateOrderResponse {
  string order_id = 1;
  string status   = 2;
}
```

**Why gRPC over REST?**
- ~5–10x faster serialization than JSON
- Strongly typed — compile-time contract checking
- Built-in streaming (server push, bidirectional)
- Code generation for all major languages
- HTTP/2 multiplexing — multiple requests over one connection

**When to use REST vs gRPC:**

| Scenario | Use |
|---|---|
| Public-facing API | REST (universal compatibility) |
| Internal service-to-service | gRPC (speed, type safety) |
| Real-time streaming | gRPC |
| Simple CRUD | REST |
| Polyglot services needing shared contracts | gRPC |

### 3.4 Asynchronous: Event-Driven

Services publish **events** to a message broker. Consumers subscribe and react.

```
OrderService publishes:
  {
    "event_type": "order.created",
    "version": "1.0",
    "timestamp": "2026-03-07T10:00:00Z",
    "data": {
      "order_id": "o_789",
      "user_id": "u_123",
      "total": 59.99,
      "items": [...]
    }
  }

Consumers:
  InventoryService  → reserves stock
  PaymentService    → initiates charge
  NotificationService → sends confirmation email
  AnalyticsService  → records for reporting
```

**Event vs Command vs Query:**

```
Command:  "ProcessPayment"      → directed at specific service, expects action
Event:    "PaymentProcessed"    → broadcast, happened in the past, no expectation
Query:    "GetOrderStatus"      → synchronous, expects data back
```

### 3.5 Choosing Sync vs Async

```
Use SYNCHRONOUS when:
  ✓ You need an immediate response (user is waiting)
  ✓ The operation is a query (reading data)
  ✓ The transaction must be atomic (all-or-nothing)

Use ASYNCHRONOUS when:
  ✓ The operation is a side effect (notification, audit log)
  ✓ Processing can be deferred (report generation)
  ✓ You need to fan-out to multiple consumers
  ✓ You want loose coupling between services
  ✓ The downstream service is slow or unreliable
```

---

## 4. API Gateway & Edge Layer

The **API Gateway** is the single entry point for all external traffic.

### 4.1 Architecture

```
                        ┌──────────────────┐
Client (browser/app) → │    API Gateway   │ → microservices
                        └──────────────────┘
                              handles:
                         - Auth/JWT validation
                         - Rate limiting
                         - Routing
                         - SSL termination
                         - Request transformation
                         - Response aggregation
                         - Caching
                         - Logging
```

### 4.2 Gateway Responsibilities

**Authentication & Authorization**
```
Client sends: Authorization: Bearer eyJhbGci...
Gateway validates JWT signature + expiry
Gateway injects user context into downstream headers:
  X-User-Id: u_123
  X-User-Roles: admin,user
Services trust this header (mTLS ensures it came from gateway)
```

**Rate Limiting**

```
Strategies:
  - Fixed Window:   100 req/minute per API key (simple, has burst problem)
  - Sliding Window: counts requests in rolling 60s window (smoother)
  - Token Bucket:   refill at fixed rate, allow bursts up to bucket size
  - Leaky Bucket:   constant output rate regardless of input bursts

Implementation:
  Redis stores counters per user/IP per window
  Lua script for atomic increment + check (prevents race conditions)
```

**Request Routing**

```yaml
# Kong / AWS API Gateway routing rules
routes:
  - path: /api/v1/orders/*
    service: order-service:8080
    methods: [GET, POST, PUT, DELETE]

  - path: /api/v1/products/*
    service: catalog-service:8080
    methods: [GET]

  - path: /api/v1/users/*
    service: user-service:8080
    strip_prefix: true  # removes /api/v1/users before forwarding
```

**Backend for Frontend (BFF) Pattern**

Instead of one gateway, create a **dedicated gateway per client type**:

```
Mobile App     → Mobile BFF    → (optimized responses: smaller payloads, fewer fields)
Web App        → Web BFF       → (full responses, can do server-side aggregation)
Partner API    → Partner BFF   → (different auth, rate limits, versioning)
```

This avoids the "lowest common denominator" problem where one API tries to serve all clients.

### 4.3 API Gateway Tools Comparison

| Tool | Best For | Notes |
|---|---|---|
| Kong | General purpose, plugin ecosystem | Open-source, highly extensible |
| AWS API Gateway | AWS-native workloads | Managed, integrates with Lambda |
| Nginx | High performance, simplicity | Manual config, no built-in discovery |
| Traefik | Kubernetes-native | Auto-discovers services via labels |
| Envoy | Advanced traffic management | Low-level, usually wrapped by Istio |

---

## 5. Routing & Load Balancing

### 5.1 Routing Strategies

**Path-Based Routing**
```
/orders/*      → OrderService
/products/*    → CatalogService
/users/*       → UserService
/payments/*    → PaymentService
```

**Header-Based Routing**
```
X-Version: v2  → new service version (canary)
X-Region: EU   → EU-specific service instance
X-Tenant: acme → tenant-specific deployment (multi-tenancy)
```

**Content-Based Routing**
```
Request body contains "type": "enterprise"  → EnterprisePipeline
Request body contains "type": "standard"    → StandardPipeline
```

### 5.2 Load Balancing Algorithms

**Round Robin**
```
Request 1 → Instance A
Request 2 → Instance B
Request 3 → Instance C
Request 4 → Instance A (cycles)

Simple. Ignores server health/load.
```

**Weighted Round Robin**
```
Instance A (weight 3) → 3 out of 5 requests
Instance B (weight 2) → 2 out of 5 requests

Used for: canary deployments (5% traffic to new version)
          gradual rollouts
          heterogeneous hardware (powerful vs weak instances)
```

**Least Connections**
```
Routes to the instance with fewest active connections.
Better than round robin for long-lived connections (WebSockets, gRPC streams).
```

**IP Hash (Sticky Sessions)**
```
Hash(client_IP) % num_instances → always same instance
Good for: stateful services (sessions in-memory)
Bad for: stateless services (breaks if instance dies)
```

**Least Response Time**
```
Routes to instance with lowest combination of:
  - Active connections
  - Average response time
Best for: heterogeneous workloads
```

### 5.3 Layer 4 vs Layer 7 Load Balancing

```
Layer 4 (Transport):
  Works at TCP level. Doesn't inspect packet content.
  Fast, low overhead.
  Can't route by HTTP headers, paths, or cookies.
  Tools: AWS NLB, HAProxy (TCP mode)

Layer 7 (Application):
  Inspects HTTP headers, paths, body.
  Enables path-based routing, sticky sessions, SSL termination.
  Slightly more overhead.
  Tools: AWS ALB, Nginx, HAProxy (HTTP mode), Envoy
```

### 5.4 Traffic Splitting Patterns

**Canary Deployment**
```
Deploy v2 to 1 instance.
Route 5% of traffic to v2.
Monitor error rates, latency, business metrics.
If healthy → increase to 10%, 25%, 50%, 100%.
If unhealthy → route 0% to v2, fix, retry.
```

**Blue-Green Deployment**
```
Blue  = current production (100% traffic)
Green = new version (0% traffic, fully deployed)

Switch: route 100% traffic from Blue → Green (instant cutover)
Rollback: switch back to Blue (< 1 second)

Requires 2x infrastructure running simultaneously.
```

**Shadow / Mirroring**
```
Real traffic goes to production (v1).
Request is ALSO mirrored to new service (v2).
v2 responses are discarded (not returned to client).
Used for: testing v2 with real traffic without user impact.
```

---

## 6. Service Discovery

When services scale dynamically, IPs change constantly. Discovery solves the "where is service X?" problem.

### 6.1 Client-Side Discovery

```
1. Service registers itself in Service Registry on startup
2. Service deregisters (or health check fails) on shutdown
3. Client queries registry to get healthy instance list
4. Client load-balances across instances itself

Flow:
  OrderService starts → registers {name: "order-service", ip: "10.0.1.5", port: 8080}
  PaymentService needs OrderService → queries registry → gets [10.0.1.5, 10.0.1.6]
  PaymentService picks one (round-robin/random) → calls it

Tools: Netflix Eureka, HashiCorp Consul, Apache Zookeeper
```

**Eureka Registration (Spring Boot):**
```yaml
eureka:
  client:
    service-url:
      defaultZone: http://eureka-server:8761/eureka/
  instance:
    prefer-ip-address: true
    lease-renewal-interval-in-seconds: 10
    lease-expiration-duration-in-seconds: 30
```

### 6.2 Server-Side Discovery

```
1. Client sends request to a Load Balancer
2. Load Balancer queries registry
3. Load Balancer routes to healthy instance

Client doesn't know about discovery at all — simpler client code.

Tools: AWS ALB + ECS service discovery, Kubernetes Services
```

### 6.3 DNS-Based Discovery (Kubernetes)

In Kubernetes every Service gets a stable DNS name automatically:

```
Service: order-service in namespace: default

DNS name: order-service.default.svc.cluster.local

From within the cluster:
  http://order-service          (same namespace)
  http://order-service.default  (cross-namespace shorthand)
  http://order-service.default.svc.cluster.local  (fully qualified)
```

**How it works under the hood:**
```
kube-dns / CoreDNS resolves the name to the Service's ClusterIP (virtual IP)
iptables rules on every node do DNAT: ClusterIP → one of the pod IPs
kube-proxy maintains these iptables rules as pods come/go
```

### 6.4 Health Checks

Services must report their health so bad instances are removed from rotation:

```
Liveness probe:  Is the service alive? (not deadlocked)
  Fail → Kubernetes restarts the container

Readiness probe: Is the service ready to receive traffic?
  Fail → Kubernetes removes it from Service endpoints (no traffic sent)

Startup probe:   Has the app finished starting up?
  Prevents liveness probe from killing slow-starting apps
```

```yaml
# Kubernetes probe config
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

```python
# Health endpoint implementation
@app.get("/health/live")
def liveness():
    # Just check the process is alive
    return {"status": "ok"}

@app.get("/health/ready")
def readiness():
    # Check dependencies: DB connection, cache, etc.
    try:
        db.execute("SELECT 1")
        redis.ping()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
```

---

## 7. Data Architecture & Databases

### 7.1 Database Per Service — The Cardinal Rule

**Why no shared databases?**

```
Shared DB scenario:
  OrderService and InventoryService both access orders_db
  → OrderService changes the schema → InventoryService breaks
  → You can't deploy them independently
  → You've created tight coupling at the data layer

Shared DB = distributed monolith
```

**Database per service:**
```
OrderService     → PostgreSQL    (relational, ACID, complex queries)
ProductService   → PostgreSQL    (product catalog, full-text search)
InventoryService → Redis + PG    (Redis for speed, PG for persistence)
SessionService   → Redis         (TTL-based, fast reads/writes)
UserService      → PostgreSQL    (GDPR-sensitive, strong consistency)
SearchService    → Elasticsearch (full-text, faceted search)
AnalyticsService → ClickHouse    (columnar, OLAP, fast aggregations)
TimeSeriesData   → InfluxDB      (metrics, IoT, monitoring)
GraphService     → Neo4j         (social graph, recommendations)
```

### 7.2 Database Selection per Use Case

**Relational (PostgreSQL, MySQL)**
```
Best for:
  - Complex relationships and joins
  - ACID transactions within a service
  - Financial data, user accounts
  - Any data where consistency > speed

Key features to exploit:
  - Partitioning (range/hash) for large tables
  - Materialized views for complex aggregations
  - LISTEN/NOTIFY for change notifications
  - JSONB for semi-structured data (without going to MongoDB)
```

**Document (MongoDB)**
```
Best for:
  - Variable schema (product catalogs with different attributes per category)
  - Hierarchical data stored together (order with embedded items)
  - High write throughput

Watch out for:
  - No multi-document ACID (available in transactions since v4.0 but expensive)
  - Consistency trade-offs in replica sets
```

**Key-Value (Redis)**
```
Best for:
  - Session storage
  - Rate limiting counters
  - Distributed caching
  - Leaderboards (sorted sets)
  - Pub/Sub (lightweight messaging)
  - Distributed locks

Data structures: String, Hash, List, Set, Sorted Set, Stream, HyperLogLog
```

**Search (Elasticsearch)**
```
Best for:
  - Full-text search
  - Faceted filtering (category + price + brand simultaneously)
  - Log aggregation (ELK stack)
  - Geospatial queries

Pattern: ProductService writes to PostgreSQL AND Elasticsearch
         Reads from Elasticsearch for search
         PostgreSQL is source of truth
```

**Columnar (ClickHouse, Redshift, BigQuery)**
```
Best for:
  - Analytics (OLAP) — aggregations over billions of rows
  - Time series data
  - Read-heavy, write-batch workloads

NOT for: transactional workloads (OLTP)
```

### 7.3 CQRS — Command Query Responsibility Segregation

Separate the **write model** (commands) from the **read model** (queries):

```
Write Side (Command):
  - Accepts commands: CreateOrder, UpdateOrderStatus
  - Validates business rules
  - Writes to write DB (normalized, consistent)
  - Publishes events

Read Side (Query):
  - Subscribes to events
  - Builds optimized read models (denormalized views)
  - One read model per query pattern
  - Can use different DB technology

Example:
  Write: orders_db (PostgreSQL, normalized)
  Read:
    - order_list_view   (PostgreSQL, denormalized for list page)
    - order_detail_view (Elasticsearch, with product details joined)
    - order_dashboard   (Redis, pre-aggregated counts)
```

```
Write path:
  POST /orders → OrderService → validates → INSERT into orders_db → publish OrderCreated

Read path (from read DB, not write DB):
  GET /orders?user_id=123 → OrderQueryService → SELECT from order_list_view (optimized)
```

### 7.4 Event Sourcing

Instead of storing current state, store the **sequence of events** that led to it:

```
Traditional:
  orders table: {id: 1, status: "shipped", total: 59.99}

Event Sourced:
  events table:
    {order_id: 1, event: "OrderCreated",   data: {total: 59.99},    ts: T1}
    {order_id: 1, event: "PaymentTaken",   data: {amount: 59.99},   ts: T2}
    {order_id: 1, event: "ItemsPicked",    data: {warehouse: "W1"}, ts: T3}
    {order_id: 1, event: "OrderShipped",   data: {carrier: "FedEx"},ts: T4}
```

**Benefits:**
- Complete audit trail (financial, healthcare requirements)
- Replay events to rebuild state at any point in time
- Natural integration with event-driven architecture
- Time travel debugging

**Challenges:**
- Querying current state requires replaying events (use snapshots)
- Schema evolution of events is hard
- Operational complexity

---

## 8. Distributed Transactions & Consistency

### 8.1 Why Distributed Transactions Are Hard

```
In a monolith:
  BEGIN TRANSACTION
    UPDATE orders SET status = 'confirmed'
    UPDATE inventory SET stock = stock - 1
    INSERT INTO payments VALUES (...)
  COMMIT  -- all succeed or all rollback. Simple.

In microservices:
  OrderService    → its own DB
  InventoryService → its own DB
  PaymentService  → its own DB

  You CANNOT do a distributed BEGIN/COMMIT across three different databases.
  (Two-Phase Commit exists but is slow, fragile, and creates coupling)
```

### 8.2 The Saga Pattern

A saga is a sequence of **local transactions**, each triggered by the previous one's event.

**Choreography-Based Saga** (event-driven, decentralized):

```
Step 1: OrderService
  Creates order (status: PENDING)
  Publishes: OrderCreated

Step 2: PaymentService (listens to OrderCreated)
  Charges customer
  Publishes: PaymentProcessed  (or PaymentFailed)

Step 3: InventoryService (listens to PaymentProcessed)
  Reserves stock
  Publishes: StockReserved  (or StockInsufficient)

Step 4: OrderService (listens to StockReserved)
  Updates order status to CONFIRMED
  Publishes: OrderConfirmed

FAILURE PATH:
  If PaymentFailed →
    OrderService listens → updates status to FAILED

  If StockInsufficient →
    PaymentService listens to StockInsufficient →
      issues refund, publishes PaymentRefunded
    OrderService listens to PaymentRefunded →
      updates status to FAILED
```

**Orchestration-Based Saga** (centralized coordinator):

```
OrderSaga (orchestrator):

  1. Send command: ProcessPayment to PaymentService
     Wait for PaymentProcessed event

  2. Send command: ReserveStock to InventoryService
     Wait for StockReserved event

  3. Send command: ConfirmOrder to OrderService

  On failure at step 2:
     Send command: RefundPayment to PaymentService (compensation)
     Send command: CancelOrder to OrderService
```

```python
# Saga orchestrator using a state machine
class OrderSaga:
    def __init__(self, order_id):
        self.order_id = order_id
        self.state = "STARTED"

    def handle_event(self, event):
        if self.state == "STARTED" and event.type == "saga.start":
            self.state = "PAYMENT_PENDING"
            self.send_command("payment-service", "ProcessPayment", {
                "order_id": self.order_id,
                "amount": event.data["total"]
            })

        elif self.state == "PAYMENT_PENDING" and event.type == "payment.processed":
            self.state = "INVENTORY_PENDING"
            self.send_command("inventory-service", "ReserveStock", {
                "order_id": self.order_id,
                "items": event.data["items"]
            })

        elif self.state == "PAYMENT_PENDING" and event.type == "payment.failed":
            self.state = "FAILED"
            self.send_command("order-service", "CancelOrder", {"order_id": self.order_id})

        elif self.state == "INVENTORY_PENDING" and event.type == "stock.reserved":
            self.state = "COMPLETED"
            self.send_command("order-service", "ConfirmOrder", {"order_id": self.order_id})

        elif self.state == "INVENTORY_PENDING" and event.type == "stock.insufficient":
            self.state = "COMPENSATING"
            self.send_command("payment-service", "RefundPayment", {
                "order_id": self.order_id
            })
```

### 8.3 The Outbox Pattern

Guarantees events are published **exactly when** the DB write happens — not separately.

**Problem:**
```python
# WRONG — these two operations are not atomic:
db.execute("INSERT INTO orders ...")   # succeeds
kafka.publish("order.created", ...)   # CRASHES HERE — event never sent!
                                       # DB has the order, Kafka doesn't know
```

**Solution — Transactional Outbox:**
```sql
-- Single DB transaction (atomic):
BEGIN;
  INSERT INTO orders (id, status, user_id) VALUES ('o_789', 'pending', 'u_123');
  INSERT INTO outbox (id, topic, payload, created_at)
    VALUES (gen_random_uuid(), 'order.created', '{"order_id":"o_789",...}', NOW());
COMMIT;

-- Separate process (Message Relay / Debezium):
  Reads unprocessed rows from outbox
  Publishes to Kafka
  Marks rows as published (or deletes them)
```

**Using Debezium (CDC - Change Data Capture):**
```
Debezium tails PostgreSQL WAL (Write-Ahead Log)
Captures every INSERT/UPDATE/DELETE
Streams changes to Kafka automatically
No polling overhead, near-real-time
```

### 8.4 Idempotency

Since messages can be delivered **at least once**, consumers must handle duplicates:

```python
# Consumer with idempotency key
def handle_payment_event(event):
    idempotency_key = event["event_id"]  # unique per event

    # Check if we've processed this event before
    if redis.get(f"processed:{idempotency_key}"):
        logger.info(f"Skipping duplicate event {idempotency_key}")
        return

    # Process the event
    with db.transaction():
        process_payment(event["data"])
        # Mark as processed (within same transaction or with TTL)
        redis.setex(f"processed:{idempotency_key}", ttl=86400, value="1")
```

---

## 9. Event-Driven Architecture & Messaging

### 9.1 Apache Kafka Deep-Dive

Kafka is the dominant choice for high-throughput event streaming.

**Core Concepts:**

```
Topic:
  A named stream of events (like a category).
  "order-events", "payment-events", "inventory-events"

Partition:
  A topic is split into partitions for parallelism.
  Each partition is an ordered, immutable log.
  Messages within a partition are ordered. Across partitions — no ordering guarantee.

Offset:
  Each message in a partition has an offset (sequential integer).
  Consumers track their offset — they control where they are.
  Messages are NOT deleted after consumption (unlike queues).
  Retention is time-based (default 7 days) or size-based.

Consumer Group:
  A group of consumers sharing a subscription to a topic.
  Each partition assigned to exactly one consumer in the group.
  Multiple groups = multiple independent consumers of same data.
```

**Partition Key — Critical for Ordering:**

```python
# If order_id is the partition key:
# All events for the same order → same partition → guaranteed ordering

producer.send(
    topic="order-events",
    key=order_id.encode(),   # same key → same partition
    value=json.dumps(event).encode()
)
```

**Consumer Group Parallelism:**

```
Topic: order-events (6 partitions)
Consumer Group A (InventoryService, 3 instances):
  Instance 1 → partitions 0, 1
  Instance 2 → partitions 2, 3
  Instance 3 → partitions 4, 5

Consumer Group B (NotificationService, 2 instances):
  Instance 1 → partitions 0, 1, 2
  Instance 2 → partitions 3, 4, 5

Both groups independently consume all messages. One doesn't affect the other.
```

**Kafka vs RabbitMQ:**

| Aspect | Kafka | RabbitMQ |
|---|---|---|
| Model | Log (events persist, consumers pull) | Queue (messages deleted after ack) |
| Throughput | Millions msg/sec | Hundreds of thousands msg/sec |
| Message ordering | Per-partition | Per-queue |
| Replay | Yes (go back to any offset) | No (once consumed, gone) |
| Consumer control | Consumer pulls at own pace | Broker pushes to consumer |
| Use case | Event streaming, audit log, CQRS | Task queues, RPC, routing |
| Retention | Time/size based | Until consumed |

### 9.2 Event Schema & Evolution

**Use a Schema Registry (Confluent)**
```
Producers register schemas before publishing.
Consumers validate messages against the registry.
Schema evolution rules enforced (backward/forward compatibility).

Avro schema example:
{
  "type": "record",
  "name": "OrderCreated",
  "namespace": "com.company.orders",
  "fields": [
    {"name": "order_id",  "type": "string"},
    {"name": "user_id",   "type": "string"},
    {"name": "total",     "type": "double"},
    {"name": "items",     "type": {"type": "array", "items": "string"}},
    {"name": "source",    "type": ["null", "string"], "default": null}  // new optional field — backward compatible
  ]
}
```

**Event Versioning Strategies:**
```
1. Add optional fields only (never remove/rename — breaking change)
2. Create new event type: "order.created.v2" (parallel consumers)
3. Version field in payload: {"version": "2", "data": {...}}
4. Header-based: "X-Event-Version: 2"
```

---

## 10. Orchestration & Container Management

### 10.1 Docker — Containerization

Each microservice is a Docker image — isolated, reproducible, portable.

**Optimized Production Dockerfile:**

```dockerfile
# Multi-stage build — keeps final image small
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci                        # install ALL deps (including dev)
COPY . .
RUN npm run build                 # compile TypeScript, bundle, etc.

FROM node:20-alpine AS runtime
RUN addgroup -S appgroup && adduser -S appuser -G appgroup  # non-root user
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production      # only prod deps
COPY --from=builder /app/dist ./dist

USER appuser                      # never run as root in prod
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s \
  CMD wget -qO- http://localhost:8080/health || exit 1

CMD ["node", "dist/server.js"]
```

### 10.2 Kubernetes — The Control Plane

Kubernetes manages the desired state of your cluster.

**Core Objects:**

```yaml
# Deployment — manages ReplicaSet, rolling updates, rollback
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-service
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1   # at most 1 pod unavailable during update
      maxSurge: 1         # at most 1 extra pod during update
  template:
    metadata:
      labels:
        app: order-service
        version: "2.1.0"
    spec:
      containers:
      - name: order-service
        image: company/order-service:2.1.0
        ports:
        - containerPort: 8080
        env:
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: order-service-secrets
              key: db-host
        - name: KAFKA_BROKERS
          valueFrom:
            configMapKeyRef:
              name: order-service-config
              key: kafka-brokers
        resources:
          requests:            # guaranteed resources
            cpu: "100m"        # 0.1 CPU cores
            memory: "256Mi"
          limits:              # maximum allowed
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      affinity:
        podAntiAffinity:       # spread pods across nodes
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: order-service
              topologyKey: kubernetes.io/hostname
```

```yaml
# Service — stable network endpoint, load balances across pods
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  selector:
    app: order-service
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP             # internal only
```

```yaml
# HorizontalPodAutoscaler — auto-scales based on metrics
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-service
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second  # custom metric from Prometheus
      target:
        type: AverageValue
        averageValue: "1000"
```

### 10.3 Kubernetes Networking Internals

```
How a request gets from Service to Pod:

1. Client resolves "order-service" via CoreDNS → ClusterIP (e.g., 10.96.45.12)
2. Packet sent to 10.96.45.12:80
3. kube-proxy's iptables rules intercept the packet
4. DNAT: 10.96.45.12:80 → 10.244.2.5:8080 (a real pod IP, randomly chosen)
5. Packet routed through CNI (Calico/Flannel/Cilium) overlay network to the pod
6. Pod processes request
```

### 10.4 Namespaces — Multi-Tenancy

```yaml
# Environments as namespaces
kubectl create namespace production
kubectl create namespace staging
kubectl create namespace development

# ResourceQuota per namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "20"
    requests.memory: "40Gi"
    limits.cpu: "40"
    limits.memory: "80Gi"
    count/pods: "100"
```

### 10.5 StatefulSets vs Deployments

```
Deployment:
  Pods are interchangeable. Any pod can handle any request.
  Pod names: order-service-7f9d-abc, order-service-7f9d-xyz (random suffix)
  Used for: stateless microservices

StatefulSet:
  Pods have stable identity and persistent storage.
  Pod names: kafka-0, kafka-1, kafka-2 (ordinal index)
  Pods start/stop in order (kafka-0 before kafka-1)
  Each pod gets its own PersistentVolume
  Used for: databases, Kafka, ZooKeeper, any stateful workload
```

---

## 11. Service Mesh

A service mesh adds a **transparent infrastructure layer** for service-to-service communication.

### 11.1 Sidecar Proxy Pattern

```
Instead of putting retry/circuit-breaker/TLS logic in every service:

Every pod gets an injected sidecar proxy (Envoy):

  Pod:
    ┌─────────────────────────────┐
    │ Order Service (port 8080)   │
    │ Envoy Sidecar (port 15001)  │  ← intercepts all in/out traffic
    └─────────────────────────────┘

All traffic goes through Envoy. App code knows nothing about:
  - mTLS encryption/auth
  - Retries and timeouts
  - Circuit breaking
  - Distributed tracing headers
  - Traffic splitting
```

### 11.2 Istio Architecture

```
Data Plane:
  Envoy sidecars in every pod — handle actual traffic

Control Plane (istiod):
  - Pilot:    pushes routing rules to Envoy sidecars
  - Citadel:  manages certificates for mTLS
  - Galley:   validates and distributes config

Traffic flow:
  Service A's Envoy → (mTLS) → Service B's Envoy → Service B app
```

### 11.3 Istio Traffic Management

```yaml
# VirtualService — fine-grained routing rules
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: order-service
spec:
  hosts:
  - order-service
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: order-service
        subset: v2                # 100% canary traffic to v2

  - route:                        # default: weighted split
    - destination:
        host: order-service
        subset: v1
      weight: 95
    - destination:
        host: order-service
        subset: v2
      weight: 5

  - retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: "5xx,reset,connect-failure"

  - timeout: 10s
```

```yaml
# DestinationRule — defines subsets and load balancing
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: order-service
spec:
  host: order-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: UPGRADE
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s      # circuit breaker: eject bad instances
  subsets:
  - name: v1
    labels:
      version: "1.0.0"
  - name: v2
    labels:
      version: "2.0.0"
```

---

## 12. Resilience Patterns

Distributed systems fail. Design for failure as a first-class concern.

### 12.1 Circuit Breaker

```
States:
  CLOSED:   Requests flow normally. Failure count monitored.
  OPEN:     Too many failures. Requests fail immediately (no network call).
            After timeout, transition to HALF-OPEN.
  HALF-OPEN: Allow one test request through.
             If success → CLOSED
             If failure → OPEN again

Implementation (Resilience4j / Java):
  CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)          // open at 50% failure rate
    .waitDurationInOpenState(30s)      // wait 30s before trying again
    .slidingWindowSize(10)             // measure last 10 requests
    .permittedNumberOfCallsInHalfOpenState(3)
    .build();
```

### 12.2 Retry with Exponential Backoff

```python
import time, random

def call_with_retry(fn, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return fn()
        except TransientError as e:
            if attempt == max_attempts - 1:
                raise
            # Exponential backoff with jitter
            base_delay = 2 ** attempt          # 1s, 2s, 4s
            jitter = random.uniform(0, 0.5)    # prevents thundering herd
            time.sleep(base_delay + jitter)

# Retry only on transient errors (network timeout, 503)
# Never retry on: 400 Bad Request, 401 Unauthorized, 404 Not Found
```

### 12.3 Bulkhead Pattern

Isolate failures by limiting resource use per dependency:

```python
# Without bulkhead: PaymentService slowness consumes all threads
# and takes down OrderService entirely

# With bulkhead: each downstream service gets its own thread pool
payment_executor = ThreadPoolExecutor(max_workers=10)
inventory_executor = ThreadPoolExecutor(max_workers=10)
shipping_executor = ThreadPoolExecutor(max_workers=5)

# PaymentService uses all 10 threads → inventory and shipping still work
```

### 12.4 Timeout Strategy

```
Every network call MUST have a timeout. No exceptions.

Timeout hierarchy:
  User-facing API: 3s total
    → Gateway: 2.5s
      → Service A: 2s
        → Service B: 1.5s
          → DB query: 1s

Rule: Each downstream timeout must be < upstream timeout
      (leaves time for the caller to handle the response)

Never use:
  requests.get("http://service-b/data")       # infinite wait
Always use:
  requests.get("http://service-b/data", timeout=2.0)
```

### 12.5 Fallback Strategies

```python
def get_product_recommendations(user_id):
    try:
        # Try ML-powered recommendations
        return recommendation_service.get(user_id, timeout=1.0)
    except (TimeoutError, ServiceUnavailableError):
        # Fallback 1: try cached recommendations
        cached = redis.get(f"recs:{user_id}")
        if cached:
            return json.loads(cached)

        # Fallback 2: static popular products (always works)
        return get_top_selling_products(category="all", limit=10)
```

---

## 13. Security

### 13.1 Authentication & Authorization

**JWT Flow:**
```
1. User authenticates with AuthService (username + password / OAuth)
2. AuthService returns signed JWT:
   Header:  {"alg": "RS256", "typ": "JWT"}
   Payload: {"sub": "u_123", "roles": ["user"], "exp": 1741392000}
   Signature: RS256(base64(header) + "." + base64(payload), private_key)

3. Client sends JWT in every request:
   Authorization: Bearer eyJhbGciOiJSUzI1NiJ9...

4. API Gateway validates JWT:
   - Checks signature with public key (no DB call needed)
   - Checks expiry
   - Extracts claims, forwards as headers:
     X-User-Id: u_123
     X-User-Roles: user

5. Services trust these headers (but only from the gateway — enforced by network policy)
```

**OAuth 2.0 / OIDC for Service-to-Service:**
```
Service A needs to call Service B:
  Service A requests token from Auth Server (client credentials flow)
  Auth Server returns access token
  Service A calls Service B with token
  Service B validates token with Auth Server (or via public key)
```

### 13.2 mTLS — Mutual TLS

```
Regular TLS: Server proves identity to client (one-way)
mTLS:        Both server AND client prove identity (two-way)

In service mesh (Istio):
  Every service gets a certificate (SPIFFE ID): spiffe://cluster/ns/prod/sa/order-service
  When OrderService calls PaymentService:
    OrderService presents its cert → PaymentService verifies it's a legitimate service
    PaymentService presents its cert → OrderService verifies it
  Unauthorized services (no valid cert) cannot communicate

Benefits:
  - Encryption in transit (even within the cluster)
  - Service identity (not just IP-based auth)
  - Zero-trust network model
```

### 13.3 Secrets Management

```
Never:
  - Hardcode secrets in code
  - Store secrets in ConfigMaps (they're not encrypted)
  - Commit secrets to git

Use:
  - Kubernetes Secrets (base64 encoded, but encrypted at rest if configured)
  - HashiCorp Vault (dynamic secrets, auto-rotation, audit log)
  - AWS Secrets Manager / GCP Secret Manager

Vault dynamic secrets:
  Service requests DB credentials from Vault
  Vault creates a temporary DB user (TTL: 1 hour)
  Service uses credentials
  After 1 hour, Vault revokes the credentials automatically
  Compromised credentials expire on their own
```

### 13.4 Network Policies

```yaml
# Only allow OrderService to receive traffic from API Gateway and other allowed services
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: order-service-policy
spec:
  podSelector:
    matchLabels:
      app: order-service
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
    - podSelector:
        matchLabels:
          app: payment-service   # PaymentService can call OrderService for status
    ports:
    - port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: inventory-service
    - podSelector:
        matchLabels:
          app: postgres-order
    ports:
    - port: 5432
```

---

## 14. Observability: Logging, Metrics, Tracing

"You can't manage what you can't measure."

### 14.1 Distributed Tracing

```
Every request gets a Trace ID at the gateway.
Each service creates a Span with timing info.
Spans are linked by Trace ID and parent Span ID.

Request: GET /orders/o_789

Trace ID: abc-123

  API Gateway         [0ms ─────────────────────────── 250ms] span_id: 1
    OrderService      [5ms ───────────────────── 240ms]        span_id: 2, parent: 1
      DB query        [6ms ─── 50ms]                           span_id: 3, parent: 2
      PaymentService  [60ms ────────── 180ms]                  span_id: 4, parent: 2
        DB query      [62ms ─ 100ms]                           span_id: 5, parent: 4
      InventoryService[185ms ── 235ms]                         span_id: 6, parent: 2
```

**OpenTelemetry (vendor-neutral standard):**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

tracer = trace.get_tracer("order-service")

def get_order(order_id):
    with tracer.start_as_current_span("get-order") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("db.type", "postgresql")

        result = db.query("SELECT * FROM orders WHERE id = ?", order_id)

        span.set_attribute("order.status", result.status)
        return result
```

### 14.2 Structured Logging

```python
import structlog

log = structlog.get_logger()

# Every log entry includes trace context + service info
log.info(
    "order.created",
    order_id="o_789",
    user_id="u_123",
    total=59.99,
    trace_id="abc-123",          # inject from request context
    span_id="span-456",
    service="order-service",
    environment="production",
    version="2.1.0"
)
```

```json
{
  "timestamp": "2026-03-07T10:00:00.123Z",
  "level": "info",
  "event": "order.created",
  "order_id": "o_789",
  "user_id": "u_123",
  "total": 59.99,
  "trace_id": "abc-123",
  "service": "order-service",
  "environment": "production"
}
```

**Log Aggregation Stack:**
```
Services → Fluent Bit (log shipper, runs as DaemonSet) → Elasticsearch → Kibana

Or: Services → CloudWatch / Datadog / Splunk
```

### 14.3 Metrics

**RED Method (per service):**
- **R**ate — requests per second
- **E**rrors — error rate (%)
- **D**uration — latency (p50, p95, p99)

**USE Method (per resource):**
- **U**tilization — CPU, memory, disk
- **S**aturation — queue depths, wait times
- **E**rrors — error counts

```python
from prometheus_client import Counter, Histogram, Gauge

request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code', 'service']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

# Instrument request handling
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        service="order-service"
    ).inc()

    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

**Alerting Rules (Prometheus):**

```yaml
groups:
- name: order-service-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status_code=~"5..",service="order-service"}[5m]) /
          rate(http_requests_total{service="order-service"}[5m]) > 0.05
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Order service error rate > 5%"

  - alert: HighLatency
    expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{service="order-service"}[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Order service p99 latency > 2s"
```

---

## 15. CI/CD for Microservices

### 15.1 Pipeline Per Service

Each microservice has its own pipeline. Independent deployments.

```
Trigger: push to main branch

Pipeline:
  1. Build
     └── Compile code, run linter, check types

  2. Unit Tests
     └── Fast, isolated, no external dependencies (mock everything)

  3. Build Docker Image
     └── docker build → tag with git SHA (e.g., order-service:a3f7d91)

  4. Integration Tests
     └── Spin up DB, Kafka in Docker
     └── Run service against real dependencies

  5. Push Image
     └── docker push company/order-service:a3f7d91

  6. Contract Tests
     └── Verify API contract with consumer (Pact framework)

  7. Deploy to Staging
     └── kubectl set image deployment/order-service order-service=company/order-service:a3f7d91

  8. Smoke Tests
     └── Hit key endpoints in staging

  9. Deploy to Production (canary)
     └── 5% traffic to new version
     └── Monitor for 10 minutes

  10. Full Rollout or Rollback
```

### 15.2 GitOps

```
The git repository is the single source of truth for deployment state.

Developer merges PR → CI builds and pushes image
CI updates image tag in Helm values / Kubernetes manifests in a git repo
GitOps controller (ArgoCD / Flux) detects the change
Controller applies changes to the cluster
Cluster state always matches git state

Rollback = git revert → controller restores previous state
Audit trail = git history
```

---

## 16. Configuration Management

### 16.1 12-Factor App Config

```
Rule: Config that varies between environments (dev/staging/prod) goes in environment variables.
Never: hardcode URLs, credentials, feature flags in code.

Environment variables injected via:
  - Kubernetes ConfigMaps (non-sensitive)
  - Kubernetes Secrets (sensitive)
  - External secrets operator (from Vault / AWS Secrets Manager)
```

### 16.2 Feature Flags

Control features without deployments:

```python
# LaunchDarkly / Unleash / homegrown
def get_product_page(product_id, user):
    if feature_flags.is_enabled("new-product-page", context={"user_id": user.id}):
        return render_new_product_page(product_id)
    else:
        return render_old_product_page(product_id)

# Feature flags enable:
#   - A/B testing (50% users see new UI)
#   - Gradual rollout (10% → 25% → 100%)
#   - Kill switch (instantly disable broken feature)
#   - Beta features for specific users/tenants
```

---

## 17. Testing Strategies

### 17.1 The Testing Pyramid

```
         ╱ E2E ╲          ← Few, slow, expensive. Full user journeys.
        ╱────────╲
       ╱Integration╲      ← Some. Service + real DB + real dependencies.
      ╱──────────────╲
     ╱   Unit Tests   ╲   ← Many, fast, cheap. Single function/class.
    ╱──────────────────╲
```

### 17.2 Consumer-Driven Contract Testing (Pact)

The key testing challenge in microservices: how to test that services work together without full integration tests.

```
Consumer (OrderService) defines what it expects from PaymentService:
  "When I call POST /payments with {order_id, amount}, 
   I expect {payment_id, status: 'success'}"

This contract is stored in a Pact Broker.

Provider (PaymentService) runs contract verification:
  PaymentService test spins up, replays the consumer's request
  Verifies the response matches the contract

If PaymentService changes its API in a breaking way → contract test fails
→ PaymentService team is notified before deployment
→ No surprise breakage in production
```

### 17.3 Testing in Production (Safely)

```
Chaos Engineering:
  Deliberately inject failures in production to validate resilience
  Tools: Netflix Chaos Monkey, Chaos Toolkit, AWS Fault Injection Simulator

  Examples:
    - Randomly kill pods
    - Inject 500ms latency into specific service
    - Drop 10% of packets to a dependency
    - Fill disk of a node

Feature Flags for Testing:
  Dark launch: new feature deployed but hidden behind flag
  Shadow testing: run new code path but use old result

Synthetic Monitoring:
  Automated scripts run real user journeys continuously
  Alert if journey fails or exceeds SLA
```

---

## 18. Anti-Patterns & Pitfalls

### ❌ Distributed Monolith

```
Services that are always deployed together, call each other synchronously in a chain,
and share a database. You have all the complexity of microservices with none of the benefits.

Signs:
  - Service A cannot start without Service B running
  - Deploying Service A requires coordinating with teams B, C, D
  - Services share a common library that has domain logic
  - Database tables are accessed by multiple services
```

### ❌ Chatty Services

```
Service A calls Service B 10 times per request.
Each call: 10ms → 100ms overhead per request.

Fix:
  Batch calls: "get me products [1, 2, 3, 4, 5]" instead of 5 separate calls
  Cache locally with short TTL
  Rethink service boundaries (maybe A and B should be one service)
```

### ❌ The "All Async" Trap

```
Using event queues for everything, including operations that need immediate responses.
Users hate waiting for an email confirmation to know if their order succeeded.

Rule: user-facing write operations = sync (you need the result now)
      side effects, fan-out = async (notification, analytics = async)
```

### ❌ Missing Idempotency

```
A payment event is delivered twice (normal in at-least-once messaging).
Service charges the customer twice.

Always:
  - Generate unique IDs for every operation
  - Check before processing
  - Use database unique constraints as a safety net
```

### ❌ Sharing Domain Models / Libraries

```
Shared library has the Order class.
OrderService and InventoryService both import it.
A change to Order breaks both services.
You've recreated compile-time coupling.

Rule: share nothing except:
  - Infrastructure code (logging, HTTP client wrappers)
  - API contracts (protobuf definitions, OpenAPI specs)
  - Never: domain objects, business logic
```

### ❌ Not Designing for Partial Failure

```
One service in a chain is slow → all callers timeout → cascading failure

Always:
  - Set timeouts on every outbound call
  - Implement circuit breakers
  - Design fallback behavior
  - Ask: "What happens to my service if Service X is completely down?"
```

---

## 19. Decision Framework

### When to Adopt Microservices

| Signal | Consider Microservices |
|---|---|
| Team > 20 engineers | ✓ Team coupling is the bottleneck |
| Multiple teams stepping on each other | ✓ Conway's Law applies |
| Specific components need 100x more scale than others | ✓ Granular scaling needed |
| Different tech requirements per component | ✓ Polyglot valuable |
| Regulatory isolation (PCI, HIPAA) | ✓ Data boundaries critical |
| < 5 engineers, new product | ✗ Start with a monolith |
| Unclear domain boundaries | ✗ Don't decompose prematurely |
| No DevOps/platform team | ✗ Infrastructure burden too high |

### Service Decomposition Checklist

```
Before extracting a service, verify:
  □ Clear bounded context with single responsibility
  □ Team ownership is clear (who owns this service?)
  □ Can it be deployed independently?
  □ Does it have its own data store?
  □ Is its API contract stable?
  □ Are failure modes understood?
  □ Is the operational overhead justified by the benefit?
```

### Technology Reference Card

```
API Gateway:          Kong, AWS API Gateway, Traefik, Nginx
Service Discovery:    Consul, Eureka, Kubernetes DNS
Load Balancing:       Envoy, AWS ALB/NLB, HAProxy
Message Broker:       Apache Kafka, RabbitMQ, AWS SQS/SNS
Service Mesh:         Istio, Linkerd, Consul Connect
Container Runtime:    Docker, containerd
Orchestration:        Kubernetes, AWS ECS, Nomad
Databases:            PostgreSQL, Redis, MongoDB, Elasticsearch, ClickHouse
Secrets:              HashiCorp Vault, AWS Secrets Manager
Tracing:              Jaeger, Zipkin, OpenTelemetry → Grafana Tempo
Metrics:              Prometheus + Grafana, Datadog
Logging:              ELK Stack, Loki + Grafana, Datadog
CI/CD:                GitHub Actions, ArgoCD, Flux, Jenkins
Contract Testing:     Pact
Chaos Engineering:    Chaos Monkey, AWS FIS
```

---

*The fundamental insight: microservices are an **organizational architecture** as much as a technical one. Conway's Law states that systems mirror the communication structure of the organizations that build them. Microservices work best when service boundaries align with team boundaries — enabling autonomous teams to move fast without coordination overhead.*
